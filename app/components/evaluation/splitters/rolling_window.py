
from app.components.evaluation.base import (
    get_sorted_periods,
    create_split,
)


def rolling_window_split(
    df,
    time_col="quarter",
    train_size=8,
    test_size=1,
    step_size=1,
):
    """
    Chia dữ liệu theo phương pháp Rolling Window.

    Kích thước tập Train cố định và trượt dần theo thời gian.
    """

    if train_size < 1 or test_size < 1 or step_size < 1:
        raise ValueError("Các tham số chia tập phải lớn hơn 0.")

    periods = get_sorted_periods(df, time_col)

    if len(periods) < train_size + test_size:
        raise ValueError("Không đủ dữ liệu để chia Train/Test.")

    splits = []

    train_start = 0

    while train_start + train_size + test_size <= len(periods):
        train_periods = periods[
            train_start:train_start + train_size
        ]

        test_periods = periods[
            train_start + train_size:
            train_start + train_size + test_size
        ]

        split = create_split(
            df,
            time_col,
            train_periods,
            test_periods,
        )

        splits.append(split)

        train_start += step_size

    return splits
