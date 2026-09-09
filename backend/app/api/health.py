from fastapi import APIRouter

from app.core.config import get_settings
from app.db.session import check_database_connection
from app.schemas.health import DatabaseHealthResponse, HealthResponse, HealthV2Response

router = APIRouter(prefix="/api", tags=["system"])


@router.get("/health", response_model=HealthV2Response)
def health() -> HealthV2Response:
    settings = get_settings()
    connected = check_database_connection()
    return HealthV2Response(
        status="ok" if connected else "degraded",
        service=settings.app_name,
        version=settings.app_version,
        database="connected" if connected else "unavailable",
    )


@router.get("/health/database", response_model=DatabaseHealthResponse)
def database_health() -> DatabaseHealthResponse:
    connected = check_database_connection()
    return DatabaseHealthResponse(
        status="ok" if connected else "unavailable",
        service="TalentScreen API",
        database="connected" if connected else "unavailable",
    )
