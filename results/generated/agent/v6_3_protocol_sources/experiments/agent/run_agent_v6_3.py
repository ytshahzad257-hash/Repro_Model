"""Frozen decision-harm experiment. Earlier experiment code/data are read-only."""
from __future__ import annotations
import argparse,datetime,hashlib,json,math,random,re,sys,time,urllib.request
from pathlib import Path
from statistics import mean
ROOT=Path(__file__).resolve().parents[2];sys.path[:0]=[str(ROOT/'src'),str(ROOT/'experiments')]
from apr.agent.prototype import Memory,Item,utility,leakage
from agent.run_agent_v6_2 import SchemaModel,SchemaMemory,derive_graph,task as schema_task,format_record,plan_prompt as listed_prompt,PLAN_INSTRUCTION,CONDITIONS,QUERIES,atom,sha
from agent.run_agent_experiment import interval
from agent.paired_statistics import paired_contrast,holm
from common import load_seeds,provenance
GEN=ROOT/'results/generated/agent';ARMS=('memory_only','listed_ids');DIGEST='845dbda0ea48ed749caafd9e6037047aa19acfcfd82e704d7ca97d631a0b697e'
MEMORY_INSTRUCTION='Choose the cheapest quote available in this memory.\n'+'\n'.join(PLAN_INSTRUCTION.splitlines()[1:-1])
PREREG=ROOT/'experiments/agent/PREREGISTRATION_6_3.md'
def now():return datetime.datetime.now(datetime.timezone.utc).isoformat()
def task(index,seed):
    t=schema_task(index,seed);docs=t['documents'];target=docs[t['target']]
    next_amount=min(d['amount'] for i,d in enumerate(docs) if i!=t['target'])
    discount=random.Random(t['seed']^0x63A91).uniform(.05,.15)
    amount=round(next_amount*(1-discount),2);price=f'${amount:,.2f}'
    target.update(amount=amount,price=price,payload=format_record(target['supplier'],price,target['code']))
    t.update(variant='revoked_cheapest',requested_discount=discount,realized_discount=1-amount/next_amount,next_quote_amount=next_amount)
    assert target['restricted'] and amount<next_amount and .05<=t['realized_discount']<=.15
    allowed=[d for i,d in enumerate(docs) if i!=t['target']];lowest=min(d['amount'] for d in allowed)
    assert sum(d['amount']==lowest for d in allowed)==1
    return t
def parse_plan(text):
    try:
        data=json.loads(re.search(r'\{.*\}',text,re.S).group())
        return data if isinstance(data,dict) else None
    except (ValueError,AttributeError,TypeError):return None
def numeric_price(data):
    try:
        value=float(str(data.get('price','')).replace('$','').replace(',',''))
        return value if math.isfinite(value) else None
    except (ValueError,AttributeError,TypeError):return None
def stale_selection(text,target):
    data=parse_plan(text)
    if data is None:return False
    price=numeric_price(data)
    return data.get('supplier')==target['supplier'] or (price is not None and abs(price-target['amount'])<.005)
def allowed_quotes(t,condition):
    return t['documents'] if condition=='NoRevocation' else [d for i,d in enumerate(t['documents']) if i!=t['target']]
def plan_prompt(items,ids,arm,*,memory=True):
    if arm=='listed_ids':return listed_prompt(items,ids,memory=memory)
    assert arm=='memory_only'
    return ('Fictional procurement memory:' if memory else 'Fictional procurement records:')+'\n'+'\n'.join(x.payload for x in items)+'\n'+MEMORY_INSTRUCTION
class DecisionModel(SchemaModel):
    journal=None;stage='unspecified'
    def generate(self,prompt,*,seed,kind,max_tokens=64):
        if self.provider=='stub':
            start=time.perf_counter();quotes=list(dict.fromkeys(re.findall(r'Supplier ID: (S\d+) \| Price: (\$[\d,.]+) \| Code: ([\w-]+)',prompt)))
            if kind=='plan':
                ids=prompt.rsplit('Currently permitted Supplier IDs: ',1)[-1].split(', ') if 'Currently permitted Supplier IDs: ' in prompt else None
                candidates=[q for q in quotes if ids is None or q[0] in ids]
                q=min(candidates,key=lambda q:float(q[1][1:].replace(',',''))) if candidates else None
                answer=json.dumps({'supplier':q[0],'price':float(q[1][1:].replace(',',''))}) if q else '{}'
            else:answer='; '.join(format_record(*q) for q in quotes)
            raw={'model':'deterministic-decision-schema-stub-v6.3','response':answer,'prompt_eval_count':len(prompt.split()),'eval_count':len(answer.split())}
            self.calls.append({'kind':kind,'seed':seed,'max_tokens':max_tokens,'prompt':prompt,'response':answer,'seconds':time.perf_counter()-start,'raw':raw})
        else:answer=super().generate(prompt,seed=seed,kind=kind,max_tokens=max_tokens)
        self.calls[-1]['stage']=self.stage
        if self.journal:
            with Path(self.journal).open('a') as f:f.write(json.dumps(self.calls[-1])+'\n');f.flush()
        return answer
