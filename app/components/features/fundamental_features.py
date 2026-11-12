
import pandas as pd


def growth_yoy(
    values: pd.Series,
    periods: int = 4,
) -> pd.Series:
    """Tăng trưởng so với cùng kỳ, mặc định cách 4 quý."""
    if periods <= 0:
        raise ValueError("periods phải lớn hơn 0.")

    previous = values.shift(periods)

    # Tránh chia cho 0 hoặc mẫu số bị thiếu.
    result = values / previous.where(previous != 0) - 1

    return result


def profit_growth_yoy(
    net_profit: pd.Series,
    periods: int = 4,
) -> pd.Series:
    """Tăng trưởng lợi nhuận sau thuế so với cùng kỳ."""
    return growth_yoy(net_profit, periods)


def asset_growth_yoy(
    total_assets: pd.Series,
    periods: int = 4,
) -> pd.Series:
    """Tăng trưởng tổng tài sản so với cùng kỳ."""
    return growth_yoy(total_assets, periods)


def equity_growth_yoy(
    owners_equity: pd.Series,
    periods: int = 4,
) -> pd.Series:
    """Tăng trưởng vốn chủ sở hữu so với cùng kỳ."""
    return growth_yoy(owners_equity, periods)


def profit_ttm(
    net_profit: pd.Series,
    periods: int = 4,
) -> pd.Series:
    """Tổng lợi nhuận của các quý gần nhất."""
    if periods <= 0:
        raise ValueError("periods phải lớn hơn 0.")

    return net_profit.rolling(
        window=periods,
        min_periods=periods,
    ).sum()


def roe_ttm_approx(
    net_profit: pd.Series,
    owners_equity: pd.Series,
    periods: int = 4,
) -> pd.Series:
    """ROE TTM xấp xỉ."""
    denominator = owners_equity.where(owners_equity != 0)

    return profit_ttm(net_profit, periods) / denominator


def roa_ttm_approx(
    net_profit: pd.Series,
    total_assets: pd.Series,
    periods: int = 4,
) -> pd.Series:
    """ROA TTM xấp xỉ."""
    denominator = total_assets.where(total_assets != 0)

    return profit_ttm(net_profit, periods) / denominator


def debt_to_equity(
    liabilities: pd.Series,
    owners_equity: pd.Series,
) -> pd.Series:
    """Tỷ lệ nợ phải trả trên vốn chủ sở hữu."""
    denominator = owners_equity.where(owners_equity != 0)

    return liabilities / denominator
