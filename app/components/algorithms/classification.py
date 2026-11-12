
from sklearn.linear_model import LogisticRegression
from sklearn.tree import DecisionTreeClassifier
from sklearn.ensemble import (
    RandomForestClassifier,
    ExtraTreesClassifier,
    GradientBoostingClassifier,
    HistGradientBoostingClassifier,
)
from sklearn.neighbors import KNeighborsClassifier
from sklearn.svm import SVC


def _create_model(estimator_class, default_params, algorithm_name, params):
    """Khởi tạo model và kiểm tra cấu hình."""

    supported_params = estimator_class().get_params()

    invalid_params = set(params) - set(supported_params)

    if invalid_params:
        raise ValueError(
            f"{algorithm_name} không hỗ trợ tham số: "
            f"{sorted(invalid_params)}"
        )

    config = {
        **default_params,
        **params,
    }

    try:
        model = estimator_class(**config)

        if hasattr(model, "_validate_params"):
            model._validate_params()

        return model

    except (TypeError, ValueError) as error:
        raise ValueError(
            f"Cấu hình {algorithm_name} không hợp lệ: {error}"
        ) from error


def create_logistic_regression(**params):
    default_params = {
        "max_iter": 1000,
        "class_weight": "balanced",
        "random_state": 42,
    }

    return _create_model(
        LogisticRegression, default_params,
        "Logistic Regression", params
    )


def create_decision_tree(**params):
    default_params = {
        "class_weight": "balanced",
        "random_state": 42,
    }

    return _create_model(
        DecisionTreeClassifier, default_params,
        "Decision Tree", params
    )


def create_random_forest(**params):
    default_params = {
        "n_estimators": 200,
        "class_weight": "balanced",
        "random_state": 42,
        "n_jobs": -1,
    }

    return _create_model(
        RandomForestClassifier, default_params,
        "Random Forest", params
    )


def create_extra_trees(**params):
    default_params = {
        "n_estimators": 200,
        "class_weight": "balanced",
        "random_state": 42,
        "n_jobs": -1,
    }

    return _create_model(
        ExtraTreesClassifier, default_params,
        "Extra Trees", params
    )


def create_gradient_boosting(**params):
    default_params = {
        "n_estimators": 100,
        "learning_rate": 0.1,
        "max_depth": 3,
        "random_state": 42,
    }

    return _create_model(
        GradientBoostingClassifier, default_params,
        "Gradient Boosting", params
    )


def create_hist_gradient_boosting(**params):
    default_params = {
        "max_iter": 100,
        "learning_rate": 0.1,
        "max_leaf_nodes": 15,
        "random_state": 42,
    }

    return _create_model(
        HistGradientBoostingClassifier, default_params,
        "Hist Gradient Boosting", params
    )


def create_knn(**params):
    default_params = {
        "n_neighbors": 5,
        "weights": "distance",
        "n_jobs": -1,
    }

    return _create_model(
        KNeighborsClassifier, default_params,
        "K-Nearest Neighbors", params
    )


def create_svm(**params):
    default_params = {
        "C": 1.0,
        "kernel": "rbf",
        "class_weight": "balanced",
        "probability": True,
        "random_state": 42,
    }

    return _create_model(
        SVC, default_params,
        "Support Vector Machine", params
    )
