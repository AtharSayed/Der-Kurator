# rag/qa.py
import asyncio
import logging
from concurrent.futures import ThreadPoolExecutor
from functools import lru_cache
from typing import Dict, List

import ollama
from rag.retriever import Retriever
from rag.prompt import PROMPT_TEMPLATE

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize retriever with optimized params
retriever = Retriever(
    top_k=10,
    min_similarity=0.42,
    min_chunk_length=50,
    variant_boost=0.18
)

SPEC_KEYWORDS = [
    "torque", "hp", "horsepower", "power", "nm", "lb-ft", "bhp", "kw",
    "acceleration", "top speed", "0-60", "0-100", "0 to ", "weight", "displacement"
]

REFUSAL_PHRASES = [
    "i don't know", "not mentioned", "not in the documents", "no information",
    "unable to find", "cannot answer", "not provided", "no data", "insufficient",
    "not explicitly stated", "no clear match"
]

@lru_cache(maxsize=256)
def _cached_retrieve(question: str) -> List[Dict]:
    """Cached retrieval to avoid re-embedding identical queries."""
    try:
        return retriever.retrieve(question)
    except Exception as e:
        logger.error(f"Retrieval error for query '{question}': {e}")
        return []

def _build_context(retrieved: List[Dict]) -> str:
    return "\n\n".join(r["content"] for r in retrieved)

def _is_spec_question(question: str) -> bool:
    return any(k in question.lower() for k in SPEC_KEYWORDS)

async def ask_async(question: str) -> Dict:
    """
    Asynchronous version of ask() – recommended for Streamlit integration.
    """
    question = question.strip()
    if not question:
        return {"answer": "Please provide a valid question.", "citations": []}

    # Retrieve with cache
    retrieved = _cached_retrieve(question)

    if not retrieved:
        return {
            "answer": "I don't know — no relevant information was found in the documents.",
            "citations": []
        }

    best_score = retrieved[0]["score"]
    threshold = 0.38 if _is_spec_question(question) else 0.45

    if best_score < threshold:
        return {
            "answer": "I don't know — insufficient confidence based on available documents.",
            "citations": []
        }

    context = _build_context(retrieved)
    prompt = PROMPT_TEMPLATE.format(context=context, question=question)

    loop = asyncio.get_event_loop()
    try:
        with ThreadPoolExecutor() as pool:
            response = await loop.run_in_executor(
                pool,
                lambda: ollama.chat(
                    model="mistral:7b-instruct-q4_0",
                    messages=[{"role": "user", "content": prompt}],
                    options={
                        "temperature": 0.0,
                        "num_ctx": 8192,
                        "max_tokens": 700
                    }
                )
            )
        answer = response["message"]["content"].strip()
    except Exception as e:
        logger.error(f"Ollama generation error: {e}")
        return {
            "answer": "Sorry, I encountered an error while generating the response. Please try again.",
            "citations": []
        }

    # Strong refusal detection
    if any(phrase in answer.lower() for phrase in REFUSAL_PHRASES):
        return {
            "answer": "I don't know based on the provided Porsche 911 documents.",
            "citations": []
        }

    citations = retriever.get_citations(retrieved)

    return {
        "answer": answer,
        "citations": citations,
        "best_score": round(best_score, 3),
        "num_sources": len(citations)
    }

# Synchronous wrapper for backward compatibility
def ask(question: str) -> Dict:
    """Synchronous fallback – uses async under the hood."""
    return asyncio.run(ask_async(question))