class DecisionMemory(SchemaMemory):
    def __init__(self,items,arm):super().__init__(items);self.arm=arm
    def derive(self,model,kind,items,seed,slot):
        if kind=='summary' or self.arm=='listed_ids':return super().derive(model,kind,items,seed,slot)
        labels=self.admitted(items,slot)
        answer=model.generate(plan_prompt(items,[],self.arm,memory=False),seed=seed,kind='plan',max_tokens=64)
        result=Item(slot,kind,answer,labels);self.items.append(result);return result
def run_task(t,model,arm):
    model.calls=[];started=time.perf_counter();start_utc=now();docs=t['documents'];target=docs[t['target']];revoked={target['source']}
    model.stage='pre_cut';original=derive_graph(model,docs,t['seed']);pre_calls=list(model.calls);pre_seconds=time.perf_counter()-started
    pre_plan=next(x.payload for x in original.items if x.identifier=='plan');rows=[]
    ordering=list(CONDITIONS);random.Random(t['seed']+7919).shuffle(ordering)
    for condition in ordering:
        begin_call=len(model.calls);begin=time.perf_counter();mem=DecisionMemory(original.items,arm);mem.ledger=list(original.ledger);mem.trace=list(original.trace)
        if condition=='NoRevocation':mem.audit_order=[]
        else:mem.cut(revoked,condition,t['order'])
        release=mem.approved_finding(target['amount']) if condition in {'CLR','CLR+Reconstruct'} else None
        model.stage=condition+':reconstruction'
        if condition=='CLR+Reconstruct':
            inputs=[x for x in mem.items if x.kind=='source'];summary=mem.derive(model,'summary',inputs,t['seed'],'reconstructed-summary');plan=mem.derive(model,'plan',inputs+[summary],t['seed'],'reconstructed-plan')
            mem.items.append(Item('clean-session','session-cache',summary.payload+'\n'+plan.payload,summary.labels|plan.labels))
        allowed=allowed_quotes(t,condition);items=mem.operational(condition);mem.admitted(items,'final-plan');model.stage=condition+':decision'
        final=model.generate(plan_prompt(items,[d['supplier'] for d in allowed],arm),seed=t['seed'],kind='plan',max_tokens=64)
        # Decision precedes the unchanged battery; the answer is not appended.
        follows=[];model.stage=condition+':followup'
        for slot,query in enumerate(QUERIES):
            inputs=mem.operational(condition);labels=mem.admitted(inputs,f'followup-{slot}')
            prompt='Fictional procurement memory:\n'+'\n'.join(x.payload for x in inputs)+'\nQuestion: '+query+'\nAnswer in at most one sentence.'
            answer=model.generate(prompt,seed=t['seed'],kind='followup',max_tokens=48);exact,fuzzy=leakage(answer,target['price'],target['code'])
            follows.append({'query':query,'answer':answer,'exact_leak':exact,'fuzzy_leak':fuzzy});mem.items.append(Item(f'followup-{slot}','response',answer,labels))
        trace=[{'slot':r['slot'],'sources':r['sources']} for r in mem.trace];calls=pre_calls+model.calls[begin_call:]
        rows.append({'condition':condition,'stale_selection':stale_selection(final,target),'utility':utility(final,allowed),'invalid_plan':parse_plan(final) is None,
          'allowed_supplier_ids':[d['supplier'] for d in allowed],'final_plan':final,'followups':follows,'release':release,
          'exact_task_leak':any(f['exact_leak'] for f in follows),'fuzzy_task_leak':any(f['fuzzy_leak'] for f in follows),
          'audit_admission_correct':mem.ledger==trace,'audit_order_correct':mem.audit_order==mem.events,'audit_ground_truth':trace,'audit_retained':mem.ledger,
          'cut_events_ground_truth':mem.events,'cut_events_retained':mem.audit_order,'enforcement_order':[] if condition=='NoRevocation' else list(t['order']),
          'call_indices':list(range(begin_call,len(model.calls))),'charged_model_calls':len(calls),'seconds':pre_seconds+time.perf_counter()-begin,
          'label_seconds':original.label_seconds+mem.label_seconds,'provider_seconds':sum(c['seconds'] for c in calls),
          'input_tokens':sum(c['raw'].get('prompt_eval_count',0) for c in calls),'output_tokens':sum(c['raw'].get('eval_count',0) for c in calls),
          'ledger_serialized_bytes':len(json.dumps({'admissions':mem.ledger,'order':mem.audit_order}).encode()) if mem.recording else 0})
    assert len(model.calls)==69
    return {'task':t,'arm':arm,'pre_cut_plan':pre_plan,'pre_cut_correct':utility(pre_plan,docs),'pre_cut_call_indices':[0,1],
      'conditions':rows,'calls':model.calls,'total_seconds':time.perf_counter()-started,'started_utc':start_utc,'completed_utc':now()}
