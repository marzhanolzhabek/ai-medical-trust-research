# Domain model — survey pipeline (Software Engineering / C4-style)

```mermaid
flowchart LR
 A[Anonymous synthetic survey CSV] --> B[Input validation and deduplication]
 B --> C[Group aggregation: student / patient]
 C --> D[Bootstrap 95% confidence intervals]
 D --> E[Scientific figures and metrics summary]
 B --> F[Guardrail collection: invalid response rate]
 C --> G[Metric collection: trust score 1–5]
```

**Measurement points:** B measures invalid and duplicate rows; C measures group mean, median, p95 and p99; D measures bootstrap 95% CI. The Task 2 dataset is a synthetic pipeline test, not a clinical or population study.
