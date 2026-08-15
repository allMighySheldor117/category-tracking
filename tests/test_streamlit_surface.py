"""Frozen Streamlit, accessibility, query-binding, and cache contracts.

The fixture is reviewed static data. This module reads it but never generates
or updates it.
"""

from __future__ import annotations

import json
import random
import tomllib
import unittest
from pathlib import Path
from typing import Any

from streamlit.testing.v1 import AppTest

import category_tracking as legacy
import category_tracking_web as web
from tests.test_baseline_behavior import structural_digest


APP_DIR = Path(__file__).parents[1]
APP_FILE = APP_DIR / "category_tracking_web.py"
FIXTURE_PATH = Path(__file__).parent / "fixtures" / "phase1_streamlit_surface.json"
SCIENTIFIC_FIXTURE_PATH = Path(__file__).parent / "fixtures" / "phase1_scientific_baseline.json"


def widget_contract(widget: Any, fields: tuple[str, ...]) -> dict[str, Any]:
    return {field: getattr(widget, field) for field in fields}


def chart_contract(app: AppTest) -> list[dict[str, Any]]:
    charts = []
    for element in app.get("plotly_chart"):
        spec = json.loads(element.proto.spec)
        charts.append(
            {
                "title": spec.get("layout", {}).get("title", {}).get("text"),
                "trace_names": [trace.get("name") for trace in spec.get("data", [])],
            }
        )
    return charts


def click_run_analysis(app: AppTest) -> AppTest:
    app.button(key="run_analysis").click()
    return app.run(timeout=120)


class StreamlitSurfaceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.fixture = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
        cls.scientific_fixture = json.loads(
            SCIENTIFIC_FIXTURE_PATH.read_text(encoding="utf-8")
        )
        cls.default_app = AppTest.from_file(str(APP_FILE)).run(timeout=120)

    def test_default_widget_and_presentation_surface(self) -> None:
        app = self.default_app
        page = self.fixture["page"]
        self.assertEqual([item.value for item in app.title], [page["title"]])
        self.assertEqual(app.caption[0].value, page["caption"])
        self.assertEqual([item.value for item in app.header], [page["header"]])
        self.assertEqual(len(app.exception), page["default_exception_count"])
        self.assertEqual(len(app.error), page["default_error_count"])
        self.assertEqual(len(app.get("plotly_chart")), 0)
        self.assertEqual(len(app.dataframe), 0)
        self.assertIn("run_analysis", [button.key for button in app.button])

        segmented = [
            widget_contract(item, ("type", "label", "key", "value", "options"))
            for item in app.segmented_control
        ]
        self.assertEqual(segmented, self.fixture["segmented_controls"])

        number_inputs = [
            widget_contract(item, ("label", "value", "min", "max", "step"))
            for item in app.number_input
        ]
        self.assertEqual(number_inputs, self.fixture["number_inputs"])

        text_inputs = [
            widget_contract(item, ("label", "key", "value", "placeholder"))
            for item in app.text_input
        ]
        self.assertEqual(text_inputs, self.fixture["text_inputs"])

        self.assertEqual(len(app.selectbox), len(self.fixture["selectboxes"]))
        expected_options = [web.codon_label(codon) for codon in legacy.VALID_CODONS]
        for widget, expected in zip(app.selectbox, self.fixture["selectboxes"]):
            observed = {
                "label": widget.label,
                "key": widget.key,
                "value": widget.value,
                "option_count": len(widget.options),
                "first_option": widget.options[0],
                "last_option": widget.options[-1],
            }
            self.assertEqual(observed, expected)
            self.assertEqual(list(widget.options), expected_options)

        self.assertEqual(len(app.slider), 1)
        self.assertEqual(
            widget_contract(app.slider[0], ("label", "value", "min", "max", "step")),
            self.fixture["slider"],
        )

    def test_whole_population_surface(self) -> None:
        app = AppTest.from_file(str(APP_FILE)).run(timeout=120)
        app.segmented_control[0].set_value("Whole population")
        app.run(timeout=120)
        click_run_analysis(app)
        expected = self.fixture["whole_population"]
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("plotly_chart")), expected["plotly_count"])
        self.assertEqual(len(app.dataframe), expected["dataframe_count"])
        self.assertEqual([item.value for item in app.subheader], expected["subheaders"])
        trait_widget = app.selectbox[0]
        self.assertEqual(
            widget_contract(trait_widget, ("label", "key", "value", "options")),
            expected["trait_selectbox"],
        )
        self.assertEqual(chart_contract(app), expected["charts"])

    def test_query_parameter_bindings(self) -> None:
        expected = self.fixture["query_binding"]
        app = AppTest.from_file(str(APP_FILE))
        for key, value in expected["injected"].items():
            app.query_params[key] = value
        app.run(timeout=120)
        click_run_analysis(app)
        self.assertFalse(app.exception)
        self.assertEqual(dict(app.query_params), expected["retained_query_params"])
        self.assertEqual(
            [item.value for item in app.segmented_control],
            expected["segmented_values"],
        )
        self.assertEqual([item.value for item in app.selectbox], expected["selectbox_values"])

    def test_invalid_probability_message(self) -> None:
        app = AppTest.from_file(str(APP_FILE)).run(timeout=120)
        app.text_input[0].set_value("abc")
        app.run(timeout=120)
        self.assertFalse(app.exception)
        self.assertEqual(
            [item.value for item in app.error],
            [self.fixture["invalid_probability_error"]],
        )

    def test_cloud_safe_initial_load_waits_for_explicit_run(self) -> None:
        app = AppTest.from_file(str(APP_FILE)).run(timeout=120)
        self.assertFalse(app.exception)
        button_keys = [button.key for button in app.button]
        self.assertIn("run_analysis", button_keys)
        self.assertEqual(len(app.get("plotly_chart")), 0)
        self.assertEqual(len(app.dataframe), 0)

        captions = [item.value for item in app.caption]
        self.assertIn(
            "Press Run analysis to compute charts and tables for the current sidebar settings.",
            captions,
        )

        app.segmented_control[1].set_value("Compare both")
        app.run(timeout=120)
        self.assertFalse(app.exception)
        self.assertEqual(len(app.get("plotly_chart")), 0)
        self.assertEqual(len(app.dataframe), 0)

    def test_explicit_run_renders_accepted_default_results(self) -> None:
        app = AppTest.from_file(str(APP_FILE)).run(timeout=120)
        app.button(key="run_analysis").click()
        app.run(timeout=120)
        self.assertFalse(app.exception)
        page = self.fixture["page"]
        self.assertEqual(len(app.get("plotly_chart")), page["default_plotly_count"])
        self.assertEqual(len(app.dataframe), page["default_dataframe_count"])
        self.assertEqual(list(app.dataframe[0].value.shape), page["default_dataframe_shape"])
        self.assertEqual(
            list(app.dataframe[0].value.columns),
            page["default_dataframe_columns"],
        )
        self.assertEqual(chart_contract(app), self.fixture["default_charts"])
        captions = [item.value for item in app.caption]
        runtime_caption = next(
            (caption for caption in captions if caption.startswith("Analysis runtime:")),
            None,
        )
        self.assertIsNotNone(runtime_caption)
        self.assertRegex(runtime_caption, r"^Analysis runtime: \d+\.\d{2} s$")

    def test_analysis_runtime_is_reported_in_sidebar(self) -> None:
        app = AppTest.from_file(str(APP_FILE)).run(timeout=120)
        app.button(key="run_analysis").click()
        app.run(timeout=120)
        self.assertFalse(app.exception)
        captions = [item.value for item in app.caption]
        runtime_caption = next(
            (caption for caption in captions if caption.startswith("Analysis runtime:")),
            None,
        )
        self.assertIsNotNone(runtime_caption)
        self.assertRegex(runtime_caption, r"^Analysis runtime: \d+\.\d{2} s$")

    def test_compare_both_no_more_change_uses_side_by_side_panels(self) -> None:
        app = AppTest.from_file(str(APP_FILE)).run(timeout=120)
        app.segmented_control[1].set_value("Compare both")
        app.run(timeout=120)
        click_run_analysis(app)
        self.assertFalse(app.exception)

        no_more_specs = []
        for element in app.get("plotly_chart"):
            spec = json.loads(element.proto.spec)
            title = spec.get("layout", {}).get("title", {}).get("text")
            if title == "No more category change by starting codon":
                no_more_specs.append(spec)

        self.assertEqual(len(no_more_specs), 2)
        for spec in no_more_specs:
            trace_names = {trace.get("name") for trace in spec.get("data", [])}
            self.assertFalse(
                {"User probability", "Preset probability"} & trace_names,
                trace_names,
            )

        comparison_tables = [
            dataframe.value
            for dataframe in app.dataframe
            if "no_more_change" in dataframe.value.columns
        ]
        self.assertEqual(len(comparison_tables), 2)
        self.assertTrue(
            all("probability" not in table.columns for table in comparison_tables)
        )

        subheaders = [item.value for item in app.subheader]
        summary_index = subheaders.index("No more category change for all starting codons")
        self.assertEqual(
            subheaders[summary_index + 1: summary_index + 3],
            ["User probability", "Preset probability"],
        )

    def test_compare_both_no_more_change_has_fullscreen_action(self) -> None:
        app = AppTest.from_file(str(APP_FILE)).run(timeout=120)
        app.segmented_control[1].set_value("Compare both")
        app.run(timeout=120)
        click_run_analysis(app)
        self.assertFalse(app.exception)

        button_keys = [button.key for button in app.button]
        self.assertIn("compare_no_more_change_fullscreen", button_keys)

        app.button(key="compare_no_more_change_fullscreen").click()
        app.run(timeout=120)
        self.assertFalse(app.exception)

        subheaders = [item.value for item in app.subheader]
        self.assertIn("No more category change", subheaders)
        fullscreen_index = subheaders.index("No more category change")
        self.assertEqual(
            subheaders[fullscreen_index + 1: fullscreen_index + 3],
            ["User probability", "Preset probability"],
        )

        no_more_specs = []
        for element in app.get("plotly_chart"):
            spec = json.loads(element.proto.spec)
            title = spec.get("layout", {}).get("title", {}).get("text")
            if title == "No more category change by starting codon":
                no_more_specs.append(spec)
        self.assertGreaterEqual(len(no_more_specs), 4)

    def test_whole_population_compare_sections_have_fullscreen_actions(self) -> None:
        app = AppTest.from_file(str(APP_FILE)).run(timeout=120)
        app.segmented_control[0].set_value("Whole population")
        app.segmented_control[1].set_value("Compare both")
        app.run(timeout=120)
        click_run_analysis(app)
        self.assertFalse(app.exception)

        button_keys = [button.key for button in app.button]
        self.assertIn("compare_all_population_fullscreen", button_keys)
        self.assertIn("compare_trait_survival_fullscreen", button_keys)

        app.button(key="compare_all_population_fullscreen").click()
        app.run(timeout=120)
        self.assertFalse(app.exception)

        subheaders = [item.value for item in app.subheader]
        self.assertIn("All-codon population overview", subheaders)
        self.assertGreaterEqual(subheaders.count("User probability"), 2)
        self.assertGreaterEqual(subheaders.count("Preset probability"), 2)

    def test_codon_focus_compare_pair_has_section_fullscreen_action(self) -> None:
        app = AppTest.from_file(str(APP_FILE)).run(timeout=120)
        app.segmented_control[1].set_value("Compare both")
        app.run(timeout=120)
        click_run_analysis(app)
        self.assertFalse(app.exception)

        button_keys = [button.key for button in app.button]
        self.assertIn("compare_codon_focus_fullscreen", button_keys)

        app.button(key="compare_codon_focus_fullscreen").click()
        app.run(timeout=120)
        self.assertFalse(app.exception)

        subheaders = [item.value for item in app.subheader]
        self.assertIn("Codon focus comparison", subheaders)
        fullscreen_index = subheaders.index("Codon focus comparison")
        self.assertEqual(
            subheaders[fullscreen_index + 1: fullscreen_index + 3],
            ["User probability", "Preset probability"],
        )

    def test_accessibility_and_theme_contract(self) -> None:
        source = APP_FILE.read_text(encoding="utf-8")
        for snippet in self.fixture["accessibility_source_contract"]:
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, source)
        with (APP_DIR / ".streamlit" / "config.toml").open("rb") as stream:
            theme = tomllib.load(stream)["theme"]
        for key, expected in self.fixture["theme"].items():
            with self.subTest(theme_key=key):
                self.assertEqual(theme[key], expected)

    def test_phase7_visual_contract_polish_markers(self) -> None:
        source = APP_FILE.read_text(encoding="utf-8")
        for snippet in (
            "phase7-product-hero",
            "phase7-sidebar-guide",
            "phase7-result-context",
            "phase7-chart-shell",
            "phase7-table-context",
        ):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, source)

        app = self.default_app
        captions = [item.value for item in app.caption]
        self.assertIn(
            "Configure once in the sidebar; the visible workspace updates together.",
            captions,
        )
        self.assertIn(
            "Charts and tables below preserve the accepted Phase 6 data display.",
            captions,
        )
        page_text = "\n".join(item.value for item in app.text)
        self.assertNotIn("STREAMLIT PRODUCT WORKSPACE", page_text)

    def test_phase8_guided_ux_contract_markers(self) -> None:
        source = APP_FILE.read_text(encoding="utf-8")
        for snippet in (
            "phase8-guided-intro",
            "phase8-sidebar-mode-guide",
            "phase8-run-guidance",
            "phase8-result-interpretation",
            "phase8-error-guidance",
        ):
            with self.subTest(snippet=snippet):
                self.assertIn(snippet, source)

        app = self.default_app
        captions = [item.value for item in app.caption]
        for expected in (
            "Configure → Run → Inspect: set the sidebar once, then read each result section from top to bottom.",
            "Your probability and Preset use the same controls so Compare both stays honest.",
            "Exact probability is deterministic; Sampled copies is the stochastic copy simulation.",
            "Use these results as a guided reading path: first the headline metrics, then the charts, then the tables.",
        ):
            with self.subTest(caption=expected):
                self.assertIn(expected, captions)

    def test_run_cached_hit_miss_and_rng_contract(self) -> None:
        expected = self.scientific_fixture["cache_contract"]
        web.run_cached.clear()

        random.seed(12345)
        before_miss = random.getstate()
        first = web.run_cached(*expected["arguments"])
        after_miss = random.getstate()

        random.seed(54321)
        before_hit = random.getstate()
        second = web.run_cached(*expected["arguments"])
        after_hit = random.getstate()

        self.assertEqual(first, second)
        self.assertEqual(structural_digest(first), expected["result_digest"])
        self.assertEqual(structural_digest(before_miss), expected["before_miss_digest"])
        self.assertEqual(structural_digest(after_miss), expected["after_miss_digest"])
        self.assertEqual(structural_digest(before_hit), expected["before_hit_digest"])
        self.assertEqual(structural_digest(after_hit), expected["after_hit_digest"])
        self.assertEqual(before_miss != after_miss, expected["miss_changes_rng"])
        self.assertEqual(before_hit == after_hit, expected["hit_preserves_rng"])


if __name__ == "__main__":
    unittest.main()
