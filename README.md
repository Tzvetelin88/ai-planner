# AI Deployment Planner

Experimental voice/text-driven deployment flow and execution plan creator.

## Overview
`AI Deployment Planner` is a Python-based project that translates user requests into a structured execution plan. A user can describe what they want by text or voice, and the system turns that intent into a machine-readable JSON plan with grouped tasks, dependencies, validation steps, and rollback actions.

The project is designed as a portfolio-ready AI system that combines:
- voice or text input
- intent recognition
- entity extraction
- plan generation
- mocked internal execution APIs
- recommendations for next steps, risk reduction, and failure recovery

## Main Idea
Instead of manually defining deployment steps, the user can say something like:

> Create a staging deployment plan for a 3-node cluster with monitoring, backup, and rollback checks.

The system should:
1. convert voice to text if needed
2. identify the user intent
3. extract key deployment parameters
4. generate a structured execution plan
5. simulate downstream provisioning APIs
6. provide recommendations, warnings, and possible fixes

## Project Goals
- Build an AI-assisted planner for deployment and configuration workflows.
- Support both voice and text interactions.
- Generate clean JSON plans separated into groups and tasks.
- Simulate execution through mocked internal APIs.
- Train models that improve intent detection and recommendations over time.
- Provide troubleshooting and remediation guidance for failed execution steps.

## Example Output
The planner is expected to generate plan objects with sections such as:
- `plan_metadata`
- `intent`
- `summary`
- `groups`
- `tasks`
- `dependencies`
- `prechecks`
- `rollback_plan`
- `risk_level`
- `recommended_actions`

## Example Use Cases
### 1. New environment deployment
Create a full deployment plan for a new staging or production environment.

### 2. Disaster recovery planning
Generate failover, validation, backup, and rollback actions for DR scenarios.

### 3. Configuration rollout planning
Build phased rollout plans for configuration updates with validation gates.

### 4. Failure remediation guidance
Recommend likely fixes when provisioning or validation steps fail.

### 5. Compliance-aware deployment preparation
Add security, auditing, encryption, and operational checks to regulated workloads.

## Experimental Workflow
```text
Voice/Text Input
    -> Speech-to-Text (if voice)
    -> Intent Recognition
    -> Entity Extraction
    -> Plan Generator
    -> Structured JSON Plan
    -> Mock Execution APIs
    -> Recommendation and Fix Engine
```

## Planned Architecture
- `FastAPI` backend for APIs and mock services
- `PyTorch` and NLP libraries for intent understanding
- `Pydantic` schemas for strict plan JSON validation
- `NetworkX` for task dependency flow modeling
- retrieval-based recommendation layer for fixes and suggestions
- local storage for requests, plans, outcomes, and feedback

## Planned Repository Areas
- `src/api/` - API entrypoints and routes
- `src/asr/` - voice transcription
- `src/nlp/` - intent and entity understanding
- `src/planner/` - plan generation and dependency logic
- `src/recommendations/` - recommendations and troubleshooting
- `training/` - model training scripts
- `data/` - datasets and knowledge assets
- `tests/` - API and planner tests

## Current Status
The repository now contains a working project skeleton with:
- a FastAPI application
- a deterministic plan generator
- mock execution APIs
- voice transcription hooks
- seed training datasets
- baseline training scripts
- focused API tests

## Quick Start
Install dependencies:

# AI Deployment Planner

Experimental voice/text-driven deployment flow and execution plan creator.

## Overview
`AI Deployment Planner` is a Python-based project that translates user requests into a structured execution plan. A user can describe what they want by text or voice, and the system turns that intent into a machine-readable JSON plan with grouped tasks, dependencies, validation steps, and rollback actions.

The project is designed as a portfolio-ready AI system that combines:
- voice or text input
- intent recognition
- entity extraction
- plan generation
- mocked internal execution APIs
- recommendations for next steps, risk reduction, and failure recovery

## Main Idea
Instead of manually defining deployment steps, the user can say something like:

> Create a staging deployment plan for a 3-node cluster with monitoring, backup, and rollback checks.

The system should:
1. convert voice to text if needed
2. identify the user intent
3. extract key deployment parameters
4. generate a structured execution plan
5. simulate downstream provisioning APIs
6. provide recommendations, warnings, and possible fixes

