# rag/retriever.py
import os
import pickle
import faiss
import numpy as np
from sentence_transformers import SentenceTransformer
from typing import List, Dict, Optional

PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
VECTOR_STORE_PATH = os.path.join(PROJECT_ROOT, "embeddings", "vector_store")
INDEX_FILE = os.path.join(VECTOR_STORE_PATH, "index.faiss")
DATA_FILE = os.path.join(VECTOR_STORE_PATH, "data.pkl")

VARIANT_KEYWORDS = {
    "gt3": "GT3",
    "gt3 rs": "GT3",
    "carrera s": "Carrera S",
    "carrera": "Carrera",  # more general
    "turbo s": "Turbo S",
    "turbo": "Turbo",
    "gts": "GTS",
}

class Retriever:
    def __init__(
        self,
        embedding_model: str = "all-mpnet-base-v2",
        top_k: int = 8,
        min_similarity: float = 0.38,
        min_chunk_length: int = 50,
        variant_boost: float = 0.30,  # how much to boost matching variant
    ):
        self.top_k = top_k
        self.min_similarity = min_similarity
        self.min_chunk_length = min_chunk_length
        self.variant_boost = variant_boost

        self.embedder = SentenceTransformer(embedding_model)

        if not os.path.exists(INDEX_FILE):
            raise FileNotFoundError(f"FAISS index not found at {INDEX_FILE}")
        self.index = faiss.read_index(INDEX_FILE)

        if not os.path.exists(DATA_FILE):
            raise FileNotFoundError(f"Vector data not found at {DATA_FILE}")
        with open(DATA_FILE, "rb") as f:
            self.chunks, self.metadata = pickle.load(f)

        if self.index.d != self.embedder.get_sentence_embedding_dimension():
            raise ValueError("Embedding dimension mismatch")

    def _extract_query_variant(self, query: str) -> Optional[str]:
        q = query.lower()
        for k, v in VARIANT_KEYWORDS.items():
            if k in q:
                return v
        return None

    def retrieve(self, query: str) -> List[Dict]:
        query_emb = self.embedder.encode([query], normalize_embeddings=True)
        distances, indices = self.index.search(query_emb.astype('float32'), self.top_k * 3)

        query_variant = self._extract_query_variant(query)

        results = []
        seen = set()

        for raw_score, idx in zip(distances[0], indices[0]):
            if idx == -1:
                continue

            similarity = float(raw_score)
            if similarity < self.min_similarity:
                continue

            content = self.chunks[idx].strip()
            if len(content) < self.min_chunk_length:
                continue
            if content in seen:
                continue

            seen.add(content)

            meta = self.metadata[idx]
            score = similarity

            # Variant-aware boost (only if query contains a variant)
            if query_variant and meta.get("variant") == query_variant:
                score += self.variant_boost  # simple additive boost
                score = min(score, 1.0)

            results.append({
                "content": content,
                "metadata": meta,
                "score": score,
                "original_score": similarity  # for debugging
            })

        # Sort by boosted score
        results = sorted(results, key=lambda x: x["score"], reverse=True)[:self.top_k]

        return results

    def get_citations(self, retrieved_chunks: List[Dict]) -> List[Dict]:
        """Improved citations using real metadata fields"""
        citations = []
        for chunk in retrieved_chunks:
            meta = chunk["metadata"]
            source_name = os.path.basename(meta.get("source", "unknown"))

            citation = {
                "source": source_name,
                "element_type": meta.get("element_type", "Unknown"),
                "variant": meta.get("variant"),
                "page": meta.get("page"),
                "element_index": meta.get("element_index"),
                "score": round(chunk["original_score"], 3),  # show original semantic score
                "boosted_score": round(chunk["score"], 3) if chunk["score"] != chunk["original_score"] else None
            }
            citations.append(citation)
        return citations