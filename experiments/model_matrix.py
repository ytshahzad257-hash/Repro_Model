"""Revision 6 shared/independent-secret and larger-model Python matrix."""
from __future__ import annotations
import argparse,time
from apr.explorer import explore,self_composition
from apr.model import TransitionSystem
from common import GENERATED,provenance,write_json,write_csv
from finite_cases import cases

def row_for(case):
    system=TransitionSystem(case['configuration'],case['sources'],secrets=case['secrets'],revoked=case['revoked'])
    started=time.perf_counter()
    left=explore(system,case['left']);right=explore(system,case['right'])
    single=time.perf_counter()-started
    started=time.perf_counter()
    full=self_composition(system,left_secret=case['left'],right_secret=case['right'])
    payload=self_composition(system,left_secret=case['left'],right_secret=case['right'],payload_only=True)
    equal=self_composition(system,left_secret=case['left'],right_secret=case['right'],equal_release=True)
    w=full.witness
    return {**case,'state_count_s0':len(left.states),'state_count_s1':len(right.states),
            'transitions_s0':left.transitions,'transitions_s1':right.transitions,
            'information_safety':'holds' if left.info_safe and right.info_safe else 'violated',
            'authorization_safety':'holds' if left.auth_safe and right.auth_safe else 'violated',
            'review_failures':left.review_failures+right.review_failures,
            'product_states':full.nodes,'product_transitions':full.transitions,
            'synchronous_observations':'differ' if w else 'equal',
            'payload_only':'differ' if payload.witness else 'equal',
            'equal_release_product_states':equal.nodes,'equal_release_product_transitions':equal.transitions,
            'equal_release_observations':'differ' if equal.witness else 'equal',
            'witness_length':None if w is None else max(len(w.left.actions),len(w.right.actions)),
            'witness_left':None if w is None else list(w.left.actions),
            'witness_right':None if w is None else list(w.right.actions),
            'explorer_seconds_single_both_secrets':round(single,4),
            'explorer_seconds_product_both_comparisons':round(time.perf_counter()-started,4)}

def run(selected=None):
    selected=cases() if selected is None else selected
    rows=[]
    for case in selected:
        row=row_for(case);rows.append(row)
        print(case['case_id'],row['state_count_s0'],row['product_states'],flush=True)
        write_json(GENERATED/'model_matrix.json',{'rows':rows,'complete':len(rows)==len(selected),
                  'metadata':provenance(experiment='model_matrix_revision6',inputs={'cases':selected})})
    write_csv(GENERATED/'model_matrix.csv',[{k:v for k,v in r.items() if not k.startswith('witness_')} for r in rows])
    return rows

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--max-k',type=int,default=4)
    p.add_argument('--no-independent',action='store_true');p.add_argument('--no-larger',action='store_true')
    a=p.parse_args();run(cases(a.max_k,not a.no_independent,not a.no_larger))
