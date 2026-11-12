from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class DataSplit:
    """Thông tin một lượt chia Train/Test."""

    train_positions: tuple[int, ...]
    test_positions: tuple[int, ...]
    train_periods: tuple[Any, ...]
    test_periods: tuple[Any, ...]


def get_sorted_periods(df, time_col):
    """Lấy danh sách các kỳ dữ liệu theo thứ tự thời gian."""

    if time_col not in df.columns:
        raise ValueError(f"Không tìm thấy cột thời gian: {time_col}")

    if df[time_col].isna().any():
        raise ValueError(f"Cột {time_col} có giá trị bị thiếu.")

    periods = (
        df[time_col]
        .drop_duplicates()
        .sort_values()
        .tolist()
    )

    if not periods:
        raise ValueError("Dataset không có dữ liệu.")

    return periods


def create_split(df, time_col, train_periods, test_periods):
    """Tạo một lượt chia dựa trên danh sách kỳ Train/Test."""

    train_mask = df[time_col].isin(train_periods)
    test_mask = df[time_col].isin(test_periods)

    train_positions = tuple(
        train_mask.to_numpy().nonzero()[0].tolist()
    )

    test_positions = tuple(
        test_mask.to_numpy().nonzero()[0].tolist()
    )

    return DataSplit(
        train_positions=train_positions,
        test_positions=test_positions,
        train_periods=tuple(train_periods),
        test_periods=tuple(test_periods),
    )