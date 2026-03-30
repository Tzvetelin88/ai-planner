from __future__ import annotations

from datetime import datetime, timezone
from enum import Enum
from typing import Any
from typing import Literal
from uuid import uuid4

from pydantic import BaseModel, Field, computed_field


class IntentType(str, Enum):
    CREATE_DEPLOYMENT_PLAN = "create_deployment_plan"
    UPDATE_CONFIGURATION_PLAN = "update_configuration_plan"
    ROLLBACK_PLAN = "rollback_plan"
    DISASTER_RECOVERY_PLAN = "disaster_recovery_plan"
    VALIDATION_HEALTH_CHECK_PLAN = "validation_health_check_plan"


class EnvironmentType(str, Enum):
    DEVELOPMENT = "development"
    STAGING = "staging"
    PRODUCTION = "production"
    DR = "dr"
    UNKNOWN = "unknown"


class RiskLevel(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class TaskStatus(str, Enum):
    PENDING = "pending"
    READY = "ready"
    BLOCKED = "blocked"
    COMPLETED = "completed"
    FAILED = "failed"


class DeploymentEntities(BaseModel):
    environment: EnvironmentType = EnvironmentType.UNKNOWN
    target_platform: str = "generic-platform"
    region: str | None = None
    cluster_size: int = Field(default=1, ge=1, le=100)
    monitoring_enabled: bool = False
    backup_enabled: bool = False
    rollback_required: bool = True
    compliance_requirements: list[str] = Field(default_factory=list)
    constraints: list[str] = Field(default_factory=list)
    integrations: list[str] = Field(default_factory=list)


class PlanRequest(BaseModel):
    text: str = Field(min_length=3)
    source: str = "text"
    user_id: str | None = None
    allow_clarification: bool = True


class IntentPrediction(BaseModel):
    intent: IntentType
    confidence: float = Field(ge=0.0, le=1.0)
    rationale: str


class PlanMetadata(BaseModel):
    plan_id: str = Field(default_factory=lambda: f"plan-{uuid4().hex[:12]}")
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    source: str = "text"
    generator_version: str = "0.2.0"


class Precheck(BaseModel):
    id: str
    title: str
    description: str
    required: bool = True


class TaskGroup(BaseModel):
    id: str
    title: str
    summary: str
    order: int


class PlanTask(BaseModel):
    id: str
    group_id: str
    title: str
    description: str
    estimated_minutes: int = Field(default=10, ge=1)
    status: TaskStatus = TaskStatus.PENDING
    automation_hint: str | None = None


class TaskDependency(BaseModel):
    task_id: str
    depends_on: str


class RollbackStep(BaseModel):
    id: str
    title: str
    description: str


class RecommendedAction(BaseModel):
    title: str
    reason: str
    priority: str = "medium"


class RetrievedPlanExample(BaseModel):
    prompt: str
    plan_summary: str
    groups: list[str]
    known_risks: list[str] = Field(default_factory=list)
    similarity_score: float = Field(default=0.0, ge=0.0)


class DeploymentPlan(BaseModel):
    plan_metadata: PlanMetadata
    intent: IntentPrediction
    target_environment: EnvironmentType
    summary: str
    entities: DeploymentEntities
    groups: list[TaskGroup]
    tasks: list[PlanTask]
    dependencies: list[TaskDependency]
    prechecks: list[Precheck]
    rollback_plan: list[RollbackStep]
    estimated_duration: int = Field(ge=1)
    risk_level: RiskLevel
    recommended_actions: list[RecommendedAction]
    strategy_source: str = "template"
    strategy_examples: list[RetrievedPlanExample] = Field(default_factory=list)

    @computed_field
    @property
    def task_count(self) -> int:
        return len(self.tasks)


class ExecutionWarning(BaseModel):
    code: str
    message: str


class MockExecutionRequest(BaseModel):
    plan_id: str
    task_id: str | None = None
    payload: dict[str, Any] = Field(default_factory=dict)


class MockExecutionResponse(BaseModel):
    success: bool
    service: str
    resource_ids: list[str] = Field(default_factory=list)
    warnings: list[ExecutionWarning] = Field(default_factory=list)
    dependency_issues: list[str] = Field(default_factory=list)
    remediation_suggestions: list[str] = Field(default_factory=list)


class RecommendationRequest(BaseModel):
    plan: DeploymentPlan
    execution_result: MockExecutionResponse | None = None


class RecommendationResponse(BaseModel):
    summary: str
    actions: list[RecommendedAction]


class ClarificationOption(BaseModel):
    value: str
    label: str


class ClarificationQuestion(BaseModel):
    id: str
    field_name: str
    prompt: str
    required: bool = True
    options: list[ClarificationOption] = Field(default_factory=list)


class ClarificationResponse(BaseModel):
    status: Literal["needs_clarification"] = "needs_clarification"
    session_id: str
    message: str
    intent: IntentPrediction
    known_entities: DeploymentEntities
    missing_fields: list[str]
    questions: list[ClarificationQuestion]


class SessionAnswer(BaseModel):
    question_id: str
    answer: str


class SessionAnswerRequest(BaseModel):
    answers: list[SessionAnswer]


class PlanningSession(BaseModel):
    session_id: str = Field(default_factory=lambda: f"session-{uuid4().hex[:12]}")
    original_text: str
    source: str = "text"
    intent: IntentPrediction
    entities: DeploymentEntities
    missing_fields: list[str] = Field(default_factory=list)
    questions: list[ClarificationQuestion] = Field(default_factory=list)
    answers: dict[str, Any] = Field(default_factory=dict)


class IntentTrainingSample(BaseModel):
    text: str
    intent: IntentType
    entities: DeploymentEntities | None = None
    needs_clarification: bool = False
    ambiguity_tags: list[str] = Field(default_factory=list)
    missing_fields: list[str] = Field(default_factory=list)


class PlanTrainingSample(BaseModel):
    prompt: str
    plan_summary: str
    groups: list[str]
    known_risks: list[str] = Field(default_factory=list)
    rollout_strategy: str | None = None
    dependency_pattern: str | None = None
    clarification_hints: list[str] = Field(default_factory=list)


class FailureTrainingSample(BaseModel):
    issue: str
    root_cause: str
    fix: str
    follow_up: str
    remediation_category: str | None = None
    plan_context: str | None = None
