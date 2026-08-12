"""JSON serializers for the Phase 4 API boundary."""

from __future__ import annotations

from typing import Any

import pandas as pd


def _json_scalar(value: Any) -> Any:
    if pd.isna(value):
        return None
    if hasattr(value, "item"):
        return value.item()
    return value


def serialize_table(frame: pd.DataFrame, *, value_kind: str) -> dict[str, Any]:
    """Serialize a DataFrame using the approved Phase 4 table envelope."""

    records: list[dict[str, Any]] = []
    for row in frame.to_dict(orient="records"):
        records.append({column: _json_scalar(row[column]) for column in frame.columns})

    return {
        "columns": list(frame.columns),
        "dtypes": {column: str(frame[column].dtype) for column in frame.columns},
        "records": records,
        "index_kind": type(frame.index).__name__,
        "row_count": int(len(frame)),
        "value_kind": value_kind,
    }


def serialize_counter(counter: Any) -> dict[str, int]:
    """Serialize an ordered Counter-like mapping as JSON-safe integers."""

    return {key: int(value) for key, value in counter.items()}


def serialize_nested_counter(counter: Any) -> dict[str, dict[str, int]]:
    """Serialize an ordered nested Counter-like mapping."""

    return {key: serialize_counter(value) for key, value in counter.items()}


def serialize_generation_counts(generation_counts: Any) -> dict[str, Any]:
    """Serialize approved bounded aggregated generation counters."""

    return {
        "generation": int(generation_counts.generation),
        "live_codon": serialize_counter(generation_counts.live_codon),
        "live_amino_acid": serialize_counter(generation_counts.live_amino_acid),
        "live_category": serialize_counter(generation_counts.live_category),
        "live_by_start_codon": serialize_counter(generation_counts.live_by_start_codon),
        "live_by_start_trait": serialize_counter(generation_counts.live_by_start_trait),
        "current_codon_by_start_codon": serialize_nested_counter(
            generation_counts.current_codon_by_start_codon
        ),
        "new_stop_codon_by_start_codon": serialize_nested_counter(
            generation_counts.new_stop_codon_by_start_codon
        ),
        "new_stops_by_stop_codon": serialize_counter(generation_counts.new_stops_by_stop_codon),
        "new_stops_by_start_codon": serialize_counter(generation_counts.new_stops_by_start_codon),
        "new_stops_by_start_trait": serialize_counter(generation_counts.new_stops_by_start_trait),
        "total_live": int(generation_counts.total_live),
        "new_stops": int(generation_counts.new_stops),
        "cumulative_stops": int(generation_counts.cumulative_stops),
    }
