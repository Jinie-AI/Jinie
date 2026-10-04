"""Expand existing synthetic datasets without changing model label vocabularies.
Run once against the starter data; a second run is a no-op. No models are trained.
"""
import collections, hashlib, itertools, json, random, re, shutil
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'training/data'
rng=random.Random(20261004)
def read(name):return [json.loads(s) for s in (DATA/(name+'.jsonl')).read_text(encoding='utf-8').splitlines() if s.strip()]
def write(name,rows):
 assert len({r['id'] for r in rows})==len(rows)
 (DATA/(name+'.jsonl')).write_text(''.join(json.dumps(r,ensure_ascii=False)+'\n' for r in rows),encoding='utf-8')
def split(key):
 v=int(hashlib.sha256(str(key).encode()).hexdigest()[:8],16)%10
 return 'train' if v<8 else 'validation' if v==8 else 'test'
labels=json.loads((DATA/'labels.json').read_text())
businesses=[s.split(':')[1] for s in labels if s.startswith('business:')]
pages=[s.split(':')[1] for s in labels if s.startswith('page:')]
styles=[s.split(':')[1] for s in labels if s.startswith('style:')]
backup=ROOT/'tmp/dataset-backup-before-2000'
if not backup.exists():
 backup.mkdir(parents=True)
 for name in ['intake.jsonl','layouts.jsonl','code.jsonl','audit.json']:shutil.copy2(DATA/name,backup/name)
rows=read('intake');seen={r['text'] for r in rows}
# Keep semantic equivalents with existing groups, even if phrased differently.
keys={}
for r in rows:
 key=(r['business_type'],r['style'],tuple(sorted(r['pages'])),tuple(sorted(r['features'])))
 if key in keys:assert keys[key][1]==r['split']
 keys[key]=(r['group_id'],r['split'])
eng=['Create a {style} app for my {business} business. Screens: {screens}. Features: {features}. {negative}',
'I run a {business} store. Use a {style} design with these pages only: {screens}. Support {features}. {negative}',
'App brief: {business}; appearance: {style}; required screens: {screens}; functions: {features}. {negative}',
'For a {business} mobile shop, I need {screens}. Keep the style {style} and support {features}. {negative}',
'Please build a {style} {business} prototype. Include {screens} and these capabilities: {features}. {negative}',
'My {business} application needs {features}. Its screen list is {screens}, with a {style} appearance. {negative}']
roman=['Mujhe {business} ki {style} app chahiye. Screens sirf {screens} hon. Features: {features}. {negative}',
'Meri {business} shop ke liye app banao. Design {style} rakho, pages {screens} hon aur features {features}. {negative}',
'Aik {style} {business} application bana dein. Is mein {screens} pages aur {features} features chahiye. {negative}',
'{business} ke business ki app banani hai. Look {style} ho. Required screens: {screens}. Functions: {features}. {negative}']
i=0
while len(rows)<2000:
 i+=1;b=rng.choice(businesses);style=rng.choice(styles)
 chosen=set(rng.sample(pages,rng.randint(2,len(pages)-1)))
 if 'checkout' in chosen:chosen.add('cart')
 ordered=[p for p in pages if p in chosen]
 features=(['catalog'] if chosen & {'home','products','detail'} else [])+[p for p in ordered if 'feature:'+p in labels]
 absent=[p for p in pages if p not in chosen];excluded=rng.sample(absent,min(len(absent),rng.randint(1,2)))
 language='en' if i%2 else 'roman_ur'
 neg=('Do not add '+', '.join(excluded)+' screens.') if language=='en' else (', '.join(excluded)+' screens mat add karna.')
 if not excluded:neg=''
 text=rng.choice(eng if language=='en' else roman).format(business=b,style=style,screens=', '.join(ordered),features=', '.join(features),negative=neg)
 if text in seen:continue
 seen.add(text);key=(b,style,tuple(sorted(ordered)),tuple(sorted(features)))
 if key not in keys:keys[key]=('expanded-brief-'+hashlib.sha256(str(key).encode()).hexdigest()[:14],split(key))
 group,part=keys[key]
 rows.append(dict(id=f'expanded-intake-{i:05}',group_id=group,split=part,text=text,business_type=b,pages=ordered,features=features,style=style,labels=[f'business:{b}',f'style:{style}']+['page:'+p for p in ordered]+['feature:'+f for f in features],language=language,excluded_pages=excluded,provenance='synthetic_template',reviewed=False))
