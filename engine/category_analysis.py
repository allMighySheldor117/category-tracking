"""Pure category, trait, survival, and denominator analysis."""

from __future__ import annotations

import collections
from typing import Any, Iterable, TypeAlias

import pandas as pd

from .genetic_code import (
    CODON_TABLE,
    PROPERTY_LABELS,
    STOP_CODONS,
    VALID_CODONS,
    get_primary_group,
    get_primary_group_name,
)
from .models import (
    AggregatedSampledResult,
    ExactSimulationResult,
    SampledSimulationResult,
    StartScope,
)


Record: TypeAlias = dict[str, Any]
RecordsInput: TypeAlias = SampledSimulationResult | Iterable[Record]
TrackInput: TypeAlias = ExactSimulationResult | dict[str, Any]
CATEGORY_NAMES = PROPERTY_LABELS


def _records(source: RecordsInput) -> Iterable[Record]:
    if isinstance(source, SampledSimulationResult):
        return source.records
    return source


def _track_data(source: TrackInput) -> dict[str, Any]:
    if isinstance(source, ExactSimulationResult):
        return source.track_data
    return source


def sampled_category_series(records: RecordsInput, codon: str, n_gen: int) -> pd.DataFrame:
    rows = []
    codon_records = [record for record in _records(records) if record.get("start") == codon]
    for gen in range(1, n_gen + 1):
        counts = collections.Counter()
        for record in codon_records:
            path = record.get("path", [])
            if len(path) <= gen:
                continue
            current = path[gen]
            if current in STOP_CODONS:
                continue
            counts[CATEGORY_NAMES[get_primary_group(CODON_TABLE[current])]] += 1
        for category in CATEGORY_NAMES.values():
            rows.append({"generation": gen, "category": category, "value": counts[category]})
    return pd.DataFrame(rows)


def exact_category_series(track_data: TrackInput, codon: str, n_gen: int) -> pd.DataFrame:
    rows = []
    per_gen = _track_data(track_data)["per_gen_codon_from"]
    for gen in range(n_gen):
        counts = collections.Counter()
        for current_codon, weight in per_gen[gen].get(codon, {}).items():
            counts[CATEGORY_NAMES[get_primary_group(CODON_TABLE[current_codon])]] += weight
        for category in CATEGORY_NAMES.values():
            rows.append({"generation": gen + 1, "category": category, "value": counts[category]})
    return pd.DataFrame(rows)


def sampled_all_category_series(records: RecordsInput, n_gen: int) -> pd.DataFrame:
    rows = []
    sampled_records = list(_records(records))
    for gen in range(1, n_gen + 1):
        counts = collections.Counter()
        for record in sampled_records:
            path = record.get("path", [])
            if len(path) <= gen:
                continue
            current = path[gen]
            if current in STOP_CODONS:
                continue
            counts[CATEGORY_NAMES[get_primary_group(CODON_TABLE[current])]] += 1
        for category in CATEGORY_NAMES.values():
            rows.append({"generation": gen, "category": category, "value": counts[category]})
    return pd.DataFrame(rows)


def exact_all_category_series(track_data: TrackInput, n_gen: int) -> pd.DataFrame:
    rows = []
    per_gen = _track_data(track_data)["per_gen_codon_from"]
    for gen in range(n_gen):
        counts = collections.Counter()
        for start_counts in per_gen[gen].values():
            for current_codon, weight in start_counts.items():
                counts[CATEGORY_NAMES[get_primary_group(CODON_TABLE[current_codon])]] += weight
        for category in CATEGORY_NAMES.values():
            rows.append({"generation": gen + 1, "category": category, "value": counts[category]})
    return pd.DataFrame(rows)


def sampled_start_trait_survival_series(records: RecordsInput, n_gen: int) -> pd.DataFrame:
    rows = []
    sampled_records = list(_records(records))
    for gen in range(1, n_gen + 1):
        counts = collections.Counter()
        for record in sampled_records:
            start_category = get_primary_group_name(record.get("start_aa"))
            path = record.get("path", [])
            if len(path) <= gen or path[gen] in STOP_CODONS:
                continue
            counts[start_category] += 1
        for category in CATEGORY_NAMES.values():
            rows.append({"generation": gen, "start_category": category, "value": counts[category]})
    return pd.DataFrame(rows)


def exact_start_trait_survival_series(track_data: TrackInput, n_gen: int) -> pd.DataFrame:
    rows = []
    per_gen = _track_data(track_data)["per_gen_codon_from"]
    for gen in range(n_gen):
        counts = collections.Counter()
        for start_codon, start_counts in per_gen[gen].items():
            start_category = get_primary_group_name(CODON_TABLE[start_codon])
            counts[start_category] += sum(start_counts.values())
        for category in CATEGORY_NAMES.values():
            rows.append({"generation": gen + 1, "start_category": category, "value": counts[category]})
    return pd.DataFrame(rows)


