# app.py
import streamlit as st
import base64
from rag.qa import ask

# Function to encode the background image
@st.cache_data
def get_base64_encoded_image(image_path):
    with open(image_path, "rb") as img_file:
        return base64.b64encode(img_file.read()).decode('utf-8')

# Path to your chosen image
image_path = "data/images/Porsche 911 Carrera T parked in a courtyard.jpeg"

# Encode the image
try:
    base64_image = get_base64_encoded_image(image_path)
except FileNotFoundError:
    st.error(f"Background image not found at {image_path}. Please ensure the file exists and the path is correct relative to app.py.")
    base64_image = None

st.set_page_config(
    page_title="Porsche 911 Knowledge Assistant",
    page_icon="🏎️",
    layout="centered",
    initial_sidebar_state="collapsed",
    menu_items={
        'About': "A document-grounded RAG assistant for Porsche 911 technical and historical information."
    }
)

# Custom CSS for premium, elegant design
st.markdown(f"""
<style>
    /* Import premium font (Montserrat for modern, elegant feel) */
    @import url('https://fonts.googleapis.com/css2?family=Montserrat:wght@400;600;800&display=swap');
    
    /* Apply font globally */
    html, body, [class*="css"]  {{
        font-family: 'Montserrat', sans-serif;
    }}
    
    /* Full-screen background image */
    .stApp {{
        background-image: url("data:image/jpeg;base64,{base64_image if base64_image else ''}");
        background-size: cover;
        background-position: center;
        background-repeat: no-repeat;
        background-attachment: fixed;
    }}
    
    /* Optimized semi-transparent black overlay for visibility */
    .stApp::before {{
        content: "";
        position: fixed;
        top: 0;
        left: 0;
        width: 100%;
        height: 100%;
        background-color: rgba(0, 0, 0, 0.65);  /* Balanced opacity for visibility without hiding image */
        z-index: -1;
        pointer-events: none;
    }}
    
    /* Porsche-inspired primary colors */
    :root {{
        --porsche-red: #B12B28;
        --porsche-dark: #1a1a1a;
        --porsche-gray: #3d3d3d;
        --porsche-light: #f5f5f5;
    }}
    
    /* Title styling - premium typography */
    .main-title {{
        font-size: 3.8rem;
        font-weight: 800;
        text-align: center;
        color: white;
        margin-bottom: 0.3rem;
        text-shadow: 2px 2px 6px rgba(0,0,0,0.7);
        letter-spacing: 0.5px;
    }}
    
    .subtitle {{
        font-size: 1.65rem;
        text-align: center;
        color: #ffffff;                  /* Pure white for maximum contrast */
        margin-bottom: 3rem;
        text-shadow: 
        0 0 8px rgba(0,0,0,0.8),
        2px 2px 6px rgba(0,0,0,0.9); /* Stronger, multi-layered shadow for better visibility */
        font-weight: 800;
        letter-spacing: 0.8px;
    }}
    
    
    /* Trust badge - elegant card design */
    .trust-badge {{
        background-color: rgba(255, 255, 255, 0.88);
        border-left: 6px solid #28a745;
        padding: 1.4rem 1.8rem;
        border-radius: 12px;
        margin: 2.5rem 0;
        font-size: 1.15rem;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        color: #222;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.15);
    }}
    
    /* Chat messages - premium glassmorphism */
    .stChatMessage {{
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 16px;
        padding: 1.4rem 1.8rem;
        margin: 1.2rem 0;
        box-shadow: 0 8px 24px rgba(0,0,0,0.25);
        backdrop-filter: blur(12px);
        border: 1px solid rgba(255,255,255,0.2);
    }}
    
    /* User message subtle styling */
    div[data-testid="stChatMessage"]:has(div[data-testid="chat-message-user"]) {{
        background-color: rgba(240, 240, 240, 0.92);
    }}
    
    /* Assistant message with red accent */
    div[data-testid="stChatMessage"]:has(div[data-testid="chat-message-assistant"]) {{
        border-left: 6px solid var(--porsche-red);
        background-color: rgba(255, 248, 240, 0.94);
    }}
    
    /* Sources styling - clean and minimal */
    .sources-header {{
        font-size: 1.35rem;
        font-weight: 600;
        color: var(--porsche-dark);
        margin-top: 1.8rem;
        margin-bottom: 1rem;
    }}
    
    .source-item {{
        background-color: rgba(249, 249, 249, 0.85);
        padding: 1rem 1.4rem;
        border-radius: 10px;
        margin-bottom: 0.8rem;
        border: 1px solid rgba(0,0,0,0.1);
        box-shadow: 0 2px 6px rgba(0,0,0,0.1);
    }}
    
    .source-file {{
        font-weight: 600;
        color: var(--porsche-red);
    }}
    
    .source-detail {{
        color: #555;
        font-size: 0.95rem;
    }}
    
 
    /* Button styling - premium hover effects */
    .stButton > button {{
        background-color: var(--porsche-red);
        color: white;
        border-radius: 10px;
        border: none;
        padding: 0.8rem 2rem;
        font-weight: 600;
        transition: all 0.4s ease;
        box-shadow: 0 4px 12px rgba(177,43,40,0.3);
    }}
    
    .stButton > button:hover {{
        background-color: #a02020;
        transform: translateY(-4px);
        box-shadow: 0 8px 20px rgba(177,43,40,0.5);
    }}
    
    /* Chat input styling for premium feel */
    div[data-testid="column"] > div > div > div > div > div.stTextInput {{
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 12px;
        padding: 0.5rem;
        box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        backdrop-filter: blur(10px);
    }}
    
    /* Spinner and info boxes */
    .stSpinner, .stInfo, .stError {{
        background-color: rgba(255, 255, 255, 0.92);
        border-radius: 12px;
        padding: 1rem;
        box-shadow: 0 4px 16px rgba(0,0,0,0.25);
    }}
</style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-title">Porsche 911 Knowledge Assistant</div>', unsafe_allow_html=True)
st.markdown('<div class="subtitle">Ask me anything about the Porsche 911 technical specs and history!</div>', unsafe_allow_html=True)



# Initialize chat history
if "messages" not in st.session_state:
    st.session_state.messages = []

# Display chat history
for message in st.session_state.messages:
    with st.chat_message(message["role"], avatar="🏎️" if message["role"] == "assistant" else None):
        st.markdown(message["content"])
        if "citations" in message:
            st.markdown('<div class="sources-header">📑 Sources</div>', unsafe_allow_html=True)
            for idx, c in enumerate(message["citations"], 1):
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
                    ref += f" <span class='source-detail'>— {' • '.join(details)}</span>"
                st.markdown(f'<div class="source-item">{ref}</div>', unsafe_allow_html=True)

# User input
if question := st.chat_input("Ask a question about the Porsche 911 (e.g., What is the horsepower of the 2024 Porsche 911 Turbo S?)"):
    st.session_state.messages.append({"role": "user", "content": question})
    with st.chat_message("user"):
        st.markdown(question)

    with st.chat_message("assistant", avatar="🏎️"):
        with st.spinner("Searching documents and generating answer..."):
            try:
                result = ask(question.strip())
                answer = result.get("answer", "").strip()
                citations = result.get("citations", [])

                # Deduplicate citations
                seen = set()
                unique_citations = []
                for c in citations:
                    key = (c.get("source"), c.get("page"), c.get("slide"))
                    if key not in seen:
                        seen.add(key)
                        unique_citations.append(c)

                # Display answer
                if answer.lower().startswith("i don't know") or "error" in answer.lower():
                    st.info(answer)
                else:
                    st.markdown(answer)

                # Display sources
                if unique_citations:
                    st.markdown('<div class="sources-header">📑 Sources</div>', unsafe_allow_html=True)
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
                            ref += f" <span class='source-detail'>— {' • '.join(details)}</span>"
                        st.markdown(f'<div class="source-item">{ref}</div>', unsafe_allow_html=True)
                elif not answer.lower().startswith("i don't know"):
                    st.caption("Answer generated from document context (no direct citation available).")

                # Store in session
                st.session_state.messages.append({
                    "role": "assistant",
                    "content": answer,
                    "citations": unique_citations if unique_citations else None
                })

            except Exception as e:
                st.error(f"An error occurred: {str(e)}")
