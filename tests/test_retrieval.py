# tests/test_retrieval.py
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


@pytest.fixture(scope="session")
def embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL_NAME)


@pytest.fixture(scope="session")
def vector_index():
    assert os.path.exists(INDEX_FILE)
    index = faiss.read_index(INDEX_FILE)
    assert isinstance(index, faiss.IndexFlatIP)
    assert index.ntotal > 0
    return index


@pytest.fixture(scope="session")
def vector_data():
    assert os.path.exists(DATA_FILE)
    with open(DATA_FILE, "rb") as f:
        chunks, metadata = pickle.load(f)
    assert len(chunks) > 0
    assert len(chunks) == len(metadata)
    return chunks, metadata


@pytest.fixture(scope="session")
def retriever():
    return Retriever(
        embedding_model=EMBEDDING_MODEL_NAME,
        top_k=8,
        min_similarity=0.45,
        min_chunk_length=10
    )


def test_index_and_data_consistency(vector_index, vector_data):
    chunks, _ = vector_data
    assert vector_index.ntotal == len(chunks)


@pytest.mark.parametrize(
    "query, expected_keywords, min_best_score, min_avg_score",
    [
        ("Porsche 911 engine torque horsepower", ["torque", "hp", "horsepower", "ps", "kw"], 0.60, 0.52),
        ("Porsche 911 GT3 RS aerodynamics wing downforce", ["gt3", "rs", "wing", "aerodynamics", "downforce"], 0.58, 0.50),
        ("Porsche 911 Turbo S acceleration 0-60 top speed", ["turbo", "acceleration", "0-60", "0-100", "top speed"], 0.57, 0.49),
        ("Porsche 911 history evolution models generations", ["generation", "992", "991", "997", "history"], 0.55, 0.47),
    ]
)
def test_relevant_queries(retriever, query, expected_keywords, min_best_score, min_avg_score):
    results = retriever.retrieve(query)
    assert results
    scores = [r["score"] for r in results]
    assert max(scores) >= min_best_score
    assert np.mean(scores) >= min_avg_score
    combined = " ".join(r["content"].lower() for r in results)
    matched = sum(1 for kw in expected_keywords if kw in combined)
    assert matched >= len(expected_keywords) // 2 + 1


@pytest.mark.parametrize(
    "query, max_allowed_score",
    [
        ("Recipe for Italian pizza", 0.45),
        ("2024 US election results", 0.48),
        ("Quantum computing basics", 0.42),
        ("Stock market analysis Apple", 0.46),
    ]
)
def test_irrelevant_queries(retriever, query, max_allowed_score):
    results = retriever.retrieve(query)
    if results:
        assert results[0]["score"] < max_allowed_score


def test_retrieval_diversity(retriever):
    query = "Porsche 911 Turbo S engine performance price interior"
    results = retriever.retrieve(query)
    assert len(results) >= 4
    embs = retriever.embedder.encode([r["content"] for r in results], normalize_embeddings=True)
    sim_matrix = cosine_similarity(embs)
    np.fill_diagonal(sim_matrix, 0)
    assert sim_matrix.max() < 0.93


def test_metadata_completeness(vector_data):
    _, metadata = vector_data
    required = {"source", "type", "unit", "index", "chunk_index", "chunk_char_count"}
    for meta in metadata:
        assert required.issubset(meta.keys())


def test_no_empty_chunks(vector_data):
    chunks, _ = vector_data
    assert all(len(c.strip()) >= 10 for c in chunks)


def test_duplicate_chunks_minimal(vector_data):
    chunks, _ = vector_data
    counts = Counter(chunks)
    duplicate_ratio = sum(count - 1 for count in counts.values() if count > 1) / len(chunks) if chunks else 0
    assert duplicate_ratio < 0.12


def test_search_empty_query(retriever):
    assert not retriever.retrieve("")


@pytest.mark.slow
def test_retrieval_performance(retriever):
    start = time.time()
    retriever.retrieve("Porsche 911 GT3 RS specs")
    duration = time.time() - start
    assert duration < 0.5