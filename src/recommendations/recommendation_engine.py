from __future__ import annotations

from src.models.schemas import (
    DeploymentPlan,
    MockExecutionResponse,
    RecommendedAction,
    RecommendationResponse,
)
from src.recommendations.troubleshooting_retriever import TroubleshootingRetriever


class RecommendationEngine:
    def __init__(self, retriever: TroubleshootingRetriever | None = None) -> None:
        self.retriever = retriever or TroubleshootingRetriever()

    def recommend(
        self,
        plan: DeploymentPlan,
        execution_result: MockExecutionResponse | None = None,
    ) -> RecommendationResponse:
        actions = list(plan.recommended_actions)

        if execution_result is not None and not execution_result.success:
            for suggestion in execution_result.remediation_suggestions:
                actions.append(
                    RecommendedAction(
                        title="Remediate failed execution",
                        reason=suggestion,
                        priority="high",
                    )
                )
            for section in self.retriever.retrieve(" ".join(execution_result.dependency_issues + execution_result.remediation_suggestions)):
                actions.append(
                    RecommendedAction(
                        title="Review troubleshooting guidance",
                        reason=section.splitlines()[0],
                        priority="medium",
                    )
                )

        if plan.risk_level.value == "high":
            actions.append(
                RecommendedAction(
                    title="Require change approval",
                    reason="High-risk plans should include a formal approval gate before execution.",
                    priority="high",
                )
            )

        summary = (
            "Recommendations generated from plan structure and execution outcome."
            if execution_result
            else "Recommendations generated from plan structure."
        )
        return RecommendationResponse(summary=summary, actions=actions)
