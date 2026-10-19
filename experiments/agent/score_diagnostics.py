"""Retrospective schema diagnostics. Primary predeclared task scores are unchanged."""
from __future__ import annotations
import json,re,sys
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'experiments')]
from common import GENERATED,provenance,write_json
from agent.run_agent_experiment import interval
from apr.agent.prototype import utility

def run():
    folder=GENERATED/'agent/local';summary=json.loads((folder/'summary.json').read_text());records=[]
    for i in range(summary['tasks']):
        record=json.loads((folder/f'task_{i:04}.json').read_text());t=record['task'];target=t['documents'][t['target']]
        allowed=[d for d in t['documents'] if d['source']!=target['source']];expected=min(allowed,key=lambda d:d['amount'])
        for row in record['conditions']:
            assert utility(row['final_plan'],allowed)==row['utility'],'Saved primary score differs from its specified predicate'
            try:
                data=json.loads(re.search(r'\{.*\}',row['final_plan'],re.S).group())
                cost=float(str(data.get('price',data.get('exact_price',''))).replace('$','').replace(',',''))
                price_ok=abs(cost-expected['amount'])<.005;supplier_ok=data.get('supplier')==expected['supplier']
            except (ValueError,TypeError,AttributeError):price_ok=False;supplier_ok=False
            records.append({'task':i,'condition':row['condition'],'primary':row['utility'],
                            'key_tolerant_success':price_ok and supplier_ok,'correct_price':price_ok,
                            'canonical_supplier':supplier_ok,'price_correct_supplier_wrong':price_ok and not supplier_ok})
    rows=[]
    for condition in [r['condition'] for r in summary['rows']]:
        selected=[r for r in records if r['condition']==condition]
        rows.append({'condition':condition,**{key:interval([r[key] for r in selected],binary=True) for key in
                     ('primary','key_tolerant_success','correct_price','canonical_supplier','price_correct_supplier_wrong')}})
    doc={'tasks':summary['tasks'],'analysis':'exploratory retrospective field-name diagnostic; primary scores unchanged',
         'rows':rows,'records':records,'metadata':provenance(experiment='agent_schema_diagnostics')}
    write_json(GENERATED/'agent/scoring_diagnostics.json',doc);return doc
if __name__=='__main__':run()
