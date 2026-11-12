from app.services.data_acquisition.planner import DataFetchRequest

from app.repositories.market_repository import get_market_prices
from app.repositories.fundamental_repository import get_fundamental_data


VNINDEX_TICKER = "VNINDEX"


def fetch_data(
    fetch_plan: list[DataFetchRequest],
) -> dict:
    """
    Thực hiện Fetch Plan và lấy dữ liệu từ PostgreSQL.

    Trả về dữ liệu theo từng nguồn.
    """

    fetched_data = {}

    for request in fetch_plan:

        if request.source_name == "market":
            # Tự bổ sung VNINDEX để tính các chỉ số thị trường.
            market_tickers = list(
                dict.fromkeys(request.tickers + [VNINDEX_TICKER])
            )

            data = get_market_prices(
                tickers=market_tickers,
                start_date=request.start_date,
                end_date=request.end_date,
                interval_code=request.frequency,
                lookback_periods=request.lookback_periods,
            )

            # Tách dữ liệu cổ phiếu và VNINDEX.
            vnindex_df = data[
                data["symbol"] == VNINDEX_TICKER
            ].copy()

            market_df = data[
                data["symbol"] != VNINDEX_TICKER
            ].copy()

            if vnindex_df.empty:
                raise ValueError(
                    "Không tìm thấy dữ liệu VNINDEX trong PostgreSQL."
                )

            fetched_data["market"] = market_df
            fetched_data["vnindex"] = vnindex_df

        elif request.source_name == "fundamental":
            data = get_fundamental_data(
                tickers=request.tickers,
                start_date=request.start_date,
                end_date=request.end_date,
                lookback_periods=request.lookback_periods,
            )

            fetched_data["fundamental"] = data

        else:
            raise ValueError(
                f"Nguồn dữ liệu không được hỗ trợ: "
                f"{request.source_name}"
            )

    return fetched_data

def get_market_fetch_end_date(end_date):
    """
    Xác định ngày kết thúc lấy dữ liệu Market.

    Lấy thêm một quý để phục vụ tạo Label
    cho quý cuối cùng trong Dataset.
    """
    import pandas as pd

    end_quarter = pd.Period(end_date, freq="Q")

    if end_date == end_quarter.end_time.date():
        end_quarter += 1

    return end_quarter.end_time.date()