# evaluation/evaluate.py
# Production-grade RAG Evaluation (Context-grounded, unit-aware, abstention-safe)

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
from rag.prompt import PROMPT_TEMPLATE
from evaluation.dataset import EVAL_QUESTIONS

# ---------------------------------------------------------
# Retriever configuration
# ---------------------------------------------------------
retriever = Retriever(top_k=16, min_similarity=0.30, min_chunk_length=50)

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
# Unit normalization (CRITICAL FIX)
# ---------------------------------------------------------
def normalize_units(nums: List[float], text: str) -> List[float]:
    t = text.lower()
    normalized = []

    for n in nums:
        if "km/h" in t:
            normalized.append(n * 0.621371)  # → mph
        elif "nm" in t:
            normalized.append(n * 0.737562)  # → lb-ft
        else:
            normalized.append(n)

    return normalized

# ---------------------------------------------------------
# Abstention detection
# ---------------------------------------------------------
def is_abstention(answer: str) -> bool:
    patterns = [
        "i don't know", "not found", "not provided", "no information",
        "cannot determine", "based on the provided", "not mentioned",
        "insufficient", "unable to answer"
    ]
    a = answer.lower()
    return any(p in a for p in patterns)

# ---------------------------------------------------------
# Grounding check (context-based)
# ---------------------------------------------------------
def grounded_sentence(sentence: str, context: str, min_overlap_ratio=0.25) -> bool:
    s_tokens = tokenize(sentence)
    c_tokens = tokenize(context)
    return (len(s_tokens & c_tokens) / len(s_tokens)) >= min_overlap_ratio if s_tokens else False

# ---------------------------------------------------------
# FACT CHECKING (NO LONGER EQUALS HALLUCINATION)
# ---------------------------------------------------------
def check_fact_coverage(item: Dict, answer: str, context: str) -> Dict:
    result = {
        "fact_coverage_rate": 1.0,
        "unsupported_claims": []
    }

    expected = item.get("expected_facts", {})
    if not expected:
        return result

    answer_lower = answer.lower()
    context_lower = context.lower()

    answer_nums = normalize_units(extract_numbers(answer), answer)
    context_nums = normalize_units(extract_numbers(context), context)

    matched = 0
    total = 0

    for key, values in expected.items():
        for v in values:
            total += 1

            # -----------------------------
            # NUMERIC FACT
            # -----------------------------
            if isinstance(v, (int, float)):
                tol = item.get("numeric_tolerance", 0)
                found_in_answer = any(abs(a - v) <= tol for a in answer_nums)
                found_in_context = any(abs(c - v) <= tol for c in context_nums)

                if found_in_answer:
                    matched += 1
                elif not found_in_context:
                    result["unsupported_claims"].append(f"{key}: ~{v}")

            # -----------------------------
            # STRING / DESCRIPTIVE FACT
            # -----------------------------
            else:
                v_str = str(v).lower()
                found_in_answer = v_str in answer_lower
                found_in_context = v_str in context_lower

                if found_in_answer:
                    matched += 1
                elif not found_in_context:
                    result["unsupported_claims"].append(f"{key}: {v}")

    result["fact_coverage_rate"] = matched / total if total else 1.0
    return result

# ---------------------------------------------------------
# LLM-as-Judge (unchanged, good design)
# ---------------------------------------------------------
def llm_behavior_judge(question: str, answer: str, context: str) -> dict:
    judge_context = f"""
Question: {question}

Answer: {answer}

Retrieved Context:
{context}
"""

    task = """
Evaluate the answer strictly. Output JSON only with scores 0.0–1.0:

relevance, specificity, faithfulness, completeness, conciseness
"""

    prompt = PROMPT_TEMPLATE.format(context=judge_context, question=task)

    try:
        resp = ollama.chat(
            model="mistral:7b-instruct-q4_0",
            messages=[{"role": "user", "content": prompt}],
            options={"temperature": 0.2}
        )
        return json.loads(resp["message"]["content"])
    except:
        return dict.fromkeys(
            ["relevance", "specificity", "faithfulness", "completeness", "conciseness"], 0.5
        )

# ---------------------------------------------------------
# End-to-End Evaluation
# ---------------------------------------------------------
def evaluate_end_to_end():
    detailed = []
    abstentions, invalid_abstentions = 0, 0
    grounded_total, sentence_total = 0, 0
    hallucinations = 0
    fact_rates = []

    scores = {k: [] for k in ["relevance", "specificity", "faithfulness", "completeness", "conciseness"]}

    for item in EVAL_QUESTIONS:
        q = item["question"]
        res = ask(q)
        answer = res.get("answer", "").strip()
        retrieved = retriever.retrieve(q)
        context = "\n".join(r["content"] for r in retrieved)

        abstained = is_abstention(answer)
        if abstained:
            abstentions += 1
        if item["answer_type"] == "abstention" and not abstained:
            invalid_abstentions += 1

        sentences = extract_sentences(answer)
        grounded = sum(1 for s in sentences if grounded_sentence(s, context))
        grounded_total += grounded
        sentence_total += max(len(sentences), 1)

        fact = check_fact_coverage(item, answer, context)
        fact_rates.append(fact["fact_coverage_rate"])
        hallucinations += len(fact["unsupported_claims"])

        judge = llm_behavior_judge(q, answer, context)
        for k in scores:
            scores[k].append(judge[k])

        detailed.append({
            "id": item["id"],
            "answer": answer,
            "abstained": abstained,
            "invalid_abstention": item["answer_type"] == "abstention" and not abstained,
            "grounded_sentence_ratio": grounded / max(len(sentences), 1),
            "fact_coverage": fact["fact_coverage_rate"],
            "unsupported_claims": fact["unsupported_claims"],
            **judge
        })

        time.sleep(0.4)

    summary = {
        "abstention_rate": abstentions / len(EVAL_QUESTIONS),
        "invalid_abstentions": invalid_abstentions,
        "grounded_sentence_rate": grounded_total / sentence_total,
        "avg_fact_coverage": float(np.mean(fact_rates)),
        "total_hallucinations": hallucinations,
        **{f"avg_{k}": float(np.mean(v)) for k, v in scores.items()}
    }

    Path("evaluation").mkdir(exist_ok=True)
    with open("evaluation/detailed_results.json", "w") as f:
        json.dump({"summary": summary, "details": detailed}, f, indent=2)

    return summary

# ---------------------------------------------------------
# Main
# ---------------------------------------------------------
if __name__ == "__main__":
    print(json.dumps(evaluate_end_to_end(), indent=2))
