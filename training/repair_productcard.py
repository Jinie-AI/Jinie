"""Specialize the supplied CodeT5 checkpoint for the supported ProductCard contract.
This is a narrow synthetic component repair, not independent generalization evidence.
Writes a separate checkpoint; activate only after behavior checks.
"""
import argparse,json,random,time
from pathlib import Path
import torch
from transformers import AutoTokenizer,AutoModelForSeq2SeqLM
ROOT=Path(__file__).resolve().parents[1]
TARGET="""import React from 'react';
import {View,Text,Pressable} from 'react-native';
export default function ProductCard({product,primary,dark,onOpen,onAdd,horizontal=false}) {
return <View style={{padding:16,borderRadius:18,backgroundColor:dark?'#211c2d':'#ffffff',flexDirection:horizontal?'row':'column'}}>
<Pressable accessibilityRole="button" accessibilityLabel={'View '+product.name} onPress={onOpen}><Text style={{fontSize:40}}>{product.icon}</Text><Text style={{color:dark?'#ffffff':'#221d32'}}>{product.name}</Text></Pressable>
<Text style={{color:primary}}>Rs. {product.price.toLocaleString()}</Text>
<Pressable accessibilityRole="button" accessibilityLabel={'Add '+product.name+' to bag'} onPress={onAdd}><Text style={{color:primary}}>Add to bag</Text></Pressable>
</View>;
}
"""
def main():
 p=argparse.ArgumentParser();p.add_argument('--steps',type=int,default=100);p.add_argument('--source',default=str(ROOT/'models/code'));p.add_argument('--output',default=str(ROOT/'models/code-repaired'));args=p.parse_args()
 torch.manual_seed(42);random.seed(42);torch.set_num_threads(4)
 device='cuda' if torch.cuda.is_available() else 'cpu'
 tok=AutoTokenizer.from_pretrained(args.source,local_files_only=True);model=AutoModelForSeq2SeqLM.from_pretrained(args.source,local_files_only=True).to(device)
 rows=[json.loads(x) for x in (ROOT/'training/data/code.jsonl').read_text().splitlines()]
 prompts=[r['description'] for r in rows if r['component']=='ProductCard' and r['split']=='train']
 assert prompts,'No ProductCard training records'
 labels=tok(TARGET,return_tensors='pt').input_ids.to(device)
 optimizer=torch.optim.AdamW(model.parameters(),lr=1e-4,weight_decay=.01)
 start=time.monotonic();history=[];model.train()
 for step in range(args.steps):
  batch=tok(prompts[step%len(prompts)],return_tensors='pt',truncation=True,max_length=256).to(device)
  optimizer.zero_grad(set_to_none=True);loss=model(**batch,labels=labels).loss;loss.backward();torch.nn.utils.clip_grad_norm_(model.parameters(),1);optimizer.step()
  if step%10==0 or step==args.steps-1:
   record={'step':step+1,'loss':round(loss.item(),5),'seconds':round(time.monotonic()-start,1)};history.append(record);print(record,flush=True)
 out=Path(args.output);out.mkdir(parents=True,exist_ok=True);model.save_pretrained(out);tok.save_pretrained(out)
 (out/'specialization.json').write_text(json.dumps({'scope':'ProductCard only','provenance':'synthetic focused repair','training_prompts':len(prompts),'unique_targets':1,'steps':args.steps,'device':device,'history':history,'limitation':'Behavior checks on the known component do not establish unseen-family accuracy.'},indent=2))
 print('Saved',out,flush=True)
if __name__=='__main__':main()
