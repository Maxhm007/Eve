# Eve reasoning + authenticated exchange (opt-in)

## Reasoning

Use Python 3.11+ and an **OpenAI-compatible** chat-completions model server. No provider or paid service is required by this repository, and no model is bundled.

Environment variables:

- `EVE_MODEL_ENDPOINT`: exact `https://host/v1/chat/completions` or loopback `http://127.0.0.1:port/v1/chat/completions`
- `EVE_MODEL_NAME`: name supported by your model endpoint
- `EVE_MODEL_API_KEY`: API key, optional for localhost (never commit it)

Example local invocation:

```bash
export EVE_MODEL_ENDPOINT=http://127.0.0.1:11434/v1/chat/completions
export EVE_MODEL_NAME=your-installed-local-model
python -m eve ask "Propose a testable hypothesis about co-evolution"
```

This executes one request on demand; it does not autonomously develop Eve or schedule work. API endpoint must be trusted: model prompts are transmitted to that endpoint.

## Authenticated file exchange

Create an independently generated random `EVE_PEER_SHARED_SECRET` (>=32 characters) and configure it securely in BOTH independently controlled environments. Never commit or print the secret. **A shared key allows either holder to impersonate the other**, so this is a first-stage demo of message authentication, not asymmetric identities.

```bash
# Eve creates signed outgoing JSON (no delivery)
python -m eve sign proposal.json > signed.json

# Eve receives an authenticated Genesis -> Eve signed envelope
python -m eve receive genesis-message.json
```

The receiver checks the HMAC signature, expiry, protocol, recipient and content integrity, then records a pending-review item. It never executes code or approves an incoming proposal. Duplication is blocked locally.

**No live Genesis integration, GitHub transport, autonomous messaging, or permissions have been enabled.** Next: asymmetrically signed agent identities, authenticated transport (e.g. restricted GitHub issue inbox), replay-safe durable state, and end-to-end pilot.
