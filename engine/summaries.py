"""Pure stop, convergence, outcome, and population summary helpers."""

from __future__ import annotations

import collections
from dataclasses import dataclass
from typing import Any, Iterable, Sequence, TypeAlias

import pandas as pd

from .category_analysis import (
    _aggregated_frame,
    exact_category_series,
    get_aggregated_category_metrics,
    get_aggregated_survivor_fractions,
    surviving_category_fraction_series,
)
from .genetic_code import (
    CODON_TABLE,
    PROPERTY_LABELS,
    STOP_CODONS,
    VALID_CODONS,
    get_primary_group_name,
)
from .models import (
    AggregatedSampledResult,
    ConvergenceBasis,
    ConvergenceResult,
    ExactSimulationResult,
    NoMoreChangeResult,
    SampledSimulationResult,
    StartScope,
)


Record: TypeAlias = dict[str, Any]
RecordsInput: TypeAlias = SampledSimulationResult | Iterable[Record]
TrackInput: TypeAlias = ExactSimulationResult | dict[str, Any]
StopInput: TypeAlias = ExactSimulationResult | dict[str, Any]


@dataclass(frozen=True)
class StartingPopulationMetrics:
    """Starting-population values shared by population and trait panels."""

    total_start_copies: float
    copies_per_codon: float


@dataclass(frozen=True)
class FinalPopulationMetrics:
    """Final live/stopped values shown by the population panel."""

    final_live: float
    final_stopped: float
    stop_fraction: float


def _records(source: RecordsInput) -> Iterable[Record]:
    if isinstance(source, SampledSimulationResult):
        return source.records
    return source


def _track_data(source: TrackInput) -> dict[str, Any]:
    if isinstance(source, ExactSimulationResult):
        return source.track_data
    return source


def _stop_data(source: StopInput) -> dict[str, Any]:
    if isinstance(source, ExactSimulationResult):
        return source.stop_data
    return source


def property_stop_counter(stop_data: StopInput) -> collections.Counter[str]:
    """Return stop totals grouped by starting biochemical property label."""
    data = _stop_data(stop_data)
    raw = data.get("by_start_prop")
    if raw:
        return collections.Counter(
            {PROPERTY_LABELS.get(key, key): value for key, value in raw.items()}
        )
    out = collections.Counter()
    for amino_acid, weight in data.get("by_start_aa", {}).items():
        out[get_primary_group_name(amino_acid)] += weight
    return out


def convergence_generation(
    series: dict[str, Sequence[float]],
    threshold: float = 1e-4,
) -> ConvergenceResult:
    """Return the first 1-based generation whose later changes stay bounded."""
    if not series:
        return ConvergenceResult(generation=None, max_delta=0.0)
    generation_count = max((len(values) for values in series.values()), default=0)
    if generation_count < 2:
        return ConvergenceResult(generation=None, max_delta=0.0)

    deltas = []
    for generation in range(1, generation_count):
        max_delta = 0.0
        for values in series.values():
            previous = values[generation - 1] if generation - 1 < len(values) else 0.0
            current = values[generation] if generation < len(values) else 0.0
            max_delta = max(max_delta, abs(current - previous))
        deltas.append(max_delta)

    for index, _delta in enumerate(deltas):
        if max(deltas[index:] or [0.0]) <= threshold:
            return ConvergenceResult(
                generation=index + 1,
                max_delta=max(deltas[index:] or [0.0]),
            )
    return ConvergenceResult(
        generation=None,
        max_delta=deltas[-1] if deltas else 0.0,
    )


def convergence_text(
    series: dict[str, Sequence[float]],
    threshold: float = 1e-4,
) -> str:
    """Format the historical convergence status text."""
    result = convergence_generation(series, threshold)
    if result.generation is None:
        return f"Still changing (last max change {result.max_delta:.5f})"
    return f"No more change by gen {result.generation} (max change < {threshold:g})"


def sampled_stop_series(records: RecordsInput, codon: str, n_gen: int) -> pd.DataFrame:
    new_stops = collections.Counter(
        record.get("stop_gen")
        for record in _records(records)
        if record.get("start") == codon
        and record.get("hit_stop")
        and record.get("stop_gen")
    )
    rows = []
    cumulative = 0
    for gen in range(1, n_gen + 1):
        new_count = int(new_stops[gen])
        cumulative += new_count
        rows.append(
            {
                "generation": gen,
                "new_stops": new_count,
                "cumulative_stops": cumulative,
            }
        )
    return pd.DataFrame(rows)


