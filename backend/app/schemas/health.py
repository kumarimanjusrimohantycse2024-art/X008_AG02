from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str
    service: str
    version: str


class DatabaseHealthResponse(BaseModel):
    status: str
    service: str
    database: str
