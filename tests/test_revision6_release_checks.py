import importlib.util
from pathlib import Path
import sys

ROOT=Path(__file__).resolve().parents[1]

def test_missing_checker_input_returns_failure(tmp_path,monkeypatch):
    spec=importlib.util.spec_from_file_location("cross_revision6",ROOT/"scripts/cross_checkers.py")
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.setattr(module,"GENERATED",tmp_path)
    assert module.main()==1

def test_zero_event_interval_retains_sampling_uncertainty():
    sys.path.insert(0,str(ROOT/"experiments"))
    from agent.run_agent_experiment import interval
    result=interval([False]*200,binary=True)
    assert result["mean"]==0 and result["lower"]==0
    assert .018<result["upper"]<.020

def test_incomplete_results_cannot_become_expected_values(tmp_path,monkeypatch):
    import json,pytest
    spec=importlib.util.spec_from_file_location('expected_revision6',ROOT/'scripts/check_expected.py')
    module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
    monkeypatch.setattr(module,'GEN',tmp_path)
    (tmp_path/'model_matrix.json').write_text(json.dumps({'complete':False,'rows':[]}))
    with pytest.raises(RuntimeError,match='incomplete'):
        module.snapshot()

def test_agent_resume_accepts_json_roundtrip_but_rejects_workload_change(tmp_path):
    import json,pytest
    sys.path.insert(0,str(ROOT/'experiments'))
    from agent.run_agent_experiment import run
    first=run(tasks=1,dry_run=True,output=tmp_path)
    resumed=run(tasks=1,dry_run=True,output=tmp_path)
    assert first['rows']==resumed['rows']
    path=tmp_path/'task_0000.json'
    record=json.loads(path.read_text())
    record['task']['documents'][0]['amount']+=1
    path.write_text(json.dumps(record))
    with pytest.raises(RuntimeError,match='Cached workload differs'):
        run(tasks=1,dry_run=True,output=tmp_path)
