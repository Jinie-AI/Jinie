"""Optional local checkpoints. Never download weights during an API request."""
import json
from functools import lru_cache
from .domain import ROOT, extract, PAGES, FEATURES, STYLES
MODEL_DIR=ROOT/'models'

def status():
    return {'intake': 'trained checkpoint' if (MODEL_DIR/'intake/config.json').exists() else 'rule fallback (untrained)',
            'layout': 'synthetic-trained Random Forest' if (MODEL_DIR/'layout.joblib').exists() else 'rule fallback',
            'code': ('CodeT5 ProductCard specialization + behavior checks' if (MODEL_DIR/'code/specialization.json').exists() else 'local CodeT5 candidate + validation') if (MODEL_DIR/'code/config.json').exists() else 'verified component templates (untrained)',
            'rag': 'LocalComponentRAG (TF-IDF + Cosine Similarity over React Native UI Catalog)'}

@lru_cache(maxsize=1)
def intake_model():
    from transformers import AutoTokenizer, AutoModelForSequenceClassification
    path=MODEL_DIR/'intake'
    return AutoTokenizer.from_pretrained(path,local_files_only=True),AutoModelForSequenceClassification.from_pretrained(path,local_files_only=True)

def intake(prompt):
    baseline=extract(prompt)
    if not (MODEL_DIR/'intake/config.json').exists(): return baseline
    try:
        import torch
        tok,model=intake_model(); model.eval()
        with torch.no_grad(): probs=torch.sigmoid(model(**tok(prompt,return_tensors='pt',truncation=True,max_length=256)).logits)[0].tolist()
        labels=json.loads((MODEL_DIR/'intake/labels.json').read_text())
        threshold=json.loads((MODEL_DIR/'intake/thresholds.json').read_text()) if (MODEL_DIR/'intake/thresholds.json').exists() else {'default':0.5}
        pairs=dict(zip(labels,probs))
        for kind,key in [('business','business'),('style','style')]:
            candidates={k.split(':')[1]:v for k,v in pairs.items() if k.startswith(kind+':')}
            if candidates: baseline[key]=max(candidates,key=candidates.get)
        selected=[k for k,v in pairs.items() if v>=threshold.get(k,threshold.get('default',0.5))]
        baseline['pages']=[p for p in PAGES if 'page:'+p in selected] or ['home','products','detail']
        if 'checkout' in baseline['pages'] and 'cart' not in baseline['pages']: baseline['pages'].append('cart')
        baseline['features']=[f for f in FEATURES if 'feature:'+f in selected]
        baseline.update(source='DistilBERT',confidence=round(max(probs),3))
    except Exception as exc: baseline['warnings'].append(f'Intake checkpoint could not run; using rules: {type(exc).__name__}')
    return baseline

@lru_cache(maxsize=1)
def layout_model():
    import joblib
    return joblib.load(MODEL_DIR/'layout.joblib')  # trusted project-owned checkpoint only

def recommend(business,page,style):
    if (MODEL_DIR/'layout.joblib').exists():
        try:
            model=layout_model(); probs=model.predict_proba([{'business':business,'page':page,'style':style,'density':'comfortable'}])[0]
            return [{'id':str(model.classes_[i]),'score':round(float(probs[i]),3),'source':'synthetic-trained Random Forest'} for i in probs.argsort()[::-1][:3]]
        except Exception: pass
    first={'minimal':'grid','luxury':'editorial','playful':'cards'}[style]
    return [{'id':x,'score':None,'source':'rules'} for x in [first]+[v for v in ['grid','editorial','cards'] if v!=first]]

@lru_cache(maxsize=1)
def code_model():
    from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
    import torch
    torch.set_num_threads(min(torch.get_num_threads(),4))
    p=MODEL_DIR/'code'
    return AutoTokenizer.from_pretrained(p,local_files_only=True),AutoModelForSeq2SeqLM.from_pretrained(p,local_files_only=True)

def code_candidate(description):
    if not (MODEL_DIR/'code/config.json').exists(): return None
    tok,model=code_model(); model.eval()
    import torch
    with torch.no_grad(): output=model.generate(**tok(description,return_tensors='pt',truncation=True,max_length=256),max_new_tokens=1024,num_beams=4,max_time=25)
    return tok.decode(output[0],skip_special_tokens=True)
