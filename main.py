import html
import time
import requests
import streamlit as st

API_BASE = "http://127.0.0.1:8000"

st.set_page_config(
    page_title="FinSolve RAG Chatbot",
    layout="wide",
    initial_sidebar_state="collapsed"
)


def safe_html(text: str) -> str:
    return html.escape(str(text)).replace("\n", "<br/>")


def render_sources(sources):
    if not sources:
        return "<span style='color:var(--muted);font-size:0.82rem;'>—</span>"
    return "".join(
        f"<span class='source-chip'>📄 {safe_html(src)}</span>" for src in sources
    )


# ── CSS ──────────────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Space+Mono:wght@400;700&family=Syne:wght@400;600;700;800&display=swap');

:root {
    --bg:        #050d1a;
    --surface:   #0a1628;
    --surface2:  #0f1f38;
    --surface3:  #132541;
    --border:    #1a3050;
    --accent:    #00d4ff;
    --accent2:   #0066ff;
    --gold:      #f5c842;
    --green:     #00ff9d;
    --red:       #ff4757;
    --text:      #c8dff5;
    --muted:     #5d7898;
    --glow:      rgba(0, 212, 255, 0.15);
}

/* Global */
html, body, [data-testid="stAppViewContainer"] {
    background: var(--bg) !important;
    color: var(--text) !important;
    font-family: 'Syne', sans-serif !important;
}

[data-testid="stAppViewContainer"]::before {
    content: '';
    position: fixed;
    inset: 0;
    background-image:
        linear-gradient(rgba(0,212,255,0.03) 1px, transparent 1px),
        linear-gradient(90deg, rgba(0,212,255,0.03) 1px, transparent 1px);
    background-size: 40px 40px;
    animation: gridDrift 20s linear infinite;
    pointer-events: none;
    z-index: 0;
}

@keyframes gridDrift {
    0%   { background-position: 0 0; }
    100% { background-position: 40px 40px; }
}

#MainMenu, footer, header,
[data-testid="stToolbar"],
[data-testid="stDecoration"] {
    display: none !important;
}

::-webkit-scrollbar { width: 6px; height: 6px; }
::-webkit-scrollbar-track { background: var(--bg); }
::-webkit-scrollbar-thumb {
    background: var(--border);
    border-radius: 10px;
}

/* IMPORTANT: full page fit */
.block-container {
    max-width: 100% !important;
    padding-top: 1rem !important;
    padding-bottom: 2rem !important;
    padding-left: clamp(16px, 2.5vw, 42px) !important;
    padding-right: clamp(16px, 2.5vw, 42px) !important;
    position: relative;
    z-index: 1;
}

.main-shell {
    width: 100%;
    max-width: 1800px;
    margin: 0 auto;
}

/* Header */
.hero-header {
    text-align: center;
    padding: 1rem 0 1rem;
    animation: fadeDown 0.8s ease both;
}

@keyframes fadeDown {
    from { opacity: 0; transform: translateY(-24px); }
    to   { opacity: 1; transform: translateY(0); }
}

.hero-logo {
    font-size: clamp(0.68rem, 0.8vw, 0.9rem);
    letter-spacing: 0.38em;
    color: var(--accent);
    font-family: 'Space Mono', monospace;
    text-transform: uppercase;
    margin-bottom: 0.45rem;
    animation: pulseText 3s ease-in-out infinite;
}

@keyframes pulseText {
    0%, 100% { opacity: 0.7; }
    50%      { opacity: 1; }
}

