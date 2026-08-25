"""Build the ChromaDB knowledge-base collection."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_BASE = ROOT / "knowledge-base"
CHROMA_PATH = ROOT / ".chroma"
COLLECTION_NAME = "knowledge_base"


def parse_document(path: Path) -> tuple[dict[str, str], list[dict[str, str]]]:
    text = path.read_text(encoding="utf-8")
    metadata: dict[str, str] = {"filename": path.name}
    body = text
    if text.startswith("---"):
        _, front_matter, body = text.split("---", 2)
        try:
            import yaml
            parsed = yaml.safe_load(front_matter) or {}
        except ImportError:
            parsed = {line.split(":", 1)[0].strip(): line.split(":", 1)[1].strip() for line in front_matter.splitlines() if ":" in line}
        metadata.update({key: str(value) for key, value in parsed.items()})
    metadata["status"] = {"14-internal-content-migration-notes.md": "internal", "02-returns-policy-legacy.md": "superseded"}.get(path.name, metadata.get("status", "active"))
    sections = re.split(r"(?=^#{2,3}\s+)", body, flags=re.MULTILINE)
    chunks = []
    for section in sections:
        section = section.strip()
        if not section:
            continue
        heading_match = re.match(r"^(#{2,3})\s+(.+?)\s*$", section)
        heading = heading_match.group(2) if heading_match else metadata.get("title", path.stem)
        chunks.append({"text": section, "heading": heading})
    return metadata, chunks


def build_chunks() -> list[dict[str, Any]]:
    result = []
    for path in sorted(KNOWLEDGE_BASE.glob("*.md")):
        metadata, sections = parse_document(path)
        for index, section in enumerate(sections):
            result.append({"text": section["text"], "heading": section["heading"], "filename": path.name, "status": metadata["status"], "chunk_id": f"{path.name}:{index}"})
    return result


def index_documents() -> int:
    import chromadb
    from sentence_transformers import SentenceTransformer

    chunks = build_chunks()
    client = chromadb.PersistentClient(path=str(CHROMA_PATH))
    collection = client.get_or_create_collection(COLLECTION_NAME, metadata={"hnsw:space": "cosine"})
    model = SentenceTransformer("all-MiniLM-L6-v2")
    collection.upsert(
        ids=[chunk["chunk_id"] for chunk in chunks],
        documents=[chunk["text"] for chunk in chunks],
        embeddings=model.encode([chunk["text"] for chunk in chunks]).tolist(),
        metadatas=[{key: chunk[key] for key in ("filename", "heading", "status", "chunk_id")} for chunk in chunks],
    )
    return len(chunks)


if __name__ == "__main__":
    print(f"Indexed {index_documents()} knowledge-base chunks into {CHROMA_PATH}")