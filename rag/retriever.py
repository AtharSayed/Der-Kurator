import os
import pickle
import faiss
from sentence_transformers import SentenceTransformer
from typing import List, Dict

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
    Responsible ONLY for retrieval quality, not generation.
    """

    def __init__(
        self,
        embedding_model: str = "sentence-transformers/all-MiniLM-L6-v2",
        top_k: int = 5,
        min_chunk_length: int = 100
    ):
        self.top_k = top_k
        self.min_chunk_length = min_chunk_length

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
        Retrieve the most relevant, content-worthy chunks for a query.

        Returns:
            List of dicts with:
            - content
            - metadata
            - score (FAISS distance)
        """
        query_embedding = self.embedder.encode([query])
        distances, indices = self.index.search(query_embedding, self.top_k)

        results = []
        seen_chunks = set()

        for score, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue

            content = self.chunks[idx].strip()

            # 🚫 Filter weak / meaningless chunks
            if len(content) < self.min_chunk_length:
                continue

            # 🚫 De-duplicate identical content
            if content in seen_chunks:
                continue
            seen_chunks.add(content)

            results.append({
                "content": content,
                "metadata": self.metadata[idx],
                "score": float(score)
            })

        return results

    # -------------------------------------------------
    # Context Builder (for LLM)
    # -------------------------------------------------
    def build_context(self, query: str) -> str:
        """
        Builds a clean, ordered context string from retrieved chunks.
        """
        retrieved_chunks = self.retrieve(query)

        if not retrieved_chunks:
            return ""

        return "\n\n".join(item["content"] for item in retrieved_chunks)

    # -------------------------------------------------
    # Citation Helper
    # -------------------------------------------------
    def get_citations(self, query: str) -> List[Dict]:
        """
        Extract citation information from retrieved chunks.
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
