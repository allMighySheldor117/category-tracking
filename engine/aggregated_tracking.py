"""Memory-bounded sampled mutation counts with an explicit local seed."""

from __future__ import annotations

from collections import Counter
from dataclasses import dataclass
from itertools import accumulate
import random
from typing import Iterable

from .genetic_code import (
    ALL_AAS,
    CODON_TABLE,
    PROPERTY_LABELS,
    STOP_CODONS,
    VALID_CODONS,
    get_primary_group_name,
)
from .models import (
    AggregatedGenerationCounts,
    AggregatedSampledResult,
    InvalidScientificScopeError,
    StartWeights,
)
from .mutation_matrix import SubstitutionMatrix


CANONICAL_STOP_ORDER = tuple(
    codon for codon in CODON_TABLE if codon in STOP_CODONS
)
CANONICAL_CATEGORY_ORDER = tuple(PROPERTY_LABELS.values())
CODON_TO_AMINO_ACID = {codon: CODON_TABLE[codon] for codon in CODON_TABLE}
CODON_TO_CATEGORY = {
    codon: get_primary_group_name(amino_acid)
    for codon, amino_acid in CODON_TO_AMINO_ACID.items()
}


@dataclass
class _GenerationAccumulator:
    live_codon: Counter[str]
    live_amino_acid: Counter[str]
    live_category: Counter[str]
    live_by_start_codon: Counter[str]
    live_by_start_trait: Counter[str]
    current_codon_by_start_codon: dict[str, Counter[str]]
    new_stop_codon_by_start_codon: dict[str, Counter[str]]


def _new_accumulator() -> _GenerationAccumulator:
    return _GenerationAccumulator(
        live_codon=Counter(),
        live_amino_acid=Counter(),
        live_category=Counter(),
        live_by_start_codon=Counter(),
        live_by_start_trait=Counter(),
        current_codon_by_start_codon={codon: Counter() for codon in VALID_CODONS},
        new_stop_codon_by_start_codon={codon: Counter() for codon in VALID_CODONS},
    )


def _ordered_counter(counter: Counter[str], order: Iterable[str]) -> Counter[str]:
    return Counter({key: counter[key] for key in order if counter[key]})


def _normalized_start_counts(start_weights: StartWeights) -> dict[str, int]:
    for codon in start_weights:
        if codon not in VALID_CODONS:
            raise InvalidScientificScopeError(f"Invalid scientific scope codon={codon}.")
    return {
        codon: max(0, int(start_weights.get(codon, 0)))
        for codon in VALID_CODONS
    }


def _freeze_generation(
    generation: int,
    state: _GenerationAccumulator,
    cumulative_stops: int,
) -> AggregatedGenerationCounts:
    stop_codon_by_start_codon = {
        codon: _ordered_counter(
            state.new_stop_codon_by_start_codon[codon],
            CANONICAL_STOP_ORDER,
        )
        for codon in VALID_CODONS
    }
    stops_by_stop_codon: Counter[str] = Counter()
    stops_by_start_codon: Counter[str] = Counter()
    stops_by_start_trait: Counter[str] = Counter()
    for start_codon in VALID_CODONS:
        start_trait = CODON_TO_CATEGORY[start_codon]
        for stop_codon in CANONICAL_STOP_ORDER:
            count = stop_codon_by_start_codon[start_codon][stop_codon]
            if count:
                stops_by_stop_codon[stop_codon] += count
                stops_by_start_codon[start_codon] += count
                stops_by_start_trait[start_trait] += count
    new_stops = sum(stops_by_stop_codon.values())
    live_codon = _ordered_counter(state.live_codon, VALID_CODONS)
    return AggregatedGenerationCounts(
        generation=generation,
        live_codon=live_codon,
        live_amino_acid=_ordered_counter(state.live_amino_acid, ALL_AAS),
        live_category=_ordered_counter(state.live_category, CANONICAL_CATEGORY_ORDER),
        live_by_start_codon=_ordered_counter(state.live_by_start_codon, VALID_CODONS),
        live_by_start_trait=_ordered_counter(
            state.live_by_start_trait,
            CANONICAL_CATEGORY_ORDER,
        ),
        current_codon_by_start_codon={
            codon: _ordered_counter(
                state.current_codon_by_start_codon[codon],
                VALID_CODONS,
            )
            for codon in VALID_CODONS
        },
        new_stop_codon_by_start_codon=stop_codon_by_start_codon,
        new_stops_by_stop_codon=_ordered_counter(
            stops_by_stop_codon,
            CANONICAL_STOP_ORDER,
        ),
        new_stops_by_start_codon=_ordered_counter(
            stops_by_start_codon,
            VALID_CODONS,
        ),
        new_stops_by_start_trait=_ordered_counter(
            stops_by_start_trait,
            CANONICAL_CATEGORY_ORDER,
        ),
        total_live=sum(live_codon.values()),
        new_stops=new_stops,
        cumulative_stops=cumulative_stops,
    )


