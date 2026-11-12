from fastapi import APIRouter, HTTPException
from fastapi.encoders import jsonable_encoder

from app.schemas.dataset import DatasetBuildRequest
from app.services.data_acquisition.service import build_dataset
from app.services.dataset_storage import (
    list_datasets,
    load_dataset,
)

router = APIRouter(
    prefix="/datasets",
    tags=["Datasets"],
)

@router.get("/")
def get_datasets():
    try:
        return {
            "status": "success",
            "datasets": list_datasets(),
        }

    except Exception as error:
        raise HTTPException(
            status_code=500,
            detail=str(error),
        )


@router.get("/{dataset_name}")
def get_dataset(dataset_name: str):
    try:
        dataset = load_dataset(dataset_name)

        return {
            "status": "success",
            "dataset_name": dataset_name,
            "columns": dataset.columns.tolist(),
            "row_count": len(dataset),
        }

    except ValueError as error:
        raise HTTPException(
            status_code=404,
            detail=str(error),
        )

@router.post("/build")
def build_dataset_endpoint(request: DatasetBuildRequest):
    try:
        result = build_dataset(request)

        return jsonable_encoder({
            "status": "success",
            "message": "Tạo và lưu Dataset thành công.",
            "dataset_name": result["dataset_name"],
            "dataset_path": result["dataset_path"],
            "builder_name": result["builder_name"],
            "validation_report": result["validation_report"],
        })

    except ValueError as error:
        raise HTTPException(
            status_code=400,
            detail=str(error),
        )