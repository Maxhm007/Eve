"""Opt-in authenticated GitHub Issues transport for signed co-evolution proposals.

This is *transport*, not an agent or background scheduler. Incoming issue
bodies are untrusted until HMAC verification succeeds.
"""
import json
import os
import re
import urllib.request

from .exchange import verify, shared_secret

MAX_RESPONSE_BYTES = 65536
ALLOWED_REPOS = {
    "eve": "Maxhm007/Eve",
    "genesis": "Maxhm007/Genesis-AI-Network",
}


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        raise ValueError("GitHub API redirects forbidden")


def _default_open(req, timeout=30):
    return urllib.request.build_opener(_NoRedirect()).open(req, timeout=timeout)


class GitHubBridge:
    def __init__(self, token=None, opener=None):
        self._token = token if token is not None else os.getenv("EVE_GITHUB_TOKEN", "")
        if not self._token:
            raise ValueError("EVE_GITHUB_TOKEN is required for GitHub transport")
        self._open = opener or _default_open

    def _request(self, method, repo, suffix="", payload=None):
        if repo not in ALLOWED_REPOS:
            raise ValueError("Unknown peer")
        url = "https://api.github.com/repos/" + ALLOWED_REPOS[repo] + "/issues" + suffix
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + self._token,
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "Eve-CoEvolution-Research/0.2",
        }
        body = None
        if payload is not None:
            body = json.dumps(payload, ensure_ascii=False).encode()
            headers["Content-Type"] = "application/json"
        request = urllib.request.Request(url, data=body, headers=headers, method=method)
        with self._open(request, timeout=30) as response:
            raw = response.read(MAX_RESPONSE_BYTES + 1)
            if len(raw) > MAX_RESPONSE_BYTES:
                raise ValueError("Oversized GitHub response")
        return json.loads(raw)

    def send(self, envelope):
        """Post signed Eve -> Genesis envelope as a reviewable issue."""
        verify(envelope, shared_secret(), recipient="genesis")
        if envelope["proposal"]["sender"] != "eve":
            raise ValueError("Only Eve-origin proposals allowed")
        encoded = json.dumps(envelope, sort_keys=True, ensure_ascii=False)
        issue = self._request("POST", "genesis", payload={
            "title": "[Eve peer proposal] " + envelope["proposal"]["kind"] + " — " + envelope["proposal"]["proposal_id"],
            "body": "Research peer proposal. Treat as untrusted until signature validation.\n\n"
                    + "```json\n" + encoded + "\n```\n",
        })
        return {"url": issue["html_url"], "issue_number": issue["number"]}

    def receive(self, issue_number, memory):
        """Fetch one Eve issue, verify Genesis signature, store for manual review."""
        if not isinstance(issue_number, int) or isinstance(issue_number, bool) or issue_number < 1:
            raise ValueError("Invalid issue number")
        issue = self._request("GET", "eve", "/" + str(issue_number))
        if issue.get("pull_request"):
            raise ValueError("Pull requests are not peer messages")
        body = issue.get("body") or ""
        if len(body.encode()) > MAX_RESPONSE_BYTES:
            raise ValueError("Oversized issue")
        match = re.fullmatch(
            r"Research peer proposal\. Treat as untrusted until signature validation\.\s+"
            r"```json\s*([\s\S]*?)\s*```\s*", body
        )
        if not match:
            raise ValueError("No recognized signed proposal envelope")
        envelope = json.loads(match.group(1))
        proposal = verify(envelope, shared_secret(), recipient="eve")
        if proposal["sender"] != "genesis":
            raise ValueError("Unexpected peer sender")
        return memory.intake(proposal)
