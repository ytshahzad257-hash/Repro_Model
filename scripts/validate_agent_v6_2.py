"""Check complete new agent evidence without changing any raw record or score."""
from pathlib import Path
import json,hashlib,sys
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'experiments')]
from agent.run_agent_v6_2 import CONDITIONS,QUERIES,utility,secondary_utility,leakage,task,load_seeds

def main():
    out=ROOT/'results/generated/agent/v6_2_qwen2_5_7b';summary=json.loads((out/'summary.json').read_text());decision=json.loads((out/'sample_decision.json').read_text())
    assert summary['complete'] and summary['tasks']==decision['tasks']
    identity=json.loads((out/'execution_protocol_identity.json').read_text())['identity']
    for name,digest in identity['files'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==digest,name
    records=sorted(out.glob('task_*.json'));assert len(records)==decision['tasks'];calls=0
    for index,path in enumerate(records):
        r=json.loads(path.read_text());assert r['task']==json.loads(json.dumps(task(index,int(load_seeds()['agent_seed']))))
        assert r['signature']['protocol']==identity and r['provider']=='ollama'
        assert set(x['condition'] for x in r['conditions'])==set(CONDITIONS)
        assert len(r['calls'])==81;calls+=len(r['calls'])
        for call in r['calls']:
            assert call['raw']['model']=='qwen2.5:7b' and call['response']==call['raw']['response']
            assert call['seed']==r['task']['seed'] and call['prompt']
            assert call['max_tokens']=={'summary':160,'plan':64,'followup':48}[call['kind']]
        docs=r['task']['documents'];target=docs[r['task']['target']]
        for row in r['conditions']:
            allowed=docs if row['condition']=='NoRevocation' else [d for d in docs if d['source']!=target['source']]
            assert row['allowed_supplier_ids']==[d['supplier'] for d in allowed]
            assert row['utility']==utility(row['final_plan'],allowed)
            assert row['secondary_utility']==secondary_utility(row['final_plan'],allowed)
            assert [f['query'] for f in row['followups']]==list(QUERIES)
            checks=[leakage(f['answer'],target['price'],target['code']) for f in row['followups']]
            assert row['exact_task_leak']==any(e for e,f in checks)
            assert row['fuzzy_task_leak']==any(f for e,f in checks)
            assert row['audit_admission_correct']==(row['audit_retained']==row['audit_ground_truth'])
            assert row['audit_order_correct']==(row['cut_events_retained']==row['cut_events_ground_truth'])
            if row['condition']=='NoRevocation':assert row['cut_events_ground_truth']==[] and row['release'] is None
            if row['condition'] in ('CLR','CLR+Reconstruct'):
                for event in row['audit_ground_truth']:
                    if event['slot'].startswith(('followup-','reconstructed-','final-plan')):assert target['source'] not in event['sources']
    assert calls==summary['raw_model_calls']
    print(f'{len(records)} new records, {calls} raw calls, metrics/source/protocol/NoRevocation checks PASS')
if __name__=='__main__':main()
