"""Validate raw workflow metrics and disclose overlapping growth-grid settings."""
import json
from statistics import mean
from common import GENERATED,provenance,write_json

def run():
    folder=GENERATED/'robustness';settings=sorted(folder.glob('setting_*.json'));seen={};total=0;parameter_sets=set()
    for path in settings:
        doc=json.loads(path.read_text());inputs=doc['inputs'];row=doc['row']
        raw=[json.loads(s) for s in path.with_name(path.name.replace('setting_','workflow_').replace('.json','.jsonl')).read_text().splitlines()]
        assert len(raw)==inputs['workflows']
        parameters=(inputs['selection'],inputs['use_model'],inputs['p_r'],inputs['derived'])
        parameter_sets.add(parameters)
        for field in ('quarantined','truly_dependent','over_quarantine_ratio','withheld_clean'):
            values=[r[field] for r in raw if r[field] is not None]
            assert abs(mean(values)-row[field])<1e-12,(path,field)
        assert all(r['sound'] for r in raw)
        for i,r in enumerate(raw):
            assert r['seed']==inputs['root_seed']+i
            key=(*parameters,r['use_probability'],r['seed'])
            if key in seen:assert seen[key]==r,'Overlapping sweep point is inconsistent'
            seen[key]=r;total+=1
    doc={'setting_runs':len(settings),'unique_parameter_settings':len(parameter_sets),
         'workflow_executions':total,'unique_seed_parameter_pairs':len(seen),'repeated_executions':total-len(seen),
         'raw_metrics_verified':True,'soundness_failures':0,'metadata':provenance(experiment='robustness_coverage_and_raw_validation')}
    write_json(folder/'coverage.json',doc);print(doc['workflow_executions'],doc['unique_seed_parameter_pairs']);return doc
if __name__=='__main__':run()
