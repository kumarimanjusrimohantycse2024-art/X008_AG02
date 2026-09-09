import logging

from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from app.api.admin import router as admin_router
from app.api.applications import router as applications_router
from app.api.auth import router as auth_router
from app.api.health import router as health_router
from app.api.jobs import router as jobs_router
from app.core.config import get_settings

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("talentscreen")
settings = get_settings()

app = FastAPI(title=settings.app_name, version=settings.app_version)
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["GET", "POST", "PATCH", "PUT", "OPTIONS"],
    allow_headers=["*"],
)


@app.exception_handler(Exception)
async def handle_unexpected_error(request: Request, exc: Exception) -> JSONResponse:
    logger.exception("Unhandled application error on %s", request.url.path)
    return JSONResponse(status_code=500, content={"detail": "An internal server error occurred."})


@app.get("/", tags=["system"])
def root() -> dict[str, str]:
    return {"service": settings.app_name, "version": settings.app_version, "status": "ready"}


app.include_router(health_router)
app.include_router(auth_router)
app.include_router(admin_router)
app.include_router(jobs_router)
app.include_router(applications_router)
