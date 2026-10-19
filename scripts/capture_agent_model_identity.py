"""Pin actual local model/runtime identity before preregistered agent inference."""
from pathlib import Path
import argparse,json,hashlib,urllib.request,datetime
ROOT=Path(__file__).resolve().parents[1]
def main():
    p=argparse.ArgumentParser();p.add_argument('--model',default='qwen2.5:7b');p.add_argument('--endpoint',required=True);p.add_argument('--models-dir',type=Path,required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--preregistration-receipt',type=Path,default=ROOT/'results/generated/agent/preregistration_v6_2.json');a=p.parse_args()
    reg=json.loads(a.preregistration_receipt.read_text())
    assert hashlib.sha256((ROOT/reg['path']).read_bytes()).hexdigest()==reg['sha256']
    def get(path,body=None):
        request=urllib.request.Request(a.endpoint+path,data=json.dumps(body).encode() if body else None,headers={'Content-Type':'application/json'})
        with urllib.request.urlopen(request,timeout=60) as response:return json.load(response)
    version=get('/api/version')['version'];tags=get('/api/tags');model=next(r for r in tags['models'] if r['name']==a.model)
    family,tag=a.model.split(':',1);manifest=a.models_dir/'manifests/registry.ollama.ai/library'/family/tag
    raw=manifest.read_bytes();sha=hashlib.sha256(raw).hexdigest();local=json.loads(raw)
    registry_raw=raw
    if sha!=model['digest']:
        # Ollama 0.40 keeps an extended local wrapper and an original-registry
        # manifest layer; its API reports the original registry digest.
        reference='sha256:'+model['digest']
        assert any(row['digest']==reference and row['mediaType']==local['mediaType'] for row in local['layers'])
        registry_raw=(a.models_dir/'blobs'/reference.replace(':','-',1)).read_bytes()
        registry=json.loads(registry_raw)
        assert local['config']==registry['config']
        assert [row for row in local['layers'] if row['mediaType']!=local['mediaType']]==registry['layers']
    assert hashlib.sha256(registry_raw).hexdigest()==model['digest']
    identity={'model':a.model,'model_digest':model['digest'],'manifest_sha256':sha,'server_version':version,'details':model['details'],'captured_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'preregistration_sha256':reg['sha256'],'source':'https://ollama.com/library/'+a.model}
    a.output.mkdir(parents=True,exist_ok=True);path=a.output/'model_identity.json'
    if path.exists():
        before=json.loads(path.read_text())
        assert all(before[k]==identity[k] for k in ('model','model_digest','manifest_sha256','server_version')),'Existing identity differs; preserve the run'
        print('Existing pinned identity verified');return
    (a.output/'model_manifest.json').write_bytes(raw)
    (a.output/'model_registry_manifest.json').write_bytes(registry_raw)
    (a.output/'model_information.json').write_text(json.dumps(get('/api/show',{'model':a.model}),indent=2)+'\n')
    path.write_text(json.dumps(identity,indent=2)+'\n')
    print(json.dumps(identity))
if __name__=='__main__':main()
