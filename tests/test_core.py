import json
import tempfile
import unittest
from pathlib import Path
from eve.core import Memory, make_proposal, validate_proposal


class EveTest(unittest.TestCase):
    def test_memory_is_persistent_and_isolated(self):
        with tempfile.TemporaryDirectory() as root:
            a = Memory(Path(root) / "eve")
            b = Memory(Path(root) / "other")
            a.add("hypothesis", "test hypothesis")
            self.assertEqual(len(Memory(Path(root) / "eve").read()), 1)
            self.assertEqual(b.read(), [])

    def test_valid_intake_pending(self):
        with tempfile.TemporaryDirectory() as root:
            memory = Memory(root)
            proposal = make_proposal("genesis", "eve", "critique", "question", "better tests")
            record = memory.intake(proposal)
            self.assertEqual(record["status"], "untrusted_pending_review")
            with self.assertRaises(ValueError):
                memory.intake(proposal)

    def test_tampering_rejected(self):
        p = make_proposal("genesis", "eve", "hypothesis", "test", "evidence")
        p["expected_benefit"] = "modified"
        with self.assertRaisesRegex(ValueError, "hash"):
            validate_proposal(p)

    def test_wrong_recipient_rejected(self):
        p = make_proposal("eve", "genesis", "test", "task", "result")
        with self.assertRaises(ValueError):
            validate_proposal(p)

    def test_unexpected_field_rejected(self):
        p = make_proposal("genesis", "eve", "test", "task", "result")
        p["run"] = "bad"
        with self.assertRaises(ValueError):
            validate_proposal(p)


if __name__ == "__main__":
    unittest.main()
