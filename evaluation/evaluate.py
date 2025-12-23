# evaluation/evaluate.py
# Scalable, behavior-based RAG evaluation
# Enhanced with partial fact-checking using expected_facts where available
# Improved metrics: better grounding, fact coverage, hallucination detection

import sys
import json
import time
import re
from pathlib import Path
import ollama
import numpy as np
from typing import List, Dict

# ---------------------------------------------------------
# Project path setup
# ---------------------------------------------------------
ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

from rag.qa import ask
from rag.retriever import Retriever
from evaluation.dataset import EVAL_QUESTIONS

# ---------------------------------------------------------
# Retriever configuration (updated params for better recall)
# ---------------------------------------------------------
retriever = Retriever(
    top_k=10,  # Increased for better coverage
    min_similarity=0.42,  # Slightly lowered for recall
    min_chunk_length=50
)

# ---------------------------------------------------------
# Utility helpers
# ---------------------------------------------------------
def tokenize(text: str):
    return set(re.findall(r"\b\w+\b", text.lower()))

def extract_sentences(text: str):
    return [s.strip() for s in re.split(r'[.!?]', text) if len(s.strip()) > 10]

def extract_numbers(text: str) -> List[float]:
    return [float(m) for m in re.findall(r'\b\d+(?:\.\d+)?\b', text)]

def extract_years(text: str) -> List[int]:
    return [int(m) for m in re.findall(r'\b(19|20)\d{2}\b', text)]

# ---------------------------------------------------------
# Abstention detection (expanded patterns)
# ---------------------------------------------------------
def is_abstention(answer: str) -> bool:
    patterns = [
        "i don't know", "not found", "not provided", "no information",
        "cannot determine", "based on the provided", "not mentioned",
        "insufficient", "no clear", "unable to answer"
    ]
    a = answer.lower()
    return any(p in a for p in patterns)

# ---------------------------------------------------------
# Improved grounding check (token overlap + similarity threshold)
# ---------------------------------------------------------
def grounded_sentence(sentence: str, context: str, min_overlap_ratio: float = 0.25) -> bool:
    s_tokens = tokenize(sentence)
    c_tokens = tokenize(context)
    overlap = len(s_tokens & c_tokens)
    return overlap / len(s_tokens) >= min_overlap_ratio if s_tokens else False

# ---------------------------------------------------------
# Fact coverage check using expected_facts
# ---------------------------------------------------------
def check_fact_coverage(item: Dict, answer: str) -> Dict:
    coverage = {
        "fact_coverage_rate": 0.0,
        "hallucination_flags": []
    }
    if "expected_facts" not in item:
        return coverage

    expected = item["expected_facts"]
    answer_lower = answer.lower()

    matched = 0
    total = 0

    if item["answer_type"] == "numeric":
        ans_nums = extract_numbers(answer)
        for key, values in expected.items():
            for v in values:
                total += 1
                if any(abs(n - v) <= item.get("numeric_tolerance", 0) for n in ans_nums):
                    matched += 1
                else:
                    coverage["hallucination_flags"].append(f"Missing/wrong {key}: expected ~{v}")

    elif item["answer_type"] == "date":
        ans_years = extract_years(answer)
        for key, values in expected.items():
            for v in values:
                total += 1
                if v in ans_years:
                    matched += 1
                else:
                    coverage["hallucination_flags"].append(f"Wrong {key}: expected {v}")

    elif item["answer_type"] == "descriptive":
        for key, values in expected.items():
            for v in values:
                total += 1
                if any(v.lower() in answer_lower for v in values):
                    matched += 1
                else:
                    coverage["hallucination_flags"].append(f"Missing {key}: expected {v}")

    coverage["fact_coverage_rate"] = matched / total if total else 1.0
    return coverage

