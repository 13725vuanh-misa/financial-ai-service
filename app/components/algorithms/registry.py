
from app.components.algorithms.base import AlgorithmDefinition

from app.components.algorithms.classification import (
    create_logistic_regression,
    create_decision_tree,
    create_random_forest,
    create_extra_trees,
    create_gradient_boosting,
    create_hist_gradient_boosting,
    create_knn,
    create_svm,
)


ALGORITHM_REGISTRY = {
    "logistic_regression": AlgorithmDefinition(
        name="logistic_regression",
        display_name="Logistic Regression",
        description="Phân loại dựa trên mô hình hồi quy logistic.",
        task_type="classification",
        create_model=create_logistic_regression,
    ),

    "decision_tree": AlgorithmDefinition(
        name="decision_tree",
        display_name="Decision Tree",
        description="Phân loại dựa trên cây quyết định.",
        task_type="classification",
        create_model=create_decision_tree,
    ),

    "random_forest": AlgorithmDefinition(
        name="random_forest",
        display_name="Random Forest",
        description="Kết hợp nhiều cây quyết định để phân loại.",
        task_type="classification",
        create_model=create_random_forest,
    ),

    "extra_trees": AlgorithmDefinition(
        name="extra_trees",
        display_name="Extra Trees",
        description="Kết hợp nhiều cây quyết định với cách chia ngẫu nhiên.",
        task_type="classification",
        create_model=create_extra_trees,
    ),

    "gradient_boosting": AlgorithmDefinition(
        name="gradient_boosting",
        display_name="Gradient Boosting",
        description="Huấn luyện tuần tự các mô hình để cải thiện dự đoán.",
        task_type="classification",
        create_model=create_gradient_boosting,
    ),

    "hist_gradient_boosting": AlgorithmDefinition(
        name="hist_gradient_boosting",
        display_name="Hist Gradient Boosting",
        description="Gradient Boosting sử dụng histogram để tối ưu quá trình học.",
        task_type="classification",
        create_model=create_hist_gradient_boosting,
    ),

    "knn": AlgorithmDefinition(
        name="knn",
        display_name="K-Nearest Neighbors",
        description="Phân loại dựa trên các mẫu dữ liệu gần nhất.",
        task_type="classification",
        create_model=create_knn,
    ),

    "svm": AlgorithmDefinition(
        name="svm",
        display_name="Support Vector Machine",
        description="Phân loại bằng cách tìm ranh giới phân tách tối ưu.",
        task_type="classification",
        create_model=create_svm,
    ),
}
