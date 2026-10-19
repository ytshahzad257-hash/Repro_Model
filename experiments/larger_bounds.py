"""Measured Experiment C with an explicit elapsed-time and RSS budget."""
from __future__ import annotations
import argparse,json,os,platform,subprocess,sys,time
from common import GENERATED,ROOT,provenance,write_json

def run(seconds=300,memory_mb=3072):
    code="""import json,resource,time
from apr.question_bounds import compute
t=time.perf_counter()
try:
 r=compute(4).as_row()
 print(json.dumps({'status':'complete','row':r,'seconds':time.perf_counter()-t,'maxrss_native':resource.getrusage(resource.RUSAGE_SELF).ru_maxrss}),flush=True)
except MemoryError:
 print(json.dumps({'status':'memory_error','seconds':time.perf_counter()-t}),flush=True)
"""
    start=time.perf_counter();peak=0;status=None
    process=subprocess.Popen([sys.executable,'-c',code],cwd=ROOT,env={**os.environ,'PYTHONPATH':str(ROOT/'src')},stdout=subprocess.PIPE,stderr=subprocess.PIPE,text=True)
    while process.poll() is None:
        try:rss=int(subprocess.check_output(['ps','-o','rss=','-p',str(process.pid)],text=True).strip())*1024
        except (OSError,ValueError,subprocess.CalledProcessError):rss=0
        peak=max(peak,rss)
        if rss>memory_mb*1024**2:status='rss_limit';process.terminate();break
        if time.perf_counter()-start>seconds:status='time_limit';process.terminate();break
        time.sleep(.25)
    out,err=process.communicate();(GENERATED/'larger_bounds_raw.log').write_text(out+err)
    row={'status':status or 'process_error','returncode':process.returncode}
    if not status and process.returncode==0:
        row=json.loads(out.strip().splitlines()[-1]);native=row.pop('maxrss_native',0)
        peak=max(peak,native if platform.system()=='Darwin' else native*1024)
    doc={**row,'wall_seconds':time.perf_counter()-start,'peak_rss_bytes':peak,'sources':4,'time_limit_seconds':seconds,'rss_limit_mb':memory_mb,
         'metadata':provenance(experiment='larger_question_bounds_revision6',inputs={'K':4,'seconds':seconds,'rss_limit_mb':memory_mb})}
    write_json(GENERATED/'larger_bounds.json',doc);print(json.dumps(doc),flush=True);return doc
if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--seconds',type=int,default=300);p.add_argument('--memory-mb',type=int,default=3072);a=p.parse_args();run(a.seconds,a.memory_mb)
