from dataclasses import dataclass


@dataclass(frozen=True)
class DataRequirement:
    source_name: str
    frequency: str
    lookback_periods: int = 0
    description: str = ""