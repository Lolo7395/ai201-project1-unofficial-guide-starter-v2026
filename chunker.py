"""
Stage 2 of the pipeline: splitting documents into chunks.

⚠️ THIS IS THE FILE YOU CHANGE IN MILESTONE 3.

`split_documents` below is deliberately plain. It cuts every document into
fixed-size pieces with a fixed overlap and pays no attention to where sentences
or paragraphs end. It works, and it is not good.

On a corpus of short posts it may not cut anything at all: `campus_life` comes
out as 88 documents and 88 chunks, because almost nothing in it reaches 800
characters. That is the baseline, not a bug — Milestone 3 is where you decide
whether one post should stay one chunk.

Your job in Milestone 3 is to replace the *body* of `split_documents` with a
strategy that fits the documents you actually read in Milestone 1. Keep the
name and the shape of what it returns — the rest of the pipeline calls it, and
your README has to name the function that produced your chunks.

If you get stuck for 30 minutes, `fallback_split` is the original. Switch back
to it, write down what you saw, and move on. That's a real observation about
your pipeline, not giving up.
"""

import re
from dataclasses import dataclass

import config
from ingest import Document


MAX_CHARS = config.CHUNK_SIZE
MIN_CHARS = config.MIN_CHUNK_SIZE
OVERLAP = config.CHUNK_OVERLAP


@dataclass
class Chunk:
    """One piece of one document."""

    text: str
    source: str        # which file it came from
    index: int         # which chunk within that file, starting at 0
    produced_by: str   # the function that made it — cite this in your README

    @property
    def label(self) -> str:
        return f"{self.source}#{self.index}"


def fallback_split(
    documents: list[Document],
    chunk_size: int | None = None,
    overlap: int | None = None,
) -> list[Chunk]:
    """
    The starter's original chunker. Fixed-size character windows with overlap.

    Keep this function. Milestone 3's stop rule points back at it, and having
    something to compare your own strategy against is useful in unit 2.
    """
    chunk_size = chunk_size or config.CHUNK_SIZE
    overlap = overlap or config.CHUNK_OVERLAP

    if overlap >= chunk_size:
        raise ValueError("overlap has to be smaller than chunk_size")

    chunks: list[Chunk] = []
    for doc in documents:
        start = 0
        index = 0
        while start < len(doc.text):
            piece = doc.text[start : start + chunk_size].strip()
            if piece:
                chunks.append(
                    Chunk(
                        text=piece,
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::fallback_split",
                    )
                )
                index += 1
            start += chunk_size - overlap

    return chunks


def _sections(text: str) -> tuple[str, list[tuple[str, str]]]:
    """Return (document title, [(section heading, section body), ...])."""
    title = ""
    sections: list[tuple[str, str]] = []
    heading, body = "", []
    for line in text.split("\n"):
        if line.startswith("# ") and not title:
            title = line[2:].strip()
        elif line.startswith("## "):
            if "".join(body).strip():
                sections.append((heading, "\n".join(body).strip()))
            heading, body = line[3:].strip(), []
        else:
            body.append(line)
    if "".join(body).strip():
        sections.append((heading, "\n".join(body).strip()))
    return title, sections


def _split_sentences(body: str, limit: int, overlap: int) -> list[str]:
    """Break one over-long paragraph at sentence ends, carrying an overlap."""
    sentences = re.split(r"(?<=[.!?])\s+", body)
    pieces: list[str] = []
    current = ""
    for sentence in sentences:
        if current and len(current) + len(sentence) + 1 > limit:
            pieces.append(current)
            # carry whole trailing sentence(s) that fit in the overlap
            tail = ""
            for prev in reversed(re.split(r"(?<=[.!?])\s+", current)):
                if len(prev) + len(tail) > overlap:
                    break
                tail = f"{prev} {tail}".strip()
            current = tail
        current = f"{current} {sentence}".strip()
    if current:
        pieces.append(current)
    return pieces


def _split_long(body: str, limit: int, overlap: int) -> list[str]:
    """
    Break an over-long section on paragraph boundaries, packing paragraphs up to
    `limit`. A paragraph is one thought (e.g. one town in the accessibility
    guide), so it is never cut unless it alone exceeds `limit`; only then do we
    fall back to sentence splits with overlap.
    """
    pieces: list[str] = []
    current = ""
    for para in (p.strip() for p in body.split("\n\n") if p.strip()):
        if len(para) > limit:
            if current:
                pieces.append(current)
                current = ""
            pieces.extend(_split_sentences(para, limit, overlap))
        elif current and len(current) + len(para) + 2 > limit:
            pieces.append(current)
            current = para
        else:
            current = f"{current}\n\n{para}" if current else para
    if current:
        pieces.append(current)
    return pieces


def split_documents(documents: list[Document]) -> list[Chunk]:
    """
    Section-aware chunking for the city guides.

    Every guide is a few hundred characters per "## " section, and each section
    is about one topic (getting there, where to stay, ...). So one section = one
    chunk. Each chunk is prefixed with "<guide title> — <section heading>" so it
    stands alone: "There is no local bus service" is useless without knowing
    which town it is about, and the embedding also learns the town name.

    Sections shorter than MIN_CHARS are merged into the next one; sections
    longer than MAX_CHARS are split at sentence ends with OVERLAP characters
    shared between the pieces. Overlap is only used when a split happens.
    """
    chunks: list[Chunk] = []
    for doc in documents:
        title, sections = _sections(doc.text)
        title = title or doc.source
        index = 0
        pending_heading, pending_body = "", ""
        for i, (heading, body) in enumerate(sections):
            if pending_body:
                heading = " / ".join(h for h in (pending_heading, heading) if h)
                body = f"{pending_body}\n\n{body}"
                pending_heading, pending_body = "", ""
            if len(body) < MIN_CHARS and i < len(sections) - 1:
                pending_heading, pending_body = heading, body
                continue
            prefix = f"{title} — {heading}" if heading else title
            for piece in (
                _split_long(body, MAX_CHARS, OVERLAP) if len(body) > MAX_CHARS else [body]
            ):
                chunks.append(
                    Chunk(
                        text=f"{prefix}\n{piece}",
                        source=doc.source,
                        index=index,
                        produced_by="chunker.py::split_documents",
                    )
                )
                index += 1
    return chunks


def describe(chunks: list[Chunk]) -> str:
    """A one-line summary, printed after indexing."""
    if not chunks:
        return "0 chunks"
    lengths = [len(c.text) for c in chunks]
    return (
        f"{len(chunks)} chunks, "
        f"{sum(lengths) // len(lengths)} characters on average "
        f"(shortest {min(lengths)}, longest {max(lengths)}), "
        f"produced by {chunks[0].produced_by}"
    )


if __name__ == "__main__":
    from ingest import load_documents

    chunks = split_documents(load_documents())
    print(describe(chunks))
