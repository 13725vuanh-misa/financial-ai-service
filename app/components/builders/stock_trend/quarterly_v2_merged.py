import pandas as pd

from app.components.builders.base import BaseDatasetBuilder
from app.components.builders.stock_trend.quarterly_v2_case_a import (
    QuarterlyV2CaseA,
)
from app.components.builders.stock_trend.quarterly_v2_case_b import (
    QuarterlyV2CaseB,
)
from app.components.builders.stock_trend.constants import FEATURES_V2
from app.components.builders.data_requirements import DataRequirement


class QuarterlyV2Merged(BaseDatasetBuilder):
    name = "quarterly_v2_merged"
    display_name = "Stock Trend V2 - Merged"
    description = "Kết hợp dữ liệu Case A và Case B."
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

        # 1. Xây dựng dataset Case A
        data_a = QuarterlyV2CaseA().build(
            market_df,
            fundamental_df,
        )

        # 2. Xây dựng dataset Case B
        data_b = QuarterlyV2CaseB().build(
            market_df,
            fundamental_df,
        )

        # 3. Nối hai dataset theo chiều dọc
        data = pd.concat(
            [data_a, data_b],
            ignore_index=True,
        )

        # 4. Sắp xếp dữ liệu
        data = (
            data.sort_values(["quarter", "ticker", "case"])
            .reset_index(drop=True)
        )

        return data
