import csv
import json
from collections.abc import Iterator
from pathlib import Path
from datetime import datetime

from models import Event
from streamstats.errors import (
    InvalidEventError,
    InvalidTimestampError,
)
from constants import ALLOWED_LEVELS


def make_event(raw: dict[str, str], line_number: int) -> Event:
    timestamp_raw = raw.get("timestamp")
    level = raw.get("level")
    source = raw.get("source")
    message = raw.get("message")

    # Проверка timestamp
    if not isinstance(timestamp_raw, str):
        raise InvalidTimestampError(
            f"Строка {line_number}. "
            f"Некорректная временная метка: {timestamp_raw}. "
            "Временная метка должна быть в строковом виде."
        )
    if not timestamp_raw.strip():
        raise InvalidTimestampError(
                    f"Строка {line_number}. "
                    f"Некорректная временная метка: {timestamp_raw}. "
                    "Временная метка не может быть пустой строкой."
                )

    # Переводим timestamp из строки в datetime
    try:
        timestamp = datetime.fromisoformat(timestamp_raw)
    except ValueError as error:
        raise InvalidTimestampError(
            f"Строка {line_number}. "
            f"Некорректная временная метка: {timestamp_raw}. "
            "Формат должен соответствовать стандарту ISO 8601."
        )

    # Проверка level
    if not isinstance(level, str):
        raise InvalidEventError(
            f"Строка {line_number}. "
            f"Некорректный уровень события: {level}. "
            "Уровень должен быть в строковом виде."
        )
    if level not in ALLOWED_LEVELS:
        raise InvalidEventError(
            f"Строка {line_number}. "
            f"Несуществующий уровень события: {level}."
        )

    # Проверка source
    if not isinstance(source, str):
        raise InvalidEventError(
            f"Строка {line_number}. "
            f"Некорректный источник: {source}. "
            "Источник должен быть в строковом виде."
        )
    if not source.strip():
        raise InvalidEventError(
            f"Строка {line_number}. "
            f"Некорректный источник: {source}. "
            "Источник не может быть пустой строкой."
        )

    # Проверка message
    if not isinstance(message, str):
        raise InvalidEventError(
            f"Строка {line_number}. "
            f"Некорректное сообщение: {message}. "
            "Сообщение должно быть в строковом виде."
        )

    return Event(
        timestamp=timestamp,
        level=level,
        source=source,
        message=message,
    )


def parse_csv(path: str | Path) -> Iterator[Event]:
    with open(path, encoding="utf-8-sig", newline="") as file:
        
        # Читаем часть файла - образец
        sample = file.read(8192)
        file.seek(0)

        if not sample:
            # Если файл пустой, то ошибки нет
            return
        
        try:
            dialect = csv.Sniffer().sniff(sample, delimiters=",;\t") # Определяем формат csv с помощью sniff
        except csv.Error:
            dialect = csv.excel
        
        reader = csv.reader(file, dialect) # Разбиваем строки на отдельные поля по разделителю
        headers = next(reader, None) # Получаем заголовки столбцов таблицы
        if headers is None:
            return
        headers = [header.strip() for header in headers]
        
        required = {"timestamp", "level", "source", "message"}
        if not required.issubset(headers):
            missing = required - set(headers) # Недостающие заголовки
            raise InvalidEventError(
                f"Строка 1: отсутствуют обязательные столбцы {sorted(missing)}."
            )

        # Читаем файл построчно
        for row in reader:
            line_number = reader.line_num
            if len(row) != len(headers):
                raise InvalidEventError(
                    f"Строка {line_number}: количество полей "
                    "не совпадает с заголовком CSV."
                )
            raw = dict(zip(headers, row))
            yield make_event(raw, line_number)


def parse_jsonl(path: str | Path) -> Iterator[Event]:
    with open(path, encoding="utf-8-sig") as file:

        for line_number, line in enumerate(file, start=1):
            try:
                raw = json.loads(line)
            except json.JSONDecodeError:
                raise InvalidEventError(
                    f"Строка {line_number}: некорректный JSON."
                )
            
            if not isinstance(raw, dict):
                raise InvalidEventError(
                    f"Строка {line_number}: JSON должен содержать объект с данными события."
                )

            yield make_event(raw, line_number)
