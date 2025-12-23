# app.py
import streamlit as st
import base64
from rag.qa import ask

# --------------------------------------------------
# Encode background image
# --------------------------------------------------
@st.cache_data
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode("utf-8")

image_path = "data/images/Porsche 911 Carrera T parked in a courtyard.jpeg"

try:
    base64_image = get_base64_encoded_image(image_path)
except FileNotFoundError:
    st.error(f"Background image not found at {image_path}")
    base64_image = ""

# --------------------------------------------------
# Page config
# --------------------------------------------------
st.set_page_config(
    page_title="Porsche 911 Knowledge Assistant",
    page_icon="🏎️",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --------------------------------------------------
# Dark translucent UI CSS (unchanged + minor tweaks)
# --------------------------------------------------
st.markdown(
    f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');

html, body, [class*="css"] {{
    font-family: 'Montserrat', sans-serif;
    color: #F9FAFB;
}}

.stApp {{
    background-image: url("data:image/jpeg;base64,{base64_image}");
    background-size: cover;
    background-position: center;
    background-repeat: no-repeat;
    background-attachment: fixed;
}}

.stApp::before {{
    content: "";
    position: fixed;
    inset: 0;
    background-color: rgba(0, 0, 0, 0.65);
    z-index: -1;
}}

:root {{
    --glass-dark: rgba(0, 0, 0, 0.72);
    --glass-darker: rgba(0, 0, 0, 0.85);
    --porsche-red: #B11210;
}}

.main-title {{
    font-size: 3.6rem;
    font-weight: 800;
    text-align: center;
    color: #FFFFFF;
    text-shadow: 2px 2px 12px rgba(0,0,0,0.9);
}}

.subtitle {{
    font-size: 1.5rem;
    text-align: center;
    color: #E5E7EB;
    margin-bottom: 3rem;
    text-shadow: 0 0 10px rgba(0,0,0,0.9);
}}

.stChatMessage {{
    background-color: var(--glass-dark);
    border-radius: 16px;
    padding: 1.4rem 1.8rem;
    margin: 1.2rem 0;
    color: #F9FAFB;
    box-shadow: 0 10px 30px rgba(0,0,0,0.5);
}}

div[data-testid="stChatMessage"]:has(div[data-testid="chat-message-assistant"]) {{
    border-left: 6px solid var(--porsche-red);
}}

.sources-header {{
    font-size: 1.3rem;
    font-weight: 700;
    margin-top: 1.8rem;
    color: #FFFFFF;
}}

.source-item {{
    background-color: var(--glass-darker);
    padding: 1rem 1.4rem;
    border-radius: 12px;
    margin-bottom: 0.8rem;
    border: 1px solid rgba(255,255,255,0.15);
    font-size: 0.95rem;
}}

.source-file {{
    font-weight: 700;
    color: #F87171;
}}

.stChatInput {{
    background-color: transparent;
}}

textarea {{
    background-color: var(--glass-darker) !important;
    color: #FFFFFF !important;
    border-radius: 15px !important;
    border: 1px solid rgba(255,255,255,0.2) !important;
}}

textarea::placeholder {{
    color: #D1D5DB !important;
}}

textarea::selection {{
    background: #B11210;
    color: #FFFFFF;
}}

.stButton > button {{
    background-color: var(--porsche-red);
    color: #FFFFFF;
    border-radius: 14px;
    font-weight: 700;
    padding: 0.8rem 2rem;
}}

.stButton > button:hover {{
    background-color: #8F0E0C;
}}

.stInfo, .stError {{
    background-color: var(--glass-dark);
    color: #FFFFFF;
    border-radius: 12px;
    border-left: 5px solid var(--porsche-red);
}}
</style>
""",
    unsafe_allow_html=True
)

# --------------------------------------------------
# Header
# --------------------------------------------------
st.markdown('<div class="main-title">Porsche 911 Knowledge Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Ask me anything about Porsche 911 technical specs and history</div>',
    unsafe_allow_html=True
)

# --------------------------------------------------
# Chat state
# --------------------------------------------------
if "messages" not in st.session_state:
    st.session_state.messages = []

for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🏎️" if message["role"] == "assistant" else None):
        st.markdown(message["content"])
        if message.get("citations"):
            st.markdown('<div class="sources-header">📑 Sources</div>', unsafe_allow_html=True)
            for idx, c in enumerate(message["citations"], 1):
                variant_str = f" • {c['variant']}" if c.get("variant") else ""
                page_str = f" (page {c['page']})" if c.get("page") else ""
                elem_type = f" • {c['element_type']}" if c.get("element_type") and c["element_type"] != "NarrativeText" else ""

                st.markdown(
                    f"""
                    <div class="source-item">
                        <strong>{idx}.</strong>
                        <span class="source-file">{c.get("source","Unknown")}</span>{variant_str}{page_str}{elem_type}
                    </div>
                    """,
                    unsafe_allow_html=True,
                )

# --------------------------------------------------
# Input & Response
# --------------------------------------------------
if question := st.chat_input("Ask about the Porsche 911 (e.g., torque of GT3, 0-60 of Turbo S)"):
    # Add user message to chat
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("user"):
        st.markdown(question)

    # Generate assistant response
    with st.chat_message("assistant", avatar="🏎️"):
        with st.spinner("Thinking..."):
            result = ask(question.strip())
            answer = result.get("answer", "").strip()
            citations = result.get("citations", [])
            best_score = result.get("best_score")

            if answer.lower().startswith("i don't know"):
                st.info(answer)
            else:
                st.markdown(answer)

                # Optional: show confidence score (uncomment if you want debug info)
                # if best_score:
                #     st.caption(f"Confidence score: {best_score:.2f}")

            # Show sources only if we have a real answer
            if citations and not answer.lower().startswith("i don't know"):
                st.markdown('<div class="sources-header">📑 Sources</div>', unsafe_allow_html=True)
                for idx, c in enumerate(citations, 1):
                    variant_str = f" • {c['variant']}" if c.get("variant") else ""
                    page_str = f" (page {c['page']})" if c.get("page") else ""
                    elem_type = f" • {c['element_type']}" if c.get("element_type") and c["element_type"] != "NarrativeText" else ""

                    st.markdown(
                        f"""
                        <div class="source-item">
                            <strong>{idx}.</strong>
                            <span class="source-file">{c.get("source","Unknown")}</span>{variant_str}{page_str}{elem_type}
                        </div>
                        """,
                        unsafe_allow_html=True,
                    )

            # Save to session state
            st.session_state.messages.append(
                {
                    "role": "assistant",
                    "content": answer,
                    "citations": citations
                }
            )