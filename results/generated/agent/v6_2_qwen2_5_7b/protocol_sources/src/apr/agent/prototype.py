"""Confined model adapter and explicitly labelled synthetic memory runtime."""
from __future__ import annotations
import json,os,re,time,urllib.request
from dataclasses import dataclass

@dataclass(frozen=True)
class Item:
    identifier:str
    kind:str
    payload:str
    labels:frozenset[str]

class Model:
    def __init__(self,provider='ollama',model='qwen2.5:0.5b',endpoint=None):
        self.provider=provider;self.model=model
        self.endpoint=endpoint or os.environ.get('OLLAMA_HOST','http://127.0.0.1:11434')
        if not self.endpoint.startswith('http'):self.endpoint='http://'+self.endpoint
        self.calls=[]
    def generate(self,prompt,*,seed,kind,max_tokens=64):
        started=time.perf_counter()
        if self.provider=='stub':
            quotes=re.findall(r'(S\d+): price (\$[\d,.]+); code ([\w-]+)',prompt)
            if kind=='plan':
                q=min(quotes,key=lambda q:float(q[1][1:].replace(',',''))) if quotes else None
                answer=json.dumps({'supplier':q[0],'price':q[1]}) if q else '{}'
            else:answer='; '.join(f'{i} {p} {c}' for i,p,c in quotes)
            raw={'response':answer,'model':'deterministic-quote-copy-stub','prompt_eval_count':len(prompt.split()),'eval_count':len(answer.split())}
        elif self.provider=='ollama':
            body={'model':self.model,'prompt':prompt,'stream':False,'keep_alive':'30m',
                  'options':{'temperature':0,'seed':seed,'num_predict':max_tokens,'num_ctx':4096}}
            req=urllib.request.Request(self.endpoint+'/api/generate',data=json.dumps(body).encode(),headers={'Content-Type':'application/json'})
            with urllib.request.urlopen(req,timeout=180) as response:raw=json.load(response)
            if 'error' in raw:raise RuntimeError(raw['error'])
            answer=raw['response']
        elif self.provider=='anthropic':
            key=os.environ.get('ANTHROPIC_API_KEY')
            if not key:raise RuntimeError('ANTHROPIC_API_KEY is not configured')
            body={'model':self.model,'max_tokens':max_tokens,'temperature':0,'messages':[{'role':'user','content':prompt}]}
            req=urllib.request.Request('https://api.anthropic.com/v1/messages',data=json.dumps(body).encode(),
                 headers={'Content-Type':'application/json','x-api-key':key,'anthropic-version':'2023-06-01'})
            with urllib.request.urlopen(req,timeout=180) as response:raw=json.load(response)
            answer=''.join(x.get('text','') for x in raw['content'])
            raw['prompt_eval_count']=raw['usage']['input_tokens'];raw['eval_count']=raw['usage']['output_tokens']
        else:raise ValueError(self.provider)
        elapsed=time.perf_counter()-started
        self.calls.append({'kind':kind,'seed':seed,'max_tokens':max_tokens,'prompt':prompt,
                           'response':answer,'seconds':elapsed,'raw':raw})
        return answer

class Memory:
    def __init__(self,items):
        self.items=list(items);self.private=[];self.ledger=[];self.trace=[];self.recording=True
        self.events=[];self.audit_order=None;self.revoked=frozenset();self.label_seconds=0.0
    def admitted(self,items,slot):
        begin=time.perf_counter();labels=frozenset(t for x in items for t in x.labels)
        event={'slot':slot,'sources':sorted(labels)}
        self.trace.append(dict(event))
        if self.recording:self.ledger.append(dict(event))
        self.label_seconds+=time.perf_counter()-begin
        return labels
    def derive(self,model,kind,items,seed,slot):
        labels=self.admitted(items,slot)
        prompt='Fictional procurement records:\n'+'\n'.join(x.payload for x in items)
        if kind=='summary':prompt+='\nSummarize each quote with its supplier, exact price and code. Be concise.'
        else:prompt+='\nChoose the cheapest quote. Return JSON only with supplier and exact price.'
        text=model.generate(prompt,seed=seed,kind=kind,max_tokens=160 if kind=='summary' else 64)
        item=Item(slot,kind,text,labels);self.items.append(item);return item
    def cut(self,revoked,condition,order):
        begin=time.perf_counter();self.revoked=frozenset(revoked)
        self.events=['RequestRevoke','UpdatePolicy']+list(order)+['Persist','CommitCut']
        if condition!='SourceOnly':
            unsafe=[x for x in self.items if x.labels & self.revoked]
            self.items=[x for x in self.items if not x.labels & self.revoked]
            if condition!='DeleteAll':self.private=unsafe
        self.audit_order=list(self.events)
        if condition=='DeleteAll':self.ledger=[];self.recording=False;self.audit_order=None
        self.label_seconds+=time.perf_counter()-begin
    def operational(self,condition):
        if condition!='SourceOnly':assert all(not x.labels & self.revoked for x in self.items)
        return list(self.items)
    def approved_finding(self,price):
        # Nonconstant approved one-bit disclosure, with separate provenance.
        payload='Approved review finding: price exceeded 50000 = '+str(price>50000)
        self.items.append(Item('approved-view','release',payload,frozenset()))
        return {'payload':payload,'source_tags':sorted(self.revoked),'approved':True,'epoch':1}

def leakage(text,price,code):
    exact=(price in text or code in text)
    numbers=[]
    for token in re.findall(r'(?<!\w)\$?\d[\d,]*(?:\.\d+)?',text):
        try:numbers.append(float(token.replace('$','').replace(',','')))
        except ValueError:pass
    amount=float(price.replace('$','').replace(',',''))
    fuzzy=code.casefold() in text.casefold() or any(abs(x-amount)<=0.01*amount for x in numbers)
    return exact,fuzzy

def utility(text,allowed):
    if not allowed:return False
    cheapest=min(allowed,key=lambda d:d['amount'])
    try:
        data=json.loads(re.search(r'\{.*\}',text,re.S).group())
        cost=float(str(data.get('price','')).replace('$','').replace(',',''))
        return data.get('supplier')==cheapest['supplier'] and abs(cost-cheapest['amount'])<0.005
    except (ValueError,AttributeError,TypeError):return False
