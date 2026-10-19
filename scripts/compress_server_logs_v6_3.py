"""Losslessly compress requested server logs with original-hash receipts."""
from pathlib import Path
import gzip,hashlib,json,datetime,shutil,argparse
from public_distribution import public_entry
ROOT=Path(__file__).resolve().parents[1];RECEIPT=ROOT/'results/generated/server_log_compression_v6_3.json'
def digest_stream(stream):
    h=hashlib.sha256()
    for block in iter(lambda:stream.read(1024*1024),b''):h.update(block)
    return h.hexdigest()
def digest(path):
    with path.open('rb') as f:return digest_stream(f)
def main():
    p=argparse.ArgumentParser();p.add_argument('--new-log',type=Path);a=p.parse_args()
    records=json.loads(RECEIPT.read_text())['logs'] if RECEIPT.exists() else []
    paths=[ROOT/'results/logs/agent_v6_2/ollama_server.log']
    if a.new_log:paths.append(a.new_log.resolve())
    for path in paths:
        if not path.exists():continue
        if path.stat().st_size<=20_000_000:continue
        name=str(path.relative_to(ROOT));compressed=path.with_suffix(path.suffix+'.gz');assert not compressed.exists()
        original_sha=digest(path);original_bytes=path.stat().st_size
        # Save original identity before compressing or removing the plain log.
        record={'original_path':name,'original_sha256':original_sha,'original_bytes':original_bytes,'compression_started_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status':'original_identity_saved'}
        records.append(record);RECEIPT.write_text(json.dumps({'logs':records},indent=2)+'\n')
        with path.open('rb') as src,compressed.open('wb') as dst:
            with gzip.GzipFile(filename='',mode='wb',fileobj=dst,mtime=0) as z:shutil.copyfileobj(src,z)
        with gzip.open(compressed,'rb') as f:assert digest_stream(f)==original_sha
        record.update(compressed_path=str(compressed.relative_to(ROOT)),compressed_sha256=digest(compressed),compressed_bytes=compressed.stat().st_size,decompression_identity_verified=True,status='PASS')
        RECEIPT.write_text(json.dumps({'logs':records},indent=2)+'\n');path.unlink()
    for record in records:
        if record['status']=='PASS':
            expected=record['original_sha256'];public=public_entry(record['compressed_path'])
            if public:
                assert public['kind']=='workspace-path-redaction'
                assert public['original_sha256']==record['compressed_sha256']
                assert public['original_plain_sha256']==expected
                assert digest(ROOT/record['compressed_path'])==public['public_sha256']
                expected=public['public_plain_sha256']
            with gzip.open(ROOT/record['compressed_path'],'rb') as f:assert digest_stream(f)==expected
    print(json.dumps({'logs':records},indent=2))
if __name__=='__main__':main()
