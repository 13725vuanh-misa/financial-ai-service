from typing import Any

from sklearn.pipeline import make_pipeline
from sklearn.preprocessing import StandardScaler

from app.components.algorithms.registry import ALGORITHM_REGISTRY


SCALING_ALGORITHMS = {
    "logistic_regression",
    "knn",
    "svm",
}


def create_algorithm_pipeline(
    algorithm_name: str,
    model_config: dict[str, Any] | None = None,
):
    definition = ALGORITHM_REGISTRY.get(algorithm_name)

    if definition is None:
        raise ValueError(
            f"Thuật toán không được hỗ trợ: {algorithm_name}"
        )

    model = definition.create_model(**(model_config or {}))

    if algorithm_name in SCALING_ALGORITHMS:
        return make_pipeline(StandardScaler(), model)

    return model
