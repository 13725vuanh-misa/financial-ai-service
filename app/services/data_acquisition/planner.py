from dataclasses import dataclass
from datetime import date

from app.components.builders.data_requirements import DataRequirement


@dataclass(frozen=True)
class DataFetchRequest:
    source_name: str
    frequency: str
    tickers: list[str]
    start_date: date
    end_date: date
    lookback_periods: int


def create_fetch_plan(
    requirements: tuple[DataRequirement, ...],
    tickers: list[str],
    start_date: date,
    end_date: date,
) -> list[DataFetchRequest]:

    if start_date >= end_date:
        raise ValueError("start_date phải nhỏ hơn end_date")

    return [
        DataFetchRequest(
            source_name=requirement.source_name,
            frequency=requirement.frequency,
            tickers=tickers,
            start_date=start_date,
            end_date=end_date,
            lookback_periods=requirement.lookback_periods,
        )
        for requirement in requirements
    ]