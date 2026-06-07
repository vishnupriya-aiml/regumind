# dashboard/app.py
# ReguMind Enterprise Dashboard - Upgraded Version
# Features: Chat history, Document manager, Analytics, Health monitor,
# Advanced AI controls, Caching, Response time, Professional dark UI

import streamlit as st
import httpx
import json
import time
from datetime import datetime
import random

# ─────────────────────────────────────────
# PAGE CONFIG - Must be first Streamlit call
# ─────────────────────────────────────────
st.set_page_config(
    page_title="ReguMind Enterprise",
    page_icon="🧠",
    layout="wide",
    initial_sidebar_state="expanded"
)

API_URL = "http://regumind_api:8000"

# ─────────────────────────────────────────
# CUSTOM CSS - Makes it look professional
# ─────────────────────────────────────────
st.markdown("""
<style>
    /* Main background */
    .stApp {
        background-color: #0e1117;
        color: #ffffff;
    }

    /* Sidebar */
    [data-testid="stSidebar"] {
        background-color: #161b22;
        border-right: 1px solid #30363d;
    }

    /* Cards */
    .metric-card {
        background: linear-gradient(135deg, #1f2937, #111827);
        border: 1px solid #374151;
        border-radius: 12px;
        padding: 20px;
        margin: 8px 0;
        text-align: center;
    }

    .metric-value {
        font-size: 2rem;
        font-weight: bold;
        color: #60a5fa;
    }

    .metric-label {
        font-size: 0.85rem;
        color: #9ca3af;
        margin-top: 4px;
    }

    /* Chat bubbles */
    .chat-user {
        background: linear-gradient(135deg, #1d4ed8, #1e40af);
        border-radius: 18px 18px 4px 18px;
        padding: 12px 18px;
        margin: 8px 0;
        margin-left: 20%;
        color: white;
        font-size: 0.95rem;
    }

    .chat-assistant {
        background: linear-gradient(135deg, #1f2937, #111827);
        border: 1px solid #374151;
        border-radius: 18px 18px 18px 4px;
        padding: 12px 18px;
        margin: 8px 0;
        margin-right: 10%;
        color: #e5e7eb;
        font-size: 0.95rem;
    }

    .chat-meta {
        font-size: 0.75rem;
        color: #6b7280;
        margin-top: 4px;
    }

    /* Confidence badge */
    .badge-high {
        background: #065f46;
        color: #6ee7b7;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }

    .badge-medium {
        background: #78350f;
        color: #fcd34d;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }

    .badge-low {
        background: #7f1d1d;
        color: #fca5a5;
        padding: 3px 10px;
        border-radius: 20px;
        font-size: 0.8rem;
        font-weight: bold;
    }

    /* Section headers */
    .section-header {
        font-size: 1.3rem;
        font-weight: bold;
        color: #60a5fa;
        border-bottom: 2px solid #1d4ed8;
        padding-bottom: 8px;
        margin-bottom: 16px;
    }

    /* Document card */
    .doc-card {
        background: #1f2937;
        border: 1px solid #374151;
        border-radius: 10px;
        padding: 14px;
        margin: 6px 0;
    }

    /* Status dot */
    .status-online {
        display: inline-block;
        width: 10px;
        height: 10px;
        background: #10b981;
        border-radius: 50%;
        margin-right: 6px;
        animation: pulse 2s infinite;
    }

    @keyframes pulse {
        0% { opacity: 1; }
        50% { opacity: 0.4; }
        100% { opacity: 1; }
    }

    /* Button styling */
    .stButton > button {
        background: linear-gradient(135deg, #1d4ed8, #7c3aed);
        color: white;
        border: none;
        border-radius: 8px;
        font-weight: bold;
        transition: all 0.3s;
    }

    .stButton > button:hover {
        transform: translateY(-2px);
        box-shadow: 0 4px 15px rgba(99, 102, 241, 0.4);
    }

    /* Input fields */
    .stTextArea textarea, .stTextInput input {
        background: #1f2937 !important;
        border: 1px solid #374151 !important;
        color: white !important;
        border-radius: 8px !important;
    }

    /* Tabs */
    .stTabs [data-baseweb="tab-list"] {
        background: #161b22;
        border-radius: 10px;
        padding: 4px;
    }

    .stTabs [data-baseweb="tab"] {
        color: #9ca3af;
        font-weight: bold;
    }

    .stTabs [aria-selected="true"] {
        background: #1d4ed8 !important;
        color: white !important;
        border-radius: 8px;
    }

    /* Hide default streamlit menu */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# SESSION STATE - stores data between clicks
# Session state is like short term memory
# for the dashboard. Without it everything
# resets every time you click a button.
# ─────────────────────────────────────────
if 'chat_history' not in st.session_state:
    st.session_state.chat_history = []

if 'query_cache' not in st.session_state:
    st.session_state.query_cache = {}

if 'analytics' not in st.session_state:
    st.session_state.analytics = {
        'total_queries': 0,
        'avg_confidence': 0,
        'confidence_scores': [],
        'response_times': [],
        'queries_list': []
    }

if 'ingested_docs' not in st.session_state:
    st.session_state.ingested_docs = []


# ─────────────────────────────────────────
# HELPER FUNCTIONS
# ─────────────────────────────────────────
def get_health():
    try:
        r = httpx.get(f"{API_URL}/health", timeout=5)
        return r.json()
    except:
        return None


def get_stats():
    try:
        r = httpx.get(f"{API_URL}/stats", timeout=5)
        return r.json()
    except:
        return None


def get_confidence_badge(score):
    if score >= 0.9:
        return f'<span class="badge-high">✅ {score:.0%} High</span>'
    elif score >= 0.7:
        return f'<span class="badge-medium">⚠️ {score:.0%} Medium</span>'
    else:
        return f'<span class="badge-low">❌ {score:.0%} Low</span>'


# ─────────────────────────────────────────
# SIDEBAR
# ─────────────────────────────────────────
with st.sidebar:
    st.markdown("## 🧠 ReguMind")
    st.markdown("*Enterprise RAG Platform*")
    st.divider()

    # Live system status
    health = get_health()
    stats = get_stats()

    if health:
        st.markdown('<span class="status-online"></span>**System Online**', unsafe_allow_html=True)
        st.markdown(f"📦 **Docs indexed:** {health.get('total_documents_indexed', 0)}")
        st.markdown(f"🗄️ **Database:** {health.get('vector_database', 'N/A')}")
    else:
        st.error("❌ API Offline")
        st.info("Start the API with:\nuvicorn api.main:app --reload --port 8000")

    st.divider()

    # ── AI CONTROLS ──
    st.markdown("### 🎛️ AI Controls")

    st.markdown("**🌡️ Temperature**")
    st.markdown("*Controls creativity. Low = precise. High = creative.*")
    temperature = st.slider("", 0.0, 1.0, 0.1, 0.05, key="temp", label_visibility="collapsed")
    if temperature < 0.3:
        st.caption("🎯 Precise & Factual")
    elif temperature < 0.7:
        st.caption("⚖️ Balanced")
    else:
        st.caption("🎨 Creative")

    st.markdown("**📊 Top-K Chunks**")
    st.markdown("*How many document pieces to retrieve.*")
    top_k = st.slider("", 1, 10, 3, key="topk", label_visibility="collapsed")

    st.markdown("**🎲 Top-P (Nucleus)**")
    st.markdown("*Controls answer diversity. 1.0 = consider all options.*")
    top_p = st.slider("", 0.1, 1.0, 0.9, 0.05, key="topp", label_visibility="collapsed")

    st.markdown("**📏 Max Tokens**")
    st.markdown("*Maximum length of the answer.*")
    max_tokens = st.select_slider(
        "",
        options=[256, 512, 750, 1000, 1500, 2000],
        value=1000,
        key="maxtok",
        label_visibility="collapsed"
    )

    st.divider()

    # ── OPTIONS ──
    st.markdown("### ⚙️ Options")
    run_hallucination = st.toggle("🔍 Hallucination Check", value=True)
    use_cache = st.toggle("⚡ Answer Cache", value=True)
    show_chunks = st.toggle("📄 Show Source Chunks", value=False)
    show_timing = st.toggle("⏱️ Show Response Time", value=True)

    st.divider()
    st.caption("ReguMind v1.0.0")
    st.caption("Built with ❤️ by Vishnu Priya")


# ─────────────────────────────────────────
# MAIN HEADER
# ─────────────────────────────────────────
st.markdown("""
<div style='text-align:center; padding: 20px 0 10px 0;'>
    <h1 style='font-size:2.5rem; background: linear-gradient(135deg, #60a5fa, #a78bfa);
    -webkit-background-clip: text; -webkit-text-fill-color: transparent;'>
    🧠 ReguMind Enterprise
    </h1>
    <p style='color:#9ca3af; font-size:1rem;'>
    Regulatory Intelligence & Verified RAG Platform
    </p>
</div>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────
# TOP METRICS ROW
# ─────────────────────────────────────────
m1, m2, m3, m4, m5 = st.columns(5)

total_queries = st.session_state.analytics['total_queries']
avg_conf = (sum(st.session_state.analytics['confidence_scores']) /
            len(st.session_state.analytics['confidence_scores'])
            if st.session_state.analytics['confidence_scores'] else 0)
avg_time = (sum(st.session_state.analytics['response_times']) /
            len(st.session_state.analytics['response_times'])
            if st.session_state.analytics['response_times'] else 0)
docs_indexed = health.get('total_documents_indexed', 0) if health else 0
cache_hits = len([q for q in st.session_state.analytics['queries_list']
                  if q.get('cached', False)])

with m1:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>🔍 {total_queries}</div>
        <div class='metric-label'>Total Queries</div>
    </div>""", unsafe_allow_html=True)

with m2:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>📊 {avg_conf:.0%}</div>
        <div class='metric-label'>Avg Confidence</div>
    </div>""", unsafe_allow_html=True)

