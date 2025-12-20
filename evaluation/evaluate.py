# evaluation/evaluate.py

import sys
from pathlib import Path

ROOT_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT_DIR))

import json
import time
import re
import ollama

from rag.qa import ask
from rag.retriever import Retriever
from evaluation.dataset import EVAL_QUESTIONS

retriever = Retriever(top_k=8, min_similarity=0.45, min_chunk_length=60)

def llm_judge(prompt: str) -> float:
    """Use Ollama (Mistral or Llama3) as judge — returns score 0.0 to 1.0"""
    try:
        response = ollama.chat(
            model="mistral:7b-instruct-q4_0",  # or llama3:8b
            messages=[{"role": "user", "content": prompt}]
        )
        text = response["message"]["content"].strip()
        # Extract score if model outputs number
        import re
        match = re.search(r"(\d+\.?\d*)", text)
        if match:
            return min(1.0, max(0.0, float(match.group(1)) / 10.0))  # assume 0-10 scale
        return 0.5  # fallback
    except:
        return 0.5

def evaluate_retrieval():
    print("Running Retrieval Evaluation...\n")
    hits = 0
    mrr = 0.0
    for item in EVAL_QUESTIONS:
        question = item["question"]
        keywords = item["expected_keywords"]
        results = retriever.retrieve(question)
        
        relevant = False
        first_rank = None
        for rank, r in enumerate(results, 1):
            content_lower = r["content"].lower()
            if any(kw.lower() in content_lower for kw in keywords):
                relevant = True
                if first_rank is None:
                    first_rank = rank
                break
        
        if relevant:
            hits += 1
            mrr += 1.0 / first_rank
    
    hit_rate = hits / len(EVAL_QUESTIONS)
    mrr_score = mrr / len(EVAL_QUESTIONS)
    
    print(f"Retrieval Hit Rate: {hit_rate:.3f}")
    print(f"Retrieval MRR:       {mrr_score:.3f}\n")
    return {"hit_rate": hit_rate, "mrr": mrr_score}

def evaluate_end_to_end():
    print("Running End-to-End RAG Evaluation (LLM-as-Judge)...\n")
    scores = {"context_relevance": [], "faithfulness": [], "answer_relevance": []}
    
    for item in EVAL_QUESTIONS:
        question = item["question"]
        result = ask(question)
        answer = result["answer"]
        context = retriever.build_context(question)
        
        # 1. Context Relevance
        cr_prompt = f"""
        Rate how relevant the retrieved context is to the question on a scale of 1-10.
        Question: {question}
        Context: {context[:3000]}
        Score only:"""
        scores["context_relevance"].append(llm_judge(cr_prompt))
        
        # 2. Faithfulness (does answer stick to context?)
        faith_prompt = f"""
        Rate how faithfully the answer uses ONLY information from the context (no hallucination) on a scale of 1-10.
        Context: {context[:3000]}
        Answer: {answer}
        Score only:"""
        scores["faithfulness"].append(llm_judge(faith_prompt))
        
        # 3. Answer Relevance
        rel_prompt = f"""
        Rate how well the answer directly and completely answers the question on a scale of 1-10.
        Question: {question}
        Answer: {answer}
        Score only:"""
        scores["answer_relevance"].append(llm_judge(rel_prompt))
        
        time.sleep(0.5)  # Be nice to Ollama
    
    avg_scores = {k: sum(v)/len(v) for k, v in scores.items()}
    for k, v in avg_scores.items():
        print(f"{k.replace('_', ' ').title()}: {v:.3f}")
    
    return avg_scores

if __name__ == "__main__":
    retrieval_metrics = evaluate_retrieval()
    e2e_metrics = evaluate_end_to_end()
    
    all_metrics = {"retrieval": retrieval_metrics, "end_to_end": e2e_metrics}
    print("\n=== Final RAG Evaluation Scores ===")
    print(json.dumps(all_metrics, indent=2))
    
    # Save for tracking improvement over time
    with open("evaluation/results.json", "w") as f:
        json.dump(all_metrics, f, indent=2)
    print("\nResults saved to evaluation/results.json")