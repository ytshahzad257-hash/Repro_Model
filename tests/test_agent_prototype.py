import importlib.util
from pathlib import Path
from apr.agent.prototype import Item,Memory,Model,leakage


def test_quarantine_includes_persistent_cache_and_queue():
    items=[Item('cache','session-cache','secret',frozenset({'s0'})),Item('queue','queued-tool-arguments','secret',frozenset({'s0'})),Item('clean','source','public',frozenset({'s1'}))]
    m=Memory(items);m.cut({'s0'},'CLR',('Fence','Isolate'))
    assert [x.identifier for x in m.operational('CLR')]==['clean']
    assert {x.identifier for x in m.private}=={'cache','queue'}
    record=m.approved_finding(60000)
    assert record['source_tags']==['s0'] and not m.items[-1].labels
    assert '60000' not in m.items[-1].payload


def test_canary_metrics_and_reconstruction_labels():
    assert leakage('$48,317.29 CODEword','$48,317.29','CODEword')==(True,True)
    assert leakage('codeword','$48,317.29','CODEword')==(False,True)
    m=Memory([Item('s1','source','S1: price $1,000.00; code clean',frozenset({'s1'}))])
    x=m.derive(Model('stub'),'summary',m.items,1,'rebuild')
    assert x.labels==frozenset({'s1'})


def test_declared_audit_service_against_separate_full_trace():
    path=Path(__file__).resolve().parents[1]/'experiments/agent/run_agent_experiment.py'
    spec=importlib.util.spec_from_file_location('agent_experiment',path);module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    result=module.run_task(module.task(0,610018),Model('stub'))
    rows={r['condition']:r for r in result['conditions']}
    assert rows['SourceOnly']['exact_task_leak']
    assert not rows['CLR']['exact_task_leak']
    assert not rows['DeleteAll']['audit_admission_correct']
    assert rows['CLR']['audit_admission_correct'] and rows['CLR']['audit_order_correct']
    assert rows['CLR']['ledger_logical_bits']==rows['CLR']['declared_slot_bound_bits']
    assert not rows['CLR+Reconstruct']['fuzzy_task_leak']
