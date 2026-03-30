# Quick Samples

This file is for fast testing.

If someone wants to see the project working quickly, they can:
1. start the API
2. run one sample request
3. inspect the returned JSON

## 1. Start the API

```bash
uvicorn src.api.main:app --reload
```

## 2. Fast sample request

Run this in another terminal:

```bash
curl -X POST "http://127.0.0.1:8000/plans/from-text" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Create a staging deployment plan for a 3-node Kubernetes cluster with monitoring, backup, and rollback.\",\"source\":\"text\"}"
```

## 3. Example output

Example response:

```json
{
  "plan_metadata": {
    "plan_id": "plan-f7d560fcc9ba",
    "created_at": "2026-03-30T19:20:31.254026Z",
    "source": "text",
    "generator_version": "0.1.0"
  },
  "intent": {
    "intent": "rollback_plan",
    "confidence": 0.84,
    "rationale": "Detected rollback-oriented language."
  },
  "target_environment": "staging",
  "summary": "Create a rollback_plan workflow for the staging environment on kubernetes with 3 node(s).",
  "entities": {
    "environment": "staging",
    "target_platform": "kubernetes",
    "region": null,
    "cluster_size": 3,
    "monitoring_enabled": true,
    "backup_enabled": true,
    "rollback_required": true,
    "compliance_requirements": [],
    "constraints": [],
    "integrations": [
      "monitoring",
      "backup"
    ]
  },
  "groups": [
    {
      "id": "pre_validation",
      "title": "Pre-Validation",
      "summary": "Validate capacity, access, and constraints.",
      "order": 1
    },
    {
      "id": "infrastructure_setup",
      "title": "Infrastructure Setup",
      "summary": "Prepare the target infrastructure or runtime.",
      "order": 2
    },
    {
      "id": "platform_configuration",
      "title": "Platform Configuration",
      "summary": "Configure the requested platform and integrations.",
      "order": 3
    },
    {
      "id": "security_and_backup",
      "title": "Security and Backup",
      "summary": "Apply protection, backup, and audit controls.",
      "order": 4
    },
    {
      "id": "verification",
      "title": "Verification",
      "summary": "Run validation, health checks, and sign-off.",
      "order": 5
    },
    {
      "id": "rollback",
      "title": "Rollback",
      "summary": "Define safe recovery steps if execution fails.",
      "order": 6
    }
  ],
  "tasks": [
    {
      "id": "validate-inventory",
      "group_id": "pre_validation",
      "title": "Validate inventory and access",
      "description": "Validate access, quotas, and prerequisites for kubernetes.",
      "estimated_minutes": 10,
      "status": "pending",
      "automation_hint": "POST /mock/inventory/validate"
    },
    {
      "id": "collect-constraints",
      "group_id": "pre_validation",
      "title": "Collect deployment constraints",
      "description": "Confirm downtime, approval, compliance, and region constraints.",
      "estimated_minutes": 8,
      "status": "pending",
      "automation_hint": null
    },
    {
      "id": "provision-infra",
      "group_id": "infrastructure_setup",
      "title": "Provision infrastructure",
      "description": "Provision 3 nodes on kubernetes.",
      "estimated_minutes": 20,
      "status": "pending",
      "automation_hint": "POST /mock/provision/infra"
    },
    {
      "id": "generate-config",
      "group_id": "platform_configuration",
      "title": "Generate platform configuration",
      "description": "Generate target configuration from deployment intent.",
      "estimated_minutes": 12,
      "status": "pending",
      "automation_hint": "POST /mock/config/generate"
    },
    {
      "id": "configure-platform",
      "group_id": "platform_configuration",
      "title": "Configure platform",
      "description": "Apply generated configuration and platform integrations.",
      "estimated_minutes": 18,
      "status": "pending",
      "automation_hint": "POST /mock/provision/platform"
    },
    {
      "id": "enable-protection",
      "group_id": "security_and_backup",
      "title": "Enable backup and security controls",
      "description": "Turn on backup, logging, and encryption controls required for the plan.",
      "estimated_minutes": 15,
      "status": "pending",
      "automation_hint": "POST /mock/backup/enable"
    },
    {
      "id": "verify-health",
      "group_id": "verification",
      "title": "Run validation and health checks",
      "description": "Validate service health, metrics, and deployment completion criteria.",
      "estimated_minutes": 10,
      "status": "pending",
      "automation_hint": "POST /mock/verify/health"
    },
    {
      "id": "rollback-plan",
      "group_id": "rollback",
      "title": "Prepare rollback activation",
      "description": "Create the rollback handoff and trigger instructions if a failure occurs.",
      "estimated_minutes": 7,
      "status": "pending",
      "automation_hint": "POST /mock/rollback/start"
    }
  ],
  "dependencies": [
    {
      "task_id": "collect-constraints",
      "depends_on": "validate-inventory"
    },
    {
      "task_id": "provision-infra",
      "depends_on": "collect-constraints"
    },
    {
      "task_id": "generate-config",
      "depends_on": "provision-infra"
    },
    {
      "task_id": "configure-platform",
      "depends_on": "generate-config"
    },
    {
      "task_id": "enable-protection",
      "depends_on": "configure-platform"
    },
    {
      "task_id": "verify-health",
      "depends_on": "enable-protection"
    },
    {
      "task_id": "rollback-plan",
      "depends_on": "verify-health"
    }
  ],
  "prechecks": [
    {
      "id": "capacity-check",
      "title": "Capacity available",
      "description": "Validate that capacity exists for 3 nodes.",
      "required": true
    },
    {
      "id": "access-check",
      "title": "Access and credentials",
      "description": "Confirm operator access to target inventory and configuration systems.",
      "required": true
    }
  ],
  "rollback_plan": [
    {
      "id": "freeze-changes",
      "title": "Freeze further changes",
      "description": "Pause additional rollout activity and preserve logs."
    },
    {
      "id": "restore-config",
      "title": "Restore previous configuration",
      "description": "Restore the last known-good configuration for the staging environment."
    },
    {
      "id": "validate-recovery",
      "title": "Validate recovery state",
      "description": "Run health checks to confirm the system returned to a stable baseline."
    }
  ],
  "estimated_duration": 100,
  "risk_level": "medium",
  "recommended_actions": [
    {
      "title": "Review execution order",
      "reason": "Topological execution order starts with `validate-inventory` and ends with `rollback-plan`.",
      "priority": "medium"
    },
    {
      "title": "Use staged validation",
      "reason": "Running validation in a lower-risk environment reduces deployment risk.",
      "priority": "high"
    },
    {
      "title": "Verify backup retention policy",
      "reason": "Backup is enabled, so retention and restore test coverage should be confirmed.",
      "priority": "high"
    },
    {
      "title": "Attach monitoring dashboards",
      "reason": "Monitoring was requested and should be included in the handoff package.",
      "priority": "medium"
    }
  ],
  "task_count": 8
}
```

## Important Note

This sample currently returns `rollback_plan` as the detected intent because the sentence includes the word `rollback`.

If you want a cleaner deployment-plan example, use:

```bash
curl -X POST "http://127.0.0.1:8000/plans/from-text" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Create a staging deployment plan for a 3-node Kubernetes cluster with monitoring and backup.\",\"source\":\"text\"}"
```

That should more naturally map to:
- deployment planning
- kubernetes
- staging
- monitoring
- backup

## Windows PowerShell Version

```powershell
Invoke-RestMethod -Uri "http://127.0.0.1:8000/plans/from-text" `
  -Method Post `
  -ContentType "application/json" `
  -Body '{"text":"Create a staging deployment plan for a 3-node Kubernetes cluster with monitoring, backup, and rollback.","source":"text"}' | ConvertTo-Json -Depth 12
```

## Fast Test Flow

1. Start API:

```bash
uvicorn src.api.main:app --reload
```

2. Run sample request.

3. Inspect returned JSON.

4. Look at:
- detected intent
- groups
- tasks
- dependencies
- rollback steps
- recommendations
