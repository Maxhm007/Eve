# Eve v0.1 local prototype

Python 3.11+; no third-party packages and no network access required.

```bash
python -m unittest discover -s tests -v
python -m eve remember hypothesis "Could independent critiques improve test quality?"
python -m eve memories
python -m eve propose hypothesis "Test new benchmark" "More reliable results"
```

To accept an incoming message, save a **valid Genesis-addressed-to-Eve** coevolution.v1 JSON proposal as `proposal.json` and run:

```bash
python -m eve intake proposal.json
```

Incoming messages are stored as **untrusted_pending_review**. Eve does not execute code, fetch evidence URLs, make autonomous decisions or transmit proposals to Genesis. The CLI's `propose` output is only a locally generated JSON document—not delivery. The hash detects accidental modification; **it does not authenticate the sender**. Add authenticated transport before cross-repository exchange. Local JSON storage is intended for a single process only; concurrent writers need locking or a database.
