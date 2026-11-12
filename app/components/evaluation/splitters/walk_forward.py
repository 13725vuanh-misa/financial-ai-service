from app.components.evaluation.base import (
    get_sorted_periods,
    create_split,
)


def walk_forward_split(
    df,
    time_col="quarter",
    min_train_size=8,
    test_size=1,
    step_size=1,
):
    """
    Chia dữ liệu theo phương pháp Walk Forward.

    Tập Train mở rộng dần theo thời gian.
    """

    if min_train_size < 1 or test_size < 1 or step_size < 1:
        raise ValueError("Các tham số chia tập phải lớn hơn 0.")

    periods = get_sorted_periods(df, time_col)

    if len(periods) < min_train_size + test_size:
        raise ValueError("Không đủ dữ liệu để chia Train/Test.")

    splits = []

    test_start = min_train_size

    while test_start + test_size <= len(periods):
        train_periods = periods[:test_start]

        test_periods = periods[
            test_start:test_start + test_size
        ]

        split = create_split(
            df,
            time_col,
            train_periods,
            test_periods,
        )

        splits.append(split)

        test_start += step_size

    return splits