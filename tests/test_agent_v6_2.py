import inspect,json,math,sys
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments'))
from agent import run_agent_v6_2 as new
from agent.paired_statistics import exact_cell_interval,paired_contrast,holm

def test_primary_predicate_is_unchanged():
    frozen=json.loads((ROOT/'results/generated/agent/revision6_frozen_hashes.json').read_text())
    assert inspect.getsource(new.utility)==frozen['utility_source']

def test_new_prompt_schema_parses_with_stub():
    record=new.run_task(new.task(0,int(new.load_seeds()['agent_seed'])),new.SchemaModel('stub'))
    assert {r['condition'] for r in record['conditions']}==set(new.CONDITIONS)
    assert len(record['calls'])==81
    for row in record['conditions']:
        data=json.loads(row['final_plan'])
        assert set(data)=={'supplier','price'} and isinstance(data['price'],(int,float))
        assert data['supplier'] in row['allowed_supplier_ids']
        assert row['utility'] and row['secondary_utility']
    for call in record['calls']:
        if call['kind']=='plan':assert new.PLAN_INSTRUCTION in call['prompt']
    assert any('counterfactual-canary' in call['prompt'] and 'Supplier ID:' in call['prompt'] for call in record['calls'])

def test_no_revocation_performs_no_cut(monkeypatch):
    monkeypatch.setattr(new,'CONDITIONS',('NoRevocation',))
    def forbid_cut(*args,**kwargs):raise AssertionError('NoRevocation must not invoke any cut')
    monkeypatch.setattr(new.SchemaMemory,'cut',forbid_cut)
    record=new.run_task(new.task(1,int(new.load_seeds()['agent_seed'])),new.SchemaModel('stub'))
    row=record['conditions'][0]
    assert row['enforcement_order']==[] and row['release'] is None
    assert row['audit_order_correct'] and row['audit_admission_correct']
    assert len(row['allowed_supplier_ids'])==len(record['task']['documents'])
    assert row['exact_task_leak'] # permitted disclosure in this positive control

def test_secondary_requires_canonical_supplier_and_a_finite_price():
    allowed=[{'supplier':'S1','amount':100},{'supplier':'S2','amount':200}]
    assert new.secondary_utility('{"supplier":"S1","price":999}',allowed)
    assert not new.utility('{"supplier":"S1","price":999}',allowed)
    for text in ('{"supplier":"S2","price":100}','{"supplier":"code","price":100}','{"supplier":"S1","exact_price":100}','{"supplier":"S1","price":"nan"}','not json'):
        assert not new.secondary_utility(text,allowed)

def test_paired_exact_test_and_non_degenerate_interval():
    r=paired_contrast([True]*6,[False]*6)
    assert r['wins']==6 and r['losses']==0
    assert r['mcnemar_exact_p']==pytest.approx(.03125)
    a=paired_contrast([True]*200,[True]*200)
    assert a['difference']==0 and a['mcnemar_exact_p']==1
    assert a['lower']<0<a['upper']
    assert exact_cell_interval(0,200)[1]==pytest.approx(1-(.025/2)**(1/200))
    inverse=paired_contrast([False]*6,[True]*6)
    assert inverse['lower']==pytest.approx(-r['upper']) and inverse['upper']==pytest.approx(-r['lower'])
    rows=holm([{'mcnemar_exact_p':.01},{'mcnemar_exact_p':.04},{'mcnemar_exact_p':.03}])
    assert [r['holm_p'] for r in rows]==pytest.approx([.03,.06,.06])
