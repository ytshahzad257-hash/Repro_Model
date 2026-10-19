"""Run TLC on the K-parametric TLA+ specification for every configuration.

For each configuration and K = 1..4 this performs six TLC runs:
  * single copy, secret 0 and 1, without invariants (exact state and
    "states generated" counts);
  * single copy, secret 0 and 1, with InfoSafe, AuthSafe, ReviewPossible and
    -continue (verdicts);
  * self-composition product without properties (exact product count) and
    with the ObsEqual and PayloadEqual action properties (verdicts).
Usage:  TLA2TOOLS_JAR=/path/tla2tools.jar python scripts/tlc_matrix.py [--jobs N]
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
import time
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SPEC = ROOT / "tla" / "v5"
OUT = ROOT / "results" / "generated" / "tlc_matrix.json"
LOGS = ROOT / "results" / "logs" / "tlc"
sys.path.insert(0, str(ROOT / "experiments"))
from finite_cases import cases
GEN = re.compile(r"([\d,]+) states generated, ([\d,]+) distinct states found, 0 states left on queue")
VERSION = re.compile(r"TLC2 Version (\S+)")


def compact_log(log: str) -> str:
    """Keep the TLC header, one line per distinct error and the final statistics.

    Runs with -continue print every violating trace, which can reach gigabytes;
    the verdict only needs the names of the violated properties.
    """

    lines = [line for line in log.splitlines() if not line.startswith("Picked up JAVA_TOOL_OPTIONS")]
    errors: dict[str, int] = {}
    for line in lines:
        if line.startswith("Error: "):
            errors[line] = errors.get(line, 0) + 1
    if len(lines) <= 200:
        return "\n".join(lines) + "\n"
    head, tail = lines[:40], lines[-30:]
    summary = [f"[compacted] {count} x {line}" for line, count in errors.items()]
    return "\n".join(head + ["[compacted] ... violation traces elided ..."] + summary + tail) + "\n"


def tlc(jar: str, module: str, cfg_text: str, name: str, extra: list[str]) -> dict[str, object]:
    work = Path(tempfile.mkdtemp(prefix="tlc_"))
    for file in SPEC.glob("*.tla"):
        shutil.copy(file, work / file.name)
    (work / "MC.cfg").write_text(cfg_text, encoding="utf-8")
    command = ["java", "-XX:+UseParallelGC", "-cp", jar, "tlc2.TLC", "-workers", "1", "-deadlock", *extra,
               "-metadir", str(work / "meta"), "-config", "MC.cfg", module]
    started = time.perf_counter()
    done = subprocess.run(command, cwd=work, text=True, capture_output=True)
    seconds = time.perf_counter() - started
    log = done.stdout + "\n" + done.stderr
    LOGS.mkdir(parents=True, exist_ok=True)
    (LOGS / f"{name}.log").write_text(compact_log(log), encoding="utf-8")
    shutil.rmtree(work, ignore_errors=True)
    match = GEN.search(log)
    version = VERSION.search(log)
    violated = sorted(set(re.findall(r"Error: (?:Invariant|Action property) (\w+) is violated", log)))
    benign = re.compile(r"^Error: ((Invariant|Action property) \w+ is violated|The behavior up to this point is:)")
    unexpected = [line for line in log.splitlines() if line.startswith("Error:") and not benign.match(line)]
    return {
        "name": name,
        "returncode": done.returncode,
        "generated": int(match.group(1).replace(",", "")) if match else None,
        "distinct": int(match.group(2).replace(",", "")) if match else None,
        "violated": violated,
        "seconds": round(seconds, 3),
        "tlc_version": version.group(1) if version else None,
        "completed": bool(match),
        "unexpected_errors": unexpected[:5],
        # A run is valid if it explored the full state space without unexpected
        # errors, or if it stopped only because a checked property was violated.
        "valid": not unexpected and (bool(match) or (bool(violated) and done.returncode != 0)),
    }


def configs(case):
    revoked="{"+", ".join(str(i+1) for i in case['revoked'])+"}"
    return (f'CONSTANTS K = {case["sources"]}\nCFG = "{case["configuration"]}"\n'
            f'MODE = "{case["secrets"]}"\nREVOKED = {revoked}\nCACHE = TRUE\n')


def jobs_for(jar, selected):
    jobs=[]
    for c in selected:
        base=configs(c); name=c['case_id'].replace('/','_')
        for side in ('left','right'):
            single=base+f'SECRET = {c[side]}\nSPECIFICATION Spec\n'
            jobs.append((jar,'APR.tla',single,f'{name}_{side}_count',[]))
            # Each invariant stops at its first counterexample. This avoids
            # retaining/printing tens of thousands of redundant error traces.
            for inv in ('InfoSafe','AuthSafe','ReviewPossible'):
                jobs.append((jar,'APR.tla',single+f'INVARIANT {inv}\n',f'{name}_{side}_{inv}',[]))
        for equal in (False,True):
            mode='equal_release' if equal else 'product'
            product=base+f'LEFT = {c["left"]}\nRIGHT = {c["right"]}\nEQRELEASE = {str(equal).upper()}\nSPECIFICATION Spec\n'
            jobs.append((jar,'APRProduct.tla',product,f'{name}_{mode}_count',[]))
            jobs.append((jar,'APRProduct.tla',product+'INVARIANT EnabledEqual\nPROPERTY ObsEqual\n',f'{name}_{mode}_ObsEqual',[]))
            if not equal:
                jobs.append((jar,'APRProduct.tla',product+'PROPERTY PayloadEqual\n',f'{name}_{mode}_PayloadEqual',[]))
    return jobs


def run(selected,jobs_count=2):
    jar=os.environ.get('TLA2TOOLS_JAR')
    if not jar or not Path(jar).is_file():raise RuntimeError('Set TLA2TOOLS_JAR')
    jobs=jobs_for(jar,selected)
    print(f'Running {len(jobs)} TLC jobs with {jobs_count} concurrent jobs',flush=True)
    with ThreadPoolExecutor(max_workers=jobs_count) as pool:
        runs=[]
        for i,r in enumerate(pool.map(lambda job:tlc(*job),jobs),1):
            runs.append(r)
            if i%13==0:print(f'{i}/{len(jobs)} jobs complete',flush=True)
    by={r['name']:r for r in runs};rows=[]
    for c in selected:
        name=c['case_id'].replace('/','_')
        get=lambda suffix:by[f'{name}_{suffix}']
        l,r=get('left_count'),get('right_count'); pc=get('product_count');eq=get('equal_release_count')
        invariant={inv:any(inv in get(f'{side}_{inv}')['violated'] for side in ('left','right'))
                   for inv in ('InfoSafe','AuthSafe','ReviewPossible')}
        relevant=[run for run in runs if run['name'].startswith(name+'_')]
        count_runs=[l,r,pc,eq]
        equal_initials=2 if c['configuration']=='ApprovedSecretRelease' and c['left']!=c['right'] else 1
        sub=lambda r,n:None if r['generated'] is None else r['generated']-n
        rows.append({**c,'state_count_s0':l['distinct'],'state_count_s1':r['distinct'],
            'transitions_s0':sub(l,1),'transitions_s1':sub(r,1),
            'product_states':pc['distinct'],'product_transitions':sub(pc,1),
            'equal_release_product_states':eq['distinct'],'equal_release_product_transitions':sub(eq,equal_initials),
            'information_safety':'violated' if invariant['InfoSafe'] else 'holds',
            'authorization_safety':'violated' if invariant['AuthSafe'] else 'holds',
            'review_possible':'violated' if invariant['ReviewPossible'] else 'holds',
            'synchronous_observations':'differ' if get('product_ObsEqual')['violated'] else 'equal',
            'payload_only':'differ' if get('product_PayloadEqual')['violated'] else 'equal',
            'equal_release_observations':'differ' if get('equal_release_ObsEqual')['violated'] else 'equal',
            'tlc_seconds_s0_count':l['seconds'],
            'all_runs_completed':all(r['completed'] for r in count_runs) and all(r['valid'] for r in relevant)})
    doc={'status':'completed' if all(r['all_runs_completed'] for r in rows) else 'FAIL',
         'rows':rows,'runs':len(runs),'run_details':runs,
         'tlc_versions':sorted({r['tlc_version'] for r in runs if r['tlc_version']}),
         'java':subprocess.run(['java','-version'],capture_output=True,text=True).stderr.splitlines()[-3:]}
    OUT.parent.mkdir(parents=True,exist_ok=True);OUT.write_text(json.dumps(doc,indent=2)+'\n')
    print(doc['status'],len(rows),'cases',len(runs),'TLC jobs',flush=True)
    return doc

if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('--jobs',type=int,default=2)
    p.add_argument('--max-k',type=int,default=4);p.add_argument('--no-independent',action='store_true')
    p.add_argument('--no-larger',action='store_true');p.add_argument('--case')
    a=p.parse_args();selected=cases(a.max_k,not a.no_independent,not a.no_larger)
    if a.case:selected=[c for c in selected if c['case_id']==a.case]
    result=run(selected,a.jobs);raise SystemExit(0 if result['status']=='completed' else 1)
