from __future__ import annotations

from fastapi import FastAPI

from src.api.routes.mock_execution import router as mock_execution_router
from src.api.routes.plans import router as plans_router


def create_app() -> FastAPI:
    app = FastAPI(
        title="AI Deployment Planner",
        description="Experimental API for voice and text driven deployment plan generation.",
        version="0.1.0",
    )

    @app.get("/health")
    def health() -> dict[str, str]:
        return {"status": "ok"}

    app.include_router(plans_router)
    app.include_router(mock_execution_router)
    return app


app = create_app()
