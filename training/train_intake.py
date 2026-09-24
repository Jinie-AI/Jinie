"""Fine-tune multilingual DistilBERT. Run on a Colab GPU after dataset review."""
import argparse,json
import numpy as np, torch
from datasets import Dataset
from transformers import AutoTokenizer,AutoModelForSequenceClassification,Trainer,TrainingArguments,EarlyStoppingCallback,set_seed
from sklearn.metrics import f1_score,accuracy_score,hamming_loss,classification_report
from common import ROOT,load,report
parser=argparse.ArgumentParser();parser.add_argument('--epochs',type=int,default=8);parser.add_argument('--batch-size',type=int,default=8);parser.add_argument('--allow-synthetic',action='store_true');args=parser.parse_args()
rows,digest=load('intake.jsonl')
if not args.allow_synthetic and any(not r.get('reviewed') for r in rows):raise SystemExit('Review and label every record or pass --allow-synthetic for a bootstrap experiment only.')
set_seed(42);labels=json.loads((ROOT/'training/data/labels.json').read_text());base='distilbert/distilbert-base-multilingual-cased'
tok=AutoTokenizer.from_pretrained(base)
model=AutoModelForSequenceClassification.from_pretrained(base,num_labels=len(labels),problem_type='multi_label_classification',id2label=dict(enumerate(labels)),label2id={v:i for i,v in enumerate(labels)})
def prepare(split):
    selected=[r for r in rows if r['split']==split]
    data=Dataset.from_list([{'text':r['text'],'labels':[float(l in r['labels']) for l in labels]} for r in selected])
    return data.map(lambda b:tok(b['text'],truncation=True,padding='max_length',max_length=256),batched=True,remove_columns=['text'])
def metrics(pred):
    logits,y=pred; p=(1/(1+np.exp(-np.clip(logits,-30,30)))>=.5).astype(int)
    return {'micro_f1':f1_score(y,p,average='micro',zero_division=0),'macro_f1':f1_score(y,p,average='macro',zero_division=0),'exact_match':accuracy_score(y,p),'hamming_loss':hamming_loss(y,p)}
out=ROOT/'models/intake';out.mkdir(parents=True,exist_ok=True)
trainer=Trainer(model=model,args=TrainingArguments(output_dir=str(ROOT/'training/checkpoints/intake'),learning_rate=2e-5,per_device_train_batch_size=args.batch_size,per_device_eval_batch_size=args.batch_size,gradient_accumulation_steps=2,num_train_epochs=args.epochs,weight_decay=.01,eval_strategy='epoch',save_strategy='epoch',load_best_model_at_end=True,metric_for_best_model='macro_f1',save_total_limit=2,fp16=torch.cuda.is_available(),report_to='none',seed=42),train_dataset=prepare('train'),eval_dataset=prepare('validation'),processing_class=tok,compute_metrics=metrics,callbacks=[EarlyStoppingCallback(early_stopping_patience=2)])
trainer.train()
# Select ONE global threshold on validation; never tune using test scores.
val=trainer.predict(prepare('validation'));vp=1/(1+np.exp(-np.clip(val.predictions,-30,30)))
threshold=max(np.arange(.2,.76,.05),key=lambda t:f1_score(val.label_ids,vp>=t,average='macro',zero_division=0))
test=trainer.predict(prepare('test'));probs=1/(1+np.exp(-np.clip(test.predictions,-30,30)));pred=probs>=threshold
trainer.save_model(str(out));tok.save_pretrained(out);report(out/'labels.json',labels);report(out/'thresholds.json',{'default':float(threshold)})
report(out/'metrics.json',{'dataset_sha256':digest,'base_model':base,'synthetic_bootstrap':any(r.get('provenance','').startswith('synthetic') for r in rows),'threshold':float(threshold),'test_micro_f1':f1_score(test.label_ids,pred,average='micro',zero_division=0),'test_macro_f1':f1_score(test.label_ids,pred,average='macro',zero_division=0),'test_exact_match':accuracy_score(test.label_ids,pred),'hamming_loss':hamming_loss(test.label_ids,pred),'per_label':classification_report(test.label_ids,pred,target_names=labels,output_dict=True,zero_division=0)})
print('Saved',out,'Restart the backend after copying this directory.')
