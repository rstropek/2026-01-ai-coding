from fastapi import APIRouter

from app.api.endpoints import ping

api_router = APIRouter(prefix="/api")

api_router.include_router(
    ping.router,
    tags=["ping"],
)