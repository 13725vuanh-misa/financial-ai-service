import json
from pathlib import Path

import pandas as pd

from app.config import BASE_DIR, DATASETS_DIR


BUNDLED_DATASETS_DIR = BASE_DIR / "app" / "datasets"


def _dataset_path(dataset_name: str, suffix: str) -> Path:
    if not dataset_name or Path(dataset_name).name != dataset_name:
        raise ValueError("Tên Dataset không hợp lệ.")

    return DATASETS_DIR / f"{dataset_name}{suffix}"


def save_dataset_metadata(
    dataset_name: str,
    metadata: dict,
) -> Path:
    metadata_path = _dataset_path(dataset_name, ".metadata.json")
    DATASETS_DIR.mkdir(parents=True, exist_ok=True)
    metadata_path.write_text(
        json.dumps(metadata, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )
    return metadata_path


def load_dataset_metadata(dataset_name: str) -> dict | None:
    metadata_path = _dataset_path(dataset_name, ".metadata.json")

    if not metadata_path.is_file():
        return None

    try:
        metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    except json.JSONDecodeError as error:
        raise ValueError(
            f"Metadata của Dataset '{dataset_name}' không hợp lệ."
        ) from error

    if not isinstance(metadata, dict):
        raise ValueError(
            f"Metadata của Dataset '{dataset_name}' không hợp lệ."
        )

    return metadata


def list_datasets() -> list[dict]:
    """
    Lấy danh sách Dataset đã lưu.
    """

    datasets_by_name = {}

    # Dataset do người dùng tạo được ưu tiên hơn Dataset đi kèm source.
    for datasets_dir in (BUNDLED_DATASETS_DIR, DATASETS_DIR):
        if not datasets_dir.exists():
            continue
        for file_path in datasets_dir.glob("*.csv"):
            datasets_by_name[file_path.stem] = {
                "dataset_name": file_path.stem,
                "file_name": file_path.name,
                "file_size": file_path.stat().st_size,
            }

    return [datasets_by_name[name] for name in sorted(datasets_by_name)]


def load_dataset(dataset_name: str) -> pd.DataFrame:
    """
    Đọc Dataset đã lưu theo tên.
    """

    storage_path = _dataset_path(dataset_name, ".csv")
    bundled_path = BUNDLED_DATASETS_DIR / storage_path.name
    dataset_path = storage_path if storage_path.is_file() else bundled_path

    if not dataset_path.is_file():
        raise ValueError(
            f"Không tìm thấy Dataset '{dataset_name}'."
        )

    dataset = pd.read_csv(
        dataset_path,
        encoding="utf-8-sig",
        parse_dates=["as_of", "bctc_available_date"],
    )

    # Khôi phục kiểu Period theo quý
    for column in ["quarter", "bctc_period"]:
        if column in dataset.columns:
            dataset[column] = pd.PeriodIndex(
                dataset[column],
                freq="Q",
            )

    return dataset
