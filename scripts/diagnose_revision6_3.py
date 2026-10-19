"""Read-only diagnostics of the saved version 6.2 agent run."""
from pathlib import Path
import hashlib,json,sys,inspect
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'experiments')]
from agent.paired_statistics import paired_contrast
from apr.agent.prototype import Memory,utility
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def main():
    out=ROOT/'results/generated/agent';records=[json.loads(p.read_text()) for p in sorted((out/'v6_2_qwen2_5_7b').glob('task_*.json'))];assert len(records)==100
    by={c:[next(x for x in r['conditions'] if x['condition']==c) for r in records] for c in ('NoRevocation','SourceOnly','CLR')}
    indices={c:[r['task']['index'] for r,row in zip(records,rows) if row['exact_task_leak']] for c,rows in by.items()}
    pairs=[{'left':'SourceOnly','right':c,'endpoint':'exact_task_leak','exploratory':True,'preregistered':False,**paired_contrast([r['exact_task_leak'] for r in by['SourceOnly']],[r['exact_task_leak'] for r in by[c]])} for c in ('CLR','NoRevocation')]
    invariance=[]
    for r in records:
        docs=r['task']['documents'];target=docs[r['task']['target']];before=min(docs,key=lambda x:x['amount']);after=min([d for d in docs if d['source']!=target['source']],key=lambda x:x['amount'])
        invariance.append({'task_index':r['task']['index'],'before_supplier':before['supplier'],'after_supplier':after['supplier'],'answer_unchanged':before['supplier']==after['supplier'],'revoked_amount':target['amount'],'permitted_minimum':after['amount']})
    paths=[]
    for folder in ('local','stub','v6_2_qwen2_5_7b','stub_v6_2'):paths.extend((out/folder).rglob('*'))
    paths.extend(out/name for name in ('scoring_diagnostics.json','diagnosis_v6_2.json','preregistration_v6_2.json','revision6_frozen_hashes.json'))
    inventory={p.relative_to(ROOT).as_posix():{'sha256':sha(p),'bytes':p.stat().st_size} for p in sorted(set(paths)) if p.is_file()}
    document={'status':'VERIFIED','tasks':len(records),'exact_emission_task_indices':indices,'same_control_and_sourceonly_tasks':indices['NoRevocation']==indices['SourceOnly'],'exploratory_pairs':pairs,'multiplicity':'Two unadjusted exploratory exact tests; neither was preregistered. No confirmatory claim is made.','utility_answer_unchanged_tasks':sum(r['answer_unchanged'] for r in invariance),'generator_checks':invariance,'sources':{'generator':'experiments/agent/run_agent_experiment.py:26-40','schema_generator':'experiments/agent/run_agent_v6_2.py:17-20','raw_files':'results/generated/agent/v6_2_qwen2_5_7b/task_0000.json through task_0099.json','plan_after_battery':'experiments/agent/run_agent_v6_2.py:104-119'}}
    (out/'diagnosis_v6_3.json').write_text(json.dumps(document,indent=2)+'\n')
    frozen={'version':'6.3 preservation baseline','files':inventory,'utility_source':inspect.getsource(utility),'memory_cut_source':inspect.getsource(Memory.cut),'memory_operational_source':inspect.getsource(Memory.operational)}
    (out/'earlier_runs_frozen_v6_3.json').write_text(json.dumps(frozen,indent=2)+'\n')
    print(json.dumps({'tasks':100,'indices':indices,'pairs':pairs,'unchanged_answers':document['utility_answer_unchanged_tasks'],'earlier_files_frozen':len(inventory)},indent=2))
if __name__=='__main__':main()