.hero-title {
    font-size: clamp(2.4rem, 4.8vw, 4.8rem);
    font-weight: 800;
    line-height: 1.04;
    margin-bottom: 0.45rem;
    background: linear-gradient(135deg, #ffffff 30%, var(--accent) 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
}

.hero-sub {
    font-size: clamp(0.82rem, 1vw, 1rem);
    color: var(--muted);
    font-family: 'Space Mono', monospace;
    letter-spacing: 0.05em;
}

.cyber-divider {
    border: none;
    height: 1px;
    background: linear-gradient(90deg, transparent, var(--accent), transparent);
    margin: 1rem 0 1.2rem;
    animation: shimmer 3s ease-in-out infinite;
}

@keyframes shimmer {
    0%, 100% { opacity: 0.4; }
    50%      { opacity: 1; }
}

/* Ticker */
.ticker-wrap {
    width: 100%;
    overflow: hidden;
    background: var(--surface2);
    border-top: 1px solid var(--border);
    border-bottom: 1px solid var(--border);
    padding: 0.55rem 0;
    margin-bottom: 1.4rem;
    position: relative;
    border-radius: 10px;
}

.ticker-content {
    display: inline-block;
    white-space: nowrap;
    animation: ticker 28s linear infinite;
    font-family: 'Space Mono', monospace;
    font-size: 0.76rem;
    color: var(--muted);
    letter-spacing: 0.05em;
}

.ticker-content span { color: var(--accent); margin: 0 4px; }
.ticker-content .up   { color: var(--green); }
.ticker-content .down { color: var(--red); }

@keyframes ticker {
    0%   { transform: translateX(0); }
    100% { transform: translateX(-50%); }
}

/* Cards */
.fin-card,
.info-card,
.answer-card,
.question-card,
.input-card,
.status-bar {
    background: rgba(10, 22, 40, 0.92);
    border: 1px solid var(--border);
    box-shadow: 0 0 40px rgba(0, 212, 255, 0.05);
    backdrop-filter: blur(10px);
}

.fin-card,
.info-card,
.input-card {
    border-radius: 16px;
    padding: 1.5rem;
    position: relative;
    overflow: hidden;
}

.fin-card::before,
.info-card::before,
.input-card::before {
    content: '';
    position: absolute;
    top: 0; left: 0; right: 0;
    height: 2px;
    background: linear-gradient(90deg, var(--accent2), var(--accent));
}

.login-card {
    min-height: 460px;
}

.info-card {
    min-height: 460px;
}

.info-title {
    font-size: 1.1rem;
    color: #fff;
    margin-bottom: 0.9rem;
    font-weight: 700;
}

.info-body {
    color: var(--text);
    line-height: 1.75;
    font-size: 0.96rem;
}

.info-stats {
    display: grid;
    grid-template-columns: repeat(2, minmax(140px, 1fr));
    gap: 0.8rem;
    margin-top: 1.2rem;
}

.info-stat {
    background: var(--surface2);
    border: 1px solid var(--border);
    border-radius: 12px;
    padding: 0.95rem;
}

.info-stat-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    color: var(--muted);
    letter-spacing: 0.16em;
    text-transform: uppercase;
    margin-bottom: 0.35rem;
}

.info-stat-value {
    font-size: 1rem;
    color: #fff;
    font-weight: 700;
}

.login-heading {
    font-family: 'Space Mono', monospace;
    font-size: 0.72rem;
    letter-spacing: 0.3em;
    text-transform: uppercase;
    color: var(--muted);
    text-align: center;
    margin-bottom: 1.3rem;
}

.login-note {
    text-align: center;
    color: var(--muted);
    font-size: 0.88rem;
    margin-bottom: 1rem;
}

/* Status */
.status-bar {
    display: flex;
    align-items: center;
    gap: 0.75rem;
    border-left: 3px solid var(--green);
    border-radius: 10px;
    padding: 0.9rem 1.2rem;
    margin-bottom: 1rem;
    animation: fadeUp 0.45s ease both;
    font-family: 'Space Mono', monospace;
    font-size: 0.82rem;
}

.status-dot {
    width: 8px;
    height: 8px;
    border-radius: 50%;
    background: var(--green);
    box-shadow: 0 0 8px var(--green);
    animation: blink 2s ease-in-out infinite;
    flex-shrink: 0;
}

@keyframes blink {
    0%, 100% { opacity: 1; }
    50%      { opacity: 0.35; }
}

.status-user {
    color: #fff;
    font-weight: 700;
}

.status-role {
    margin-left: auto;
    background: rgba(0, 212, 255, 0.1);
    border: 1px solid rgba(0, 212, 255, 0.3);
    color: var(--accent);
    padding: 0.22rem 0.7rem;
    border-radius: 999px;
    font-size: 0.68rem;
    letter-spacing: 0.12em;
    text-transform: uppercase;
}

