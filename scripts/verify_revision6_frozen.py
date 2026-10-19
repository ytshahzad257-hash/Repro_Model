"""Verify original Revision 6 model/stub/diagnostic records remain byte-identical."""
from pathlib import Path
import hashlib,json,inspect,sys
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from apr.agent.prototype import utility

def main():
    frozen=json.loads((ROOT/'results/generated/agent/revision6_frozen_hashes.json').read_text());bad=[]
    for name,expected in frozen['files'].items():
        path=ROOT/name
        if not path.is_file() or hashlib.sha256(path.read_bytes()).hexdigest()!=expected['sha256']:bad.append(name)
    if inspect.getsource(utility)!=frozen['utility_source']:bad.append('primary utility predicate source')
    print(f'{len(frozen["files"])} original files checked; {len(bad)} changes; primary predicate unchanged={inspect.getsource(utility)==frozen["utility_source"]}')
    for name in bad:print(name)
    return bool(bad)
if __name__=='__main__':raise SystemExit(main())
