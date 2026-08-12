"""Regression checks for the Streamlit category tracking web app.

Run:
    python diagnose_category_tracking_web.py
"""

from __future__ import annotations

import pandas as pd
from streamlit.testing.v1 import AppTest

from category_tracking import CODON_TABLE, VALID_CODONS, build_substitution_matrix, get_primary_group_name, run_simulation
from category_tracking_web import (
    all_codon_no_more_change,
    exact_no_more_change,
    exact_all_category_series,
    exact_start_trait_survival_series,
    exact_start_trait_stop_percentage_series,
    exact_trait_aa_survival_series,
    exact_trait_codon_survival_series,
    no_more_change_from_df,
    survival_balance_series,
    surviving_category_fraction_series,
    trait_codon_survival_summary,
)


APP_FILE = "category_tracking_web.py"


def run_case(name, mutate=None, timeout=60):
    app = AppTest.from_file(APP_FILE)
    app.run(timeout=timeout)
    if mutate:
        mutate(app)
        app.run(timeout=timeout)
    errors = [str(error.value) for error in app.exception]
    if errors:
        joined = "\n".join(errors)
        raise AssertionError(f"{name} failed with {len(errors)} exception(s):\n{joined}")
    print(f"PASS {name}")


def run_whole_population_trait_case(timeout=60):
    app = AppTest.from_file(APP_FILE)
    app.run(timeout=timeout)
    app.segmented_control[0].set_value("Whole population")
    app.run(timeout=timeout)
    app.selectbox[0].set_value("Polar uncharged")
    app.run(timeout=timeout)
    errors = [str(error.value) for error in app.exception]
    if errors:
        joined = "\n".join(errors)
        raise AssertionError(f"whole population trait selector failed:\n{joined}")
    print("PASS whole population trait selector")


