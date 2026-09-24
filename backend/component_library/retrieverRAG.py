import json
import os
import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

_GLOBAL_RAG = None

class LocalComponentRAG:
    def __init__(self, catalog_path=None):
        if not catalog_path or not os.path.exists(catalog_path):
            catalog_path = Path(__file__).resolve().parent / "data" / "catalog.json"
            
        with open(catalog_path, "r", encoding="utf-8") as f:
            self.catalog = json.load(f)
        
        self.vectorizer = TfidfVectorizer(stop_words='english', token_pattern=r'(?u)\b\w+\b')
        self.corpus = [self._get_searchable_text(c) for c in self.catalog]
        self.matrix = self.vectorizer.fit_transform(self.corpus)

    def _get_searchable_text(self, comp):
        name = comp.get("name", "")
        split_name = re.sub(r'([a-z0-9])([A-Z])', r'\1 \2', name)
        if 'Searchbar' in name:
            split_name += ' search bar'
        category = comp.get("category", "")
        description = comp.get("description", "")
        props = " ".join(comp.get("props", []))
        return f"{name} {split_name} {name} {category} {category} {description} {props}"

    def retrieve_components(self, query: str, top_k: int = 5):
        if not query or not query.strip():
            return []
        query_vec = self.vectorizer.transform([query])
        scores = cosine_similarity(query_vec, self.matrix).flatten()
        top_indices = scores.argsort()[::-1][:top_k]
        
        results = []
        for idx in top_indices:
            score_val = float(scores[idx])
            comp = self.catalog[idx]
            results.append({
                "name": comp.get("name"),
                "category": comp.get("category"),
                "score": score_val,
                "description": comp.get("description", ""),
                "props": comp.get("props", [])[:8],
                "import_path": comp.get("import_path", "react-native-paper")
            })
        return results

def get_rag_components(query: str, top_k: int = 4):
    global _GLOBAL_RAG
    if _GLOBAL_RAG is None:
        _GLOBAL_RAG = LocalComponentRAG()
    return _GLOBAL_RAG.retrieve_components(query, top_k)