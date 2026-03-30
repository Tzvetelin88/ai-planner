# Troubleshooting Knowledge Base

## Backup registration timeout
Symptoms:
- backup enablement step fails
- registration API times out
- backup status remains pending

Suggested actions:
- verify network connectivity to the backup controller
- validate authentication and service account permissions
- retry backup registration after downstream service health is restored

## Health checks failed after configuration
Symptoms:
- verification returns degraded status
- monitoring metrics are missing
- service readiness probes fail

Suggested actions:
- compare generated configuration to the expected baseline
- redeploy observability agents
- rerun health validation after configuration reconciliation

## Capacity and quota mismatch
Symptoms:
- infrastructure provisioning fails early
- requested node count exceeds available quota

Suggested actions:
- lower the requested node count
- request more capacity
- add a quota check before provisioning starts

## DR validation and DNS delay
Symptoms:
- disaster recovery failover completes but validation still fails
- traffic is not switching to the secondary region

Suggested actions:
- verify DNS propagation and TTL assumptions
- extend the validation window
- add explicit DNS cutover checkpoints to the DR runbook

## Compliance control gap
Symptoms:
- encryption or audit checks fail
- deployment blocks on mandatory security controls

Suggested actions:
- enable encryption defaults in the generated configuration
- verify audit logging sinks before rollout
- include compliance checks in pre-validation and verification groups
