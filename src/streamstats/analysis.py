from .models import Event, Stats


def update_stat(event: Event, stats: Stats) -> None:
    """Обновить статистику на основе одного события."""

    stats.total += 1
    stats.levels[event.level] += 1

    # Для каждого источника считаем события и ошибки
    source = event.source
    if source not in stats.by_source:
        stats.by_source[source] = {"total": 0, "errors": 0}
    stats.by_source[source]["total"] += 1

    if event.level in ("ERROR", "CRITICAL"):
        stats.by_source[source]["errors"] += 1

    # Находим первую и последнюю временные метки
    if stats.first_timestamp is None or event.timestamp < stats.first_timestamp:
        stats.first_timestamp = event.timestamp
    if stats.last_timestamp is None or event.timestamp > stats.last_timestamp:
        stats.last_timestamp = event.timestamp


def get_top_error_sources(stats: Stats) -> list[tuple[str, dict]]:
    """Получить топ-5 источников по количеству ошибок."""

    # Сортируем источники по убыванию ошибок, 
    # а в случае равенства - по имени
    sources = sorted(
        stats.by_source.items(),
        key=lambda item: (-item[1]["errors"], item[0])
    )
    return sources[:5]


def merge_stats(target: Stats, source: Stats) -> None:
    """Объединить статистику source с target."""

    target.total += source.total
    target.levels.update(source.levels)
    target.skipped += source.skipped

    # Суммируем счетчики событий и ошибок для каждого источника
    for name, counts in source.by_source.items():
        if name not in target.by_source:
            target.by_source[name] = {"total": 0, "errors": 0}
        target.by_source[name]["total"] += counts["total"]
        target.by_source[name]["errors"] += counts["errors"]

    # Находим самые раннюю и позднюю временные метки
    if source.first_timestamp is not None and (
        target.first_timestamp is None 
        or source.first_timestamp < target.first_timestamp
    ):
        target.first_timestamp = source.first_timestamp

    if source.last_timestamp is not None and (
        target.last_timestamp is None
        or source.last_timestamp > target.last_timestamp
    ):
        target.last_timestamp = source.last_timestamp
