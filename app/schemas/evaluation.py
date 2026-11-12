from typing import Any, Literal

from pydantic import BaseModel, Field

from app.schemas.dataset import DatasetSource


class SplitConfiguration(BaseModel):
    strategy: Literal[
        "walk_forward",
        "rolling_window",
        "single_split",
    ] = "walk_forward"
    parameters: dict[str, Any] = Field(default_factory=dict)


class EvaluationRequest(BaseModel):
    dataset: DatasetSource

    algorithms: dict[str, dict[str, Any]] = Field(
        min_length=1,
        description="Tên thuật toán và cấu hình tương ứng",
    )

    metrics: list[str] = Field(
        min_length=1,
        description="Danh sách Metrics muốn đánh giá",
    )

    split: SplitConfiguration = Field(default_factory=SplitConfiguration)


class FinalTrainingRequest(BaseModel):
    dataset_name: str = Field(
        min_length=1,
        description="Tên Dataset đã lưu",
    )
    algorithms: dict[str, dict[str, Any]] = Field(
        min_length=1,
        description="Các thuật toán được chọn và cấu hình tương ứng",
    )


class DatasetEvaluationInfo(BaseModel):
    dataset_name: str
    source: Literal["existing", "new"]
    status: Literal["reused", "created"]
    builder_name: str | None
    row_count: int
    feature_columns: list[str]
    target_column: str
    validation_report: dict[str, Any] | None = None


class AlgorithmEvaluationResult(BaseModel):
    algorithm: str
    status: Literal["success", "partial_success", "failed"]
    config: dict[str, Any]
    split_count: int
    metrics: dict[str, float | None]
    splits: list[dict[str, Any]]
    errors: list[dict[str, Any]]


class EvaluationResponse(BaseModel):
    status: Literal["success", "partial_success", "failed"]
    dataset: DatasetEvaluationInfo
    evaluation: dict[str, Any]


class ModelTrainingResult(BaseModel):
    algorithm: str
    status: Literal["success", "failed"]
    config: dict[str, Any] | None = None
    model_id: str | None = None
    file_name: str | None = None
    dataset_name: str | None = None
    algorithm_config: dict[str, Any] | None = None
    training_rows: int | None = None
    error: str | None = None


class FinalTrainingResponse(BaseModel):
    status: Literal["success", "partial_success", "failed"]
    dataset_name: str
    training_rows: int
    excluded_rows: int
    models: list[ModelTrainingResult]
