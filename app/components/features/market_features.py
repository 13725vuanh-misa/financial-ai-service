
import numpy as np
import pandas as pd


def daily_return(df: pd.DataFrame, price_col: str = "close") -> pd.Series:
    """Lợi suất từng phiên."""
    return df[price_col].pct_change()


def ma(
    period: int,
    df: pd.DataFrame,
    price_col: str = "close",
) -> pd.Series:
    """Đường trung bình động theo số phiên."""
    if period <= 0:
        raise ValueError("period phải lớn hơn 0.")

    return df[price_col].rolling(
        window=period,
        min_periods=period,
    ).mean()


def return_1q(
    quarterly_close: pd.Series,
) -> pd.Series:
    """Lợi suất quý từ giá đóng cửa cuối quý."""
    return quarterly_close.pct_change()


def volatility_1q(
    daily_returns: pd.Series,
    quarter: pd.Series,
) -> pd.Series:
    """Độ lệch chuẩn lợi suất ngày trong từng quý."""
    return daily_returns.groupby(quarter).std()


def avg_volume_1q(
    volume: pd.Series,
    quarter: pd.Series,
) -> pd.Series:
    """Khối lượng giao dịch trung bình theo quý."""
    return volume.groupby(quarter).mean()


def log_avg_volume_1q(
    volume: pd.Series,
    quarter: pd.Series,
) -> pd.Series:
    """Log(1 + khối lượng giao dịch trung bình quý)."""
    if (volume.dropna() < 0).any():
        raise ValueError("Khối lượng không được âm.")

    return np.log1p(avg_volume_1q(volume, quarter))


def price_to_ma(
    period: int,
    df: pd.DataFrame,
    price_col: str = "close",
) -> pd.Series:
    """Giá chia MA rồi trừ 1."""
    if period <= 0:
        raise ValueError("period phải lớn hơn 0.")

    moving_average = ma(period, df, price_col)

    return df[price_col] / moving_average - 1


def vn_return_1q(
    vn_quarterly_close: pd.Series,
) -> pd.Series:
    """Lợi suất VNINDEX theo quý."""
    return vn_quarterly_close.pct_change()


def vn_volatility_1q(
    vn_daily_returns: pd.Series,
    quarter: pd.Series,
) -> pd.Series:
    """Độ biến động lợi suất VNINDEX theo quý."""
    return vn_daily_returns.groupby(quarter).std()


def relative_return_1q(
    stock_return: pd.Series,
    market_return: pd.Series,
) -> pd.Series:
    """Lợi suất cổ phiếu trừ lợi suất thị trường."""
    return stock_return - market_return
