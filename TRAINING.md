# Training Guide

This document explains how training works in `AI Deployment Planner`, what data is used, where outputs are stored, how those outputs relate to the API, and how the current logic helps improve planning quality.

## Overview
The project currently has two training-related parts:
- an intent classifier baseline
- a recommendation and retrieval baseline

These training jobs are designed to prove the ML pipeline and create reusable artifacts for later improvement.

## 1. Intent Model Training

### Purpose
The intent model learns how to classify a user request into one of the supported deployment-planning intents.

Examples:
- create deployment plan
- update configuration plan
- rollback plan
- disaster recovery plan
- validation and health-check plan

### Input Data
The input dataset is:
- `data/training/intents.jsonl`

Each line contains:
- `text` - the user request
- `intent` - the target label
- `entities` - optional structured deployment details

Example records:

```json
{"text":"Create a staging deployment plan for a 3-node Kubernetes cluster with monitoring and backup enabled.","intent":"create_deployment_plan","entities":{"environment":"staging","target_platform":"kubernetes","region":null,"cluster_size":3,"monitoring_enabled":true,"backup_enabled":true,"rollback_required":true,"compliance_requirements":[],"constraints":[],"integrations":["monitoring","backup"]}}
{"text":"Generate a disaster recovery failover plan for our secondary region with health checks.","intent":"disaster_recovery_plan","entities":{"environment":"dr","target_platform":"generic-platform","region":"secondary-region","cluster_size":1,"monitoring_enabled":false,"backup_enabled":false,"rollback_required":true,"compliance_requirements":[],"constraints":[],"integrations":[]}}
```

### Current Training Logic
The baseline classifier is implemented in `src/nlp/intent_model.py`.

It currently uses:
- `scikit-learn`
- `TfidfVectorizer`
- `LogisticRegression`

Training flow:
1. Read all labeled rows from `data/training/intents.jsonl`
2. Extract the input text and target intent labels
3. Convert text into TF-IDF features
4. Train a logistic regression classifier
5. Report basic training metrics

Relevant code:

```python
texts = [sample.text for sample in samples]
labels = [sample.intent.value for sample in samples]
features = self.vectorizer.fit_transform(texts)
self.model.fit(features, labels)
```

### Training Script
Run with:

```bash
python training/train_intent_model.py
```

The script:
- loads the dataset
- trains the classifier
- writes metrics
- writes metadata
- optionally logs to MLflow if MLflow is installed

### Output Files
Generated output:
- `artifacts/intent/metrics.json`
- `artifacts/intent/metadata.json`

Example meaning:
- `metrics.json` contains training accuracy and sample count
- `metadata.json` currently stores whether the model was trained in that run

## 2. Recommendation / Retrieval Training

### Purpose
This training step creates a basic retrieval layer that can help connect:
- new deployment requests to similar known plans
- failure scenarios to similar known issues
- future recommendations to previous examples

### Input Data
The recommendation baseline uses two datasets:
- `data/training/plans.jsonl`
- `data/training/failures.jsonl`

#### Plans dataset
Contains:
- `prompt`
- `plan_summary`
- `groups`
- `known_risks`

Example:

```json
{"prompt":"Create a production deployment plan for a 5-node Kubernetes cluster with monitoring, backup, and rollback.","plan_summary":"Production Kubernetes rollout with prechecks, infra provisioning, platform configuration, protection controls, verification, and rollback steps.","groups":["pre_validation","infrastructure_setup","platform_configuration","security_and_backup","verification","rollback"],"known_risks":["production_change_window","backup_validation_needed","monitoring_dashboard_gap"]}
```

#### Failures dataset
Contains:
- `issue`
- `root_cause`
- `fix`
- `follow_up`

Example:

```json
{"issue":"Backup registration timed out during provisioning.","root_cause":"Backup service endpoint was unreachable from the target network.","fix":"Validate network path to the backup controller, then rerun backup enablement.","follow_up":"Add a precheck for backup service connectivity before provisioning."}
```

### Current Training Logic
The baseline retrieval model is implemented in `training/train_recommendation_model.py`.

It currently:
1. loads plan prompts and failure issue text
2. merges them into a single text corpus
3. vectorizes them with TF-IDF
4. computes similarity scores
5. saves a retrieval artifact

Current approach:
- `TfidfVectorizer`
- cosine similarity

