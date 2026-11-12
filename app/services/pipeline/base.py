
from abc import ABC, abstractmethod

import pandas as pd


class BasePipeline(ABC):
    name = "base"
    display_name = "Base Pipeline"
    description = ""

    @abstractmethod
    def prepare_dataset(self, **kwargs) -> pd.DataFrame:
        """
        Chuẩn bị Dataset đầu vào cho các bước xử lý tiếp theo.
        """
        raise NotImplementedError
