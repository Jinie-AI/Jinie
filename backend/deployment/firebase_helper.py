"""Deploys only to an explicitly configured Firebase project, using CLI credentials."""
from pathlib import Path
import json,re,shutil,subprocess
class FirebaseHelper:
    def __init__(self,workspace='.'):self.workspace=Path(workspace).resolve();self.project_id=None
    def configure_hosting(self,project_id,config_data):
        if not re.fullmatch(r'[a-z][a-z0-9-]{4,28}[a-z0-9]',project_id):raise ValueError('Invalid Firebase project ID')
        self.project_id=project_id;self.workspace.mkdir(parents=True,exist_ok=True)
        (self.workspace/'firebase.json').write_text(json.dumps(config_data,indent=2))
        return True
    def deploy_app(self,build_dir):
        if not self.project_id:raise RuntimeError('Configure the project first')
        if not (Path(build_dir)/'index.html').is_file():raise ValueError('Build directory has no index.html')
        cli=shutil.which('firebase')
        if not cli:raise RuntimeError('Install firebase-tools and run firebase login')
        result=subprocess.run([cli,'deploy','--only','hosting','--project',self.project_id,'--non-interactive','--json'],cwd=self.workspace,capture_output=True,text=True,timeout=240)
        if result.returncode:raise RuntimeError(result.stderr or result.stdout)
        payload=json.loads(result.stdout)
        if payload.get('status')!='success':raise RuntimeError('Firebase did not confirm deployment')
        return 'https://'+self.project_id+'.web.app'
