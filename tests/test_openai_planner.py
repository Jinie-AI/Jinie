"""Offline integration checks; no paid API calls."""
import sys,json
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import MagicMock
import pytest
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'backend'))
from studio import openai_planner as planner
BASE={'business':'beauty','pages':['home'],'style':'minimal','features':[],'warnings':[],'source':'DistilBERT'}
def test_no_key(monkeypatch):
 monkeypatch.delenv('OPENAI_API_KEY',raising=False)
 with pytest.raises(planner.PlannerError,match='Set OPENAI_API_KEY'):planner.plan_requirements('clothing store','',BASE)
def test_api_plan_and_provenance(monkeypatch):
 import openai
 monkeypatch.setenv('OPENAI_API_KEY','test-key-never-real')
 plan=planner.Plan(business='clothing',pages=['products','checkout','products'],style='minimal',summary='A clothing demo.',questions=['Which currency?'],unsupported_features=['Online payments'])
 client=MagicMock();client.responses.parse.return_value=SimpleNamespace(status='completed',output_parsed=plan,usage=None)
 factory=MagicMock();factory.return_value.__enter__.return_value=client;monkeypatch.setattr(openai,'OpenAI',factory)
 spec,meta=planner.plan_requirements('clothing store','reference',BASE)
 assert spec['business']=='clothing' and set(spec['pages'])=={'products','detail','checkout','cart'}
 assert meta['local_prediction']['business']=='beauty'
 assert 'Not implemented: Online payments' in spec['warnings']
 kwargs=client.responses.parse.call_args.kwargs
 assert kwargs['store'] is False and kwargs['text_format'] is planner.Plan
 assert 'test-key-never-real' not in json.dumps(meta)
def test_refusal(monkeypatch):
 import openai
 monkeypatch.setenv('OPENAI_API_KEY','fake')
 client=MagicMock();client.responses.parse.return_value=SimpleNamespace(status='completed',output_parsed=None)
 factory=MagicMock();factory.return_value.__enter__.return_value=client;monkeypatch.setattr(openai,'OpenAI',factory)
 with pytest.raises(planner.PlannerError,match='complete plan'):planner.plan_requirements('clothing store','',BASE)
def test_error_redaction(monkeypatch):
 import openai
 monkeypatch.setenv('OPENAI_API_KEY','private-test-value')
 factory=MagicMock(side_effect=RuntimeError('private-test-value'));monkeypatch.setattr(openai,'OpenAI',factory)
 with pytest.raises(planner.PlannerError) as e:planner.plan_requirements('clothing store','',BASE)
 assert 'private-test-value' not in str(e.value)
def test_schema_rejects_unsupported_page():
 with pytest.raises(ValueError):planner.Plan(business='clothing',pages=['tracking'],style='minimal',summary='',questions=[],unsupported_features=[])
def test_route_automatic(monkeypatch):
 monkeypatch.delenv("OPENAI_API_KEY",raising=False)
 from fastapi.testclient import TestClient
 from fastapi import FastAPI
 from studio import api
 saved={}
 monkeypatch.setattr(api.models,'intake',lambda _:dict(BASE))
 monkeypatch.setattr(api.models,'recommend',lambda *a:[{'id':'grid','score':None,'source':'rules'}])
 monkeypatch.setattr(api.store,'save',lambda p:saved.update(p))
 fn=MagicMock(return_value=({**BASE,'business':'clothing'},{'model':'test','summary':'x','questions':[],'unsupported_features':[]}))
 monkeypatch.setattr(api.openai_planner,'plan_requirements',fn)
 app=FastAPI();app.include_router(api.router);c=TestClient(app)
 assert c.post('/api/projects',json={'prompt':'Make a clothing shop'}).status_code==201
 fn.assert_not_called()
 monkeypatch.setenv('OPENAI_API_KEY','test-only')
 result=c.post('/api/projects',json={'prompt':'Make a clothing shop'})
 assert result.status_code==201 and result.json()['spec']['business']=='clothing'
 assert result.json()['api_plan']['model']=='test'
 assert all(not x['approved'] for x in result.json()['requirements'])
 fn.side_effect=planner.PlannerError('API unavailable')
 assert c.post('/api/projects',json={'prompt':'Make a clothing shop','use_openai':True}).status_code==502


def test_custom_catalog_schema():
 p=planner.Product(name='Telescope',price=12000,description='Sample telescope',category='Astronomy',icon='🔭')
 assert p.price==12000
 with pytest.raises(ValueError):planner.Product(name='x',price=-1,description='x',category='x',icon='x')
 with pytest.raises(ValueError):planner.Product(name='x',price=float('nan'),description='x',category='x',icon='x')


def test_custom_catalog_reaches_generated_app(monkeypatch,tmp_path):
 from studio import compiler,store
 monkeypatch.setattr(store,'DATA',tmp_path)
 monkeypatch.setattr(compiler,'code_candidate',lambda _:None)
 product={'id':'sample-1','name':'Telescope','price':12000,'description':'Sample product','category':'Astronomy','icon':'🔭'}
 p={'id':'a'*32,'name':'Star Shop','spec':{'business':'electronics','business_label':'astronomy','features':['catalog'],'products':[product]},'design':{'primary':'#112233','theme':'light','font':'sans','layout':'grid'},'requirements':[{'id':'REQ-001','page':'products','approved':True}],'model_warnings':[]}
 compiler.compile_project(p)
 config=json.loads((store.folder(p['id'])/'source/src/config.json').read_text(encoding='utf-8'))
 assert config['products']==[product] and config['business']=='astronomy'
 compiler.bundle(p)
 html=(store.folder(p['id'])/p['_pending_preview']/'index.html').read_text(encoding='utf-8')
 assert 'reportPreviewError' in html
