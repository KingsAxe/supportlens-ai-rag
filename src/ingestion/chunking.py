"""Deterministic chunk preparation for retrieval."""

from __future__ import annotations

from typing import Any

Chunk = dict[str, Any]
Document = dict[str, Any]


def _split_text(text: str, max_chars: int = 700) -> list[str]:
    paragraphs = [part.strip() for part in text.split("\n\n") if part.strip()]
    if not paragraphs:
        return [text.strip()]

    chunks: list[str] = []
    current = ""
    for paragraph in paragraphs:
        candidate = paragraph if not current else f"{current}\n\n{paragraph}"
        if len(candidate) <= max_chars:
            current = candidate
            continue
        if current:
            chunks.append(current)
        if len(paragraph) <= max_chars:
            current = paragraph
            continue
        for start in range(0, len(paragraph), max_chars):
            chunks.append(paragraph[start : start + max_chars].strip())
        current = ""
    if current:
        chunks.append(current)
    return chunks


def chunk_document(document: Document, max_chars: int = 700) -> list[Chunk]:
    content = document["content"].strip()
    if document["source_type"] == "case":
        text_parts = [content]
    else:
        text_parts = _split_text(content, max_chars=max_chars)

    chunks: list[Chunk] = []
    for chunk_index, text in enumerate(text_parts):
        chunks.append(
            {
                "chunk_id": f"{document['document_id']}-chunk-{chunk_index}",
                "document_id": document["document_id"],
                "source_type": document["source_type"],
                "source_id": document["source_id"],
                "chunk_index": chunk_index,
                "text": text,
                "metadata": {
                    **document["metadata"],
                    "title": document["title"],
                    "category": document["category"],
                },
            }
        )
    return chunks


def chunk_documents(documents: list[Document], max_chars: int = 700) -> list[Chunk]:
    chunks: list[Chunk] = []
    for document in documents:
        chunks.extend(chunk_document(document, max_chars=max_chars))
    return chunks