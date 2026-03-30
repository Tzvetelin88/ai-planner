# Changelog

## v0.2.0

### New
- Added clarification-first planning flow for ambiguous or incomplete requests.
- Added planning sessions so the API can ask questions before finalizing a plan.
- Added runtime loading of trained intent artifacts from `artifacts/intent/model.pkl`.
- Added retrieval-backed adaptive planning using similar plan examples.
- Added retrieval-backed failure recommendations on top of troubleshooting markdown lookup.
- Added `ADVANCED_SAMPLES.md` for dynamic and clarification-heavy scenarios.
- Added clarification-oriented training data in `data/training/clarifications.jsonl`.
- Added structured retrieval artifacts that keep plan and failure records, not only raw text.

### Changed
- The planner is now a hybrid system: deterministic fallback plus adaptive retrieval-guided strategy selection.
- `POST /plans/from-text` and `POST /plans/from-voice` can now return either a final plan or a clarification response.
- Added `POST /plans/sessions/{session_id}/answer` to continue a planning session.
- Updated documentation to explain runtime learning, clarification flow, and advanced usage.
- Bumped application and package version to `0.2.0`.

### Notes
- Fully generative planning is still a future phase.
- The current version keeps schema and DAG validation as the safety boundary around dynamic planning.

## v0.1.0

### Initial version
- Added voice/text-driven plan generation API.
- Added deterministic group/task templates.
- Added mock execution APIs.
- Added baseline training scripts for intent classification and recommendation retrieval.
- Added sample datasets, tests, and quick-run scripts.