with m3:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>⚡ {avg_time:.1f}s</div>
        <div class='metric-label'>Avg Response Time</div>
    </div>""", unsafe_allow_html=True)

with m4:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>📦 {docs_indexed}</div>
        <div class='metric-label'>Docs Indexed</div>
    </div>""", unsafe_allow_html=True)

with m5:
    st.markdown(f"""<div class='metric-card'>
        <div class='metric-value'>💾 {cache_hits}</div>
        <div class='metric-label'>Cache Hits</div>
    </div>""", unsafe_allow_html=True)

st.divider()

# ─────────────────────────────────────────
# MAIN TABS
# ─────────────────────────────────────────
tab1, tab2, tab3, tab4, tab5 = st.tabs([
    "💬 Ask ReguMind",
    "📄 Documents",
    "📊 Analytics",
    "🖥️ System Health",
    "📜 Chat History"
])


# ══════════════════════════════════════════
# TAB 1 — ASK REGUMIND
# ══════════════════════════════════════════
with tab1:
    col_chat, col_info = st.columns([3, 1])

    with col_chat:
        st.markdown('<div class="section-header">💬 Ask ReguMind</div>',
                    unsafe_allow_html=True)

        # Show recent chat history in chat bubble style
        if st.session_state.chat_history:
            st.markdown("**Recent conversation:**")
            # Show last 3 exchanges
            recent = st.session_state.chat_history[-3:]
            for entry in recent:
                st.markdown(f"""
                <div class='chat-user'>
                    🧑 {entry['question']}
                    <div class='chat-meta'>{entry['timestamp']}</div>
                </div>""", unsafe_allow_html=True)

                answer_preview = entry['answer'][:300] + "..." \
                    if len(entry['answer']) > 300 else entry['answer']
                cached_tag = " ⚡ cached" if entry.get('cached') else ""
                st.markdown(f"""
                <div class='chat-assistant'>
                    🧠 {answer_preview}
                    <div class='chat-meta'>
                        Confidence: {entry.get('confidence', 0):.0%} |
                        Time: {entry.get('response_time', 0):.2f}s{cached_tag}
                    </div>
                </div>""", unsafe_allow_html=True)

            st.divider()

        # Question input
        question = st.text_area(
            "Your question",
            placeholder="Example: What are the hallucination detection requirements?",
            height=100,
            key="question_input"
        )

        col_btn1, col_btn2, col_btn3 = st.columns([2, 1, 1])
        with col_btn1:
            ask_clicked = st.button("🧠 Ask ReguMind", type="primary",
                                    use_container_width=True)
        with col_btn2:
            clear_clicked = st.button("🗑️ Clear History",
                                      use_container_width=True)
        with col_btn3:
            if st.button("🎲 Random Q", use_container_width=True):
                sample_questions = [
                    "What are the success metrics?",
                    "What is the technology stack?",
                    "What are the functional requirements?",
                    "What are the risks and mitigations?",
                    "Who are the stakeholders?"
                ]
                st.session_state['random_q'] = random.choice(sample_questions)
                st.info(f"Try asking: *{st.session_state['random_q']}*")

        if clear_clicked:
            st.session_state.chat_history = []
            st.session_state.query_cache = {}
            st.rerun()

        # ── PROCESS QUESTION ──
        if ask_clicked and question:
            cache_key = question.strip().lower()
            is_cached = False

            # Check cache first
            if use_cache and cache_key in st.session_state.query_cache:
                is_cached = True
                result = st.session_state.query_cache[cache_key]
                response_time = 0.01
                st.success("⚡ Instant answer from cache!")
            else:
                # Call the API
                start_time = time.time()

                with st.spinner("🔍 Searching documents..."):
                    time.sleep(0.3)

                with st.spinner("🧠 Generating verified answer..."):
                    try:
                        response = httpx.post(
                            f"{API_URL}/ask",
                            json={
                                "question": question,
                                "top_k": top_k,
                                "run_hallucination_check": run_hallucination
                            },
                            timeout=120
                        )
                        result = response.json()
                        response_time = time.time() - start_time

                        # Cache the result
                        if use_cache:
                            st.session_state.query_cache[cache_key] = result

                    except Exception as e:
                        st.error(f"❌ Error: {str(e)}")
                        st.stop()

            # ── DISPLAY ANSWER ──
            confidence = result.get('confidence_score', 0)

            st.markdown("---")
            st.markdown("### 📝 Answer")

            # Streaming effect - display words one by one
            answer_placeholder = st.empty()
            answer_text = result.get('answer', '')
            if not is_cached:
                displayed = ""
                words = answer_text.split()
                for i, word in enumerate(words):
                    displayed += word + " "
                    if i % 8 == 0:
                        answer_placeholder.markdown(displayed + "▌")
                        time.sleep(0.02)
                answer_placeholder.markdown(answer_text)
            else:
                answer_placeholder.markdown(answer_text)

            # Metrics row
            r1, r2, r3, r4 = st.columns(4)
            with r1:
                badge = get_confidence_badge(confidence)
                st.markdown(f"**Confidence:** {badge}",
                            unsafe_allow_html=True)
            with r2:
                if show_timing:
                    if is_cached:
                        st.markdown("**Time:** ⚡ ~0.01s (cached)")
                    else:
                        st.markdown(f"**Time:** ⏱️ {response_time:.2f}s")
            with r3:
                st.markdown(f"**Chunks:** 📄 {result.get('chunks_retrieved', 0)}")
            with r4:
                st.markdown(f"**Model:** 🤖 {result.get('model_used', 'N/A')}")

            # Sources
            sources = list(set(result.get('sources', [])))
            if sources:
                st.markdown("**📁 Sources:**")
                for s in sources:
                    st.markdown(f"- 📄 `{s}`")

            # Flagged sentences
            flagged = result.get('flagged_sentences', [])
            if flagged:
                with st.expander("⚠️ Flagged sentences (not fully supported)"):
                    for f in flagged:
                        st.warning(f)
            elif run_hallucination:
                st.success("✅ All sentences verified against source documents!")

            # Show raw chunks if toggled
            if show_chunks:
                with st.expander("📄 View retrieved source chunks"):
                    search_resp = httpx.post(
                        f"{API_URL}/search",
                        json={"query": question, "top_k": top_k},
                        timeout=30
                    )
                    chunks_data = search_resp.json()
                    for i, chunk in enumerate(chunks_data.get('results', [])):
                        st.markdown(f"**Chunk {i+1}** — Score: `{chunk['hybrid_score']:.4f}`")
                        st.text(chunk['text'][:400])
                        st.divider()

            # Save to history
            st.session_state.chat_history.append({
                'question': question,
                'answer': answer_text,
                'confidence': confidence,
                'response_time': response_time,
                'timestamp': datetime.now().strftime("%H:%M:%S"),
                'cached': is_cached,
                'sources': sources
            })

            # Update analytics
            st.session_state.analytics['total_queries'] += 1
            st.session_state.analytics['confidence_scores'].append(confidence)
            st.session_state.analytics['response_times'].append(response_time)
            st.session_state.analytics['queries_list'].append({
                'question': question[:50],
                'confidence': confidence,
                'time': response_time,
                'cached': is_cached,
                'timestamp': datetime.now().strftime("%H:%M:%S")
            })

    with col_info:
        st.markdown('<div class="section-header">💡 Tips</div>',
                    unsafe_allow_html=True)
        st.info("📌 **Temperature** controls how creative vs precise the answer is. Keep it low (0.1) for regulatory documents.")
        st.info("📌 **Top-K** controls how many document chunks are searched. Higher = more context but slower.")
        st.info("📌 **Cache** stores answers. Same question twice = instant reply.")
        st.info("📌 **Hallucination check** verifies every sentence. Turn off for faster responses.")

        st.markdown("**💬 Sample Questions:**")
        samples = [
            "What are the success metrics?",
            "What is the tech stack?",
            "What are the risks?",
            "Who are the stakeholders?",
            "What is out of scope?"
        ]
        for s in samples:
            st.code(s, language=None)


