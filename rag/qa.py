# rag/qa.py
import ollama
from rag.retriever import Retriever
from rag.prompt import PROMPT_TEMPLATE

retriever = Retriever(
    top_k=9,
    min_similarity=0.44,
    min_chunk_length=50,
    variant_boost=0.18
)

SPEC_KEYWORDS = ["torque", "hp", "horsepower", "power", "nm", "lb-ft", "bhp", "kw",
                 "acceleration", "top speed", "0-60", "0-100", "0 to ", "weight"]

REFUSAL_PHRASES = [
    "i don't know", "not mentioned", "not in the documents", "no information",
    "unable to find", "cannot answer", "not provided", "no data"
]

def ask(question: str) -> dict:
    retrieved = retriever.retrieve(question)

    if not retrieved:
        return {
            "answer": "I don't know — no relevant information found in the Porsche 911 documents.",
            "citations": []
        }

    best_score = retrieved[0]["score"]

    is_spec = any(k in question.lower() for k in SPEC_KEYWORDS)
    threshold = 0.38 if is_spec else 0.45

    if best_score < threshold:
        return {
            "answer": "I don't know — insufficient confidence or no clear match in documents.",
            "citations": []
        }

    context = "\n\n".join(r["content"] for r in retrieved)

    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    try:
        response = ollama.chat(
            model="mistral:7b-instruct-q4_0",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.0, "max_tokens": 700}
        )
        answer = response["message"]["content"].strip()
    except Exception as e:
        return {"answer": f"Error: {str(e)}", "citations": []}

    # Stronger refusal detection
    if any(phrase in answer.lower() for phrase in REFUSAL_PHRASES):
        return {
            "answer": "I don't know based on the provided Porsche 911 documents.",
            "citations": []
        }

    citations = retriever.get_citations(retrieved)

    return {
        "answer": answer,
        "citations": citations,
        "best_score": round(best_score, 3)
    }