from fastapi import APIRouter

from app.api.endpoints import calculator, ping, todos

api_router = APIRouter(prefix="/api")

api_router.include_router(
    ping.router,
    tags=["ping"],
)

api_router.include_router(
    todos.router,
    tags=["todos"],
)

api_router.include_router(
    calculator.router,
    tags=["calculator"],
)
