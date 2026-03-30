from __future__ import annotations

import re
from typing import Any
from uuid import uuid4

from src.api.store import PlannerStore
from src.models.schemas import (
    ClarificationOption,
    ClarificationQuestion,
    ClarificationResponse,
    DeploymentEntities,
    DeploymentPlan,
    EnvironmentType,
    IntentPrediction,
    IntentType,
    PlanRequest,
    PlanningSession,
    SessionAnswerRequest,
)
from src.nlp.entity_parser import EntityParser
from src.nlp.intent_model import IntentClassifier
from src.planner.plan_generator import PlanGenerator


class PlanningService:
    def __init__(
        self,
        *,
        store: PlannerStore,
        entity_parser: EntityParser,
        intent_classifier: IntentClassifier,
        plan_generator: PlanGenerator,
    ) -> None:
        self.store = store
        self.entity_parser = entity_parser
        self.intent_classifier = intent_classifier
        self.plan_generator = plan_generator

    def create_plan_or_clarification(self, request: PlanRequest) -> DeploymentPlan | ClarificationResponse:
        intent = self.intent_classifier.predict(request.text)
        entities = self.entity_parser.parse(request.text)
        session = self._build_session(
            text=request.text,
            source=request.source,
            intent=intent,
            entities=entities,
            answers={},
        )
        if request.allow_clarification and session.questions:
            self.store.save_session(session)
            return self._to_clarification_response(session)
        return self._finalize_plan(session)

    def continue_session(self, session_id: str, request: SessionAnswerRequest) -> DeploymentPlan | ClarificationResponse | None:
        session = self.store.get_session(session_id)
        if session is None:
            return None

        applied_answers = dict(session.answers)
        for answer in request.answers:
            question = next((item for item in session.questions if item.id == answer.question_id), None)
            if question is None:
                continue
            self._apply_answer(session.entities, session.intent, question.field_name, answer.answer)
            applied_answers[question.field_name] = answer.answer

        updated = self._build_session(
            text=session.original_text,
            source=session.source,
            intent=session.intent,
            entities=session.entities,
            answers=applied_answers,
            session_id=session.session_id,
        )
        self.store.save_session(updated)
        if updated.questions:
            return self._to_clarification_response(updated)
        return self._finalize_plan(updated)

    def _build_session(
        self,
        *,
        text: str,
        source: str,
        intent: IntentPrediction,
        entities: DeploymentEntities,
        answers: dict[str, Any],
        session_id: str | None = None,
    ) -> PlanningSession:
        questions = self._build_questions(text, intent, entities, answers)
        missing_fields = [question.field_name for question in questions]
        return PlanningSession(
            session_id=session_id or f"session-{uuid4().hex[:12]}",
            original_text=text,
            source=source,
            intent=intent,
            entities=entities,
            missing_fields=missing_fields,
            questions=questions,
            answers=answers,
        )

    def _build_questions(
        self,
        text: str,
        intent: IntentPrediction,
        entities: DeploymentEntities,
        answers: dict[str, Any],
    ) -> list[ClarificationQuestion]:
        lowered = text.lower()
        questions: list[ClarificationQuestion] = []

        if intent.confidence < 0.7 and "intent" not in answers:
            questions.append(
                ClarificationQuestion(
                    id="intent-choice",
                    field_name="intent",
                    prompt="What kind of plan do you want the system to build?",
                    options=[
                        ClarificationOption(value=item.value, label=item.value.replace("_", " "))
                        for item in IntentType
                    ],
                )
            )

        if entities.environment == EnvironmentType.UNKNOWN and "environment" not in answers:
            questions.append(
                ClarificationQuestion(
                    id="environment-choice",
                    field_name="environment",
                    prompt="Which environment should this plan target?",
                    options=[
                        ClarificationOption(value=item.value, label=item.value)
                        for item in (EnvironmentType.DEVELOPMENT, EnvironmentType.STAGING, EnvironmentType.PRODUCTION, EnvironmentType.DR)
                    ],
                )
            )

        if entities.target_platform == "generic-platform" and "target_platform" not in answers:
            questions.append(
                ClarificationQuestion(
                    id="platform-choice",
                    field_name="target_platform",
                    prompt="Which platform should the plan be built for?",
                    options=[
                        ClarificationOption(value=value, label=value)
                        for value in ("kubernetes", "aws", "azure", "gcp", "vmware", "databricks")
                    ],
                )
            )

        explicit_cluster_size = bool(re.search(r"(\d+)[-\s]*(node|nodes|instance|instances)", lowered)) or "cluster_size" in answers
        if (
            intent.intent in {IntentType.CREATE_DEPLOYMENT_PLAN, IntentType.UPDATE_CONFIGURATION_PLAN, IntentType.DISASTER_RECOVERY_PLAN}
            and not explicit_cluster_size
        ):
            questions.append(
                ClarificationQuestion(
                    id="cluster-size",
                    field_name="cluster_size",
                    prompt="How many nodes or instances should the plan assume?",
                )
            )

        if entities.environment == EnvironmentType.PRODUCTION and "rollback_required" not in answers and "rollback" not in lowered:
            questions.append(
                ClarificationQuestion(
                    id="rollback-required",
                    field_name="rollback_required",
                    prompt="Should the production plan include explicit rollback steps?",
                    options=[
                        ClarificationOption(value="true", label="yes"),
                        ClarificationOption(value="false", label="no"),
                    ],
                )
            )

        return questions[:4]

    def _apply_answer(
        self,
        entities: DeploymentEntities,
        intent: IntentPrediction,
        field_name: str,
        answer: str,
    ) -> None:
        normalized = answer.strip().lower()
        if field_name == "intent":
            intent.intent = IntentType(normalized)
            intent.confidence = 1.0
            intent.rationale = "Confirmed by user during clarification."
        elif field_name == "environment":
            entities.environment = EnvironmentType(normalized)
        elif field_name == "target_platform":
            entities.target_platform = normalized
        elif field_name == "cluster_size":
            entities.cluster_size = max(1, int(normalized))
        elif field_name == "rollback_required":
            entities.rollback_required = normalized in {"true", "yes", "y", "1"}

    def _finalize_plan(self, session: PlanningSession) -> DeploymentPlan:
        effective_text = self._compose_effective_text(session)
        plan = self.plan_generator.generate(
            text=effective_text,
            source=session.source,
            intent=session.intent,
            entities=session.entities,
        )
        self.store.save_plan(plan)
        return plan

    def _compose_effective_text(self, session: PlanningSession) -> str:
        answer_suffix = " ".join(f"{key} {value}" for key, value in session.answers.items())
        return f"{session.original_text} {answer_suffix}".strip()

    def _to_clarification_response(self, session: PlanningSession) -> ClarificationResponse:
        return ClarificationResponse(
            session_id=session.session_id,
            message="The system needs a few more details before it can build a reliable plan.",
            intent=session.intent,
            known_entities=session.entities,
            missing_fields=session.missing_fields,
            questions=session.questions,
        )
