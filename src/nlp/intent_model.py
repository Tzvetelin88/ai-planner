from __future__ import annotations

import json
import pickle
from pathlib import Path

from src.models.schemas import IntentPrediction, IntentTrainingSample, IntentType

try:
    from sklearn.feature_extraction.text import TfidfVectorizer
    from sklearn.linear_model import LogisticRegression
except ImportError:  # pragma: no cover
    TfidfVectorizer = None
    LogisticRegression = None


class IntentClassifier:
    def __init__(self) -> None:
        self.vectorizer = TfidfVectorizer(ngram_range=(1, 2)) if TfidfVectorizer else None
        self.model = LogisticRegression(max_iter=500) if LogisticRegression else None
        self._is_trained = False

    def predict(self, text: str) -> IntentPrediction:
        lowered = text.lower()
        if self._is_trained and self.vectorizer is not None and self.model is not None:
            features = self.vectorizer.transform([text])
            probabilities = self.model.predict_proba(features)[0]
            classes = self.model.classes_
            best_index = int(probabilities.argmax())
            return IntentPrediction(
                intent=IntentType(classes[best_index]),
                confidence=float(probabilities[best_index]),
                rationale="Predicted by trained TF-IDF baseline classifier.",
            )

        return self._heuristic_predict(lowered)

    def train(self, dataset_path: Path) -> dict[str, float]:
        if self.vectorizer is None or self.model is None:
            raise RuntimeError("scikit-learn is required to train the intent classifier")

        samples: list[IntentTrainingSample] = []
        with dataset_path.open("r", encoding="utf-8") as handle:
            for line in handle:
                if line.strip():
                    samples.append(IntentTrainingSample.model_validate_json(line))

        texts = [sample.text for sample in samples]
        labels = [sample.intent.value for sample in samples]
        features = self.vectorizer.fit_transform(texts)
        self.model.fit(features, labels)
        self._is_trained = True

        accuracy = float(self.model.score(features, labels))
        return {"train_accuracy": accuracy, "samples": float(len(samples))}

    def export_metadata(self, target_path: Path) -> None:
        payload = {"trained": self._is_trained, "artifact": "artifacts/intent/model.pkl"}
        target_path.write_text(json.dumps(payload, indent=2), encoding="utf-8")

    def export_artifact(self, target_path: Path) -> None:
        if self.vectorizer is None or self.model is None or not self._is_trained:
            raise RuntimeError("Cannot export an untrained intent classifier")

        with target_path.open("wb") as handle:
            pickle.dump({"vectorizer": self.vectorizer, "model": self.model}, handle)

    def load_artifact(self, target_path: Path) -> bool:
        if not target_path.exists():
            return False

        with target_path.open("rb") as handle:
            payload = pickle.load(handle)

        self.vectorizer = payload.get("vectorizer")
        self.model = payload.get("model")
        self._is_trained = self.vectorizer is not None and self.model is not None
        return self._is_trained

    def _heuristic_predict(self, text: str) -> IntentPrediction:
        matches: list[tuple[IntentType, float, str]] = []
        if any(keyword in text for keyword in ("failover", "dr", "disaster recovery")):
            matches.append(
                (
                    IntentType.DISASTER_RECOVERY_PLAN,
                    0.85,
                    "Detected failover and disaster recovery language.",
                )
            )
        if any(keyword in text for keyword in ("rollback", "restore previous", "undo deployment")):
            matches.append(
                (
                    IntentType.ROLLBACK_PLAN,
                    0.84,
                    "Detected rollback-oriented language.",
                )
            )
        if any(keyword in text for keyword in ("validate", "health check", "verification", "check system")):
            matches.append(
                (
                    IntentType.VALIDATION_HEALTH_CHECK_PLAN,
                    0.82,
                    "Detected validation and health-check language.",
                )
            )
        if any(keyword in text for keyword in ("update config", "change configuration", "roll out config")):
            matches.append(
                (
                    IntentType.UPDATE_CONFIGURATION_PLAN,
                    0.83,
                    "Detected staged configuration change language.",
                )
            )
        if any(keyword in text for keyword in ("deploy", "deployment plan", "create plan", "create a")):
            matches.append(
                (
                    IntentType.CREATE_DEPLOYMENT_PLAN,
                    0.8,
                    "Detected deployment planning language.",
                )
            )

        if not matches:
            return IntentPrediction(
                intent=IntentType.CREATE_DEPLOYMENT_PLAN,
                confidence=0.75,
                rationale="Defaulted to new deployment planning intent.",
            )

        if len(matches) > 1:
            best_intent, best_confidence, _ = max(matches, key=lambda item: item[1])
            matched_names = ", ".join(sorted({intent.value for intent, _, _ in matches}))
            return IntentPrediction(
                intent=best_intent,
                confidence=0.58,
                rationale=f"Ambiguous request matched multiple intent families: {matched_names}.",
            )

        intent, confidence, rationale = matches[0]
        return IntentPrediction(intent=intent, confidence=confidence, rationale=rationale)