# ══════════════════════════════════════════
# TAB 2 — DOCUMENTS
# ══════════════════════════════════════════
with tab2:
    st.markdown('<div class="section-header">📄 Document Manager</div>',
                unsafe_allow_html=True)

    upload_col, list_col = st.columns([1, 1])

    with upload_col:
        st.markdown("### ⬆️ Upload New Document")
        st.markdown("Supported: PDF, DOCX, TXT — Max 200MB")

        uploaded = st.file_uploader(
            "Drop file here",
            type=['pdf', 'docx', 'txt'],
            key="doc_uploader"
        )

        if uploaded:
            file_size = len(uploaded.getvalue()) / 1024
            st.info(f"📄 **{uploaded.name}** ({file_size:.1f} KB)")

            if st.button("📥 Ingest Document", type="primary"):
                with st.spinner("Processing and indexing document..."):
                    try:
                        files = {"file": (uploaded.name, uploaded.getvalue())}
                        r = httpx.post(
                            f"{API_URL}/ingest",
                            files=files,
                            timeout=120
                        )
                        res = r.json()

                        if r.status_code == 200:
                            st.success(f"✅ Ingested successfully!")
                            st.markdown(f"- Chunks created: **{res.get('chunks_created')}**")
                            st.markdown(f"- Total vectors: **{res.get('total_vectors')}**")

                            st.session_state.ingested_docs.append({
                                'name': uploaded.name,
                                'size': f"{file_size:.1f} KB",
                                'chunks': res.get('chunks_created'),
                                'time': datetime.now().strftime("%Y-%m-%d %H:%M")
                            })
                        else:
                            st.error(f"❌ {res.get('detail')}")
                    except Exception as e:
                        st.error(f"❌ {str(e)}")

    with list_col:
        st.markdown("### 📚 Ingested Documents")

        if st.session_state.ingested_docs:
            for doc in st.session_state.ingested_docs:
                st.markdown(f"""
                <div class='doc-card'>
                    <strong>📄 {doc['name']}</strong><br>
                    <span style='color:#9ca3af; font-size:0.85rem;'>
                    Size: {doc['size']} &nbsp;|&nbsp;
                    Chunks: {doc['chunks']} &nbsp;|&nbsp;
                    Added: {doc['time']}
                    </span>
                </div>""", unsafe_allow_html=True)
        else:
            st.info("No documents ingested in this session yet. Upload one on the left!")

        st.divider()
        st.markdown("### 📊 Database Status")
        if health:
            st.markdown(f"""
            <div class='doc-card'>
                <strong>🗄️ Qdrant Vector Database</strong><br>
                <span style='color:#6ee7b7;'>● Online</span><br>
                <span style='color:#9ca3af; font-size:0.85rem;'>
                Vectors stored: {health.get('total_documents_indexed', 0)}<br>
                Collection: regumind_documents
                </span>
            </div>""", unsafe_allow_html=True)


