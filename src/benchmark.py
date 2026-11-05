"""Pilot: validate synthetic survey responses and summarize trust by patient age."""
import argparse
import csv
import json
import time
from pathlib import Path
from statistics import mean

REQUIRED = {"response_id", "age", "trust_score", "prior_ai_use", "ai_knowledge", "perceived_accuracy", "explanation_clarity", "doctor_supervision"}

def age_group(age):
    if 18 <= age <= 30: return "18-30"
    if 31 <= age <= 50: return "31-50"
    if age >= 51: return "51+"
    raise ValueError("Age must be >= 18")

def run(config_path):
    cfg_file = Path(config_path).resolve()
    root = cfg_file.parent.parent
    cfg = json.loads(cfg_file.read_text(encoding="utf-8"))
    source = root / cfg["input_path"]
    destination = root / cfg["output_path"]
    start = time.perf_counter()
    with source.open(encoding="utf-8", newline="") as f:
        reader = csv.DictReader(f)
        if not REQUIRED.issubset(set(reader.fieldnames or [])):
            raise ValueError("Missing required CSV columns")
        rows = list(reader)
    groups = {"18-30": [], "31-50": [], "51+": []}
    seen = set()
    invalid = 0
    for row in rows:
        try:
            ident = row["response_id"].strip()
            age = int(row["age"])
            trust = int(row["trust_score"])
            if not ident or ident in seen or not cfg["trust_score_min"] <= trust <= cfg["trust_score_max"]:
                raise ValueError("Invalid ID or trust score")
            for col in ("ai_knowledge", "perceived_accuracy", "explanation_clarity", "doctor_supervision"):
                if not 1 <= int(row[col]) <= 5: raise ValueError("Invalid rating")
            if row["prior_ai_use"].strip().lower() not in {"yes", "no"}: raise ValueError("Invalid prior use")
            group = age_group(age)
            seen.add(ident)
            groups[group].append(trust)
        except (ValueError, TypeError, KeyError):
            invalid += 1
    total = len(rows)
    valid = total - invalid
    result = {
        "study": "Trust in AI-generated medical recommendations among patients",
        "dataset_type": "synthetic demonstration" if cfg["synthetic_data"] else "survey",
        "total_rows": total, "valid_rows": valid, "invalid_rows": invalid,
        "completion_rate": round(valid / total, 4) if total else 0,
        "invalid_rate": round(invalid / total, 4) if total else 0,
        "age_groups": {k: {"n": len(v), "mean_trust": round(mean(v), 3) if v else None} for k,v in groups.items()},
        "runtime_ms": round((time.perf_counter()-start)*1000, 4),
    }
    result["guardrails_passed"] = (result["completion_rate"] >= cfg["min_completion_rate"] and result["invalid_rate"] <= cfg["max_invalid_rate"])
    destination.parent.mkdir(parents=True, exist_ok=True)
    destination.write_text(json.dumps(result,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,indent=2))
    return result

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config",default="configs/config.json")
    args = parser.parse_args()
    run(args.config)
