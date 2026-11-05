# Reviewer entry — CHENGXU v0.9.7

This private package contains a local Chinese WeChat drafting tool and its measured evidence. Start with the current documents below; historical experiments are supporting material rather than the main reading order.

| Reading order | Material | Purpose |
| --- | --- | --- |
| 1 | [B — Methodology](docs/methodology.md) | Problem, assumptions, design decisions, authorship and evaluation method |
| 2 | [Architecture](docs/architecture.md) / [standalone SVG](docs/diagrams/architecture-v0.9.7.svg) | Current source-reference, inference, composition, storage and review flow |
| 3 | [C — 50-case output table](docs/verification/ai-quality-review-v0.9.7/full-50-cases.csv) | Original fixed 50 inputs and 150 final outputs in the required columns |
| 4 | [D — Evaluation](docs/evaluation-report.md) | Final results, verification scope and limits |
| 5 | [E — Defects and next steps](docs/defects-and-next-steps.md) | Actual before/after evidence, observed repairs and remaining issues |
| Supporting | [A — existing Work Log](WORK_LOG.md), [150 scores/comments](docs/verification/ai-quality-review-v0.9.7/candidate-scores.csv), [runbook](docs/running-and-evaluation.md) | Process evidence, detailed quality judgments and local execution |

**Result:** 50/50 cases meet the internal AI-applied threshold; mean 4.3097/5. This is source-reference drafting with actual local-model editing, assessed by the same AI assistant that helped implement it. It is not independent human or holdout validation. Human ratings and release acceptance remain pending; the brief does not prescribe human signoff or a pass rate.

Required screenshots are not included. All customers/products/events are fictional; credentials, private brief, weights and runtime database are excluded. The current archive is `CHENGXU-review-draft-v0.9.7-final-docs-20261105.zip`. No material has been emailed, uploaded or published. See [README](README.md) for the wider project guide.
