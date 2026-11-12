import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import joblib
import numpy as np
import pandas as pd

from app.components.validators.base import ValidationReport
from app.schemas.evaluation import EvaluationRequest, FinalTrainingRequest
from app.services.local_ai import (
    evaluate_local_ai,
    train_selected_algorithms,
)


FEATURE_COLUMNS = [
    "return_1q",
    "volatility_1q",
    "log_avg_volume_1q",
    "price_to_ma20",
    "price_to_ma50",
    "vn_return_1q",
    "vn_volatility_1q",
    "relative_return_1q",
    "profit_growth_yoy",
    "asset_growth_yoy",
    "equity_growth_yoy",
    "roe_ttm_approx",
    "roa_ttm_approx",
    "debt_to_equity",
]


def make_dataset() -> pd.DataFrame:
    rows = []
    for period_index, period in enumerate(
        pd.period_range("2020Q1", periods=4, freq="Q")
    ):
        for sample_index, target in enumerate([0, 1, 0, 1]):
            row = {
                name: float(period_index + sample_index + feature_index / 10)
                for feature_index, name in enumerate(FEATURE_COLUMNS)
            }
            row.update({"quarter": period, "target": target})
            rows.append(row)

    return pd.DataFrame(rows)


class LocalAIWorkflowTests(unittest.TestCase):
    def setUp(self):
        self.dataset = make_dataset()
        self.metadata = {
            "builder_name": "quarterly_v2_case_a",
            "feature_columns": FEATURE_COLUMNS,
            "target_column": "target",
        }

    def test_evaluation_keeps_success_when_an_algorithm_fails(self):
        request = EvaluationRequest.model_validate({
            "dataset": {"source": "existing", "dataset_name": "sample"},
            "algorithms": {
                "decision_tree": {},
                "knn": {"n_neighbors": 99},
            },
            "metrics": ["accuracy"],
            "split": {
                "strategy": "walk_forward",
                "parameters": {
                    "min_train_size": 2,
                    "test_size": 1,
                    "step_size": 1,
                },
            },
        })

        with (
            patch(
                "app.services.local_ai.load_dataset",
                return_value=self.dataset,
            ),
            patch(
                "app.services.local_ai.load_dataset_metadata",
                return_value=self.metadata,
            ),
            self.assertLogs(
                "app.components.evaluation.evaluator",
                level="ERROR",
            ),
        ):
            result = evaluate_local_ai(request)

        self.assertEqual(result["status"], "partial_success")
        algorithms = {
            item["algorithm"]: item
            for item in result["evaluation"]["algorithms"]
        }
        self.assertEqual(algorithms["decision_tree"]["status"], "success")
        self.assertEqual(algorithms["knn"]["status"], "failed")
        self.assertTrue(algorithms["knn"]["errors"])

    def test_new_dataset_is_built_before_evaluation(self):
        request = EvaluationRequest.model_validate({
            "dataset": {
                "source": "new",
                "dataset_name": "new_sample",
                "builder_name": "quarterly_v2_case_a",
                "tickers": ["AAA"],
                "start_date": "2020-01-01",
                "end_date": "2022-01-01",
            },
            "algorithms": {"decision_tree": {}},
            "metrics": ["accuracy"],
            "split": {
                "strategy": "single_split",
                "parameters": {"train_size": 2},
            },
        })

        with (
            patch(
                "app.services.local_ai.build_dataset",
                return_value={
                    "dataset": self.dataset,
                    "dataset_name": "new_sample",
                    "validation_report": ValidationReport(),
                },
            ) as build_dataset,
            patch(
                "app.services.local_ai.load_dataset_metadata",
                return_value=self.metadata,
            ),
        ):
            result = evaluate_local_ai(request)

        build_dataset.assert_called_once()
        self.assertEqual(result["dataset"]["status"], "created")
        self.assertEqual(result["status"], "success")

    def test_dataset_build_failure_stops_evaluation(self):
        request = EvaluationRequest.model_validate({
            "dataset": {
                "source": "new",
                "dataset_name": "failed_sample",
                "builder_name": "quarterly_v2_case_a",
                "tickers": ["AAA"],
                "start_date": "2020-01-01",
                "end_date": "2022-01-01",
            },
            "algorithms": {"decision_tree": {}},
            "metrics": ["accuracy"],
        })

        with (
            patch(
                "app.services.local_ai.build_dataset",
                side_effect=ValueError("build failed"),
            ),
            patch("app.services.local_ai.run_evaluation") as run_evaluation,
        ):
            with self.assertRaisesRegex(ValueError, "build failed"):
                evaluate_local_ai(request)

        run_evaluation.assert_not_called()

    def test_final_training_saves_model_with_valid_rows_and_config(self):
        training_dataset = self.dataset.copy()
        training_dataset.loc[0, FEATURE_COLUMNS[0]] = np.inf
        training_dataset.loc[1, FEATURE_COLUMNS[0]] = np.nan
        request = FinalTrainingRequest.model_validate({
            "dataset_name": "sample",
            "algorithms": {"decision_tree": {"max_depth": 3}},
        })

        with tempfile.TemporaryDirectory() as temp_dir:
            with (
                patch(
                    "app.services.local_ai.load_dataset",
                    return_value=training_dataset,
                ),
                patch(
                    "app.services.local_ai.load_dataset_metadata",
                    return_value=self.metadata,
                ),
                patch(
                    "app.services.model_storage.MODELS_DIR",
                    Path(temp_dir),
                ),
            ):
                result = train_selected_algorithms(request)

            model_files = list(Path(temp_dir).glob("*.joblib"))
            self.assertEqual(result["status"], "success")
            self.assertEqual(result["training_rows"], len(self.dataset) - 2)
            self.assertEqual(result["excluded_rows"], 2)
            self.assertEqual(len(model_files), 1)

            artifact = joblib.load(model_files[0])
            self.assertEqual(
                artifact["metadata"]["algorithm_config"],
                {"max_depth": 3},
            )
            self.assertEqual(
                artifact["model"].get_params()["max_depth"],
                3,
            )
            self.assertEqual(
                artifact["metadata"]["training_rows"],
                len(self.dataset) - 2,
            )


if __name__ == "__main__":
    unittest.main()
