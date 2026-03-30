from __future__ import annotations

import re

from src.models.schemas import DeploymentEntities, EnvironmentType


class EntityParser:
    ENVIRONMENT_KEYWORDS = {
        EnvironmentType.DEVELOPMENT: ("dev", "development"),
        EnvironmentType.STAGING: ("stage", "staging", "uat"),
        EnvironmentType.PRODUCTION: ("prod", "production"),
        EnvironmentType.DR: ("dr", "disaster recovery", "failover", "secondary region"),
    }

    PLATFORM_KEYWORDS = {
        "kubernetes": ("kubernetes", "k8s"),
        "vmware": ("vmware", "vsphere"),
        "databricks": ("databricks", "spark"),
        "aws": ("aws", "ec2"),
        "azure": ("azure",),
        "gcp": ("gcp", "google cloud"),
    }

    COMPLIANCE_KEYWORDS = ("pci", "hipaa", "sox", "gdpr")

    def parse(self, text: str) -> DeploymentEntities:
        lowered = text.lower()
        entities = DeploymentEntities()

        entities.environment = self._detect_environment(lowered)
        entities.target_platform = self._detect_platform(lowered)
        entities.cluster_size = self._detect_cluster_size(lowered)
        entities.region = self._detect_region(lowered)
        entities.monitoring_enabled = any(keyword in lowered for keyword in ("monitoring", "metrics", "observability"))
        entities.backup_enabled = any(keyword in lowered for keyword in ("backup", "snapshot", "restore point"))
        entities.rollback_required = "no rollback" not in lowered
        entities.compliance_requirements = [item.upper() for item in self.COMPLIANCE_KEYWORDS if item in lowered]
        entities.integrations = self._detect_integrations(lowered)
        entities.constraints = self._detect_constraints(lowered)
        return entities

    def _detect_environment(self, text: str) -> EnvironmentType:
        for environment, keywords in self.ENVIRONMENT_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return environment
        return EnvironmentType.UNKNOWN

    def _detect_platform(self, text: str) -> str:
        for platform, keywords in self.PLATFORM_KEYWORDS.items():
            if any(keyword in text for keyword in keywords):
                return platform
        return "generic-platform"

    def _detect_cluster_size(self, text: str) -> int:
        match = re.search(r"(\d+)[-\s]*(node|nodes|instance|instances)", text)
        if match:
            return int(match.group(1))
        return 1

    def _detect_region(self, text: str) -> str | None:
        match = re.search(r"(us-[a-z]+-\d|eu-[a-z]+-\d|ap-[a-z]+-\d)", text)
        if match:
            return match.group(1)
        if "secondary region" in text:
            return "secondary-region"
        return None

    def _detect_integrations(self, text: str) -> list[str]:
        integrations: list[str] = []
        for keyword in ("monitoring", "backup", "logging", "vault", "servicenow"):
            if keyword in text:
                integrations.append(keyword)
        return integrations

    def _detect_constraints(self, text: str) -> list[str]:
        constraints: list[str] = []
        if "zero downtime" in text:
            constraints.append("zero_downtime")
        if "approval" in text:
            constraints.append("manual_approval")
        if "encrypted" in text or "encryption" in text:
            constraints.append("encryption_required")
        return constraints
