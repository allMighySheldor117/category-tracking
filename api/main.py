"""FastAPI application for the Phase 4 service adapter."""

from __future__ import annotations

from typing import Any

from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError

from engine.aggregated_tracking import run_aggregated_experiment
from engine.category_analysis import get_aggregated_category_metrics, get_aggregated_survivor_fractions
from engine.comparisons import compare_exact_to_sampled, compare_numeric_metric
from engine.exact_analysis import (
    CANONICAL_STOP_CODONS,
    get_exact_category_metrics,
    get_exact_codon_outcomes,
    get_exact_convergence,
    get_exact_stop_outcomes,
    get_exact_survival_by_start,
    get_exact_survivor_fractions,
    run_exact_analysis,
)
from engine.genetic_code import PROPERTY_LABELS, VALID_CODONS
from engine.models import (
    ExactResultProvenanceError,
    InvalidScientificScopeError,
    MetricSchemaError,
    ScientificInvariantError,
    UnsupportedComparisonError,
)
from engine.mutation_matrix import PRESET_AC, PRESET_AG, PRESET_AT, build_substitution_matrix
from engine.summaries import (
    get_aggregated_codon_outcomes,
    get_aggregated_convergence,
    get_aggregated_stop_outcomes,
    get_aggregated_survival_by_start,
)

from .models import API_VERSION, error_envelope, success_envelope
from .serializers import serialize_counter, serialize_generation_counts, serialize_nested_counter, serialize_table


MAX_EXACT_GENERATIONS = 2000
MAX_AGGREGATED_GENERATIONS = 500
MAX_AGGREGATED_START_COUNT = 100_000


class ApiRequestValidationError(ValueError):
    """Raised when an API JSON request has an invalid shape."""


def _require_mapping(request: dict[str, Any], field: str) -> dict[str, Any]:
    value = request.get(field)
    if not isinstance(value, dict):
        raise ApiRequestValidationError(f"{field} must be an object")
    return value


def _n_generations(request: dict[str, Any]) -> int:
    try:
        return int(request["n_generations"])
    except (KeyError, TypeError, ValueError) as exc:
        raise ApiRequestValidationError("n_generations must be an integer") from exc


def _probabilities(request: dict[str, Any]) -> tuple[float, float, float]:
    probabilities = _require_mapping(request, "probabilities")
    values = []
    for key in ("a_to_t", "a_to_g", "a_to_c"):
        try:
            values.append(float(probabilities[key]))
        except (KeyError, TypeError, ValueError) as exc:
            raise ApiRequestValidationError(f"probabilities.{key} is required") from exc
    return (values[0], values[1], values[2])


def _starting_weights(request: dict[str, Any]) -> dict[str, float] | None:
    start_weights = request.get("start_weights")
    if start_weights is None:
        return None
    if not isinstance(start_weights, dict):
        raise ApiRequestValidationError("start_weights must be an object")
    return {str(codon): float(weight) for codon, weight in start_weights.items()}


def _integer_starting_weights(request: dict[str, Any]) -> dict[str, int]:
    start_weights = request.get("start_weights") or {}
    if not isinstance(start_weights, dict):
        raise ApiRequestValidationError("start_weights must be an object")
    return {str(codon): int(weight) for codon, weight in start_weights.items()}


def _oversized_error(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=413,
        content=error_envelope(code="oversized_request", message=message, status_code=413),
    )


def _validation_error(message: str) -> JSONResponse:
    return JSONResponse(
        status_code=422,
        content=error_envelope(code="validation_error", message=message, status_code=422),
    )


def _exact_oversized_response(simulation: dict[str, Any]) -> JSONResponse | None:
    if _n_generations(simulation) > MAX_EXACT_GENERATIONS:
        return _oversized_error("exact n_generations must be at most 2000")
    return None


