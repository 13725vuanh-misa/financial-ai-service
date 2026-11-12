import pandas as pd


def create_stock_trend_label(
    df: pd.DataFrame,
    current_price_col: str = "close_end",
    future_price_col: str = "future_close",
    target_col: str = "target",
) -> pd.DataFrame:
    """
    Tạo nhãn xu hướng cổ phiếu.

    target = 1: Giá tương lai tăng.
    target = 0: Giá tương lai không tăng.
    """

    required_columns = [current_price_col, future_price_col]

    missing_columns = [
        col for col in required_columns
        if col not in df.columns
    ]

    if missing_columns:
        raise ValueError(
            f"Thiếu các cột cần thiết: {missing_columns}"
        )

    result = df.copy()

    result[target_col] = pd.Series(
        float("nan"),
        index=result.index,
    )

    valid = (
        result[current_price_col].notna()
        & result[future_price_col].notna()
    )

    result.loc[valid, target_col] = (
        result.loc[valid, future_price_col]
        > result.loc[valid, current_price_col]
    ).astype("int")

    return result
