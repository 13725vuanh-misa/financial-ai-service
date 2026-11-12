MARKET_FEATURES = [
    "return_1q",
    "volatility_1q",
    "log_avg_volume_1q",
    "price_to_ma20",
    "price_to_ma50",
    "vn_return_1q",
    "vn_volatility_1q",
    "relative_return_1q",
]

FUNDAMENTAL_FEATURES = [
    "profit_growth_yoy",
    "asset_growth_yoy",
    "equity_growth_yoy",
    "roe_ttm_approx",
    "roa_ttm_approx",
    "debt_to_equity",
]

FEATURES_V2 = MARKET_FEATURES + FUNDAMENTAL_FEATURES

DATASET_COLUMNS = (
    [
        "ticker",
        "quarter",
        "as_of",
        "case",
        "bctc_lag",
        "bctc_period",
        "bctc_available_date",
        "known_at_asof",
    ]
    + FEATURES_V2
    + ["future_return_1q", "target"]
)