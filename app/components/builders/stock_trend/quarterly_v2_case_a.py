import pandas as pd

from app.components.builders.base import BaseDatasetBuilder
from app.components.builders.stock_trend.constants import (
    FUNDAMENTAL_FEATURES,
    FEATURES_V2,
    DATASET_COLUMNS,
)
from app.components.builders.data_requirements import DataRequirement


class QuarterlyV2CaseA(BaseDatasetBuilder):
    name = "quarterly_v2_case_a"
    display_name = "Stock Trend V2 - Case A"
    description = "Market quý q kết hợp với BCTC quý q."
    feature_columns = tuple(FEATURES_V2)
    data_requirements = (
        DataRequirement(
            source_name="market",
            frequency="daily",
            lookback_periods=250,
            description="Dữ liệu giá cổ phiếu để tính chỉ báo thị trường",
        ),
        DataRequirement(
            source_name="fundamental",
            frequency="quarterly",
            lookback_periods=4,
            description="Dữ liệu báo cáo tài chính để tính chỉ báo cơ bản",
        ),
    )
    def build(
        self,
        market_df: pd.DataFrame,
        fundamental_df: pd.DataFrame,
    ) -> pd.DataFrame:

        # Các cột cần lấy từ dữ liệu BCTC
        fundamental_columns = (
            ["ticker", "period", "available_date"]
            + FUNDAMENTAL_FEATURES
        )

        fm = fundamental_df[fundamental_columns].copy()

        # Case A: BCTC quý q ghép với Market quý q
        fm["quarter"] = fm["period"]

        fm = fm.rename(
            columns={
                "period": "bctc_period",
                "available_date": "bctc_available_date",
            }
        )

        # Ghép Market và Fundamental
        data = market_df.merge(
            fm,
            on=["ticker", "quarter"],
            how="left",
        )

        # Đánh dấu Case A
        data["case"] = "A"
        data["bctc_lag"] = 0

        # Kiểm tra BCTC đã khả dụng tại thời điểm as_of chưa
        data["known_at_asof"] = (
            data["bctc_available_date"].notna()
            & (data["bctc_available_date"] <= data["as_of"])
        )

        # Chỉ giữ những dòng đã có nhãn mục tiêu
        data = data[data["target"].notna()]

        # Chỉ giữ những dòng có đủ 14 Feature
        data = data[
            data[DATASET_COLUMNS[8:-2]].notna().all(axis=1)
        ]

        # Sắp xếp và trả về các cột theo cấu trúc dataset
        data = (
            data[DATASET_COLUMNS]
            .sort_values(["quarter", "ticker"])
            .reset_index(drop=True)
        )

        return data