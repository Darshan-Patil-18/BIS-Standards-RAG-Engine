"""
BIS Standards Finder — Streamlit UI
Complete UI Redesign with Groq + FAISS Backend
Run: streamlit run src/app.py
"""

import sys
import os
import time

sys.path.insert(0, os.path.dirname(__file__))

import streamlit as st

# ── Page Config ───────────────────────────────────────────────────────────────
st.set_page_config(
    layout="wide",
    page_title="BIS Standards Finder",
    page_icon="📋",
    initial_sidebar_state="expanded"
)

with st.spinner("Loading BIS Standards Engine..."):
    import time
    time.sleep(0)

# ── Custom CSS ────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');

.stSpinner { color: #1E3A5F !important; }

html, body, [class*="css"] {
    font-family: 'Inter', sans-serif;
}

#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

.stApp { background: #F8FAFC; }

/* ---- Sidebar Dark Blue Theme ---- */
[data-testid="stSidebar"] {
    background-color: #0F172A !important;
}
[data-testid="stSidebar"] * {
    color: #E2E8F0 !important;
}
.sidebar-title {
    font-size: 0.9rem;
    font-weight: 700;
    color: #38BDF8 !important;
    text-transform: uppercase;
    letter-spacing: 1px;
    margin-bottom: 12px;
    border-bottom: 1px solid #1E293B;
    padding-bottom: 8px;
    margin-top: 24px;
}
.sidebar-text {
    font-size: 0.9rem;
    line-height: 1.6;
    color: #94A3B8 !important;
}
.step-item {
    display: flex;
    align-items: flex-start;
    gap: 12px;
    margin-bottom: 14px;
}
.step-num {
    background: #38BDF8;
    color: #0F172A !important;
    font-size: 0.75rem;
    font-weight: 800;
    width: 20px;
    height: 20px;
    border-radius: 50%;
    display: flex;
    align-items: center;
    justify-content: center;
    flex-shrink: 0;
    margin-top: 2px;
}
.db-status {
    background: rgba(16, 185, 129, 0.1);
    border: 1px solid rgba(16, 185, 129, 0.2);
    border-radius: 8px;
    padding: 12px;
    display: flex;
    align-items: center;
    gap: 10px;
    margin-top: 8px;
}
.status-dot {
    width: 10px; height: 10px;
    border-radius: 50%;
    background: #10B981;
    box-shadow: 0 0 8px #10B981;
}

/* ---- Hero Section ---- */
.hero-box {
    background: linear-gradient(135deg, #1E3A8A 0%, #3B82F6 100%);
    border-radius: 16px;
    padding: 40px 48px;
    margin-bottom: 32px;
    color: white;
    box-shadow: 0 10px 25px -5px rgba(37, 99, 235, 0.3);
}
.hero-box h1 {
    font-size: 2.8rem;
    font-weight: 800;
    margin: 0 0 8px;
    color: white !important;
}
.hero-box p {
    font-size: 1.15rem;
    font-weight: 500;
    margin: 0;
    color: rgba(255, 255, 255, 0.9) !important;
}

/* ---- Input Area ---- */
.stTextArea textarea {
    color: #1a1a2e !important;
    background-color: #ffffff !important;
    border: 2px solid #2E86AB !important;
    border-radius: 12px !important;
    font-size: 1rem !important;
    padding: 12px !important;
    caret-color: #1a1a2e !important;
}
.stTextArea textarea::placeholder {
    color: #94a3b8 !important;
    opacity: 1 !important;
}
.stTextArea label {
    color: #1E3A5F !important;
    font-weight: 600 !important;
    font-size: 1rem !important;
}

/* ---- Buttons ---- */
.stButton > button {
    border-radius: 20px !important;
    border: 1px solid #CBD5E1 !important;
    background: white !important;
    color: #334155 !important;
    font-weight: 600 !important;
    transition: all 0.2s !important;
}
.stButton > button:hover {
    border-color: #3B82F6 !important;
    color: #3B82F6 !important;
    background: #EFF6FF !important;
}
div[data-testid="stButton"].primary-search > button {
    background: #2563EB !important;
    color: white !important;
    border: none !important;
    border-radius: 12px !important;
    font-size: 1.1rem !important;
    font-weight: 700 !important;
    padding: 14px 24px !important;
    width: 100% !important;
    box-shadow: 0 4px 12px rgba(37, 99, 235, 0.3) !important;
}
div[data-testid="stButton"].primary-search > button:hover {
    background: #1D4ED8 !important;
    box-shadow: 0 6px 16px rgba(37, 99, 235, 0.4) !important;
}

/* ---- Metrics ---- */
.metric-card {
    background: white;
    border-radius: 12px;
    padding: 24px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
    text-align: center;
}
.metric-value { font-size: 2.5rem; font-weight: 800; color: #0F172A; line-height: 1; }
.metric-label { font-size: 0.85rem; font-weight: 600; color: #64748B; text-transform: uppercase; margin-top: 8px; }

/* ---- Results ---- */
.raw-results-notice {
    background: #FFFBEB;
    border: 1px solid #FEF3C7;
    border-left: 4px solid #F59E0B;
    padding: 16px 20px;
    border-radius: 8px;
    color: #B45309;
    font-weight: 600;
    margin-bottom: 24px;
    font-size: 0.95rem;
}
.result-card {
    background: white;
    border-radius: 16px;
    padding: 28px;
    border: 1px solid #E2E8F0;
    box-shadow: 0 4px 12px -2px rgba(0, 0, 0, 0.05);
    margin-bottom: 20px;
    position: relative;
}
.is-badge {
    display: inline-block;
    background: #2563EB;
    color: white;
    font-weight: 700;
    padding: 6px 16px;
    border-radius: 20px;
    font-size: 0.9rem;
    margin-bottom: 12px;
}
.std-title { font-size: 1.2rem; font-weight: 800; color: #0F172A; margin-bottom: 12px; line-height: 1.4; }
.rationale { background: #F8FAFC; padding: 16px; border-radius: 8px; border-left: 3px solid #3B82F6; color: #334155; font-size: 0.95rem; line-height: 1.6; margin-bottom: 20px; }
.conf-outer { background: #E2E8F0; border-radius: 8px; height: 8px; width: 100%; overflow: hidden; margin-top: 6px; }
.conf-inner { height: 100%; border-radius: 8px; }
.page-ref { font-size: 0.8rem; color: #94A3B8; font-weight: 500; margin-top: 16px; text-transform: uppercase; letter-spacing: 0.5px; }
</style>
""", unsafe_allow_html=True)


# ── Lazy imports ──────────────────────────────────────────────────────────────
@st.cache_resource(show_spinner=False)
def load_pipeline():
    try:
        from rag_pipeline import get_recommendations
        from retriever import get_collection_count
        return get_recommendations, get_collection_count, None
    except Exception as e:
        return None, None, str(e)


get_recs_fn, get_count_fn, load_error = load_pipeline()

if "query_text" not in st.session_state:
    st.session_state.query_text = ""
if "results" not in st.session_state:
    st.session_state.results = None


# ── Sidebar (Dark Blue Theme) ─────────────────────────────────────────────────
with st.sidebar:
    st.markdown('<div class="sidebar-title">About</div>', unsafe_allow_html=True)
    st.markdown('<div class="sidebar-text">BIS Standards Finder uses AI-powered Retrieval Augmented Generation (RAG) to search through BIS SP 21 and recommend the most relevant Indian Standards for your product.</div>', unsafe_allow_html=True)

    st.markdown('<div class="sidebar-title">How to Use</div>', unsafe_allow_html=True)
    steps = [
        "Describe your product or manufacturing process.",
        "Click 'Find BIS Standards'.",
        "Review the recommended IS codes and rationale."
    ]
    for i, step in enumerate(steps, 1):
        st.markdown(f"""
        <div class="step-item">
            <div class="step-num">{i}</div>
            <div class="sidebar-text">{step}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="sidebar-title">Database Status</div>', unsafe_allow_html=True)
    count = get_count_fn() if get_count_fn else 0
    st.markdown(f"""
    <div class="db-status">
        <div class="status-dot"></div>
        <div style="font-weight:600;font-size:0.95rem;color:#E2E8F0;">{count:,} standards indexed</div>
    </div>
    """, unsafe_allow_html=True)


# ── Hero Section ──────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-box">
    <h1>BIS Standards Finder</h1>
    <p>AI-powered compliance engine for Indian MSEs — find the right standards instantly</p>
</div>
""", unsafe_allow_html=True)


# ── Search Section ────────────────────────────────────────────────────────────
st.markdown('<div style="font-weight:700;color:#0F172A;margin-bottom:8px;font-size:1.1rem;">Describe your product or manufacturing process</div>', unsafe_allow_html=True)

query_input = st.text_area(
    label="Product description",
    value=st.session_state.query_text,
    height=100,
    placeholder="e.g. I manufacture Portland cement OPC 53 grade for structural construction...",
    label_visibility="collapsed",
    key="query_area",
)

btn_cols = st.columns(4)
examples = [
    "Portland Cement",
    "TMT Steel Bars",
    "Fly Ash Bricks",
    "Ready Mix Concrete"
]
for col, ex in zip(btn_cols, examples):
    with col:
        if st.button(ex, use_container_width=True):
            st.session_state.query_text = f"I manufacture {ex.lower()}"
            st.rerun()

st.markdown("<br/>", unsafe_allow_html=True)
st.markdown('<div class="primary-search">', unsafe_allow_html=True)
search_clicked = st.button("Find BIS Standards", type="primary", use_container_width=True)
st.markdown('</div>', unsafe_allow_html=True)


# ── Results Section ───────────────────────────────────────────────────────────
st.markdown("<br/><br/>", unsafe_allow_html=True)
effective_query = st.session_state.query_text or query_input

if search_clicked and effective_query.strip():
    with st.spinner("Searching BIS Database..."):
        try:
            st.session_state.results = get_recs_fn(effective_query, top_k=5)
        except Exception:
            st.session_state.results = None


if st.session_state.results:
    res = st.session_state.results
    recs = res.get("recommendations", [])
    raw_recs = res.get("raw_results", [])
    latency = res.get("latency_seconds", 0)

    # Calculate standards found (prefer AI recs, fallback to raw)
    num_found = len(recs) if recs else len(raw_recs)

    if num_found > 0:
        # ── Metrics Row (2 columns only) ──
        m1, m2 = st.columns(2)
        with m1:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{num_found}</div><div class="metric-label">Standards Found</div></div>', unsafe_allow_html=True)
        with m2:
            st.markdown(f'<div class="metric-card"><div class="metric-value">{latency}s</div><div class="metric-label">Response Time</div></div>', unsafe_allow_html=True)
        
        st.markdown("<br/>", unsafe_allow_html=True)

        # ── Display Results ──
        if recs:
            # Groq worked
            for rec in recs:
                code  = rec.get("standard_code", "Unknown")
                title = rec.get("standard_title", "BIS Standard")
                rat   = rec.get("rationale", "")
                conf  = rec.get("confidence", 50)
                page  = rec.get("page_number", 0)

                color = "#10B981" if conf >= 80 else ("#F59E0B" if conf >= 50 else "#EF4444")

                st.markdown(f"""
                <div class="result-card">
                    <div class="is-badge">{code}</div>
                    <div class="std-title">{title}</div>
                    <div class="rationale">{rat}</div>
                    <div style="display:flex;justify-content:space-between;font-size:0.85rem;font-weight:600;color:#64748B;">
                        <span>Confidence Score</span>
                        <span style="color:{color};">{conf}%</span>
                    </div>
                    <div class="conf-outer"><div class="conf-inner" style="width:{conf}%;background:{color};"></div></div>
                    <div class="page-ref">📄 Reference: SP 21, Page {page}</div>
                </div>
                """, unsafe_allow_html=True)
        else:
            # Fallback to FAISS raw results
            st.markdown('<div class="raw-results-notice">Showing matched standards from database. Add Groq API key for AI-generated rationale.</div>', unsafe_allow_html=True)
            for rec in raw_recs:
                code  = rec.get("standard_code", "Unknown")
                title = rec.get("standard_title", "BIS Standard")
                page  = rec.get("page_number", 0)
                
                st.markdown(f"""
                <div class="result-card">
                    <div class="is-badge">{code}</div>
                    <div class="std-title">{title}</div>
                    <div class="page-ref">📄 Reference: SP 21, Page {page}</div>
                </div>
                """, unsafe_allow_html=True)
    else:
        st.markdown("""
        <div style="text-align:center;padding:60px 20px;background:white;border-radius:16px;border:1px dashed #CBD5E1;">
            <div style="font-size:3rem;margin-bottom:16px;">🤔</div>
            <div style="font-size:1.2rem;font-weight:700;color:#0F172A;">No Standards Found</div>
            <div style="color:#64748B;margin-top:8px;">Try refining your product description.</div>
        </div>
        """, unsafe_allow_html=True)

elif not search_clicked and not effective_query:
    st.markdown("""
    <div style="text-align:center;padding:60px 20px;background:white;border-radius:16px;border:1px dashed #CBD5E1;color:#64748B;">
        <div style="font-size:2.5rem;margin-bottom:16px;">🔍</div>
        <div style="font-size:1.1rem;font-weight:600;">Enter a product description to begin</div>
    </div>
    """, unsafe_allow_html=True)
