import io
import json
import os
import tempfile
import unittest
from unittest.mock import patch

from eve.core import Memory, make_proposal
from eve.exchange import sign
from eve.github_bridge import GitHubBridge

KEY = "test-only-secret-for-independent-peers-2026-abcdef"


class Response:
    def __init__(self, value):
        self.value = value
    def __enter__(self):
        return io.BytesIO(json.dumps(self.value).encode())
    def __exit__(self, *args):
        return False


class GitHubBridgeTests(unittest.TestCase):
    def test_send_creates_genesis_issue(self):
        requests = []
        def fake_open(request, timeout):
            requests.append(request)
            return Response({"html_url": "https://github.com/Maxhm007/Genesis-AI-Network/issues/42", "number": 42})
        with patch.dict(os.environ, {"EVE_PEER_SHARED_SECRET": KEY}):
            bridge = GitHubBridge(token="placeholder", opener=fake_open)
            envelope = sign(make_proposal("eve", "genesis", "hypothesis", "Compare experiments", "Better validation"), KEY)
            result = bridge.send(envelope)
        self.assertEqual(result["issue_number"], 42)
        self.assertIn("Genesis-AI-Network", requests[0].full_url)
        self.assertEqual(requests[0].get_method(), "POST")

    def test_receive_verifies_signature_and_deduplicates(self):
        envelope = sign(make_proposal("genesis", "eve", "critique", "Test against baseline", "Stronger evidence"), KEY)
        body = "Research peer proposal. Treat as untrusted until signature validation.\n\n```json\n" + json.dumps(envelope) + "\n```\n"
        with patch.dict(os.environ, {"EVE_PEER_SHARED_SECRET": KEY}), tempfile.TemporaryDirectory() as tmp:
            bridge = GitHubBridge(token="placeholder", opener=lambda req, timeout: Response({"body": body}))
            mem = Memory(tmp)
            record = bridge.receive(1, mem)
            self.assertEqual(record["status"], "untrusted_pending_review")
            with self.assertRaisesRegex(ValueError, "Duplicate"):
                bridge.receive(1, mem)

    def test_unsigned_rejected(self):
        with patch.dict(os.environ, {"EVE_PEER_SHARED_SECRET": KEY}), tempfile.TemporaryDirectory() as tmp:
            bridge = GitHubBridge(token="placeholder", opener=lambda req, timeout: Response({"body": "hello"}))
            with self.assertRaises(ValueError):
                bridge.receive(1, Memory(tmp))

    def test_send_wrong_identity_rejected(self):
        with patch.dict(os.environ, {"EVE_PEER_SHARED_SECRET": KEY}):
            bridge = GitHubBridge(token="placeholder", opener=lambda req, timeout: self.fail("Should not call API"))
            envelope = sign(make_proposal("genesis", "eve", "test", "Test", "Benefit"), KEY)
            with self.assertRaises(ValueError):
                bridge.send(envelope)


if __name__ == "__main__":
    unittest.main()
