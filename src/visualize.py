"""Publication-ready survey plots; data are SYNTHETIC demonstrations."""
import csv
import random
import statistics
from pathlib import Path
import matplotlib.pyplot as plt
from process_data import analyze, GROUPS

def plot(input_path='data/sample/sample_synthetic.csv',out_dir='reports/figures'):
    result=analyze(input_path);summ=result['summary'];out=Path(out_dir);out.mkdir(parents=True,exist_ok=True)
    names=['18–30','31–50','51+'];palette=['#0072B2','#E69F00','#009E73']
    means=[r['mean_trust'] for r in summ]
    lower=[r['mean_trust']-r['ci95_lower'] for r in summ]
    upper=[r['ci95_upper']-r['mean_trust'] for r in summ]
    fig,ax=plt.subplots(figsize=(8.2,4.7))
    ax.bar(names,means,color=palette,width=.58)
    ax.errorbar(names,means,yerr=[lower,upper],fmt='none',ecolor='#222222',capsize=6,lw=1.6)
    ax.set_ylim(0,5.3);ax.set_xlabel('Patient age group (years)');ax.set_ylabel('Mean trust score (1–5)')
    ax.set_title('Trust in AI medical recommendations by age group')
    ax.text(.99,-.20,'Synthetic demonstration data; n=15 per group; error bars: 95% bootstrap CI',transform=ax.transAxes,ha='right',fontsize=8)
    fig.tight_layout();save(fig,out/'fig1_trust_by_age');plt.close(fig)
    fig,ax=plt.subplots(figsize=(8.2,4.7))
    vals=[[int(r['trust_score']) for r in result['valid_rows'] if r['age_group']==g] for g in GROUPS]
    bp=ax.boxplot(vals,patch_artist=True,tick_labels=names,showmeans=True)
    for patch,color in zip(bp['boxes'],palette):patch.set_facecolor(color);patch.set_alpha(.65)
    # 95% bootstrap confidence intervals for group medians, shown as diamond markers.
    for i, scores in enumerate(vals, start=1):
        rng=random.Random(42+i); estimates=sorted(statistics.median(rng.choices(scores,k=len(scores))) for _ in range(2000))
        m=statistics.median(scores);lo=estimates[49];hi=estimates[1949]
        ax.errorbar(i,m,yerr=[[max(0,m-lo)],[max(0,hi-m)]],fmt='D',color='#202020',
                    ecolor='#202020',capsize=6,markersize=5,zorder=10)
    ax.set_ylim(.5,5.5);ax.set_xlabel('Patient age group (years)');ax.set_ylabel('Trust score (1–5)')
    ax.set_title('Distribution of trust scores across patient age groups')
    ax.text(.99,-.20,'Synthetic demonstration data; boxes show IQR, whiskers use 1.5×IQR; diamonds: median with 95% bootstrap CI',transform=ax.transAxes,ha='right',fontsize=8)
    fig.tight_layout();save(fig,out/'fig2_trust_distribution');plt.close(fig)

def save(fig,stem):
    fig.savefig(str(stem)+'.png',dpi=350,bbox_inches='tight')
    fig.savefig(str(stem)+'.pdf',bbox_inches='tight')
if __name__=='__main__':plot()
