"""Reproducible pilot survey data quality and descriptive metrics (stdlib only)."""
import argparse
import csv
import json
from pathlib import Path
import statistics
from statistics import mean

REQUIRED = {"response_id", "participant_group", "trust_score", "prior_ai_use",
            "ai_knowledge", "perceived_accuracy", "explanation_clarity",
            "doctor_supervision", "age", "education"}


def calculate_trust(rows, cfg):
    """Pure, in-memory survey calculation; no logging, printing or disk I/O."""
    groups = {"student": [], "patient": []}
    seen = set()
    invalid = 0
    for row in rows:
        try:
            ident = row["response_id"].strip()
            group = row["participant_group"].strip().lower()
            score = int(row["trust_score"])
            if not ident or ident in seen or group not in groups:
                raise ValueError("invalid identifier/group")
            if not cfg["trust_score_min"] <= score <= cfg["trust_score_max"]:
                raise ValueError("invalid trust score")
            seen.add(ident)
            groups[group].append(score)
        except (KeyError, TypeError, ValueError, AttributeError):
            invalid += 1
    valid = sum(len(v) for v in groups.values())
    n = len(rows)
    means = {k: statistics.mean(v) if v else None for k, v in groups.items()}
    difference = means["student"] - means["patient"] if all(v is not None for v in means.values()) else None
    completion_rate = valid / n if n else 0.0
    invalid_rate = invalid / n if n else 0.0
    return {
        "total_rows": n,
        "valid_rows": valid,
        "invalid_rows": invalid,
        "completion_rate": round(completion_rate, 4),
        "invalid_response_rate": round(invalid_rate, 4),
        "groups": {k: {"n": len(v), "mean_trust_score": round(means[k], 3) if means[k] is not None else None} for k, v in groups.items()},
        "student_minus_patient_mean_trust": round(difference, 3) if difference is not None else None,
        "guardrails": {
            "completion_rate_pass": completion_rate >= cfg["minimum_completion_rate"],
            "invalid_response_rate_pass": invalid_rate <= cfg["maximum_invalid_response_rate"],
        },
    }


def run(config_file):
    config_path = Path(config_file).resolve()
    base = config_path.parent.parent
    cfg = json.loads(config_path.read_text(encoding="utf-8"))
    source = base / cfg["input_path"]
    dest = base / cfg["output_path"]
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        if not REQUIRED.issubset(set(reader.fieldnames or [])):
            raise ValueError("Missing required CSV headers: " + ", ".join(sorted(REQUIRED - set(reader.fieldnames or []))))
        records = list(reader)
    if not records:
        raise ValueError("Input CSV has no rows")
    groups = {"student": [], "patient": []}
    invalid = 0
    seen = set()
    for row in records:
        try:
            ident = row["response_id"].strip()
            group = row["participant_group"].strip().lower()
            rating = int(row["trust_score"])
            if not ident or ident in seen or group not in groups or not cfg["trust_score_min"] <= rating <= cfg["trust_score_max"]:
                raise ValueError("invalid row")
            seen.add(ident)
            groups[group].append(rating)
        except (ValueError, TypeError):
            invalid += 1
    valid = sum(map(len, groups.values()))
    completion = valid / len(records)
    invalid_rate = invalid / len(records)
    summaries = {group: {"n": len(scores), "mean_trust_score": round(mean(scores), 3) if scores else None}
                 for group, scores in groups.items()}
    student, patient = summaries["student"], summaries["patient"]
    gap = round(student["mean_trust_score"] - patient["mean_trust_score"], 3) if student["n"] and patient["n"] else None
    eligible = min(student["n"], patient["n"]) >= cfg["minimum_group_size_for_inference"]
    result = {
        "dataset": str(cfg["input_path"]), "scenario": cfg["scenario"],
        "synthetic_sample": "synthetic" in source.name.lower(),
        "total_rows": len(records), "valid_rows": valid, "invalid_rows": invalid,
        "completion_rate": round(completion, 4), "invalid_response_rate": round(invalid_rate, 4),
        "groups": summaries, "student_minus_patient_mean_trust": gap,
        "guardrails": {"completion_rate_pass": completion >= cfg["minimum_completion_rate"],
                       "invalid_response_rate_pass": invalid_rate <= cfg["maximum_invalid_response_rate"]},
        "inference_status": "not_performed_smoke_test" if cfg["scenario"] == "smoke_test_only" else (
            "sample_sufficient_for_later_statistical_analysis" if eligible else "insufficient_group_size"),
        "notes": "Descriptive pipeline only. No hypothesis confirmation or population inference."
    }
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(result, indent=2), encoding="utf-8")
    print(json.dumps(result, indent=2))
    return result


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="AI medical advice trust survey benchmark")
    parser.add_argument("--config", default="configs/config.json")
    args = parser.parse_args()
    run(args.config)
