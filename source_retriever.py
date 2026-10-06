import json
import re
from pathlib import Path
from collections import Counter


BASE_DIR = Path(__file__).resolve().parent
SOURCE_PATH = BASE_DIR / "Source" / "source.json"


# Common words that do not help source retrieval.
STOPWORDS = {
    "the",
    "and",
    "for",
    "with",
    "that",
    "this",
    "from",
    "was",
    "were",
    "has",
    "have",
    "had",
    "patient",
    "medical",
    "report",
    "actual",
    "expected",
    "json",
    "result",
    "information",
    "difference",
    "differences",
    "summary",
    "data",
    "value",
    "field",
    "unknown",
    "not",
    "but",
    "are",
    "is",
    "to",
    "of",
    "in",
    "on",
    "at",
    "as",
    "an",
    "or",
    "by",
    "be",
    "it",
    "was",
    "also",
    "may",
    "can",
    "when",
    "than",
    "then",
    "into",
    "their",
    "there",
    "which",
    "these",
    "those",
    "should",
    "could",
    "would",
}


def load_source(path: Path = SOURCE_PATH):
    if not path.exists():
        raise FileNotFoundError(
            f"Source JSON not found: {path}"
        )

    try:
        with path.open("r", encoding="utf-8-sig") as file:
            return json.load(file)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"Invalid source JSON in {path}: {exc}"
        ) from exc


def normalize_text(text):
    if not text:
        return ""

    text = str(text).lower()

    # Preserve useful medical tokens such as:
    # c5-c6, 02/23/2020, l4-l5, icd-10
    text = re.sub(r"[^a-z0-9/\-.]+", " ", text)

    return text


def tokenize(text):
    normalized = normalize_text(text)

    tokens = normalized.split()

    result = []

    for token in tokens:
        if len(token) <= 1:
            continue

        if token in STOPWORDS:
            continue

        result.append(token)

    return result


def build_query(comparison_text, expected_text="", actual_text=""):
    """
    Build a retrieval query from the existing comparison plus the
    expected and actual reports.

    The comparison is weighted most heavily because it already
    identifies the meaningful differences.
    """

    comparison_text = comparison_text or ""
    expected_text = expected_text or ""
    actual_text = actual_text or ""

    # Limit very large inputs so retrieval remains inexpensive.
    comparison_text = comparison_text[:15000]
    expected_text = expected_text[:10000]
    actual_text = actual_text[:10000]

    return "\n".join(
        [
            comparison_text,
            comparison_text,
            expected_text,
            actual_text,
        ]
    )


def score_chunk(query_tokens, chunk):
    """
    Deterministic lexical relevance score.

    This intentionally does not require another LLM/API call.
    The source set is only ~125 chunks, so this is inexpensive.
    """

    text = chunk.get("text", "")
    chunk_tokens = tokenize(text)

    if not chunk_tokens:
        return 0.0

    query_counter = Counter(query_tokens)
    chunk_counter = Counter(chunk_tokens)

    score = 0.0

    for token, query_count in query_counter.items():
        if token not in chunk_counter:
            continue

        occurrence = chunk_counter[token]

        # Exact token overlap.
        score += min(query_count, occurrence)

        # Slightly reward repeated medically relevant terms.
        if occurrence > 1:
            score += 0.25

    # Normalize so very large chunks do not automatically win.
    score = score / max(len(chunk_tokens) ** 0.5, 1)

    return score


def retrieve_relevant_chunks(
    query,
    top_k=8,
    source_path=SOURCE_PATH,
):
    """
    Search the entire source.json and return the most relevant chunks.

    Returns chunks with their original document/page provenance.
    """

    source = load_source(source_path)

    chunks = source.get("chunks", [])

    if not chunks:
        raise ValueError(
            f"No chunks found in source file: {source_path}"
        )

    query_tokens = tokenize(query)

    if not query_tokens:
        return []

    scored = []

    for chunk in chunks:
        score = score_chunk(query_tokens, chunk)

        if score <= 0:
            continue

        scored.append(
            {
                "score": score,
                "chunk": chunk,
            }
        )

    scored.sort(
        key=lambda item: item["score"],
        reverse=True,
    )

    results = []

    for item in scored[:top_k]:
        chunk = item["chunk"]

        results.append(
            {
                "chunk_id": chunk.get("chunk_id"),
                "document_id": chunk.get("document_id"),
                "file_name": chunk.get("file_name"),
                "page_number": chunk.get("page_number"),
                "text": chunk.get("text", ""),
                "retrieval_score": round(
                    item["score"],
                    4,
                ),
            }
        )

    return results


def format_chunks_for_judge(chunks):
    if not chunks:
        return "NO SOURCE EVIDENCE WAS RETRIEVED."

    sections = []

    for index, chunk in enumerate(chunks, start=1):
        sections.append(
            f"""
--- SOURCE EVIDENCE {index} ---

Chunk ID: {chunk["chunk_id"]}
Document ID: {chunk["document_id"]}
File: {chunk["file_name"]}
PDF Page: {chunk["page_number"]}

Source Text:
{chunk["text"]}
""".strip()
        )

    return "\n\n".join(sections)