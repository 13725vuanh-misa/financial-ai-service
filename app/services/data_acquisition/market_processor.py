
import pandas as pd

from app.components.features.registry import FEATURE_REGISTRY
from app.components.labels.stock_trend import create_stock_trend_label


def get_complete_quarters(
    start_date,
    end_date,
) -> list[pd.Period]:
    """Lấy các quý nằm trọn vẹn trong khoảng thời gian yêu cầu."""

    start_date = pd.Timestamp(start_date)
    end_date = pd.Timestamp(end_date)

    if start_date >= end_date:
        raise ValueError("start_date phải nhỏ hơn end_date")

    quarters = pd.period_range(
        start=start_date.to_period("Q"),
        end=end_date.to_period("Q"),
        freq="Q",
    )

    complete_quarters = []

    for quarter in quarters:
        # Quý đầu phải bắt đầu đúng ngày đầu quý.
        if (
            quarter == start_date.to_period("Q")
            and start_date.date() != quarter.start_time.date()
        ):
            continue

        # Quý cuối phải kết thúc đúng ngày cuối quý.
        if (
            quarter == end_date.to_period("Q")
            and end_date.date() != quarter.end_time.date()
        ):
            continue

        complete_quarters.append(quarter)

    return complete_quarters


def _prepare_market_data(
    market_df: pd.DataFrame,
) -> pd.DataFrame:
    """Chuẩn hóa dữ liệu giá thô từ Repository."""

    df = market_df.copy()

    rename_columns = {}

    if "ticker" not in df.columns and "symbol" in df.columns:
        rename_columns["symbol"] = "ticker"

    if "date" not in df.columns and "price_timestamp" in df.columns:
        rename_columns["price_timestamp"] = "date"

    if "close" not in df.columns and "close_price" in df.columns:
        rename_columns["close_price"] = "close"

    df = df.rename(columns=rename_columns)

    required_columns = [
        "ticker",
        "date",
        "close",
        "volume",
    ]

    missing = [
        column
        for column in required_columns
        if column not in df.columns
    ]

    if missing:
        raise ValueError(f"Market thiếu các cột: {missing}")

    df["date"] = pd.to_datetime(df["date"])
    df["close"] = pd.to_numeric(df["close"], errors="coerce")
    df["volume"] = pd.to_numeric(df["volume"], errors="coerce")

    df = df.dropna(subset=["ticker", "date", "close"])

    df = df.drop_duplicates(
        subset=["ticker", "date"],
        keep="last",
    )

    df["quarter"] = df["date"].dt.to_period("Q")

    return (
        df.sort_values(["ticker", "date"])
        .reset_index(drop=True)
    )


def _calculate_stock_features(
    stock_df: pd.DataFrame,
) -> pd.DataFrame:
    """Tính Market Feature cho một mã cổ phiếu theo quý."""

    df = stock_df.copy()

    registry = FEATURE_REGISTRY

    # Feature theo ngày.
    df["daily_return"] = registry["daily_return"].calculate(df)

    df["ma20"] = registry["ma"].calculate(
        period=20,
        df=df,
    )

    df["ma50"] = registry["ma"].calculate(
        period=50,
        df=df,
    )

    df["price_to_ma20"] = registry["price_to_ma"].calculate(
        period=20,
        df=df,
    )

    df["price_to_ma50"] = registry["price_to_ma"].calculate(
        period=50,
        df=df,
    )

    # Tổng hợp dữ liệu tại phiên cuối mỗi quý.
    quarterly = (
        df.groupby("quarter", sort=True)
        .agg(
            as_of=("date", "last"),
            close_end=("close", "last"),
            price_to_ma20=("price_to_ma20", "last"),
            price_to_ma50=("price_to_ma50", "last"),
        )
    )

    # Lợi suất giữa hai quý liên tiếp.
    quarterly["return_1q"] = (
        registry["return_1q"].calculate(
            quarterly["close_end"]
        )
    )

    # Không tính lợi suất nếu hai quý không liên tiếp.
    previous_quarter = quarterly.index.to_series().shift(1)
    expected_previous = quarterly.index.to_series() - 1

    quarterly["return_1q"] = quarterly["return_1q"].where(
        previous_quarter == expected_previous
    )

    # Độ biến động trong quý.
    quarterly["volatility_1q"] = (
        registry["volatility_1q"].calculate(
            df["daily_return"],
            df["quarter"],
        ).reindex(quarterly.index)
    )

    # Log trung bình khối lượng giao dịch trong quý.
    quarterly["log_avg_volume_1q"] = (
        registry["log_avg_volume_1q"].calculate(
            df["volume"],
            df["quarter"],
        ).reindex(quarterly.index)
    )

    quarterly = quarterly.reset_index()
    quarterly["ticker"] = df["ticker"].iloc[0]

    return quarterly


