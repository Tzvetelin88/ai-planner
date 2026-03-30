from __future__ import annotations

from fastapi import APIRouter

from src.api.store import store
from src.models.schemas import ExecutionWarning, MockExecutionRequest, MockExecutionResponse


router = APIRouter(prefix="/mock", tags=["mock-execution"])


def _build_response(service: str, request: MockExecutionRequest) -> MockExecutionResponse:
    warning_list: list[ExecutionWarning] = []
    dependency_issues: list[str] = []
    remediation_suggestions: list[str] = []
    success = True

    lower_payload = " ".join(str(value).lower() for value in request.payload.values())
    if "timeout" in lower_payload or "fail" in lower_payload:
        success = False
        warning_list.append(ExecutionWarning(code="SIMULATED_FAILURE", message="The mock service encountered a simulated failure."))
        dependency_issues.append("Downstream platform response timeout")
        remediation_suggestions.extend(
            [
                "Retry the failed step after validating downstream availability.",
                "Review backup registration and platform connectivity before rerun.",
            ]
        )
    elif "warning" in lower_payload:
        warning_list.append(ExecutionWarning(code="SIMULATED_WARNING", message="The mock service returned a non-blocking warning."))

    response = MockExecutionResponse(
        success=success,
        service=service,
        resource_ids=[f"{service}-resource-001"],
        warnings=warning_list,
        dependency_issues=dependency_issues,
        remediation_suggestions=remediation_suggestions,
    )
    store.save_execution_result(request.plan_id, response)
    return response


@router.post("/inventory/validate", response_model=MockExecutionResponse)
def validate_inventory(request: MockExecutionRequest) -> MockExecutionResponse:
    return _build_response("inventory.validate", request)


@router.post("/config/generate", response_model=MockExecutionResponse)
def generate_config(request: MockExecutionRequest) -> MockExecutionResponse:
    return _build_response("config.generate", request)


@router.post("/provision/infra", response_model=MockExecutionResponse)
def provision_infra(request: MockExecutionRequest) -> MockExecutionResponse:
    return _build_response("provision.infra", request)


@router.post("/provision/platform", response_model=MockExecutionResponse)
def provision_platform(request: MockExecutionRequest) -> MockExecutionResponse:
    return _build_response("provision.platform", request)


@router.post("/backup/enable", response_model=MockExecutionResponse)
def enable_backup(request: MockExecutionRequest) -> MockExecutionResponse:
    return _build_response("backup.enable", request)


@router.post("/verify/health", response_model=MockExecutionResponse)
def verify_health(request: MockExecutionRequest) -> MockExecutionResponse:
    return _build_response("verify.health", request)


@router.post("/rollback/start", response_model=MockExecutionResponse)
def rollback_start(request: MockExecutionRequest) -> MockExecutionResponse:
    return _build_response("rollback.start", request)
