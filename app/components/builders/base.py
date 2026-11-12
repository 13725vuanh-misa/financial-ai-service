
from abc import ABC, abstractmethod

import pandas as pd

from app.components.builders.data_requirements import DataRequirement


class BaseDatasetBuilder(ABC):
    """
    Lớp cơ sở cho các Builder tạo dataset.
    """

    name: str = "base"
    display_name: str = "Base Dataset Builder"
    description: str = ""

    data_requirements: tuple[DataRequirement, ...] = ()

    # Các cột được sử dụng để huấn luyện và đánh giá
    feature_columns: tuple[str, ...] = ()
    target_column: str = "target"

    @abstractmethod
    def build(
        self,
        market_df: pd.DataFrame,
        fundamental_df: pd.DataFrame,
    ) -> pd.DataFrame:
        """
        Xây dựng dataset từ dữ liệu thị trường và dữ liệu BCTC.
        """
        raise NotImplementedError
