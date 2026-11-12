
import pandas as pd

from app.components.features.registry import FEATURE_REGISTRY
from app.services.data_acquisition.market_processor import (
    get_complete_quarters,
)

def _prepare_fundamental_data(
    fundamental_df: pd.DataFrame,
) -> pd.DataFrame:
    """Chuẩn hóa dữ liệu BCTC từ long format sang wide format."""

    if fundamental_df.empty:
        raise ValueError("Fundamental DataFrame không có dữ liệu.")

    required_columns = [
        "symbol",
        "fiscal_year",
        "period_type",
        "end_date",
        "as_of_date",
        "metric_code",
        "value",
    ]

    missing = [
        column
        for column in required_columns
        if column not in fundamental_df.columns
    ]

    if missing:
        raise ValueError(f"Fundamental thiếu các cột: {missing}")

    df = fundamental_df.copy()

    df = df.rename(columns={"symbol": "ticker"})

    df["end_date"] = pd.to_datetime(df["end_date"])
    df["as_of_date"] = pd.to_datetime(df["as_of_date"])
    df["value"] = pd.to_numeric(df["value"], errors="coerce")

    # Chỉ xử lý dữ liệu báo cáo theo quý.
    df = df[
        df["period_type"].astype(str).str.lower().isin(
            ["quarter", "quarterly", "q"]
        )
    ].copy()

    if df.empty:
        raise ValueError("Không có dữ liệu BCTC theo quý.")

    # Xác định quý tài chính.
    df["period"] = df["end_date"].dt.to_period("Q")

    # Với cùng mã, quý và chỉ tiêu, lấy bản ghi mới nhất.
    df = df.sort_values("as_of_date")

    df = df.drop_duplicates(
        subset=["ticker", "period", "metric_code"],
        keep="last",
    )

    # Chuyển từ long format sang wide format.
    data = df.pivot(
        index=["ticker", "period"],
        columns="metric_code",
        values="value",
    ).reset_index()

    data.columns.name = None

    # Ngày dữ liệu sẵn sàng là ngày muộn nhất của các chỉ tiêu.
    available_dates = (
        df.groupby(["ticker", "period"])["as_of_date"]
        .max()
        .reset_index(name="available_date")
    )

    data = data.merge(
        available_dates,
        on=["ticker", "period"],
        how="left",
    )

    required_metrics = [
        "net_profit",
        "total_assets",
        "owners_equity",
        "liabilities",
    ]

    for metric in required_metrics:
        if metric not in data.columns:
            data[metric] = pd.NA

    return data.sort_values(
        ["ticker", "period"]
    ).reset_index(drop=True)


def _calculate_fundamental_features(
    fundamental_df: pd.DataFrame,
) -> pd.DataFrame:
    """Tính Fundamental Feature riêng cho từng mã cổ phiếu."""

    results = []

    registry = FEATURE_REGISTRY

    for ticker, group in fundamental_df.groupby("ticker"):
        df = group.copy().sort_values("period")

        # Tăng trưởng lợi nhuận cùng kỳ năm trước.
        df["profit_growth_yoy"] = (
            registry["profit_growth_yoy"].calculate(
                df["net_profit"],
                periods=4,
            )
        )

        # Tăng trưởng tổng tài sản cùng kỳ năm trước.
        df["asset_growth_yoy"] = (
            registry["asset_growth_yoy"].calculate(
                df["total_assets"],
                periods=4,
            )
        )

        # Tăng trưởng vốn chủ sở hữu cùng kỳ năm trước.
        df["equity_growth_yoy"] = (
            registry["equity_growth_yoy"].calculate(
                df["owners_equity"],
                periods=4,
            )
        )

        # ROE xấp xỉ từ lợi nhuận TTM.
        df["roe_ttm_approx"] = (
            registry["roe_ttm_approx"].calculate(
                df["net_profit"],
                df["owners_equity"],
                periods=4,
            )
        )

        # ROA xấp xỉ từ lợi nhuận TTM.
        df["roa_ttm_approx"] = (
            registry["roa_ttm_approx"].calculate(
                df["net_profit"],
                df["total_assets"],
                periods=4,
            )
        )

        # Nợ trên vốn chủ sở hữu.
        df["debt_to_equity"] = (
            registry["debt_to_equity"].calculate(
                df["liabilities"],
                df["owners_equity"],
            )
        )

        results.append(df)

    if not results:
        raise ValueError("Không có dữ liệu để tính Fundamental Feature.")

    return pd.concat(
        results,
        ignore_index=True,
    )


def process_fundamental_data(
    fundamental_df: pd.DataFrame,
    start_date,
    end_date,
) -> pd.DataFrame:
    """
    Chuẩn hóa BCTC và tính Fundamental Feature theo quý.

    Dữ liệu lookback được sử dụng để tính Feature nhưng
    không được đưa vào kết quả Dataset.
    """

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    if start_date >= end_date:
        raise ValueError("start_date phải nhỏ hơn end_date")

    df = _prepare_fundamental_data(fundamental_df)

    # Tính Feature trước khi lọc để tận dụng dữ liệu lookback.
    df = _calculate_fundamental_features(df)

    # Chỉ giữ các quý nằm trọn trong khoảng ngày yêu cầu.
    complete_quarters = get_complete_quarters(
            start_date,
            end_date,
        )

    if not complete_quarters:
            raise ValueError(
                "Khoảng thời gian không có quý nào đầy đủ."
            )

    df = df[
        df["period"].isin(complete_quarters)
    ].copy()

    if df.empty:
        raise ValueError(
            "Không có dữ liệu BCTC thuộc các quý đầy đủ."
        )

    output_columns = [
        "ticker",
        "period",
        "available_date",
        "profit_growth_yoy",
        "asset_growth_yoy",
        "equity_growth_yoy",
        "roe_ttm_approx",
        "roa_ttm_approx",
        "debt_to_equity",
    ]

    return (
        df[output_columns]
        .sort_values(["ticker", "period"])
        .reset_index(drop=True)
    )