## Project Goals
- Build an AI-assisted planner for deployment and configuration workflows.
- Support both voice and text interactions.
- Generate clean JSON plans separated into groups and tasks.
- Simulate execution through mocked internal APIs.
- Train models that improve intent detection and recommendations over time.
- Provide troubleshooting and remediation guidance for failed execution steps.

## Example Output
The planner is expected to generate plan objects with sections such as:
- `plan_metadata`
- `intent`
- `summary`
- `groups`
- `tasks`
- `dependencies`
- `prechecks`
- `rollback_plan`
- `risk_level`
- `recommended_actions`

## Example Use Cases
### 1. New environment deployment
Create a full deployment plan for a new staging or production environment.

### 2. Disaster recovery planning
Generate failover, validation, backup, and rollback actions for DR scenarios.

### 3. Configuration rollout planning
Build phased rollout plans for configuration updates with validation gates.

### 4. Failure remediation guidance
Recommend likely fixes when provisioning or validation steps fail.

### 5. Compliance-aware deployment preparation
Add security, auditing, encryption, and operational checks to regulated workloads.

## Experimental Workflow
```text
Voice/Text Input
    -> Speech-to-Text (if voice)
    -> Intent Recognition
    -> Entity Extraction
    -> Plan Generator
    -> Structured JSON Plan
    -> Mock Execution APIs
    -> Recommendation and Fix Engine
```

## Planned Architecture
- `FastAPI` backend for APIs and mock services
- `PyTorch` and NLP libraries for intent understanding
- `Pydantic` schemas for strict plan JSON validation
- `NetworkX` for task dependency flow modeling
- retrieval-based recommendation layer for fixes and suggestions
- local storage for requests, plans, outcomes, and feedback

## Planned Repository Areas
- `src/api/` - API entrypoints and routes
- `src/asr/` - voice transcription
- `src/nlp/` - intent and entity understanding
- `src/planner/` - plan generation and dependency logic
- `src/recommendations/` - recommendations and troubleshooting
- `training/` - model training scripts
- `data/` - datasets and knowledge assets
- `tests/` - API and planner tests

## Current Status
The repository now contains a working project skeleton with:
- a FastAPI application
- a deterministic plan generator
- mock execution APIs
- voice transcription hooks
- seed training datasets
- baseline training scripts
- focused API tests

## Quick Start
Install dependencies:

```bash
pip install -e .[dev]
```

Run the API:

```bash
uvicorn src.api.main:app --reload
```

Run tests:

```bash
pytest
```

Run baseline training:

```bash
python training/train_intent_model.py
python training/train_recommendation_model.py
```

Quick demo run with Bash:

```bash
sh ./quick_run.sh
```

This script:
- installs the minimal runtime dependencies
- runs both baseline training scripts
- starts the API locally
- generates a sample deployment plan
- fetches the saved plan and recommendations
- stores output files under `outputs/`

For voice input support, also install:

```bash
pip install -e .[asr]
```

## Main API Endpoints
- `GET /health`
- `POST /plans/from-text`
- `POST /plans/from-voice`
- `GET /plans/{plan_id}`
- `POST /plans/{plan_id}/recommendations`
- `POST /mock/inventory/validate`
- `POST /mock/config/generate`
- `POST /mock/provision/infra`
- `POST /mock/provision/platform`
- `POST /mock/backup/enable`
- `POST /mock/verify/health`
- `POST /mock/rollback/start`

## Output Files
When you run `sh ./quick_run.sh`, you will get:
- `outputs/plan_response.json` - the initial generated plan returned by the API
- `outputs/plan_saved.json` - the same plan fetched back from the in-memory store
- `outputs/recommendations.json` - recommendation output for the generated plan
- `outputs/server.log` - local API server logs
- `artifacts/intent/metrics.json` - intent training metrics
- `artifacts/intent/metadata.json` - exported intent model metadata
- `artifacts/recommendations/metrics.json` - retrieval training metrics
- `artifacts/recommendations/retrieval_index.pkl` - saved recommendation retrieval artifact

## Why This Project Matters
This project demonstrates practical AI engineering beyond a simple chatbot. It focuses on converting human intent into actionable operational workflows that can later integrate with provisioning, deployment, backup, and disaster recovery platforms.
