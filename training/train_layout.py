"""CPU training with group-disjoint fixed test set and training-only CV."""
import json,platform
import numpy as np,joblib,sklearn
from sklearn.feature_extraction import DictVectorizer
from sklearn.ensemble import RandomForestClassifier
from sklearn.pipeline import Pipeline
from sklearn.model_selection import GridSearchCV,GroupKFold
from sklearn.metrics import accuracy_score,f1_score,classification_report,confusion_matrix
from common import ROOT,load,report
rows,digest=load('layouts.jsonl')
train=[r for r in rows if r['split']=='train'];val=[r for r in rows if r['split']=='validation'];test=[r for r in rows if r['split']=='test']
def X(rows):return [{k:r[k] for k in ['business','page','style','density']} for r in rows]
def y(rows):return [r['template_id'] for r in rows]
pipeline=Pipeline([('vectorizer',DictVectorizer()),('forest',RandomForestClassifier(random_state=42,class_weight='balanced',n_jobs=-1))])
search=GridSearchCV(pipeline,{'forest__n_estimators':[100,200],'forest__max_depth':[6,None],'forest__min_samples_leaf':[1,2]},cv=GroupKFold(5),scoring='f1_macro',n_jobs=1)
search.fit(X(train),y(train),groups=[r['group_id'] for r in train])
model=search.best_estimator_
result={'dataset_sha256':digest,'provenance':'synthetic rule-generated bootstrap; NOT independent real-world evaluation','sklearn':sklearn.__version__,'seed':42,'best_params':search.best_params_,'cv_macro_f1':search.best_score_,'split_sizes':{s:sum(r['split']==s for r in rows) for s in ['train','validation','test']}}
for label,records in [('validation',val),('test',test)]:
    pred=model.predict(X(records));prob=model.predict_proba(X(records));classes=model.classes_
    result[label]={'accuracy':accuracy_score(y(records),pred),'macro_f1':f1_score(y(records),pred,average='macro'),'top2_accuracy':float(np.mean([r['template_id'] in classes[p.argsort()[-2:]] for r,p in zip(records,prob)])),'classification_report':classification_report(y(records),pred,output_dict=True,zero_division=0),'confusion_matrix':confusion_matrix(y(records),pred,labels=classes).tolist(),'labels':classes.tolist()}
(ROOT/'models').mkdir(exist_ok=True);joblib.dump(model,ROOT/'models/layout.joblib')
report(ROOT/'models/layout_metrics.json',result)
print(json.dumps({k:v for k,v in result.items() if k not in ['test','validation']},indent=2));print('Held-out synthetic test accuracy:',result['test']['accuracy'])
