import logging

import pandas as pd

from app.components.algorithms import ALGORITHM_REGISTRY
from app.components.algorithms.factory import create_algorithm_pipeline
from app.components.metrics import calculate_classification_metrics

from app.components.evaluation.splitters import (
    walk_forward_split,
    rolling_window_split,
    single_split,
)


SPLITTER_REGISTRY = {
    "walk_forward": walk_forward_split,
    "rolling_window": rolling_window_split,
    "single_split": single_split,
}

logger = logging.getLogger(__name__)

AVAILABLE_METRICS = {
    "accuracy",
    "balanced_accuracy",
    "precision",
    "recall",
    "f1",
    "auc",
}


def run_evaluation(
    df,
    feature_cols,
    algorithms,
    metrics,
    evaluation_config,
    target_col="target",
):
    """
    Chạy đánh giá nhiều thuật toán trên cùng một dataset.

    Mỗi thuật toán sử dụng cùng các lượt Train/Test.
    """

    # 1. Kiểm tra cấu hình Metrics
    invalid_metrics = set(metrics) - AVAILABLE_METRICS

    if invalid_metrics:
        raise ValueError(
            f"Metrics không được hỗ trợ: {sorted(invalid_metrics)}"
        )

    if not metrics:
        raise ValueError("Phải chọn ít nhất một Metric.")

    # 2. Kiểm tra cột dữ liệu
    required_columns = set(feature_cols) | {target_col}

    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Dataset thiếu các cột: {sorted(missing_columns)}"
        )

    if not feature_cols:
        raise ValueError("Dataset không có Feature để đánh giá.")

    if df[feature_cols + [target_col]].isna().any().any():
        raise ValueError(
            "Dataset có giá trị thiếu trong Feature hoặc Target."
        )

    # 3. Lấy cấu hình chia tập
    config = evaluation_config.copy()

    strategy = config.pop("strategy", "walk_forward")

    if strategy not in SPLITTER_REGISTRY:
        raise ValueError(
            f"Phương pháp chia tập không được hỗ trợ: {strategy}"
        )

    splitter = SPLITTER_REGISTRY[strategy]

    try:
        splits = splitter(df, **config)
    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Cấu hình chia tập không hợp lệ: {error}"
        ) from error

    # 4. Kiểm tra danh sách thuật toán
    if not algorithms:
        raise ValueError("Phải chọn ít nhất một thuật toán.")

    invalid_algorithms = set(algorithms) - set(ALGORITHM_REGISTRY)

    if invalid_algorithms:
        raise ValueError(
            f"Thuật toán không được hỗ trợ: "
            f"{sorted(invalid_algorithms)}"
        )

    # 5. Chạy từng thuật toán trên cùng các lượt chia
    results = []

    for algorithm_name, model_config in algorithms.items():
        for split_index, split in enumerate(splits, start=1):
            try:
                train_df = df.iloc[list(split.train_positions)]
                test_df = df.iloc[list(split.test_positions)]

                X_train = train_df[feature_cols]
                y_train = train_df[target_col]
                X_test = test_df[feature_cols]
                y_test = test_df[target_col]

                model = create_algorithm_pipeline(
                    algorithm_name,
                    model_config,
                )

                model.fit(X_train, y_train)
                y_pred = model.predict(X_test)

                y_score = None
                if hasattr(model, "predict_proba"):
                    y_score = model.predict_proba(X_test)[:, 1]

                calculated_metrics = calculate_classification_metrics(
                    y_true=y_test,
                    y_pred=y_pred,
                    y_score=y_score,
                )
                selected_metrics = {
                    name: calculated_metrics[name]
                    for name in metrics
                }

                results.append({
                    "algorithm": algorithm_name,
                    "status": "success",
                    "split": split_index,
                    "train_periods": [
                        str(period) for period in split.train_periods
                    ],
                    "test_periods": [
                        str(period) for period in split.test_periods
                    ],
                    "n_train": len(train_df),
                    "n_test": len(test_df),
                    **selected_metrics,
                })
            except Exception as error:
                logger.exception(
                    "Đánh giá thuật toán %s thất bại ở lượt chia %s",
                    algorithm_name,
                    split_index,
                )
                results.append({
                    "algorithm": algorithm_name,
                    "status": "error",
                    "split": split_index,
                    "error": str(error),
                })

    return pd.DataFrame(results)
