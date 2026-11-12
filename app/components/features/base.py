from dataclasses import dataclass
from typing import Callable

import pandas as pd


@dataclass(frozen=True)
class FeatureDefinition:
    """Thông tin mô tả một feature được hệ thống hỗ trợ."""

    name: str
    display_name: str
    description: str
    category: str
    required_columns: tuple[str, ...]
    calculate: Callable[..., pd.Series]