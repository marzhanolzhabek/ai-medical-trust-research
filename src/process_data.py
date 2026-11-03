"""Analyze synthetic survey responses; never interpret as real participant evidence."""
from pathlib import Path
import numpy as np
import pandas as pd

REQUIRED = ['response_id','participant_group','trust_score','prior_ai_use']
def bootstrap_ci(values, seed=42, n_boot=3000):
    values = np.asarray(values, dtype=float)
    if len(values) == 0: return (np.nan, np.nan)
    rng = np.random.default_rng(seed)
    samples = rng.choice(values, size=(n_boot,len(values)), replace=True)
    return tuple(np.percentile(samples.mean(axis=1),[2.5,97.5]))

def analyze(source, output=None):
    df = pd.read_csv(source)
    missing = set(REQUIRED)-set(df.columns)
    if missing: raise ValueError(f'Missing columns: {missing}')
    total = len(df)
    valid = df['response_id'].notna() & ~df['response_id'].duplicated() & df['participant_group'].isin(['student','patient']) & pd.to_numeric(df['trust_score'],errors='coerce').between(1,5)
    clean = df.loc[valid].copy()
    clean['trust_score'] = clean['trust_score'].astype(float)
    summary=[]
    for i,(group,g) in enumerate(clean.groupby('participant_group')):
        v=g['trust_score'].to_numpy()
        lo,hi=bootstrap_ci(v,42+i)
        summary.append({'group':group,'n':len(v),'mean':v.mean(),'sd':v.std(ddof=1) if len(v)>1 else 0,'median':np.median(v),'p25':np.percentile(v,25),'p75':np.percentile(v,75),'p95':np.percentile(v,95),'p99':np.percentile(v,99),'ci95_low':lo,'ci95_high':hi,'invalid_rate':(total-len(clean))/total if total else np.nan})
    result=pd.DataFrame(summary).sort_values('group').reset_index(drop=True)
    if output is not None:
        Path(output).parent.mkdir(parents=True,exist_ok=True)
        result.to_csv(output,index=False)
    return clean,result,{'total_rows':total,'valid_rows':len(clean),'invalid_rows':total-len(clean),'completion_rate':len(clean)/total if total else np.nan,'invalid_response_rate':(total-len(clean))/total if total else np.nan}
