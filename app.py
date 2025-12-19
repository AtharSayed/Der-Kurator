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
# Global Styling (SAFE – no widget wrapping)
# =====================================================
st.markdown(
    """
    <style>
    .title {
        font-size: 36px;
        font-weight: 700;
        margin-bottom: 4px;
    }
    .subtitle {
        font-size: 16px;
        color: #6b7280;
        margin-bottom: 24px;
    }
    .section-label {
        font-size: 15px;
        font-weight: 600;
        margin-bottom: 6px;
    }
    .answer-box {
        background-color: #f9fafb;
        padding: 20px;
        border-radius: 14px;
        border: 1px solid #e5e7eb;
        margin-top: 24px;
        font-size: 16px;
        line-height: 1.6;
    }
    .citation-box {
        background-color: #ffffff;
        padding: 16px;
        border-radius: 12px;
        border: 1px dashed #d1d5db;
        margin-top: 16px;
        font-size: 14px;
    }
    .footer {
        margin-top: 48px;
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
st.markdown(
    '<div class="title">Porsche 911 Knowledge Assistant</div>',
    unsafe_allow_html=True
)
st.markdown(
    '<div class="subtitle">Accurate answers grounded strictly in verified Porsche 911 documents</div>',
    unsafe_allow_html=True
)

# =====================================================
# Trust Message
# =====================================================
st.success(
    "✔️ This assistant answers questions using only curated Porsche 911 documentation. "
    "If information is not explicitly available, it will clearly say so."
)

# =====================================================
# Question Input
# =====================================================
st.markdown(
    '<div class="section-label">Ask a question</div>',
    unsafe_allow_html=True
)

question = st.text_input(
    "Porsche 911 Question",
    placeholder="e.g. What is the torque of the Porsche 911?",
    label_visibility="collapsed"
)

ask_btn = st.button("Get Answer", use_container_width=True)

# =====================================================
# Answer + Citations Output
# =====================================================
if ask_btn:
    if not question.strip():
        st.warning("Please enter a question related to Porsche 911.")
    else:
        with st.spinner("Finding the most accurate answer..."):
            result = ask(question)

        # Explicit extraction
        answer = result.get("answer", "").strip()
        citations = result.get("citations", [])

        # ---- Answer ----
        st.markdown('<div class="answer-box">', unsafe_allow_html=True)
        st.markdown("**Answer**")
        st.write(answer)
        st.markdown('</div>', unsafe_allow_html=True)

        # ---- Citations (ONLY if answer is grounded) ----
        if citations and not answer.lower().startswith("i don't know"):
            st.markdown('<div class="citation-box">', unsafe_allow_html=True)
            st.markdown("**Sources**")

            seen = set()
            for c in citations:
                key = (c.get("source"), c.get("page"), c.get("slide"))
                if key in seen:
                    continue
                seen.add(key)

                ref = f"- {c.get('source', 'Unknown source')}"
                if c.get("page") is not None:
                    ref += f" (page {c['page']})"
                if c.get("slide") is not None:
                    ref += f" (slide {c['slide']})"

                st.markdown(ref)

            st.markdown('</div>', unsafe_allow_html=True)

# =====================================================
# Footer
# =====================================================
st.markdown(
    """
    <div class="footer">
    Porsche 911 Knowledge Assistant · Citation-backed, document-grounded responses
    </div>
    """,
    unsafe_allow_html=True
)
