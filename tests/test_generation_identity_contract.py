from __future__ import annotations

import unittest

from src.contracts.generation_identity import (
    GENERATION_IDENTITY_SCHEMA_VERSION,
    LEGACY_UNVERSIONED,
    GenerationIdentity,
    compare_generation_identities,
)


def identity(**changes: object) -> GenerationIdentity:
    values: dict[str, object] = {
        "program": "P",
        "runtime_generation": "p-runtime-1",
        "source_head": "abc123",
        "schema_version": "signal.v1",
        "method_version": "method.v1",
        "cutoff_utc": "2026-07-25T00:00:00Z",
        "classifier_version": "manual_operator_classifier.v4",
    }
    values.update(changes)
    return GenerationIdentity(identity_schema_version=GENERATION_IDENTITY_SCHEMA_VERSION, **values)


class GenerationIdentityContractTests(unittest.TestCase):
    def test_valid_p_and_m_identities(self) -> None:
        self.assertEqual(identity().program, "P")
        macro = identity(program="M", runtime_generation="m-runtime-1")
        self.assertEqual(macro.program, "M")

    def test_invalid_program_and_blank_required_values(self) -> None:
        with self.assertRaises(ValueError): identity(program="X")
        for field in ("runtime_generation", "source_head", "schema_version", "method_version", "cutoff_utc"):
            with self.subTest(field=field), self.assertRaises(ValueError): identity(**{field: ""})

    def test_naive_timestamp_rejected_and_optional_versions_are_legacy(self) -> None:
        with self.assertRaises(ValueError): identity(cutoff_utc="2026-07-25T00:00:00")
        value = identity(classifier_version=None, score_version="")
        self.assertEqual(value.classifier_version, LEGACY_UNVERSIONED)
        self.assertEqual(value.score_version, LEGACY_UNVERSIONED)

    def test_deterministic_serialization(self) -> None:
        first = identity().to_dict()
        second = identity().to_dict()
        self.assertEqual(first, second)
        self.assertEqual(first["cutoff_utc"], "2026-07-25T00:00:00Z")

    def test_program_runtime_schema_and_legacy_boundaries(self) -> None:
        base = identity()
        self.assertEqual(compare_generation_identities(base, identity(program="M" , runtime_generation="m-runtime-1")).status, "not_comparable_program")
        self.assertEqual(compare_generation_identities(base, identity(runtime_generation="p-runtime-2")).status, "not_comparable_runtime_generation")
        self.assertEqual(compare_generation_identities(base, identity(schema_version="signal.v2")).status, "not_comparable_schema_version")
        result = compare_generation_identities(base, identity(classifier_version=LEGACY_UNVERSIONED), "classifier_version")
        self.assertEqual(result.status, "not_comparable_legacy_unversioned")
        self.assertFalse(result.comparable)

    def test_method_reset_compatibility_and_source_lineage(self) -> None:
        base = identity()
        method = compare_generation_identities(base, identity(method_version="method.v2"))
        self.assertEqual(method.status, "baseline_reset_required_method_version")
        self.assertFalse(method.comparable)
        self.assertTrue(method.baseline_reset_required)
        source = compare_generation_identities(base, identity(source_head="def456"))
        self.assertEqual(source.status, "comparable")
        self.assertTrue(source.comparable)
        self.assertEqual(compare_generation_identities(base, base).reason_codes, ("generation_contract_match",))

    def test_unknown_comparison_component_is_rejected(self) -> None:
        with self.assertRaises(ValueError): compare_generation_identities(identity(), identity(), "unknown_version")


if __name__ == "__main__":
    unittest.main()
