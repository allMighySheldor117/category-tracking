"""Fresh-process completion gates for the Phase 1 architecture."""

from __future__ import annotations

import hashlib
import subprocess
import sys
import unittest
from pathlib import Path


APP_ROOT = Path(__file__).parents[1].resolve()
WORKSPACE_ROOT = APP_ROOT.parent
FORBIDDEN_UI_MODULES = {"streamlit", "tkinter", "plotly", "PyQt5"}


def run_fresh(command: str) -> subprocess.CompletedProcess[str]:
    """Run one boundary assertion without inherited application imports."""
    return subprocess.run(
        [sys.executable, "-c", command],
        cwd=APP_ROOT,
        check=False,
        capture_output=True,
        text=True,
    )


class Phase1BoundaryTests(unittest.TestCase):
    def assert_fresh_passes(self, command: str) -> None:
        completed = run_fresh(command)
        self.assertEqual(completed.returncode, 0, completed.stderr or completed.stdout)

    def test_every_engine_module_import_is_ui_independent(self) -> None:
        modules = (
            "engine",
            "engine.models",
            "engine.genetic_code",
            "engine.mutation_matrix",
            "engine.exact_tracking",
            "engine.sampled_tracking",
            "engine.category_analysis",
            "engine.summaries",
        )
        module_list = repr(modules)
        forbidden = repr(FORBIDDEN_UI_MODULES)
        self.assert_fresh_passes(
            "import importlib, sys; "
            f"[importlib.import_module(name) for name in {module_list}]; "
            f"forbidden={forbidden}; "
            "assert not forbidden.intersection(sys.modules), forbidden.intersection(sys.modules)"
        )

    def test_web_import_does_not_cross_the_tkinter_adapter_boundary(self) -> None:
        self.assert_fresh_passes(
            "import sys, category_tracking_web; "
            "assert 'category_tracking' not in sys.modules; "
            "assert 'tkinter' not in sys.modules"
        )

    def test_application_modules_resolve_inside_final_code(self) -> None:
        self.assert_fresh_passes(
            "from pathlib import Path; "
            "import category_tracking, category_tracking_web, engine; "
            "root=Path.cwd().resolve(); "
            "modules=(category_tracking, category_tracking_web, engine); "
            "assert all(root in Path(module.__file__).resolve().parents for module in modules)"
        )

    def test_engine_and_adapters_import_without_cycles(self) -> None:
        orders = (
            ("engine", "category_tracking", "category_tracking_web"),
            ("category_tracking_web", "engine", "category_tracking"),
            ("category_tracking", "engine", "category_tracking_web"),
        )
        for order in orders:
            with self.subTest(order=order):
                self.assert_fresh_passes(
                    "import importlib; "
                    f"[importlib.import_module(name) for name in {order!r}]"
                )

    def test_frozen_diagnostics_and_fixtures_keep_step1_hashes(self) -> None:
        expected = {
            APP_ROOT / "diagnose_category_tracking_web.py": "03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4",
            APP_ROOT / "tests" / "compat" / "diagnose_category_tracking_web_phase1_baseline.py": "03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4",
            APP_ROOT / "tests" / "fixtures" / "phase1_scientific_baseline.json": "96c75420dbde1ccc497fe05419a163703e0ca251b7c466ed8b976bdbad3ed95b",
            APP_ROOT / "tests" / "fixtures" / "phase1_streamlit_surface.json": "4e4b1ce860cd07bc495b818f99e3f873a463e482005756e39f0041db48fb1035",
        }
        for path, digest in expected.items():
            with self.subTest(path=path.name):
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)

    def test_root_research_application_files_keep_step1_hashes(self) -> None:
        expected = {
            WORKSPACE_ROOT / "category_tracking.py": "7f017a872252450fb10546b3d9f4d6de4f98e0d513f047e32dd1a48643cb47de",
            WORKSPACE_ROOT / "category_tracking_web.py": "eb04c1e6e1e1272a8cbf84ef5e8543b13fcf6ae7e1783aeacd709ad3073441e8",
            WORKSPACE_ROOT / "diagnose_category_tracking_web.py": "03e67dce0f254323debc3dbfa3d257f9a749909ffa989721d7ddc4ac42bd59a4",
        }
        for path, digest in expected.items():
            with self.subTest(path=path.name):
                self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(), digest)


if __name__ == "__main__":
    unittest.main()