write('intake',rows)
rows=read('layouts');fields=['business','page','style','density'];known={tuple(r[k] for k in fields):r for r in rows}
# Complete supported combinations first. The current schema cannot represent 2,000 unique designs.
for combo in itertools.product(sorted({r['business'] for r in rows}),sorted({r['page'] for r in rows}),styles,['comfortable','compact']):
 if combo in known:continue
 b,page,style,density=combo;gid='expanded-layout-'+hashlib.sha256(str(combo).encode()).hexdigest()[:14]
 r=dict(id=gid,group_id=gid,split=split(combo),business=b,page=page,style=style,density=density,template_id='cards' if page in ['cart','checkout'] else {'minimal':'grid','luxury':'editorial','playful':'cards'}[style],components=['ProductCard','SectionHeading'] if page in ['home','products','search'] else ['SectionHeading'],source_url=None,license=None,provenance='synthetic_rule',reviewed=False)
 rows.append(r);known[combo]=r
base=list(known.values());rng.shuffle(base);i=0
while len(rows)<2000:
 original=base[i%len(base)];i+=1;r=dict(original)
 r.update(id=f'layout-repeat-{i:05}',replica_of=original['id'],provenance='synthetic_rule_replica',reviewed=False)
 rows.append(r)
write('layouts',rows)
rows=read('code');families={}
for r in rows:families.setdefault(r['component'],r)
i=0
# Change only literal visual constants; retain imports, props, callbacks and behaviour.
while len(rows)<2000:
 family=list(families)[i%len(families)];variant=i//len(families);i+=1;original=families[family];code=original['code']
 scale=[.85,.90,.95,1.05,1.10,1.15,1.20][variant%7]
 changes={}
 def resize(m):
  prop,value=m.group(1),float(m.group(2));new=round(value*scale,2)
  changes[f'{prop} {m.group(2)}']=str(new)
  return prop+':'+str(new)
 code=re.sub(r'\b(padding|paddingHorizontal|paddingVertical|marginTop|marginBottom|gap|borderRadius|fontSize)\s*:\s*(\d+(?:\.\d+)?)',resize,code)
 # Vary existing hex colours within the same colour neighbourhood, preserving alpha.
 def tint(m):
  value=m.group(1)
  if len(value)==3:value=''.join(c*2 for c in value)
  if len(value) not in [6,8]:return m.group(0)
  delta=(variant//7+1)*2
  rgb=[int(value[k:k+2],16) for k in [0,2,4]]
  shifted=[min(255,max(0,v+delta if v<128 else v-delta)) for v in rgb]
  return '#'+''.join(f'{v:02x}' for v in shifted)+value[6:]
 code=re.sub(r'#([0-9a-fA-F]{8}|[0-9a-fA-F]{6}|[0-9a-fA-F]{3})(?![0-9a-fA-F])',tint,code)
 desc=f'Generate a default-exported React Native {family}. Preserve its standard props and interactions. Scale spacing, corner radii and font sizes by {scale:g} from the base component. Use colour palette variant {variant//7+1}: '+', '.join(sorted(set(re.findall(r'#[0-9a-fA-F]{3,8}',code))))+'.'
 if family=='ProductCard':desc+=' Accept product, primary, dark, onOpen, onAdd and optional horizontal props.'
 rows.append(dict(id=f'expanded-{family}-{variant:03}',group_id=original['group_id'],split=original['split'],description=desc,code=code,component=family,provenance='synthetic_style_variant',reviewed=False,variant_of=original['id']))
write('code',rows)
print('Expanded all three datasets to 2,000 records. Layout unique feature combinations:',len(known))
