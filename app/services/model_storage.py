from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from uuid import uuid4

import joblib

from app.config import MODELS_DIR


def save_model(
    model: Any,
    dataset_name: str,
    algorithm_name: str,
    model_config: dict[str, Any],
    feature_columns: list[str],
    target_column: str,
    training_rows: int,
) -> dict[str, Any]:
    model_id = f"{algorithm_name}_{uuid4().hex}"
    model_path = MODELS_DIR / f"{model_id}.joblib"
    temporary_path = MODELS_DIR / f".{model_id}.tmp"

    artifact = {
        "model": model,
        "metadata": {
            "model_id": model_id,
            "dataset_name": dataset_name,
            "algorithm": algorithm_name,
            "algorithm_config": model_config,
            "feature_columns": feature_columns,
            "target_column": target_column,
            "training_rows": training_rows,
            "created_at": datetime.now(timezone.utc).isoformat(),
        },
    }

    MODELS_DIR.mkdir(parents=True, exist_ok=True)

    try:
        joblib.dump(artifact, temporary_path)
        temporary_path.replace(model_path)
    except Exception:
        if temporary_path.exists():
            temporary_path.unlink()
        raise

    return {
        "model_id": model_id,
        "file_name": Path(model_path).name,
        "dataset_name": dataset_name,
        "algorithm": algorithm_name,
        "algorithm_config": model_config,
        "training_rows": training_rows,
    }
