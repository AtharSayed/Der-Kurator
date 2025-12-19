# rag/qa.py
import ollama
from rag.retriever import Retriever
from rag.prompt import PROMPT_TEMPLATE

retriever = Retriever(
    top_k=8,
    min_similarity=0.50,  # Balanced for precision
    min_chunk_length=50
)

SPEC_KEYWORDS = ["torque", "hp", "horsepower", "power", "nm", "lb-ft", "bhp", "kw", "acceleration", "top speed", "0-60", "0-100"]

def ask(question: str) -> dict:
    retrieved = retriever.retrieve(question)

    if not retrieved:
        return {
            "answer": "I don't know based on the provided Porsche 911 documents.",
            "citations": []
        }

    best_similarity = retrieved[0]["score"]

    is_spec_question = any(k in question.lower() for k in SPEC_KEYWORDS)
    effective_threshold = 0.45 if is_spec_question else 0.50

    if best_similarity < effective_threshold:
        return {
            "answer": "I don't know based on the provided Porsche 911 documents.",
            "citations": []
        }

    context = "\n\n".join(r["content"] for r in retrieved)

    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    try:
        response = ollama.chat(
            model="mistral:7b-instruct-q4_0",
            messages=[{"role": "user", "content": prompt}]
        )
        answer = response["message"]["content"].strip()
    except Exception as e:
        answer = "Error generating answer: " + str(e)

    if "i don't know" in answer.lower() or "not mentioned" in answer.lower():
        return {
            "answer": "I don't know based on the provided Porsche 911 documents.",
            "citations": []
        }

    return {
        "answer": answer,
        "citations": retriever.get_citations(question)
    }