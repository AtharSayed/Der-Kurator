# app.py
import asyncio
import base64
import logging

import streamlit as st
from rag.qa import ask_async

# --------------------------------------------------
# Logging setup
# --------------------------------------------------
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Der Kurator — Porsche 911 Knowledge Assistant",
    page_icon="🏎️",
    layout="wide",
    initial_sidebar_state="auto"
)

# --------------------------------------------------
# Load and encode background image
# --------------------------------------------------
@st.cache_data(show_spinner=False)
def get_base64_encoded_image(image_path):
    try:
        with open(image_path, "rb") as img_file:
            return base64.b64encode(img_file.read()).decode("utf-8")
    except FileNotFoundError:
        st.warning("Background image not found. Using dark overlay only.")
        return None
    except Exception as e:
        st.error(f"Error loading image: {e}")
        return None

image_path = "data/images/Porsche 911 Carrera T parked in a courtyard.jpeg"
base64_image = get_base64_encoded_image(image_path)

background_css = ""
if base64_image:
    background_css = f"""
    .stApp {{
        background-image: url("data:image/jpeg;base64,{base64_image}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    """

# --------------------------------------------------
# Custom CSS
# --------------------------------------------------
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Montserrat', sans-serif;
}}

.stApp::before {{
    content: "";
    position: fixed;
    top: 0; left: 0; right: 0; bottom: 0;
    background: rgba(0, 0, 0, 0.70);
    z-index: -1;
}}

{background_css}

:root {{
    --glass-bg: rgba(15, 15, 25, 0.80);
    --glass-bg-darker: rgba(10, 10, 20, 0.92);
    --porsche-red: #B11210;
    --text-primary: #F9FAFB;
    --text-secondary: #E5E7EB;
    --border-light: rgba(255, 255, 255, 0.15);
}}

.main-title {{
    font-size: clamp(2.8rem, 6vw, 4.2rem);
    font-weight: 800;
    text-align: center;
    color: #FFFFFF;
    text-shadow: 0 4px 20px rgba(0,0,0,0.9);
    margin: 2rem 0 0.5rem;
}}

.subtitle {{
    font-size: clamp(1.1rem, 3vw, 1.6rem);
    text-align: center;
    color: var(--text-secondary);
    margin-bottom: 3rem;
    text-shadow: 0 2px 10px rgba(0,0,0,0.8);
}}

div[data-testid="stChatMessage"] {{
    background-color: var(--glass-bg) !important;
    backdrop-filter: blur(12px);
    -webkit-backdrop-filter: blur(12px);
    border-radius: 18px !important;
    padding: 1.4rem 1.8rem !important;
    margin: 1rem 0 !important;
    box-shadow: 0 8px 32px rgba(0, 0, 0, 0.6);
    border: 1px solid var(--border-light);
}}

div[data-testid="stChatMessage"]:has(div[data-testid="chat-message-assistant"]) {{
    border-left: 6px solid var(--porsche-red) !important;
}}

.sources-header {{
    font-size: 1.3rem;
    font-weight: 700;
    margin: 1.8rem 0 0.8rem 0;
    color: #FFFFFF;
}}

.source-item {{
    background-color: var(--glass-bg-darker);
    padding: 1rem 1.4rem;
    border-radius: 12px;
    margin-bottom: 0.8rem;
    border: 1px solid var(--border-light);
    font-size: 0.95rem;
}}

.source-item:hover {{
    background-color: rgba(30, 30, 40, 0.95);
}}

.source-file {{
    font-weight: 700;
    color: #F87171;
}}

div[data-testid="stChatInput"] > div > div {{
    background-color: var(--glass-bg-darker) !important;
    border-radius: 18px !important;
    border: 1px solid var(--border-light) !important;
    backdrop-filter: blur(8px);
}}

div[data-testid="stChatInput"] textarea {{
    background-color: transparent !important;
    color: var(--text-primary) !important;
    caret-color: var(--porsche-red);
}}

div[data-testid="stChatInput"] textarea::placeholder {{
    color: #9CA3AF !important;
}}

.stButton > button {{
    background-color: var(--porsche-red);
    color: white;
    border-radius: 12px;
    font-weight: 600;
    border: none;
    transition: all 0.3s ease;
}}

.stButton > button:hover {{
    background-color: #8F0E0C;
    transform: translateY(-2px);
}}

