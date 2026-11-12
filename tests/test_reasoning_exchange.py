import io
import json
import tempfile
import unittest
from datetime import datetime, timezone, timedelta
from pathlib import Path

from eve.core import Memory, make_proposal
from eve.exchange import sign, verify
from eve.reasoning import Reasoner

SECRET = "sample-only-test-secret-do-not-use-production-1234"


class DummyResponse:
    def __enter__(self):
        return io.BytesIO(json.dumps({"choices": [{"message": {"content": "Testable."}}]}).encode())
    def __exit__(self, *args):
        return False


class NewFeaturesTest(unittest.TestCase):
    def test_reasoning_fake_transport(self):
        captured = {}
        def fake(req, timeout):
            captured["url"] = req.full_url
            captured["body"] = json.loads(req.data)
            return DummyResponse()
        client = Reasoner(endpoint="http://127.0.0.1:11434/v1/chat/completions",
                          model="test-model", transport=fake)
        self.assertEqual(client.ask("Consider experiment"), "Testable.")
        self.assertEqual(captured["body"]["model"], "test-model")

    def test_remote_http_rejected(self):
        with self.assertRaises(ValueError):
            Reasoner(endpoint="http://example.com/v1/chat/completions", model="test")

    def test_signed_intake(self):
        with tempfile.TemporaryDirectory() as tmp:
            proposal = make_proposal("genesis", "eve", "critique", "Check benchmark", "Reduced error")
            envelope = sign(proposal, SECRET)
            valid = verify(envelope, SECRET)
            stored = Memory(tmp).intake(valid)
            self.assertEqual(stored["status"], "untrusted_pending_review")
            with self.assertRaises(ValueError):
                Memory(tmp).intake(valid)

    def test_tamper_rejected(self):
        proposal = make_proposal("genesis", "eve", "critique", "Check evidence", "More reliable")
        envelope = sign(proposal, SECRET)
        envelope["proposal"]["expected_benefit"] = "Altered"
        with self.assertRaises(ValueError):
            verify(envelope, SECRET)

    def test_wrong_key_rejected(self):
        proposal = make_proposal("genesis", "eve", "hypothesis", "Test", "Learn")
        envelope = sign(proposal, SECRET)
        with self.assertRaises(ValueError):
            verify(envelope, "another-long-key-for-testing-only-not-real")

    def test_old_proposal_rejected(self):
        proposal = make_proposal("genesis", "eve", "test", "Test", "Learn")
        envelope = sign(proposal, SECRET)
        later = datetime.now(timezone.utc) + timedelta(days=8)
        with self.assertRaises(ValueError):
            verify(envelope, SECRET, now=later)


if __name__ == "__main__":
    unittest.main()
