from __future__ import annotations

import json
import pickle
from pathlib import Path
from typing import Any

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.metrics.pairwise import cosine_similarity
except ImportError:  # pragma: no cover
    TfidfVectorizer = None
    cosine_similarity = None


class RetrievalIndex:
    def __init__(
        self,
        *,
        artifact_path: Path | None = None,
        plans_path: Path | None = None,
        failures_path: Path | None = None,
    ) -> None:
        self.artifact_path = artifact_path or Path("artifacts/recommendations/retrieval_index.pkl")
        self.plans_path = plans_path or Path("data/training/plans.jsonl")
        self.failures_path = failures_path or Path("data/training/failures.jsonl")
        self.vectorizer: Any | None = None
        self.documents: list[dict[str, Any]] = []
        self._document_matrix: Any | None = None
        self._load()

    def retrieve(self, query: str, *, document_type: str | None = None, limit: int = 3) -> list[dict[str, Any]]:
        candidates = [
            (index, document)
            for index, document in enumerate(self.documents)
            if document_type is None or document.get("type") == document_type
        ]
        if not candidates:
            return []

        if self.vectorizer is not None and self._document_matrix is not None and cosine_similarity is not None:
            query_vector = self.vectorizer.transform([query])
            scores = cosine_similarity(query_vector, self._document_matrix)[0]
            ranked = sorted(
                ((float(scores[index]), document) for index, document in candidates),
                key=lambda item: item[0],
                reverse=True,
            )
        else:
            query_terms = set(query.lower().split())
            ranked = sorted(
                (
                    (
                        float(sum(1 for term in query_terms if term in document["text"].lower())),
                        document,
                    )
                    for _, document in candidates
                ),
                key=lambda item: item[0],
                reverse=True,
            )

        return [
            {"score": score, **document}
            for score, document in ranked[:limit]
            if score > 0 or document_type == "plan"
        ]

    def retrieve_plan_examples(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        return self.retrieve(query, document_type="plan", limit=limit)

    def retrieve_failure_examples(self, query: str, limit: int = 3) -> list[dict[str, Any]]:
        return self.retrieve(query, document_type="failure", limit=limit)

    def _load(self) -> None:
        if self.artifact_path.exists():
            with self.artifact_path.open("rb") as handle:
                payload = pickle.load(handle)
            self.vectorizer = payload.get("vectorizer")
            self.documents = payload.get("documents", [])

            # Backward compatibility with the earlier corpus-only artifact.
            if not self.documents and "corpus" in payload:
                self.documents = [
                    {"type": "legacy", "text": text, "record": {"text": text}}
                    for text in payload["corpus"]
                ]

            if self.vectorizer is not None and self.documents:
                self._document_matrix = self.vectorizer.transform([doc["text"] for doc in self.documents])
            return

        self._build_from_datasets()

    def _build_from_datasets(self) -> None:
        documents: list[dict[str, Any]] = []
        for record in self._load_jsonl(self.plans_path):
            documents.append({"type": "plan", "text": record["prompt"], "record": record})
        for record in self._load_jsonl(self.failures_path):
            documents.append({"type": "failure", "text": record["issue"], "record": record})

        self.documents = documents
        if TfidfVectorizer is not None and self.documents:
            self.vectorizer = TfidfVectorizer(ngram_range=(1, 2))
            self._document_matrix = self.vectorizer.fit_transform([doc["text"] for doc in self.documents])

    def _load_jsonl(self, path: Path) -> list[dict[str, Any]]:
        if not path.exists():
            return []

        records: list[dict[str, Any]] = []
        with path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    records.append(json.loads(line))
        return records
