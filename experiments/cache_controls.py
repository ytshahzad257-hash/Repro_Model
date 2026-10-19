"""Cache-off controls for the original configurations, not a tuned expectation."""
from apr.explorer import explore,self_composition
from apr.model import TransitionSystem,GLOBAL_ACTIONS,INTERNAL_ACTIONS
from common import GENERATED,provenance,write_json
from finite_cases import CONFIGS

def run():
    rows=[]
    for cfg in CONFIGS[:7]:
        models=[TransitionSystem(cfg,session_cache=cache) for cache in (False,True)]
        results=[]
        for system in models:
            ex=[explore(system,b) for b in (0,1)]
            results.append({'states':[len(r.states) for r in ex],
                'verdicts':{'info':all(r.info_safe for r in ex),'auth':all(r.auth_safe for r in ex),
                           'review':any(r.review_failures>0 for r in ex),
                           'observations':self_composition(system).witness is None,
                           'payload':self_composition(system,payload_only=True).witness is None}})
        rows.append({'configuration':cfg,'without_cache':results[0],'with_cache':results[1],
                     'verdicts_equal':results[0]['verdicts']==results[1]['verdicts'],
                     'counts_changed':results[0]['states']!=results[1]['states']})
    assert all(r['verdicts_equal'] for r in rows)
    write_json(GENERATED/'cache_controls.json',{'rows':rows,'sources':1,'metadata':provenance(experiment='cache_off_revision6')})
    write_json(GENERATED/'model_definition.json',{'global_actions':GLOBAL_ACTIONS,'internal_actions':INTERNAL_ACTIONS})
    return rows
if __name__=='__main__':run()
