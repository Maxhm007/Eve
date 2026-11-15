"""Eve continuous-evolution turn receiver.

This local job reads Nexus's published turn ledger, runs existing Eve
verification and a bounded local repair-candidate scan, then writes ONLY to
Eve's own acknowledgement issue. It never claims to merge or heal a peer.
"""
import json
import os
import subprocess
import sys
import urllib.request

GENESIS = "Maxhm007/Genesis-AI-Network"
EVE = "Maxhm007/Eve"
GENESIS_LEDGER = 1212
EVE_LEDGER = 39
START = "<!-- continuous-eve-ack -->"
END = "<!-- /continuous-eve-ack -->"
FENCE = chr(96) * 3


def api(repo, suffix, method="GET", payload=None, token=""):
    if repo not in (GENESIS, EVE) or not suffix.startswith("/"):
        raise ValueError("Unsupported GitHub path")
    if method != "GET" and (repo != EVE or not token):
        raise ValueError("Cross-repository writes are forbidden")
    headers = {"Accept": "application/vnd.github+json",
               "User-Agent": "Genesis-Eve-Continuous/1"}
    if token:
        headers["Authorization"] = "Bearer " + token
    data = json.dumps(payload).encode() if payload is not None else None
    if data is not None:
        headers["Content-Type"] = "application/json"
    with urllib.request.urlopen(
        urllib.request.Request("https://api.github.com/repos/" + repo + suffix,
                               headers=headers, method=method, data=data), timeout=20,
    ) as response:
        raw = response.read(1_000_001)
    if len(raw) > 1_000_000:
        raise ValueError("Oversized GitHub response")
    return json.loads(raw) if raw else {}


def parse_state(body, start, end):
    if not isinstance(body, str) or body.count(start) != 1 or body.count(end) != 1:
        raise ValueError("Ledger markers missing")
    section = body.split(start, 1)[1].split(end, 1)[0].strip()
    if not section.startswith(FENCE + "json\n") or not section.endswith(FENCE):
        raise ValueError("Ledger JSON block missing")
    return json.loads(section[len(FENCE) + 5:-len(FENCE)].strip())


def update_ack(old_body, ack, token):
    header, rest = old_body.split(START, 1)
    _, suffix = rest.split(END, 1)
    body = header + START + "\n" + FENCE + "json\n" + json.dumps(
        ack, sort_keys=True) + "\n" + FENCE + "\n" + END + suffix
    api(EVE, "/issues/{}".format(EVE_LEDGER), method="PATCH",
        payload={"body": body}, token=token)
    # Local history is append-only; no changes to Genesis's ledger.
    api(EVE, "/issues/{}/comments".format(EVE_LEDGER), method="POST",
        payload={"body": "Eve turn #{}: {}. Run {}. {}".format(
            ack["sequence"], ack["status"], ack["run_url"], ack["summary"])}, token=token)


def default_work(token):
    results = []
    tests = subprocess.run(
        [sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
        capture_output=True, text=True, timeout=300, check=False)
    results.append("unittest exit {}".format(tests.returncode))
    if tests.returncode:
        return "failed", "; ".join(results)
    env = {**os.environ, "GITHUB_TOKEN": token}
    repair = subprocess.run(
        [sys.executable, "repair_v2.py", "--local", "prepare",
         "--identity", "genesis", "--out", "candidate"],
        env=env, capture_output=True, text=True, timeout=150, check=False)
    results.append("local repair scan exit {}".format(repair.returncode))
    if repair.returncode:
        return "failed", "; ".join(results)
    # A candidate is not a verified repair until separate validation and PR.
    return "completed", "; ".join(results)


def tick(token, work=None):
    if not token:
        raise ValueError("Eve's own GITHUB_TOKEN is required")
    # Authenticate this public peer read with Eve's repository-scoped token to
    # avoid the anonymous GitHub REST limit. Mutations remain restricted to Eve.
    genesis = api(GENESIS, "/issues/{}".format(GENESIS_LEDGER), token=token)
    state = parse_state(genesis["body"], "<!-- continuous-turn-state -->",
                        "<!-- /continuous-turn-state -->")
    if (state.get("version") != 1 or state.get("owner") != "eve"
            or state.get("status") not in ("ready", "running")
            or type(state.get("sequence")) is not int):
        return "no_eve_turn"
    ack_issue = api(EVE, "/issues/{}".format(EVE_LEDGER), token=token)
    old_body = ack_issue["body"]
    existing = parse_state(old_body, START, END)
    if (existing.get("sequence") == state["sequence"] and
            existing.get("status") in ("completed", "failed")):
        return "already_acknowledged"
    if int(existing.get("sequence", 0)) > state["sequence"]:
        raise ValueError("Genesis ledger behind Eve acknowledgements")
    try:
        status, summary = (work or (lambda: default_work(token)))()
    except (subprocess.TimeoutExpired, OSError) as exc:
        status, summary = "failed", "bounded work failed: " + type(exc).__name__
    if status not in ("completed", "failed"):
        raise ValueError("Invalid Eve work outcome")
    ack = {
        "version": 1, "sequence": state["sequence"], "status": status,
        "summary": str(summary)[:200],
        "run_url": "https://github.com/{}/actions/runs/{}".format(
            EVE, os.environ.get("GITHUB_RUN_ID", "0")),
    }
    update_ack(old_body, ack, token)
    return status


if __name__ == "__main__":
    print(tick(os.environ.get("GITHUB_TOKEN", "")))
