from app.components.evaluation.base import (
    get_sorted_periods,
    create_split,
)


def single_split(
    df,
    time_col="quarter",
    train_size=9,
    test_size=None,
):
    """
    Chia dữ liệu một lần theo thứ tự thời gian.

    Train lấy các kỳ đầu tiên.
    Test lấy các kỳ tiếp theo.
    """

    if train_size < 1:
        raise ValueError("train_size phải lớn hơn 0.")

    periods = get_sorted_periods(df, time_col)

    if train_size >= len(periods):
        raise ValueError("Không đủ dữ liệu để tạo tập Test.")

    if test_size is None:
        test_size = len(periods) - train_size

    if test_size < 1:
        raise ValueError("test_size phải lớn hơn 0.")

    if train_size + test_size > len(periods):
        raise ValueError("Tổng Train và Test vượt quá số kỳ dữ liệu.")

    train_periods = periods[:train_size]
    test_periods = periods[
        train_size:train_size + test_size
    ]

    return [
        create_split(
            df,
            time_col,
            train_periods,
            test_periods,
        )
    ]