def main():
    tolerance_df = pd.DataFrame([
        {"generation": 1, "category": "Hydrophobic", "value": 10.0},
        {"generation": 1, "category": "Polar uncharged", "value": 5.0},
        {"generation": 2, "category": "Hydrophobic", "value": 10.6},
        {"generation": 2, "category": "Polar uncharged", "value": 4.4},
        {"generation": 3, "category": "Hydrophobic", "value": 9.8},
        {"generation": 3, "category": "Polar uncharged", "value": 5.2},
    ])
    exact_gen, _ = no_more_change_from_df(tolerance_df, tolerance=1.0)
    strict_gen, _ = no_more_change_from_df(tolerance_df, tolerance=0.0)
    if exact_gen != "1" or strict_gen != "3":
        raise AssertionError(
            "Exact no-more-change tolerance failed: "
            f"tolerance=1 -> {exact_gen}, tolerance=0 -> {strict_gen}"
        )
    print("PASS no-more-change exact tolerance")

    labeled_generation_df = pd.DataFrame([
        {"generation": 2, "category": "Hydrophobic", "value": 10.0},
        {"generation": 4, "category": "Hydrophobic", "value": 8.0},
        {"generation": 6, "category": "Hydrophobic", "value": 8.0},
    ])
    start_gen, start_status = no_more_change_from_df(labeled_generation_df)
    if start_gen != "4" or not start_status.startswith("constant state starts"):
        raise AssertionError(
            "No-more-change should return the first generation label of the constant state: "
            f"{start_gen}, {start_status}"
        )
    print("PASS constant-state start generation")

    alpha_df = pd.DataFrame([
        {"generation": 1, "category": "Hydrophobic", "value": 0.500},
        {"generation": 1, "category": "Polar uncharged", "value": 0.500},
        {"generation": 2, "category": "Hydrophobic", "value": 0.5088},
        {"generation": 2, "category": "Polar uncharged", "value": 0.4912},
        {"generation": 3, "category": "Hydrophobic", "value": 0.5092},
        {"generation": 3, "category": "Polar uncharged", "value": 0.4908},
    ])
    loose_gen, _ = no_more_change_from_df(alpha_df, tolerance=0.01)
    strict_gen, _ = no_more_change_from_df(alpha_df, tolerance=0.001)
    if loose_gen != "1" or strict_gen != "2":
        raise AssertionError(
            "Alpha tolerance should define the start of the stable state: "
            f"alpha=0.01 -> {loose_gen}, alpha=0.001 -> {strict_gen}"
        )
    print("PASS alpha stable-state tolerance")

    fraction_source = pd.DataFrame([
        {"generation": 1, "category": "Hydrophobic", "value": 20.0},
        {"generation": 1, "category": "Polar uncharged", "value": 30.0},
        {"generation": 2, "category": "Hydrophobic", "value": 0.0},
        {"generation": 2, "category": "Polar uncharged", "value": 0.0},
    ])
    fraction_rows = surviving_category_fraction_series(fraction_source)
    totals = fraction_rows.groupby("generation")["value"].sum().round(8).to_dict()
    if totals != {1: 1.0, 2: 0.0}:
        raise AssertionError(f"Surviving-category fractions are wrong: {totals}")
    print("PASS surviving-category fractions")

    matrix = build_substitution_matrix(1 / 3, 1 / 3, 1 / 3)
    sim = run_simulation(4, matrix, {codon: 100 for codon in VALID_CODONS})
    stats = sim[8]
    track_data = sim[10]
    aggregate_counts = exact_all_category_series(track_data, 4)
    start_trait_survival = exact_start_trait_survival_series(track_data, 4)
    trait_codon_survival = exact_trait_codon_survival_series(track_data, "Hydrophobic", 4)
    trait_aa_survival = exact_trait_aa_survival_series(track_data, "Hydrophobic", 4)
    trait_summary = trait_codon_survival_summary(trait_codon_survival, 100)
    aggregate_fractions = surviving_category_fraction_series(aggregate_counts)
    live_generations = aggregate_counts.groupby("generation")["value"].sum()
    start_trait_live = start_trait_survival.groupby("generation")["value"].sum()
    if not live_generations.round(8).equals(start_trait_live.round(8)):
        raise AssertionError(
            "Start-trait survival totals should match aggregate live totals: "
            f"{live_generations.to_dict()} vs {start_trait_live.to_dict()}"
        )
    trait_codon_live = trait_codon_survival.groupby("generation")["value"].sum().round(8)
    trait_overview_live = (
        start_trait_survival[start_trait_survival["start_category"] == "Hydrophobic"]
        .set_index("generation")["value"]
        .round(8)
    )
    if not trait_codon_live.equals(trait_overview_live):
        raise AssertionError(
            "Selected-trait codon survival should match that trait's survival total: "
            f"{trait_codon_live.to_dict()} vs {trait_overview_live.to_dict()}"
        )
    codon_grouped_by_aa = (
        trait_codon_survival
        .groupby(["generation", "aa"])["value"]
        .sum()
        .round(8)
        .sort_index()
    )
    aa_survival = (
        trait_aa_survival
        .set_index(["generation", "aa"])["value"]
        .round(8)
        .sort_index()
    )
    if not codon_grouped_by_aa.equals(aa_survival):
        raise AssertionError("Trait AA survival should equal codon survival grouped by AA.")
    if trait_summary.empty or trait_summary["final_surviving"].iloc[0] < trait_summary["final_surviving"].iloc[-1]:
        raise AssertionError("Trait codon survival summary should be sorted by final survivors.")
    stop_check = (
        trait_summary["final_surviving"] +
        trait_summary["stopped"]
    ).round(8).unique().tolist()
    if stop_check != [100.0]:
        raise AssertionError(f"Trait codon stop summary should conserve starting copies: {stop_check}")
    aggregate_totals = aggregate_fractions.groupby("generation")["value"].sum()
    for gen, total in aggregate_totals.items():
        expected = 1.0 if live_generations.loc[gen] > 0 else 0.0
        if round(float(total), 8) != expected:
            raise AssertionError(
                f"Aggregate surviving fractions should sum to {expected} at gen {gen}, got {total}"
            )
    survival_rows = survival_balance_series(
        aggregate_counts,
        stats["total_start_copies"],
    )
    survival_totals = survival_rows.groupby("generation")["value"].sum().round(8).to_dict()
    expected_total = round(float(stats["total_start_copies"]), 8)
    if any(total != expected_total for total in survival_totals.values()):
        raise AssertionError(f"Aggregate survival balance does not conserve total: {survival_totals}")

    stop_percentages = exact_start_trait_stop_percentage_series(track_data, 4, 100)
    final_stop_percentages = (
        stop_percentages[stop_percentages["generation"] == 4]
        .set_index("start_category")
    )
    final_trait_survival = (
        start_trait_survival[start_trait_survival["generation"] == 4]
        .set_index("start_category")["value"]
    )
    start_totals_by_trait = pd.Series({
        trait: sum(1 for codon in VALID_CODONS if get_primary_group_name(CODON_TABLE[codon]) == trait) * 100.0
        for trait in final_stop_percentages.index
    })
    expected_stop_percentages = (
        (start_totals_by_trait - final_trait_survival).clip(lower=0) /
        start_totals_by_trait.where(start_totals_by_trait > 0)
    ).fillna(0.0)
    if not final_stop_percentages["value"].round(8).equals(expected_stop_percentages.round(8)):
        raise AssertionError(
            "Stop percentages by starting trait should match missing survivors: "
            f"{final_stop_percentages['value'].to_dict()} vs {expected_stop_percentages.to_dict()}"
        )
    print("PASS aggregate all-codon population series")

    sampled_rows = all_codon_no_more_change([], track_data, 4, "Sampled copies")
    exact_rows = all_codon_no_more_change([], track_data, 4, "Exact probability")
    if not sampled_rows[["codon", "no_more_change", "status"]].equals(
        exact_rows[["codon", "no_more_change", "status"]]
    ):
        raise AssertionError("Sampled and exact no-more-change values drifted apart.")
    print("PASS no-more-change shared exact source")

    fraction_gen, fraction_status = exact_no_more_change(
        track_data,
        "TGG",
        4,
        "Exact surviving trait fractions",
    )
    if not fraction_gen or not fraction_status:
        raise AssertionError("Surviving-fraction no-more-change basis returned an empty result.")
    print("PASS surviving-fraction no-more-change basis")

    run_case("default render")
    run_case("whole population workspace", lambda app: app.segmented_control[0].set_value("Whole population"))
    run_whole_population_trait_case()
    run_case("preset mode", lambda app: app.segmented_control[1].set_value("Preset"))
    run_case("compare both mode", lambda app: app.segmented_control[1].set_value("Compare both"))
    run_case("exact probability mode", lambda app: app.segmented_control[2].set_value("Exact probability"))
    run_case(
        "surviving-fraction no-more-change mode",
        lambda app: app.segmented_control[3].set_value("Exact surviving trait fractions"),
    )
    run_case(
        "surviving-fraction alpha input",
        lambda app: (
            app.segmented_control[3].set_value("Exact surviving trait fractions"),
            app.number_input[3].set_value(0.02),
        ),
    )
    run_case("selected codon TGG", lambda app: app.selectbox[0].set_value("TGG"))
    run_case("invalid probability handled", lambda app: app.text_input[0].set_value("abc"))


if __name__ == "__main__":
    main()
