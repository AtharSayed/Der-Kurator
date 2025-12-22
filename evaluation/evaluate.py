# evaluation/evaluate.py
# Scalable, behavior-based RAG evaluation
# Does NOT rely on gold answers

import sys
import json
import time
import re
from pathlib import Path
import ollama

# ---------------------------------------------------------
# Project path setup
# ---------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from rag.qa import ask
from rag.retriever import Retriever
from evaluation.dataset import EVAL_QUESTIONS

# ---------------------------------------------------------
# Retriever configuration
# ---------------------------------------------------------
retriever = Retriever(
    top_k=8,
    min_similarity=0.45,
    min_chunk_length=60
)

# ---------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------
def tokenize(text: str):
    return set(re.findall(r"\b\w+\b", text.lower()))

def extract_sentences(text: str):
    return [s.strip() for s in text.split(".") if len(s.strip()) > 10]

# ---------------------------------------------------------
# Abstention detection
# ---------------------------------------------------------
def is_abstention(answer: str) -> bool:
    patterns = [
        "i don't know",
        "not found",
        "not provided",
        "no information",
        "cannot determine",
        "based on the provided"
    ]
    a = answer.lower()
    return any(p in a for p in patterns)

# ---------------------------------------------------------
# Grounding check (token overlap)
# ---------------------------------------------------------
def grounded_sentence(sentence: str, context: str, min_overlap: int = 3) -> bool:
    s_tokens = tokenize(sentence)
    c_tokens = tokenize(context)
    return len(s_tokens & c_tokens) >= min_overlap

# ---------------------------------------------------------
# LLM behavioral judge (NOT fact correctness)
# ---------------------------------------------------------
def llm_behavior_judge(question: str, answer: str, context: str) -> dict:
    """
    Evaluates BEHAVIOR, not factual correctness.
    """
    prompt = f"""
You are evaluating the behavior of a RAG system.

Question:
{question}

Answer:
{answer}

Context:
{context[:2500]}

Evaluate ONLY these aspects (score 0–1):
1. Relevance: Does the answer address the question?
2. Specificity: Is the answer as specific as the context allows?
3. Faithfulness: Does the answer avoid adding unsupported information?

Return JSON only:
{{"relevance": x, "specificity": y, "faithfulness": z}}
"""
    try:
        resp = ollama.chat(
            model="mistral:7b-instruct-q4_0",
            messages=[{"role": "user", "content": prompt}]
        )
        text = resp["message"]["content"]
        scores = json.loads(text)
        return {
            "relevance": float(scores.get("relevance", 0.5)),
            "specificity": float(scores.get("specificity", 0.5)),
            "faithfulness": float(scores.get("faithfulness", 0.5)),
        }
    except Exception:
        return {"relevance": 0.5, "specificity": 0.5, "faithfulness": 0.5}

# ---------------------------------------------------------
# Retrieval evaluation (answerability proxy)
# ---------------------------------------------------------
def evaluate_retrieval():
    hits = 0

    for item in EVAL_QUESTIONS:
        question = item["question"]
        results = retriever.retrieve(question)

        # Proxy: at least one chunk has overlap with question
        q_tokens = tokenize(question)
        found = False
        for r in results:
            if len(tokenize(r["content"]) & q_tokens) >= 2:
                found = True
                break

        if found:
            hits += 1

    return {
        "context_coverage_rate": hits / len(EVAL_QUESTIONS)
    }

# ---------------------------------------------------------
# End-to-End Evaluation (Behavior + Grounding)
# ---------------------------------------------------------
def evaluate_end_to_end():
    print("Running Scalable End-to-End RAG Evaluation...\n")

    detailed = []

    grounded_sentences_total = 0
    sentences_total = 0
    abstentions = 0

    relevance_scores = []
    specificity_scores = []
    faithfulness_scores = []

    for item in EVAL_QUESTIONS:
        question = item["question"]
        response = ask(question)
        answer = response.get("answer", "").strip()
        context = retriever.build_context(question)

        abstained = is_abstention(answer)
        if abstained:
            abstentions += 1

        # -------------------------------
        # Grounding analysis
        # -------------------------------
        answer_sentences = extract_sentences(answer)
        grounded_count = 0

        for s in answer_sentences:
            if grounded_sentence(s, context):
                grounded_count += 1

        grounded_sentences_total += grounded_count
        sentences_total += len(answer_sentences)

        # -------------------------------
        # Behavioral LLM judge
        # -------------------------------
        judge_scores = llm_behavior_judge(question, answer, context)

        relevance_scores.append(judge_scores["relevance"])
        specificity_scores.append(judge_scores["specificity"])
        faithfulness_scores.append(judge_scores["faithfulness"])

        detailed.append({
            "id": item["id"],
            "question": question,
            "answer": answer,
            "abstained": abstained,
            "grounded_sentence_ratio":
                grounded_count / len(answer_sentences) if answer_sentences else 1.0,
            "relevance": judge_scores["relevance"],
            "specificity": judge_scores["specificity"],
            "faithfulness": judge_scores["faithfulness"],
            "source_hint": item.get("source_hint", "unknown")
        })

        time.sleep(0.3)

    # -------------------------------
    # Aggregate metrics
    # -------------------------------
    summary = {
        "abstention_rate": abstentions / len(EVAL_QUESTIONS),
        "grounded_sentence_rate":
            grounded_sentences_total / sentences_total if sentences_total else 1.0,
        "avg_relevance": sum(relevance_scores) / len(relevance_scores),
        "avg_specificity": sum(specificity_scores) / len(specificity_scores),
        "avg_faithfulness": sum(faithfulness_scores) / len(faithfulness_scores)
    }

    output_path = Path("evaluation/detailed_results.json")
    output_path.parent.mkdir(exist_ok=True)

    with open(output_path, "w") as f:
        json.dump({"summary": summary, "details": detailed}, f, indent=2)

    print("\n=== End-to-End Evaluation Summary ===")
    print(json.dumps(summary, indent=2))
    print(f"\nDetailed results saved to {output_path}")

    return summary

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
if __name__ == "__main__":
    retrieval_metrics = evaluate_retrieval()
    e2e_metrics = evaluate_end_to_end()

    final = {
        "retrieval": retrieval_metrics,
        "end_to_end": e2e_metrics
    }

    print("\n=== FINAL SCALABLE RAG EVALUATION ===")
    print(json.dumps(final, indent=2))
