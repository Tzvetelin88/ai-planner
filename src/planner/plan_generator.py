from __future__ import annotations

from src.models.schemas import (
    DeploymentEntities,
    DeploymentPlan,
    IntentPrediction,
    IntentType,
    PlanMetadata,
    PlanTask,
    Precheck,
    RecommendedAction,
    RetrievedPlanExample,
    RiskLevel,
    RollbackStep,
    TaskDependency,
    TaskGroup,
)
from src.planner.dependency_graph import topological_task_ids, validate_dependencies
from src.recommendations.retrieval_index import RetrievalIndex


class PlanGenerator:
    GROUP_LIBRARY = {
        "pre_validation": ("Pre-Validation", "Validate capacity, access, and constraints."),
        "infrastructure_setup": ("Infrastructure Setup", "Prepare the target infrastructure or runtime."),
        "platform_configuration": ("Platform Configuration", "Configure the requested platform and integrations."),
        "security_and_backup": ("Security and Backup", "Apply protection, backup, and audit controls."),
        "verification": ("Verification", "Run validation, health checks, and sign-off."),
        "rollback": ("Rollback", "Define safe recovery steps if execution fails."),
    }

    def __init__(self, retrieval_index: RetrievalIndex | None = None) -> None:
        self.retrieval_index = retrieval_index or RetrievalIndex()

    def generate(self, *, text: str, source: str, intent: IntentPrediction, entities: DeploymentEntities) -> DeploymentPlan:
        strategy_examples = self._retrieve_strategy_examples(text)
        groups = self._build_groups(intent.intent, entities, strategy_examples)
        tasks = self._build_tasks(groups, intent.intent, entities)
        dependencies = self._build_dependencies(tasks)
        validate_dependencies(tasks, dependencies)

        estimated_duration = sum(task.estimated_minutes for task in tasks)
        risk_level = self._assess_risk(entities)
        summary = self._build_summary(intent, entities, groups)
        prechecks = self._build_prechecks(entities)
        rollback_plan = self._build_rollback_steps(entities)
        recommendations = self._build_recommendations(entities, intent.intent, strategy_examples)
        ordering = topological_task_ids(tasks, dependencies)

        recommendations.insert(
            0,
            RecommendedAction(
                title="Review execution order",
                reason=f"Topological execution order starts with `{ordering[0]}` and ends with `{ordering[-1]}`.",
                priority="medium",
            ),
        )

        return DeploymentPlan(
            plan_metadata=PlanMetadata(source=source),
            intent=intent,
            target_environment=entities.environment,
            summary=summary,
            entities=entities,
            groups=groups,
            tasks=tasks,
            dependencies=dependencies,
            prechecks=prechecks,
            rollback_plan=rollback_plan,
            estimated_duration=estimated_duration,
            risk_level=risk_level,
            recommended_actions=recommendations,
            strategy_source="retrieval_hybrid" if strategy_examples else "template",
            strategy_examples=strategy_examples,
        )

    def _build_groups(
        self,
        intent: IntentType,
        entities: DeploymentEntities,
        strategy_examples: list[RetrievedPlanExample],
    ) -> list[TaskGroup]:
        if strategy_examples:
            group_ids = list(strategy_examples[0].groups)
        elif intent == IntentType.VALIDATION_HEALTH_CHECK_PLAN:
            group_ids = ["pre_validation", "verification", "rollback"]
        else:
            group_ids = list(self.GROUP_LIBRARY)

        if entities.backup_enabled and "security_and_backup" not in group_ids:
            group_ids.append("security_and_backup")
        if intent in {IntentType.DISASTER_RECOVERY_PLAN, IntentType.ROLLBACK_PLAN} and "rollback" not in group_ids:
            group_ids.append("rollback")
        if "verification" not in group_ids:
            group_ids.append("verification")
        if "pre_validation" not in group_ids:
            group_ids.insert(0, "pre_validation")

        if intent == IntentType.ROLLBACK_PLAN:
            prioritized = ["pre_validation", "rollback", "verification"]
            group_ids = [group_id for group_id in prioritized if group_id in group_ids]

        group_ids = list(dict.fromkeys(group_ids))
        group_defs: list[tuple[str, str, str]] = []
        for group_id in group_ids:
            title, summary = self.GROUP_LIBRARY[group_id]
            if intent == IntentType.VALIDATION_HEALTH_CHECK_PLAN and group_id == "pre_validation":
                summary = "Confirm environment and monitoring coverage."
            if intent == IntentType.VALIDATION_HEALTH_CHECK_PLAN and group_id == "verification":
                summary = "Run validation and health-check actions."
            group_defs.append((group_id, title, summary))

        return [
            TaskGroup(id=group_id, title=title, summary=summary, order=index)
            for index, (group_id, title, summary) in enumerate(group_defs, start=1)
        ]

    def _build_tasks(
        self,
        groups: list[TaskGroup],
        intent: IntentType,
        entities: DeploymentEntities,
    ) -> list[PlanTask]:
        tasks: list[PlanTask] = []
        for group in groups:
            if group.id == "pre_validation":
                tasks.extend(
                    [
                        PlanTask(
                            id="validate-inventory",
                            group_id=group.id,
                            title="Validate inventory and access",
                            description=f"Validate access, quotas, and prerequisites for {entities.target_platform}.",
                            estimated_minutes=10,
                            automation_hint="POST /mock/inventory/validate",
                        ),
                        PlanTask(
                            id="collect-constraints",
                            group_id=group.id,
                            title="Collect deployment constraints",
                            description="Confirm downtime, approval, compliance, and region constraints.",
                            estimated_minutes=8,
                        ),
                    ]
                )
            elif group.id == "infrastructure_setup":
                tasks.append(
                    PlanTask(
                        id="provision-infra",
                        group_id=group.id,
                        title="Provision infrastructure",
                        description=f"Provision {entities.cluster_size} nodes on {entities.target_platform}.",
                        estimated_minutes=20,
                        automation_hint="POST /mock/provision/infra",
                    )
                )
            elif group.id == "platform_configuration":
                tasks.extend(
                    [
                        PlanTask(
                            id="generate-config",
                            group_id=group.id,
                            title="Generate platform configuration",
                            description="Generate target configuration from deployment intent.",
                            estimated_minutes=12,
                            automation_hint="POST /mock/config/generate",
                        ),
                        PlanTask(
                            id="configure-platform",
                            group_id=group.id,
                            title="Configure platform",
                            description="Apply generated configuration and platform integrations.",
                            estimated_minutes=18,
                            automation_hint="POST /mock/provision/platform",
                        ),
                    ]
                )
            elif group.id == "security_and_backup":
                tasks.append(
                    PlanTask(
                        id="enable-protection",
                        group_id=group.id,
                        title="Enable backup and security controls",
                        description="Turn on backup, logging, and encryption controls required for the plan.",
                        estimated_minutes=15,
                        automation_hint="POST /mock/backup/enable",
                    )
                )
            elif group.id == "verification":
                verification_title = "Run health checks" if intent == IntentType.VALIDATION_HEALTH_CHECK_PLAN else "Run validation and health checks"
                tasks.append(
                    PlanTask(
                        id="verify-health",
                        group_id=group.id,
                        title=verification_title,
                        description="Validate service health, metrics, and deployment completion criteria.",
                        estimated_minutes=10,
                        automation_hint="POST /mock/verify/health",
                    )
                )
            elif group.id == "rollback":
                tasks.append(
                    PlanTask(
                        id="rollback-plan",
                        group_id=group.id,
                        title="Prepare rollback activation",
                        description="Create the rollback handoff and trigger instructions if a failure occurs.",
                        estimated_minutes=7,
                        automation_hint="POST /mock/rollback/start",
                    )
                )
        return tasks

    def _build_dependencies(self, tasks: list[PlanTask]) -> list[TaskDependency]:
        ids = {task.id for task in tasks}
        pairs = [
            ("collect-constraints", "validate-inventory"),
            ("provision-infra", "collect-constraints"),
            ("generate-config", "provision-infra"),
            ("configure-platform", "generate-config"),
            ("enable-protection", "configure-platform"),
            ("verify-health", "enable-protection"),
            ("rollback-plan", "verify-health"),
        ]
        return [
            TaskDependency(task_id=task_id, depends_on=depends_on)
            for task_id, depends_on in pairs
            if task_id in ids and depends_on in ids
        ]

    def _build_prechecks(self, entities: DeploymentEntities) -> list[Precheck]:
        checks = [
            Precheck(
                id="capacity-check",
                title="Capacity available",
                description=f"Validate that capacity exists for {entities.cluster_size} nodes.",
            ),
            Precheck(
                id="access-check",
                title="Access and credentials",
                description="Confirm operator access to target inventory and configuration systems.",
            ),
        ]
        if entities.compliance_requirements:
            checks.append(
                Precheck(
                    id="compliance-check",
                    title="Compliance controls confirmed",
                    description="Confirm security controls required by compliance requirements are available.",
                )
            )
        return checks

    def _build_rollback_steps(self, entities: DeploymentEntities) -> list[RollbackStep]:
        return [
            RollbackStep(
                id="freeze-changes",
                title="Freeze further changes",
                description="Pause additional rollout activity and preserve logs.",
            ),
            RollbackStep(
                id="restore-config",
                title="Restore previous configuration",
                description=f"Restore the last known-good configuration for the {entities.environment.value} environment.",
            ),
            RollbackStep(
                id="validate-recovery",
                title="Validate recovery state",
                description="Run health checks to confirm the system returned to a stable baseline.",
            ),
        ]

    def _build_recommendations(
        self,
        entities: DeploymentEntities,
        intent: IntentType,
        strategy_examples: list[RetrievedPlanExample],
    ) -> list[RecommendedAction]:
        actions = [
            RecommendedAction(
                title="Use staged validation",
                reason="Running validation in a lower-risk environment reduces deployment risk.",
                priority="high",
            )
        ]
        if entities.backup_enabled:
            actions.append(
                RecommendedAction(
                    title="Verify backup retention policy",
                    reason="Backup is enabled, so retention and restore test coverage should be confirmed.",
                    priority="high",
                )
            )
        if entities.monitoring_enabled:
            actions.append(
                RecommendedAction(
                    title="Attach monitoring dashboards",
                    reason="Monitoring was requested and should be included in the handoff package.",
                    priority="medium",
                )
            )
        if intent == IntentType.DISASTER_RECOVERY_PLAN:
            actions.append(
                RecommendedAction(
                    title="Include failback readiness",
                    reason="DR plans should define the return path after secondary-region activation.",
                    priority="high",
                )
            )
        for example in strategy_examples:
            for risk in example.known_risks[:2]:
                actions.append(
                    RecommendedAction(
                        title="Review retrieved plan risk",
                        reason=f"Similar plan `{example.prompt}` highlights risk `{risk}`.",
                        priority="medium",
                    )
                )
        return actions

    def _build_summary(
        self,
        intent: IntentPrediction,
        entities: DeploymentEntities,
        groups: list[TaskGroup],
    ) -> str:
        return (
            f"Create a {intent.intent.value} workflow for the {entities.environment.value} environment "
            f"on {entities.target_platform} with {entities.cluster_size} node(s) across "
            f"{len(groups)} group(s)."
        )

    def _assess_risk(self, entities: DeploymentEntities) -> RiskLevel:
        if entities.environment.value == "production" or entities.compliance_requirements:
            return RiskLevel.HIGH
        if entities.backup_enabled or entities.monitoring_enabled or entities.cluster_size > 3:
            return RiskLevel.MEDIUM
        return RiskLevel.LOW

    def _retrieve_strategy_examples(self, text: str) -> list[RetrievedPlanExample]:
        examples: list[RetrievedPlanExample] = []
        for match in self.retrieval_index.retrieve_plan_examples(text, limit=2):
            record = match.get("record", {})
            if not record:
                continue
            examples.append(
                RetrievedPlanExample(
                    prompt=record.get("prompt", match["text"]),
                    plan_summary=record.get("plan_summary", "Retrieved similar plan."),
                    groups=record.get("groups", []),
                    known_risks=record.get("known_risks", []),
                    similarity_score=match.get("score", 0.0),
                )
            )
        return examples
