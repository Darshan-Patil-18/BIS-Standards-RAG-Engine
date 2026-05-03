from sentence_transformers import SentenceTransformer
import faiss
import json
import numpy as np
import os

FAISS_DIR = "./faiss_index"
_model = None

def get_model():
    global _model
    if _model is None:
        print("[INFO] Loading embedding model...")
        _model = SentenceTransformer("all-MiniLM-L6-v2")
    return _model

def get_collection_count():
    meta_path = os.path.join(FAISS_DIR, "metadata.json")
    if os.path.exists(meta_path):
        try:
            with open(meta_path, "r", encoding="utf-8") as f:
                return len(json.load(f))
        except Exception:
            return 0
    return 0

def retrieve(query: str, top_k: int = 5) -> list:
    model = get_model()
    
    index_path = os.path.join(FAISS_DIR, "index.faiss")
    meta_path = os.path.join(FAISS_DIR, "metadata.json")
    
    if not os.path.exists(index_path):
        print("[ERROR] FAISS index not found. Run ingest.py first.")
        return []
    
    index = faiss.read_index(index_path)
    
    with open(meta_path, "r", encoding="utf-8") as f:
        metadata = json.load(f)
    
    # Embed query exactly same way as ingestion
    query_vector = model.encode([query], normalize_embeddings=True)
    query_vector = np.array(query_vector, dtype="float32")
    
    distances, indices = index.search(query_vector, top_k)
    
    results = []
    for i, idx in enumerate(indices[0]):
        if idx == -1 or idx >= len(metadata):
            continue
        meta = metadata[idx]
        score = float(distances[0][i])
        results.append({
            "standard_code": meta.get("standard_code", "Unknown"),
            "standard_title": meta.get("standard_title", ""),
            "content": meta.get("content", ""),
            "relevance_score": round(score, 4),
            "page_number": meta.get("page_number", 0)
        })
    
    # Debug print — remove after testing
    print(f"[DEBUG] Query: {query[:60]}")
    print(f"[DEBUG] Top results: {[r['standard_code'] for r in results]}")
    print(f"[DEBUG] Scores: {[r['relevance_score'] for r in results]}")
    
    return results