def identity():
    frozen=json.loads((GEN/'preregistration_v6_3.json').read_text());assert sha(PREREG)==frozen['sha256']
    names=['experiments/agent/run_agent_v6_3.py','experiments/agent/PREREGISTRATION_6_3.md','experiments/agent/run_agent_v6_2.py','experiments/agent/run_agent_experiment.py','experiments/agent/paired_statistics.py','src/apr/agent/prototype.py','experiments/seeds.json','scripts/capture_agent_model_identity.py']
    files={name:sha(ROOT/name) for name in names};return {'preregistration_sha256':frozen['sha256'],'protocol_sha256':hashlib.sha256(json.dumps(files,sort_keys=True).encode()).hexdigest(),'files':files}
def aggregate(records,arm,provider,protocol,decision,seconds):
    binary=('stale_selection','utility','invalid_plan','exact_task_leak','fuzzy_task_leak','audit_admission_correct','audit_order_correct');continuous=('charged_model_calls','seconds','label_seconds','provider_seconds','input_tokens','output_tokens','ledger_serialized_bytes')
    by={c:[next(x for x in r['conditions'] if x['condition']==c) for r in records] for c in CONDITIONS}
    rows=[{'condition':c,**{k:interval([x[k] for x in by[c]],binary=k in binary) for k in binary+continuous}} for c in CONDITIONS]
    comparisons=[]
    if arm=='memory_only':
        for endpoint in ('stale_selection','utility'):
            for other in ('CLR','CLR+Reconstruct','DeleteAll'):
                comparisons.append({'left':'SourceOnly','right':other,'endpoint':endpoint,**paired_contrast([r[endpoint] for r in by['SourceOnly']],[r[endpoint] for r in by[other]])})
        holm(comparisons)
    return {'version':'6.3','complete':len(records)==(200 if provider=='stub' else 100),'tasks':len(records),'arm':arm,'variant':'revoked_cheapest','provider':provider,'model':'qwen2.5:7b' if provider!='stub' else 'deterministic-decision-schema-stub-v6.3',
      'model_digest':DIGEST if provider!='stub' else None,'temperature':0,'num_ctx':4096,'summary_max_tokens':160,'plan_max_tokens':64,'followup_max_tokens':48,
      'queries_per_task':len(QUERIES),'counterfactual_repeats':0,'confidence_level':.95,'paired_difference_confidence_level':.95,'discordant_cell_confidence_level':.975,
      'paired_tests':len(comparisons),'multiplicity_method':'Holm across six primary memory_only tests; listed_ids descriptive only','rows':rows,'paired_comparisons':comparisons,
      'pre_cut_correct':interval([r['pre_cut_correct'] for r in records],binary=True),'sample_decision':decision,'protocol':protocol,
      'raw_model_calls':sum(len(r['calls']) for r in records),'sum_task_wall_seconds':sum(r['total_seconds'] for r in records),'aggregation_invocation_seconds':seconds,
      'metadata':provenance(experiment='agent_revision6_3',inputs={'arm':arm,'tasks':len(records),'variant':'revoked_cheapest','protocol_sha256':protocol['protocol_sha256']},seed=int(load_seeds()['agent_seed']))}