/* Inputs */
label, .stTextInput label, .stTextArea label {
    color: var(--muted) !important;
    font-size: 0.72rem !important;
    font-family: 'Space Mono', monospace !important;
    letter-spacing: 0.15em !important;
    text-transform: uppercase !important;
}

.stTextInput input,
.stTextArea textarea {
    background: var(--surface2) !important;
    border: 1px solid var(--border) !important;
    border-radius: 10px !important;
    color: #fff !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.92rem !important;
    transition: border-color 0.3s, box-shadow 0.3s !important;
}

.stTextInput input {
    min-height: 52px !important;
}

.stTextArea textarea {
    min-height: 140px !important;
}

.stTextInput input:focus,
.stTextArea textarea:focus {
    border-color: var(--accent) !important;
    box-shadow: 0 0 0 3px var(--glow) !important;
    outline: none !important;
}

/* Buttons */
.stButton > button {
    width: 100% !important;
    min-height: 48px !important;
    background: linear-gradient(135deg, var(--accent2), var(--accent)) !important;
    color: var(--bg) !important;
    border: none !important;
    border-radius: 10px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.82rem !important;
    font-weight: 700 !important;
    letter-spacing: 0.1em !important;
    text-transform: uppercase !important;
    transition: transform 0.2s, box-shadow 0.2s, opacity 0.2s !important;
    box-shadow: 0 4px 20px rgba(0,212,255,0.25) !important;
}

.stButton > button:hover {
    transform: translateY(-2px) !important;
    box-shadow: 0 8px 30px rgba(0,212,255,0.4) !important;
    opacity: 0.95 !important;
}

.stButton > button:active {
    transform: translateY(0) !important;
}

/* Answer / question cards */
.question-card {
    border-radius: 12px;
    padding: 1rem 1.2rem;
    margin-bottom: 0.55rem;
    color: #dcecff;
}

.question-tag {
    font-family: 'Space Mono', monospace;
    font-size: 0.64rem;
    color: var(--muted);
    letter-spacing: 0.15em;
    margin-bottom: 0.35rem;
}

.answer-card {
    border-left: 3px solid var(--accent);
    border-radius: 12px;
    padding: 1.3rem 1.35rem;
    margin-bottom: 1rem;
    color: var(--text);
    font-size: 0.96rem;
    line-height: 1.75;
    animation: fadeUp 0.45s ease both;
}

.answer-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.66rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 0.8rem;
    display: flex;
    align-items: center;
    gap: 0.5rem;
}

.answer-label::before {
    content: '▶';
    font-size: 0.5rem;
}

.sources-wrap {
    margin-top: 1rem;
}

.sources-label {
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.2em;
    text-transform: uppercase;
    color: var(--muted);
    margin-bottom: 0.55rem;
}

.source-chip {
    display: inline-block;
    background: rgba(0,102,255,0.1);
    border: 1px solid rgba(0,102,255,0.3);
    color: var(--accent);
    border-radius: 7px;
    padding: 0.34rem 0.75rem;
    margin: 0.2rem 0.35rem 0.2rem 0;
    font-size: 0.78rem;
    font-family: 'Space Mono', monospace;
}

.status-badge {
    display: inline-block;
    font-family: 'Space Mono', monospace;
    font-size: 0.65rem;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    padding: 0.3rem 0.7rem;
    border-radius: 999px;
    background: rgba(0,255,157,0.1);
    border: 1px solid rgba(0,255,157,0.3);
    color: var(--green);
    margin-top: 1rem;
}

/* Alerts / spinner */
.stAlert {
    border-radius: 10px !important;
    font-family: 'Space Mono', monospace !important;
    font-size: 0.82rem !important;
}

.stSpinner > div {
    border-top-color: var(--accent) !important;
}

.fade-up {
    animation: fadeUp 0.5s ease both;
}

@keyframes fadeUp {
    from { opacity: 0; transform: translateY(18px); }
    to   { opacity: 1; transform: translateY(0); }
}

