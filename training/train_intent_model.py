from __future__ import annotations

import argparse
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.nlp.intent_model import IntentClassifier

try:
    import mlflow
except ImportError:  # pragma: no cover
    mlflow = None


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Train the baseline intent classifier.")
    parser.add_argument("--dataset", type=Path, default=Path("data/training/intents.jsonl"))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/intent"))
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    args.output_dir.mkdir(parents=True, exist_ok=True)

    classifier = IntentClassifier()
    metrics = classifier.train(args.dataset)
    classifier.export_metadata(args.output_dir / "metadata.json")

    summary_path = args.output_dir / "metrics.json"
    summary_path.write_text(json.dumps(metrics, indent=2), encoding="utf-8")

    if mlflow is not None:
        with mlflow.start_run(run_name="intent-baseline"):
            mlflow.log_param("dataset", str(args.dataset))
            mlflow.log_param("model_type", "tfidf_logistic_regression")
            mlflow.log_metrics(metrics)
            mlflow.log_artifact(str(summary_path))
            mlflow.log_artifact(str(args.output_dir / "metadata.json"))

    print(json.dumps(metrics, indent=2))


if __name__ == "__main__":
    main()
