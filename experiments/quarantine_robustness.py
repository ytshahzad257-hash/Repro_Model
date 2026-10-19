"""Experiment B: full declared skew/use/restriction grid and recency growth."""
from __future__ import annotations
import argparse,json
from pathlib import Path
from apr.quarantine import run_quarantine_experiment
from common import GENERATED,load_seeds,provenance,write_json,write_csv

def run(workflows=2000):
    seed=int(load_seeds()['robustness_seed']);out=GENERATED/'robustness';out.mkdir(parents=True,exist_ok=True)
    rows=[];growth=[]
    settings=[(s,u,p,100,False) for s in ('uniform','recency','zipf') for u in ('independent','correlated','first_only') for p in (.05,.1,.2)]
    settings += [('recency',u,.1,n,True) for u in ('independent','correlated','first_only') for n in (25,50,100,200,400)]
    for index,(selection,use_model,restriction,n,is_growth) in enumerate(settings):
        seeds=[seed+i for i in range(workflows)];raw=[]
        row=run_quarantine_experiment(seeds=seeds,use_probabilities=(.5,),sources=20,derived=n,
                     restricted_probability=restriction,fanin=3,selection=selection,use_model=use_model,raw_records=raw)[0]
        row.update(selection=selection,use_model=use_model,restriction_probability=restriction,derived=n)
        (growth if is_growth else rows).append(row)
        (out/f'workflow_{index:02}.jsonl').write_text(''.join(json.dumps(r,sort_keys=True)+'\n' for r in raw))
        write_json(out/f'setting_{index:02}.json',{'inputs':{'selection':selection,'use_model':use_model,'p_r':restriction,'derived':n,'workflows':workflows,'root_seed':seed},'row':row})
        print(index+1,len(settings),selection,use_model,restriction,n,flush=True)
    result={'rows':rows,'growth_rows':growth,'settings':len(settings),'workflows_per_setting':workflows,
            'total_workflows':workflows*len(settings),'soundness_failures':sum(r['soundness_failures'] for r in rows+growth),
            'metadata':provenance(experiment='quarantine_robustness_revision6',inputs={'sources':20,'fanin':3,'nominal_u':.5,'recency_decay':.9,'zipf_exponent':1.1,'correlated_all_probability':.5,'confidence_level':.95,'selection':['uniform','recency','zipf'],'use_model':['independent','correlated','first_only'],'p_r':[.05,.1,.2]},seed=seed)}
    write_json(out/'summary.json',result);write_csv(out/'grid.csv',rows);write_csv(out/'growth.csv',growth)
    return result
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--workflows',type=int,default=2000);a=p.parse_args();run(a.workflows)
