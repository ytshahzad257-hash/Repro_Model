"""Verify declared public representations against their distribution receipt."""
from pathlib import Path
import hashlib
import json

ROOT = Path(__file__).resolve().parents[1]
RECEIPT = ROOT / 'results/generated/public_distribution.json'


def digest(path):
    h = hashlib.sha256()
    with path.open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def public_entry(name):
    if not RECEIPT.exists():
        return None
    records = json.loads(RECEIPT.read_text())['changed_files']
    return next((row for row in records if row['path'] == name), None)


def verify_original_or_public(name, expected_original_sha256):
    actual = digest(ROOT / name)
    if actual == expected_original_sha256:
        return False
    row = public_entry(name)
    assert row and row['kind'] == 'workspace-path-redaction', name
    assert row['original_sha256'] == expected_original_sha256, name
    assert row['public_sha256'] == actual, name
    return True


def main():
    receipt = json.loads(RECEIPT.read_text())
    for row in receipt['changed_files']:
        assert digest(ROOT / row['path']) == row['public_sha256'], row['path']
    for name, expected in receipt['frozen_scientific_sources'].items():
        assert digest(ROOT / name) == expected, name
    print(len(receipt['changed_files']), 'public representations verified;',
          len(receipt['frozen_scientific_sources']), 'frozen scientific sources unchanged')


if __name__ == '__main__':
    main()
