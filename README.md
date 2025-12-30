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

## 📊 RAG Evaluation

Offline evaluation is performed using:

- Abstention Rate 
- Grounded Sentence Rate 
- Average Fact Coverage 
- Total hallucinations
- Average relevance
- Average Specificity
- Average Faithfullness
- Average Completeness
- Average Conciseness 

### Latest Evaluation Results

```json
{
  "summary": {
    "abstention_rate": 0.09090909090909091,
    "invalid_abstentions": 1,
    "grounded_sentence_rate": 0.9705882352941176,
    "avg_fact_coverage": 0.5151515151515151,
    "total_hallucinations": 11,
    "avg_relevance": 0.9545454545454546,
    "avg_specificity": 0.9818181818181819,
    "avg_faithfulness": 0.990909090909091,
    "avg_completeness": 0.9727272727272727,
    "avg_conciseness": 0.8090909090909091
  }
```

