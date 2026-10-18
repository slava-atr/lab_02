from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Event:
    timestamp: datetime
    level: str
    source: str
    message: str
@dataclass
class Stats:
    total: int = 0
    levels: Counter = field(default_factory=Counter)
    by_source: dict = field(default_factory=dict)
    first_timestamp: datetime | None = None
    last_timestamp: datetime | None = None
    skipped: int = 0