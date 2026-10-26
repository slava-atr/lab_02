from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Event:
    """Описывает одно событие из входного файла."""
    timestamp: datetime
    level: str
    source: str
    message: str

    
@dataclass
class Stats:
    """Хранит статистику по событиям."""
    total: int = 0
    levels: Counter = field(default_factory=Counter)
    by_source: dict[str, dict[str, int]] = field(default_factory=dict)
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None
    skipped: int = 0
