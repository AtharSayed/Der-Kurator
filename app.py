# app.py
import streamlit as st
from rag.qa import ask

st.set_page_config(
    page_title="Porsche 911 Knowledge Assistant",
    page_icon="🏎️",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "A document-grounded RAG assistant for Porsche 911 technical and historical information."
    }
)

# Custom CSS (unchanged from your version)
st.markdown("""
<style>
/* Your CSS here - unchanged */
</style>
""", unsafe_allow_html=True)

# Header (unchanged)
st.markdown('<div class="main-title">Porsche 911 Knowledge Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Get precise, citation-backed answers from official Porsche 911 documentation</div>', unsafe_allow_html=True)

# Trust message (unchanged)
st.markdown("""
<div class="trust-badge">
<strong>✔️ Document-Grounded Responses Only</strong><br>
This assistant uses only ingested Porsche 911 documents (PDFs, PPTX, DOCX, TXT). 
If information is not present in the source material, it will honestly say "I don't know" rather than hallucinate.
</div>
""", unsafe_allow_html=True)

# Question input (unchanged)
st.markdown("### Ask a question about the Porsche 911")

question = st.text_input(
    label="Your question",
    placeholder="e.g., What is the horsepower of the 2024 Porsche 911 Turbo S?",
    key="question_input",
    label_visibility="collapsed"
)

col1, col2, col3 = st.columns([1, 2, 1])
ask_btn = col2.button("🚀 Get Answer", type="primary", use_container_width=True)

# Answer Processing & Display
if ask_btn:
    if not question.strip():
        st.warning("Please enter a question about the Porsche 911.")
        st.stop()

    with st.spinner("Searching Porsche 911 documents and generating answer..."):
        try:
            result = ask(question.strip())
            answer = result.get("answer", "").strip()
            citations = result.get("citations", [])
        except Exception as e:
            st.error(f"An error occurred: {str(e)}")
            st.stop()

    st.markdown('<div class="answer-container">', unsafe_allow_html=True)

    st.markdown('<div class="answer-header">💡 Answer</div>', unsafe_allow_html=True)
    if answer.lower().startswith("i don't know") or "error" in answer.lower():
        st.info(answer)
    else:
        st.write(answer)

    if citations:
        st.markdown('<div class="sources-header">📑 Sources</div>', unsafe_allow_html=True)

        seen = set()
        unique_citations = []
        for c in citations:
            key = (c.get("source"), c.get("page"), c.get("slide"))
            if key not in seen:
                seen.add(key)
                unique_citations.append(c)

        for idx, c in enumerate(unique_citations, 1):
            source_name = c.get("source", "Unknown")
            ref = f"**{idx}.** <span class='source-file'>{source_name}</span>"

            details = []
            if c.get("page") is not None:
                details.append(f"Page {c['page']}")
            if c.get("slide") is not None:
                details.append(f"Slide {c['slide']}")
            if c.get("chunk_index") is not None:
                details.append(f"Chunk {c['chunk_index']}")

            if details:
                ref += f"<span class='source-detail'>— {' • '.join(details)}</span>"

            st.markdown(f'<div class="source-item">{ref}</div>', unsafe_allow_html=True)

    else:
        if not answer.lower().startswith("i don't know"):
            st.caption("Answer generated from document context (no direct citation available).")

    st.markdown('</div>', unsafe_allow_html=True)

# Footer (unchanged)
st.markdown("""
<div class="footer">
    Porsche 911 Knowledge Assistant • Built with RAG • Document-grounded • No hallucinations<br>
    Powered by sentence-transformers, FAISS, and Ollama
</div>
""", unsafe_allow_html=True)