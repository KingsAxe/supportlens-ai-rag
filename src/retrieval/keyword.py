"""Lightweight BM25-style keyword retrieval baseline."""

from __future__ import annotations

import math
import re
from collections import Counter, defaultdict
from typing import Any

Chunk = dict[str, Any]
Result = dict[str, Any]
_TOKEN_RE = re.compile(r"[a-z0-9_]+")


def tokenize(text: str) -> list[str]:
    return _TOKEN_RE.findall(text.lower())


class KeywordRetriever:
    """A small BM25 implementation over chunk text.

    Score formula:
    idf(term) * ((tf * (k1 + 1)) / (tf + k1 * (1 - b + b * dl / avgdl)))
    """

    def __init__(self, chunks: list[Chunk], k1: float = 1.5, b: float = 0.75) -> None:
        self.chunks = chunks
        self.k1 = k1
        self.b = b
        self.term_frequencies: list[Counter[str]] = []
        self.document_frequencies: dict[str, int] = defaultdict(int)
        self.doc_lengths: list[int] = []

        for chunk in chunks:
            tokens = tokenize(chunk["text"])
            frequencies = Counter(tokens)
            self.term_frequencies.append(frequencies)
            self.doc_lengths.append(len(tokens))
            for term in frequencies:
                self.document_frequencies[term] += 1

        self.avg_doc_length = sum(self.doc_lengths) / len(self.doc_lengths) if self.doc_lengths else 0.0

    def _idf(self, term: str) -> float:
        doc_freq = self.document_frequencies.get(term, 0)
        doc_count = len(self.chunks)
        if doc_freq == 0 or doc_count == 0:
            return 0.0
        return math.log(1.0 + (doc_count - doc_freq + 0.5) / (doc_freq + 0.5))

    def retrieve(self, query: str, top_k: int = 5) -> list[Result]:
        query_terms = tokenize(query)
        if not query_terms:
            return []

        results: list[Result] = []
        for index, chunk in enumerate(self.chunks):
            score = 0.0
            frequencies = self.term_frequencies[index]
            doc_length = self.doc_lengths[index] or 1
            for term in query_terms:
                term_frequency = frequencies.get(term, 0)
                if term_frequency == 0:
                    continue
                numerator = term_frequency * (self.k1 + 1.0)
                denominator = term_frequency + self.k1 * (
                    1.0 - self.b + self.b * doc_length / (self.avg_doc_length or 1.0)
                )
                score += self._idf(term) * (numerator / denominator)
            if score > 0:
                results.append(
                    {
                        "chunk_id": chunk["chunk_id"],
                        "document_id": chunk["document_id"],
                        "source_type": chunk["source_type"],
                        "source_id": chunk["source_id"],
                        "score": round(score, 6),
                        "text": chunk["text"],
                        "metadata": chunk["metadata"],
                    }
                )

        results.sort(key=lambda item: item["score"], reverse=True)
        return results[:top_k]


def retrieve_chunks(chunks: list[Chunk], query: str, top_k: int = 5) -> list[Result]:
    return KeywordRetriever(chunks).retrieve(query=query, top_k=top_k)