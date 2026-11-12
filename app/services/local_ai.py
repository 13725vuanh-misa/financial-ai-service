import logging
from typing import Any

import numpy as np
import pandas as pd

from app.components.algorithms import ALGORITHM_REGISTRY
from app.components.algorithms.factory import create_algorithm_pipeline
from app.components.builders.registry import BUILDER_REGISTRY, get_builder
from app.components.evaluation import run_evaluation
from app.components.evaluation.evaluator import AVAILABLE_METRICS
from app.schemas.dataset import (
    ExistingDatasetRequest,
    NewDatasetRequest,
    DatasetBuildRequest,
)
from app.schemas.evaluation import EvaluationRequest, FinalTrainingRequest
from app.services.data_acquisition.service import build_dataset
from app.services.dataset_storage import (
    load_dataset,
    load_dataset_metadata,
)
from app.services.model_storage import save_model


logger = logging.getLogger(__name__)


def _resolve_model_metadata(
    dataset_name: str,
    dataset: pd.DataFrame,
) -> dict[str, Any]:
    metadata = load_dataset_metadata(dataset_name)

    if metadata is None:
        candidates = []
        for builder_name in BUILDER_REGISTRY:
            builder = get_builder(builder_name)
            feature_columns = list(builder.feature_columns)
            target_column = builder.target_column

            if (
                feature_columns
                and target_column in dataset.columns
                and set(feature_columns).issubset(dataset.columns)
            ):
                candidates.append({
                    "builder_name": builder.name,
                    "feature_columns": feature_columns,
                    "target_column": target_column,
                })

        unique_layouts = {
            (tuple(item["feature_columns"]), item["target_column"])
            for item in candidates
        }
        if len(unique_layouts) != 1:
            raise ValueError(
                f"Dataset '{dataset_name}' chưa có metadata Feature "
                "và Backend không thể xác định duy nhất cấu trúc."
            )

        metadata = candidates[0]

    feature_columns = metadata.get("feature_columns")
    target_column = metadata.get("target_column")

    if (
        not isinstance(feature_columns, list)
        or not feature_columns
        or not all(isinstance(column, str) for column in feature_columns)
        or not isinstance(target_column, str)
    ):
        raise ValueError(
            f"Metadata của Dataset '{dataset_name}' thiếu cấu hình Feature."
        )

    missing_columns = (
        set(feature_columns) | {target_column}
    ) - set(dataset.columns)
    if missing_columns:
        raise ValueError(
            f"Dataset '{dataset_name}' thiếu các cột: "
            f"{sorted(missing_columns)}"
        )

    return {
        "builder_name": metadata.get("builder_name"),
        "feature_columns": feature_columns,
        "target_column": target_column,
    }


def _serialize_evaluation_results(
    result_frame: pd.DataFrame,
    request: EvaluationRequest,
) -> list[dict[str, Any]]:
    result_rows = result_frame.to_dict(orient="records")
    algorithm_results = []

    for algorithm_name, model_config in request.algorithms.items():
        rows = [
            row for row in result_rows
            if row["algorithm"] == algorithm_name
        ]
        successful_splits = [
            row for row in rows
            if row["status"] == "success"
        ]
        failed_splits = [
            {
                "split": row.get("split"),
                "error": row.get("error"),
            }
            for row in rows
            if row["status"] == "error"
        ]

        metrics = {}
        for metric in request.metrics:
            values = [
                row[metric]
                for row in successful_splits
                if row.get(metric) is not None
                and not pd.isna(row[metric])
            ]
            metrics[metric] = (
                float(np.mean(values)) if values else None
            )

        if successful_splits and failed_splits:
            status = "partial_success"
        elif successful_splits:
            status = "success"
        else:
            status = "failed"

        algorithm_results.append({
            "algorithm": algorithm_name,
            "status": status,
            "config": model_config,
            "split_count": len(successful_splits),
            "metrics": metrics,
            "splits": successful_splits,
            "errors": failed_splits,
        })

    return algorithm_results


