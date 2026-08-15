"""Phase 4 API service-boundary and dependency review tests."""

from __future__ import annotations

import ast
import subprocess
import sys
import unittest
from pathlib import Path

from api.main import app


REPO_ROOT = Path(__file__).resolve().parents[1]
API_ROOT = REPO_ROOT / "api"
ENGINE_ROOT = REPO_ROOT / "engine"


def _python_sources(root: Path) -> list[Path]:
    return sorted(path for path in root.rglob("*.py") if "__pycache__" not in path.parts)


class ApiBoundaryTests(unittest.TestCase):
    def test_requirements_contain_only_approved_backend_and_deployment_dependencies(self) -> None:
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

    def test_openapi_has_exactly_approved_routes(self) -> None:
        schema = app.openapi()

        self.assertEqual(schema["info"]["title"], "Codon Category Tracking API")
        self.assertEqual(schema["info"]["version"], "phase4-api-v1")
        self.assertEqual(
            set(schema["paths"]),
            {
                "/health",
                "/api/v1/metadata",
                "/api/v1/simulations/exact",
                "/api/v1/simulations/aggregated",
                "/api/v1/comparisons/exact",
                "/api/v1/comparisons/exact-vs-sampled",
                "/api/v1/jobs/exact",
                "/api/v1/jobs/aggregated",
                "/api/v1/jobs/comparisons/exact",
                "/api/v1/jobs/comparisons/exact-vs-sampled",
                "/api/v1/jobs/{job_id}",
                "/api/v1/jobs/{job_id}/result",
                "/api/v1/jobs/{job_id}/retry",
            },
        )

    def test_engine_fresh_import_does_not_load_api_or_ui_frameworks(self) -> None:
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

    def test_api_does_not_import_ui_or_root_research_modules(self) -> None:
        forbidden_roots = {"streamlit", "tkinter", "plotly", "PyQt5"}
        forbidden_modules = {"category_tracking", "category_tracking_web", "diagnose_category_tracking_web"}

        for source in _python_sources(API_ROOT):
            with self.subTest(source=source.name):
                tree = ast.parse(source.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported = {alias.name.split(".")[0] for alias in node.names}
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imported = {node.module.split(".")[0]}
                    else:
                        continue
                    self.assertFalse(forbidden_roots.intersection(imported))
                    self.assertFalse(forbidden_modules.intersection(imported))

    def test_api_does_not_call_legacy_detailed_or_exact_compatibility_paths(self) -> None:
        api_text = "\n".join(source.read_text(encoding="utf-8") for source in _python_sources(API_ROOT))

        self.assertNotIn("run_simulation", api_text)
        self.assertNotIn("run_experiment", api_text)
        self.assertNotIn("category_tracking.py", api_text)
        self.assertNotIn("category_tracking_web.py", api_text)

    def test_api_does_not_duplicate_biological_or_simulation_owners(self) -> None:
        forbidden_assignments = {
            "CODON_TABLE",
            "STOP_CODONS",
            "AA_PROPERTIES",
            "PROPERTY_LABELS",
            "PRESET_AT",
            "PRESET_AG",
            "PRESET_AC",
        }

        for source in _python_sources(API_ROOT):
            with self.subTest(source=source.name):
                tree = ast.parse(source.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Assign):
                        names = {
                            target.id
                            for target in node.targets
                            if isinstance(target, ast.Name)
                        }
                        self.assertFalse(forbidden_assignments.intersection(names))

    def test_engine_sources_do_not_import_phase4_web_dependencies(self) -> None:
        forbidden = {"fastapi", "starlette", "uvicorn", "httpx"}

        for source in _python_sources(ENGINE_ROOT):
            with self.subTest(source=source.name):
                tree = ast.parse(source.read_text(encoding="utf-8"))
                for node in ast.walk(tree):
                    if isinstance(node, ast.Import):
                        imported = {alias.name.split(".")[0] for alias in node.names}
                    elif isinstance(node, ast.ImportFrom) and node.module:
                        imported = {node.module.split(".")[0]}
                    else:
                        continue
                    self.assertFalse(forbidden.intersection(imported))


if __name__ == "__main__":
    unittest.main()
