# Eve v0.2: configure reasoning and peer transport

## 1. Local AI model — no GPU required

Install Ollama from its official website on the computer where Eve will run. Then install a modest model:

```sh
ollama pull qwen2.5:3b
```

Ensure Ollama is running. Eve now defaults to:

- `EVE_MODEL_ENDPOINT=http://127.0.0.1:11434/v1/chat/completions`
- `EVE_MODEL_NAME=qwen2.5:3b`

Test explicitly:

```sh
python -m eve ask "Propose a measurable experiment for Genesis–Eve co-evolution"
```

Model download and local inference are **not** performed by GitHub or ChatGPT. CPU-only inference may be slow. To use a trusted hosted OpenAI-compatible endpoint, override `EVE_MODEL_ENDPOINT`, `EVE_MODEL_NAME`, and `EVE_MODEL_API_KEY` locally. Eve rejects redirects to protect credentials.

## 2. GitHub transport (explicit manual operations only)

Obtain separate, narrowly scoped GitHub tokens with Issues write access to the other repository and read access to the own inbox. Use `EVE_GITHUB_TOKEN` on Eve and `GENESIS_EVE_GITHUB_TOKEN` on Genesis. Provision the **same securely generated random secret** (minimum 32 characters) as `EVE_PEER_SHARED_SECRET` and `GENESIS_EVE_SHARED_SECRET` in their respective runtimes. Never commit or paste tokens or secrets into issues.

Eve -> Genesis:

```sh
python -m eve propose hypothesis "Compare two independent solutions" "Reduce errors" > proposal.json
python -m eve sign proposal.json > signed.json
python -m eve github-send signed.json
```

Genesis -> Eve:

```sh
python scripts/eve_peer_bridge.py prepare critique "Check experimental controls" "Better evidence" > proposal.json
python scripts/eve_peer_bridge.py send proposal.json
```

To receive: `python -m eve github-receive ISSUE_NUMBER` on Eve, or `python scripts/eve_peer_bridge.py receive ISSUE_NUMBER` on Genesis.

Signed messages are held as untrusted proposals until reviewed. These are opt-in commands, not continuously operating AI agents.

## 3. Current integration boundary

- Shared proposal format and verification: implemented and unit-tested in both repos.
- GitHub Issues transport: implemented and unit-tested using mocked HTTP.
- GitHub cross-repository access: verified using **manual connector-created test issues**, not signed agent delivery.
- No real model server has been provisioned.
- No GitHub tokens or shared signing secret have been configured by ChatGPT.
- No unattended peer cycle, self-modification, or auto-merge has been enabled.
