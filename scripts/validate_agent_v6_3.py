"""Independently check the saved new evidence; never touch earlier run data."""
from pathlib import Path
import json,hashlib,sys,math
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'experiments')]
from agent.run_agent_v6_3 import task,allowed_quotes,stale_selection,parse_plan,identity,MEMORY_INSTRUCTION,DIGEST,CONDITIONS,QUERIES
from agent.run_agent_experiment import interval
from agent.paired_statistics import paired_contrast,holm
from apr.agent.prototype import utility,leakage
from common import load_seeds
def same_numbers(actual,expected,key=''):
    if isinstance(expected,dict):return isinstance(actual,dict) and actual.keys()==expected.keys() and all(same_numbers(actual[k],v,k) for k,v in expected.items())
    if isinstance(expected,list):return isinstance(actual,list) and len(actual)==len(expected) and all(same_numbers(x,y,key) for x,y in zip(actual,expected))
    if isinstance(expected,float):return math.isclose(actual,expected,rel_tol=1e-12,abs_tol=0 if key.endswith('_p') else 1e-12)
    return actual==expected
def main():
    gen=ROOT/'results/generated/agent';decision=json.loads((gen/'sample_decision_v6_3.json').read_text());protocol=identity();snapshot=json.loads((gen/'execution_protocol_identity_v6_3.json').read_text());assert protocol==snapshot['identity']
    arms=['memory_only']+(['listed_ids'] if decision['secondary_eligible'] else []);report=[]
    for arm in arms:
        out=gen/('v6_3_revoked_cheapest_'+arm);summary=json.loads((out/'summary.json').read_text());assert summary['complete'] and summary['tasks']==100 and summary['arm']==arm
        records=sorted(out.glob('task_*.json'));assert len(records)==100;by={c:[] for c in CONDITIONS};calls=0;pre=[]
        for index,path in enumerate(records):
            r=json.loads(path.read_text());assert r['task']==json.loads(json.dumps(task(index,int(load_seeds()['agent_seed'])))) and r['arm']==arm
            assert r['signature']['protocol']==protocol and r['signature']['runtime']['model_digest']==DIGEST and r['provider']=='ollama'
            assert len(r['calls'])==69;calls+=69;target=r['task']['documents'][r['task']['target']]
            assert r['pre_cut_correct']==utility(r['pre_cut_plan'],r['task']['documents']);pre.append(r['pre_cut_correct'])
            journal=out/'call_journals'/f"task_{index:04}_attempt_{r['attempt']:03}.jsonl"
            assert [json.loads(s) for s in journal.read_text().splitlines()]==r['calls']
            for c in r['calls']:
                assert c['seed']==r['task']['seed'] and c['raw']['model']=='qwen2.5:7b' and c['response']==c['raw']['response']
                assert c['max_tokens']=={'summary':160,'plan':64,'followup':48}[c['kind']]
            assert {row['condition'] for row in r['conditions']}==set(CONDITIONS)
            if arm=='memory_only':
                prompts={c:next(call['prompt'] for call in r['calls'] if call['stage']==c+':decision') for c in ('NoRevocation','SourceOnly')}
                assert prompts['NoRevocation']==prompts['SourceOnly']
            for row in r['conditions']:
                condition=row['condition'];by[condition].append(row);allowed=allowed_quotes(r['task'],condition)
                assert row['allowed_supplier_ids']==[d['supplier'] for d in allowed]
                assert row['stale_selection']==stale_selection(row['final_plan'],target) and row['utility']==utility(row['final_plan'],allowed)
                assert row['invalid_plan']==(parse_plan(row['final_plan']) is None)
                own=[r['calls'][i] for i in row['call_indices']];first=next(i for i,c in enumerate(own) if c['stage'].endswith(':decision'));follow=next(i for i,c in enumerate(own) if c['kind']=='followup');assert first<follow
                assert own[first]['response']==row['final_plan'] and row['charged_model_calls']==2+len(own)
                charged=r['calls'][:2]+own
                assert same_numbers(row['provider_seconds'],sum(c['seconds'] for c in charged))
                assert row['input_tokens']==sum(c['raw'].get('prompt_eval_count',0) for c in charged)
                assert row['output_tokens']==sum(c['raw'].get('eval_count',0) for c in charged)
                ledger_bytes=len(json.dumps({'admissions':row['audit_retained'],'order':row['cut_events_retained']}).encode()) if condition!='DeleteAll' else 0
                assert row['ledger_serialized_bytes']==ledger_bytes
                for c in own:
                    if c['kind']=='plan':
                        if arm=='memory_only':assert c['prompt'].endswith(MEMORY_INSTRUCTION)
                        else:assert c['prompt'].endswith('Currently permitted Supplier IDs: '+', '.join(d['supplier'] for d in allowed))
                assert [f['query'] for f in row['followups']]==list(QUERIES)
                checks=[leakage(f['answer'],target['price'],target['code']) for f in row['followups']]
                assert row['exact_task_leak']==any(x for x,y in checks) and row['fuzzy_task_leak']==any(y for x,y in checks)
                assert row['audit_admission_correct']==(row['audit_retained']==row['audit_ground_truth']) and row['audit_order_correct']==(row['cut_events_retained']==row['cut_events_ground_truth'])
                if condition=='NoRevocation':assert row['cut_events_ground_truth']==[] and row['release'] is None
                elif condition!='SourceOnly':
                    for event in row['audit_ground_truth']:
                        if event['slot'] not in ('summary','plan'):assert target['source'] not in event['sources']
        assert calls==summary['raw_model_calls'] and same_numbers(interval(pre,binary=True),summary['pre_cut_correct'])
        for row in summary['rows']:
            for field in ('stale_selection','utility','invalid_plan','exact_task_leak','fuzzy_task_leak','audit_admission_correct','audit_order_correct'):
                assert same_numbers(interval([r[field] for r in by[row['condition']]],binary=True),row[field])
            for field in ('charged_model_calls','seconds','label_seconds','provider_seconds','input_tokens','output_tokens','ledger_serialized_bytes'):
                assert same_numbers(interval([r[field] for r in by[row['condition']]]),row[field])
        contrasts=[]
        if arm=='memory_only':
            for endpoint in ('stale_selection','utility'):
                for other in ('CLR','CLR+Reconstruct','DeleteAll'):
                    contrasts.append({'left':'SourceOnly','right':other,'endpoint':endpoint,**paired_contrast([r[endpoint] for r in by['SourceOnly']],[r[endpoint] for r in by[other]])})
            holm(contrasts)
        assert same_numbers(contrasts,summary['paired_comparisons'])
        report.append({'arm':arm,'tasks':100,'calls':calls,'raw_journals_match':True,'endpoints_and_intervals_match':True,'paired_tests_match':True})
    result={'status':'PASS','arms':report,'protocol_sha256':protocol['protocol_sha256'],'earlier_runs':'Verified separately without rescoring','numeric_validation_tolerance':'1e-12 absolute/relative for reported continuous values/intervals; p-values relative only, preserving tiny nonzero p-values; binary endpoints and raw journals exact'}
    (ROOT/'results/generated/agent/evidence_validation_v6_3.json').write_text(json.dumps(result,indent=2)+'\n');print(json.dumps(result,indent=2))
if __name__=='__main__':main()
