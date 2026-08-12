"""Biological definitions shared by exact, sampled, and UI adapters."""

from __future__ import annotations


BASES = ["A", "C", "G", "T"]
STOP_CODONS = {"TAA", "TAG", "TGA"}

CODON_TABLE = {
    "TTT": "Phe", "TTC": "Phe", "TTA": "Leu", "TTG": "Leu",
    "CTT": "Leu", "CTC": "Leu", "CTA": "Leu", "CTG": "Leu",
    "ATT": "Ile", "ATC": "Ile", "ATA": "Ile", "ATG": "Met",
    "GTT": "Val", "GTC": "Val", "GTA": "Val", "GTG": "Val",
    "TCT": "Ser", "TCC": "Ser", "TCA": "Ser", "TCG": "Ser",
    "CCT": "Pro", "CCC": "Pro", "CCA": "Pro", "CCG": "Pro",
    "ACT": "Thr", "ACC": "Thr", "ACA": "Thr", "ACG": "Thr",
    "GCT": "Ala", "GCC": "Ala", "GCA": "Ala", "GCG": "Ala",
    "TAT": "Tyr", "TAC": "Tyr", "TAA": "Stop", "TAG": "Stop",
    "CAT": "His", "CAC": "His", "CAA": "Gln", "CAG": "Gln",
    "AAT": "Asn", "AAC": "Asn", "AAA": "Lys", "AAG": "Lys",
    "GAT": "Asp", "GAC": "Asp", "GAA": "Glu", "GAG": "Glu",
    "TGT": "Cys", "TGC": "Cys", "TGA": "Stop", "TGG": "Trp",
    "CGT": "Arg", "CGC": "Arg", "CGA": "Arg", "CGG": "Arg",
    "AGT": "Ser", "AGC": "Ser", "AGA": "Arg", "AGG": "Arg",
    "GGT": "Gly", "GGC": "Gly", "GGA": "Gly", "GGG": "Gly",
}

AA_FULL = {
    "Ala": "Alanine", "Arg": "Arginine", "Asn": "Asparagine", "Asp": "Aspartate",
    "Cys": "Cysteine", "Gln": "Glutamine", "Glu": "Glutamate", "Gly": "Glycine",
    "His": "Histidine", "Ile": "Isoleucine", "Leu": "Leucine", "Lys": "Lysine",
    "Met": "Methionine", "Phe": "Phenylalanine", "Pro": "Proline", "Ser": "Serine",
    "Stop": "Stop codon", "Thr": "Threonine", "Trp": "Tryptophan", "Tyr": "Tyrosine",
    "Val": "Valine",
}

VALID_CODONS = sorted(
    b1 + b2 + b3
    for b1 in BASES
    for b2 in BASES
    for b3 in BASES
    if b1 + b2 + b3 not in STOP_CODONS
)
ALL_AAS = sorted({aa for aa in CODON_TABLE.values() if aa != "Stop"})

AA_PROPERTIES = {
    "Ala": ("hydrophobic", False, True),
    "Val": ("hydrophobic", False, False),
    "Ile": ("hydrophobic", False, False),
    "Leu": ("hydrophobic", False, False),
    "Met": ("hydrophobic", False, False),
    "Phe": ("hydrophobic", True, False),
    "Trp": ("hydrophobic", True, False),
    "Pro": ("special", False, False),
    "Gly": ("special", False, True),
    "Cys": ("special", False, False),
    "Ser": ("polar_uncharged", False, True),
    "Thr": ("polar_uncharged", False, False),
    "Asn": ("polar_uncharged", False, False),
    "Gln": ("polar_uncharged", False, False),
    "Tyr": ("polar_uncharged", True, False),
    "His": ("pos_charged", True, False),
    "Lys": ("pos_charged", False, False),
    "Arg": ("pos_charged", False, False),
    "Asp": ("neg_charged", False, False),
    "Glu": ("neg_charged", False, False),
}

PROPERTY_LABELS = {
    "hydrophobic": "Hydrophobic",
    "polar_uncharged": "Polar uncharged",
    "pos_charged": "Positively charged",
    "neg_charged": "Negatively charged",
    "special": "Special (Cys/Gly/Pro)",
}

AA_AROMATIC = {aa for aa, (_group, aromatic, _small) in AA_PROPERTIES.items() if aromatic}
AA_SMALL = {aa for aa, (_group, _aromatic, small) in AA_PROPERTIES.items() if small}


def get_primary_group(aa: str) -> str:
    """Return the scientific property identifier for an amino acid."""
    return AA_PROPERTIES.get(aa, ("unknown", False, False))[0]


def get_primary_group_name(aa: str) -> str:
    """Return the existing user-visible label for an amino-acid property."""
    key = get_primary_group(aa)
    return PROPERTY_LABELS.get(key, key)


def count_codons_for_aa(aa: str) -> int:
    """Count sense codons encoding an amino acid."""
    return sum(1 for codon, encoded_aa in CODON_TABLE.items() if encoded_aa == aa and codon not in STOP_CODONS)


CODON_COUNT_MAP = {aa: count_codons_for_aa(aa) for aa in ALL_AAS}
CODON_COUNT_GROUPS: dict[int, list[str]] = {}
for amino_acid in ALL_AAS:
    codon_count = CODON_COUNT_MAP[amino_acid]
    CODON_COUNT_GROUPS.setdefault(codon_count, []).append(amino_acid)
for codon_count in CODON_COUNT_GROUPS:
    CODON_COUNT_GROUPS[codon_count].sort()


def get_codon_count(aa: str) -> int:
    """Return the sense-codon degeneracy for an amino acid."""
    return CODON_COUNT_MAP.get(aa, 0)
