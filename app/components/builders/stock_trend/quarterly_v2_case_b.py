
import pandas as pd

from app.components.builders.base import BaseDatasetBuilder
from app.components.builders.stock_trend.constants import (
    FUNDAMENTAL_FEATURES,
    FEATURES_V2,
    DATASET_COLUMNS,
)
from app.components.builders.data_requirements import DataRequirement


class QuarterlyV2CaseB(BaseDatasetBuilder):
    name = "quarterly_v2_case_b"
    display_name = "Stock Trend V2 - Case B"
    description = "Market quý q kết hợp với BCTC quý q-1."
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

        # 1. Lấy các cột cần thiết từ dữ liệu BCTC
        fundamental_columns = [
            "ticker",
            "period",
            "available_date",
        ] + FUNDAMENTAL_FEATURES

        fm = fundamental_df[fundamental_columns].copy()

        # 2. Ghép BCTC quý trước với Market quý hiện tại
        lag = 1
        fm["quarter"] = fm["period"] + lag

        # 3. Đổi tên cột để phân biệt thông tin BCTC
        fm = fm.rename(
            columns={
                "period": "bctc_period",
                "available_date": "bctc_available_date",
            }
        )

        # 4. Ghép theo mã cổ phiếu và quý
        data = market_df.merge(
            fm,
            on=["ticker", "quarter"],
            how="left",
        )

        # 5. Ghi nhận loại dữ liệu đang xây dựng
        data["case"] = "B"
        data["bctc_lag"] = lag

        # 6. Ghi nhận BCTC đã được công bố tại thời điểm as_of hay chưa
        data["known_at_asof"] = (
            data["bctc_available_date"].notna()
            & (data["bctc_available_date"] <= data["as_of"])
        )

        # 7. Loại các dòng không có nhãn hoặc thiếu đặc trưng
        data = data[data["target"].notna()]
        data = data[data[FEATURES_V2].notna().all(axis=1)]

        # 8. Chọn cột và sắp xếp dữ liệu
        data = (
            data[DATASET_COLUMNS]
            .sort_values(["quarter", "ticker"])
            .reset_index(drop=True)
        )

        return data
