from __future__ import annotations

from dataclasses import dataclass, field

from src.models.schemas import DeploymentPlan, MockExecutionResponse


@dataclass
class PlannerStore:
    plans: dict[str, DeploymentPlan] = field(default_factory=dict)
    execution_results: dict[str, list[MockExecutionResponse]] = field(default_factory=dict)

    def save_plan(self, plan: DeploymentPlan) -> DeploymentPlan:
        self.plans[plan.plan_metadata.plan_id] = plan
        return plan

    def get_plan(self, plan_id: str) -> DeploymentPlan | None:
        return self.plans.get(plan_id)

    def save_execution_result(self, plan_id: str, result: MockExecutionResponse) -> None:
        self.execution_results.setdefault(plan_id, []).append(result)

    def get_execution_results(self, plan_id: str) -> list[MockExecutionResponse]:
        return self.execution_results.get(plan_id, [])


store = PlannerStore()
