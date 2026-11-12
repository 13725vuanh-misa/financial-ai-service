import pandas as pd

from app.services.pipeline.base import BasePipeline


class DatabasePipeline(BasePipeline):
    name = "database"
    display_name = "Database Pipeline"
    description = "Tạo Dataset mới từ dữ liệu trong Database."

    def prepare_dataset(
        self,
        market_df: pd.DataFrame,
        fundamental_df: pd.DataFrame,
        builder_name: str,
    ) -> pd.DataFrame:
        """
        Tạo Dataset từ dữ liệu thị trường và dữ liệu tài chính.
        """

        from app.components.builders import get_builder

        builder = get_builder(builder_name)

        dataset = builder.build(
            market_df=market_df,
            fundamental_df=fundamental_df,
        )

        return dataset
