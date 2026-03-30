from __future__ import annotations

import argparse
import json
import pickle
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

try:
    import mlflow
except ImportError:  # pragma: no cover
    mlflow = None

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the baseline recommendation retrieval model.")
    parser.add_argument("--plans", type=Path, default=Path("data/training/plans.jsonl"))
    parser.add_argument("--failures", type=Path, default=Path("data/training/failures.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/recommendations"))
    return parser.parse_args()


def _load_jsonl(path: Path) -> list[dict]:
    records: list[dict] = []
    with path.open("r", encoding="utf-8") as handle:
        for line in handle:
            if line.strip():
                records.append(json.loads(line))
    return records


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    plan_records = _load_jsonl(args.plans)
    failure_records = _load_jsonl(args.failures)
    documents = [{"type": "plan", "text": record["prompt"], "record": record} for record in plan_records]
    documents.extend({"type": "failure", "text": record["issue"], "record": record} for record in failure_records)
    corpus = [document["text"] for document in documents]

    vectorizer = TfidfVectorizer(ngram_range=(1, 2))
    matrix = vectorizer.fit_transform(corpus)
    similarities = cosine_similarity(matrix, matrix)

    self_retrieval = float((similarities.argmax(axis=1) == list(range(len(corpus)))).mean())
    metrics = {
        "documents": float(len(corpus)),
        "plan_records": float(len(plan_records)),
        "failure_records": float(len(failure_records)),
        "self_retrieval_at_1": self_retrieval,
        "clarification_ready_records": float(sum(1 for record in plan_records if record.get("clarification_hints"))),
    }

    artifact_path = args.output_dir / "retrieval_index.pkl"
    with artifact_path.open("wb") as handle:
        pickle.dump({"vectorizer": vectorizer, "documents": documents}, handle)

    metrics_path = args.output_dir / "metrics.json"
    metrics_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    if mlflow is not None:
        with mlflow.start_run(run_name="recommendation-baseline"):
            mlflow.log_param("vectorizer", "tfidf")
            mlflow.log_param("plans_dataset", str(args.plans))
            mlflow.log_param("failures_dataset", str(args.failures))
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(str(metrics_path))
            mlflow.log_artifact(str(artifact_path))

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
