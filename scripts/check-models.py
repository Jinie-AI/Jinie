"""Run actual local inference; status alone only checks checkpoint files."""
import json,sys,time
from pathlib import Path
root=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(root/'backend'))
from studio import models
result={'checkpoint_status':models.status(),'checks':{}}
for name,call in [('layout',lambda:models.recommend('clothing','products','minimal')),('intake',lambda:models.intake('Build a minimal clothing store with products, cart and checkout.')),('code',lambda:models.code_candidate('Generate a React Native ProductCard with product, primary, dark, onOpen, onAdd props. Export default ProductCard.'))]:
 start=time.monotonic()
 try:
  value=call()
  result['checks'][name]={'seconds':round(time.monotonic()-start,2),'result':value}
 except Exception as exc:result['checks'][name]={'error':str(exc),'type':type(exc).__name__}
out=root/'docs/model-integration-results.json';out.write_text(json.dumps(result,indent=2,ensure_ascii=False))
print(json.dumps(result,indent=2,ensure_ascii=False))