Relevant code:

```python
plan_records = _load_jsonl(args.plans)
failure_records = _load_jsonl(args.failures)
corpus = [record["prompt"] for record in plan_records] + [record["issue"] for record in failure_records]

vectorizer = TfidfVectorizer(ngram_range=(1, 2))
matrix = vectorizer.fit_transform(corpus)
similarities = cosine_similarity(matrix, matrix)
```

### Training Script
Run with:

```bash
python training/train_recommendation_model.py
```

### Output Files
Generated output:
- `artifacts/recommendations/metrics.json`
- `artifacts/recommendations/retrieval_index.pkl`

Meaning:
- `metrics.json` stores basic training and retrieval stats
- `retrieval_index.pkl` stores the vectorizer and the corpus used for retrieval

## 3. Optional MLflow Logging

If `mlflow` is installed, both training scripts also log:
- run parameters
- metrics
- artifacts

You may see generated MLflow content under:
- `mlruns/`

This helps track experiments across multiple training runs.

## 4. Where the Runtime Input Comes From

At API runtime, the planner receives input from:
- `POST /plans/from-text`
- `POST /plans/from-voice`

Flow:
1. user sends text or audio
2. audio is converted to text if needed
3. intent is predicted
4. entities are extracted
5. a structured deployment plan is generated
6. the plan is returned as JSON
7. recommendations can be requested for that plan

Relevant runtime flow lives in:
- `src/api/routes/plans.py`

## 5. Where Runtime Output Goes

### API output
Generated plan responses are returned directly from the API and stored in the in-memory store while the API process is running.

Current in-memory storage:
- plans are not persisted to a database yet
- restarting the server clears the saved plans

### Demo script output
When running `sh ./quick_run.sh`, generated runtime output is saved to:
- `outputs/plan_response.json`
- `outputs/plan_saved.json`
- `outputs/recommendations.json`
- `outputs/server.log`

### Training output
Training artifacts are written to:
- `artifacts/intent/`
- `artifacts/recommendations/`

## 6. How the Current API Uses Training Results

Important current limitation:
- the training scripts produce artifacts on disk
- the runtime API does not yet automatically reload those artifacts on startup

Today this means:
- training validates the ML pipeline
- artifacts are created and available for reuse
- the API currently still uses the in-process classifier object and deterministic planning logic

So the training is useful, but the model-loading loop is not fully connected yet.

## 7. How Training Helps Improve the Planner

Even in the current form, more training data helps shape a stronger system.

### Better intent detection
More intent examples improve the system's ability to recognize:
- new wording styles
- short or ambiguous requests
- enterprise-specific deployment language

### Better recommendations
More plan and failure data improve:
- failure matching
- suggestion quality
- next-step recommendations
- safe remediation guidance

### Better deployment plans
As the datasets grow, the system can become better at:
- identifying risks
- proposing more useful prechecks
- improving rollback suggestions
- producing more realistic grouped task flows

## 8. Short Code and Flow Logic

### Runtime planning flow
1. User submits text or voice
2. Voice is transcribed if needed
3. Intent classifier predicts the request type
4. Entity parser extracts things like environment, platform, region, cluster size, monitoring, backup, and compliance
5. Plan generator builds:
   - plan metadata
   - groups
   - tasks
   - dependencies
   - prechecks
   - rollback steps
   - recommended actions
6. Plan is returned as JSON
7. Recommendation engine can enrich results, especially after a simulated failure

### Recommendation flow
The recommendation layer:
- starts with recommendations already attached to the plan
- adds remediation suggestions if execution fails
- pulls related troubleshooting guidance from the knowledge base
- adds risk-based actions for high-risk plans

## 9. Current State vs Future Improvements

### Current state
- working training scripts
- working output artifacts
- working API flow
- deterministic plan generation
- baseline ML/retrieval experiments

### Recommended next improvements
- persist trained models to a reusable format
- load trained artifacts during API startup
- save plans and execution results in SQLite instead of memory
- expand the training datasets
- move from baseline TF-IDF models to richer embedding or transformer-based models

## 10. Practical Summary

Short version:
- input training data lives in `data/training/`
- training scripts live in `training/`
- training output is saved in `artifacts/`
- runtime output is returned by the API and optionally saved in `outputs/`
- current training improves the project structure and future model quality, but automatic artifact reuse in the API is still the next step
