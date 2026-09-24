import json, subprocess, shutil, re, uuid
from .domain import ROOT, products, CATALOG
from .store import write, folder
from .models import code_candidate
TEMPLATES=ROOT/'backend/studio/templates'

from .catalog import component_source

def compile_project(p):
    pid=p['id']; spec=p['spec']; design=p['design']
    screen_configs = p.get('screen_configs') or spec.get('screen_configs') or {}
    config={'name':p['name'],'business':spec.get('business_label') or spec['business'],'pages':[r['page'] for r in p['requirements'] if r['approved']], 'features':spec['features'], 'products':spec.get('products') or products(spec['business']), 'primary':design['primary'],'secondary':design.get('secondary','#ede5f7'),'accent':design.get('accent','#b98849'),'bodyFont':design.get('bodyFont','sans'),'navigation':design.get('navigation','bottom'),'theme':design['theme'],'font':design['font'],'layout':design['layout'],'contact':'hello@example.com','screen_configs':screen_configs}
    write(pid,'src/config.json',json.dumps(config,ensure_ascii=False,indent=2))
    write(pid,'App.jsx',(TEMPLATES/'App.jsx').read_text(encoding='utf-8'))
    write(pid,'src/components/ProductCard.jsx',component_source('ProductCard'))
    components=[]
    for i,name in enumerate(CATALOG):
        source=component_source(name)
        write(pid,f'src/components/{name}.jsx',source)
        components.append({'id':f'CMP-{i+1:03}','name':name,'file':f'src/components/{name}.jsx','source':'template','used':name=='ProductCard'})
    # A fine-tuned candidate is kept as an inspectable artifact. It is only substituted
    # for the main product card after export/contract checks and a successful bundle.
    try:
        candidate=code_candidate('Generate a React Native ProductCard with product, primary, dark, onOpen, onAdd props. Export default ProductCard.')
        if candidate:
            write(pid,'model-candidates/ProductCard.txt',candidate)
            node=shutil.which('node')
            if not node: raise RuntimeError('Node.js is required for candidate validation')
            checked=subprocess.run([node,str(ROOT/'scripts/validate-product-card.mjs'),str(folder(pid)/'source/model-candidates/ProductCard.txt')],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=15)
            if checked.returncode==0:
                write(pid,'src/components/ProductCard.jsx',candidate)
                components[0]['source']='CodeT5 candidate'
            else:
                from .openai_planner import repair_code_candidate, configuration as openai_config
                if openai_config()['configured']:
                    repaired = repair_code_candidate(candidate, checked.stderr or checked.stdout)
                    write(pid,'model-candidates/ProductCard_repaired.txt',repaired)
                    checked_rep = subprocess.run([node,str(ROOT/'scripts/validate-product-card.mjs'),str(folder(pid)/'source/model-candidates/ProductCard_repaired.txt')],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=15)
                    write(pid,'model-candidates/repair_validation.json',checked_rep.stdout or json.dumps({'passed':False,'error':checked_rep.stderr[-1000:]}))
                    if checked_rep.returncode==0:
                        write(pid,'src/components/ProductCard.jsx',repaired)
                        components[0]['source']='CodeT5 (LLM-repaired)'
                        p['model_warnings'].append('CodeT5 candidate was automatically verified and repaired to satisfy React Native behavior checks.')
                    else:
                        p['model_warnings'].append('CodeT5 candidate failed syntax checks. Template used; inspect model-candidates/validation.json.')
                else:
                    p['model_warnings'].append('CodeT5 candidate failed syntax or behavior checks. Template used; inspect model-candidates/validation.json.')
    except Exception as exc: p['model_warnings'].append('CodeT5 inference failed; template used: '+type(exc).__name__)
    write(pid,'index.js',"import {registerRootComponent} from 'expo';\nimport App from './App';\nregisterRootComponent(App);\n")
    gallery_imports='\n'.join(f"import {name} from './src/components/{name}';" for name in CATALOG)
    gallery="import React,{useState} from 'react';\nimport {createRoot} from 'react-dom/client';\nimport {View,Text} from 'react-native';\nimport App from './App';\nimport config from './src/config.json';\n"+gallery_imports+"\nconst components={"+','.join(CATALOG)+"};\nfunction Gallery(){const [value,setValue]=useState('');const [quantity,setQuantity]=useState(1);const [message,setMessage]=useState('');const C=components[new URLSearchParams(location.search).get('component')];return C?<View style={{padding:24,gap:24,backgroundColor:'#fff',minHeight:'100%'}}><Text style={{fontSize:12,color:'#888'}}>ISOLATED COMPONENT PREVIEW</Text><C product={config.products[0]} primary={config.primary} value={C===QuantityControl?quantity:value} onChange={setQuantity} onChangeText={setValue} quantity={quantity} onIncrease={()=>setQuantity(q=>q+1)} onDecrease={()=>setQuantity(q=>Math.max(0,q-1))} onOpen={()=>setMessage('Open product callback fired')} onAdd={()=>setMessage('Add to cart callback fired')} onPress={()=>setMessage('Press callback fired')} onBook={()=>setMessage('Booking callback fired')} onAction={()=>setMessage('Action callback fired')}/><Text>{message}</Text></View>:<App/>;}\nclass PreviewBoundary extends React.Component{constructor(p){super(p);this.state={error:null};}static getDerivedStateFromError(error){return {error:String(error.message||error)};}render(){return this.state.error?<pre style={{whiteSpace:'pre-wrap',padding:24,color:'#922'}}>Preview error: {this.state.error}. Check generated source and rebuild.</pre>:this.props.children;}}\ncreateRoot(document.getElementById('root')).render(<PreviewBoundary><Gallery/></PreviewBoundary>);\n"
    gallery+="document.addEventListener('click',e=>{if(e.altKey){e.preventDefault();e.stopPropagation();const el=document.querySelector('[id^=jinie-page-]');parent.postMessage({type:'jinie-annotation',page:el?.id.replace('jinie-page-',''),text:e.target.textContent?.slice(0,100)},'*');}},true);\n"
    write(pid,'preview.jsx',gallery)
    write(pid,'src/storage.web.js',"const KEY="+json.dumps('jinie-'+pid)+";\nexport async function loadState(){try{return JSON.parse(localStorage.getItem(KEY)||'null');}catch{return null;}}\nexport async function saveState(value){try{localStorage.setItem(KEY,JSON.stringify(value));}catch{/* sandboxed preview has memory-only state */}}\n")
    write(pid,'src/storage.js',"import AsyncStorage from '@react-native-async-storage/async-storage';\nconst KEY='jinie-state';\nexport async function loadState(){return JSON.parse(await AsyncStorage.getItem(KEY)||'null');}\nexport async function saveState(value){await AsyncStorage.setItem(KEY,JSON.stringify(value));}\n")
    package={'name':'jinie-generated-app','version':'1.0.0','private':True,'main':'index.js','scripts':{'start':'expo start','android':'expo start --android','ios':'expo start --ios','web':'expo start --web','build:web':'expo export --platform web'},'dependencies':{'expo':'~54.0.0','react':'19.1.0','react-dom':'19.1.0','react-native':'0.81.5','react-native-web':'~0.21.0','@react-native-async-storage/async-storage':'2.2.0','@expo/metro-runtime':'~6.1.2'}}
    write(pid,'package.json',json.dumps(package,indent=2))
    write(pid,'app.json',json.dumps({'expo':{'name':p['name'],'slug':'jinie-'+pid[:8],'version':'1.0.0','orientation':'portrait','userInterfaceStyle':design['theme'],'web':{'bundler':'metro','output':'single'}}},indent=2))
    write(pid,'firebase.json',json.dumps({'hosting':{'public':'dist','ignore':['firebase.json','**/.*','**/node_modules/**'],'rewrites':[{'source':'**','destination':'/index.html'}]}},indent=2))
    write(pid,'firestore.rules',"rules_version = '2';\nservice cloud.firestore { match /databases/{database}/documents { match /{document=**} { allow read, write: if false; } } }\n")
    write(pid,'README.md','# '+p['name']+'\n\nGenerated by Jinie. React Native + Expo SDK 54.\n\n1. Install Node 20.19+ or 22 LTS.\n2. `npm install`\n3. `npx expo install --fix`\n4. `npm start` (Android emulator / matching Expo Go or development build)\n5. `npm run web` for browser.\n\nRun `npm run build:web` then `firebase deploy --only hosting --project YOUR_PROJECT` after Firebase login.\n\nCart and demo COD orders are device-local. No real payment, login, inventory server, or fulfilment is connected. Replace the sample catalog and contact details before publication. Generated native output requires device testing.\n')
    rag_comps = p.get('rag_components') or spec.get('rag_components') or []
    if rag_comps:
        write(pid, 'src/rag_components.json', json.dumps(rag_comps, indent=2))
        for j, rc in enumerate(rag_comps):
            components.append({
                'id': f'RAG-{j+1:03}',
                'name': rc.get('name', f'RAGComponent{j+1}'),
                'file': 'src/rag_components.json',
                'source': f"RAG ({rc.get('category', 'UI')})",
                'used': True
            })
    p['components']=components
    rag_ids = [c['id'] for c in components if str(c.get('id', '')).startswith('RAG-')]
    p['traceability']=[{'requirement':r['id'],'page':r['page'],'components':(['CMP-001'] + rag_ids[:2]) if r['page'] in ['home','products','detail','search'] else [],'files':['App.jsx','src/config.json'] + (['src/rag_components.json'] if rag_comps else []),'test':f'TEST-{i+1:03}'} for i,r in enumerate(p['requirements']) if r['approved']]
    write(pid,'traceability.json',json.dumps(p['traceability'],indent=2))
    return p

def bundle(p):
    node=shutil.which('node')
    if not node: raise RuntimeError('Node.js is required to compile the live preview. Install Node 22 LTS.')
    preview_name='preview-'+uuid.uuid4().hex
    def run():
        return subprocess.run([node,str(ROOT/'scripts/build-preview.mjs'),str(folder(p['id'])/'source'),str(folder(p['id'])/preview_name)],capture_output=True,text=True,encoding="utf-8",errors="replace",timeout=120)
    result=run()
    if result.returncode and any(c['source']=='CodeT5 candidate' for c in p.get('components',[])):
        write(p['id'],'src/components/ProductCard.jsx',component_source('ProductCard'))
        p['components'][0]['source']='template (CodeT5 failed build)'
        p['model_warnings'].append('CodeT5 candidate failed compilation and was replaced with the tested template.')
        result=run()
    if result.returncode: raise RuntimeError('Preview build failed: '+result.stderr[-3500:])
    p['_pending_preview']=preview_name