def exact_stop_series(track_data: TrackInput, codon: str, n_gen: int) -> pd.DataFrame:
    data = _track_data(track_data)
    rows = []
    cumulative = 0.0
    for gen in range(n_gen):
        new_count = data["per_gen_stop_codon_from"][gen].get(codon, 0.0)
        cumulative += new_count
        rows.append(
            {
                "generation": gen + 1,
                "new_stops": new_count,
                "cumulative_stops": cumulative,
            }
        )
    return pd.DataFrame(rows)


def no_more_change_from_df(
    df: pd.DataFrame,
    tolerance: float = 0.0,
    stable_status: str = "category counts stable",
) -> NoMoreChangeResult:
    pivot = (
        df.pivot(index="generation", columns="category", values="value")
        .fillna(0)
        .sort_index()
    )
    vectors = [tuple(row) for row in pivot.to_numpy()]
    for index, vector in enumerate(vectors):
        if all(
            all(abs(current - reference) <= tolerance for current, reference in zip(future, vector))
            for future in vectors[index:]
        ):
            start_generation = str(pivot.index[index])
            if sum(vector) == 0:
                return NoMoreChangeResult(
                    generation=start_generation,
                    status="constant state starts: all stopped",
                )
            return NoMoreChangeResult(
                generation=start_generation,
                status=f"constant state starts: {stable_status}",
            )
    return NoMoreChangeResult(generation="Not yet", status="still changing")


def exact_no_more_change(
    track_data: TrackInput,
    codon: str,
    n_gen: int,
    basis: str = "Current computation",
    alpha: float = 0.01,
) -> NoMoreChangeResult:
    exact_df = exact_category_series(track_data, codon, n_gen)
    if basis in {"Surviving trait fractions", "Exact surviving trait fractions"}:
        fraction_df = surviving_category_fraction_series(exact_df)
        return no_more_change_from_df(
            fraction_df,
            tolerance=alpha,
            stable_status=f"exact surviving fractions stable within alpha={alpha:g}",
        )
    return no_more_change_from_df(exact_df, tolerance=1.0)


def no_more_change_note(basis: str, alpha: float = 0.01) -> str:
    if basis in {"Surviving trait fractions", "Exact surviving trait fractions"}:
        return (
            "Start of the stable state in exact trait fraction / surviving copies "
            f"within alpha={alpha:g}."
        )
    return "Start of the constant state in exact category counts with ±1 tolerance."


def _codon_outcome_frame(
    values: collections.Counter[str],
    stopped: collections.Counter[str],
    codon_table: dict[str, str],
) -> pd.DataFrame:
    rows = [
        {
            "codon": target,
            "value": value,
            "amino_acid": codon_table[target],
            "category": get_primary_group_name(codon_table[target]),
        }
        for target, value in values.items()
    ]
    for stop_codon, value in stopped.items():
        rows.append(
            {
                "codon": f"{stop_codon} stop",
                "value": value,
                "amino_acid": "Stop",
                "category": "Stop",
            }
        )
    frame = pd.DataFrame(rows)
    if frame.empty:
        frame = pd.DataFrame(
            [{"codon": "No live outcomes", "value": 0, "category": "None"}]
        )
    return frame.sort_values("value", ascending=False)


def sampled_codon_outcome_table(
    records: RecordsInput,
    codon: str,
    generation: int,
) -> pd.DataFrame:
    """Build sampled codon outcomes without accepting UI display state."""
    counts = collections.Counter()
    stopped = collections.Counter()
    for record in _records(records):
        if record.get("start") != codon:
            continue
        path = record.get("path", [])
        if len(path) <= generation:
            if record.get("hit_stop") and record.get("stop_gen", 10**9) <= generation:
                stopped[record.get("final")] += 1
            continue
        current = path[generation]
        if current in STOP_CODONS:
            stopped[current] += 1
        else:
            counts[current] += 1
    return _codon_outcome_frame(counts, stopped, CODON_TABLE)


def exact_codon_outcome_table(
    track_data: TrackInput,
    codon: str,
    generation: int,
) -> pd.DataFrame:
    """Build exact codon outcomes without accepting UI display state."""
    data = _track_data(track_data)
    values = collections.Counter(
        data["per_gen_codon_from"][generation - 1].get(codon, {})
    )
    stopped = collections.Counter(
        data["per_gen_stop_codon_to"][generation - 1].get(codon, {})
    )
    return _codon_outcome_frame(values, stopped, CODON_TABLE)


