from pathlib import Path
import re

from app.config import DATASETS_DIR
from app.schemas.dataset import DatasetBuildRequest
from app.components.builders.registry import get_builder
from app.components.validators import validate_dataset

from app.services.data_acquisition.planner import create_fetch_plan
from app.services.data_acquisition.fetcher import fetch_data
from app.services.data_acquisition.market_processor import process_market_data
from app.services.data_acquisition.fundamental_processor import (
    process_fundamental_data,
)
from app.services.dataset_storage import save_dataset_metadata


def prepare_fetch_plan(request: DatasetBuildRequest):
    """
    Xác định các nguồn dữ liệu cần lấy dựa trên Builder.
    """

    builder = get_builder(request.builder_name)

    fetch_plan = create_fetch_plan(
        requirements=builder.data_requirements,
        tickers=request.tickers,
        start_date=request.start_date,
        end_date=request.end_date,
    )

    return {
        "builder_name": builder.name,
        "fetch_plan": fetch_plan,
    }


def acquire_data(request: DatasetBuildRequest):
    """
    Tạo Fetch Plan và lấy dữ liệu thô từ PostgreSQL.
    """

    result = prepare_fetch_plan(request)
    fetched_data = fetch_data(result["fetch_plan"])

    return {
        "builder_name": result["builder_name"],
        "fetch_plan": result["fetch_plan"],
        "market_df": fetched_data.get("market"),
        "vnindex_df": fetched_data.get("vnindex"),
        "fundamental_df": fetched_data.get("fundamental"),
    }


def save_dataset(dataset, dataset_name: str) -> Path:
    """
    Lưu Dataset vào thư mục storage/datasets.
    """

    # Chỉ cho phép tên file đơn giản, tránh truy cập ra ngoài thư mục.
    if not re.fullmatch(r"[\w.-]+", dataset_name):
        raise ValueError(
            "Tên Dataset chỉ được chứa chữ cái, chữ số, dấu gạch dưới, "
            "dấu gạch ngang và dấu chấm."
        )

    if dataset_name in {".", ".."}:
        raise ValueError("Tên Dataset không hợp lệ.")

    DATASETS_DIR.mkdir(parents=True, exist_ok=True)

    dataset_path = DATASETS_DIR / f"{dataset_name}.csv"

    # Không ghi đè Dataset đã tồn tại.
    if dataset_path.exists():
        raise ValueError(
            f"Dataset '{dataset_name}' đã tồn tại."
        )

    dataset.to_csv(dataset_path, index=False, encoding="utf-8-sig")

    return dataset_path


def build_dataset(request: DatasetBuildRequest):
    """
    Lấy dữ liệu, xử lý Features và Labels,
    tạo Dataset, kiểm tra và lưu Dataset.
    """

    # 1. Tìm Builder
    builder = get_builder(request.builder_name)

    # 2. Lấy dữ liệu thô
    acquisition_result = acquire_data(request)

    # 3. Xử lý dữ liệu Market
    market_df = process_market_data(
        market_df=acquisition_result["market_df"],
        vnindex_df=acquisition_result["vnindex_df"],
        start_date=request.start_date,
        end_date=request.end_date,
    )

    # 4. Xử lý dữ liệu Fundamental
    fundamental_df = process_fundamental_data(
        fundamental_df=acquisition_result["fundamental_df"],
        start_date=request.start_date,
        end_date=request.end_date,
    )

    # 5. Ghép dữ liệu theo quy tắc của Builder
    dataset = builder.build(
        market_df=market_df,
        fundamental_df=fundamental_df,
    )

    # 6. Kiểm tra Dataset
    validation_report = validate_dataset(dataset)

    if not validation_report.is_valid:
        error_messages = [
            issue.message
            for issue in validation_report.errors
        ]

        raise ValueError(
            "Dataset không hợp lệ: "
            + "; ".join(error_messages)
        )

    # 7. Lưu Dataset sau khi kiểm tra hợp lệ
    dataset_path = save_dataset(
        dataset=dataset,
        dataset_name=request.dataset_name,
    )

    save_dataset_metadata(
        request.dataset_name,
        {
            "builder_name": builder.name,
            "feature_columns": list(builder.feature_columns),
            "target_column": builder.target_column,
        },
    )

    # 8. Trả về kết quả
    return {
        "dataset_name": request.dataset_name,
        "dataset_path": str(dataset_path),
        "builder_name": builder.name,
        "fetch_plan": acquisition_result["fetch_plan"],
        "dataset": dataset,
        "validation_report": validation_report,
    }
