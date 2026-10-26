import argparse
import json
import logging
import sys

from .analysis import update_stat
from .errors import StreamStatsError
from .models import Stats
from .parsers import parse_csv, parse_jsonl
from .report import build_report, write_json_report

logging.basicConfig(
    level=logging.WARNING,
    format="%(levelname)s: %(message)s",
)
logger = logging.getLogger(__name__)

def handle_invalid(error: Exception, stats: Stats) -> None:
    """Подсчитать количество пропущенных событий и записать предупреждение в log."""
    stats.skipped += 1
    logger.warning("%s", error)


def main() -> None:
    """Запустить анализ данных через CLI.

    Обрабатывает аргументы и формирует отчет 
    со статистикой по входным файлам.
    """
    
    parser = argparse.ArgumentParser(description="Анализ CSV и JSONL событий")
    subparsers = parser.add_subparsers(
        dest="command",
        required=True
    )

    analyze_parser = subparsers.add_parser(
        "analyze",
        help="Анализировать файлы с событиями"
    )
    analyze_parser.add_argument(
        "inputs",
        nargs="+",
        help="Пути к входным файлам"
    )
    analyze_parser.add_argument(
        "--format",
        choices=("csv", "jsonl"),
        required=True,
        help="Формат входных файлов"
    )
    analyze_parser.add_argument(
        "--output",
        help="Путь к JSON-отчету со статистикой"
    )
    analyze_parser.add_argument(
        "--skip-invalid",
        action="store_true",
        help="Пропускать некорректные события с пометкой WARNING",
    )

    args = parser.parse_args()
    stats = Stats()

    # Выбираем парсер по формату файлов: csv или jsonl
    if args.format == "csv":
        parse_file = parse_csv
    else:
        parse_file = parse_jsonl

    # Собираем статистику по входным файлам
    try:
        for path in args.inputs:
            for event in parse_file(path, skip_invalid=args.skip_invalid, 
                                    on_invalid=lambda error: 
                                    handle_invalid(error, stats)):
                  update_stat(event, stats)
    except StreamStatsError as error:
        print(f"{path}: {error}", file=sys.stderr)
        sys.exit(2)

    # Формируем и выводим отчет
    report = build_report(stats)

    if args.output:
        write_json_report(report, args.output)
    else:
        print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
