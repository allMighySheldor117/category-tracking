"""Exhaustive comparisons for extracted biological and mutation primitives."""

from __future__ import annotations

import inspect
import unittest

import category_tracking as legacy
from engine import genetic_code
from engine import mutation_matrix


class GeneticCodeTests(unittest.TestCase):
    def test_biological_definitions_equal_legacy_values_and_order(self) -> None:
        comparisons = (
            (genetic_code.BASES, legacy.BASES),
            (genetic_code.STOP_CODONS, legacy.STOP_CODONS),
            (genetic_code.CODON_TABLE, legacy.CODON_TABLE),
            (genetic_code.AA_FULL, legacy.AA_FULL),
            (genetic_code.VALID_CODONS, legacy.VALID_CODONS),
            (genetic_code.ALL_AAS, legacy.ALL_AAS),
            (genetic_code.AA_PROPERTIES, legacy.AA_PROPERTIES),
            (genetic_code.AA_AROMATIC, legacy.AA_AROMATIC),
            (genetic_code.AA_SMALL, legacy.AA_SMALL),
            (genetic_code.CODON_COUNT_MAP, legacy.CODON_COUNT_MAP),
            (genetic_code.CODON_COUNT_GROUPS, legacy.CODON_COUNT_GROUPS),
        )
        for extracted, expected in comparisons:
            with self.subTest(definition=type(extracted).__name__):
                self.assertEqual(extracted, expected)
                if isinstance(extracted, dict):
                    self.assertEqual(list(extracted), list(expected))

        self.assertEqual(
            list(genetic_code.PROPERTY_LABELS.items()),
            [(key, label_and_color[0]) for key, label_and_color in legacy.PROPERTY_GROUPS.items()],
        )

    def test_codon_and_category_invariants(self) -> None:
        self.assertEqual(len(genetic_code.CODON_TABLE), 64)
        self.assertEqual(len(genetic_code.VALID_CODONS), 61)
        self.assertEqual(len(genetic_code.STOP_CODONS), 3)
        self.assertEqual(set(genetic_code.AA_PROPERTIES), set(genetic_code.ALL_AAS))
        self.assertEqual(set(genetic_code.PROPERTY_LABELS), {value[0] for value in genetic_code.AA_PROPERTIES.values()})
        self.assertEqual(sum(genetic_code.CODON_COUNT_MAP.values()), 61)

    def test_grouping_helpers_match_for_every_known_and_unknown_value(self) -> None:
        for amino_acid in [*legacy.AA_FULL, "unknown"]:
            with self.subTest(amino_acid=amino_acid):
                self.assertEqual(
                    genetic_code.get_primary_group(amino_acid),
                    legacy.get_primary_group(amino_acid),
                )
                self.assertEqual(
                    genetic_code.get_primary_group_name(amino_acid),
                    legacy.get_primary_group_name(amino_acid),
                )
                self.assertEqual(
                    genetic_code.count_codons_for_aa(amino_acid),
                    legacy.count_codons_for_aa(amino_acid),
                )
                self.assertEqual(
                    genetic_code.get_codon_count(amino_acid),
                    legacy.get_codon_count(amino_acid),
                )

    def test_presets_and_substitution_matrices_match_exactly(self) -> None:
        self.assertEqual(
            [mutation_matrix.PRESET_AT.hex(), mutation_matrix.PRESET_AG.hex(), mutation_matrix.PRESET_AC.hex()],
            [legacy.PRESET_AT.hex(), legacy.PRESET_AG.hex(), legacy.PRESET_AC.hex()],
        )
        cases = (
            (0.2, 0.5, 0.3),
            (1 / 3, 1 / 3, 1 / 3),
            (0.0, 0.0, 0.0),
            (-0.2, 1.4, -0.2),
        )
        for values in cases:
            with self.subTest(values=values):
                observed = mutation_matrix.build_substitution_matrix(*values)
                expected = legacy.build_substitution_matrix(*values)
                self.assertEqual(observed, expected)
                self.assertEqual(list(observed), list(expected))
                for base in observed:
                    self.assertEqual(list(observed[base]), list(expected[base]))
                    self.assertEqual(sum(observed[base].values()), sum(expected[base].values()))

    def test_new_public_functions_are_typed(self) -> None:
        functions = (
            genetic_code.get_primary_group,
            genetic_code.get_primary_group_name,
            genetic_code.count_codons_for_aa,
            genetic_code.get_codon_count,
            mutation_matrix.build_substitution_matrix,
        )
        for function in functions:
            with self.subTest(function=function.__name__):
                signature = inspect.signature(function)
                self.assertTrue(
                    all(parameter.annotation is not inspect.Parameter.empty for parameter in signature.parameters.values())
                )
                self.assertIsNot(signature.return_annotation, inspect.Signature.empty)

    def test_engine_primitives_contain_no_visual_metadata(self) -> None:
        for module in (genetic_code, mutation_matrix):
            names = set(vars(module))
            self.assertFalse({"AA_COLORS", "AA_COLOR_MAP", "PROPERTY_GROUP_BG", "parse_prob"} & names)


if __name__ == "__main__":
    unittest.main()
