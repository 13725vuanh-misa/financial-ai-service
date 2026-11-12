
from datetime import date
from typing import Annotated, Literal, Union

from pydantic import BaseModel, Field


class DatasetBuildRequest(BaseModel):
    dataset_name: str = Field(
        min_length=1,
        description="Tên Dataset muốn tạo",
    )

    builder_name: str = Field(
        min_length=1,
        description="Tên Builder sử dụng",
    )

    tickers: list[str] = Field(
        min_length=1,
        description="Danh sách mã cổ phiếu",
    )

    start_date: date
    end_date: date


class ExistingDatasetRequest(BaseModel):
    source: Literal["existing"]
    dataset_name: str = Field(
        min_length=1,
        description="Tên Dataset đã lưu",
    )


class NewDatasetRequest(DatasetBuildRequest):
    source: Literal["new"]


DatasetSource = Annotated[
    Union[ExistingDatasetRequest, NewDatasetRequest],
    Field(discriminator="source"),
]
