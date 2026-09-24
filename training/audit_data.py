"""Audit dataset counts, grouping and supported labels without downloading models."""
import json,hashlib,collections
from common import ROOT,load,report
result={}
labels=set(json.loads((ROOT/'training/data/labels.json').read_text()))
for name in ['intake','layouts','code']:
    rows,digest=load(name+'.jsonl');ids=[r['id'] for r in rows]
    assert len(ids)==len(set(ids)),name+' duplicate IDs'
    if name=='intake':
        for r in rows:
            assert set(r['labels'])<=labels
            expected={f"business:{r['business_type']}",f"style:{r['style']}"}|{'page:'+p for p in r['pages']}|{'feature:'+f for f in r['features']}
            assert set(r['labels'])==expected,r['id']+' label mismatch'
    field={'intake':'text','layouts':None,'code':'code'}[name]
    splits=collections.defaultdict(set)
    for r in rows:
        text=r[field] if field else json.dumps({k:r[k] for k in ['business','page','style','density']},sort_keys=True)
        digest_text=hashlib.sha256(' '.join(text.split()).encode()).hexdigest();splits[digest_text].add(r['split'])
    leaked=sum(len(v)>1 for v in splits.values())
    result[name]={'rows':len(rows),'groups':len(set(r['group_id'] for r in rows)),'splits':dict(collections.Counter(r['split'] for r in rows)),'unreviewed':sum(not r.get('reviewed') for r in rows),'cross_split_exact_duplicates':leaked,'sha256':digest}
    assert not leaked,f'{name}: exact duplicates across splits'
report(ROOT/'training/data/audit.json',result)
print(json.dumps(result,indent=2))
