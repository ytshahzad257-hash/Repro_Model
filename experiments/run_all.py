"""Revision 6.3 reproduction, including all experiment groups.

Full: TLA2TOOLS_JAR=... OLLAMA_HOST=... python experiments/run_all.py
Fast: python experiments/run_all.py --fast  # reuses the full finite/local-model records
Use --dry-run to regenerate stub controls without an API key or model service.
"""
from __future__ import annotations
import argparse,json,os,subprocess,sys,time
from concurrent.futures import ThreadPoolExecutor,as_completed
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT/'src'),str(ROOT/'experiments'),str(ROOT/'scripts')]
from common import GENERATED,ensure_outputs,provenance,write_json

def execute(name,command):
    start=time.perf_counter();log=ROOT/'results/logs/reproduction'/(''.join(c if c.isalnum() else '_' for c in name)+'.log')
    log.parent.mkdir(parents=True,exist_ok=True)
    env={**os.environ,'PYTHONPATH':str(ROOT/'src'),'PYTHONUNBUFFERED':'1'}
    with log.open('w') as stream:done=subprocess.run(command,cwd=ROOT,env=env,text=True,stdout=stream,stderr=subprocess.STDOUT)
    row={'step':name,'status':'PASS' if done.returncode==0 else 'FAIL','seconds':round(time.perf_counter()-start,3),'log':str(log.relative_to(ROOT)),'command':command}
    print(f"[{row['status']}] {name} ({row['seconds']:.1f}s)",flush=True);return row

def main():
    p=argparse.ArgumentParser();p.add_argument('--fast',action='store_true');p.add_argument('--dry-run',action='store_true');p.add_argument('--jobs',type=int,default=2)
    p.add_argument('--provider',choices=['ollama'],default='ollama');p.add_argument('--tasks',type=int,default=None,help='Optional assertion of the preselected sample size; never overrides the timing rule');p.add_argument('--model',default='qwen2.5:7b');p.add_argument('--endpoint')
    a=p.parse_args();ensure_outputs();py=sys.executable;statuses=[];tlc_mode='REUSED saved TLC records' if a.fast or not os.environ.get('TLA2TOOLS_JAR') else 'rerun in this invocation'
    if a.model!='qwen2.5:7b' or a.tasks not in (None,100):raise RuntimeError('Revision 6.3 fixes qwen2.5:7b and 100 primary tasks; a new design needs its own preregistration')
    agent_mode='stub only; reported local-model records reused' if a.fast or a.dry_run else 'preregistered local run resumed from matching per-task records'
    # A full run fails if required external dependencies are absent. Fast mode
    # is explicitly a reuse/smoke mode, never represented as fresh full evidence.
    if not a.fast and not os.environ.get('TLA2TOOLS_JAR'):raise RuntimeError('Full reproduction requires TLA2TOOLS_JAR; use --fast for an explicit smoke/reuse run')
    statuses.append(execute('Unit tests',[py,'-m','pytest','-q']))
    jobs=[]
    if not a.fast:
        jobs += [('Finite Python matrix',[py,'experiments/model_matrix.py']),('TLC matrix',[py,'scripts/tlc_matrix.py','--jobs',str(a.jobs)]),
                 ('Evidence bounds',[py,'experiments/question_bounds.py']),('Larger evidence bounds',[py,'experiments/larger_bounds.py']),
                 ('Sufficiency',[py,'experiments/reproduce_table6.py']),('Skew and correlated robustness',[py,'experiments/quarantine_robustness.py'])]
    else:statuses.append({'step':'Finite matrix, bounds and sufficiency','status':'REUSED','seconds':0,'log':'committed generated records'})
    quarantine=[py,'-c',"import sys;sys.path[:0]=['src','experiments'];from reproduce_table7 import run;run(workflows_per_setting="+('100' if a.fast else '2000')+")"]
    jobs += [('Uniform quarantine',quarantine),('Cache controls',[py,'experiments/cache_controls.py'])]
    phase='stub' if a.fast or a.dry_run else 'main'
    agent=[py,'experiments/agent/run_agent_v6_3.py','--phase',phase]
    if a.endpoint:agent+=['--endpoint',a.endpoint]
    if phase=='main':
        warm=[py,'experiments/agent/run_agent_v6_3.py','--phase','warmup']
        if a.endpoint:warm+=['--endpoint',a.endpoint]
        statuses.append(execute('Predeclared timing decision',warm))
        if statuses[-1]['status']!='PASS':return 1
        if a.tasks is not None:
            chosen=json.loads((GENERATED/'agent/sample_decision_v6_3.json').read_text())['tasks']
            if a.tasks!=chosen:raise RuntimeError('--tasks differs from the immutable timing decision')
    jobs.append(('Preregistered agent experiment',agent))
    # Independent result families have separate files. Bound aggregation runs
    # again after its larger computation to avoid an ordering dependency.
    with ThreadPoolExecutor(max_workers=4) as pool:
        futures=[pool.submit(execute,n,c) for n,c in jobs]
        for future in as_completed(futures):statuses.append(future.result())
    follow=[('Bounds aggregation',[py,'experiments/question_bounds.py']),('Configuration results',[py,'experiments/reproduce_table4.py']),
            ('Scaling results',[py,'experiments/reproduce_table5.py']),('Python/TLC cross-check',[py,'scripts/cross_checkers.py']),
            ('Expected-value regression',[py,'scripts/check_expected.py'])]
    # Keep the stub as a separate control in a normal model invocation.
    if not a.fast and not a.dry_run:
        if json.loads((GENERATED/'agent/sample_decision_v6_3.json').read_text())['secondary_eligible']:
            secondary=[py,'experiments/agent/run_agent_v6_3.py','--phase','main','--arm','listed_ids']
            if a.endpoint:secondary+=['--endpoint',a.endpoint]
            follow.append(('Optional descriptive arm',secondary))
        follow.append(('Revision 6.3 stub control',[py,'experiments/agent/run_agent_v6_3.py','--phase','stub']))
    follow += [('Earlier immutable runs',[py,'scripts/verify_earlier_runs_v6_3.py']),('Result plots',[py,'experiments/paper_figures.py'])]
    for name,command in follow:statuses.append(execute(name,command))
    mode='SMOKE / REUSED EVIDENCE' if a.fast or a.dry_run else 'FULL'
    write_json(GENERATED/'REPRODUCTION_REPORT.metadata.json',{'mode':mode,'steps':statuses,'tlc':tlc_mode,'agent':agent_mode,'metadata':provenance(experiment='run_all_revision6_3',inputs=vars(a))})
    lines=['# Reproduction report','',f'Mode: **{mode}**.',f'TLC results: **{tlc_mode}**.',f'Agent results: {agent_mode}.','',
           'Per-task model records are resumable; existing records are retained and new tasks use the recorded model and seeds.','',
           '| Step | Status | Seconds | Log |','| --- | --- | ---: | --- |']
    lines += [f"| {r['step']} | {r['status']} | {r['seconds']} | {r['log']} |" for r in statuses]
    (GENERATED/'REPRODUCTION_REPORT.md').write_text('\n'.join(lines)+'\n')
    # Last mutation after the report and generated data/plots.
    manifest=subprocess.run([py,'scripts/build_manifest.py'],cwd=ROOT,check=False)
    return 0 if manifest.returncode==0 and all(r['status'] in {'PASS','REUSED'} for r in statuses) else 1
if __name__=='__main__':raise SystemExit(main())
