# Samples and Scenarios

This document contains example text prompts and voice-style phrases for the current `AI Deployment Planner`.

These samples are based on what the project supports today:
- text input
- voice input after speech-to-text
- intent detection
- entity extraction
- grouped deployment plans
- recommendations and troubleshooting support

## What the System Understands Today

The current parser is strongest when prompts include clear keywords for:
- environment: `development`, `staging`, `production`, `dr`
- platform: `kubernetes`, `k8s`, `aws`, `azure`, `gcp`, `vmware`, `databricks`
- size: `3 nodes`, `5 nodes`, `2 instances`
- features: `monitoring`, `backup`, `logging`
- constraints: `zero downtime`, `approval`, `encryption`
- compliance: `pci`, `hipaa`, `sox`, `gdpr`
- regions such as `us-east-1`, `eu-west-1`

## How To Use These Samples

### Text mode
Send the sample prompt as the `text` field to:
- `POST /plans/from-text`

### Voice mode
Say the same sentence naturally and upload the recorded audio to:
- `POST /plans/from-voice`

The system will transcribe the audio, then use the same planning logic as text mode.

## Sample 1: Kubernetes Staging Deployment

### Text prompt
`Create a staging deployment plan for a 3-node Kubernetes cluster with monitoring, backup, and rollback.`

### Voice example
`Create a staging deployment plan for a three node Kubernetes cluster with monitoring, backup, and rollback.`

### What this should trigger
- intent: `create_deployment_plan`
- environment: `staging`
- platform: `kubernetes`
- cluster size: `3`
- monitoring: enabled
- backup: enabled

### Typical outcome
- grouped plan
- infrastructure setup tasks
- platform configuration tasks
- security and backup tasks
- verification and rollback steps

## Sample 2: Production Kubernetes With Constraints

### Text prompt
`Create a production k8s plan with 5 nodes, zero downtime, approval, encryption, logging, and backup.`

### Voice example
`Create a production K eight S plan with five nodes, zero downtime, approval, encryption, logging, and backup.`

### What this should trigger
- intent: `create_deployment_plan`
- environment: `production`
- platform: `kubernetes`
- cluster size: `5`
- constraints: `zero_downtime`, `manual_approval`, `encryption_required`
- backup: enabled
- integrations: logging, backup

### Typical outcome
- high-risk plan
- stronger recommendations
- security and backup group included
- rollback and validation steps included

## Sample 3: Disaster Recovery Plan

### Text prompt
`Prepare a DR failover plan for our secondary region with backup validation and health checks.`

### Voice example
`Prepare a disaster recovery failover plan for our secondary region with backup validation and health checks.`

### What this should trigger
- intent: `disaster_recovery_plan`
- environment: `dr`
- region: `secondary-region`
- backup: enabled

### Typical outcome
- DR-style plan
- verification focus
- rollback and recovery guidance
- failback-oriented recommendations

## Sample 4: Configuration Rollout

### Text prompt
`Roll out a config update to staging first and production after approval.`

### Voice example
`Roll out a configuration update to staging first and production after approval.`

### What this should trigger
- intent: `update_configuration_plan`
- environment: `staging`
- constraint: `manual_approval`

### Typical outcome
- configuration-oriented plan
- validation and approval steps
- rollback included

## Sample 5: Validation and Health Check

### Text prompt
`Run validation and health checks for the production Kubernetes cluster with monitoring.`

### Voice example
`Run validation and health checks for the production Kubernetes cluster with monitoring.`

### What this should trigger
- intent: `validation_health_check_plan`
- environment: `production`
- platform: `kubernetes`
- monitoring: enabled

### Typical outcome
- smaller validation-focused plan
- pre-validation group
- verification group
- rollback group

## Sample 6: Compliance-Aware Deployment

### Text prompt
`Create a deployment plan for a PCI workload with encryption, logging, and backup in production.`

### Voice example
`Create a deployment plan for a P C I workload with encryption, logging, and backup in production.`

### What this should trigger
- intent: `create_deployment_plan`
- compliance: `PCI`
- environment: `production`
- backup: enabled
- constraint: `encryption_required`
- integrations: logging, backup

### Typical outcome
- high-risk plan
- compliance precheck
- security and backup tasks
- validation and rollback included

## Sample 7: Databricks Environment Plan

### Text prompt
`Deploy a production Databricks environment with encryption and logging enabled.`

### Voice example
`Deploy a production Databricks environment with encryption and logging enabled.`

### What this should trigger
- intent: `create_deployment_plan`
- environment: `production`
- platform: `databricks`
- constraint: `encryption_required`
- integrations: logging

### Typical outcome
- production deployment plan
- configuration steps
- security-oriented recommendations

## Sample 8: Rollback Plan

### Text prompt
`Prepare a rollback plan to restore the previous production release.`

### Voice example
`Prepare a rollback plan to restore the previous production release.`

### What this should trigger
- intent: `rollback_plan`
- environment: `production`

### Typical outcome
- rollback-oriented plan
- recovery validation
- lower number of tasks than a full deployment plan

## Suggested Demo Prompts

If you want fast demo-ready examples, use these:

1. `Create a staging deployment plan for a 3-node Kubernetes cluster with monitoring, backup, and rollback.`
2. `Create a production k8s plan with 5 nodes, zero downtime, approval, encryption, logging, and backup.`
3. `Prepare a DR failover plan for our secondary region with backup validation and health checks.`
4. `Roll out a config update to staging first and production after approval.`
5. `Create a deployment plan for a PCI workload with encryption, logging, and backup in production.`

## Current Limitations

The current system does not yet generate completely free-form custom groups and tasks from arbitrary requests.

Right now it works best when:
- the request includes supported keywords
- the platform and environment are stated clearly
- the request maps to one of the supported planning intents

The planner then fills in a structured plan using the current built-in group and task templates.

## Best Prompt Style

For best results, use this pattern:

`Create a [environment] [platform] deployment plan with [size], [features], and [constraints].`

Examples:
- `Create a staging Kubernetes deployment plan with 3 nodes, monitoring, backup, and rollback.`
- `Create a production AWS deployment plan with 5 nodes, encryption, approval, and backup.`
- `Prepare a DR Azure failover plan with health checks and backup validation.`