def _aggregated_oversized_response(simulation: dict[str, Any]) -> JSONResponse | None:
    if _n_generations(simulation) > MAX_AGGREGATED_GENERATIONS:
        return _oversized_error("aggregated n_generations must be at most 500")

    start_weights = _starting_weights(simulation) or {}
    normalized_total = sum(max(0, int(weight)) for weight in start_weights.values())
    if normalized_total > MAX_AGGREGATED_START_COUNT:
        return _oversized_error("aggregated normalized start count must be at most 100000")
    return None


def _exact_scope_payload(analysis: Any, scope: dict[str, Any]) -> dict[str, Any]:
    start_scope = str(scope["start_scope"])
    start_key = str(scope["start_key"])
    return {
        "start_scope": start_scope,
        "start_key": start_key,
        "category_metrics": serialize_table(
            get_exact_category_metrics(analysis, start_scope=start_scope, start_key=start_key),
            value_kind="probability_weight",
        ),
        "survivor_fractions": serialize_table(
            get_exact_survivor_fractions(analysis, start_scope=start_scope, start_key=start_key),
            value_kind="fraction",
        ),
        "survival_by_start": serialize_table(
            get_exact_survival_by_start(analysis, start_scope=start_scope, start_key=start_key),
            value_kind="fraction",
        ),
        "stop_outcomes": serialize_table(
            get_exact_stop_outcomes(analysis, start_scope=start_scope, start_key=start_key),
            value_kind="probability_weight",
        ),
    }


def _aggregated_scope_payload(result: Any, scope: dict[str, Any]) -> dict[str, Any]:
    start_scope = str(scope["start_scope"])
    start_key = str(scope["start_key"])
    return {
        "start_scope": start_scope,
        "start_key": start_key,
        "category_metrics": serialize_table(
            get_aggregated_category_metrics(result, start_scope=start_scope, start_key=start_key),
            value_kind="copy_count",
        ),
        "survivor_fractions": serialize_table(
            get_aggregated_survivor_fractions(result, start_scope=start_scope, start_key=start_key),
            value_kind="fraction",
        ),
        "survival_by_start": serialize_table(
            get_aggregated_survival_by_start(result, start_scope=start_scope, start_key=start_key),
            value_kind="fraction",
        ),
        "stop_outcomes": serialize_table(
            get_aggregated_stop_outcomes(result, start_scope=start_scope, start_key=start_key),
            value_kind="copy_count",
        ),
    }


def _exact_analysis_from_request(simulation: dict[str, Any]) -> Any:
    matrix = build_substitution_matrix(*_probabilities(simulation))
    return run_exact_analysis(
        _n_generations(simulation),
        matrix,
        _starting_weights(simulation),
    )


def _aggregated_result_from_request(simulation: dict[str, Any]) -> Any:
    if "seed" not in simulation or not isinstance(simulation["seed"], int):
        raise ApiRequestValidationError("aggregated sampled requests require an integer seed")

    matrix = build_substitution_matrix(*_probabilities(simulation))
    return run_aggregated_experiment(
        _n_generations(simulation),
        matrix,
        _integer_starting_weights(simulation),
        seed=int(simulation["seed"]),
    )


def _exact_metric_table(analysis: Any, *, metric: str, scope: dict[str, Any]) -> Any:
    start_scope = str(scope["start_scope"])
    start_key = str(scope["start_key"])
    if metric == "category_live_value":
        return get_exact_category_metrics(analysis, start_scope=start_scope, start_key=start_key)
    if metric == "category_fraction":
        return get_exact_survivor_fractions(analysis, start_scope=start_scope, start_key=start_key)
    if metric in {"survivor_fraction", "stop_fraction"}:
        return get_exact_survival_by_start(analysis, start_scope=start_scope, start_key=start_key)
    if metric in {"new_stop_value", "cumulative_stop_value", "cumulative_stop_fraction"}:
        return get_exact_stop_outcomes(analysis, start_scope=start_scope, start_key=start_key)
    raise UnsupportedComparisonError(f"Unsupported comparison metric: {metric}.")


