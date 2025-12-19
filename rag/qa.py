import ollama
from rag.retriever import Retriever
from rag.prompt import PROMPT_TEMPLATE

retriever = Retriever(top_k=5)

MAX_DISTANCE_THRESHOLD = 0.55   # relaxed slightly
SPEC_KEYWORDS = ["torque", "hp", "power", "nm", "lb-ft", "bhp"]

def ask(question: str) -> dict:
    retrieved = retriever.retrieve(question)

    if not retrieved:
        return {
            "answer": "I don't know based on the provided Porsche 911 documents.",
            "citations": []
        }

    best_score = retrieved[0]["score"]

    # 🔒 Smarter gate
    is_spec_question = any(k in question.lower() for k in SPEC_KEYWORDS)

    if best_score > MAX_DISTANCE_THRESHOLD and not is_spec_question:
        return {
            "answer": "I don't know based on the provided Porsche 911 documents.",
            "citations": []
        }

    context = "\n\n".join(r["content"] for r in retrieved)

    prompt = PROMPT_TEMPLATE.format(
        context=context,
        question=question
    )

    response = ollama.chat(
        model="mistral:7b-instruct-q4_0",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response["message"]["content"]

    # 🚫 Final safety: model still refused
    if "i don't know" in answer.lower():
        return {
            "answer": "I don't know based on the provided Porsche 911 documents.",
            "citations": []
        }

    return {
        "answer": answer,
        "citations": retriever.get_citations(question)
    }