# ══════════════════════════════════════════
# TAB 3 — ANALYTICS
# ══════════════════════════════════════════
with tab3:
    st.markdown('<div class="section-header">📊 Analytics Dashboard</div>',
                unsafe_allow_html=True)

    analytics = st.session_state.analytics

    if not analytics['queries_list']:
        st.info("📊 No data yet. Ask some questions in the Ask tab to see analytics here!")
    else:
        # Summary metrics
        a1, a2, a3 = st.columns(3)
        with a1:
            st.metric("Total Queries", analytics['total_queries'])
        with a2:
            avg = (sum(analytics['confidence_scores']) /
                   len(analytics['confidence_scores'])
                   if analytics['confidence_scores'] else 0)
            st.metric("Avg Confidence", f"{avg:.0%}")
        with a3:
            avg_t = (sum(analytics['response_times']) /
                     len(analytics['response_times'])
                     if analytics['response_times'] else 0)
            st.metric("Avg Response Time", f"{avg_t:.2f}s")

        st.divider()

        chart_col1, chart_col2 = st.columns(2)

        with chart_col1:
            st.markdown("**📈 Confidence Scores Over Time**")
            if analytics['confidence_scores']:
                import pandas as pd
                df_conf = pd.DataFrame({
                    'Query': range(1, len(analytics['confidence_scores']) + 1),
                    'Confidence': [c * 100 for c in analytics['confidence_scores']]
                })
                st.line_chart(df_conf.set_index('Query'))

        with chart_col2:
            st.markdown("**⏱️ Response Times Over Time**")
            if analytics['response_times']:
                df_time = pd.DataFrame({
                    'Query': range(1, len(analytics['response_times']) + 1),
                    'Seconds': analytics['response_times']
                })
                st.bar_chart(df_time.set_index('Query'))

        st.divider()
        st.markdown("**📋 Query Log**")
        if analytics['queries_list']:
            import pandas as pd
            df_log = pd.DataFrame(analytics['queries_list'])
            df_log['confidence'] = df_log['confidence'].apply(lambda x: f"{x:.0%}")
            df_log['time'] = df_log['time'].apply(lambda x: f"{x:.2f}s")
            df_log['cached'] = df_log['cached'].apply(lambda x: "⚡ Yes" if x else "No")
            df_log.columns = ['Question', 'Confidence', 'Time', 'Cached', 'Timestamp']
            st.dataframe(df_log, use_container_width=True)


