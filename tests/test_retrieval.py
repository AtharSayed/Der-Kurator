# tests/test_retrieval.py
# Production-aligned retrieval tests (realistic, stable, RAG-correct)

import os
import faiss
import numpy as np
import pytest
import pickle
import time
from collections import Counter
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
from rag.retriever import Retriever

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VECTOR_STORE_PATH = os.path.join(PROJECT_ROOT, "embeddings", "vector_store")
INDEX_FILE = os.path.join(VECTOR_STORE_PATH, "index.faiss")
DATA_FILE = os.path.join(VECTOR_STORE_PATH, "data.pkl")
EMBEDDING_MODEL_NAME = "all-mpnet-base-v2"


# ---------------------------------------------------------
# Fixtures
# ---------------------------------------------------------
@pytest.fixture(scope="session")
def vector_index():
    index = faiss.read_index(INDEX_FILE)
    assert index.ntotal > 0
    return index


@pytest.fixture(scope="session")
def vector_data():
    with open(DATA_FILE, "rb") as f:
        chunks, metadata = pickle.load(f)
    return chunks, metadata


@pytest.fixture(scope="session")
def retriever():
    return Retriever(
        embedding_model=EMBEDDING_MODEL_NAME,
        top_k=8,
        min_similarity=0.45,
        min_chunk_length=5
    )


# ---------------------------------------------------------
# Helpers
# ---------------------------------------------------------
def semantic_match_ratio(text: str, keywords: list[str]) -> float:
    text = text.lower()
    return sum(1 for kw in keywords if kw in text) / len(keywords)


def is_structural_chunk(text: str) -> bool:
    return len(text.strip()) < 15


# ---------------------------------------------------------
# Structural integrity
# ---------------------------------------------------------
def test_index_and_data_consistency(vector_index, vector_data):
    chunks, _ = vector_data
    assert vector_index.ntotal == len(chunks)


def test_metadata_minimum_fields(vector_data):
    _, metadata = vector_data
    required = {"source", "chunk_char_count"}
    for meta in metadata:
        assert required.issubset(meta.keys())


def test_no_empty_chunks(vector_data):
    chunks, _ = vector_data
    assert all(len(c.strip()) > 0 for c in chunks)


def test_retrieved_chunks_not_redundant(retriever):
    query = "Porsche 911 Turbo S engine performance specifications"
    results = retriever.retrieve(query)

    contents = [r["content"].strip() for r in results]
    counts = Counter(contents)

    duplicate_ratio = (
        sum(c - 1 for c in counts.values() if c > 1) / len(contents)
        if contents else 0
    )

    # Retrieved context should not be highly redundant
    assert duplicate_ratio < 0.3



# ---------------------------------------------------------
# Relevance tests (robust)
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "query, expected_keywords",
    [
        ("Porsche 911 engine torque horsepower",
         ["torque", "hp", "horsepower", "ps", "kw"]),
        ("Porsche 911 GT3 RS aerodynamics wing downforce",
         ["gt3", "rs", "wing", "downforce"]),
        ("Porsche 911 Turbo S acceleration top speed",
         ["turbo", "acceleration", "top speed"]),
        ("Porsche 911 history evolution generations",
         ["generation", "992", "991", "997"]),
    ]
)
def test_relevant_queries(retriever, query, expected_keywords):
    results = retriever.retrieve(query)
    assert results

    scores = np.array([r["score"] for r in results])
    combined = " ".join(r["content"].lower() for r in results)

    # Top result must be strong
    assert scores.max() > np.mean(scores)

    # Semantic support must exist
    assert semantic_match_ratio(combined, expected_keywords) >= 0.4


# ---------------------------------------------------------
# Irrelevant query safety
# ---------------------------------------------------------
@pytest.mark.parametrize(
    "query",
    [
        "Recipe for Italian pizza",
        "2024 US election results",
        "Quantum computing basics",
        "Stock market analysis Apple",
    ]
)
def test_irrelevant_queries_safe(retriever, query):
    results = retriever.retrieve(query)
    assert not results or max(r["score"] for r in results) < 0.5


# ---------------------------------------------------------
# Diversity
# ---------------------------------------------------------
def test_retrieval_diversity(retriever):
    query = "Porsche 911 Turbo S engine performance interior"
    results = retriever.retrieve(query)

    assert len(results) >= 4

    embeddings = retriever.embedder.encode(
        [r["content"] for r in results],
        normalize_embeddings=True
    )

    sim_matrix = cosine_similarity(embeddings)
    np.fill_diagonal(sim_matrix, 0)

    assert sim_matrix.max() < 0.95


# ---------------------------------------------------------
# Answer support (core RAG test)
# ---------------------------------------------------------
def test_retrieval_supports_answer_dimensions(retriever):
    query = "Porsche 911 Turbo S horsepower torque top speed"
    results = retriever.retrieve(query)

    combined = " ".join(r["content"].lower() for r in results)

    dimensions = ["horsepower", "hp", "torque", "top speed"]
    covered = sum(1 for d in dimensions if d in combined)

    assert covered >= 2


# ---------------------------------------------------------
# Edge & performance
# ---------------------------------------------------------
def test_empty_query(retriever):
    assert not retriever.retrieve("")


@pytest.mark.slow
def test_retrieval_latency(retriever):
    start = time.time()
    retriever.retrieve("Porsche 911 GT3 RS specs")
    assert time.time() - start < 0.6
