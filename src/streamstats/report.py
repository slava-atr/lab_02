import json
from pathlib import Path

from .analysis import get_top_error_sources
from .models import Stats


def build_report(stats: Stats) -> dict:
    """Собрать статистику в словарь для JSON-отчета."""
    top_sources = get_top_error_sources(stats)
    top_error_sources = [
        {"source": name, "errors": counts["errors"]}
        for name, counts in top_sources
    ]

    report = {
        "total": stats.total,
        "levels": dict(stats.levels),
        "by_source": stats.by_source,
        "skipped": stats.skipped,
        "top_error_sources": top_error_sources,
        "first_timestamp": (
            stats.first_timestamp.isoformat()
            if stats.first_timestamp is not None else None
        ),
        "last_timestamp": (
            stats.last_timestamp.isoformat()
            if stats.last_timestamp is not None else None
        ),
    }

    return report


def write_json_report(report: dict, path: str | Path) -> None:
    """Записать отчет со статистикой в JSON-файл."""
    with open(path, "w", encoding="utf-8") as file:
        json.dump(report, file, ensure_ascii=False, indent=2)