# ══════════════════════════════════════════
# TAB 4 — SYSTEM HEALTH
# ══════════════════════════════════════════
with tab4:
    st.markdown('<div class="section-header">🖥️ System Health Monitor</div>',
                unsafe_allow_html=True)

    if st.button("🔄 Refresh Status"):
        st.rerun()

    h1, h2, h3 = st.columns(3)

    with h1:
        st.markdown("### 🔌 API Server")
        if health:
            st.markdown("""
            <div class='metric-card'>
                <div style='color:#10b981; font-size:1.5rem;'>● Online</div>
                <div class='metric-label'>FastAPI on port 8000</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='metric-card'>
                <div style='color:#ef4444; font-size:1.5rem;'>● Offline</div>
                <div class='metric-label'>FastAPI on port 8000</div>
            </div>""", unsafe_allow_html=True)

    with h2:
        st.markdown("### 🗄️ Vector Database")
        if health and health.get('vector_database') == 'connected':
            st.markdown(f"""
            <div class='metric-card'>
                <div style='color:#10b981; font-size:1.5rem;'>● Connected</div>
                <div class='metric-label'>Qdrant on port 6333</div>
                <div class='metric-label'>{health.get('total_documents_indexed', 0)} vectors stored</div>
            </div>""", unsafe_allow_html=True)
        else:
            st.markdown("""
            <div class='metric-card'>
                <div style='color:#ef4444; font-size:1.5rem;'>● Disconnected</div>
                <div class='metric-label'>Qdrant on port 6333</div>
            </div>""", unsafe_allow_html=True)

    with h3:
        st.markdown("### 🤖 AI Model")
        if stats:
            st.markdown(f"""
            <div class='metric-card'>
                <div style='color:#10b981; font-size:1.5rem;'>● Ready</div>
                <div class='metric-label'>{stats.get('ai_model', 'N/A')}</div>
                <div class='metric-label'>via Groq API</div>
            </div>""", unsafe_allow_html=True)

    st.divider()

    # Component details
    st.markdown("### 🔧 Component Details")
    if stats:
        comp1, comp2 = st.columns(2)
        with comp1:
            st.markdown(f"""
            <div class='doc-card'>
                <strong>🧠 Embedding Model</strong><br>
                <span style='color:#60a5fa;'>{stats.get('embedding_model', 'N/A')}</span><br>
                <span style='color:#9ca3af; font-size:0.85rem;'>384 dimensions • Local • Free</span>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div class='doc-card'>
                <strong>🔍 Search Engine</strong><br>
                <span style='color:#60a5fa;'>Hybrid Search</span><br>
                <span style='color:#9ca3af; font-size:0.85rem;'>Vector (70%) + BM25 (30%)</span>
            </div>""", unsafe_allow_html=True)

        with comp2:
            st.markdown(f"""
            <div class='doc-card'>
                <strong>🛡️ Hallucination Detector</strong><br>
                <span style='color:#60a5fa;'>Sentence-level verification</span><br>
                <span style='color:#9ca3af; font-size:0.85rem;'>Checks every sentence against source</span>
            </div>""", unsafe_allow_html=True)

            st.markdown(f"""
            <div class='doc-card'>
                <strong>⚡ Cache System</strong><br>
                <span style='color:#60a5fa;'>In-memory cache</span><br>
                <span style='color:#9ca3af; font-size:0.85rem;'>{len(st.session_state.query_cache)} queries cached</span>
            </div>""", unsafe_allow_html=True)

    st.divider()
    st.markdown("### 📡 Quick Endpoint Test")
    test_col1, test_col2, test_col3 = st.columns(3)

    with test_col1:
        if st.button("Test GET /health"):
            try:
                r = httpx.get(f"{API_URL}/health", timeout=5)
                st.json(r.json())
            except Exception as e:
                st.error(str(e))

    with test_col2:
        if st.button("Test GET /stats"):
            try:
                r = httpx.get(f"{API_URL}/stats", timeout=5)
                st.json(r.json())
            except Exception as e:
                st.error(str(e))

    with test_col3:
        if st.button("Test GET /"):
            try:
                r = httpx.get(f"{API_URL}/", timeout=5)
                st.json(r.json())
            except Exception as e:
                st.error(str(e))