def _calculate_vnindex_features(
    vn_df: pd.DataFrame,
) -> pd.DataFrame:
    """Tính Feature thị trường từ dữ liệu VNINDEX."""

    df = vn_df.copy().sort_values("date")

    if df["ticker"].nunique() != 1:
        raise ValueError("Dữ liệu VNINDEX phải chỉ chứa một mã.")

    registry = FEATURE_REGISTRY

    df["vn_daily_return"] = (
        registry["daily_return"].calculate(df)
    )

    quarterly = (
        df.groupby("quarter", sort=True)
        .agg(
            close_end=("close", "last"),
        )
    )

    # Lợi suất VNINDEX giữa hai quý liên tiếp.
    quarterly["vn_return_1q"] = (
        registry["vn_return_1q"].calculate(
            quarterly["close_end"]
        )
    )

    previous_quarter = quarterly.index.to_series().shift(1)
    expected_previous = quarterly.index.to_series() - 1

    quarterly["vn_return_1q"] = (
        quarterly["vn_return_1q"].where(
            previous_quarter == expected_previous
        )
    )

    # Độ biến động VNINDEX trong quý.
    quarterly["vn_volatility_1q"] = (
        registry["vn_volatility_1q"].calculate(
            df["vn_daily_return"],
            df["quarter"],
        ).reindex(quarterly.index)
    )

    return quarterly[
        ["vn_return_1q", "vn_volatility_1q"]
    ].reset_index()


def process_market_data(
    market_df: pd.DataFrame,
    vnindex_df: pd.DataFrame,
    start_date,
    end_date,
) -> pd.DataFrame:
    """
    Chuẩn hóa Market thô và tính các Feature theo quý.

    Dữ liệu lookback được dùng để tính Feature nhưng không
    được đưa vào kết quả Dataset.
    """

    if market_df.empty:
        raise ValueError("Market DataFrame không có dữ liệu.")

    if vnindex_df.empty:
        raise ValueError("VNINDEX DataFrame không có dữ liệu.")

    complete_quarters = get_complete_quarters(
        start_date=start_date,
        end_date=end_date,
    )

    if not complete_quarters:
        raise ValueError(
            "Khoảng thời gian không có quý nào đầy đủ."
        )

    # Chuẩn hóa hai nguồn dữ liệu.
    stock_df = _prepare_market_data(market_df)
    vn_df = _prepare_market_data(vnindex_df)

    # Tính Feature VNINDEX.
    vn_features = _calculate_vnindex_features(vn_df)

    # Tính Feature cho từng mã cổ phiếu.
    stock_results = []

    for ticker, group in stock_df.groupby("ticker"):
        stock_results.append(
            _calculate_stock_features(group)
        )

    if not stock_results:
        raise ValueError("Không có dữ liệu cổ phiếu.")

    result = pd.concat(
        stock_results,
        ignore_index=True,
    )

    
    result = result.merge(vn_features, on="quarter", how="left")

    # 1. Tính lợi suất tương đối
    result["relative_return_1q"] = FEATURE_REGISTRY[
        "relative_return_1q"
    ].calculate(
        result["return_1q"],
        result["vn_return_1q"],
    )

    # 2. Sắp xếp toàn bộ dữ liệu theo ticker và quý
    result = result.sort_values(
        ["ticker", "quarter"]
    ).reset_index(drop=True)

    # 3. Lấy giá đóng cửa của quý kế tiếp
    result["future_close"] = (
        result.groupby("ticker")["close_end"].shift(-1)
    )

    next_quarter = result.groupby("ticker")["quarter"].shift(-1)

    # Chỉ chấp nhận đúng quý liền sau
    result["future_close"] = result["future_close"].where(
        next_quarter == result["quarter"] + 1
    )

    # 4. Tính lợi suất tương lai và Label
    result["future_return_1q"] = (
        result["future_close"] / result["close_end"] - 1
    )

    result = create_stock_trend_label(result)

    # 5. Chỉ giữ các quý FE yêu cầu
    result = result[
        result["quarter"].isin(complete_quarters)
    ].copy()

    if result.empty:
        raise ValueError(
            "Không có dữ liệu Market thuộc các quý hoàn chỉnh."
        )

    # 6. Chọn các cột đầu ra
    output_columns = [
        "ticker",
        "quarter",
        "as_of",
        "return_1q",
        "volatility_1q",
        "log_avg_volume_1q",
        "price_to_ma20",
        "price_to_ma50",
        "vn_return_1q",
        "vn_volatility_1q",
        "relative_return_1q",
        "future_return_1q",
        "target",
    ]

    return result[output_columns].sort_values(
        ["quarter", "ticker"]
    ).reset_index(drop=True)

