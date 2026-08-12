"""Mutation probability presets and substitution-matrix construction."""

from __future__ import annotations

from typing import TypeAlias


SubstitutionRow: TypeAlias = dict[str, float]
SubstitutionMatrix: TypeAlias = dict[str, SubstitutionRow]

PRESET_AT = 1 / 6
PRESET_AG = 2 / 3
PRESET_AC = 1 / 6


def build_substitution_matrix(
    p_at: float,
    p_ag: float,
    p_ac: float,
) -> SubstitutionMatrix:
    """Build the historical transition/transversion mapping in insertion order."""
    return {
        "A": {"C": p_ac, "G": p_ag, "T": p_at},
        "C": {"A": p_ac, "G": p_at, "T": p_ag},
        "G": {"A": p_ag, "C": p_at, "T": p_ac},
        "T": {"A": p_at, "C": p_ag, "G": p_ac},
    }
