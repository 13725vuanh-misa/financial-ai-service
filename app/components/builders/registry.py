from app.components.builders.stock_trend import (
    QuarterlyV2CaseA,
    QuarterlyV2CaseB,
    QuarterlyV2Merged,
)
from app.components.builders.base import BaseDatasetBuilder


BUILDER_REGISTRY = {
    QuarterlyV2CaseA.name: QuarterlyV2CaseA,
    QuarterlyV2CaseB.name: QuarterlyV2CaseB,
    QuarterlyV2Merged.name: QuarterlyV2Merged,
}


def get_builder(builder_name: str) -> BaseDatasetBuilder:
    """
    Lấy Builder theo tên.

    Parameters
    ----------
    builder_name : str
        Tên Builder cần sử dụng.

    Returns
    -------
    BaseDatasetBuilder
        Một đối tượng Builder tương ứng.
    """
    builder_class = BUILDER_REGISTRY.get(builder_name)

    if builder_class is None:
        raise ValueError(
            f"Builder không tồn tại: {builder_name}"
        )

    return builder_class()
