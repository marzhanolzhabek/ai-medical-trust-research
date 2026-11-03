"""Week 7: reproducible measurement harness for the Task 2 trust benchmark.

Only in-memory survey parsing and calculation is timed. File I/O, timestamps,
JSONL serialization, and summary calculations occur outside timed sections.
"""
import argparse
import csv
import json
import math
import os
import platform
import statistics
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

from benchmark import REQUIRED, calculate_trust


def load_config(path):
    # JSON is a valid YAML 1.2 subset. This file deliberately uses JSON syntax
    # under a .yaml name to avoid introducing unpinned parser dependencies.
    cfg_path = Path(path).resolve()
    cfg = json.loads(cfg_path.read_text(encoding="utf-8"))
    return cfg_path.parent.parent, cfg


def load_rows(path):
    with path.open(newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        missing = REQUIRED - set(reader.fieldnames or [])
        if missing:
            raise ValueError(f"Missing CSV headers: {sorted(missing)}")
        return list(reader)



def percentile(data, percent):
    """Linear-interpolation percentile, with rank (n-1)*p/100."""
    if not data:
        return None
    s = sorted(data)
    pos = (len(s) - 1) * percent / 100
    low = math.floor(pos)
    high = math.ceil(pos)
    return s[low] + (s[high] - s[low]) * (pos - low)


def environment_info():
    return {
        "cpu_model": platform.processor() or platform.machine() or "unknown",
        "cpu_count": os.cpu_count(),
        "ram_bytes": _ram_bytes(),
        "os": platform.platform(),
        "python_version": platform.python_version(),
        "platform": sys.platform,
    }


def _ram_bytes():
    try:
        if sys.platform == "linux":
            for line in Path("/proc/meminfo").read_text().splitlines():
                if line.startswith("MemTotal:"):
                    return int(line.split()[1]) * 1024
        if sys.platform == "darwin":
            import subprocess
            return int(subprocess.check_output(["sysctl", "-n", "hw.memsize"], text=True).strip())
    except (OSError, ValueError, IndexError):
        pass
    return None


def collect(config_file="configs/config.yaml"):
    root, cfg = load_config(config_file)
    settings = cfg["workload"]
    warmup = int(settings["warmup_runs"])
    runs = int(settings["measurement_runs"])
    repeats = int(settings["calculations_per_measurement"])
    if warmup < 0 or runs < 100 or repeats < 1:
        raise ValueError("Require warmup>=0, measurement_runs>=100, calculations_per_measurement>=1")
    rows = load_rows(root / cfg["input_path"])  # I/O occurs before the clock
    if not rows:
        raise ValueError("Input CSV has no rows")

    def target():
        result = None
        for _ in range(repeats):
            result = calculate_trust(rows, cfg)
        return result

    for _ in range(warmup):
        target()  # Discard warm-up timings entirely

    samples = []
    timings = []
    last_result = None
    for i in range(runs):
        started_at = datetime.now(timezone.utc).isoformat(timespec="microseconds")
        start_ns = time.perf_counter_ns()
        try:
            last_result = target()
            duration_ns = time.perf_counter_ns() - start_ns
            status = "ok"
            error = None
        except Exception as exc:  # record failures, do not silently drop them
            duration_ns = time.perf_counter_ns() - start_ns
            status = "error"
            error = f"{type(exc).__name__}: {exc}"
        duration_us = duration_ns / 1000
        record = {
            "measurement_id": i + 1,
            "timestamp_utc": started_at,
            "status": status,
            "latency_us": round(duration_us, 3),
            "calculations_per_measurement": repeats,
            "error": error,
        }
        samples.append(record)  # No console or disk I/O while timed
        if status == "ok":
            timings.append(duration_us)

    log_path = root / cfg["output_jsonl_path"]
    log_path.parent.mkdir(parents=True, exist_ok=True)
    with log_path.open("w", encoding="utf-8") as fh:
        for sample in samples:
            fh.write(json.dumps(sample, ensure_ascii=False) + "\n")

    summary = {
        "scenario": cfg["scenario"],
        "synthetic_sample": True,
        "purpose": "Pipeline performance smoke test, NOT evidence about real patients/students",
        "warmup_runs_excluded": warmup,
        "measured_runs": runs,
        "successes": len(timings),
        "errors": runs - len(timings),
        "environment": environment_info(),
        "latency_us": {
            "mean": round(statistics.mean(timings), 3) if timings else None,
            "median": round(statistics.median(timings), 3) if timings else None,
            "p95": round(percentile(timings, 95), 3) if timings else None,
            "p99": round(percentile(timings, 99), 3) if timings else None,
            "min": round(min(timings), 3) if timings else None,
            "max": round(max(timings), 3) if timings else None,
        },
        "last_descriptive_result": last_result,
        "log_path": cfg["output_jsonl_path"],
        "caveats": "Measured latency includes only the in-memory target; startup, CSV I/O, JSONL I/O excluded. This does not benchmark an AI medical model.",
    }
    summary_path = root / cfg["summary_output_path"]
    summary_path.parent.mkdir(parents=True, exist_ok=True)
    summary_path.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    print(json.dumps(summary, indent=2))
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--config", default="configs/config.yaml")
    args = ap.parse_args()
    collect(args.config)
