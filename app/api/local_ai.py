from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.schemas.evaluation import (
    EvaluationRequest,
    EvaluationResponse,
    FinalTrainingRequest,
    FinalTrainingResponse,
)
from app.services.local_ai import (
    evaluate_local_ai,
    train_selected_algorithms,
)


router = APIRouter(
    prefix="/local-ai",
    tags=["Local AI"],
)


@router.post("/evaluations", response_model=EvaluationResponse)
def evaluate_algorithms(request: EvaluationRequest):
    try:
        return jsonable_encoder(evaluate_local_ai(request))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error


@router.post("/train", response_model=FinalTrainingResponse)
def train_selected_models(request: FinalTrainingRequest):
    try:
        return jsonable_encoder(train_selected_algorithms(request))
    except ValueError as error:
        raise HTTPException(status_code=400, detail=str(error)) from error
