"""Fail-closed comparison of all declared Python/TLC cases."""
from __future__ import annotations
import json,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'experiments'))
from common import GENERATED,provenance,write_json
FIELDS=('state_count_s0','state_count_s1','transitions_s0','transitions_s1','information_safety',
        'authorization_safety','product_states','product_transitions','synchronous_observations','payload_only',
        'equal_release_product_states','equal_release_product_transitions','equal_release_observations')

def run():
    paths=[GENERATED/n for n in ('model_matrix.json','tlc_matrix.json')]
    if not all(p.exists() for p in paths):
        result={'status':'FAIL','reason':'Missing fresh model or TLC matrix','mismatches':[{'field':'missing_matrix'}]}
        write_json(GENERATED/'cross_checker_agreement.json',result);return result
    py_doc,tl_doc=[json.loads(p.read_text()) for p in paths]
    py={r['case_id']:r for r in py_doc['rows']};tl={r['case_id']:r for r in tl_doc['rows']}
    mismatches=[];compared=0
    if set(py)!=set(tl):mismatches.append({'field':'case_coverage','python_only':sorted(set(py)-set(tl)),'tlc_only':sorted(set(tl)-set(py))})
    if not py_doc.get('complete',False):mismatches.append({'field':'python_matrix_incomplete'})
    for key,r in py.items():
        other=tl.get(key,{})
        if not other.get('all_runs_completed'):mismatches.append({'case_id':key,'field':'tlc_run_validity'})
        for field in FIELDS:
            compared+=1
            if field not in other or r.get(field)!=other[field]:
                mismatches.append({'case_id':key,'field':field,'python':r.get(field),'tlc':other.get(field)})
        compared+=1
        if (r['review_failures']>0)!=(other.get('review_possible')=='violated'):
            mismatches.append({'case_id':key,'field':'review','python':r['review_failures'],'tlc':other.get('review_possible')})
    result={'status':'FAIL' if mismatches else 'PASS','configurations_x_K':len(py),
            'single_copy_count_comparisons':4*len(py),'product_count_comparisons':4*len(py),
            'field_comparisons':compared,'mismatches':mismatches,'tlc_versions':tl_doc.get('tlc_versions'),
            'tlc_runs':tl_doc.get('runs'),'metadata':provenance(experiment='cross_checker_revision6')}
    write_json(GENERATED/'cross_checker_agreement.json',result);return result
def main():
    r=run();print(r['status'],r.get('field_comparisons'),len(r.get('mismatches',[])))
    return 0 if r['status']=='PASS' else 1
if __name__=='__main__':raise SystemExit(main())
