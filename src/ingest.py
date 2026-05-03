"""
BIS Standards Ingestion Pipeline
Parses BIS SP21 PDF and stores chunks in a FAISS index with sentence-transformer embeddings.
Usage: python src/ingest.py --pdf data/BIS_SP21.pdf
"""

import argparse
import json
import os
import re
import sys
import time

import numpy as np
import faiss
import pdfplumber
from sentence_transformers import SentenceTransformer

# ── Constants ─────────────────────────────────────────────────────────────────
INDEX_DIR      = "./faiss_index"
INDEX_FILE     = os.path.join(INDEX_DIR, "index.faiss")
METADATA_FILE  = os.path.join(INDEX_DIR, "metadata.json")
EMBED_MODEL    = "all-MiniLM-L6-v2"
CHUNK_SIZE     = 500   # approx words
CHUNK_OVERLAP  = 50


# ── Text helpers ──────────────────────────────────────────────────────────────
def chunk_text(text: str, chunk_size: int = CHUNK_SIZE, overlap: int = CHUNK_OVERLAP):
    words = text.split()
    chunks, start = [], 0
    while start < len(words):
        chunks.append(" ".join(words[start:start + chunk_size]))
        start += chunk_size - overlap
    return chunks


IS_CODE_RE = re.compile(
    r"\b(IS[:\s]?\d{2,6}(?:[:\s]\d{4})?(?:\s*\(Part\s*\d+\))?)\b", re.IGNORECASE
)
TITLE_RE = re.compile(
    r"(?:IS[:\s]?\d{2,6}[^—\n]*?)[—–:]\s*([A-Z][^\n]{5,80})", re.IGNORECASE
)


def extract_standard_code(text: str) -> str:
    m = IS_CODE_RE.search(text)
    return m.group(1).strip() if m else "Unknown"


def extract_standard_title(text: str) -> str:
    m = TITLE_RE.search(text)
    if m:
        return m.group(1).strip()
    lines = [l.strip() for l in text.splitlines() if len(l.strip()) > 20]
    return lines[0][:120] if lines else "BIS Standard"


# ── Main ingestion ─────────────────────────────────────────────────────────────
def ingest(pdf_path: str):
    if not os.path.exists(pdf_path):
        print(f"[ERROR] PDF not found: {pdf_path}")
        sys.exit(1)

    print(f"\n{'='*60}")
    print(f"  BIS Standards Ingestion Pipeline (FAISS)")
    print(f"{'='*60}")
    print(f"  PDF        : {pdf_path}")
    print(f"  Index dir  : {INDEX_DIR}")
    print(f"  Embeddings : {EMBED_MODEL}")
    print(f"{'='*60}\n")

    os.makedirs(INDEX_DIR, exist_ok=True)

    # Step 1 ── Load embedding model
    print("[1/4] Loading sentence-transformer model...")
    model = SentenceTransformer(EMBED_MODEL)
    print(f"      ✓ Model loaded.\n")

    # Step 2 ── Parse PDF
    print("[2/4] Parsing PDF with pdfplumber...")
    pages_data = []
    with pdfplumber.open(pdf_path) as pdf:
        total = len(pdf.pages)
        print(f"      Total pages: {total}")
        for i, page in enumerate(pdf.pages, 1):
            text = (page.extract_text() or "").strip()
            if text:
                pages_data.append({"page_number": i, "text": text})
            if i % 50 == 0 or i == total:
                print(f"      Parsed {i}/{total} pages...", end="\r")
    print(f"\n      ✓ Text extracted from {len(pages_data)} pages.\n")

    # Step 3 ── Chunk & embed
    print("[3/4] Chunking and generating embeddings...")
    chunks, metadatas = [], []
    for page in pages_data:
        for chunk in chunk_text(page["text"]):
            if len(chunk.split()) < 20:
                continue
            chunks.append(chunk)
            metadatas.append({
                "page_number":    page["page_number"],
                "standard_code":  extract_standard_code(chunk),
                "standard_title": extract_standard_title(chunk),
                "content":        chunk,
            })

    print(f"      Total chunks: {len(chunks)}")
    print("      Generating embeddings (may take a minute)...")
    t0 = time.time()
    embeddings = model.encode(
        chunks, batch_size=64, show_progress_bar=True, convert_to_numpy=True
    ).astype("float32")
    print(f"      ✓ Done in {time.time()-t0:.1f}s  |  Shape: {embeddings.shape}\n")

    # Normalise for cosine similarity (inner product on unit vectors = cosine)
    faiss.normalize_L2(embeddings)

    # Step 4 ── Build & save FAISS index
    print("[4/4] Building FAISS index and saving to disk...")
    dim   = embeddings.shape[1]
    index = faiss.IndexFlatIP(dim)   # Inner-product on normalised → cosine
    index.add(embeddings)
    faiss.write_index(index, INDEX_FILE)

    with open(METADATA_FILE, "w", encoding="utf-8") as f:
        json.dump(metadatas, f, ensure_ascii=False)

    print(f"\n{'='*60}")
    print(f"  ✅  Ingestion complete!")
    print(f"  📦 Chunks indexed : {index.ntotal:,}")
    print(f"  💾 Index file     : {INDEX_FILE}")
    print(f"  📄 Metadata file  : {METADATA_FILE}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Ingest BIS SP21 PDF into FAISS")
    parser.add_argument("--pdf", default="data/BIS_SP21.pdf", help="Path to BIS SP21 PDF")
    args = parser.parse_args()
    ingest(args.pdf)
