# Technology Stack

This document lists the planned and currently used technologies for `AI Deployment Planner` and the role each one plays in the system.

## Primary Language

### Python
Main language for backend development, AI/ML pipelines, NLP, speech handling, API development, testing, and training workflows.

## Backend and API

### FastAPI
Used for:
- REST API endpoints
- text and voice submission endpoints
- plan generation endpoints
- mocked downstream execution APIs
- API documentation through OpenAPI/Swagger

### Pydantic
Used for:
- request and response validation
- plan JSON schemas
- task, group, dependency, risk, and rollback models
- consistent typed data exchange across the system

### SQLite
Planned for:
- local storage of requests
- generated plans
- execution outcomes
- user feedback
- lightweight training data persistence

### SQLModel
Optional helper layer for working with SQLite using typed Python models.

## AI / ML Frameworks

### PyTorch
Primary ML framework planned for:
- custom intent classification
- recommendation model training
- future fine-tuning experiments

### transformers
Planned for:
- transformer-based NLP models
- intent classification
- later custom model fine-tuning

### sentence-transformers
Planned for:
- text embeddings
- semantic similarity
- retrieval support
- intent matching improvements
- recommendation relevance

### scikit-learn
Currently used for:
- baseline classifiers
- training utilities
- train/test split
- evaluation metrics
- confusion matrices

## NLP and Understanding

### spaCy
Planned for:
- entity extraction
- normalization of deployment parameters
- rules plus NLP hybrid parsing

Examples of extracted entities:
- environment
- region
- cluster size
- monitoring enabled
- backup enabled
- rollback required
- compliance requirements

## Voice and Speech

### faster-whisper
Primary speech-to-text option for:
- local voice transcription
- high-quality offline voice input

### Vosk
Optional lightweight alternative for:
- lower-resource local speech recognition
- fallback voice processing

## Planning and Workflow Modeling

### NetworkX
Used for:
- task dependency graphs
- execution ordering
- validation of plan structure
- modeling flow between task groups

## Recommendation and Troubleshooting

### FAISS
Planned for:
- local vector search
- retrieval of similar plans, issues, and fixes

### Chroma
Alternative to FAISS for:
- local vector storage
- troubleshooting and recommendation retrieval

One of `FAISS` or `Chroma` is expected to be used depending on project preference and setup simplicity.

## Training and MLOps

### MLflow
Used for:
- experiment tracking
- metric logging
- model versioning
- comparison of intent and recommendation models

## Testing and Mocking

### pytest
Used for:
- unit tests
- API tests
- planner validation tests

### httpx
Used for:
- API client testing
- async request testing for FastAPI endpoints

### respx
Planned for:
- mocking external or internal HTTP calls in tests
- isolating execution flow tests

## Tooling and Development

### Git
Version control for the project.

### pip
Used for Python package installation and environment setup.

### Docker
Optional later addition for:
- local reproducible setup
- demo packaging
- deployment-ready containerization

## Planned System Capabilities Mapped to Technologies

### Voice to execution plan
- `faster-whisper` or `Vosk`
- `FastAPI`
- `Pydantic`

### Intent recognition
- `PyTorch`
- `transformers`
- `sentence-transformers`
- `scikit-learn`

### Entity extraction
- `spaCy`
- `Pydantic`

### Plan generation
- `FastAPI`
- `Pydantic`
- `NetworkX`

### Mock execution APIs
- `FastAPI`
- `httpx`
- `respx`

### Recommendations and failure fixes
- `sentence-transformers`
- `FAISS` or `Chroma`
- `PyTorch`

### Model training and evaluation
- `PyTorch`
- `scikit-learn`
- `MLflow`

## Short Resume-Friendly Stack

`Python, FastAPI, PyTorch, Transformers, Sentence-Transformers, spaCy, faster-whisper, Pydantic, SQLite, NetworkX, FAISS/Chroma, MLflow, pytest`

## Notes

- This stack is intentionally local-first and portfolio-friendly.
- The current version uses deterministic plan generation plus baseline ML training scripts.
- Custom model loading and persistent runtime storage can be layered in after the core workflow is working end to end.
