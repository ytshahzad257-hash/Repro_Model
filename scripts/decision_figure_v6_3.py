"""Scientific figure for the frozen decision-harm outcomes; JSON is sole data."""
from pathlib import Path
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def build(out,summary=None):
    a=json.loads(Path(summary or ROOT/'results/generated/agent/v6_3_revoked_cheapest_memory_only/summary.json').read_text());assert a['complete']
    if summary is None:assert a['provider']=='ollama' and a['arm']=='memory_only'
    out=Path(out);out.mkdir(parents=True,exist_ok=True)
    with plt.rc_context({'font.size':9,'axes.labelsize':9,'xtick.labelsize':8.5,'ytick.labelsize':9,'axes.titlesize':9,'pdf.fonttype':42}):
        fig,axes=plt.subplots(1,2,figsize=(6.4,2.8),sharey=True)
        for ax,key,title,color in zip(axes,('stale_selection','utility'),('(a) Supplier/price selection (E1)','(b) Correct permitted choice (E2)'),('#B34B31','#1F5A96')):
            for i,row in enumerate(a['rows']):
                d=row[key];ax.errorbar(d['mean'],i,xerr=[[max(0,d['mean']-d['lower'])],[max(0,d['upper']-d['mean'])]],fmt='o',color='#777777' if row['condition']=='NoRevocation' else color,capsize=3,markersize=5)
            ax.set_xlim(-.04,1.04);ax.set_xticks([0,.25,.5,.75,1]);ax.set_title(title);ax.set_xlabel('fraction of tasks');ax.grid(axis='x',color='#dddddd',linewidth=.5)
            ax.spines[['top','right']].set_visible(False)
        axes[0].set_yticks(range(len(a['rows'])),[r['condition'].replace('NoRevocation','NoRevocation*').replace('CLR+Reconstruct','CLR + reconstruct') for r in a['rows']]);axes[0].invert_yaxis()
        fig.text(.5,.015,'* NoRevocation selection is permitted; error bars are Wilson intervals.',ha='center',fontsize=8.5)
        fig.tight_layout(pad=.7,rect=(0,.07,1,1));fig.savefig(out/'fig12_decision.pdf');plt.close(fig)
if __name__=='__main__':
    import argparse
    p=argparse.ArgumentParser();p.add_argument('out',type=Path);p.add_argument('--preview-summary',type=Path);a=p.parse_args();build(a.out,a.preview_summary)
