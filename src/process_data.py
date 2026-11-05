"""Validate anonymized survey records and compute age-cohort descriptive results.
No synthetic data are evidence about real patients.
"""
import csv, json, argparse, random, statistics
from pathlib import Path
GROUPS=('18-30','31-50','51+')
REQUIRED={'response_id','age','age_group','trust_score','prior_ai_use','ai_knowledge','perceived_accuracy','explanation_clarity','doctor_supervision','education'}
def age_group(age):
    return '18-30' if 18<=age<=30 else '31-50' if 31<=age<=50 else '51+' if age>=51 else None
def bootstrap_ci(values,seed=42,reps=2000):
    if not values:return (None,None)
    rng=random.Random(seed);n=len(values)
    means=sorted(sum(rng.choices(values,k=n))/n for _ in range(reps))
    return (round(means[int(.025*(reps-1))],3),round(means[int(.975*(reps-1))],3))
def analyze(path):
    with open(path,newline='',encoding='utf-8') as f:
        reader=csv.DictReader(f)
        if not REQUIRED.issubset(set(reader.fieldnames or [])):
            raise ValueError('Missing columns: '+str(REQUIRED-set(reader.fieldnames or [])))
        data=list(reader)
    valid=[];seen=set();invalid=0
    for r in data:
        try:
            ident=r['response_id'].strip();age=int(r['age']);trust=int(r['trust_score'])
            if not ident or ident in seen or not 1<=trust<=5 or age_group(age)!=r['age_group']:
                raise ValueError('Invalid ID, age group or trust score')
            for k in ['ai_knowledge','perceived_accuracy','explanation_clarity','doctor_supervision']:
                if not 1<=int(r[k])<=5:raise ValueError('Invalid rating')
            if r['prior_ai_use'] not in ('yes','no'):raise ValueError('Invalid prior use')
            seen.add(ident);valid.append(r)
        except (ValueError,TypeError,KeyError):invalid+=1
    output=[]
    for g in GROUPS:
        scores=[int(r['trust_score']) for r in valid if r['age_group']==g]
        ci=bootstrap_ci(scores)
        output.append({'age_group':g,'n':len(scores),'mean_trust':round(statistics.mean(scores),3) if scores else None,
                       'median_trust':statistics.median(scores) if scores else None,
                       'sd_trust':round(statistics.stdev(scores),3) if len(scores)>1 else None,
                       'ci95_lower':ci[0],'ci95_upper':ci[1],
                       'prior_ai_yes':sum(r['prior_ai_use']=='yes' for r in valid if r['age_group']==g)})
    return {'summary':output,'valid':len(valid),'invalid':invalid,'total':len(data),
            'completion_rate':round(len(valid)/len(data),3) if data else 0,
            'invalid_rate':round(invalid/len(data),3) if data else 0,
            'valid_rows':valid}
def main():
    ap=argparse.ArgumentParser();ap.add_argument('--input',default='data/sample/sample_synthetic.csv');ap.add_argument('--output',default='data/processed/age_group_summary.csv');args=ap.parse_args()
    result=analyze(args.input);p=Path(args.output);p.parent.mkdir(parents=True,exist_ok=True)
    with p.open('w',newline='',encoding='utf-8') as f:
        writer=csv.DictWriter(f,fieldnames=list(result['summary'][0]));writer.writeheader();writer.writerows(result['summary'])
    print(json.dumps({k:v for k,v in result.items() if k!='valid_rows'},indent=2))
if __name__=='__main__':main()
