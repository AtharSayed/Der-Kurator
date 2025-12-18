import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Tuple

# -------------------------------------------------
# Resolve project paths safely
# -------------------------------------------------
PROJECT_ROOT = os.path.abspath(
    os.path.join(os.path.dirname(__file__), "..")
)

VECTOR_STORE_PATH = os.path.join(
    PROJECT_ROOT, "embeddings", "vector_store"
)

INDEX_FILE = os.path.join(VECTOR_STORE_PATH, "index.faiss")
DATA_FILE = os.path.join(VECTOR_STORE_PATH, "data.pkl")

# -------------------------------------------------
# Retriever Class
# -------------------------------------------------
class Retriever:
    """
    Handles semantic retrieval over the FAISS vector store.
    """

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        top_k: int = 5
    ):
        self.top_k = top_k

        # Load embedding model
        self.embedder = SentenceTransformer(embedding_model)

        # Load FAISS index
        if not os.path.exists(INDEX_FILE):
            raise FileNotFoundError(f"FAISS index not found at {INDEX_FILE}")

        self.index = faiss.read_index(INDEX_FILE)

        # Load stored chunks & metadata
        if not os.path.exists(DATA_FILE):
            raise FileNotFoundError(f"Vector data not found at {DATA_FILE}")

        with open(DATA_FILE, "rb") as f:
            self.chunks, self.metadata = pickle.load(f)

    # -------------------------------------------------
    # Core Retrieval Method
    # -------------------------------------------------
    def retrieve(self, query: str) -> List[Dict]:
        """
        Retrieve the most relevant chunks for a query.

        Returns:
            List of dicts with:
            - content
            - metadata
            - score
        """
        query_embedding = self.embedder.encode([query])

        distances, indices = self.index.search(query_embedding, self.top_k)

        results = []
        for score, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue

            results.append({
                "content": self.chunks[idx],
                "metadata": self.metadata[idx],
                "score": float(score)
            })

        return results

    # -------------------------------------------------
    # Context Builder (for LLM)
    # -------------------------------------------------
    def build_context(self, query: str) -> str:
        """
        Builds a clean context string from retrieved chunks.
        """
        retrieved_chunks = self.retrieve(query)

        context_blocks = []
        for item in retrieved_chunks:
            context_blocks.append(item["content"])

        return "\n\n".join(context_blocks)

    # -------------------------------------------------
    # Citation Helper (Future-Ready)
    # -------------------------------------------------
    def get_citations(self, query: str) -> List[Dict]:
        """
        Extract citation info from retrieved chunks.
        """
        retrieved_chunks = self.retrieve(query)

        citations = []
        for item in retrieved_chunks:
            meta = item["metadata"]

            citations.append({
                "source": meta.get("source", "unknown"),
                "page": meta.get("page"),
                "slide": meta.get("slide"),
                "score": item["score"]
            })

        return citations
