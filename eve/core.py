"""Local-only Eve memory and peer proposal intake. No code execution or network calls."""
from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from tempfile import NamedTemporaryFile
from uuid import UUID, uuid4

PROTOCOL = "coevolution.v1"
ALLOWED_SENDERS = {"genesis", "eve"}
ALLOWED_KINDS = {"hypothesis", "test", "critique", "candidate_patch"}
MAX_SIZE = 32768


def validate_proposal(proposal: dict, recipient: str = "eve") -> dict:
    """Validate an untrusted peer message; NEVER execute content."""
    if not isinstance(proposal, dict) or set(proposal) != {
        "protocol", "proposal_id", "sender", "recipient", "kind",
        "problem_statement", "evidence_links", "reproduction_steps",
        "expected_benefit", "risks", "content_hash", "created_at"
    }:
        raise ValueError("Invalid proposal fields")
    if proposal["protocol"] != PROTOCOL:
        raise ValueError("Unsupported protocol")
    if proposal["sender"] not in ALLOWED_SENDERS or proposal["recipient"] != recipient:
        raise ValueError("Invalid participants")
    if proposal["sender"] == proposal["recipient"]:
        raise ValueError("Self-addressed peer proposal")
    if proposal["kind"] not in ALLOWED_KINDS:
        raise ValueError("Invalid proposal kind")
    try:
        UUID(proposal["proposal_id"])
        timestamp = datetime.fromisoformat(proposal["created_at"].replace("Z", "+00:00"))
        if timestamp.tzinfo is None:
            raise ValueError("Timezone required")
    except (TypeError, ValueError) as exc:
        raise ValueError("Invalid id or timestamp") from exc
    for field in ("problem_statement", "expected_benefit"):
        if not isinstance(proposal[field], str) or not proposal[field].strip():
            raise ValueError("Missing text: " + field)
    for field in ("evidence_links", "reproduction_steps", "risks"):
        if not isinstance(proposal[field], list) or len(proposal[field]) > 30 or not all(
            isinstance(v, str) and len(v) <= 2048 for v in proposal[field]
        ):
            raise ValueError("Invalid array: " + field)
    canonical = dict(proposal)
    digest = canonical.pop("content_hash")
    actual = "sha256:" + hashlib.sha256(json.dumps(canonical, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    if digest != actual:
        raise ValueError("Content hash mismatch")
    if len(json.dumps(proposal, ensure_ascii=False).encode()) > MAX_SIZE:
        raise ValueError("Oversized proposal")
    return proposal


def make_proposal(sender: str, recipient: str, kind: str, problem: str, benefit: str) -> dict:
    result = {
        "protocol": PROTOCOL, "proposal_id": str(uuid4()), "sender": sender,
        "recipient": recipient, "kind": kind, "problem_statement": problem,
        "evidence_links": [], "reproduction_steps": [], "expected_benefit": benefit,
        "risks": [], "created_at": datetime.now(timezone.utc).isoformat()
    }
    result["content_hash"] = "sha256:" + hashlib.sha256(json.dumps(result, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode()).hexdigest()
    return validate_proposal(result, recipient)


class Memory:
    """Isolated versionable local state; uses atomic replacement for writes."""
    def __init__(self, root: str | Path):
        self.root = Path(root).resolve()
        self.root.mkdir(parents=True, exist_ok=True)
        self.path = self.root / "eve-memory.json"

    def read(self) -> list[dict]:
        if not self.path.exists():
            return []
        value = json.loads(self.path.read_text(encoding="utf-8"))
        if not isinstance(value, list):
            raise ValueError("Invalid memory state")
        return value

    def add(self, category: str, content: str, evidence: str = "") -> dict:
        if category not in {"observation", "hypothesis", "validated", "failure"}:
            raise ValueError("Invalid memory category")
        if not content.strip() or len(content) > 8000:
            raise ValueError("Invalid memory content")
        state = self.read()
        record = {"id": str(uuid4()), "category": category, "content": content,
                  "evidence": evidence, "created_at": datetime.now(timezone.utc).isoformat()}
        state.append(record)
        self._write(state)
        return record

    def intake(self, proposal: dict) -> dict:
        validate_proposal(proposal)
        state = self.read()
        normalized_id = str(UUID(proposal["proposal_id"]))
        if any(item.get("proposal_id") and str(UUID(item["proposal_id"])) == normalized_id for item in state):
            raise ValueError("Duplicate proposal")
        record = {"id": str(uuid4()), "category": "peer_proposal",
                  "proposal_id": normalized_id, "content": proposal,
                  "status": "untrusted_pending_review",
                  "created_at": datetime.now(timezone.utc).isoformat()}
        state.append(record)
        self._write(state)
        return record

    def _write(self, state: list[dict]) -> None:
        temp_name = None
        try:
            with NamedTemporaryFile(mode="w", encoding="utf-8", dir=self.root,
                                    prefix=".eve-", suffix=".tmp", delete=False) as tmp:
                temp_name = tmp.name
                json.dump(state, tmp, ensure_ascii=False, indent=2)
                tmp.flush()
                os.fsync(tmp.fileno())
            os.replace(temp_name, self.path)
        finally:
            if temp_name and os.path.exists(temp_name):
                os.unlink(temp_name)
