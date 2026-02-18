from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


class AddRequest(BaseModel):
    """Request model for add endpoint."""

    a: float
    b: float


class AddResponse(BaseModel):
    """Response model for add endpoint."""

    result: float


@router.post("/calculator/add")
def add(request: AddRequest) -> AddResponse:
    return AddResponse(result=request.a + request.b)
