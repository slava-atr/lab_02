from datetime import datetime

from streamstats.analysis import merge_stats, update_stat
from streamstats.models import Event, Stats


def test_merge_stats():
    first = Stats()
    event1 = Event(
        timestamp=datetime(2026, 10, 25, 10, 0),
        level="ERROR",
        source="api",
        message="Request failed",
    )
    update_stat(event1, first)

    second = Stats()
    event2 = Event(
        timestamp=datetime(2026, 10, 25, 11, 0),
        level="INFO",
        source="database",
        message="Connected",
    )
    update_stat(event2, second)
    second.skipped = 1
    
    merge_stats(first, second)

    assert first.total == 2
    assert first.levels == {"ERROR": 1, "INFO": 1}
    assert first.by_source["api"] == {"total": 1, "errors": 1}
    assert first.by_source["database"] == {"total": 1, "errors": 0}
    assert first.skipped == 1
    assert first.first_timestamp == datetime(2026, 10, 25, 10, 0)
    assert first.last_timestamp == datetime(2026, 10, 25, 11, 0)
