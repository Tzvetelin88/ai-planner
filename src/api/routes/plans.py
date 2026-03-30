from __future__ import annotations

from fastapi import APIRouter, File, HTTPException, UploadFile

from src.api.store import store
from src.models.schemas import DeploymentPlan, PlanRequest, RecommendationRequest, RecommendationResponse
from src.nlp.entity_parser import EntityParser
from src.nlp.intent_model import IntentClassifier
from src.planner.plan_generator import PlanGenerator
from src.recommendations.recommendation_engine import RecommendationEngine

try:
    from src.asr.transcribe import SpeechTranscriber
except ImportError:  # pragma: no cover
    SpeechTranscriber = None


router = APIRouter(prefix="/plans", tags=["plans"])

entity_parser = EntityParser()
intent_classifier = IntentClassifier()
plan_generator = PlanGenerator()
recommendation_engine = RecommendationEngine()


@router.post("/from-text", response_model=DeploymentPlan)
def create_plan_from_text(request: PlanRequest) -> DeploymentPlan:
    intent = intent_classifier.predict(request.text)
    entities = entity_parser.parse(request.text)
    plan = plan_generator.generate(text=request.text, source=request.source, intent=intent, entities=entities)
    return store.save_plan(plan)


@router.post("/from-voice", response_model=DeploymentPlan)
async def create_plan_from_voice(audio: UploadFile = File(...)) -> DeploymentPlan:
    if SpeechTranscriber is None:
        raise HTTPException(status_code=500, detail="Speech transcription module is unavailable.")

    transcriber = SpeechTranscriber()
    audio_bytes = await audio.read()
    transcript = transcriber.transcribe_bytes(audio_bytes, audio.filename or "upload.wav")
    intent = intent_classifier.predict(transcript)
    entities = entity_parser.parse(transcript)
    plan = plan_generator.generate(text=transcript, source="voice", intent=intent, entities=entities)
    return store.save_plan(plan)


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