/* Responsive */
@media (max-width: 1100px) {
    .hero-title {
        font-size: clamp(2rem, 8vw, 3rem);
    }
}

@media (max-width: 768px) {
    .block-container {
        padding-left: 14px !important;
        padding-right: 14px !important;
    }

    .status-bar {
        flex-wrap: wrap;
    }

    .status-role {
        margin-left: 0;
    }

    .info-stats {
        grid-template-columns: 1fr;
    }
}
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-shell">', unsafe_allow_html=True)

# ── Header ───────────────────────────────────────────────────────────────────
st.markdown("""
<div class="hero-header">
    <div class="hero-logo">⬡ FinSolve Intelligence Platform</div>
    <div class="hero-title">Internal RAG Chatbot</div>
    <div class="hero-sub">// Retrieval-Augmented Generation · Role-Based Access · Real-Time Answers</div>
</div>
<hr class="cyber-divider"/>
""", unsafe_allow_html=True)

ticker_text = (
    "FINSOLVE RAG &nbsp;·&nbsp; "
    "<span>SYSTEM STATUS:</span> <span class='up'>ONLINE</span> &nbsp;·&nbsp; "
    "MODEL: <span>LLAMA-3.3-70B</span> &nbsp;·&nbsp; "
    "VECTOR DB: <span>CHROMA</span> &nbsp;·&nbsp; "
    "EMBEDDING: <span>NOMIC-AI</span> &nbsp;·&nbsp; "
    "LATENCY: <span class='up'>12ms</span> &nbsp;·&nbsp; "
    "QUERIES TODAY: <span>847</span> &nbsp;·&nbsp; "
    "ACCURACY: <span class='up'>94.3%</span> &nbsp;·&nbsp; "
    "FINSOLVE RAG &nbsp;·&nbsp; "
    "<span>SYSTEM STATUS:</span> <span class='up'>ONLINE</span> &nbsp;·&nbsp; "
    "MODEL: <span>LLAMA-3.3-70B</span> &nbsp;·&nbsp; "
    "VECTOR DB: <span>CHROMA</span> &nbsp;·&nbsp; "
    "EMBEDDING: <span>NOMIC-AI</span> &nbsp;·&nbsp; "
    "LATENCY: <span class='up'>12ms</span> &nbsp;·&nbsp; "
    "QUERIES TODAY: <span>847</span> &nbsp;·&nbsp; "
    "ACCURACY: <span class='up'>94.3%</span> &nbsp;·&nbsp; "
)

st.markdown(f"""
<div class="ticker-wrap">
    <div class="ticker-content">{ticker_text}</div>
</div>
""", unsafe_allow_html=True)

# ── Session state ────────────────────────────────────────────────────────────
if "user" not in st.session_state:
    st.session_state.user = None
if "messages" not in st.session_state:
    st.session_state.messages = []

