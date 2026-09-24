import io,json,os,sys,time,zipfile
from pathlib import Path
import pytest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'backend'))
from fastapi.testclient import TestClient
from main import app
client=TestClient(app)

def new():
    r=client.post('/api/projects',json={'name':'Test shop','prompt':'Build a clothing store with cart checkout search about and contact'})
    assert r.status_code==201,r.text
    return r.json()
def approve(p):
    for r in p['requirements']:r['approved']=True
    res=client.put(f"/api/projects/{p['id']}/review",json={k:p[k] for k in ['requirements','design']}|{'business':p['spec']['business']})
    assert res.status_code==200,res.text
    return res.json()
def wait(pid):
    for _ in range(300):
        p=client.get('/api/projects/'+pid).json()
        if p['status']!='building':return p
        time.sleep(.1)
    pytest.fail('build timed out')
def test_complete_pipeline_and_edit():
    p=new();url='/api/projects/'+p['id']
    assert client.post(url+'/build').status_code==409
    p=approve(p);assert client.post(url+'/build').status_code==200
    p=wait(p['id']);assert p['status']=='ready',p.get('error')
    assert len(p['traceability'])==8
    assert client.get(url+'/preview/index.html').status_code==200
    archive=client.get(url+'/download');assert archive.status_code==200
    with zipfile.ZipFile(io.BytesIO(archive.content)) as z:
        assert 'jinie-app/App.jsx' in z.namelist()
        package=json.loads(z.read('jinie-app/package.json'));assert package['dependencies']['react-native']=='0.81.5'
    original=client.get(url+'/file',params={'path':'src/config.json'}).json()['content']
    config=json.loads(original);config['name']='Edited shop'
    assert client.put(url+'/file',params={'path':'src/config.json'},json={'content':json.dumps(config)}).status_code==200
    assert client.get(url+'/download').status_code==409
    assert client.post(url+'/rebuild').status_code==200
    p=wait(p['id']);assert p['status']=='ready',p.get('error')
    # A failed edited build must not replace the last successful preview.
    previous_bundle=client.get(url+'/preview/app.js').content
    app_source=client.get(url+'/file',params={'path':'App.jsx'}).json()['content']
    client.put(url+'/file',params={'path':'App.jsx'},json={'content':'export default function Broken( {'})
    assert client.post(url+'/rebuild').status_code==200
    failed=wait(p['id']);assert failed['status']=='failed'
    assert client.get(url+'/preview/app.js').content==previous_bundle
    assert client.get(url+'/download').status_code==409
    client.put(url+'/file',params={'path':'App.jsx'},json={'content':app_source})
    client.post(url+'/rebuild');assert wait(p['id'])['status']=='ready'
    r=client.post(url+'/feedback',json={'requirement_id':'REQ-001','text':'Change the home styling','rating':4})
    assert r.status_code==200 and not r.json()['requirements'][0]['approved']
    assert client.post(url+'/build').status_code==409

def test_validation_and_paths():
    assert client.post('/api/projects',json={'prompt':'        '}).status_code==422
    p=new();url='/api/projects/'+p['id']
    for path in ['../../main.py','/etc/passwd']:
        assert client.get(url+'/file',params={'path':path}).status_code==400
    assert client.post(url+'/feedback',json={'requirement_id':'BAD','text':'hello','rating':1}).status_code==422
    assert client.post(url+'/deploy').status_code==409
    assert client.post('/api/references',files={'file':('a.exe',b'fake','application/octet-stream')}).status_code==415
    assert client.post('/api/references',files={'file':('a.txt',b'clothing business','text/plain')}).json()['text']=='clothing business'
    duplicate=[p['requirements'][0],p['requirements'][0]]
    assert client.put(url+'/review',json={'requirements':duplicate,'design':p['design'],'business':'clothing'}).status_code==422

def test_dataset_split_groups():
    for file in ['intake','layouts','code']:
        rows=[json.loads(x) for x in (ROOT/'training/data'/f'{file}.jsonl').read_text().splitlines()]
        groups={s:{r['group_id'] for r in rows if r['split']==s} for s in ['train','validation','test']}
        assert not groups['train']&groups['test']
        assert not groups['train']&groups['validation']
        assert not groups['test']&groups['validation']
