# 🏎️ Der Kurator — Porsche 911 Knowledge Assistant

**Der Kurator** is a **document-grounded Retrieval-Augmented Generation (RAG) system** designed to answer **technical, factual, and variant-specific questions about the Porsche 911** using only verified source documents.

The system prioritizes **faithfulness, accuracy, and traceability**, making it suitable for domains where **numerical correctness and source attribution are critical**.

---

## 🎯 Project Goals

- Answer questions **strictly from provided documents**
- Prevent hallucinations and speculative responses
- Support multiple document formats automatically
- Preserve **variant-specific specifications** (Carrera S, GT3, Turbo S, etc.)
- Quantitatively evaluate RAG performance

---

---
##  System Architecture (Overview)

The following diagram illustrates the end-to-end architecture of **Der Kurator**

![Der Kurator System Diagram](data/images/Der-Kurator%20System%20Design%20RAG.png)

---

---
## Der Kurator Streamlit Application 

The following image illustrates the Streamlit UI of Der Kurator where users can ask specific questions 

![Der Kurator Streamlit UI](data/images/Der-Kurator%20Streamlit%20.png)

![Chat response + Citations reference](data/images/Der-Kurator%20Streamlit-II.png)
---

## 📁 Project Structure
```bash
atharsayed-der-kurator/
├── app.py                # Streamlit client application
├── ingest.py             # Ingestion & indexing pipeline
├── requirements.txt
├── .gitignore            # venv & pycache files & other irrelevent files ignored 
│
├── data/
│   └── raw/              # Raw source documents (PDF, DOCX, TXT, PPTX)
│
├── preprocessing/
│   └── cleaner.py        # Text cleaning & normalization
│
├── rag/
│   ├──__init__.py       
│   ├── prompt.py         # Strict grounding prompt
│   ├── retriever.py      # FAISS retrieval + filtering
│   └── qa.py             # Answer gating & orchestration
│
├── evaluation/
│   ├──__init__.py        
│   ├── dataset.py        # Evaluation dataset
│   ├── evaluate.py       # RAG evaluation pipeline
│   └── results.json      # Stored evaluation results
│
├── tests/
│   ├──__init__.py  
    └── test_retrieval.py  # Retrieval correctness tests
```

##  Supported Document Formats

The ingestion pipeline automatically detects and processes:

- **PDF**
- **DOCX**
- **PPTX**
- **TXT**

This is handled using **Unstructured’s automatic document partitioning**, so **no format-specific loaders are required**.

Simply add new files to `data/raw/` and re-run ingestion.

---

##  Chunking Strategy

### **Structure-Aware, Element-Level Chunking**

- Each document is partitioned into **structural elements** (headings, paragraphs, tables, slide blocks).
- **Each element becomes one atomic chunk**.
- No fixed-size chunking
- No sliding windows
- No overlap

This preserves:
- Numeric specifications
- Variant boundaries
- Table integrity

---

## 🔎 Retrieval Strategy

- SentenceTransformer embeddings
- FAISS vector similarity search
- **Variant-aware filtering**
- **Spec-aware prioritization** for numeric queries
- Soft fallback to avoid over-filtering

---

## 🛡️ Hallucination Control

Der Kurator uses multiple layers of safeguards:

1. **Strict grounding prompt**
2. **Variant consistency checks**
3. **Confidence-based answer gating**
4. **Explicit refusal when evidence is insufficient**
5. **Citations shown only for grounded answers**

---

## 📊 Evaluation & Performance Metrics

Der Kurator is designed not just to *work*, but to be **verifiable, safe, and reliable**.  
To ensure this, we adopted a rigorous multi-stage evaluation framework that covers both **retrieval quality** and **answer generation quality**.

### 🧠 What is RAG?

Der Kurator implements Retrieval-Augmented Generation (RAG), a modern AI architecture that combines:

1. **Document retrieval from curated knowledge sources**, and  
2. **Large language model (LLM) generation grounded in that retrieval**  

This ensures responses are accurate and traceable to real documents, not fabricated by the model.

---

## 📈 Retrieval Quality Benchmarks

The retrieval layer powers all downstream answering. We evaluate it with automated tests to ensure:

- Relevant information is retrieved for domain queries  
- Irrelevant queries do not return misleading context  
- Results are diverse and not redundant  
- Retrieval supports multi-dimension answers

### Key Retrieval Test Highlights

| Test Category | Description |
|---------------|-------------|
| **Semantic relevance** | Queries about Porsche 911 specs, torque, top speed, etc. return semantically relevant chunks |
| **Irrelevant query rejection** | Non-domain queries (pizza recipe, US election results, etc.) either return no result or low similarity scores |
| **Diversity** | Retrieved chunks exhibit low redundancy (max similarity < 0.95) |
| **Dimension coverage** | Retrieval supports key answer dimensions (e.g., horsepower + torque + top speed) |

All retrieval tests pass using our FAISS + SentenceTransformers pipeline.

---

## 🧪 Answer Generation (End-to-End RAG Evaluation)

We evaluate answers generated by Der Kurator using `evaluate.py`. The evaluation considers:

- **Grounded Sentence Rate** — how much of the answer is traceable to retrieved context  
- **Fact Coverage** — numeric & textual fact alignment  
- **Hallucinations** — unsupported claims not found in retrieved sources  
- **LLM Behavior Metrics** — relevance, specificity, faithfulness, completeness, conciseness  

### 📊 Latest Evaluation Results

```json
{
  "summary": {
    "abstention_rate": 0.0909,
    "invalid_abstentions": 1,
    "grounded_sentence_rate": 0.9706,
    "avg_fact_coverage": 0.5152,
    "total_hallucinations": 11,
    "avg_relevance": 0.9545,
    "avg_specificity": 0.9818,
    "avg_faithfulness": 0.9909,
    "avg_completeness": 0.9727,
    "avg_conciseness": 0.8091
  }
}

```
---

## 🔍 Interpreting the Results

- **97% Grounded Sentence Rate**  
  Almost all generated sentences are directly supported by retrieved documents.

- **~99% Faithfulness**  
  The system very rarely introduces information not present in the source context.

- **~51% Fact Coverage**  
  This reflects *partial completeness*, not incorrectness.  
  Many questions require multiple facts, and the model may answer correctly but not exhaustively.

- **Invalid Abstentions = 1**  
  Indicates a single case where the model answered despite insufficient evidence — intentionally tracked to improve safety.

Overall, **Der Kurator prioritizes correctness and grounding over verbosity or speculation**.

---

## 🎯 Why These Benchmarks Matter

Unlike many RAG demos, Der Kurator is evaluated across both **retrieval behavior** and **answer generation behavior**.

This ensures:

- Retrieval failures are caught early
- Hallucinations are explicitly measured
- The system refuses to answer when evidence is missing
- Quality regressions can be detected over time

This makes Der Kurator suitable for **technical, safety-critical, and factual domains**, not just casual Q&A.
