"""Verify finite semantics/cases/expected snapshot match sealed version 6."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[1]
def main():
    data=json.loads((ROOT/'results/generated/finite_preservation_6_2.json').read_text());bad=[]
    for row in data['files']:
        if hashlib.sha256((ROOT/row['path']).read_bytes()).hexdigest()!=row['revision6_sha256']:bad.append(row['path'])
    print(f"{len(data['files'])} finite source/case/expectation files checked; {len(bad)} changes")
    return bool(bad)
if __name__=='__main__':raise SystemExit(main())
