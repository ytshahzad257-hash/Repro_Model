"""Trace printed cost denominators to actual saved admission/call slots."""
from pathlib import Path
import json
ROOT=Path(__file__).resolve().parents[1]
def run():
    out=ROOT/'results/generated/agent/v6_2_qwen2_5_7b'
    summary=json.loads((out/'summary.json').read_text());assert summary['complete']
    counts={row['condition']:set() for row in summary['rows']}
    records=sorted(out.glob('task_*.json'));assert len(records)==summary['tasks']
    for path in records:
        for row in json.loads(path.read_text())['conditions']:
            counts[row['condition']].add(len(row['audit_ground_truth']))
    assert all(len(values)==1 for values in counts.values())
    data={'tasks':len(records),'charged_model_calls':{c:next(iter(values)) for c,values in counts.items()},
      'definition':'Every recorded admission slot corresponds to one charged model invocation; shared pre-cut slots are included, counterfactual replays are excluded.',
      'low_ceiling_threshold':.5,'source':'agent/v6_2_qwen2_5_7b/task_*.json'}
    (ROOT/'results/generated/agent/evaluation_metadata_v6_2.json').write_text(json.dumps(data,indent=2)+'\n');return data
if __name__=='__main__':print(run())
