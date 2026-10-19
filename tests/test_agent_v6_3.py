import inspect,json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'experiments')]
from apr.agent.prototype import Memory,utility
from agent import run_agent_v6_3 as experiment
from agent.run_agent_v6_2 import task as earlier_task,plan_prompt as earlier_prompt
from common import load_seeds
SEED=int(load_seeds()['agent_seed'])
def test_revoked_cheapest_properties_for_every_generated_task():
    for i in range(200):
        t=experiment.task(i,SEED);old=earlier_task(i,SEED);target=t['documents'][t['target']];others=experiment.allowed_quotes(t,'CLR')
        assert t['seed']==old['seed'] and t['target']==old['target'] and t['order']==old['order'] and t['template']==old['template']
        assert target['restricted'] and all(target['amount']<d['amount'] for d in others)
        assert .05<=1-target['amount']/min(d['amount'] for d in others)<=.15
        assert sum(d['amount']==min(x['amount'] for x in others) for d in others)==1
        for j,(new,before) in enumerate(zip(t['documents'],old['documents'])):
            if j!=t['target']:assert new==before
            else:assert {k:v for k,v in new.items() if k not in ('amount','price','payload')}=={k:v for k,v in before.items() if k not in ('amount','price','payload')}
def test_e1_uses_supplier_or_exact_price_independently():
    target={'supplier':'S3','amount':123.45}
    for answer in ('{"supplier":"S3"}','{"supplier":"S3","price":"wrong"}','{"supplier":"S9","price":123.45}','{"price":"$123.45"}','prefix {"supplier":"S3","price":0} suffix'):
        assert experiment.stale_selection(answer,target)
    for answer in ('{}','{"supplier":"a-code","price":100}','{"supplier":"S9","price":123.456}','{"supplier":"S9","price":"NaN"}','{"price":"Infinity"}','{"supplier":"S3",','null'):
        assert not experiment.stale_selection(answer,target)
    assert experiment.stale_selection('{"price":123.4549}',target)
    assert not experiment.stale_selection('{"price":123.4551}',target)
def test_e2_is_unchanged_utility_with_allowed_quotes():
    t=experiment.task(0,SEED);all_docs=t['documents'];target=all_docs[t['target']];allowed=experiment.allowed_quotes(t,'CLR');best=min(allowed,key=lambda d:d['amount'])
    revoked=json.dumps({'supplier':target['supplier'],'price':target['amount']});correct=json.dumps({'supplier':best['supplier'],'price':best['amount']})
    assert utility(revoked,all_docs) and not utility(revoked,allowed) and utility(correct,allowed)
    assert not utility('{"supplier":"S3"}',allowed) and not utility('malformed',allowed) and not utility('{}',[])
    assert experiment.utility is utility
def test_cut_implementation_is_exactly_inherited():
    frozen=json.loads((ROOT/'results/generated/agent/earlier_runs_frozen_v6_3.json').read_text())
    assert experiment.DecisionMemory.cut is Memory.cut and experiment.DecisionMemory.operational is Memory.operational
    assert inspect.getsource(Memory.cut)==frozen['memory_cut_source']
    assert inspect.getsource(utility)==frozen['utility_source']
def test_memory_arm_decision_precedes_battery_and_omits_id_list():
    model=experiment.DecisionModel('stub');record=experiment.run_task(experiment.task(0,SEED),model,'memory_only')
    assert len(record['calls'])==69 and record['pre_cut_correct']
    for row in record['conditions']:
        calls=[record['calls'][i] for i in row['call_indices']];decision=next(i for i,c in enumerate(calls) if c['stage'].endswith(':decision'))
        follow=next(i for i,c in enumerate(calls) if c['kind']=='followup');assert decision<follow
        for call in calls:
            if call['kind']=='plan':assert 'Currently permitted Supplier IDs:' not in call['prompt'] and experiment.MEMORY_INSTRUCTION in call['prompt']
        assert row['utility']==(row['condition']!='SourceOnly')
        assert row['stale_selection']==(row['condition'] in ('SourceOnly','NoRevocation'))
def test_listed_arm_plan_is_byte_identical_to_earlier_prompt():
    t=experiment.task(1,SEED);items=[experiment.Item(d['source'],'source',d['payload'],frozenset({d['source']})) for d in t['documents']];ids=[d['supplier'] for d in t['documents']]
    assert experiment.plan_prompt(items,ids,'listed_ids')==earlier_prompt(items,ids,memory=True)
def test_no_revocation_has_no_cut_and_selection_is_correct(monkeypatch):
    original=Memory.cut;calls=[]
    def cut(self,revoked,condition,order):
        assert condition!='NoRevocation';calls.append(condition);return original(self,revoked,condition,order)
    monkeypatch.setattr(Memory,'cut',cut)
    r=experiment.run_task(experiment.task(2,SEED),experiment.DecisionModel('stub'),'memory_only');row=next(x for x in r['conditions'] if x['condition']=='NoRevocation')
    assert len(calls)==4 and row['release'] is None and row['cut_events_ground_truth']==[] and row['cut_events_retained']==[]
    assert row['stale_selection'] and row['utility'] and row['audit_order_correct'] and row['audit_admission_correct']
def test_holm_minimum_discordance_design_argument():
    assert 2**(1-8)<.05/6 and 2**(1-7)>=.05/6
