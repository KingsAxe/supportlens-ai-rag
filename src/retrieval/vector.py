"""Local vector retrieval with sentence-transformers or a sklearn fallback."""

from __future__ import annotations

import pickle
from pathlib import Path
from typing import Any

import numpy as np
from sklearn.decomposition import TruncatedSVD
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.preprocessing import normalize

from src.ingestion.io import ensure_parent_dir, resolve_repo_path

Chunk = dict[str, Any]
Result = dict[str, Any]
DEFAULT_MODEL_NAME = "sentence-transformers/all-MiniLM-L6-v2"
CATEGORY_HINTS = {
    "billing_dispute": "duplicate charge tax issue invoice mismatch bank dispute chargeback incorrect billing payment problem",
    "refund_request": "refund reversal money back mistaken purchase grace period",
    "subscription_change": "cancel renewal downgrade upgrade billing cycle end date",
    "account_access": "sign in login verification code lockout reset backup access",
    "account_security": "account takeover suspicious access ownership recovery compromised account",
    "payment_failure": "declined card failed payment retry billing details issuer",
    "technical_issue": "bug incident outage malfunction crash missing data export problem",
    "escalation_risk": "urgent high impact executive risk specialist escalation",
}


def _safe_name(value: str) -> str:
    return value.replace("/", "_").replace("-", "_").replace(":", "_")


def _combine_chunk_text(chunk: Chunk) -> str:
    metadata = chunk["metadata"]
    title = metadata.get("title", "")
    category = metadata.get("category", "")
    intent = metadata.get("intent", "")
    product_area = metadata.get("product_area", "")
    hints = CATEGORY_HINTS.get(category, "")
    return f"{title}\n{category}\n{intent}\n{product_area}\n{hints}\n{chunk['text']}".strip()


class VectorRetriever:
    def __init__(
        self,
        chunks: list[Chunk],
        model_name: str = DEFAULT_MODEL_NAME,
        cache_dir: str | Path | None = None,
    ) -> None:
        self.chunks = chunks
        self.model_name = model_name
        self.cache_dir = Path(cache_dir) if cache_dir else resolve_repo_path("data", "processed")
        self.chunk_ids = [chunk["chunk_id"] for chunk in chunks]
        self.texts = [_combine_chunk_text(chunk) for chunk in chunks]
        self.backend = "sentence_transformers"
        self.embeddings: np.ndarray | None = None
        self.vectorizer: TfidfVectorizer | None = None
        self.svd: TruncatedSVD | None = None
        self._sentence_model = None
        self._load_or_build_index()

    @property
    def cache_path(self) -> Path:
        return self.cache_dir / f"vector_index_{_safe_name(self.model_name)}.pkl"

    def _load_or_build_index(self) -> None:
        if self.cache_path.exists():
            with self.cache_path.open("rb") as handle:
                payload = pickle.load(handle)
            if payload.get("chunk_ids") == self.chunk_ids and payload.get("model_name") == self.model_name:
                self.backend = payload["backend"]
                self.embeddings = payload["embeddings"]
                self.vectorizer = payload.get("vectorizer")
                self.svd = payload.get("svd")
                return
        self._build_index()

    def _build_index(self) -> None:
        try:
            from sentence_transformers import SentenceTransformer

            model = SentenceTransformer(self.model_name)
            embeddings = model.encode(self.texts, normalize_embeddings=True, show_progress_bar=False)
            self.backend = "sentence_transformers"
            self.embeddings = np.asarray(embeddings, dtype=np.float32)
            self._sentence_model = model
            payload = {
                "backend": self.backend,
                "model_name": self.model_name,
                "chunk_ids": self.chunk_ids,
                "embeddings": self.embeddings,
            }
        except Exception:
            self.backend = "sklearn_tfidf_svd"
            self.vectorizer = TfidfVectorizer(stop_words="english", ngram_range=(1, 2))
            tfidf_matrix = self.vectorizer.fit_transform(self.texts)
            max_components = min(64, tfidf_matrix.shape[0] - 1, tfidf_matrix.shape[1] - 1)
            if max_components >= 2:
                self.svd = TruncatedSVD(n_components=max_components, random_state=42)
                dense = self.svd.fit_transform(tfidf_matrix)
            else:
                dense = tfidf_matrix.toarray()
            self.embeddings = normalize(np.asarray(dense, dtype=np.float32))
            payload = {
                "backend": self.backend,
                "model_name": self.model_name,
                "chunk_ids": self.chunk_ids,
                "embeddings": self.embeddings,
                "vectorizer": self.vectorizer,
                "svd": self.svd,
            }
        ensure_parent_dir(self.cache_path)
        with self.cache_path.open("wb") as handle:
            pickle.dump(payload, handle)

    def _encode_query(self, query: str) -> np.ndarray:
        if self.backend == "sentence_transformers":
            if self._sentence_model is None:
                from sentence_transformers import SentenceTransformer

                self._sentence_model = SentenceTransformer(self.model_name)
            encoded = self._sentence_model.encode([query], normalize_embeddings=True, show_progress_bar=False)
            return np.asarray(encoded[0], dtype=np.float32)

        if self.vectorizer is None:
            raise RuntimeError("Vectorizer not initialized for sklearn fallback backend")
        query_matrix = self.vectorizer.transform([query])
        if self.svd is not None:
            dense = self.svd.transform(query_matrix)
        else:
            dense = query_matrix.toarray()
        return normalize(np.asarray(dense, dtype=np.float32))[0]

    def retrieve(self, query: str, top_k: int = 5) -> list[Result]:
        if self.embeddings is None:
            return []
        query_vector = self._encode_query(query)
        scores = np.matmul(self.embeddings, query_vector)
        ranked_indices = np.argsort(scores)[::-1][:top_k]
        results: list[Result] = []
        for index in ranked_indices:
            chunk = self.chunks[int(index)]
            score = float(scores[int(index)])
            results.append(
                {
                    "chunk_id": chunk["chunk_id"],
                    "document_id": chunk["document_id"],
                    "source_type": chunk["source_type"],
                    "source_id": chunk["source_id"],
                    "score": round(score, 6),
                    "text": chunk["text"],
                    "metadata": {
                        **chunk["metadata"],
                        "vector_backend": self.backend,
                        "vector_model_name": self.model_name,
                    },
                }
            )
        return results


def retrieve_chunks(
    chunks: list[Chunk],
    query: str,
    top_k: int = 5,
    model_name: str = DEFAULT_MODEL_NAME,
) -> list[Result]:
    return VectorRetriever(chunks=chunks, model_name=model_name).retrieve(query=query, top_k=top_k)