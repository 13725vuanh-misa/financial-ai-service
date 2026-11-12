from fastapi import APIRouter
from app.schemas.common import HealthResponse

router = APIRouter()


@router.get("/")
def home():
    return {
        "message": "Financial AI Service is running!",
        "status": "OK",
    }


@router.get("/health", response_model=HealthResponse)
def health_check():
    return {
        "status": "UP",
        "service": "financial-ai-service",
    }