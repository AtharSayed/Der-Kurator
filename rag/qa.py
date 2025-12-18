# rag/qa.py
import faiss, pickle
from sentence_transformers import SentenceTransformer
import ollama
from rag.prompt import PROMPT_TEMPLATE

model = SentenceTransformer("all-MiniLM-L6-v2")
index = faiss.read_index("embeddings/vector_store/index.faiss")
chunks, metadata = pickle.load(open("embeddings/vector_store/data.pkl", "rb"))

def ask(question, k=3):
    q_emb = model.encode([question])
    _, idx = index.search(q_emb, k)

    context = "\n\n".join([chunks[i] for i in idx[0]])

    prompt = PROMPT_TEMPLATE.format(
        context=context,
        question=question
    )

    response = ollama.chat(
        model="mistral:7b-instruct-q4_0",
        messages=[{"role": "user", "content": prompt}]
    )


    return response["message"]["content"]
