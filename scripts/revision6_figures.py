"""Additional static scientific figures from Revision 6 result JSON."""
import json
from pathlib import Path
import matplotlib.pyplot as plt
ROOT=Path(__file__).resolve().parents[1]
def load(p):return json.loads((ROOT/'results/generated'/p).read_text())
def build(out,agent_summary=None):
    out=Path(out);repaired=agent_summary is not None or (ROOT/'results/generated/agent/v6_2_qwen2_5_7b/summary.json').exists()
    doc=json.loads(Path(agent_summary).read_text()) if agent_summary else load('agent/v6_2_qwen2_5_7b/summary.json' if repaired else 'agent/local/summary.json');rows=doc['rows']
    if repaired and agent_summary is None:assert doc['provider']=='ollama' and doc['complete']
    series=[('exact_task_leak','Exact canary','#B34B31'),('fuzzy_task_leak','Fuzzy proxy','#D29A3A'),('utility','Primary success','#1F5A96')]
    if repaired:series.append(('secondary_utility','Secondary success','#557F57'))
    fig,ax=plt.subplots(figsize=(5,3.8 if repaired else 3.3));width=.18 if repaired else .23
    for j,(key,label,color) in enumerate(series):
        xs=[i+(j-(len(series)-1)/2)*width for i in range(len(rows))];ys=[r[key]['mean'] for r in rows]
        err=[[max(0,r[key]['mean']-r[key]['lower']) for r in rows],[max(0,r[key]['upper']-r[key]['mean']) for r in rows]]
        ax.bar(xs,ys,width,label=label,color=color,yerr=err,capsize=2)
    ax.set_xticks(range(len(rows)),[r['condition'].replace('+','+\n').replace('NoRevocation','No\nRevocation') for r in rows],fontsize=8.5)
    ax.set_ylim(0,1.15 if repaired else 1.08);ax.set_ylabel('fraction of tasks');ax.legend(frameon=False,loc='upper center',ncol=2 if repaired else 3,fontsize=8.5)
    fig.tight_layout(pad=.5);fig.savefig(out/'fig10_agent.pdf');plt.close(fig)
    doc=load('robustness/summary.json');rows=doc['rows']
    grow=doc['growth_rows'];p=doc['metadata']['inputs']['p_r'][1]
    fig,axes=plt.subplots(1,2,figsize=(5,3.6));colors=['#1F5A96','#C76F00','#6D4C7D'];uses=['independent','correlated','first_only'];sels=['uniform','recency','zipf']
    for j,use in enumerate(uses):
        pick=[next(r for r in rows if r['selection']==s and r['use_model']==use and r['restriction_probability']==p) for s in sels]
        x=[i+(j-1)*.22 for i in range(len(sels))]
        axes[0].errorbar(x,[r['quarantined'] for r in pick],yerr=[r['quarantined_half_width'] for r in pick],color=colors[j],marker='o',linestyle='-',capsize=2,linewidth=1,label=use.replace('_',' '))
        axes[0].plot(x,[r['truly_dependent'] for r in pick],color=colors[j],marker='s',linestyle=':',linewidth=1)
        pick=[r for r in grow if r['use_model']==use]
        for key,style,marker in [('quarantined','-','o'),('truly_dependent',':','s'),('withheld_clean','--','^')]:
            axes[1].errorbar([r['derived'] for r in pick],[r[key] for r in pick],yerr=[r[key+'_half_width'] for r in pick],color=colors[j],marker=marker,linestyle=style,markersize=3,linewidth=1,capsize=1)
    axes[0].set_xticks(range(len(sels)),['Uniform','Recency','Zipf'],rotation=30,ha='right',fontsize=9);axes[0].set_title('(a) Selection/use grid')
    axes[1].set_title('(b) Recency growth');axes[1].set_xlabel('derived items');axes[1].set_xscale('log');axes[1].set_xticks(sorted({r['derived'] for r in grow}));axes[1].get_xaxis().set_major_formatter(__import__('matplotlib').ticker.ScalarFormatter());axes[1].minorticks_off();axes[1].tick_params(axis='x',labelsize=8)
    for ax in axes:ax.set_ylim(0,1);ax.set_ylabel('item share')
    h,l=axes[0].get_legend_handles_labels();fig.legend(h,l,loc='lower center',ncol=3,frameon=False,fontsize=8.5)
    fig.text(.5,.085,'solid: quarantined    dotted: dependent    dashed: clean withheld',ha='center',fontsize=8.1)
    fig.tight_layout(pad=.5,rect=(0,.15,1,1));fig.savefig(out/'fig11_robustness.pdf');plt.close(fig)
