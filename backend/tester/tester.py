from pathlib import Path
import json
class Tester:
    def generate_tests(self,functional_specs):
        return [{'id':f'TEST-{i+1:03}','requirement':r['id'],'page':r.get('page'),'kind':'structural'} for i,r in enumerate(functional_specs)]
    def run_tests(self,project_path,test_specs):
        root=Path(project_path);config=json.loads((root/'src/config.json').read_text())
        tests=[dict(t,status='passed' if t['page'] in config['pages'] else 'failed') for t in test_specs]
        return {'tests':tests,'passed':sum(t['status']=='passed' for t in tests),'failed':sum(t['status']=='failed' for t in tests),'native_tests':'not_run'}
