# 📋 BIS Standards Finder
### AI-powered BIS compliance recommendations for Indian MSEs

> A production-ready RAG (Retrieval Augmented Generation) system that searches through BIS SP 21 and recommends the most relevant Indian Standards for any product or manufacturing process — powered by Google Gemini 1.5 Flash + ChromaDB.

---

## 🚀 Features

- 🤖 **AI-Powered Search** — Google Gemini 1.5 Flash with anti-hallucination prompting
- 🔍 **Semantic Retrieval** — ChromaDB vector search with `all-MiniLM-L6-v2` embeddings  
- 📚 **BIS SP 21 Coverage** — Cement, Steel, Concrete, Aggregates, Building Materials
- 🎨 **Professional UI** — Streamlit app styled like a real SaaS product
- ⚡ **Judge-Ready CLI** — `inference.py` never crashes, always returns structured JSON
- 📊 **Evaluation Harness** — Precision scoring across test queries

---

## 📁 Folder Structure

```
bis-rag/
├── src/
│   ├── ingest.py          # PDF → ChromaDB ingestion pipeline
│   ├── retriever.py       # Cosine similarity retrieval from ChromaDB
│   ├── rag_pipeline.py    # Gemini LLM + retrieval = recommendations
│   └── app.py             # Streamlit web UI
├── data/
│   ├── BIS_SP21.pdf       # ← Place your PDF here (not included)
│   ├── test.json          # Sample test queries for judges
│   └── results.json       # Output from inference.py
├── inference.py           # CLI entry point for judges
├── eval_script.py         # Evaluation / precision scoring
├── requirements.txt       # Python dependencies
├── .env.example           # Environment variable template
└── README.md
```

---

## ⚙️ Setup (Step-by-Step)

### Step 1 — Clone and enter the project

```bash
cd bis-rag
```

### Step 2 — Create a virtual environment (recommended)

```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate
```

### Step 3 — Install dependencies

```bash
pip install -r requirements.txt
```

### Step 4 — Set your Gemini API key

```bash
# Copy the example file
copy .env.example .env        # Windows
cp .env.example .env          # macOS/Linux

# Edit .env and add your key:
# GEMINI_API_KEY=your_key_here
```

> 🔑 Get a free Gemini API key at: https://aistudio.google.com/app/apikey

### Step 5 — Place the BIS SP 21 PDF

Copy your `BIS_SP21.pdf` into the `data/` folder:
```
bis-rag/data/BIS_SP21.pdf
```

---

## 📥 Ingest the PDF

This only needs to be done once (or when the PDF changes):

```bash
python src/ingest.py --pdf data/BIS_SP21.pdf
```

Expected output:
```
[1/4] Loading sentence-transformer model...
[2/4] Parsing PDF pages with pdfplumber...
[3/4] Chunking text and generating embeddings...
[4/4] Storing chunks in ChromaDB...
✅ Ingestion complete! 1,247 chunks stored.
```

---

## 🎨 Run the Streamlit UI

```bash
streamlit run src/app.py
```

Opens at: **http://localhost:8501**

---

## 🏁 Run Inference (For Judges)

```bash
python inference.py --input data/test.json --output data/results.json
```

**Input format** (`test.json`):
```json
[
  {"id": "q1", "query": "I manufacture Portland cement OPC 53 grade."},
  {"id": "q2", "query": "We produce TMT steel reinforcement bars."}
]
```

**Output format** (`results.json`):
```json
[
  {"id": "q1", "retrieved_standards": ["IS 269", "IS 8112"], "latency_seconds": 1.4},
  {"id": "q2", "retrieved_standards": ["IS 1786", "IS 432"], "latency_seconds": 1.2}
]
```

---

## 📊 Run Evaluation

```bash
python eval_script.py
```

Outputs precision scores per query and saves to `data/eval_results.json`.

---

## 🌍 Environment Variables

| Variable | Description | Required |
|---|---|---|
| `GEMINI_API_KEY` | Google Gemini API key (free tier) | ✅ Yes |

---

## 🧪 Tech Stack

| Component | Technology |
|---|---|
| LLM | Google Gemini 1.5 Flash |
| Vector DB | ChromaDB (local, persistent) |
| Embeddings | `all-MiniLM-L6-v2` (sentence-transformers) |
| PDF Parsing | pdfplumber |
| RAG Framework | LangChain |
| UI | Streamlit |
| Language | Python 3.10+ |

---

## 📌 Quick Command Reference

```bash
# 1. Install dependencies
pip install -r requirements.txt

# 2. Ingest PDF
python src/ingest.py --pdf data/BIS_SP21.pdf

# 3. Launch UI
streamlit run src/app.py

# 4. Run inference (for judges)
python inference.py --input data/test.json --output data/results.json

# 5. Evaluate
python eval_script.py
```

---

*Built for AI Hackathon — BIS Standards Recommendation Engine using RAG*
