# Training Guide

This document explains how training works in `AI Deployment Planner`, what data is used, where outputs are stored, how runtime now reuses those outputs, and how to build better datasets for dynamic planning.

## Overview
The current training setup has three data layers:
- intent training data
- plan and failure retrieval data
- clarification examples for future learning and evaluation

The current runtime is a hybrid system:
- trained intent artifacts can be loaded at startup
- retrieval artifacts can shape plans and recommendations
- clarification data is currently a dataset foundation and reference, not a fully trained model

## 1. Intent Model Training

### Purpose
The intent model learns to classify a request into one of the supported planning intents:
- create deployment plan
- update configuration plan
- rollback plan
- disaster recovery plan
- validation and health-check plan

### Input Data
Primary dataset:
- `data/training/intents.jsonl`

Each row contains:
- `text`
- `intent`
- optional `entities`
- optional clarification metadata such as `needs_clarification`, `ambiguity_tags`, and `missing_fields`

### Current Training Logic
The baseline classifier in `src/nlp/intent_model.py` uses:
- `TfidfVectorizer`
- `LogisticRegression`

Training flow:
1. load `intents.jsonl`
2. convert input text into TF-IDF vectors
3. train the classifier
4. save metrics and model artifact

### Training Script

```bash
python training/train_intent_model.py
```

### Output Files
- `artifacts/intent/metrics.json`
- `artifacts/intent/metadata.json`
- `artifacts/intent/model.pkl`

### Runtime Use
The API now attempts to load `artifacts/intent/model.pkl` at startup. If the artifact is not available, the project falls back to heuristic intent detection.

## 2. Recommendation And Retrieval Training

### Purpose
This training step creates a retrieval artifact that helps the runtime:
- find similar known plan strategies
- reuse plan groups from similar examples
- reuse known risks from related plans
- suggest remediation based on similar failures

### Input Data
Datasets:
- `data/training/plans.jsonl`
- `data/training/failures.jsonl`

Plan records now support fields such as:
- `prompt`
- `plan_summary`
- `groups`
- `known_risks`
- `rollout_strategy`
- `dependency_pattern`
- `clarification_hints`

Failure records now support fields such as:
- `issue`
- `root_cause`
- `fix`
- `follow_up`
- `remediation_category`
- `plan_context`

### Current Training Logic
The retrieval trainer in `training/train_recommendation_model.py`:
1. loads plan and failure records
2. converts them into structured retrieval documents
3. builds TF-IDF vectors
4. saves a retrieval artifact containing both the vectorizer and the documents

### Training Script

```bash
python training/train_recommendation_model.py
```

### Output Files
- `artifacts/recommendations/metrics.json`
- `artifacts/recommendations/retrieval_index.pkl`

### Runtime Use
The runtime retrieval index can now load `retrieval_index.pkl` and use it to:
- adapt plan groups in the planner
- add retrieved risk suggestions
- reuse similar failure fixes in the recommendation layer

## 3. Clarification Dataset Foundation

### Purpose
Clarification data captures the cases where the system should ask questions before building a final plan.

### Dataset
- `data/training/clarifications.jsonl`

This dataset documents:
- the original request
- which fields were missing
- which questions should be asked
- example answers
- resolved intent and entities

### Current Use
This dataset is not yet directly consumed by a dedicated model. It currently acts as:
- a curation guide
- a regression reference
- a future training foundation for a smarter clarification policy

## 4. Optional MLflow Logging

If `mlflow` is installed, both training scripts log:
- parameters
- metrics
- artifacts

Local MLflow runs may appear under:
- `mlruns/`

## 5. Runtime Input And Output Flow

### Runtime input
The API receives:
- `POST /plans/from-text`
- `POST /plans/from-voice`
- `POST /plans/sessions/{session_id}/answer`

### Runtime output
The planner can now return either:
- a final `DeploymentPlan`
- or a clarification response with questions and a `session_id`

Generated plans are still stored in memory in the current version.

## 6. How The New Runtime Uses Training Results

The current version now reuses training artifacts in two ways:

### Intent artifact reuse
- runtime loads `artifacts/intent/model.pkl` if present
- otherwise it falls back to heuristic prediction

### Retrieval artifact reuse
- runtime loads `artifacts/recommendations/retrieval_index.pkl` if present
- retrieved plan examples can shape group selection
- retrieved failure examples can improve remediation suggestions

## 7. How Training Improves Dynamic Planning

### Better intent detection
More labeled intent rows help the system:
- recognize more wording styles
- reduce wrong intent guesses
- detect ambiguity more reliably

### Better clarification behavior
More clarification examples help define:
- when to ask questions
- which fields are essential
- how to recover from partially specified requests

### Better plan strategies
More plan examples help the system:
- choose better group layouts
- carry forward known risks
- handle rollout-specific strategies more realistically

### Better remediation
More failure examples improve:
- fix suggestions
- fallback guidance
- execution-time recommendations

## 8. Best Practices For Building Good Datasets

Good datasets should include:
- clear requests
- ambiguous requests
- incomplete requests
- corrected user answers after clarification
- production, staging, DR, rollback, and compliance scenarios
- successful and failed execution cases

Recommended dataset qualities:
- consistent labels
- realistic enterprise language
- enough variety in wording
- clear mapping from request to structured plan outcome

## 9. Short Flow Logic

1. user submits text or voice
2. runtime predicts intent and extracts entities
3. if confidence is low or important fields are missing, the system asks clarification questions
4. once enough data is available, the planner retrieves similar plan examples
5. the planner builds a structured plan using retrieved strategy plus safe fallback templates
6. dependency validation checks the final task graph
7. recommendations add known risks and failure guidance

## 10. Practical Summary

Short version:
- training data lives in `data/training/`
- training scripts live in `training/`
- trained outputs are saved in `artifacts/`
- runtime now reuses saved intent and retrieval artifacts when available
- clarification examples are part of the dataset foundation for future learning
