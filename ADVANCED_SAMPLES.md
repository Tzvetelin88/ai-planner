# Advanced Samples

This file demonstrates the new hybrid planner behavior introduced in version `0.2.0`.

These examples focus on:
- ambiguous requests
- missing information
- clarification questions
- adaptive planning from retrieved examples
- dataset-driven improvement

## 1. Ambiguous Deployment Versus Rollback

### Request
`Create a staging deployment plan for a 3-node Kubernetes cluster with monitoring, backup, and rollback.`

### Why it is advanced
This sentence contains both deployment and rollback language.

### Expected behavior
The system may return a clarification response instead of a final plan.

Typical question:
- `What kind of plan do you want the system to build?`

Typical answer:
- `create_deployment_plan`

After the answer, the planner finalizes the deployment plan.

## 2. Missing Cluster Size

### Request
`Create a production Kubernetes deployment plan with backup and monitoring.`

### Expected clarification
- `How many nodes or instances should the plan assume?`
- `Should the production plan include explicit rollback steps?`

### Example answers
- `5`
- `yes`

### Result
The final plan includes:
- production risk level
- rollback steps
- validation tasks
- protection controls

## 3. Missing Platform

### Request
`Build me a deployment plan for staging.`

### Expected clarification
- `Which platform should the plan be built for?`
- `How many nodes or instances should the plan assume?`

### Example answers
- `kubernetes`
- `3`

### Result
The planner can build a valid structured plan after the missing fields are supplied.

## 4. Adaptive Configuration Rollout

### Request
`Roll out a config update to staging first and production after validation.`

### Why it matters
This type of request should no longer always look like a full infrastructure deployment.

### Expected adaptive behavior
The planner should favor a configuration-style strategy using retrieved examples, such as:
- `pre_validation`
- `platform_configuration`
- `verification`
- `rollback`

Instead of always forcing infrastructure-heavy groups.

## 5. Compliance-Aware Dynamic Plan

### Request
`Create a production deployment plan for a PCI workload with encryption, logging, and backup.`

### Expected behavior
The planner should:
- detect higher risk
- include security-focused groups
- add compliance-aware prechecks
- attach stronger recommendations
- reuse known risks from similar plan examples where available

## 6. DR-Focused Retrieval Strategy

### Request
`Prepare a DR failover plan for the secondary region with health checks and backup validation.`

### Expected behavior
The planner should adapt toward a DR-like strategy:
- less emphasis on generic infra provisioning
- more emphasis on validation, failover readiness, and rollback/failback

## 7. API Example: Clarification Flow

### Step 1: initial request

```bash
curl -X POST "http://127.0.0.1:8000/plans/from-text" \
  -H "Content-Type: application/json" \
  -d "{\"text\":\"Create a production Kubernetes deployment plan with backup and monitoring.\",\"source\":\"text\"}"
```

### Step 2: expected kind of response

```json
{
  "status": "needs_clarification",
  "session_id": "session-123456789abc",
  "missing_fields": [
    "cluster_size",
    "rollback_required"
  ],
  "questions": [
    {
      "id": "cluster-size",
      "field_name": "cluster_size",
      "prompt": "How many nodes or instances should the plan assume?",
      "required": true,
      "options": []
    },
    {
      "id": "rollback-required",
      "field_name": "rollback_required",
      "prompt": "Should the production plan include explicit rollback steps?",
      "required": true,
      "options": [
        {
          "value": "true",
          "label": "yes"
        },
        {
          "value": "false",
          "label": "no"
        }
      ]
    }
  ]
}
```

### Step 3: answer the questions

```bash
curl -X POST "http://127.0.0.1:8000/plans/sessions/session-123456789abc/answer" \
  -H "Content-Type: application/json" \
  -d "{\"answers\":[{\"question_id\":\"cluster-size\",\"answer\":\"5\"},{\"question_id\":\"rollback-required\",\"answer\":\"yes\"}]}"
```

### Step 4: final result
The system should return the final `DeploymentPlan`.

## 8. Dataset Improvement Examples

The project now supports the idea of using clarification data as future learning material.

Examples live in:
- `data/training/clarifications.jsonl`

Good examples include:
- ambiguous prompts
- missing required fields
- user answers to clarification questions
- final resolved entities and intent

## 9. Best Advanced Prompt Style

If you want to test the dynamic behavior, use prompts that are:
- partially specified
- intentionally ambiguous
- compliance-heavy
- DR-heavy
- staged rollout oriented

Examples:
- `Create a safer production rollout for Kubernetes.`
- `Build me a deployment plan for staging.`
- `Prepare a DR failover plan for our secondary region.`
- `Create a PCI deployment plan for production with backup and encryption.`

## 10. Current Boundaries

The planner is now more dynamic, but it is still not fully free-form generative planning.

The current best-practice model is:
- retrieve similar examples
- ask follow-up questions when needed
- shape the plan dynamically
- validate it with schemas and dependency checks
- fall back to deterministic templates if needed
