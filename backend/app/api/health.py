from fastapi import APIRouter

from app.core.config import get_settings
from app.db.session import check_database_connection
from app.schemas.health import DatabaseHealthResponse, HealthResponse

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    settings = get_settings()
    return HealthResponse(status="ok", service=settings.app_name, version=settings.app_version)


@router.get("/health/database", response_model=DatabaseHealthResponse)
def database_health() -> DatabaseHealthResponse:
    connected = check_database_connection()
    return DatabaseHealthResponse(
        status="ok" if connected else "unavailable",
        service="TalentScreen API",
        database="connected" if connected else "unavailable",
    )
