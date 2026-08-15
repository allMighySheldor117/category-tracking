"""Phase 4 FastAPI skeleton contract tests."""

from __future__ import annotations

import subprocess
import sys
import unittest
from pathlib import Path

from fastapi.testclient import TestClient

from engine.exact_analysis import CANONICAL_STOP_CODONS
from engine.genetic_code import PROPERTY_LABELS, VALID_CODONS
from engine.mutation_matrix import PRESET_AC, PRESET_AG, PRESET_AT


REPO_ROOT = Path(__file__).resolve().parents[1]


class ApiAppTests(unittest.TestCase):
    def test_dependency_file_contains_approved_backend_and_deployment_packages(self) -> None:
        requirements = (REPO_ROOT / "requirements.txt").read_text(encoding="utf-8").splitlines()
        meaningful = [line.strip() for line in requirements if line.strip() and not line.startswith("#")]

        approved_backend_dependencies = [
            "fastapi>=0.139,<0.141",
            "uvicorn[standard]>=0.51,<0.52",
            "httpx>=0.28,<0.29",
        ]
        approved_phase9_deployment_dependencies = [
            "streamlit>=1.60,<1.61",
            "pandas>=2.2,<2.3",
            "plotly>=6.8,<6.9",
        ]

        self.assertEqual(
            meaningful,
            approved_backend_dependencies + approved_phase9_deployment_dependencies,
        )

    def test_app_import_and_health_endpoint(self) -> None:
        from api.main import app

        client = TestClient(app)
        response = client.get("/health")

        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            response.json(),
            {
                "api_version": "phase4-api-v1",
                "mode": "health",
                "scientific_authority": "none",
                "status": "ok",
            },
        )

    def test_metadata_endpoint_uses_engine_ordering(self) -> None:
        from api.main import app

        client = TestClient(app)
        response = client.get("/api/v1/metadata")

        self.assertEqual(response.status_code, 200)
        payload = response.json()
        self.assertEqual(payload["api_version"], "phase4-api-v1")
        self.assertEqual(payload["mode"], "metadata")
        self.assertEqual(payload["scientific_authority"], "engine")
        self.assertEqual(payload["data"]["valid_codons"], VALID_CODONS)
        self.assertEqual(payload["data"]["stop_codons"], list(CANONICAL_STOP_CODONS))
        self.assertEqual(payload["data"]["category_labels"], list(PROPERTY_LABELS.values()))
        self.assertEqual(
            payload["data"]["probability_presets"],
            {"at": PRESET_AT, "ag": PRESET_AG, "ac": PRESET_AC},
        )

    def test_openapi_metadata_is_discoverable(self) -> None:
        from api.main import app

        schema = app.openapi()
        self.assertEqual(schema["info"]["title"], "Codon Category Tracking API")
        self.assertEqual(schema["info"]["version"], "phase4-api-v1")
        self.assertIn("/health", schema["paths"])
        self.assertIn("/api/v1/metadata", schema["paths"])

    def test_base_table_serializer_contract(self) -> None:
        import pandas as pd

        from api.serializers import serialize_table

        frame = pd.DataFrame(
            {
                "generation": pd.Series([1, 2], dtype="int64"),
                "fraction": pd.Series([0.25, pd.NA], dtype="Float64"),
            }
        )
        serialized = serialize_table(frame, value_kind="fraction")

        self.assertEqual(
            serialized,
            {
                "columns": ["generation", "fraction"],
                "dtypes": {"generation": "int64", "fraction": "Float64"},
                "records": [
                    {"generation": 1, "fraction": 0.25},
                    {"generation": 2, "fraction": None},
                ],
                "index_kind": "RangeIndex",
                "row_count": 2,
                "value_kind": "fraction",
            },
        )

    def test_engine_import_does_not_load_api_or_ui_frameworks(self) -> None:
        command = (
            "import sys, engine; "
            "forbidden={'fastapi','starlette','uvicorn','httpx','streamlit','tkinter','plotly','PyQt5'}; "
            "loaded=forbidden.intersection(sys.modules); "
            "assert not loaded, sorted(loaded); "
            "print('engine-boundary-ok')"
        )
        completed = subprocess.run(
            [sys.executable, "-c", command],
            cwd=REPO_ROOT,
            env={"PYTHONDONTWRITEBYTECODE": "1"},
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        self.assertIn("engine-boundary-ok", completed.stdout)

    def test_api_package_does_not_import_ui_frameworks(self) -> None:
        command = (
            "import sys; import api.main; "
            "forbidden={'streamlit','tkinter','plotly','PyQt5'}; "
            "loaded=forbidden.intersection(sys.modules); "
            "assert not loaded, sorted(loaded); "
            "print('api-boundary-ok')"
        )
        completed = subprocess.run(
            [sys.executable, "-c", command],
            cwd=REPO_ROOT,
            env={"PYTHONDONTWRITEBYTECODE": "1"},
            text=True,
            capture_output=True,
            check=False,
        )

        self.assertEqual(completed.returncode, 0, completed.stderr + completed.stdout)
        self.assertIn("api-boundary-ok", completed.stdout)


if __name__ == "__main__":
    unittest.main()
