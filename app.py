import streamlit as st
from rag.qa import ask

# =====================================================
# Page Configuration
# =====================================================
st.set_page_config(
    page_title="Porsche 911 Knowledge Assistant",
    page_icon="🏎️",
    layout="centered"
)

# =====================================================
# Minimal Premium Styling
# =====================================================
st.markdown(
    """
    <style>
    body {
        background-color: #ffffff;
    }
    .title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 6px;
    }
    .subtitle {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 28px;
    }
    .card {
        background-color: #f9fafb;
        padding: 22px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
    }
    .answer-card {
        background-color: #ffffff;
        padding: 22px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        margin-top: 24px;
        font-size: 16px;
        line-height: 1.6;
    }
    .footer {
        margin-top: 40px;
        text-align: center;
        font-size: 13px;
        color: #9ca3af;
    }
    </style>
    """,
    unsafe_allow_html=True
)

# =====================================================
# Header
# =====================================================
st.markdown('<div class="title">Porsche 911 Knowledge Assistant</div>', unsafe_allow_html=True)
st.markdown(
    '<div class="subtitle">Accurate answers sourced directly from official Porsche 911 documents</div>',
    unsafe_allow_html=True
)

# =====================================================
# Trust Message (Client-Friendly)
# =====================================================
st.success(
    "✔️ This assistant provides answers based only on verified Porsche 911 documentation. "
    "If information is unavailable, it will clearly state so."
)

# =====================================================
# Question Input
# =====================================================
st.markdown('<div class="card">', unsafe_allow_html=True)

question = st.text_input(
    "Ask a question",
    placeholder="e.g. What is the difference between the Porsche 911 Carrera and GT3?",
    label_visibility="collapsed"
)

ask_btn = st.button("Get Answer", use_container_width=True)

st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# Answer Output (No Chat History)
# =====================================================
if ask_btn:
    if not question.strip():
        st.warning("Please enter a question related to Porsche 911.")
    else:
        with st.spinner("Finding the most accurate answer..."):
            answer = ask(question)

        st.markdown('<div class="answer-card">', unsafe_allow_html=True)
        st.markdown("**Answer**")
        st.write(answer)
        st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# Footer (No Tech Jargon)
# =====================================================
st.markdown(
    """
    <div class="footer">
    Porsche 911 Knowledge Assistant · Designed for clarity & accuracy
    </div>
    """,
    unsafe_allow_html=True
)
