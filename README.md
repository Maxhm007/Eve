# Eve — Independent AI Recovery Partner

> **Eve is an independent recovery partner for [Genesis](https://github.com/Maxhm007/Genesis-AI-Network). Eve monitors Genesis's failing workflows, retries transient failures once, and escalates persistent defects with evidence. Genesis performs the same service for Eve.**

**Status:** Mutual healing watchdog and schedule are implemented with unit tests. Live cross-repository recovery requires a target-scoped GitHub token and explicit enablement. Automated code patches and recovery success have not yet been verified.

## Purpose

Keep Genesis and Eve resilient through independent health checks, bounded workflow recovery and evidence-backed repair processes, without requiring conversations between agents.

Eve is a **female-named conceptual counterpart**, not a biologically female entity and not a claim of consciousness.

## Principles

1. **Independence:** Separate repository, memory, development history, tasks, evaluations and governance.
2. **Equality:** Genesis cannot command Eve; Eve cannot command Genesis. Either may reject a proposal.
3. **Variation:** Eve should develop distinct hypotheses and tests rather than mirror Genesis.
4. **Evidence:** No claimed improvement without reproducible measurements and review.
5. **Bounded evolution:** Changes are proposed on branches, tested in a sandbox, and approved through independent validation before promotion.
6. **Safety:** No unreviewed self-modification, privileged cross-repo writes, credential exchange, unbounded spending or irreversible actions.
7. **Research honesty:** Open-ended co-evolution is a hypothesis to measure, not an established fact.

## Legacy research architecture (not the active workflow)

```text
Genesis (independent)         Eve (independent)
  memory / models               memory / models
  research / tests              research / tests
           |                         |
           +---- proposal exchange --+
                      |
             common test protocol
                      |
           independent verification
                      |
       accept / reject / revise locally
```

The exchange layer transfers signed or attributable **proposals and evidence**, not executable commands or unrestricted repository permissions.

## Previous research experiment (no longer scheduled)

Compare three matched conditions over identical tasks and budgets:
- A: one isolated agent;
- B: two agents cooperating without persistent independent evolution;
- C: Genesis and Eve with separate memory, independently generated hypotheses, peer critiques, and versioned improvements.

Record task success, reproducibility, novel verified improvements, error rate, compute cost, and regression frequency. Avoid claiming co-evolution unless C shows repeatable gains against A and B.

## Original roadmap (superseded by mutual healing)

- [ ] Define Eve's constitution, safety rules and explicit permissions
- [ ] Build independent memory, task queue, and experiment logging
- [ ] Implement a schema-validated proposal exchange with Genesis
- [ ] Add unit tests, benchmark suite and independent validation
- [ ] Run a manually triggered, non-destructive end-to-end pilot
- [ ] Review evidence before enabling any scheduled operation

See [ARCHITECTURE.md](ARCHITECTURE.md).

## Relationship to Genesis

Genesis is an inspiration and possible peer, not Eve's owner or runtime dependency. The two may share long-range research interests (including scientifically grounded longevity and human wellbeing), but each maintains independently tested priorities and hypotheses.

Licensed and third-party Genesis components must be reviewed before any copying. At this stage no Genesis code has been copied.

## Active mutual healing

See [MUTUAL_HEALING.md](MUTUAL_HEALING.md). Eve monitors Genesis; Genesis monitors Eve. The old research conversation schedules are removed. Recovery is initially limited to one native rerun of failed jobs and evidence-backed repair tickets; no automatic patch merge is authorized.
