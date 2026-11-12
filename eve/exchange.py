"""Signed, manual Genesis/Eve peer message envelopes.

HMAC proves that a peer with the pre-shared secret authored the message.
It does not prove which human/agent holds that secret. Use independent,
rotatable credentials, a protected transport, and least-privilege access.
"""
import hashlib
import hmac
import json
import os
from datetime import datetime, timezone, timedelta

from .core import validate_proposal

MAX_ENVELOPE = 40000
MAX_AGE = timedelta(days=7)


def canonical(data):
    return json.dumps(data, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()


def sign(proposal: dict, secret: str) -> dict:
    validate_proposal(proposal, recipient=proposal["recipient"])
    if proposal["sender"] == proposal["recipient"]:
        raise ValueError("Invalid sender")
    if not isinstance(secret, str) or len(secret) < 32:
        raise ValueError("Shared secret must be at least 32 characters")
    envelope = {"proposal": proposal, "auth": "hmac-sha256"}
    envelope["signature"] = hmac.new(secret.encode(), canonical(envelope), hashlib.sha256).hexdigest()
    return envelope


def verify(envelope: dict, secret: str, recipient="eve", now=None) -> dict:
    if not isinstance(envelope, dict) or set(envelope) != {"proposal", "auth", "signature"}:
        raise ValueError("Invalid envelope")
    if len(canonical(envelope)) > MAX_ENVELOPE or envelope["auth"] != "hmac-sha256":
        raise ValueError("Invalid envelope size or algorithm")
    if not isinstance(secret, str) or len(secret) < 32:
        raise ValueError("Shared secret must be at least 32 characters")
    signature = envelope["signature"]
    if not isinstance(signature, str) or len(signature) != 64:
        raise ValueError("Invalid signature")
    unsigned = {"proposal": envelope["proposal"], "auth": envelope["auth"]}
    expected = hmac.new(secret.encode(), canonical(unsigned), hashlib.sha256).hexdigest()
    if not hmac.compare_digest(expected, signature):
        raise ValueError("Authentication failed")
    proposal = validate_proposal(envelope["proposal"], recipient=recipient)
    timestamp = datetime.fromisoformat(proposal["created_at"].replace("Z", "+00:00"))
    now = now or datetime.now(timezone.utc)
    if timestamp < now - MAX_AGE or timestamp > now + timedelta(minutes=5):
        raise ValueError("Expired or future-dated proposal")
    return proposal


def shared_secret():
    secret = os.getenv("EVE_PEER_SHARED_SECRET", "")
    if len(secret) < 32:
        raise ValueError("Set EVE_PEER_SHARED_SECRET to a random secret (>=32 characters)")
    return secret