@media (max-width: 768px) {{
    .main-title {{ font-size: 2.8rem; }}
    .subtitle {{ font-size: 1.3rem; }}
    div[data-testid="stChatMessage"] {{ padding: 1.2rem !important; }}
}}
</style>
""",
    unsafe_allow_html=True
)

# --------------------------------------------------
# Sidebar
# --------------------------------------------------
with st.sidebar:
    st.markdown("### ⚙️ Controls")
    if st.button("🗑️ Clear Chat History", use_container_width=True):
        st.session_state.messages = []
        st.rerun()
    st.markdown("---")
    st.caption("**Der Kurator** – Porsche 911 RAG Assistant\nVersion 1.3 • Async + Cached")

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown('<div class="main-title">Der Kurator</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Porsche 911 Knowledge Assistant — Precise, document-grounded answers</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# Session state & welcome message
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = [
        {
            "role": "assistant",
            "content": "Hello! I'm **Der Kurator**, your dedicated Porsche 911 expert. "
                       "Ask me about specifications, variants, history, performance, or technical details across all generations.",
            "citations": []
        }
    ]

# --------------------------------------------------
# Chat display container
# --------------------------------------------------
chat_container = st.container()

with chat_container:
    for message in st.session_state.messages:
        avatar = "🏎️" if message["role"] == "assistant" else "🧑"
        with st.chat_message(message["role"], avatar=avatar):
            st.markdown(message["content"], unsafe_allow_html=False)
            
            if message.get("citations"):
                st.markdown('<div class="sources-header">📑 Sources</div>', unsafe_allow_html=True)
                for idx, citation in enumerate(message["citations"], 1):
                    variant = f" • {citation.get('variant', '')}" if citation.get("variant") else ""
                    page = f" (page {citation.get('page', '')})" if citation.get("page") else ""
                    elem = f" • {citation.get('element_type', '')}" if citation.get("element_type") and citation.get("element_type") != "NarrativeText" else ""
                    
                    st.markdown(
                        f"""
                        <div class="source-item">
                            <strong>{idx}.</strong>
                            <span class="source-file">{citation.get("source", "Unknown")}</span>{variant}{page}{elem}
                        </div>
                        """,
                        unsafe_allow_html=True
                    )

# --------------------------------------------------
# User input & response handling (Modern Streamlit compatible)
# --------------------------------------------------
if question := st.chat_input("Ask about Porsche 911 specs, variants, history, etc."):
    question = question.strip()
    if question:
        # Add user message
        st.session_state.messages.append({"role": "user", "content": question})
        with chat_container:
            with st.chat_message("user", avatar="🧑"):
                st.markdown(question)

        # Assistant response
        with chat_container:
            with st.chat_message("assistant", avatar="🏎️"):
                response_placeholder = st.empty()
                status_placeholder = st.status("Retrieving and thinking...")

                try:
                    result = asyncio.run(ask_async(question))
                    answer = result.get("answer", "").strip()
                    citations = result.get("citations", [])

                    if not answer:
                        answer = "I don't have sufficient information to answer this question."

                    # Update status and display answer
                    status_placeholder.update(label="Complete!", state="complete")
                    response_placeholder.markdown(answer)

                    # Display sources
                    if citations:
                        st.markdown('<div class="sources-header">📑 Sources</div>', unsafe_allow_html=True)
                        for idx, c in enumerate(citations, 1):
                            variant = f" • {c.get('variant', '')}" if c.get("variant") else ""
                            page = f" (page {c.get('page', '')})" if c.get("page") else ""
                            elem = f" • {c.get('element_type', '')}" if c.get("element_type") and c.get("element_type") != "NarrativeText" else ""
                            
                            st.markdown(
                                f"""
                                <div class="source-item">
                                    <strong>{idx}.</strong>
                                    <span class="source-file">{c.get("source", "Unknown")}</span>{variant}{page}{elem}
                                </div>
                                """,
                                unsafe_allow_html=True
                            )

                    # Save to history
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": answer,
                        "citations": citations
                    })

                except Exception as e:
                    logger.error(f"Error in ask_async: {e}")
                    status_placeholder.update(label="Error occurred", state="error")
                    response_placeholder.error("Sorry, something went wrong. Please try again.")
                    st.session_state.messages.append({
                        "role": "assistant",
                        "content": "Sorry, something went wrong. Please rephrase or try again.",
                        "citations": []
                    })

        # Trigger rerun to update chat history
        st.rerun()