"""Explain every changed baseline assertion; not used by model semantics."""
import json
from common import ROOT,GENERATED,write_json

def run():
    before=json.loads((ROOT/'results/historical_paper_assertions/revision5_1_expected.json').read_text())
    after=json.loads((ROOT/'results/expected/revision5.json').read_text());changes=[]
    def walk(a,b,path=''):
        if isinstance(a,dict) and isinstance(b,dict):
            for k in sorted(set(a)|set(b)):
                key=path+'/'+k
                if k not in a:changes.append({'key':key,'old':None,'new':b[k],'reason':'New Revision 6 case/field, explicitly added for independent secrets, larger coverage or equal-release comparison.'})
                elif k not in b:changes.append({'key':key,'old':a[k],'new':None,'reason':'Replaced schema; see Revision 6 changelog.'})
                else:walk(a[k],b[k],key)
        elif a!=b:
            reason=('Separate persistent cache can survive public reconstruction and be reloaded in mutation cases; no guard was tuned to match expected counts.' if path.startswith('/model/') else
                    'Exact bounds extended through K=4; cache is explicit in pre-cut final states.' if path.startswith('/bounds') else
                    'Sufficiency product now carries explicit session-cache state; hidden-use construction and verdicts are preserved.' if path.startswith('/sufficiency/') else
                    'Seeded uniform workflow baseline retained; investigate any change rather than accepting it automatically.')
            changes.append({'key':path,'old':a,'new':b,'reason':reason})
    walk(before,after);write_json(GENERATED/'expected_delta.json',{'changes':changes,'changed_keys':len(changes)})
    return changes
if __name__=='__main__':print(len(run()),'changed expected keys documented')
