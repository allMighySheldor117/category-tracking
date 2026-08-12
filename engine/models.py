"""Named result contracts and explicit legacy compatibility boundaries."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from typing import Any, Literal, Mapping, TypeAlias

import pandas as pd


CodonCounter: TypeAlias = Counter[str]
AminoAcidCounter: TypeAlias = Counter[str]
GenerationCounters: TypeAlias = list[Counter[str]]
StartToFinalCounters: TypeAlias = dict[str, Counter[str]]
OrderedData: TypeAlias = dict[str, Any]
SampleRecord: TypeAlias = dict[str, Any]
StartWeights: TypeAlias = Mapping[str, float]
StartScope: TypeAlias = Literal["population", "codon", "amino_acid", "trait"]
ConvergenceBasis: TypeAlias = Literal["category_weight", "survivor_fraction"]
MetricName: TypeAlias = Literal[
    "category_live_value",
    "category_fraction",
    "survivor_fraction",
    "stop_fraction",
    "new_stop_value",
    "cumulative_stop_value",
    "cumulative_stop_fraction",
    "codon_live_value",
    "codon_new_stop_value",
    "codon_cumulative_stop_value",
]

ExactLegacyTuple: TypeAlias = tuple[
    CodonCounter,
    AminoAcidCounter,
    CodonCounter,
    AminoAcidCounter,
    CodonCounter,
    AminoAcidCounter,
    GenerationCounters,
    StartToFinalCounters,
    OrderedData,
    OrderedData,
    OrderedData,
]
SampledLegacyTuple: TypeAlias = tuple[
    list[SampleRecord],
    CodonCounter,
    AminoAcidCounter,
    StartToFinalCounters,
]


class ExactResultProvenanceError(ValueError):
    """Reject an exact result paired with unrelated starting weights."""


class InvalidScientificScopeError(ValueError):
    """Reject an unknown or incompatible scientific scope and key."""


class UnsupportedComparisonError(ValueError):
    """Reject a metric or mode pairing without an approved comparison."""


class MetricSchemaError(ValueError):
    """Reject metric data that violates its canonical table schema."""


class ScientificInvariantError(ValueError):
    """Report a failed scientific conservation or ordering invariant."""


@dataclass(frozen=True)
class ConvergenceResult:
    """Named convergence generation and maximum remaining change."""

    generation: int | None
    max_delta: float

    def to_legacy_tuple(self) -> tuple[int | None, float]:
        """Return the historical two-position compatibility result."""
        return self.generation, self.max_delta


@dataclass(frozen=True)
class NoMoreChangeResult:
    """Named generation label and stability status."""

    generation: str
    status: str

    def to_legacy_tuple(self) -> tuple[str, str]:
        """Return the historical two-position compatibility result."""
        return self.generation, self.status


@dataclass
class ExactSimulationResult:
    """Named form of the frozen 11-position exact-simulation result."""

    enc_codon: CodonCounter
    enc_aa: AminoAcidCounter
    enc_codon_cnt: CodonCounter
    enc_aa_cnt: AminoAcidCounter
    fin_codon: CodonCounter
    fin_aa: AminoAcidCounter
    per_gen_aa: GenerationCounters
    start_to_fin: StartToFinalCounters
    stats: OrderedData
    stop_data: OrderedData
    track_data: OrderedData

    def to_legacy_tuple(self) -> ExactLegacyTuple:
        """Return the exact historical field order without copying containers."""
        return (
            self.enc_codon,
            self.enc_aa,
            self.enc_codon_cnt,
            self.enc_aa_cnt,
            self.fin_codon,
            self.fin_aa,
            self.per_gen_aa,
            self.start_to_fin,
            self.stats,
            self.stop_data,
            self.track_data,
        )

    @classmethod
    def from_legacy_tuple(cls, result: ExactLegacyTuple) -> ExactSimulationResult:
        """Name an exact legacy result at an explicit compatibility boundary."""
        (
            enc_codon,
            enc_aa,
            enc_codon_cnt,
            enc_aa_cnt,
            fin_codon,
            fin_aa,
            per_gen_aa,
            start_to_fin,
            stats,
            stop_data,
            track_data,
        ) = result
        return cls(
            enc_codon=enc_codon,
            enc_aa=enc_aa,
            enc_codon_cnt=enc_codon_cnt,
            enc_aa_cnt=enc_aa_cnt,
            fin_codon=fin_codon,
            fin_aa=fin_aa,
            per_gen_aa=per_gen_aa,
            start_to_fin=start_to_fin,
            stats=stats,
            stop_data=stop_data,
            track_data=track_data,
        )


@dataclass
class SampledSimulationResult:
    """Named form of the frozen four-position sampled-simulation result."""

    records: list[SampleRecord]
    sample_fin_codon: CodonCounter
    sample_fin_aa: AminoAcidCounter
    sample_start_to_fin: StartToFinalCounters

    def to_legacy_tuple(self) -> SampledLegacyTuple:
        """Return the exact historical field order without copying containers."""
        return (
            self.records,
            self.sample_fin_codon,
            self.sample_fin_aa,
            self.sample_start_to_fin,
        )

    @classmethod
    def from_legacy_tuple(cls, result: SampledLegacyTuple) -> SampledSimulationResult:
        """Name a sampled legacy result at an explicit compatibility boundary."""
        records, sample_fin_codon, sample_fin_aa, sample_start_to_fin = result
        return cls(
            records=records,
            sample_fin_codon=sample_fin_codon,
            sample_fin_aa=sample_fin_aa,
            sample_start_to_fin=sample_start_to_fin,
        )


@dataclass(frozen=True)
class ExactAnalysisResult:
    """Authoritative exact simulation and eager population-wide tables."""

    simulation: ExactSimulationResult
    start_weights: dict[str, float]
    population_category_metrics: pd.DataFrame
    population_survivor_fractions: pd.DataFrame
    population_survival: pd.DataFrame
    population_stop_outcomes: pd.DataFrame


@dataclass(frozen=True)
class AggregatedGenerationCounts:
    """Memory-bounded integer counters retained for one sampled generation."""

    generation: int
    live_codon: Counter[str]
    live_amino_acid: Counter[str]
    live_category: Counter[str]
    live_by_start_codon: Counter[str]
    live_by_start_trait: Counter[str]
    current_codon_by_start_codon: dict[str, Counter[str]]
    new_stop_codon_by_start_codon: dict[str, Counter[str]]
    new_stops_by_stop_codon: Counter[str]
    new_stops_by_start_codon: Counter[str]
    new_stops_by_start_trait: Counter[str]
    total_live: int
    new_stops: int
    cumulative_stops: int


@dataclass(frozen=True)
class AggregatedSampledResult:
    """Explicitly seeded sampled result without per-copy histories."""

    seed: int
    n_generations: int
    start_counts: dict[str, int]
    total_start_count: int
    generations: tuple[AggregatedGenerationCounts, ...]
    final_live_codon: Counter[str]
    final_live_amino_acid: Counter[str]
    final_live_by_start_codon: dict[str, Counter[str]]
    total_stopped: int


@dataclass(frozen=True)
class ComparisonResult:
    """Directed numeric comparison with explicit alignment keys."""

    metric: str
    baseline_label: str
    candidate_label: str
    key_columns: tuple[str, ...]
    table: pd.DataFrame


@dataclass(frozen=True)
class ConvergenceComparisonResult:
    """Comparison of nullable convergence generations and statuses."""

    baseline_label: str
    candidate_label: str
    table: pd.DataFrame


@dataclass(frozen=True)
class ExactSampledComparisonResult:
    """Statistical comparison of sampled estimates with exact fractions."""

    metric: str
    denominator_scope: str
    familywise_alpha: float
    family_size: int
    table: pd.DataFrame


@dataclass(frozen=True)
class ScientificInvariantReport:
    """Observed and expected values for one checked scientific invariant."""

    metric: str
    scope: str
    generation: int | None
    expected: Any
    observed: Any
    tolerance: float
