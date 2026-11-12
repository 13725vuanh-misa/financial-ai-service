from app.components.features.base import FeatureDefinition

from app.components.features.market_features import (
    daily_return,
    ma,
    return_1q,
    volatility_1q,
    avg_volume_1q,
    log_avg_volume_1q,
    price_to_ma,
    vn_return_1q,
    vn_volatility_1q,
    relative_return_1q,
)

from app.components.features.fundamental_features import (
    growth_yoy,
    profit_growth_yoy,
    asset_growth_yoy,
    equity_growth_yoy,
    profit_ttm,
    roe_ttm_approx,
    roa_ttm_approx,
    debt_to_equity,
)


FEATURE_REGISTRY = {
    # =========================
    # MARKET FEATURES
    # =========================

    "daily_return": FeatureDefinition(
        name="daily_return",
        display_name="Lợi suất ngày",
        description="Tính tỷ lệ thay đổi giá đóng cửa giữa hai phiên liên tiếp.",
        category="market",
        required_columns=("close",),
        calculate=daily_return,
    ),

    "ma": FeatureDefinition(
        name="ma",
        display_name="Đường trung bình động",
        description="Tính giá trung bình động theo số phiên được chỉ định.",
        category="market",
        required_columns=("close",),
        calculate=ma,
    ),

    "return_1q": FeatureDefinition(
        name="return_1q",
        display_name="Lợi suất quý",
        description="Tính tỷ lệ thay đổi giá đóng cửa cuối quý so với quý trước.",
        category="market",
        required_columns=("quarterly_close",),
        calculate=return_1q,
    ),

    "volatility_1q": FeatureDefinition(
        name="volatility_1q",
        display_name="Độ biến động quý",
        description="Tính độ lệch chuẩn lợi suất ngày trong từng quý.",
        category="market",
        required_columns=("daily_return", "quarter"),
        calculate=volatility_1q,
    ),

    "avg_volume_1q": FeatureDefinition(
        name="avg_volume_1q",
        display_name="Khối lượng giao dịch trung bình quý",
        description="Tính khối lượng giao dịch trung bình trong từng quý.",
        category="market",
        required_columns=("volume", "quarter"),
        calculate=avg_volume_1q,
    ),

    "log_avg_volume_1q": FeatureDefinition(
        name="log_avg_volume_1q",
        display_name="Log khối lượng giao dịch trung bình quý",
        description="Tính log(1 + khối lượng giao dịch trung bình quý).",
        category="market",
        required_columns=("volume", "quarter"),
        calculate=log_avg_volume_1q,
    ),

    "price_to_ma": FeatureDefinition(
        name="price_to_ma",
        display_name="Giá so với trung bình động",
        description="Tính mức chênh lệch tương đối giữa giá và đường trung bình động.",
        category="market",
        required_columns=("close",),
        calculate=price_to_ma,
    ),

    "vn_return_1q": FeatureDefinition(
        name="vn_return_1q",
        display_name="Lợi suất VNINDEX theo quý",
        description="Tính lợi suất VNINDEX giữa hai quý liên tiếp.",
        category="market",
        required_columns=("vn_quarterly_close",),
        calculate=vn_return_1q,
    ),

    "vn_volatility_1q": FeatureDefinition(
        name="vn_volatility_1q",
        display_name="Độ biến động VNINDEX theo quý",
        description="Tính độ lệch chuẩn lợi suất ngày VNINDEX trong từng quý.",
        category="market",
        required_columns=("vn_daily_return", "quarter"),
        calculate=vn_volatility_1q,
    ),

    "relative_return_1q": FeatureDefinition(
        name="relative_return_1q",
        display_name="Lợi suất tương đối so với thị trường",
        description="Tính chênh lệch giữa lợi suất cổ phiếu và lợi suất VNINDEX.",
        category="market",
        required_columns=("stock_return", "market_return"),
        calculate=relative_return_1q,
    ),

    # =========================
    # FUNDAMENTAL FEATURES
    # =========================

    "growth_yoy": FeatureDefinition(
        name="growth_yoy",
        display_name="Tăng trưởng cùng kỳ",
        description="Tính tỷ lệ thay đổi so với giá trị cách đó một số quý.",
        category="fundamental",
        required_columns=("values",),
        calculate=growth_yoy,
    ),

    "profit_growth_yoy": FeatureDefinition(
        name="profit_growth_yoy",
        display_name="Tăng trưởng lợi nhuận",
        description="Tính tăng trưởng lợi nhuận so với cùng kỳ năm trước.",
        category="fundamental",
        required_columns=("net_profit",),
        calculate=profit_growth_yoy,
    ),

    "asset_growth_yoy": FeatureDefinition(
        name="asset_growth_yoy",
        display_name="Tăng trưởng tổng tài sản",
        description="Tính tăng trưởng tổng tài sản so với cùng kỳ năm trước.",
        category="fundamental",
        required_columns=("total_assets",),
        calculate=asset_growth_yoy,
    ),

    "equity_growth_yoy": FeatureDefinition(
        name="equity_growth_yoy",
        display_name="Tăng trưởng vốn chủ sở hữu",
        description="Tính tăng trưởng vốn chủ sở hữu so với cùng kỳ năm trước.",
        category="fundamental",
        required_columns=("owners_equity",),
        calculate=equity_growth_yoy,
    ),

    "profit_ttm": FeatureDefinition(
        name="profit_ttm",
        display_name="Lợi nhuận TTM",
        description="Tính tổng lợi nhuận của các quý gần nhất theo cửa sổ được chỉ định.",
        category="fundamental",
        required_columns=("net_profit",),
        calculate=profit_ttm,
    ),

    "roe_ttm_approx": FeatureDefinition(
        name="roe_ttm_approx",
        display_name="ROE xấp xỉ theo TTM",
        description="Tính lợi nhuận TTM chia cho vốn chủ sở hữu.",
        category="fundamental",
        required_columns=("net_profit", "owners_equity"),
        calculate=roe_ttm_approx,
    ),

    "roa_ttm_approx": FeatureDefinition(
        name="roa_ttm_approx",
        display_name="ROA xấp xỉ theo TTM",
        description="Tính lợi nhuận TTM chia cho tổng tài sản.",
        category="fundamental",
        required_columns=("net_profit", "total_assets"),
        calculate=roa_ttm_approx,
    ),

    "debt_to_equity": FeatureDefinition(
        name="debt_to_equity",
        display_name="Tỷ lệ nợ trên vốn chủ sở hữu",
        description="Tính tổng nợ phải trả chia cho vốn chủ sở hữu.",
        category="fundamental",
        required_columns=("liabilities", "owners_equity"),
        calculate=debt_to_equity,
    ),
}