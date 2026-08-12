"""Exact probability tracking with the historical accumulation order."""

from __future__ import annotations

import collections

from .genetic_code import CODON_TABLE, STOP_CODONS, VALID_CODONS, get_primary_group
from .models import ExactSimulationResult
from .mutation_matrix import SubstitutionMatrix


def run_simulation(
    n_generations: int,
    sub_matrix: SubstitutionMatrix,
    start_weights: dict[str, float] | None = None,
) -> ExactSimulationResult:
    """Run the exact mutation simulation without altering legacy iteration order."""
    if start_weights is None:
        start_weights = {codon: 1.0 for codon in VALID_CODONS}

    enc_codon = collections.Counter()
    enc_aa = collections.Counter()
    enc_codon_cnt = collections.Counter()
    enc_aa_cnt = collections.Counter()
    fin_codon = collections.Counter()
    fin_aa = collections.Counter()
    per_gen_aa = [collections.Counter() for _ in range(n_generations)]
    start_to_fin = {}

    per_gen_cat_from = [
        collections.defaultdict(lambda: collections.Counter())
        for _ in range(n_generations)
    ]
    per_gen_aa_from = [
        collections.defaultdict(lambda: collections.Counter())
        for _ in range(n_generations)
    ]
    per_gen_aa_codon_from = [
        collections.defaultdict(lambda: collections.Counter())
        for _ in range(n_generations)
    ]
    per_gen_codon_from = [
        collections.defaultdict(lambda: collections.Counter())
        for _ in range(n_generations)
    ]
    per_gen_stop_cat_from = [collections.Counter() for _ in range(n_generations)]
    per_gen_stop_aa_from = [collections.Counter() for _ in range(n_generations)]
    per_gen_stop_codon_from = [collections.Counter() for _ in range(n_generations)]
    per_gen_stop_codon_to = [
        collections.defaultdict(lambda: collections.Counter())
        for _ in range(n_generations)
    ]

    stop_by_start_aa = collections.Counter()
    stop_by_start_prop = collections.Counter()
    stop_by_start_codon = collections.Counter()
    stop_by_pre_codon = collections.Counter()
    stop_by_stop_codon = collections.Counter()
    stop_detail = []

    for codon in VALID_CODONS:
        w0 = start_weights.get(codon, 0.0)
        if w0 <= 0:
            continue
        aa = CODON_TABLE[codon]
        enc_codon[codon] += w0
        enc_aa[aa] += w0
        enc_codon_cnt[codon] += int(w0)
        enc_aa_cnt[aa] += int(w0)

    for start_codon in VALID_CODONS:
        w0 = start_weights.get(start_codon, 0.0)
        if w0 <= 0:
            continue
        start_aa = CODON_TABLE[start_codon]
        start_grp = get_primary_group(start_aa)
        live = {start_codon: w0}

        for gen in range(n_generations):
            next_live = collections.defaultdict(float)
            for codon, weight in live.items():
                for pos in range(3):
                    old_base = codon[pos]
                    for new_base, base_prob in sub_matrix[old_base].items():
                        new_codon = codon[:pos] + new_base + codon[pos + 1:]
                        p = weight * (1.0 / 3.0) * base_prob
                        if new_codon in STOP_CODONS:
                            sa = CODON_TABLE[start_codon]
                            pa = CODON_TABLE[codon]
                            stop_by_start_aa[sa] += p
                            stop_by_start_prop[start_grp] += p
                            stop_by_start_codon[start_codon] += p
                            stop_by_pre_codon[codon] += p
                            stop_by_stop_codon[new_codon] += p
                            per_gen_stop_cat_from[gen][start_grp] += p
                            per_gen_stop_aa_from[gen][start_aa] += p
                            per_gen_stop_codon_from[gen][start_codon] += p
                            per_gen_stop_codon_to[gen][start_codon][new_codon] += p
                            stop_detail.append((start_codon, sa, codon, pa, new_codon, p))
                        else:
                            next_live[new_codon] += p
                            aa = CODON_TABLE[new_codon]
                            enc_codon[new_codon] += p
                            enc_aa[aa] += p
                            enc_codon_cnt[new_codon] += 1
                            enc_aa_cnt[aa] += 1
                            per_gen_aa[gen][aa] += p
                            cur_grp = get_primary_group(aa)
                            per_gen_cat_from[gen][start_grp][cur_grp] += p
                            per_gen_aa_from[gen][start_aa][aa] += p
                            per_gen_aa_codon_from[gen][start_aa][new_codon] += p
                            per_gen_codon_from[gen][start_codon][new_codon] += p
            live = dict(next_live)
            if not live:
                break

        final_for_start = collections.Counter()
        for codon, weight in live.items():
            fin_codon[codon] += weight
            fin_aa[CODON_TABLE[codon]] += weight
            final_for_start[codon] += weight
        start_to_fin[start_codon] = final_for_start

    active_starts = sum(1 for weight in start_weights.values() if weight > 0)
    total_start_copies = sum(weight for weight in start_weights.values() if weight > 0)
    total_stop_prob = sum(stop_by_stop_codon.values())

    per_gen_cat_from = [{key: dict(value) for key, value in generation.items()} for generation in per_gen_cat_from]
    per_gen_aa_from = [{key: dict(value) for key, value in generation.items()} for generation in per_gen_aa_from]
    per_gen_aa_codon_from = [
        {key: dict(value) for key, value in generation.items()}
        for generation in per_gen_aa_codon_from
    ]
    per_gen_codon_from = [
        {key: dict(value) for key, value in generation.items()}
        for generation in per_gen_codon_from
    ]
    per_gen_stop_cat_from = [dict(generation) for generation in per_gen_stop_cat_from]
    per_gen_stop_aa_from = [dict(generation) for generation in per_gen_stop_aa_from]
    per_gen_stop_codon_from = [dict(generation) for generation in per_gen_stop_codon_from]
    per_gen_stop_codon_to = [
        {key: dict(value) for key, value in generation.items()}
        for generation in per_gen_stop_codon_to
    ]

    stats = {
        "n_starts": active_starts,
        "total_start_copies": total_start_copies,
        "n_generations": n_generations,
        "unique_aas_seen": len(enc_aa),
        "unique_codons_seen": len(enc_codon),
        "total_enc_weight": sum(enc_codon.values()),
        "total_fin_weight": sum(fin_codon.values()),
        "total_stop_prob": total_stop_prob,
    }
    stop_data = {
        "by_start_aa": stop_by_start_aa,
        "by_start_prop": stop_by_start_prop,
        "by_start_codon": stop_by_start_codon,
        "by_pre_codon": stop_by_pre_codon,
        "by_stop_codon": stop_by_stop_codon,
        "detail": stop_detail,
        "total_prob": total_stop_prob,
    }
    track_data = {
        "per_gen_cat_from": per_gen_cat_from,
        "per_gen_aa_from": per_gen_aa_from,
        "per_gen_aa_codon_from": per_gen_aa_codon_from,
        "per_gen_codon_from": per_gen_codon_from,
        "per_gen_stop_cat_from": per_gen_stop_cat_from,
        "per_gen_stop_aa_from": per_gen_stop_aa_from,
        "per_gen_stop_codon_from": per_gen_stop_codon_from,
        "per_gen_stop_codon_to": per_gen_stop_codon_to,
    }
    return ExactSimulationResult(
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
