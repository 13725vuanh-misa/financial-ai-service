import numpy as np

from sklearn.dummy import DummyClassifier


def create_dummy(**params):
    """Khởi tạo Dummy Classifier."""

    default_params = {
        "strategy": "most_frequent",
    }

    default_params.update(params)

    return DummyClassifier(**default_params)


def predict_momentum(
    df,
    return_col="return_1q",
    threshold=0.0,
):
    """
    Dự đoán theo xu hướng Momentum.

    return > threshold: Tăng (1)
    return <= threshold: Không tăng (0)
    """

    if return_col not in df.columns:
        raise ValueError(
            f"Dataset không có cột {return_col}."
        )

    values = df[return_col]

    if values.isna().any() or not np.isfinite(values).all():
        raise ValueError(
            f"Cột {return_col} có giá trị thiếu hoặc không hợp lệ."
        )

    return (values > threshold).astype(int)