# ══════════════════════════════════════════
# TAB 5 — CHAT HISTORY
# ══════════════════════════════════════════
with tab5:
    st.markdown('<div class="section-header">📜 Full Chat History</div>',
                unsafe_allow_html=True)

    if not st.session_state.chat_history:
        st.info("No chat history yet. Ask some questions in the Ask tab!")
    else:
        st.markdown(f"**{len(st.session_state.chat_history)} conversations recorded**")

        if st.button("🗑️ Clear All History"):
            st.session_state.chat_history = []
            st.rerun()

        for i, entry in enumerate(reversed(st.session_state.chat_history)):
            with st.expander(
                f"Q{len(st.session_state.chat_history)-i}: "
                f"{entry['question'][:60]}... "
                f"| {entry['timestamp']} "
                f"| Confidence: {entry.get('confidence', 0):.0%}"
            ):
                st.markdown(f"**🧑 Question:**\n{entry['question']}")
                st.markdown(f"**🧠 Answer:**\n{entry['answer']}")
                col_h1, col_h2, col_h3 = st.columns(3)
                with col_h1:
                    badge = get_confidence_badge(entry.get('confidence', 0))
                    st.markdown(f"**Confidence:** {badge}",
                                unsafe_allow_html=True)
                with col_h2:
                    st.markdown(f"**Time:** {entry.get('response_time', 0):.2f}s")
                with col_h3:
                    cached = "⚡ Yes" if entry.get('cached') else "No"
                    st.markdown(f"**Cached:** {cached}")

                if entry.get('sources'):
                    st.markdown("**Sources:** " +
                                ", ".join([f"`{s}`" for s in entry['sources']]))