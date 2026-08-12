"""Sampled per-copy mutation paths with the historical RNG contract."""

from __future__ import annotations

import collections
import random as _random

from .genetic_code import CODON_TABLE, STOP_CODONS, VALID_CODONS
from .models import SampledSimulationResult
from .mutation_matrix import SubstitutionMatrix


def run_experiment(
    n_generations: int,
    sub_matrix: SubstitutionMatrix,
    start_weights: dict[str, float],
) -> SampledSimulationResult:
    """Run sampled copies using Python's module-level random generator."""
    records = []
    sample_fin_codon = collections.Counter()
    sample_fin_aa = collections.Counter()
    sample_start_to_fin = {codon: collections.Counter() for codon in VALID_CODONS}

    cum = {}
    for base, row in sub_matrix.items():
        keys = list(row.keys())
        probs = [row[key] for key in keys]
        cum[base] = (keys, probs)

    for start_codon in VALID_CODONS:
        n_copies = int(start_weights.get(start_codon, 0))
        start_aa = CODON_TABLE[start_codon]
        for copy_idx in range(1, n_copies + 1):
            codon = start_codon
            hit_stop = False
            stop_gen = None
            path = [start_codon]
            for gen in range(n_generations):
                pos = _random.randint(0, 2)
                old_base = codon[pos]
                keys, probs = cum[old_base]
                new_base = _random.choices(keys, probs)[0]
                new_codon = codon[:pos] + new_base + codon[pos + 1:]
                if new_codon in STOP_CODONS:
                    hit_stop = True
                    stop_gen = gen + 1
                    codon = new_codon
                    path.append(codon)
                    break
                codon = new_codon
                path.append(codon)
            final_aa = CODON_TABLE.get(codon, "Stop")
            records.append(
                {
                    "start": start_codon,
                    "start_aa": start_aa,
                    "final": codon,
                    "final_aa": final_aa,
                    "hit_stop": hit_stop,
                    "stop_gen": stop_gen,
                    "copy": copy_idx,
                    "path": path,
                }
            )
            if not hit_stop:
                sample_fin_codon[codon] += 1
                sample_fin_aa[final_aa] += 1
                sample_start_to_fin[start_codon][codon] += 1

    return SampledSimulationResult(
        records=records,
        sample_fin_codon=sample_fin_codon,
        sample_fin_aa=sample_fin_aa,
        sample_start_to_fin=sample_start_to_fin,
    )
