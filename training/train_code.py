"""CodeT5-small fine-tuning on React Native JSX; GPU recommended."""
import argparse,json,re
import numpy as np,torch
from datasets import Dataset
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM,Seq2SeqTrainer,Seq2SeqTrainingArguments,DataCollatorForSeq2Seq,EarlyStoppingCallback,set_seed
from common import ROOT,load,report
parser=argparse.ArgumentParser();parser.add_argument('--epochs',type=int,default=20);parser.add_argument('--batch-size',type=int,default=2);parser.add_argument('--allow-synthetic',action='store_true');args=parser.parse_args()
rows,digest=load('code.jsonl')
if not args.allow_synthetic and any(not r.get('reviewed') for r in rows):raise SystemExit('Review every component and target or pass --allow-synthetic for a bootstrap experiment only.')
set_seed(42);base='Salesforce/codet5-small';tok=AutoTokenizer.from_pretrained(base);model=AutoModelForSeq2SeqLM.from_pretrained(base)
# Fail rather than silently chop off the end of long target components.
max_target=max(len(tok(r['code']).input_ids) for r in rows)
if max_target>1024:raise SystemExit(f'Target has {max_target} tokens. Break large components into smaller pairs (limit 1024).')
def prepare(split):
    data=Dataset.from_list([{'description':r['description'],'code':r['code']} for r in rows if r['split']==split])
    def encode(b):
        inputs=tok(b['description'],max_length=256,truncation=True)
        inputs['labels']=tok(text_target=b['code'],max_length=1024,truncation=False)['input_ids'];return inputs
    return data.map(encode,batched=True,remove_columns=['description','code'])
def metrics(pred):
    ids,labels=pred
    if isinstance(ids,tuple):ids=ids[0]
    generated=tok.batch_decode(np.where(ids!=-100,ids,tok.pad_token_id),skip_special_tokens=True)
    targets=tok.batch_decode(np.where(labels!=-100,labels,tok.pad_token_id),skip_special_tokens=True)
    norm=lambda s:re.sub(r'\s+',' ',s).strip()
    return {'exact_match':float(np.mean([norm(a)==norm(b) for a,b in zip(generated,targets)]))}
out=ROOT/'models/code';out.mkdir(parents=True,exist_ok=True)
trainer=Seq2SeqTrainer(model=model,args=Seq2SeqTrainingArguments(output_dir=str(ROOT/'training/checkpoints/code'),learning_rate=5e-5,per_device_train_batch_size=args.batch_size,per_device_eval_batch_size=args.batch_size,gradient_accumulation_steps=4,num_train_epochs=args.epochs,weight_decay=.01,eval_strategy='epoch',save_strategy='epoch',load_best_model_at_end=True,metric_for_best_model='eval_loss',greater_is_better=False,save_total_limit=2,predict_with_generate=True,generation_max_length=1024,generation_num_beams=4,fp16=torch.cuda.is_available(),report_to='none',seed=42),train_dataset=prepare('train'),eval_dataset=prepare('validation'),processing_class=tok,data_collator=DataCollatorForSeq2Seq(tok,model=model),compute_metrics=metrics,callbacks=[EarlyStoppingCallback(early_stopping_patience=3)])
trainer.train();prediction=trainer.predict(prepare('test'));trainer.save_model(str(out));tok.save_pretrained(out)
outputs=tok.batch_decode(np.where(prediction.predictions!=-100,prediction.predictions,tok.pad_token_id),skip_special_tokens=True)
testrows=[r for r in rows if r['split']=='test'];report(out/'predictions.json',[{'id':r['id'],'description':r['description'],'target':r['code'],'generated':g} for r,g in zip(testrows,outputs)])
report(out/'metrics.json',{'base_model':base,'dataset_sha256':digest,'synthetic_bootstrap':any(r.get('provenance','').startswith('synthetic') for r in rows),'test':prediction.metrics,'note':'Exact match is not functional correctness. Run node scripts/check-code-predictions.mjs models/code/predictions.json, then test accepted components in Expo.'})
print('Saved',out)