def _aggregated_metric_table(result: Any, *, metric: str, scope: dict[str, Any]) -> Any:
    start_scope = str(scope["start_scope"])
    start_key = str(scope["start_key"])
    if metric == "category_live_value":
        return get_aggregated_category_metrics(result, start_scope=start_scope, start_key=start_key)
    if metric == "category_fraction":
        return get_aggregated_survivor_fractions(result, start_scope=start_scope, start_key=start_key)
    if metric in {"survivor_fraction", "stop_fraction"}:
        return get_aggregated_survival_by_start(result, start_scope=start_scope, start_key=start_key)
    if metric in {"new_stop_value", "cumulative_stop_value", "cumulative_stop_fraction"}:
        return get_aggregated_stop_outcomes(result, start_scope=start_scope, start_key=start_key)
    raise UnsupportedComparisonError(f"Unsupported comparison metric: {metric}.")


def create_app() -> FastAPI:
    """Create the Codon Category Tracking API application."""

    service = FastAPI(
        title="Codon Category Tracking API",
        version=API_VERSION,
        description="HTTP adapter over the UI-independent codon category tracking engine.",
        openapi_tags=[
            {"name": "health", "description": "Service liveness."},
            {"name": "metadata", "description": "Engine metadata and supported options."},
            {"name": "simulations", "description": "Exact and aggregated sampled simulations."},
            {"name": "comparisons", "description": "Exact and sampled comparison outputs."},
        ],
    )

    @service.exception_handler(RequestValidationError)
    async def validation_exception_handler(
        request: Request, exc: RequestValidationError
    ) -> JSONResponse:
        errors = exc.errors()
        is_json_error = any(error.get("type") == "json_invalid" for error in errors)
        status_code = 400 if is_json_error else 422
        code = "malformed_json" if is_json_error else "validation_error"
        return JSONResponse(
            status_code=status_code,
            content=error_envelope(code=code, message=code.replace("_", " "), status_code=status_code),
        )

    @service.exception_handler(ApiRequestValidationError)
    async def api_validation_exception_handler(
        request: Request, exc: ApiRequestValidationError
    ) -> JSONResponse:
        return _validation_error(str(exc))

    @service.exception_handler(InvalidScientificScopeError)
    async def invalid_scope_exception_handler(
        request: Request, exc: InvalidScientificScopeError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_envelope(
                code="invalid_scientific_scope",
                message=str(exc),
                status_code=422,
            ),
        )

    @service.exception_handler(UnsupportedComparisonError)
    async def unsupported_comparison_exception_handler(
        request: Request, exc: UnsupportedComparisonError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_envelope(
                code="unsupported_comparison",
                message=str(exc),
                status_code=422,
            ),
        )

    @service.exception_handler(MetricSchemaError)
    async def metric_schema_exception_handler(
        request: Request, exc: MetricSchemaError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_envelope(code="metric_schema_mismatch", message=str(exc), status_code=422),
        )

    @service.exception_handler(ExactResultProvenanceError)
    async def exact_provenance_exception_handler(
        request: Request, exc: ExactResultProvenanceError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=422,
            content=error_envelope(code="exact_provenance_error", message=str(exc), status_code=422),
        )

    @service.exception_handler(ScientificInvariantError)
    async def invariant_exception_handler(
        request: Request, exc: ScientificInvariantError
    ) -> JSONResponse:
        return JSONResponse(
            status_code=500,
            content=error_envelope(
                code="scientific_invariant_error",
                message=str(exc),
                status_code=500,
            ),
        )

    @service.get("/health", tags=["health"])
    def health() -> dict[str, str]:
        return {
            "api_version": API_VERSION,
            "mode": "health",
            "scientific_authority": "none",
            "status": "ok",
        }

    @service.get("/api/v1/metadata", tags=["metadata"])
    def metadata() -> dict[str, object]:
        return success_envelope(
            mode="metadata",
            scientific_authority="engine",
            data={
                "valid_codons": VALID_CODONS,
                "stop_codons": list(CANONICAL_STOP_CODONS),
                "category_labels": list(PROPERTY_LABELS.values()),
                "probability_presets": {
                    "at": PRESET_AT,
                    "ag": PRESET_AG,
                    "ac": PRESET_AC,
                },
                "supported_modes": ["exact", "aggregated_sampled"],
                "detailed_sampled_http": False,
            },
        )

    @service.post("/api/v1/simulations/exact", tags=["simulations"], response_model=None)
    def exact_simulation(request: dict[str, Any]) -> dict[str, Any] | JSONResponse:
        oversized = _exact_oversized_response(request)
        if oversized is not None:
            return oversized
        n_generations = _n_generations(request)

        matrix = build_substitution_matrix(*_probabilities(request))
        start_weights = _starting_weights(request)
        analysis = run_exact_analysis(n_generations, matrix, start_weights)

        scopes = request.get("scopes") or [{"start_scope": "population", "start_key": "all"}]
        codon_outcomes = []
        for item in request.get("codon_outcomes", []):
            start_codon = str(item["start_codon"])
            generation = int(item["generation"])
            codon_outcomes.append(
                {
                    "start_codon": start_codon,
                    "generation": generation,
                    "table": serialize_table(
                        get_exact_codon_outcomes(
                            analysis,
                            start_codon=start_codon,
                            generation=generation,
                        ),
                        value_kind="probability_weight",
                    ),
                }
            )

        convergence = []
        for item in request.get("convergence", []):
            start_scope = str(item["start_scope"])
            start_key = str(item["start_key"])
            basis = str(item["basis"])
            tolerance = float(item["tolerance"])
            convergence.append(
                {
                    "start_scope": start_scope,
                    "start_key": start_key,
                    "basis": basis,
                    "tolerance": tolerance,
                    "table": serialize_table(
                        get_exact_convergence(
                            analysis,
                            start_scope=start_scope,
                            start_key=start_key,
                            basis=basis,
                            tolerance=tolerance,
                        ),
                        value_kind="status",
                    ),
                }
            )

        return success_envelope(
            mode="exact",
            scientific_authority="exact_probability",
            data={
                "n_generations": n_generations,
                "start_weights": dict(analysis.start_weights),
                "scopes": [_exact_scope_payload(analysis, scope) for scope in scopes],
                "codon_outcomes": codon_outcomes,
                "convergence": convergence,
            },
        )

    @service.post("/api/v1/simulations/aggregated", tags=["simulations"], response_model=None)
    def aggregated_simulation(request: dict[str, Any]) -> dict[str, Any] | JSONResponse:
        if "seed" not in request or not isinstance(request["seed"], int):
            return _validation_error("aggregated sampled requests require an integer seed")

        oversized = _aggregated_oversized_response(request)
        if oversized is not None:
            return oversized
        n_generations = _n_generations(request)
        start_weights = _starting_weights(request) or {}

        matrix = build_substitution_matrix(*_probabilities(request))
        result = run_aggregated_experiment(
            n_generations,
            matrix,
            start_weights,
            seed=int(request["seed"]),
        )

        scopes = request.get("scopes") or [{"start_scope": "population", "start_key": "all"}]
        codon_outcomes = []
        for item in request.get("codon_outcomes", []):
            start_codon = str(item["start_codon"])
            generation = int(item["generation"])
            codon_outcomes.append(
                {
                    "start_codon": start_codon,
                    "generation": generation,
                    "table": serialize_table(
                        get_aggregated_codon_outcomes(
                            result,
                            start_codon=start_codon,
                            generation=generation,
                        ),
                        value_kind="copy_count",
                    ),
                }
            )

        convergence = []
        for item in request.get("convergence", []):
            start_scope = str(item["start_scope"])
            start_key = str(item["start_key"])
            basis = str(item["basis"])
            tolerance = float(item["tolerance"])
            convergence.append(
                {
                    "start_scope": start_scope,
                    "start_key": start_key,
                    "basis": basis,
                    "tolerance": tolerance,
                    "table": serialize_table(
                        get_aggregated_convergence(
                            result,
                            start_scope=start_scope,
                            start_key=start_key,
                            basis=basis,
                            tolerance=tolerance,
                        ),
                        value_kind="status",
                    ),
                }
            )

        return success_envelope(
            mode="aggregated_sampled",
            scientific_authority="experimental_sampled",
            data={
                "seed": result.seed,
                "n_generations": result.n_generations,
                "start_counts": dict(result.start_counts),
                "total_start_count": result.total_start_count,
                "generation_counts": [
                    serialize_generation_counts(generation_counts)
                    for generation_counts in result.generations
                ],
                "final_live_codon": serialize_counter(result.final_live_codon),
                "final_live_amino_acid": serialize_counter(result.final_live_amino_acid),
                "final_live_by_start_codon": serialize_nested_counter(
                    result.final_live_by_start_codon
                ),
                "total_stopped": result.total_stopped,
                "scopes": [_aggregated_scope_payload(result, scope) for scope in scopes],
                "codon_outcomes": codon_outcomes,
                "convergence": convergence,
            },
        )

    @service.post("/api/v1/comparisons/exact", tags=["comparisons"], response_model=None)
    def exact_comparison(request: dict[str, Any]) -> dict[str, Any]:
        metric = str(request["metric"])
        scope = request["scope"]
        baseline = request["baseline"]
        candidate = request["candidate"]
        baseline_oversized = _exact_oversized_response(baseline["simulation"])
        if baseline_oversized is not None:
            return baseline_oversized
        candidate_oversized = _exact_oversized_response(candidate["simulation"])
        if candidate_oversized is not None:
            return candidate_oversized
        baseline_analysis = _exact_analysis_from_request(baseline["simulation"])
        candidate_analysis = _exact_analysis_from_request(candidate["simulation"])
        comparison = compare_numeric_metric(
            _exact_metric_table(baseline_analysis, metric=metric, scope=scope),
            _exact_metric_table(candidate_analysis, metric=metric, scope=scope),
            metric=metric,
            baseline_label=str(baseline["label"]),
            candidate_label=str(candidate["label"]),
        )
        return success_envelope(
            mode="exact_comparison",
            scientific_authority="exact_probability",
            data={
                "metric": comparison.metric,
                "baseline_label": comparison.baseline_label,
                "candidate_label": comparison.candidate_label,
                "key_columns": list(comparison.key_columns),
                "table": serialize_table(comparison.table, value_kind="delta"),
            },
        )

    @service.post("/api/v1/comparisons/exact-vs-sampled", tags=["comparisons"], response_model=None)
    def exact_vs_sampled_comparison(request: dict[str, Any]) -> dict[str, Any]:
        metric = str(request["metric"])
        scope = {"start_scope": "population", "start_key": "all"}
        exact_oversized = _exact_oversized_response(request["exact"])
        if exact_oversized is not None:
            return exact_oversized
        sampled_oversized = _aggregated_oversized_response(request["sampled"])
        if sampled_oversized is not None:
            return sampled_oversized
        exact_analysis = _exact_analysis_from_request(request["exact"])
        sampled_result = _aggregated_result_from_request(request["sampled"])
        comparison = compare_exact_to_sampled(
            _exact_metric_table(exact_analysis, metric=metric, scope=scope),
            _aggregated_metric_table(sampled_result, metric=metric, scope=scope),
            metric=metric,
            denominator_scope=str(request["denominator_scope"]),
            familywise_alpha=float(request.get("familywise_alpha", 0.01)),
        )
        return success_envelope(
            mode="exact_vs_sampled",
            scientific_authority="exact_probability",
            data={
                "metric": comparison.metric,
                "denominator_scope": comparison.denominator_scope,
                "familywise_alpha": comparison.familywise_alpha,
                "family_size": comparison.family_size,
                "table": serialize_table(comparison.table, value_kind="calibration"),
            },
        )

    return service


app = create_app()
