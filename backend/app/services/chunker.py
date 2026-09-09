from __future__ import annotations

from dataclasses import dataclass

from app.services.document_parser import ParsedSegment

TARGET_WORDS = 650
OVERLAP_WORDS = 75


@dataclass(frozen=True)
class ChunkDraft:
    chunk_index: int
    text: str
    page_number: int | None
    section: str | None


def chunk_segments(segments: list[ParsedSegment]) -> list[ChunkDraft]:
    chunks: list[ChunkDraft] = []
    words: list[str] = []
    page_number: int | None = None
    section: str | None = None

    def emit() -> None:
        nonlocal words, page_number, section
        if not words:
            return
        chunks.append(ChunkDraft(len(chunks), " ".join(words), page_number, section))
        words = words[-OVERLAP_WORDS:]
        page_number = None
        section = None

    for segment in segments:
        segment_words = segment.text.split()
        if not segment_words:
            continue
        if words and segment.page_number is not None and page_number is not None and segment.page_number != page_number:
            chunks.append(ChunkDraft(len(chunks), " ".join(words), page_number, section))
            words = []
            page_number = None
            section = None
        if not words:
            page_number = segment.page_number
            section = segment.section
        if len(words) + len(segment_words) > TARGET_WORDS and words:
            emit()
            if not words:
                page_number = segment.page_number
                section = segment.section
        words.extend(segment_words)
    emit()
    return chunks
