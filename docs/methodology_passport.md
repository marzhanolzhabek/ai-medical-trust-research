# Methodology Passport Card — Revised

**Title:** Trust in AI-Generated Medical Recommendations Among Patients: A Comparison of Three Age Groups  
**Authors:** Sharipkhan Merey; Olzhabek Marzhan  
**Repository:** https://github.com/marzhanolzhabek/ai-medical-trust-research

## 1. Research type
Quantitative, observational, cross-sectional survey (planned). **Only patients** aged 18+ are included. Age cohorts: **18–30**, **31–50**, **51+**. No random assignment; no causal claims.

## 2. Research questions and hypotheses
**RQ1:** Does mean self-reported trust in AI-generated medical recommendations differ among patient age groups 18–30, 31–50, and 51+?  
**H0₁:** μ18–30 = μ31–50 = μ51+.  
**H1₁:** At least one patient age group's mean trust differs.

**RQ2:** Among patients, are AI knowledge, perceived recommendation accuracy, explanation clarity, and perceived doctor supervision associated with trust, after accounting for age group and other available covariates?  
**H0₂:** All four adjusted association coefficients are zero.  
**H1₂:** At least one adjusted coefficient differs from zero.

**RQ3:** Is previous use of AI tools associated with higher trust among patients, after accounting for age group?  
**H0₃:** Prior AI use is not associated with trust after age-group adjustment.  
**H1₃:** Prior AI use is positively associated with trust after age-group adjustment.

## 3. Variables and operational definitions
| Role | Variables |
|---|---|
| Main independent | Patient age group: 18–30, 31–50, 51+ (based on self-reported age) |
| Dependent | Trust score: 1 (very low) to 5 (very high) |
| Secondary independent | Prior AI use (yes/no); AI knowledge, perceived accuracy, explanation clarity, doctor supervision (each 1–5) |
| Planned covariates | Education, healthcare experience, digital literacy and medical-app experience; collect only as ethically approved |
| Fixed protocol | Same questionnaire and trust anchors for all three groups |

## 4. Metrics
**Primary:** Mean trust score (1–5) by age group, group differences, and uncertainty intervals.  
**Secondary:** Median and SD of trust by group; associations of trust with prior AI use and perception ratings.  
**Guardrails:** Valid completion rate ≥90%; invalid/duplicate record rate ≤10%; no personally identifiable or diagnostic data in public files.

## 5. Planned hypothesis testing
With real responses: descriptive group summaries, 95% confidence intervals, omnibus comparison across three groups (ANOVA if assumptions fit, otherwise Kruskal–Wallis), multiplicity-aware post-hoc comparisons, and adjusted ordinal/linear models as appropriate. Target **at least 30 valid responses per group** as a planning minimum, not a statistical power guarantee.

## 6. Reproducible demonstration and ethics
The included **45 simulated records (15 per age group)** demonstrate code and plots only. **They are not collected from real patients**; no hypothesis is supported or rejected using this synthetic dataset. Obtain voluntary informed consent for a real survey, minimize sensitive details, anonymize responses, and seek institutional ethics approval when required.
