# rag/retriever.py
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VECTOR_STORE_PATH = os.path.join(PROJECT_ROOT, "embeddings", "vector_store")
INDEX_FILE = os.path.join(VECTOR_STORE_PATH, "index.faiss")
DATA_FILE = os.path.join(VECTOR_STORE_PATH, "data.pkl")

class Retriever:
    def __init__(
        self,
        embedding_model: str = "all-mpnet-base-v2",
        top_k: int = 8,
        min_similarity: float = 0.45,
        min_chunk_length: int = 50
    ):
        self.top_k = top_k
        self.min_similarity = min_similarity
        self.min_chunk_length = min_chunk_length

        self.embedder = SentenceTransformer(embedding_model)

        if not os.path.exists(INDEX_FILE):
            raise FileNotFoundError(f"FAISS index not found at {INDEX_FILE}")
        self.index = faiss.read_index(INDEX_FILE)

        if not os.path.exists(DATA_FILE):
            raise FileNotFoundError(f"Vector data not found at {DATA_FILE}")
        with open(DATA_FILE, "rb") as f:
            self.chunks, self.metadata = pickle.load(f)

        # Robustness: check dimension match
        if self.index.d != self.embedder.get_sentence_embedding_dimension():
            raise ValueError("Embedding dimension mismatch between model and index")

    def retrieve(self, query: str) -> List[Dict]:
        query_emb = self.embedder.encode([query], normalize_embeddings=True)
        distances, indices = self.index.search(query_emb.astype('float32'), self.top_k * 2)

        results = []
        seen_contents = set()

        for score, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue

            similarity = float(score)
            if similarity < self.min_similarity:
                continue

            content = self.chunks[idx].strip()
            if len(content) < self.min_chunk_length:
                continue
            if content in seen_contents:
                continue

            seen_contents.add(content)

            meta = self.metadata[idx]
            results.append({
                "content": content,
                "metadata": meta,
                "score": similarity
            })

        results = sorted(results, key=lambda x: x["score"], reverse=True)[:self.top_k]

        return results

    def build_context(self, query: str) -> str:
        chunks = self.retrieve(query)
        if not chunks:
            return ""
        return "\n\n".join(chunk["content"] for chunk in chunks)

    def get_citations(self, query: str) -> List[Dict]:
        chunks = self.retrieve(query)
        citations = []
        for chunk in chunks:
            meta = chunk["metadata"]
            source_name = os.path.basename(meta.get("source", "unknown"))

            citation = {
                "source": source_name,
                "page": meta.get("index") if meta.get("unit") in ["page", "paragraph"] else None,
                "slide": meta.get("index") if meta.get("unit") == "slide" else None,
                "chunk_index": meta.get("chunk_index"),
                "score": round(chunk["score"], 3)
            }
            citations.append(citation)
        return citations