"""Verify MongoDB and optionally copy existing local projects."""
import argparse
import sys
from pathlib import Path
from dotenv import load_dotenv
ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / "backend/.env")
sys.path.insert(0, str(ROOT / "backend"))
from modules.utilities import store

parser = argparse.ArgumentParser()
parser.add_argument("--migrate", action="store_true")
args = parser.parse_args()
try:
    collection = store.mongo_collection()
    if collection is None:
        raise RuntimeError("Add MONGODB_URI to backend/.env first.")
    print("MongoDB connection verified.")
    if args.migrate:
        print(f"Copied {store.migrate_sqlite()} projects; existing MongoDB records were preserved.")
finally:
    store.close()