def sampled_start_trait_stop_percentage_series(records: RecordsInput, n_gen: int) -> pd.DataFrame:
    rows = []
    sampled_records = list(_records(records))
    totals = collections.Counter(
        get_primary_group_name(record.get("start_aa")) for record in sampled_records
    )
    stop_generations = collections.Counter()
    for record in sampled_records:
        if record.get("hit_stop") and record.get("stop_gen"):
            start_category = get_primary_group_name(record.get("start_aa"))
            stop_generations[(int(record["stop_gen"]), start_category)] += 1

    cumulative = collections.Counter()
    for gen in range(1, n_gen + 1):
        for category in CATEGORY_NAMES.values():
            cumulative[category] += stop_generations[(gen, category)]
            total = float(totals[category])
            stopped = float(cumulative[category])
            rows.append(
                {
                    "generation": gen,
                    "start_category": category,
                    "value": stopped / total if total else 0.0,
                    "stopped": stopped,
                    "total": total,
                }
            )
    return pd.DataFrame(rows)


def exact_start_trait_stop_percentage_series(
    track_data: TrackInput,
    n_gen: int,
    copies_per_codon: float,
) -> pd.DataFrame:
    rows = []
    per_gen_stops = _track_data(track_data)["per_gen_stop_codon_from"]
    totals = collections.Counter()
    for codon in VALID_CODONS:
        totals[get_primary_group_name(CODON_TABLE[codon])] += float(copies_per_codon)

    cumulative = collections.Counter()
    for gen in range(n_gen):
        for start_codon, stop_weight in per_gen_stops[gen].items():
            start_category = get_primary_group_name(CODON_TABLE[start_codon])
            cumulative[start_category] += float(stop_weight)
        for category in CATEGORY_NAMES.values():
            total = float(totals[category])
            stopped = float(cumulative[category])
            rows.append(
                {
                    "generation": gen + 1,
                    "start_category": category,
                    "value": stopped / total if total else 0.0,
                    "stopped": stopped,
                    "total": total,
                }
            )
    return pd.DataFrame(rows)


def codons_for_trait(trait: str) -> list[str]:
    return [
        codon
        for codon in VALID_CODONS
        if get_primary_group_name(CODON_TABLE[codon]) == trait
    ]


def sampled_trait_codon_survival_series(
    records: RecordsInput,
    trait: str,
    n_gen: int,
) -> pd.DataFrame:
    rows = []
    trait_codons = codons_for_trait(trait)
    trait_codon_set = set(trait_codons)
    sampled_records = [
        record for record in _records(records) if record.get("start") in trait_codon_set
    ]
    for gen in range(1, n_gen + 1):
        counts = collections.Counter()
        for record in sampled_records:
            path = record.get("path", [])
            if len(path) <= gen or path[gen] in STOP_CODONS:
                continue
            counts[record.get("start")] += 1
        for codon in trait_codons:
            rows.append(
                {
                    "generation": gen,
                    "codon": codon,
                    "aa": CODON_TABLE[codon],
                    "value": counts[codon],
                }
            )
    return pd.DataFrame(rows)


def exact_trait_codon_survival_series(
    track_data: TrackInput,
    trait: str,
    n_gen: int,
) -> pd.DataFrame:
    rows = []
    trait_codons = codons_for_trait(trait)
    per_gen = _track_data(track_data)["per_gen_codon_from"]
    for gen in range(n_gen):
        for codon in trait_codons:
            rows.append(
                {
                    "generation": gen + 1,
                    "codon": codon,
                    "aa": CODON_TABLE[codon],
                    "value": sum(per_gen[gen].get(codon, {}).values()),
                }
            )
    return pd.DataFrame(rows)


def sampled_trait_aa_survival_series(
    records: RecordsInput,
    trait: str,
    n_gen: int,
) -> pd.DataFrame:
    rows = []
    trait_codons = set(codons_for_trait(trait))
    trait_aas = sorted({CODON_TABLE[codon] for codon in trait_codons})
    sampled_records = [
        record for record in _records(records) if record.get("start") in trait_codons
    ]
    for gen in range(1, n_gen + 1):
        counts = collections.Counter()
        for record in sampled_records:
            path = record.get("path", [])
            if len(path) <= gen or path[gen] in STOP_CODONS:
                continue
            counts[record.get("start_aa")] += 1
        for amino_acid in trait_aas:
            rows.append({"generation": gen, "aa": amino_acid, "value": counts[amino_acid]})
    return pd.DataFrame(rows)


