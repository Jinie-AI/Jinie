import json, hashlib
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
def load(name):
    path=ROOT/'training/data'/name
    rows=[json.loads(line) for line in path.read_text(encoding='utf-8').splitlines() if line.strip()]
    groups={s:{r['group_id'] for r in rows if r['split']==s} for s in ['train','validation','test']}
    assert not groups['train']&groups['validation'] and not groups['train']&groups['test'] and not groups['validation']&groups['test'],'Group leakage'
    assert all(groups.values()),'All three splits are required'
    return rows,hashlib.sha256(path.read_bytes()).hexdigest()
def report(path,data):
    path.parent.mkdir(parents=True,exist_ok=True);path.write_text(json.dumps(data,indent=2,ensure_ascii=False))
