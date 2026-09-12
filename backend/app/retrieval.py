from pathlib import Path
from typing import Any


class RetrievalEngine:
    def __init__(self, docs_dir: Path) -> None:
        self.docs_dir = docs_dir
        self.documents = self._load_documents()

    def _load_documents(self) -> list[dict[str, Any]]:
        docs: list[dict[str, Any]] = []
        if not self.docs_dir.exists():
            return docs

        for file_path in sorted(self.docs_dir.glob("*.md")):
            content = file_path.read_text(encoding="utf-8")
            docs.append(
                {
                    "id": file_path.stem,
                    "title": file_path.stem.replace("_", " ").title(),
                    "content": content,
                    "tags": [part.strip().lower() for part in content.splitlines()[0:3] if part.strip()],
                }
            )
        return docs

    def retrieve(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        norm_query = query.lower()
        results: list[tuple[float, dict[str, Any]]] = []

        for doc in self.documents:
            text = f"{doc['title']} {doc['content']}".lower()
            score = 0.0
            for token in norm_query.split():
                if token in text:
                    score += 1.5
                if token in doc["tags"]:
                    score += 2.0
            if score > 0:
                results.append((score, doc))

        results.sort(key=lambda item: item[0], reverse=True)
        ranked = [doc for _, doc in results[:limit]]

        if not ranked:
            ranked = [
                {
                    "id": "fallback-sop",
                    "title": "Safe Simulation Fallback",
                    "content": "No exact matching SOP found. Use deterministic recovery heuristics and verify state before re-enabling traffic.",
                    "tags": ["fallback", "recovery"],
                    "confidence": 55,
                }
            ]

        for doc in ranked:
            doc.setdefault("confidence", 90)
        return ranked
