import os
import pickle
import faiss
import pytest
from sentence_transformers import SentenceTransformer

# -------------------------------------------------
# Resolve project root dynamically
# -------------------------------------------------
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

VECTOR_STORE_PATH = os.path.join(
    PROJECT_ROOT, "embeddings", "vector_store"
)

INDEX_FILE = os.path.join(VECTOR_STORE_PATH, "index.faiss")
DATA_FILE = os.path.join(VECTOR_STORE_PATH, "data.pkl")

EMBEDDING_MODEL = "sentence-transformers/all-MiniLM-L6-v2"

# -------------------------------------------------
# Fixtures
# -------------------------------------------------
@pytest.fixture(scope="session")
def embedding_model():
    return SentenceTransformer(EMBEDDING_MODEL)

@pytest.fixture(scope="session")
def vector_index():
    assert os.path.exists(INDEX_FILE), f"FAISS index file not found at {INDEX_FILE}"
    return faiss.read_index(INDEX_FILE)

@pytest.fixture(scope="session")
def vector_data():
    assert os.path.exists(DATA_FILE), f"Vector data file not found at {DATA_FILE}"
    with open(DATA_FILE, "rb") as f:
        chunks, metadata = pickle.load(f)
    return chunks, metadata

# -------------------------------------------------
# Tests
# -------------------------------------------------
def test_retrieval_returns_results(embedding_model, vector_index, vector_data):
    chunks, metadata = vector_data

    query = "What engine is used in the Porsche 911 GT3?"
    query_embedding = embedding_model.encode([query])

    distances, indices = vector_index.search(query_embedding, k=5)

    assert len(indices[0]) > 0
    assert indices[0][0] != -1


def test_retrieval_is_domain_relevant(embedding_model, vector_index, vector_data):
    chunks, metadata = vector_data

    query = "Explain Porsche 911 GT3 performance"
    query_embedding = embedding_model.encode([query])

    _, indices = vector_index.search(query_embedding, k=3)

    retrieved_text = " ".join(
        chunks[i].lower() for i in indices[0] if i != -1
    )

    assert "911" in retrieved_text or "porsche" in retrieved_text


def test_out_of_domain_query_retrieval(embedding_model, vector_index):
    query = "Who founded Ferrari?"
    query_embedding = embedding_model.encode([query])

    distances, indices = vector_index.search(query_embedding, k=3)

    assert distances is not None
    assert indices is not None
