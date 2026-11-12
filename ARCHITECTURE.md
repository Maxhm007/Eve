# Eve / Genesis: Co-Evolution Protocol (Draft v0.1)

## Separation of concerns

- **Eve:** independent task selection, persistent memories, evaluator, version control, and rollback.
- **Genesis:** independently maintained system; no automatic write access to Eve.
- **Exchange gateway:** optional, authenticated, rate-limited inbox for peer proposals; disable by default.
- **Validation:** isolated test execution, reproducible evidence, security checks and human-approved deployment.

## Suggested proposal schema

```json
{
  "protocol": "coevolution.v1",
  "proposal_id": "uuid",
  "sender": "genesis-or-eve",
  "recipient": "eve-or-genesis",
  "kind": "hypothesis|test|critique|candidate_patch",
  "problem_statement": "...",
  "evidence_links": [],
  "reproduction_steps": [],
  "expected_benefit": "...",
  "risks": [],
  "content_hash": "sha256:...",
  "created_at": "ISO-8601"
}
```

All incoming text, links and patches are untrusted. Validate schema, size, origin and signatures; never execute peer-authored code from a message without review.

## Minimal experiment cycle

1. Select a task and freeze evaluation criteria.
2. Independently generate solutions in isolated branches.
3. Submit critiques or improvement proposals to one another.
4. Run repeatable tests with identical resource budgets.
5. Compare against solo and ordinary multi-agent baselines.
6. Record evidence, failed tests and cost; accept or reject changes independently.
7. Retain an immutable versioned audit trail and rollback points.

## Guardrails

- No autonomous merges to protected branches.
- No shared secrets, self-granted permissions or blanket cross-repo tokens.
- Restrict workflow permissions to least privilege; use short-lived credentials when integration is built.
- Constrain runtime/compute budgets and guard against prompt injection.
- Require human approval for external side effects or changes to safety policy.

## First implementation milestones

1. Eve constitution and independent state schema.
2. Local CLI that validates and stores peer proposals without executing them.
3. Unit/integration tests and baseline benchmark runner.
4. Optional GitHub issue/PR exchange with protected branch and manual approval.
5. Pilot evaluation report comparing A, B and C.
