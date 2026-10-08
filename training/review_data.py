"""Record a bounded dataset review"""
import json,re,hashlib,collections,shutil
from pathlib import Path
root=Path(__file__).resolve().parents[1];data=root/'training/data'
labels=json.loads((data/'labels.json').read_text())
pages=[x.split(':',1)[1] for x in labels if x.startswith('page:')]
features=[x.split(':',1)[1] for x in labels if x.startswith('feature:')]
backup=root/'tmp/dataset-before-review';backup.mkdir(parents=True,exist_ok=True)
summary={}
for name in ['intake','layouts','code']:
 path=data/(name+'.jsonl')
 if not (backup/path.name).exists():shutil.copy2(path,backup/path.name)
 rows=[json.loads(x) for x in path.read_text(encoding='utf-8').splitlines() if x.strip()]
 for row in rows:
  issues=[];checks=[]
  if name=='intake':
   text=row['text'];positive=text
   if row.get('excluded_pages'):
    negative=(', '.join(row['excluded_pages'])+' screens mat add karna.') if row['language']=='roman_ur' else ('Do not add '+', '.join(row['excluded_pages'])+' screens.')
    if not text.endswith(negative):issues.append('Exclusion phrase needs manual interpretation')
    else:positive=text[:-len(negative)]
   found={p for p in pages if re.search(r'\b'+re.escape(p)+r'\b',positive)}
   if found!=set(row['pages']):issues.append('Screen labels do not match explicit positive screen names')
   for field in ['business_type','style']:
    if not re.search(r'\b'+re.escape(row[field])+r'\b',positive):issues.append(field+' absent from prompt')
   found_features={f for f in features if re.search(r'\b'+re.escape(f)+r'\b',positive)}
   if found_features!=set(row['features']):issues.append('Feature labels do not match explicit terms')
   if set(row.get('excluded_pages',[])) & set(row['pages']):issues.append('Excluded screen included')
   expected={f"business:{row['business_type']}",f"style:{row['style']}"}|{'page:'+p for p in row['pages']}|{'feature:'+f for f in row['features']}
   if set(row['labels'])!=expected or not expected<=set(labels):issues.append('Invalid label schema')
   checks=['explicit prompt-to-label consistency','exclusion consistency','label vocabulary']
   row['reviewed']=not issues
   scope='Template-constrained label consistency. Not human authorship, linguistic certification or real-world evaluation.'
  elif name=='layouts':
   expected='cards' if row['page'] in ['cart','checkout'] else {'minimal':'grid','luxury':'editorial','playful':'cards'}.get(row['style'])
   if row['template_id']!=expected:issues.append('Rule mismatch')
   checks=['declared layout-rule consistency']
   issues.append('No independent human design-quality judgement')
   if row.get('replica_of'):issues.append('Repeated model-input record')
   row['reviewed']=False
   scope='Rule consistency only; design quality remains unreviewed.'
  else:
   checks=['record structure inspected']
   issues.append('Component behaviour and description-to-code acceptance tests pending')
   if row.get('variant_of'):issues.append('Description depends on an unspecified base component')
   row['reviewed']=False
   scope='No functional approval; prior JSX syntax checks are not behavioural validation.'
  row['review']={'reviewer':'assistant-assisted rule audit','human_reviewed':False,'scope':scope,'checks':checks,'issues':issues}
 path.write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
 summary[name]={'records':len(rows),'reviewed':sum(r['reviewed'] for r in rows),'pending':sum(not r['reviewed'] for r in rows),'issues':dict(collections.Counter(i for r in rows for i in r['review']['issues']))}
(data/'review_report.json').write_text(json.dumps(summary,indent=2)+'\n',encoding='utf-8')
print(json.dumps(summary,indent=2))
