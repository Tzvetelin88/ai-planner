from __future__ import annotations

from pathlib import Path
from typing import Union

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.api.store import store
from src.models.schemas import (
    ClarificationResponse,
    DeploymentPlan,
    PlanRequest,
    RecommendationRequest,
    RecommendationResponse,
    SessionAnswerRequest,
)
from src.nlp.entity_parser import EntityParser
from src.nlp.intent_model import IntentClassifier
from src.planner.plan_generator import PlanGenerator
from src.planner.planning_service import PlanningService
from src.recommendations.recommendation_engine import RecommendationEngine
from src.recommendations.retrieval_index import RetrievalIndex

try:
    from src.asr.transcribe import SpeechTranscriber
except ImportError:  # pragma: no cover
    SpeechTranscriber = None


router = APIRouter(prefix="/plans", tags=["plans"])

retrieval_index = RetrievalIndex()
entity_parser = EntityParser()
intent_classifier = IntentClassifier()
intent_classifier.load_artifact(Path("artifacts/intent/model.pkl"))
plan_generator = PlanGenerator(retrieval_index=retrieval_index)
recommendation_engine = RecommendationEngine(retrieval_index=retrieval_index)
planning_service = PlanningService(
    store=store,
    entity_parser=entity_parser,
    intent_classifier=intent_classifier,
    plan_generator=plan_generator,
)


@router.post("/from-text", response_model=Union[DeploymentPlan, ClarificationResponse])
def create_plan_from_text(request: PlanRequest) -> DeploymentPlan | ClarificationResponse:
    return planning_service.create_plan_or_clarification(request)


@router.post("/from-voice", response_model=Union[DeploymentPlan, ClarificationResponse])
async def create_plan_from_voice(audio: UploadFile = File(...)) -> DeploymentPlan | ClarificationResponse:
    if SpeechTranscriber is None:
        raise HTTPException(status_code=500, detail="Speech transcription module is unavailable.")

    transcriber = SpeechTranscriber()
    audio_bytes = await audio.read()
    transcript = transcriber.transcribe_bytes(audio_bytes, audio.filename or "upload.wav")
    return planning_service.create_plan_or_clarification(
        PlanRequest(text=transcript, source="voice", allow_clarification=True)
    )


@router.post("/sessions/{session_id}/answer", response_model=Union[DeploymentPlan, ClarificationResponse])
def answer_clarification(session_id: str, request: SessionAnswerRequest) -> DeploymentPlan | ClarificationResponse:
    result = planning_service.continue_session(session_id, request)
    if result is None:
        raise HTTPException(status_code=404, detail="Planning session not found")
    return result


@router.get("/{plan_id}", response_model=DeploymentPlan)
def get_plan(plan_id: str) -> DeploymentPlan:
    plan = store.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")
    return plan


@router.post("/{plan_id}/recommendations", response_model=RecommendationResponse)
def get_recommendations(plan_id: str, request: RecommendationRequest | None = None) -> RecommendationResponse:
    plan = store.get_plan(plan_id)
    if plan is None:
        raise HTTPException(status_code=404, detail="Plan not found")

    execution_result = request.execution_result if request is not None else None
    return recommendation_engine.recommend(plan=plan, execution_result=execution_result)
