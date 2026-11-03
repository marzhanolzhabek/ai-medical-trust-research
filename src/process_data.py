"""Task 3 measurement ingestion and reproducible bootstrap statistics."""
import csv
import json
from pathlib import Path
import numpy as np

def read_measurements(path):
    out = []
    with Path(path).open(encoding="utf-8") as file:
        for lineno, line in enumerate(file, 1):
            if line.strip():
                record = json.loads(line)
                if "status" not in record or "latency_us" not in record:
                    raise ValueError(f"Missing fields in {path}, line {lineno}")
                out.append(record)
    if not out:
        raise ValueError(f"Empty measurement log: {path}")
    return out

def percentile(values, p):
    return float(np.percentile(np.asarray(values, dtype=float), p))

def bootstrap_ci(values, seed=42, replicates=2000):
    values = np.asarray(values, dtype=float)
    if values.size == 0:
        return (float('nan'),float('nan'))
    rng = np.random.default_rng(seed)
    bootstrap = np.empty(replicates)
    for i in range(replicates):
        bootstrap[i] = np.median(rng.choice(values, size=len(values), replace=True))
    return tuple(float(x) for x in np.percentile(bootstrap,[2.5,97.5]))

def aggregate(records, *, source, warmup_runs=0, seed=42, replicates=2000):
    # Collector already excludes warm-ups: IDs begin at 1 after discard.
    # Other formats may explicitly label warmup records; remove those here.
    evaluation = [r for r in records if not r.get('warmup', False) and r.get('phase', 'evaluation') != 'warmup']
    if warmup_runs and any(r.get('phase') == 'warmup' for r in records):
        assert len(records)-len(evaluation) >= warmup_runs
    successes = [r for r in evaluation if r['status'] == 'ok' and r.get('latency_us') is not None]
    latency = np.asarray([float(r['latency_us']) for r in successes])
    per_calc = np.asarray([float(r['latency_us'])/max(1,int(r.get('calculations_per_measurement',1))) for r in successes])
    if not len(latency):
        raise ValueError('No successful observations')
    low,high = bootstrap_ci(per_calc,seed,replicates)
    return {'source':source,'load':int(successes[0].get('calculations_per_measurement',1)),
        'measurements':len(evaluation),'successful':len(successes),'errors':len(evaluation)-len(successes),
        'error_rate':round(1-len(successes)/len(evaluation),6),
        'mean_latency_us':float(np.mean(latency)),
        'median_latency_us':float(np.median(latency)),
        'p25_latency_us':percentile(latency,25),'p75_latency_us':percentile(latency,75),
        'p95_latency_us':percentile(latency,95),'p99_latency_us':percentile(latency,99),
        'median_us_per_calculation':float(np.median(per_calc)),
        'p25_us_per_calculation':percentile(per_calc,25),'p75_us_per_calculation':percentile(per_calc,75),
        'p95_us_per_calculation':percentile(per_calc,95),'p99_us_per_calculation':percentile(per_calc,99),
        'ci95_low_us_per_calculation':low,'ci95_high_us_per_calculation':high,
        'warmup_policy':'10 untimed runs before logged measurements'}

def build_summary(root, seed=42, replicates=2000):
    root=Path(root)
    paths=[root/f'data/raw/load_{n}.jsonl' for n in (1,10,25,50)]
    return [aggregate(read_measurements(path),source=str(path.relative_to(root)),warmup_runs=10,seed=seed,replicates=replicates) for path in paths]

def write_summary(rows,path):
    path=Path(path);path.parent.mkdir(parents=True,exist_ok=True)
    with path.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(rows[0]))
        writer.writeheader();writer.writerows(rows)

if __name__=='__main__':
    import argparse
    ap=argparse.ArgumentParser();ap.add_argument('--root',default='.')
    args=ap.parse_args()
    r=Path(args.root)
    data=build_summary(r)
    write_summary(data,r/'data/processed/metrics_summary.csv')
    print(json.dumps(data,indent=2))