def exact_trait_aa_survival_series(
    track_data: TrackInput,
    trait: str,
    n_gen: int,
) -> pd.DataFrame:
    rows = []
    trait_codons = codons_for_trait(trait)
    trait_aas = sorted({CODON_TABLE[codon] for codon in trait_codons})
    per_gen = _track_data(track_data)["per_gen_codon_from"]
    for gen in range(n_gen):
        counts = collections.Counter()
        for codon in trait_codons:
            counts[CODON_TABLE[codon]] += sum(per_gen[gen].get(codon, {}).values())
        for amino_acid in trait_aas:
            rows.append({"generation": gen + 1, "aa": amino_acid, "value": counts[amino_acid]})
    return pd.DataFrame(rows)


def surviving_category_fraction_series(cat_df: pd.DataFrame) -> pd.DataFrame:
    df = cat_df.copy()
    totals = df.groupby("generation")["value"].transform("sum")
    df["surviving"] = totals
    df["value"] = (df["value"] / totals.where(totals > 0)).fillna(0.0)
    return df


def survival_balance_series(cat_df: pd.DataFrame, total_start_copies: float) -> pd.DataFrame:
    live_by_generation = cat_df.groupby("generation", as_index=False)["value"].sum()
    rows = []
    for item in live_by_generation.itertuples(index=False):
        surviving = float(item.value)
        stopped = max(0.0, float(total_start_copies) - surviving)
        rows.append({"generation": item.generation, "state": "Surviving", "value": surviving})
        rows.append({"generation": item.generation, "state": "Stopped", "value": stopped})
    return pd.DataFrame(rows)


def trait_codon_survival_summary(
    df: pd.DataFrame,
    copies_per_codon: float,
) -> pd.DataFrame:
    if df.empty:
        return pd.DataFrame(
            columns=["codon", "aa", "final_surviving", "stopped", "stop_fraction"]
        )
    final_generation = df["generation"].max()
    summary = df[df["generation"] == final_generation].copy()
    summary = summary.rename(columns={"value": "final_surviving"})
    summary["stopped"] = (
        float(copies_per_codon) - summary["final_surviving"]
    ).clip(lower=0)
    if copies_per_codon > 0:
        summary["stop_fraction"] = summary["stopped"] / float(copies_per_codon)
    else:
        summary["stop_fraction"] = 0.0
    return (
        summary[["codon", "aa", "final_surviving", "stopped", "stop_fraction"]]
        .sort_values(
            ["final_surviving", "stop_fraction", "codon"],
            ascending=[False, True, True],
        )
        .reset_index(drop=True)
    )


def _aggregated_frame(
    rows: Iterable[dict[str, Any]],
    schema: tuple[tuple[str, str], ...],
    integer_columns: set[str],
) -> pd.DataFrame:
    from .exact_analysis import _typed_frame

    aggregated_schema = tuple(
        (column, "int64" if column in integer_columns else dtype)
        for column, dtype in schema
    )
    return _typed_frame(rows, aggregated_schema)


def get_aggregated_category_metrics(
    result: AggregatedSampledResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame:
    """Return canonical live category counts for one sampled start scope."""
    from .exact_analysis import CATEGORY_SCHEMA, _scope_start_codons

    start_codons = _scope_start_codons(start_scope, start_key)
    rows: list[dict[str, Any]] = []
    for snapshot in result.generations:
        if start_scope == "population":
            counts = snapshot.live_category
        else:
            counts: collections.Counter[str] = collections.Counter()
            for start_codon in start_codons:
                for current_codon, count in snapshot.current_codon_by_start_codon[
                    start_codon
                ].items():
                    current_aa = CODON_TABLE[current_codon]
                    counts[get_primary_group_name(current_aa)] += count
        for category in PROPERTY_LABELS.values():
            rows.append(
                {
                    "generation": snapshot.generation,
                    "start_scope": start_scope,
                    "start_key": start_key,
                    "category": category,
                    "live_value": int(counts[category]),
                    "value_kind": "copy_count",
                }
            )
    return _aggregated_frame(rows, CATEGORY_SCHEMA, {"live_value"})


def get_aggregated_survivor_fractions(
    result: AggregatedSampledResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame:
    """Return sampled category fractions among survivors in one start scope."""
    from .exact_analysis import FRACTION_SCHEMA

    categories = get_aggregated_category_metrics(
        result,
        start_scope=start_scope,
        start_key=start_key,
    )
    rows: list[dict[str, Any]] = []
    for generation in range(1, result.n_generations + 1):
        generation_rows = categories[categories["generation"] == generation]
        denominator = int(generation_rows["live_value"].sum())
        for row in generation_rows.itertuples(index=False):
            numerator = int(row.live_value)
            rows.append(
                {
                    "generation": generation,
                    "start_scope": start_scope,
                    "start_key": start_key,
                    "category": row.category,
                    "numerator": numerator,
                    "denominator": denominator,
                    "fraction": numerator / denominator if denominator else 0.0,
                }
            )
    return _aggregated_frame(
        rows,
        FRACTION_SCHEMA,
        {"numerator", "denominator"},
    )