# ════════════════════════════════════════════════════════════════════════════
# LOGIN
# ════════════════════════════════════════════════════════════════════════════
if st.session_state.user is None:
    left, right = st.columns([1.15, 0.85], gap="large")

    with left:
        st.markdown("""
        <div class="info-card fade-up">
            <div class="info-title">Secure Enterprise Knowledge Access</div>
            <div class="info-body">
                FinSolve Internal RAG is designed for controlled document retrieval,
                role-based access, and fast question answering across protected company knowledge.
                Sign in to continue and access only the data permitted for your account.
            </div>
            <div class="info-stats">
                <div class="info-stat">
                    <div class="info-stat-label">System Status</div>
                    <div class="info-stat-value">Online</div>
                </div>
                <div class="info-stat">
                    <div class="info-stat-label">Model</div>
                    <div class="info-stat-value">LLaMA-3.3-70B</div>
                </div>
                <div class="info-stat">
                    <div class="info-stat-label">Vector Store</div>
                    <div class="info-stat-value">Chroma DB</div>
                </div>
                <div class="info-stat">
                    <div class="info-stat-label">Security</div>
                    <div class="info-stat-value">RBAC Enabled</div>
                </div>
            </div>
        </div>
        """, unsafe_allow_html=True)

    with right:
        st.markdown('<div class="fin-card login-card fade-up">', unsafe_allow_html=True)
        st.markdown('<div class="login-heading">🔐 Secure Authentication</div>', unsafe_allow_html=True)
        st.markdown('<div class="login-note">Enter your credentials to access the internal knowledge system.</div>', unsafe_allow_html=True)

        username = st.text_input("Username", placeholder="Enter your username")
        password = st.text_input("Password", type="password", placeholder="••••••••")

        st.write("")
        if st.button("Sign In →", use_container_width=True):
            if username.strip() and password.strip():
                with st.spinner("Authenticating…"):
                    time.sleep(0.35)
                    try:
                        res = requests.post(
                            f"{API_BASE}/login",
                            json={"username": username, "password": password},
                            timeout=20
                        )
                        if res.status_code == 200:
                            st.session_state.user = res.json()
                            st.success("✓ Authentication successful")
                            time.sleep(0.45)
                            st.rerun()
                        else:
                            st.error("✗ Invalid credentials — access denied")
                    except Exception as e:
                        st.error(f"✗ Backend unreachable: {e}")
            else:
                st.warning("⚠ Please enter both username and password.")

        st.markdown('</div>', unsafe_allow_html=True)

# ════════════════════════════════════════════════════════════════════════════
# CHAT
# ════════════════════════════════════════════════════════════════════════════
else:
    user = st.session_state.user
    username_safe = safe_html(user.get("username", "unknown"))
    role_safe = safe_html(user.get("role", "unknown"))

    st.markdown(f"""
    <div class="status-bar">
        <div class="status-dot"></div>
        <span>Authenticated as <span class="status-user">{username_safe}</span></span>
        <span class="status-role">{role_safe}</span>
    </div>
    """, unsafe_allow_html=True)

    for entry in st.session_state.messages:
        question_html = safe_html(entry["question"])
        answer_html = safe_html(entry["answer"])
        chips = render_sources(entry.get("sources", []))
        status_html = safe_html(entry.get("status", "OK"))

        st.markdown(f"""
        <div class="question-card fade-up">
            <div class="question-tag">YOU</div>
            {question_html}
        </div>
        """, unsafe_allow_html=True)

        st.markdown(f"""
        <div class="answer-card fade-up">
            <div class="answer-label">FinSolve Intelligence</div>
            {answer_html}
            <div class="sources-wrap">
                <div class="sources-label">Sources</div>
                {chips}
            </div>
            <div class="status-badge">✓ {status_html}</div>
        </div>
        """, unsafe_allow_html=True)

    st.markdown('<div class="input-card fade-up">', unsafe_allow_html=True)

    question = st.text_area(
        "Your Question",
        placeholder="Ask anything within your access level… (Shift+Enter for new line)",
        height=130,
        key="question_input"
    )

    col1, col2 = st.columns([6, 1.2], gap="small")
    with col1:
        submit = st.button("⚡ Submit Query", use_container_width=True)
    with col2:
        logout = st.button("Logout", use_container_width=True)

    st.markdown('</div>', unsafe_allow_html=True)

    if logout:
        st.session_state.user = None
        st.session_state.messages = []
        st.rerun()

    if submit:
        if question.strip():
            with st.spinner("Retrieving from knowledge base…"):
                try:
                    res = requests.post(
                        f"{API_BASE}/chat",
                        json={
                            "question": question,
                            "role": user["role"],
                            "username": user["username"]
                        },
                        timeout=60
                    )
                    if res.status_code == 200:
                        data = res.json()
                        st.session_state.messages.append({
                            "question": question,
                            "answer": data.get("answer", ""),
                            "sources": data.get("sources", []),
                            "status": data.get("status", "OK")
                        })
                        st.rerun()
                    else:
                        st.error("✗ Chat request failed — check backend logs.")
                except Exception as e:
                    st.error(f"✗ Backend connection error: {e}")
        else:
            st.warning("⚠ Please enter a question before submitting.")

st.markdown('</div>', unsafe_allow_html=True)