def all_codon_no_more_change(
    track_data: TrackInput,
    n_gen: int,
    no_more_basis: str = "Current computation",
    no_more_alpha: float = 0.01,
) -> pd.DataFrame:
    """Return exact stable-state status for every valid starting codon."""
    rows = []
    for codon in VALID_CODONS:
        result = exact_no_more_change(
            track_data,
            codon,
            n_gen,
            no_more_basis,
            no_more_alpha,
        )
        rows.append(
            {
                "codon": codon,
                "aa": CODON_TABLE[codon],
                "start_category": get_primary_group_name(CODON_TABLE[codon]),
                "no_more_change": result.generation,
                "status": result.status,
            }
        )
    return pd.DataFrame(rows)


def starting_population_metrics(
    result: ExactSimulationResult,
    record_count: int,
) -> StartingPopulationMetrics:
    """Calculate the existing starting-total and per-codon display bases."""
    total_start_copies = float(result.stats.get("total_start_copies", record_count))
    copies_per_codon = total_start_copies / max(
        1,
        int(result.stats.get("n_starts", len(VALID_CODONS))),
    )
    return StartingPopulationMetrics(total_start_copies, copies_per_codon)


def final_population_metrics(
    category_frame: pd.DataFrame,
    n_gen: int,
    total_start_copies: float,
) -> FinalPopulationMetrics:
    """Calculate the existing final survival and stop display values."""
    final_live = float(
        category_frame[category_frame["generation"] == n_gen]["value"].sum()
    )
    final_stopped = max(0.0, total_start_copies - final_live)
    stop_fraction = final_stopped / total_start_copies if total_start_copies else 0.0
    return FinalPopulationMetrics(final_live, final_stopped, stop_fraction)


