"""Controlled processing benchmark: identical results via two implementation strategies.

Workloads repeat the SAME 45 synthetic rows with unique technical IDs solely for
processing-load tests; these are NOT new patient responses. Timings exclude disk I/O,
bootstrap confidence intervals, and any medical-AI inference.
"""
import csv
import json
import time
from pathlib import Path
from statistics import mean

COHORTS = ('18-30', '31-50', '51+')
ROOT = Path(__file__).resolve().parents[1]

def load_rows(path=None):
    source = Path(path) if path is not None else ROOT / 'data/sample/sample_synthetic.csv'
    with source.open(newline='', encoding='utf-8') as f:
        return list(csv.DictReader(f))

def repeat_workload(rows, factor):
    if factor < 1: raise ValueError('factor must be >= 1')
    return [dict(row, response_id=f"{row['response_id']}_repeat{rep}")
            for rep in range(factor) for row in rows]

def _validated_group(row):
    age = int(row['age']); rating = int(row['trust_score'])
    if not (1 <= rating <= 5 and age >= 18):
        raise ValueError('invalid age/trust score')
    group = '18-30' if age <= 30 else ('31-50' if age <= 50 else '51+')
    if row['age_group'] != group: raise ValueError('age group mismatch')
    return group, rating

def baseline(rows):
    """Three independent full-data scans (one per cohort)."""
    result = {}
    for group in COHORTS:
        scores = []
        for row in rows:
            g, rating = _validated_group(row)
            if g == group: scores.append(rating)
        result[group] = {'n':len(scores), 'mean_trust':mean(scores) if scores else None}
    return result

def proposed(rows):
    """One validation/aggregation scan (same outputs, fewer redundant checks)."""
    counts={g:0 for g in COHORTS}; sums={g:0 for g in COHORTS}
    for row in rows:
        group,rating=_validated_group(row)
        counts[group]+=1; sums[group]+=rating
    return {g:{'n':counts[g], 'mean_trust':sums[g]/counts[g] if counts[g] else None}
            for g in COHORTS}

def collect(path=None, load_factors=(1,2,4,8), warmups=10, runs=80):
    source_rows=load_rows()
    dest=Path(path) if path else ROOT/'data/raw/test_run.jsonl'
    dest.parent.mkdir(parents=True,exist_ok=True)
    count=0
    with dest.open('w',encoding='utf-8') as f:
        for factor in load_factors:
            rows=repeat_workload(source_rows,factor)
            assert baseline(rows) == proposed(rows), 'Methods disagree'
            for name,fn in [('baseline',baseline),('proposed',proposed)]:
                for index in range(warmups+runs):
                    start=time.perf_counter_ns()
                    success=True; error=''
                    try:
                        value=fn(rows)
                        if value != baseline_reference(rows):
                            raise AssertionError('Output differed from reference')
                    except Exception as exc:
                        success=False;error=repr(exc)
                    duration=(time.perf_counter_ns()-start)/1e6
                    entry={'method':name,'load_records':len(rows),'repeated_synthetic_rows':factor,
                           'phase':'warmup' if index<warmups else 'benchmark',
                           'iteration':index,'latency_ms':round(duration,6),
                           'success':success,'error':error,'dataset':'synthetic_repeated_for_load',
                           'timing_scope':'in_memory_validation_and_aggregation'}
                    f.write(json.dumps(entry)+'\n');count+=1
    print(f'Wrote {count} timestamp-free measured execution records to {dest}')
    return dest

def baseline_reference(rows):
    """Reference computation independent from both benchmark implementations."""
    counts={g:[] for g in COHORTS}
    for row in rows:
        group,score=_validated_group(row)
        counts[group].append(score)
    return {g:{'n':len(scores),'mean_trust':mean(scores) if scores else None}
            for g,scores in counts.items()}

if __name__=='__main__': collect()
