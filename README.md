# Trust in AI-Generated Medical Recommendations — TASK 3

**Authors:** Sharipkhan Merey; Olzhabek Marzhan

**Research track:** Software Engineering (survey processing pipeline)

## Scope and provenance
This project **extends the original Task 2 repository**. Its only available input is `data/sample/sample_synthetic.csv` (10 synthetic demonstration responses, 5 students and 5 patients). These are **not real survey responses**. No real Week 7–8 latency logs, warm-up runs, or clinical outcome measurements were provided. Therefore no warm-up filtering or latency-versus-load claim is made.

## Results & Discussion (synthetic demonstration only)

| Group | n | Mean ± SD (Likert 1–5) | Median (p25–p75) | p95 | p99 | Bootstrap 95% CI for mean |
|---|---:|---:|---:|---:|---:|---|
| Patient | 5 | 2.80 ± 0.84 | 3.00 (2.00–3.00) | 3.80 | 3.96 | [2.20, 3.41] |
| Student | 5 | 3.60 ± 1.14 | 4.00 (3.00–4.00) | 4.80 | 4.96 | [2.60, 4.40] |

**Primary metric:** Student − patient mean trust = 0.80 Likert points (synthetic only).

**Guardrail:** invalid response rate = 0/10 = 0%; valid completion rate = 10/10 = 100%. These reflect only this synthetic file, not real survey quality.

![Mean trust and bootstrap CI](reports/figures/fig1_mean_trust_ci.png)

![Trust-score distribution](reports/figures/fig2_trust_distribution.png)

Both figures are also exported as vector PDF at the same paths with `.pdf` extensions. The boxplot shows distribution, while uncertainty is explicitly shown in Figure 1.

## Domain model
See [C4-style survey processing diagram](docs/domain_model.md).

## Reproducibility
Install dependencies with `pip install -r requirements.txt`, then open `notebooks/01_data_analysis.ipynb` and run all cells. The notebook has saved executed outputs. Random seed is fixed at 42.

Original Task 2 benchmark remains available: `python src/benchmark.py --config configs/config.json` and `python -m unittest discover -s src -p "test_*.py"`.

## Ethics and limitations
No real respondents were collected for this artifact. Do not report synthetic numbers as research findings or claim hypotheses were confirmed. Obtain consent, anonymize data, and collect a sufficient real sample before population inference.

## Repository structure
`data/sample/`, `data/processed/`, `docs/`, `notebooks/`, `reports/figures/`, `src/`, `configs/`, `results/`, and the original Task 2 files.