# ---------------------------------------------------------
# Improved LLM behavioral judge (better prompt, more aspects)
# ---------------------------------------------------------
def llm_behavior_judge(question: str, answer: str, context: str) -> dict:
    """
    Evaluates BEHAVIOR + completeness.
    """
    prompt = f"""
You are evaluating a RAG system's response behavior and quality.

Question: {question}

Answer: {answer}

Context (first 2000 chars): {context[:2000]}

Score each aspect from 0.0 to 1.0:
- Relevance: How well does the answer address the exact question?
- Specificity: Does it provide precise details without being vague?
- Faithfulness: Does it stick to context without adding unsupported info?
- Completeness: Does it cover all key points from the context?
- Conciseness: Is it direct without unnecessary fluff?

Output JSON only:
{{"relevance": 0.x, "specificity": 0.x, "faithfulness": 0.x, "completeness": 0.x, "conciseness": 0.x}}
"""
    try:
        resp = ollama.chat(
            model="mistral:7b-instruct-q4_0",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2}
        )
        text = resp["message"]["content"].strip()
        scores = json.loads(text)
        return {k: float(v) for k, v in scores.items()}
    except Exception as e:
        print(f"LLM judge error: {e}")
        return {"relevance": 0.5, "specificity": 0.5, "faithfulness": 0.5, "completeness": 0.5, "conciseness": 0.5}

# ---------------------------------------------------------
# Improved Retrieval evaluation (embedding similarity proxy)
# ---------------------------------------------------------
def evaluate_retrieval():
    avg_sim = []
    hit_rate = 0

    for item in EVAL_QUESTIONS:
        question = item["question"]
        results = retriever.retrieve(question)

        if not results:
            continue

        # Avg top-3 similarity as proxy for relevance
        top_sims = [r["score"] for r in results[:3]]
        avg_sim.append(np.mean(top_sims))

        # Hit if best > 0.5
        if results[0]["score"] > 0.5:
            hit_rate += 1

    return {
        "avg_top_similarity": np.mean(avg_sim) if avg_sim else 0.0,
        "relevant_context_hit_rate": hit_rate / len(EVAL_QUESTIONS)
    }

# ---------------------------------------------------------
# End-to-End Evaluation
# ---------------------------------------------------------
def evaluate_end_to_end():
    print("Running Enhanced End-to-End RAG Evaluation...\n")

    detailed = []

    grounded_sentences_total = 0
    sentences_total = 0
    abstentions = 0
    fact_coverage_rates = []
    hallucination_count = 0

    scores = {
        "relevance": [], "specificity": [], "faithfulness": [],
        "completeness": [], "conciseness": []
    }

    for item in EVAL_QUESTIONS:
        question = item["question"]
        response = ask(question)
        answer = response.get("answer", "").strip()
        retrieved = retriever.retrieve(question)
        context = "\n\n".join(r["content"] for r in retrieved)

        abstained = is_abstention(answer)
        if abstained:
            abstentions += 1

        # Grounding
        answer_sentences = extract_sentences(answer)
        grounded_count = sum(1 for s in answer_sentences if grounded_sentence(s, context))
        grounded_sentences_total += grounded_count
        sentences_total += len(answer_sentences)

        # Fact coverage (if expected_facts present)
        fact_check = check_fact_coverage(item, answer)
        if "fact_coverage_rate" in fact_check:
            fact_coverage_rates.append(fact_check["fact_coverage_rate"])
            hallucination_count += len(fact_check["hallucination_flags"])

        # LLM judge
        judge_scores = llm_behavior_judge(question, answer, context)
        for k in scores:
            scores[k].append(judge_scores.get(k, 0.5))

        detailed.append({
            "id": item["id"],
            "question": question,
            "answer": answer,
            "abstained": abstained,
            "grounded_sentence_ratio": grounded_count / len(answer_sentences) if answer_sentences else 1.0,
            "fact_coverage": fact_check.get("fact_coverage_rate", "N/A"),
            "hallucination_flags": fact_check.get("hallucination_flags", []),
            **judge_scores,
            "source_hint": item.get("source_hint", "unknown")
        })

        time.sleep(0.5)  # Increased delay to avoid rate limits

    # Aggregate
    summary = {
        "abstention_rate": abstentions / len(EVAL_QUESTIONS),
        "grounded_sentence_rate": grounded_sentences_total / sentences_total if sentences_total else 1.0,
        "avg_fact_coverage": np.mean(fact_coverage_rates) if fact_coverage_rates else "N/A",
        "total_hallucinations": hallucination_count,
        **{f"avg_{k}": np.mean(v) for k, v in scores.items()}
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

    print("\n=== FINAL ENHANCED RAG EVALUATION ===")
    print(json.dumps(final, indent=2))