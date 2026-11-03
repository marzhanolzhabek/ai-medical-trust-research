"""Publication exports for 1-5 Likert trust scores (synthetic demonstration)."""
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

def generate(clean,summary,directory):
    directory=Path(directory); directory.mkdir(parents=True,exist_ok=True)
    palette=['#0072B2','#D55E00']
    fig,ax=plt.subplots(figsize=(7,4.5))
    xs=np.arange(len(summary)); means=summary['mean'].to_numpy()
    lower=np.maximum(0,means-summary['ci95_low'].to_numpy()); upper=np.maximum(0,summary['ci95_high'].to_numpy()-means)
    for i,(_,row) in enumerate(summary.iterrows()):
        ax.errorbar(i,row['mean'],yerr=[[lower[i]],[upper[i]]],fmt=['o','s'][i%2],capsize=7,markersize=9,color=palette[i%2],label=row['group'])
    ax.set_xticks(xs,summary['group'].str.title()); ax.set_ylim(1,5.2)
    ax.set_ylabel('Mean trust score (Likert points, 1–5)');ax.set_xlabel('Participant group (synthetic)')
    ax.set_title('Synthetic survey: mean trust with bootstrap 95% CI');ax.grid(axis='y',alpha=.25)
    fig.tight_layout()
    for ext in ['pdf','png']: fig.savefig(directory/f'fig1_mean_trust_ci.{ext}',dpi=300)
    plt.close(fig)
    fig,ax=plt.subplots(figsize=(7,4.5))
    groups=list(summary['group']); vals=[clean.loc[clean['participant_group']==g,'trust_score'].to_numpy() for g in groups]
    bp=ax.boxplot(vals,labels=[g.title() for g in groups],patch_artist=True,showmeans=True)
    for i,patch in enumerate(bp['boxes']): patch.set_facecolor(palette[i]);patch.set_alpha(.4)
    for i,v in enumerate(vals): ax.scatter(np.full(len(v),i+1),v,color=palette[i],marker=['o','s'][i],alpha=.8)
    ax.set_ylim(.8,5.2);ax.set_ylabel('Trust score (Likert points, 1–5)');ax.set_xlabel('Participant group (synthetic)')
    ax.set_title('Synthetic trust-score distribution (boxplot)');ax.grid(axis='y',alpha=.25)
    fig.tight_layout()
    for ext in ['pdf','png']: fig.savefig(directory/f'fig2_trust_distribution.{ext}',dpi=300)
    plt.close(fig)
