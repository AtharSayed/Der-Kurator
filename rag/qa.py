import ollama
from rag.retriever import Retriever

# Initialize retriever once (important for performance)
retriever = Retriever(top_k=5)

def ask(question: str) -> str:
    """
    Answer a question using retrieved Porsche 911 context.
    """
    context = retriever.build_context(question)

    if not context.strip():
        return "I don’t know based on the provided Porsche 911 documents."

    prompt = f"""
You are a Porsche 911 knowledge assistant.

Use ONLY the information in the context below to answer.
If the answer is not present, say you don't know.

Context:
{context}

Question:
{question}

Answer:
"""

    response = ollama.chat(
        model="mistral:7b-instruct-q4_0",
        messages=[{"role": "user", "content": prompt}]
    )

    return response["message"]["content"]
