"""Scientific plots for the controlled, in-memory processing benchmark."""
from pathlib import Path
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from benchmark_statistics import read_logs, aggregate, bootstrap_median_ci

COLORS={'baseline':'#0072B2','proposed':'#D55E00'}
STYLES={'baseline':('--','s'),'proposed':('-','o')}
ROOT=Path(__file__).resolve().parents[1]

def save(fig,out,stem):
    fig.savefig(out/(stem+'.png'),dpi=350,bbox_inches='tight')
    fig.savefig(out/(stem+'.pdf'),bbox_inches='tight')
    plt.close(fig)

def figures(out_dir=None):
    out=Path(out_dir) if out_dir else ROOT/'reports/figures'
    out.mkdir(parents=True,exist_ok=True)
    entries=read_logs(); rows=aggregate(entries)
    fig,ax=plt.subplots(figsize=(8.2,4.7))
    for method in ('baseline','proposed'):
        rs=sorted([r for r in rows if r['method']==method],key=lambda x:x['load_records'])
        x=[r['load_records'] for r in rs];y=[r['median_ms'] for r in rs]
        yerr=[[max(0,r['median_ms']-r['ci95_low_ms']) for r in rs],
              [max(0,r['ci95_high_ms']-r['median_ms']) for r in rs]]
        ls,marker=STYLES[method]
        ax.errorbar(x,y,yerr=yerr,linestyle=ls,marker=marker,color=COLORS[method],
                    label=method.title(),capsize=4,lw=2)
    ax.set_xlabel('Synthetic records processed per run (records)')
    ax.set_ylabel('In-memory processing latency (ms)')
    ax.set_title('Processing latency vs workload (95% CI for median)')
    ax.grid(alpha=.2);ax.legend(title='Implementation')
    fig.text(.5,.01,'Same 45 synthetic observations repeated for load; not new patient participants.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1));save(fig,out,'fig1_latency_vs_load')

    highest=max(r['load_records'] for r in rows)
    fig,ax=plt.subplots(figsize=(8.2,4.7))
    groups=[]
    for method in ('baseline','proposed'):
        groups.append([float(e['latency_ms']) for e in entries if e['phase']=='benchmark'
                       and e['success'] and e['load_records']==highest and e['method']==method])
    bp=ax.boxplot(groups,positions=[1,2],patch_artist=True,widths=.45,showfliers=True)
    for patch,name in zip(bp['boxes'],('baseline','proposed')):
        patch.set_facecolor(COLORS[name]);patch.set_alpha(.35)
    for i,(name,vals) in enumerate(zip(('baseline','proposed'),groups),1):
        from statistics import median
        m=median(vals);lo,hi=bootstrap_median_ci(vals)
        ax.errorbar([i],[m],yerr=[[max(0,m-lo)],[max(0,hi-m)]],fmt='D',
                    color=COLORS[name],ecolor=COLORS[name],capsize=9,label=f'{name.title()} median 95% CI',zorder=9)
    ax.set_xticks([1,2],['Baseline','Proposed'])
    ax.set_xlabel('Processing method (same synthetic workload)')
    ax.set_ylabel('In-memory processing latency (ms)')
    ax.set_title(f'Latency distribution at {highest} synthetic records')
    ax.legend(loc='upper right',fontsize=8)
    ax.grid(axis='y',alpha=.2)
    fig.text(.5,.01,'Boxes: IQR and whiskers; diamonds: medians with 95% bootstrap CI.',ha='center',fontsize=8)
    fig.tight_layout(rect=(0,.04,1,1));save(fig,out,'fig2_distribution_boxplot')
    return out

if __name__=='__main__':print(figures())
