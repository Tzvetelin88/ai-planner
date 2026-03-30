from __future__ import annotations

from pathlib import Path


class TroubleshootingRetriever:
    def __init__(self, knowledge_path: Path | None = None) -> None:
        self.knowledge_path = knowledge_path or Path("data/knowledge/troubleshooting.md")

    def retrieve(self, query: str, limit: int = 3) -> list[str]:
        if not self.knowledge_path.exists():
            return []

        content = self.knowledge_path.read_text(encoding="utf-8")
        sections = [section.strip() for section in content.split("\n## ") if section.strip()]
        query_terms = set(query.lower().split())

        scored_sections: list[tuple[int, str]] = []
        for raw_section in sections:
            normalized = raw_section.lower()
            score = sum(1 for term in query_terms if term in normalized)
            if score:
                scored_sections.append((score, raw_section))

        scored_sections.sort(key=lambda item: item[0], reverse=True)
        return [section for _, section in scored_sections[:limit]]
