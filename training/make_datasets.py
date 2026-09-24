"""Reproducible SYNTHETIC bootstraps, not manually curated research evidence."""
import sys,json,random,itertools
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1];sys.path.insert(0,str(ROOT/'backend'))
from studio.domain import BUSINESSES,PAGES,STYLES,CATALOG,LABELS
from studio.compiler import component_source
OUT=ROOT/'training/data';OUT.mkdir(parents=True,exist_ok=True)
rng=random.Random(42)
def write(name,rows):
    (OUT/name).write_text('\n'.join(json.dumps(r,ensure_ascii=False) for r in rows)+'\n',encoding='utf-8')
def partition(groups):
    groups=list(groups);rng.shuffle(groups);n=len(groups);return {g:('train' if i<int(n*.8) else 'validation' if i<int(n*.9) else 'test') for i,g in enumerate(groups)}
rows=[];groups=[f'brief-{i:03}' for i in range(240)];splits=partition(groups)
seen_intake=set()
for i,g in enumerate(groups):
    business=list(BUSINESSES)[i%10];style=STYLES[(i//10)%3]
    while True:
        chosen=['home','products','detail']+rng.sample(['cart','checkout','search','contact','about'],rng.randint(1,5))
        if 'checkout' in chosen and 'cart' not in chosen:chosen.append('cart')
        chosen=[p for p in PAGES if p in chosen]
        key=(business,style,tuple(chosen))
        if key not in seen_intake:seen_intake.add(key);break
    features=['catalog']+[p for p in chosen if p in ['cart','checkout','search','contact','about']]
    phrase=', '.join(chosen)
    texts=[('en',f'Build a {style} {business} shop for my small business. Include {phrase}. Customers need '+', '.join(features)+'.'),('roman_ur',f'Mujhe {business} ki {style} app chahiye. Is mein {phrase} pages hon aur '+', '.join(features)+' features chahiye.'),('ur',f'مجھے {business} کے کاروبار کے لیے ایک {style} ایپ چاہیے۔ اس میں {phrase} صفحات اور '+', '.join(features)+' کی سہولت ہونی چاہیے۔')]
    for lang,text in texts:rows.append({'id':g+'-'+lang,'group_id':g,'split':splits[g],'text':text,'business_type':business,'pages':chosen,'features':features,'style':style,'labels':[f'business:{business}',f'style:{style}']+['page:'+p for p in chosen]+['feature:'+f for f in features],'language':lang,'provenance':'synthetic_template','reviewed':False})
write('intake.jsonl',rows)
# Unique business/page/style tuples: avoid exact feature duplicates between splits.
combos=list(itertools.product(BUSINESSES,PAGES,STYLES,["comfortable","compact"]));rng.shuffle(combos)
rows=[];groups=[f'layout-{i:03}' for i in range(400)];splits=partition(groups)
for i,(business,page,style,density) in enumerate(combos[:400]):
    target={'minimal':'grid','luxury':'editorial','playful':'cards'}[style]
    if page in ['cart','checkout']:target='cards'
    rows.append({'id':groups[i],'group_id':groups[i],'split':splits[groups[i]],'business':business,'page':page,'style':style,'density':density,'template_id':target,'components':['ProductCard','SectionHeading'] if page in ['home','products','search'] else ['SectionHeading'],'source_url':None,'license':None,'provenance':'synthetic_rule','reviewed':False})
write('layouts.jsonl',rows)
# Split by implementation family, keeping all nine paraphrases together.
# This is deliberately harder than leaking identical target code across splits.
splits=partition(CATALOG);rows=[]
for family in CATALOG:
    code=component_source(family)
    descriptions=[f'Generate a React Native {family} component. Use named React Native imports and a default export.',f'Create the {family} UI in JSX for a mobile commerce app.',f'Write reusable React Native code for {family}.',f'Implement a {family} with an accessible mobile-friendly layout.',f'I need a {family} for an Expo store.',f'Build {family} using View and Text for a shop screen.',f'Output a default-exported {family} component for React Native.',f'For the component library, provide the JSX source for {family}.',f'Create a self-contained {family} with inline or StyleSheet styling.']
    if family=='ProductCard':descriptions[0]='Generate a React Native ProductCard with product, primary, dark, onOpen, onAdd props. Export default ProductCard.'
    for j,d in enumerate(descriptions):rows.append({'id':family+'-'+str(j),'group_id':family,'split':splits[family],'description':d,'code':code,'component':family,'provenance':'synthetic_template','reviewed':False})
write('code.jsonl',rows)
(OUT/'labels.json').write_text(json.dumps(LABELS,indent=2))
print('Created 720 intake, 400 layout, 180 code records. All synthetic and awaiting human review.')
