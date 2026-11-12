from sklearn.metrics import (
    accuracy_score,
    balanced_accuracy_score,
    precision_score,
    recall_score,
    f1_score,
    roc_auc_score,
)


def calculate_classification_metrics(
    y_true,
    y_pred,
    y_score=None,
    zero_division=0,
):
    """
    Tính các chỉ số đánh giá bài toán phân loại nhị phân.

    Parameters:
        y_true: Nhãn thực tế.
        y_pred: Nhãn dự đoán (0 hoặc 1).
        y_score: Xác suất hoặc điểm dự đoán thuộc lớp 1.
        zero_division: Giá trị trả về khi phép tính Precision,
                       Recall hoặc F1 không xác định.
    """

    metrics = {
        "n": len(y_true),
        "accuracy": accuracy_score(y_true, y_pred),
        "balanced_accuracy": balanced_accuracy_score(
            y_true, y_pred
        ),
        "precision": precision_score(
            y_true, y_pred, zero_division=zero_division
        ),
        "recall": recall_score(
            y_true, y_pred, zero_division=zero_division
        ),
        "f1": f1_score(
            y_true, y_pred, zero_division=zero_division
        ),
        "auc": None,
    }

    # Chỉ tính AUC khi có điểm dự đoán
    # và dữ liệu thực tế có đủ hai lớp.
    if y_score is not None and len(set(y_true)) == 2:
        metrics["auc"] = roc_auc_score(y_true, y_score)

    return metrics