def _initial_final_counts(
    start_counts: dict[str, int],
) -> tuple[Counter[str], Counter[str], dict[str, Counter[str]]]:
    final_live_codon = Counter(
        {codon: start_counts[codon] for codon in VALID_CODONS if start_counts[codon]}
    )
    amino_acid_counts: Counter[str] = Counter()
    for codon in VALID_CODONS:
        count = start_counts[codon]
        if count:
            amino_acid_counts[CODON_TO_AMINO_ACID[codon]] += count
    final_live_by_start_codon = {
        codon: Counter({codon: start_counts[codon]}) if start_counts[codon] else Counter()
        for codon in VALID_CODONS
    }
    return (
        final_live_codon,
        _ordered_counter(amino_acid_counts, ALL_AAS),
        final_live_by_start_codon,
    )


def run_aggregated_experiment(
    n_generations: int,
    sub_matrix: SubstitutionMatrix,
    start_weights: StartWeights,
    seed: int,
) -> AggregatedSampledResult:
    """Stream sampled copies into generation-level integer counters."""
    if type(n_generations) is not int or n_generations < 0:
        raise ValueError("n_generations must be >= 0")
    if type(seed) is not int:
        raise TypeError("seed must be an int")

    start_counts = _normalized_start_counts(start_weights)
    total_start_count = sum(start_counts.values())
    generator = random.Random(seed)
    transitions = {
        base: (tuple(row), tuple(row.values()))
        for base, row in sub_matrix.items()
    }
    mutable_generations = tuple(
        _new_accumulator()
        for _generation in range(n_generations)
    )

    for start_codon in VALID_CODONS:
        start_trait = CODON_TO_CATEGORY[start_codon]
        for _copy_number in range(1, start_counts[start_codon] + 1):
            current_codon = start_codon
            for generation_index in range(n_generations):
                position = generator.randint(0, 2)
                old_base = current_codon[position]
                keys, probabilities = transitions[old_base]
                new_base = generator.choices(keys, probabilities)[0]
                current_codon = (
                    current_codon[:position]
                    + new_base
                    + current_codon[position + 1:]
                )
                state = mutable_generations[generation_index]
                if current_codon in STOP_CODONS:
                    state.new_stop_codon_by_start_codon[start_codon][current_codon] += 1
                    break

                current_amino_acid = CODON_TO_AMINO_ACID[current_codon]
                current_trait = CODON_TO_CATEGORY[current_codon]
                state.live_codon[current_codon] += 1
                state.live_amino_acid[current_amino_acid] += 1
                state.live_category[current_trait] += 1
                state.live_by_start_codon[start_codon] += 1
                state.live_by_start_trait[start_trait] += 1
                state.current_codon_by_start_codon[start_codon][current_codon] += 1

    cumulative_values = tuple(
        accumulate(
            sum(
                sum(counter.values())
                for counter in state.new_stop_codon_by_start_codon.values()
            )
            for state in mutable_generations
        )
    )
    generations = tuple(
        _freeze_generation(generation, state, cumulative_stops)
        for generation, state, cumulative_stops in zip(
            range(1, n_generations + 1),
            mutable_generations,
            cumulative_values,
        )
    )

    if generations:
        final_generation = generations[-1]
        final_live_codon = Counter(final_generation.live_codon)
        final_live_amino_acid = Counter(final_generation.live_amino_acid)
        final_live_by_start_codon = {
            codon: Counter(final_generation.current_codon_by_start_codon[codon])
            for codon in VALID_CODONS
        }
        total_stopped = final_generation.cumulative_stops
    else:
        (
            final_live_codon,
            final_live_amino_acid,
            final_live_by_start_codon,
        ) = _initial_final_counts(start_counts)
        total_stopped = 0

    return AggregatedSampledResult(
        seed=seed,
        n_generations=n_generations,
        start_counts=start_counts,
        total_start_count=total_start_count,
        generations=generations,
        final_live_codon=final_live_codon,
        final_live_amino_acid=final_live_amino_acid,
        final_live_by_start_codon=final_live_by_start_codon,
        total_stopped=total_stopped,
    )