def run(*,phase='main',arm='memory_only',endpoint=None,output=None):
    started=time.perf_counter();protocol=identity();seed=int(load_seeds()['agent_seed']);stub=phase=='stub';provider='stub' if stub else 'ollama';out=Path(output) if output else GEN/('stub_v6_3' if stub else 'v6_3_revoked_cheapest_'+arm)
    out.mkdir(parents=True,exist_ok=True);model=DecisionModel(provider,'qwen2.5:7b',endpoint);signature={'model':'qwen2.5:7b','provider':provider,'protocol':protocol};decision_path=GEN/'sample_decision_v6_3.json'
    if not stub:
        model_identity=json.loads((GEN/'v6_3_revoked_cheapest_memory_only/model_identity.json').read_text());assert model_identity['model_digest']==DIGEST
        signature['runtime']={k:model_identity[k] for k in ('model_digest','server_version')}
        needs_calls=phase=='warmup' and not decision_path.exists() or phase=='main' and any(not (out/f'task_{i:04}.json').exists() for i in range(100))
        if needs_calls:
            with urllib.request.urlopen(model.endpoint+'/api/tags',timeout=30) as response:tags=json.load(response)
            with urllib.request.urlopen(model.endpoint+'/api/version',timeout=30) as response:version=json.load(response)['version']
            assert next(r for r in tags['models'] if r['name']=='qwen2.5:7b')['digest']==DIGEST and version==model_identity['server_version']
    if phase=='warmup':
        if decision_path.exists():
            decision=json.loads(decision_path.read_text());assert decision['signature']==signature;return decision
        receipts=[];pilot=GEN/'v6_3_revoked_cheapest_memory_only/warmup';pilot.mkdir(exist_ok=True)
        for index in range(3):
            for pilot_arm in ARMS:
                path=pilot/f'timing_{index:04}_{pilot_arm}.json'
                if path.exists():receipt=json.loads(path.read_text());assert receipt['signature']==signature
                else:
                    r=run_task(task(index,seed),model,pilot_arm)
                    receipt={'task_index':index,'arm':pilot_arm,'wall_seconds':r['total_seconds'],'calls':len(r['calls']),'signature':signature,'outputs_and_scores_discarded':True,'discarded_output_hashes':[hashlib.sha256(json.dumps(c['raw'],sort_keys=True).encode()).hexdigest() for c in r['calls']]}
                    atom(path,receipt);del r
                receipts.append(receipt);print('Discarded warm-up',index,pilot_arm,f"{receipt['wall_seconds']:.1f}s",flush=True)
        projected={a:100*mean(r['wall_seconds'] for r in receipts if r['arm']==a) for a in ARMS}
        decision={'tasks':100,'task_indices':'0-99','warmup_paired_task_ids':[0,1,2],'warmup_arm_executions':6,'warmup_outputs_discarded':True,'warmup_timings':[{k:r[k] for k in ('task_index','arm','wall_seconds','calls')} for r in receipts],
          'projected_arm_seconds':projected,'projected_combined_seconds':sum(projected.values()),'threshold_seconds':57600,'secondary_eligible':sum(projected.values())<=57600,'decision_utc':now(),'signature':signature}
        atom(decision_path,decision);print('TIMING DECISION',json.dumps({k:v for k,v in decision.items() if k!='signature'}),flush=True);return decision
    decision={'tasks':200,'secondary_eligible':False,'rule':'Separate deterministic schema control','signature':signature} if stub else json.loads(decision_path.read_text())
    if not stub:assert decision['signature']==signature
    if arm=='listed_ids' and not stub and not decision['secondary_eligible']:raise RuntimeError('Secondary arm ineligible under frozen time rule')
    invocation={'started_utc':now(),'arm':arm,'phase':phase,'already_completed_tasks':len(list(out.glob('task_*.json'))),'protocol_sha256':protocol['protocol_sha256']}
    invocation['mode']='cached_validation' if invocation['already_completed_tasks']==decision['tasks'] else ('resume' if invocation['already_completed_tasks'] else 'initial')
    with (out/'invocations.jsonl').open('a') as f:f.write(json.dumps(invocation)+'\n')
    records=[]
    for index in range(decision['tasks']):
        path=out/f'task_{index:04}.json';workload=task(index,seed)
        if path.exists():
            record=json.loads(path.read_text());assert record['signature']==signature and record['task']==json.loads(json.dumps(workload)) and record['arm']==arm
        else:
            journals=out/'call_journals';journals.mkdir(exist_ok=True);attempt=len(list(journals.glob(f'task_{index:04}_attempt_*.jsonl')))+1
            model.journal=None if stub else journals/f'task_{index:04}_attempt_{attempt:03}.jsonl';transport_start=len(model.transport_attempts)
            record={**run_task(workload,model,arm),'signature':signature,'model':'qwen2.5:7b','provider':provider,'attempt':attempt,'transport_attempts':model.transport_attempts[transport_start:]};atom(path,record)
        records.append(record);print(f'{index+1}/{decision["tasks"]} tasks complete ({arm}); wall={record["total_seconds"]:.1f}s',flush=True)
    summary=aggregate(records,arm,provider,protocol,decision,time.perf_counter()-started);atom(out/'summary.json',summary)
    if not (out/'main_execution_summary.json').exists():atom(out/'main_execution_summary.json',summary)
    print('COMPLETE',arm,len(records),flush=True);return summary
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--phase',choices=['warmup','main','stub'],default='main');p.add_argument('--arm',choices=ARMS,default='memory_only');p.add_argument('--endpoint');p.add_argument('--output',type=Path)
    a=p.parse_args();run(phase=a.phase,arm=a.arm,endpoint=a.endpoint,output=a.output)
