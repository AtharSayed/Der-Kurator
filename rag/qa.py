import ollama
from rag.retriever import Retriever
from rag.prompt import PROMPT_TEMPLATE

# Initialize retriever once (important for performance)
retriever = Retriever(top_k=5)

def ask(question: str) -> dict:
    """
    Returns:
        {
            "answer": str,
            "citations": list[dict]
        }
    """

    # 1. Retrieve context
    context = retriever.build_context(question)

    # 2. Handle empty retrieval (safety)
    if not context.strip():
        return {
            "answer": "I don't know based on the provided Porsche 911 documents.",
            "citations": []
        }

    # 3. Build prompt using centralized template
    prompt = PROMPT_TEMPLATE.format(
        context=context,
        question=question
    )

    # 4. Call LLM
    response = ollama.chat(
        model="mistral:7b-instruct-q4_0",
        messages=[{"role": "user", "content": prompt}]
    )

    answer = response["message"]["content"]

    # 5. Collect citations
    citations = retriever.get_citations(question)

    return {
        "answer": answer,
        "citations": citations
    }
