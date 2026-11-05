# C4 Component Diagram — Synthetic Patient-Age Survey Processing

```mermaid
flowchart LR
  A[(Synthetic patient CSV: 45 rows)] --> V[Survey validation and age-group assignment]
  V --> S[Survey descriptive analysis]
  S --> M1((Metric M1: trust 1–5, mean, median, CI))
  M1 --> R[Research notebook and report]
  A --> W[Repetition for controlled load testing: 45/90/180/360]
  W --> B[Baseline: 3 scans]
  W --> P[Proposed: 1 scan]
  B --> C[Timed execution collector]
  P --> C
  C --> J[(JSONL: warmup and measured runs)]
  J --> F[Warm-up filter and statistical aggregation]
  F --> M2((Metric M2: median/p95/p99 latency ms, 95% CI, error rate))
  M2 --> R
  R --> G[Four PDF and PNG scientific plots]
```

**System boundary:** offline Python data processing on a synthetic demonstration file. M1 is the *research opinion score*, while M2 is *software processing speed and reliability*. Only M2 uses simulated workload scaling, with repeated input rows; no additional human participant data and no AI model inference are included. The diagram is a C4-inspired component-level depiction with explicit collection nodes.
