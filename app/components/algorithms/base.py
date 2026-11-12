from dataclasses import dataclass
from typing import Any, Callable


@dataclass(frozen=True)
class AlgorithmDefinition:
    """Thông tin mô tả một thuật toán ML."""

    name: str
    display_name: str
    description: str
    task_type: str
    create_model: Callable[..., Any]