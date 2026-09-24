import json, os, sqlite3, threading
from pathlib import Path
from .domain import ROOT
DATA = Path(os.getenv('JINIE_DATA_DIR', str(ROOT / 'runtime')))
DATA.mkdir(parents=True, exist_ok=True)
LOCK = threading.RLock()
def connection():
    con=sqlite3.connect(DATA/'projects.sqlite3', timeout=30)
    con.execute('CREATE TABLE IF NOT EXISTS projects(id TEXT PRIMARY KEY, data TEXT NOT NULL)')
    return con

def save(project):
    with LOCK, connection() as con:
        con.execute('INSERT OR REPLACE INTO projects VALUES(?,?)',(project['id'],json.dumps(project,ensure_ascii=False)))

def get(pid):
    with connection() as con:
        row=con.execute('SELECT data FROM projects WHERE id=?',(pid,)).fetchone()
    if not row: raise KeyError(pid)
    return json.loads(row[0])

def listing():
    with connection() as con: rows=con.execute('SELECT data FROM projects ORDER BY rowid DESC').fetchall()
    return [json.loads(r[0]) for r in rows]

def folder(pid):
    if not __import__('re').fullmatch(r'[0-9a-f]{32}',pid): raise ValueError('Invalid project ID')
    path=DATA/pid
    path.mkdir(exist_ok=True)
    return path

def safe_file(pid, name):
    base=(folder(pid)/'source').resolve()
    path=(base/name).resolve()
    if not path.is_relative_to(base) or path==base: raise ValueError('Invalid file path')
    return path

def write(pid,name,content):
    path=safe_file(pid,name); path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(content,encoding='utf-8')
