"""Verify immutable earlier runs without reaggregation or rescoring."""
from pathlib import Path
import hashlib,json,sys,inspect
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'src'))
from apr.agent.prototype import Memory,utility
from public_distribution import verify_original_or_public
def main():
    frozen=json.loads((ROOT/'results/generated/agent/earlier_runs_frozen_v6_3.json').read_text())
    redacted=0
    for name,expected in frozen['files'].items():redacted+=verify_original_or_public(name,expected['sha256'])
    assert inspect.getsource(utility)==frozen['utility_source'] and inspect.getsource(Memory.cut)==frozen['memory_cut_source'] and inspect.getsource(Memory.operational)==frozen['memory_operational_source']
    print(len(frozen['files'])-redacted,'earlier files byte-identical;',redacted,'declared metadata path redactions verified; utility/cut/operational source unchanged')
if __name__=='__main__':main()
