"""Generate accessible, publication-ready benchmark figures."""
from pathlib import Path
import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from process_data import read_measurements, build_summary

def figures(root):
    root=Path(root); out=root/'reports/figures';out.mkdir(parents=True,exist_ok=True)
    summary=build_summary(root)
    loads=np.array([d['load'] for d in summary])
    med=np.array([d['median_us_per_calculation'] for d in summary])
    low=np.array([d['ci95_low_us_per_calculation'] for d in summary])
    high=np.array([d['ci95_high_us_per_calculation'] for d in summary])
    plt.rcParams.update({'font.size':10,'figure.dpi':130,'axes.spines.top':False,'axes.spines.right':False})
    fig,ax=plt.subplots(figsize=(7.3,4.6))
    ax.errorbar(loads,med,yerr=[med-low,high-med],fmt='o-',color='#0072B2',ecolor='#333333',capsize=5,lw=2,markersize=7,label='Median and 95% bootstrap CI')
    ax.set_xlabel('In-memory calculations per timed measurement (count)')
    ax.set_ylabel('Latency per calculation (microseconds)')
    ax.set_title('Survey calculation latency versus batch size')
    ax.set_xticks(loads);ax.grid(axis='y',alpha=.25)
    ax.legend(frameon=False,loc='best')
    fig.tight_layout()
    for ext in ('png','pdf'):fig.savefig(out/f'fig1_latency_vs_load.{ext}',dpi=320)
    plt.close(fig)
    selected=(1,50); data=[]
    for load in selected:
        a=read_measurements(root/f'data/raw/load_{load}.jsonl')
        data.append([float(r['latency_us'])/load for r in a if r['status']=='ok' and not r.get('warmup',False)])
    fig,ax=plt.subplots(figsize=(7.3,4.6))
    bp=ax.boxplot(data,tick_labels=['Baseline: 1 calculation','Batch: 50 calculations'],patch_artist=True,showfliers=True,medianprops={'color':'black','linewidth':2})
    for patch,color in zip(bp['boxes'],('#0072B2','#E69F00')):
        patch.set_facecolor(color);patch.set_alpha(.55);patch.set_edgecolor('black')
    for i,load in enumerate(selected):
        d=next(x for x in summary if x['load']==load)
        ax.errorbar(i+1,d['median_us_per_calculation'],yerr=[[d['median_us_per_calculation']-d['ci95_low_us_per_calculation']],[d['ci95_high_us_per_calculation']-d['median_us_per_calculation']]],fmt='D',color='black',capsize=6,markersize=5,label='Median 95% CI' if i==0 else None)
    ax.set_ylabel('Latency per calculation (microseconds)')
    ax.set_xlabel('Measured workload configuration')
    ax.set_title('Latency distribution: single versus batch workload')
    ax.legend(frameon=False);ax.grid(axis='y',alpha=.25)
    fig.tight_layout()
    for ext in ('png','pdf'):fig.savefig(out/f'fig2_distribution_boxplot.{ext}',dpi=320)
    plt.close(fig)
    return summary

if __name__=='__main__':
    root=Path(sys.argv[1]) if len(sys.argv)>1 else Path('.')
    figures(root)
    print('Exported two PNG (320 dpi) and two vector PDF figures')
