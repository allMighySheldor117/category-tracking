"""UI-independent scientific engine public surface."""

from .aggregated_tracking import run_aggregated_experiment
from .category_analysis import (
    get_aggregated_category_metrics,
    get_aggregated_survivor_fractions,
)
from .comparisons import (
    compare_convergence,
    compare_exact_to_sampled,
    compare_numeric_metric,
)
from .exact_analysis import (
    build_exact_analysis,
    get_exact_category_metrics,
    get_exact_codon_outcomes,
    get_exact_convergence,
    get_exact_stop_outcomes,
    get_exact_survival_by_start,
    get_exact_survivor_fractions,
    run_exact_analysis,
)
from .invariants import (
    validate_biological_invariants,
    validate_exact_analysis,
    validate_mutation_matrix,
)
from .models import (
    AggregatedGenerationCounts,
    AggregatedSampledResult,
    ComparisonResult,
    ConvergenceComparisonResult,
    ConvergenceResult,
    ExactAnalysisResult,
    ExactResultProvenanceError,
    ExactSampledComparisonResult,
    ExactSimulationResult,
    InvalidScientificScopeError,
    MetricSchemaError,
    NoMoreChangeResult,
    SampledSimulationResult,
    ScientificInvariantError,
    ScientificInvariantReport,
    UnsupportedComparisonError,
)
from .summaries import (
    get_aggregated_codon_outcomes,
    get_aggregated_convergence,
    get_aggregated_stop_outcomes,
    get_aggregated_survival_by_start,
)

__all__ = [
    "AggregatedGenerationCounts",
    "AggregatedSampledResult",
    "ComparisonResult",
    "ConvergenceComparisonResult",
    "ConvergenceResult",
    "ExactAnalysisResult",
    "ExactResultProvenanceError",
    "ExactSampledComparisonResult",
    "ExactSimulationResult",
    "InvalidScientificScopeError",
    "MetricSchemaError",
    "NoMoreChangeResult",
    "SampledSimulationResult",
    "ScientificInvariantError",
    "ScientificInvariantReport",
    "UnsupportedComparisonError",
    "build_exact_analysis",
    "compare_convergence",
    "compare_exact_to_sampled",
    "compare_numeric_metric",
    "get_aggregated_category_metrics",
    "get_aggregated_codon_outcomes",
    "get_aggregated_convergence",
    "get_aggregated_stop_outcomes",
    "get_aggregated_survival_by_start",
    "get_aggregated_survivor_fractions",
    "get_exact_category_metrics",
    "get_exact_codon_outcomes",
    "get_exact_convergence",
    "get_exact_stop_outcomes",
    "get_exact_survival_by_start",
    "get_exact_survivor_fractions",
    "run_aggregated_experiment",
    "run_exact_analysis",
    "validate_biological_invariants",
    "validate_exact_analysis",
    "validate_mutation_matrix",
]