def evaluate_local_ai(request: EvaluationRequest) -> dict[str, Any]:
    invalid_algorithms = set(request.algorithms) - set(ALGORITHM_REGISTRY)
    if invalid_algorithms:
        raise ValueError(
            f"Thuật toán không được hỗ trợ: "
            f"{sorted(invalid_algorithms)}"
        )

    invalid_metrics = set(request.metrics) - AVAILABLE_METRICS
    if invalid_metrics:
        raise ValueError(
            f"Metrics không được hỗ trợ: {sorted(invalid_metrics)}"
        )

    if "strategy" in request.split.parameters:
        raise ValueError(
            "strategy phải được truyền riêng trong cấu hình split."
        )

    dataset_source = request.dataset
    validation_report = None

    if isinstance(dataset_source, ExistingDatasetRequest):
        dataset = load_dataset(dataset_source.dataset_name)
        dataset_name = dataset_source.dataset_name
        dataset_status = "reused"
    elif isinstance(dataset_source, NewDatasetRequest):
        build_request = DatasetBuildRequest(
            **dataset_source.model_dump(exclude={"source"})
        )
        build_result = build_dataset(build_request)
        dataset = build_result["dataset"]
        dataset_name = build_result["dataset_name"]
        dataset_status = "created"
        validation_report = build_result["validation_report"]
    else:
        raise ValueError("Nguồn Dataset không được hỗ trợ.")

    model_metadata = _resolve_model_metadata(dataset_name, dataset)
    split_config = {
        "strategy": request.split.strategy,
        **request.split.parameters,
    }
    results_frame = run_evaluation(
        df=dataset,
        feature_cols=model_metadata["feature_columns"],
        algorithms=request.algorithms,
        metrics=request.metrics,
        evaluation_config=split_config,
        target_col=model_metadata["target_column"],
    )
    algorithm_results = _serialize_evaluation_results(
        results_frame,
        request,
    )

    successful_count = sum(
        result["status"] in {"success", "partial_success"}
        for result in algorithm_results
    )
    if successful_count == len(algorithm_results):
        evaluation_status = "success"
    elif successful_count:
        evaluation_status = "partial_success"
    else:
        evaluation_status = "failed"

    dataset_info = {
        "dataset_name": dataset_name,
        "source": dataset_source.source,
        "status": dataset_status,
        "builder_name": model_metadata["builder_name"],
        "row_count": len(dataset),
        "feature_columns": model_metadata["feature_columns"],
        "target_column": model_metadata["target_column"],
    }
    if validation_report is not None:
        dataset_info["validation_report"] = validation_report

    return {
        "status": evaluation_status,
        "dataset": dataset_info,
        "evaluation": {
            "status": evaluation_status,
            "split": {
                "strategy": request.split.strategy,
                "parameters": request.split.parameters,
            },
            "metrics": request.metrics,
            "algorithms": algorithm_results,
        },
    }


def _prepare_training_data(
    dataset: pd.DataFrame,
    feature_columns: list[str],
    target_column: str,
) -> tuple[pd.DataFrame, pd.Series, int]:
    features = dataset[feature_columns].apply(
        pd.to_numeric,
        errors="coerce",
    )
    target = pd.to_numeric(dataset[target_column], errors="coerce")

    valid_rows = features.notna().all(axis=1) & target.notna()
    valid_rows &= np.isfinite(features.to_numpy(dtype=float)).all(axis=1)
    valid_rows &= np.isfinite(target.to_numpy(dtype=float))

    clean_features = features.loc[valid_rows]
    clean_target = target.loc[valid_rows]
    if clean_features.empty:
        raise ValueError("Dataset không có dòng hợp lệ để huấn luyện.")

    return (
        clean_features,
        clean_target,
        int((~valid_rows).sum()),
    )


def train_selected_algorithms(
    request: FinalTrainingRequest,
) -> dict[str, Any]:
    invalid_algorithms = set(request.algorithms) - set(ALGORITHM_REGISTRY)
    if invalid_algorithms:
        raise ValueError(
            f"Thuật toán không được hỗ trợ: "
            f"{sorted(invalid_algorithms)}"
        )

    dataset = load_dataset(request.dataset_name)
    model_metadata = _resolve_model_metadata(
        request.dataset_name,
        dataset,
    )
    features, target, excluded_rows = _prepare_training_data(
        dataset,
        model_metadata["feature_columns"],
        model_metadata["target_column"],
    )

    results = []
    for algorithm_name, model_config in request.algorithms.items():
        try:
            model = create_algorithm_pipeline(
                algorithm_name,
                model_config,
            )
            model.fit(features, target)
            model_info = save_model(
                model=model,
                dataset_name=request.dataset_name,
                algorithm_name=algorithm_name,
                model_config=model_config,
                feature_columns=model_metadata["feature_columns"],
                target_column=model_metadata["target_column"],
                training_rows=len(features),
            )
            results.append({
                "algorithm": algorithm_name,
                "status": "success",
                **model_info,
            })
        except Exception as error:
            logger.exception(
                "Huấn luyện cuối cùng cho thuật toán %s thất bại",
                algorithm_name,
            )
            results.append({
                "algorithm": algorithm_name,
                "status": "failed",
                "config": model_config,
                "error": str(error),
            })

    successful_count = sum(
        result["status"] == "success" for result in results
    )
    if successful_count == len(results):
        status = "success"
    elif successful_count:
        status = "partial_success"
    else:
        status = "failed"

    return {
        "status": status,
        "dataset_name": request.dataset_name,
        "training_rows": len(features),
        "excluded_rows": excluded_rows,
        "models": results,
    }
