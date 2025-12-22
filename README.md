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

## 📁 Project Structure
```bash
atharsayed-der-kurator/
├── app.py                # Streamlit client application
├── ingest.py             # Ingestion & indexing pipeline
├── requirements.txt
│
├── data/
│   └── raw/              # Raw source documents (PDF, DOCX, TXT, PPTX)
│
├── preprocessing/
│   └── cleaner.py        # Text cleaning & normalization
│
├── rag/
│   ├── prompt.py         # Strict grounding prompt
│   ├── retriever.py      # FAISS retrieval + filtering
│   └── qa.py             # Answer gating & orchestration
│
├── evaluation/
│   ├── dataset.py        # Evaluation dataset
│   ├── evaluate.py       # RAG evaluation pipeline
│   └── results.json      # Stored evaluation results
│
└── tests/
    └── test_retrieval.py # Retrieval correctness tests
```

## 📄 Supported Document Formats

The ingestion pipeline automatically detects and processes:

- **PDF**
- **DOCX**
- **PPTX**
- **TXT**

This is handled using **Unstructured’s automatic document partitioning**, so **no format-specific loaders are required**.

Simply add new files to `data/raw/` and re-run ingestion.

---

## ✂️ Chunking Strategy

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

## 📊 RAG Evaluation

Offline evaluation is performed using:

- Hit Rate
- Mean Reciprocal Rank (MRR)
- Context Relevance
- Faithfulness
- Answer Relevance

### Latest Evaluation Results

```json
{
  "summary": {
    "abstention_rate": 0.5,
    "grounded_sentence_rate": 1.0,
    "avg_relevance": 0.75,
    "avg_specificity": 0.85,
    "avg_faithfulness": 1.0
  }
```

