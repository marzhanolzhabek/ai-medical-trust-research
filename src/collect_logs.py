"""Measure runtime of the age-group survey processing pipeline (not medical model latency).
Benchmarks re-process the SAME 45 synthetic rows, not additional participants.
"""
import json,time,sys,csv,random
from pathlib import Path
from process_data import analyze

def run():
    root=Path(__file__).resolve().parents[1]
    source=root/'data/sample/sample_synthetic.csv'
    output=root/'data/raw/test_run.jsonl';output.parent.mkdir(parents=True,exist_ok=True)
    random.seed(42)
    with output.open('w',encoding='utf-8') as f:
        for i in range(65):
            start=time.perf_counter_ns();success=True;error=''
            try:result=analyze(source)
            except Exception as e:success=False;error=str(e)
            ms=(time.perf_counter_ns()-start)/1e6
            f.write(json.dumps({'iteration':i,'phase':'warmup' if i<5 else 'benchmark',
                'method':'age_cohort_analysis','load_records':45,'latency_ms':round(ms,6),
                'success':success,'error':error,'seed':42})+'\n')
    print('Saved 65 benchmark logs; 5 warmup and 60 measurements; synthetic dataset has 45 rows')
if __name__=='__main__':run()