def get_aggregated_survival_by_start(
    result: AggregatedSampledResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame:
    """Return sampled live and cumulative-stop counts for one start scope."""
    from .exact_analysis import SURVIVAL_SCHEMA, _scope_start_codons

    start_codons = _scope_start_codons(start_scope, start_key)
    initial_value = sum(result.start_counts[codon] for codon in start_codons)
    cumulative_stopped = 0
    rows: list[dict[str, Any]] = []
    for snapshot in result.generations:
        live_value = sum(
            sum(snapshot.current_codon_by_start_codon[codon].values())
            for codon in start_codons
        )
        new_stopped = sum(
            sum(snapshot.new_stop_codon_by_start_codon[codon].values())
            for codon in start_codons
        )
        cumulative_stopped += new_stopped
        rows.append(
            {
                "generation": snapshot.generation,
                "start_scope": start_scope,
                "start_key": start_key,
                "initial_value": initial_value,
                "live_value": live_value,
                "stopped_value": cumulative_stopped,
                "survivor_fraction": (
                    live_value / initial_value if initial_value else 0.0
                ),
                "stop_fraction": (
                    cumulative_stopped / initial_value if initial_value else 0.0
                ),
                "value_kind": "copy_count",
            }
        )
    return _aggregated_frame(
        rows,
        SURVIVAL_SCHEMA,
        {"initial_value", "live_value", "stopped_value"},
    )


def get_aggregated_stop_outcomes(
    result: AggregatedSampledResult,
    *,
    start_scope: StartScope,
    start_key: str,
) -> pd.DataFrame:
    """Return sampled new and cumulative stops in canonical codon order."""
    from .exact_analysis import (
        CANONICAL_STOP_CODONS,
        STOP_SCHEMA,
        _scope_start_codons,
    )

    start_codons = _scope_start_codons(start_scope, start_key)
    initial_value = sum(result.start_counts[codon] for codon in start_codons)
    cumulative = {stop_codon: 0 for stop_codon in CANONICAL_STOP_CODONS}
    rows: list[dict[str, Any]] = []
    for snapshot in result.generations:
        for stop_codon in CANONICAL_STOP_CODONS:
            new_value = sum(
                snapshot.new_stop_codon_by_start_codon[codon][stop_codon]
                for codon in start_codons
            )
            cumulative[stop_codon] += new_value
            rows.append(
                {
                    "generation": snapshot.generation,
                    "start_scope": start_scope,
                    "start_key": start_key,
                    "stop_codon": stop_codon,
                    "new_stop_value": new_value,
                    "cumulative_stop_value": cumulative[stop_codon],
                    "initial_value": initial_value,
                    "cumulative_stop_fraction": (
                        cumulative[stop_codon] / initial_value
                        if initial_value
                        else 0.0
                    ),
                    "value_kind": "copy_count",
                }
            )
    return _aggregated_frame(
        rows,
        STOP_SCHEMA,
        {"new_stop_value", "cumulative_stop_value", "initial_value"},
    )


def get_aggregated_codon_outcomes(
    result: AggregatedSampledResult,
    *,
    start_codon: str,
    generation: int,
) -> pd.DataFrame:
    """Return complete sampled sense and stop outcomes for one starting codon."""
    from .exact_analysis import (
        CANONICAL_STOP_CODONS,
        CODON_OUTCOME_SCHEMA,
        _scope_start_codons,
    )
    from .models import InvalidScientificScopeError

    _scope_start_codons("codon", start_codon)
    if (
        type(generation) is not int
        or generation < 1
        or generation > result.n_generations
    ):
        raise InvalidScientificScopeError(
            f"Invalid scientific scope generation={generation}."
        )

    snapshot = result.generations[generation - 1]
    live = snapshot.current_codon_by_start_codon[start_codon]
    new_stops = snapshot.new_stop_codon_by_start_codon[start_codon]
    cumulative: collections.Counter[str] = collections.Counter()
    for prior_snapshot in result.generations[:generation]:
        cumulative.update(
            prior_snapshot.new_stop_codon_by_start_codon[start_codon]
        )

    rows: list[dict[str, Any]] = []
    for target_codon in VALID_CODONS:
        target_aa = CODON_TABLE[target_codon]
        rows.append(
            {
                "generation": generation,
                "start_codon": start_codon,
                "target_codon": target_codon,
                "target_aa": target_aa,
                "target_category": get_primary_group_name(target_aa),
                "live_value": int(live[target_codon]),
                "new_stop_value": 0,
                "cumulative_stop_value": 0,
                "value_kind": "copy_count",
            }
        )
    for stop_codon in CANONICAL_STOP_CODONS:
        rows.append(
            {
                "generation": generation,
                "start_codon": start_codon,
                "target_codon": stop_codon,
                "target_aa": "Stop",
                "target_category": "Stop",
                "live_value": 0,
                "new_stop_value": int(new_stops[stop_codon]),
                "cumulative_stop_value": int(cumulative[stop_codon]),
                "value_kind": "copy_count",
            }
        )
    return _aggregated_frame(
        rows,
        CODON_OUTCOME_SCHEMA,
        {"live_value", "new_stop_value", "cumulative_stop_value"},
    )


def get_aggregated_convergence(
    result: AggregatedSampledResult,
    *,
    start_scope: StartScope,
    start_key: str,
    basis: ConvergenceBasis,
    tolerance: float,
) -> pd.DataFrame:
    """Return first sampled generation stable against every later category vector."""
    from .exact_analysis import CONVERGENCE_SCHEMA, _scope_start_codons
    from .models import InvalidScientificScopeError

    _scope_start_codons(start_scope, start_key)
    if basis not in {"category_weight", "survivor_fraction"}:
        raise InvalidScientificScopeError(
            f"Invalid scientific scope convergence_basis={basis}."
        )
    tolerance_value = float(tolerance)
    source = (
        get_aggregated_category_metrics(
            result,
            start_scope=start_scope,
            start_key=start_key,
        ).rename(columns={"live_value": "basis_value"})
        if basis == "category_weight"
        else get_aggregated_survivor_fractions(
            result,
            start_scope=start_scope,
            start_key=start_key,
        ).rename(columns={"fraction": "basis_value"})
    )

    vectors: list[tuple[float, ...]] = []
    for generation in range(1, result.n_generations + 1):
        generation_rows = source[source["generation"] == generation]
        vectors.append(
            tuple(float(value) for value in generation_rows["basis_value"])
        )

    selected_generation: int | Any = pd.NA
    selected_delta = 0.0
    status = "no_generations"
    maximum_observed_delta = 0.0
    for index, vector in enumerate(vectors):
        candidate_delta = 0.0
        for future in vectors[index:]:
            for current, reference in zip(future, vector):
                candidate_delta = max(
                    candidate_delta,
                    abs(current - reference),
                )
        maximum_observed_delta = max(maximum_observed_delta, candidate_delta)
        if candidate_delta <= tolerance_value:
            selected_generation = index + 1
            selected_delta = candidate_delta
            all_stopped = all(
                all(value == 0.0 for value in future)
                for future in vectors[index:]
            )
            status = "all_stopped" if all_stopped else "stable"
            break
    else:
        if vectors:
            selected_delta = maximum_observed_delta
            status = "still_changing"

    return _aggregated_frame(
        [
            {
                "start_scope": start_scope,
                "start_key": start_key,
                "basis": basis,
                "tolerance": tolerance_value,
                "generation": selected_generation,
                "max_delta": selected_delta,
                "status": status,
            }
        ],
        CONVERGENCE_SCHEMA,
        set(),
    )
