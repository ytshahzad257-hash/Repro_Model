"""Verify the final artifact hashes; a mismatch is a failing exit status."""
from pathlib import Path
from build_manifest import ROOT,digest

def main():
    rows=(ROOT/'artifact/CHECKSUMS.txt').read_text().splitlines();bad=[]
    for row in rows:
        checksum,name=row.split('  ',1);path=ROOT/name
        if not path.is_file() or digest(path)!=checksum:bad.append(name)
    print(f'{len(rows)} entries verified; {len(bad)} mismatches')
    for name in bad:print(name)
    return bool(bad)
if __name__=='__main__':raise SystemExit(main())
