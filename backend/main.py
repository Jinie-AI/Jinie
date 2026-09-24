"""Run from backend/: python -m uvicorn main:app --reload --host 127.0.0.1"""
import os
from pathlib import Path
from dotenv import load_dotenv
load_dotenv(Path(__file__).resolve().parent / ".env", override=False)
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from studio.api import router
from studio import store
app=FastAPI(title='Jinie Studio',version='2.0.0')
app.add_middleware(CORSMiddleware,allow_origins=os.getenv('JINIE_ALLOWED_ORIGINS','http://localhost:5173,http://127.0.0.1:5173').split(','),allow_methods=['GET','POST','PUT'],allow_headers=['*'])
app.include_router(router)
@app.on_event('startup')
def recover_interrupted_jobs():
    for p in store.listing():
        if p['status'] in ['building','deploying']:
            p.update(status='failed',error='Server restarted during this job. Retry the build or deployment.')
            store.save(p)
@app.get('/')
def root():return {'status':'ok','docs':'/docs'}
