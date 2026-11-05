"""Summarise time measurements; remove warm-ups; compute seeded bootstrap CIs."""
import csv, json, random, statistics
from collections import defaultdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def percentile(values,percent):
    xs=sorted(values)
    if not xs: raise ValueError('no values')
    if len(xs)==1: return xs[0]
    index=(len(xs)-1)*percent/100
    lo=int(index);hi=min(lo+1,len(xs)-1)
    return xs[lo]+(xs[hi]-xs[lo])*(index-lo)

def bootstrap_median_ci(values,seed=42,reps=2000):
    rng=random.Random(seed);n=len(values)
    if not n:return (None,None)
    medians=sorted(statistics.median(rng.choices(values,k=n)) for _ in range(reps))
    return percentile(medians,2.5),percentile(medians,97.5)

def read_logs(path=None):
    source=Path(path) if path else ROOT/'data/raw/test_run.jsonl'
    with source.open(encoding='utf-8') as f:
        entries=[json.loads(line) for line in f if line.strip()]
    return entries

def aggregate(entries):
    partitions=defaultdict(list)
    for e in entries:
        if e['phase'] not in ('warmup','benchmark'):
            raise ValueError('unknown phase')
        partitions[(e['method'],int(e['load_records']))].append(e)
    summary=[]
    for (method,load), group in sorted(partitions.items(),key=lambda pair:(pair[0][1],pair[0][0])):
        evals=[e for e in group if e['phase']=='benchmark']
        warmups=sum(e['phase']=='warmup' for e in group)
        successful=[float(e['latency_ms']) for e in evals if e['success']]
        if not successful:raise ValueError('no successful measured runs')
        lower,upper=bootstrap_median_ci(successful)
        summary.append({'method':method,'load_records':load,'warmup_runs_excluded':warmups,
                        'benchmark_runs':len(evals),'successful_runs':len(successful),
                        'error_rate':round(1-len(successful)/len(evals),5),
                        'median_ms':round(statistics.median(successful),6),
                        'p25_ms':round(percentile(successful,25),6),
                        'p75_ms':round(percentile(successful,75),6),
                        'p95_ms':round(percentile(successful,95),6),
                        'p99_ms':round(percentile(successful,99),6),
                        'ci95_low_ms':round(lower,6),'ci95_high_ms':round(upper,6)})
    return summary

def save_summary(summary,path=None):
    dest=Path(path) if path else ROOT/'data/processed/metrics_summary.csv'
    dest.parent.mkdir(parents=True,exist_ok=True)
    with dest.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(summary[0]));writer.writeheader();writer.writerows(summary)
    return dest

if __name__=='__main__':
    data=aggregate(read_logs());print(save_summary(data));
    for row in data:print(row)
