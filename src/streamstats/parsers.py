import csv
import json
from collections.abc import Callable, Iterator
from datetime import datetime
from pathlib import Path

from .constants import ALLOWED_LEVELS
from .errors import InputFileError, InvalidEventError, InvalidTimestampError
from .models import Event


def make_event(raw: dict[str, object], line_number: int) -> Event:
    """Создать событие из словаря с исходными данными.
    
    Проверяет корректность полей событий и 
    преобразует временную метку в datetime.

    Args:
        raw: Словарь с данными события.
        line_number: Номер строки с данными события.

    Returns:
        Объект Event с проверенными данными.

    Raises:
        InvalidTimestampError: Если временная метка некорректна.
        InvalidEventError: Если остальные поля события некорректны.
    """

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

    # Преобразуем врменную метку в datetime
    try:
        timestamp = datetime.fromisoformat(timestamp_raw)
    except ValueError:
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


def parse_csv(
        path: str | Path, 
        skip_invalid: bool = False, 
        on_invalid: Callable[[Exception], None] | None = None
) -> Iterator[Event]:
    """Прочитать CSV-файл и вернуть корректные события.

    В режиме skip_invalid=True игнорирует некорректные события,
    а ошибки передаются в on_invalid.
    """

    # Открываем файл и проверяем ошибки доступа
    try:
        with open(path, encoding="utf-8-sig", newline="") as file:
            # Читаем образец файла, чтобы определить разделитель
            sample = file.read(8192)
            file.seek(0)

            if not sample:
                # Если файл пустой, то ошибки нет
                return
            
            try:
                dialect = csv.Sniffer().sniff(sample, delimiters=",;\t")
            except csv.Error:
                dialect = csv.excel
            
            reader = csv.reader(file, dialect)
            headers = next(reader, None) # Получаем заголовки столбцов таблицы
            if headers is None:
                return
            headers = [header.strip() for header in headers]
            
            required = {"timestamp", "level", "source", "message"}
            if not required.issubset(headers):
                missing = required - set(headers)
                raise InvalidEventError(
                    f"Строка 1: отсутствуют обязательные столбцы {sorted(missing)}."
                )

            # Читаем файл построчно
            for row in reader:
                line_number = reader.line_num

                try:
                    if len(row) != len(headers):
                        raise InvalidEventError(
                            f"Строка {line_number}: количество полей "
                            "не совпадает с заголовком CSV."
                        )

                    raw = dict(zip(headers, row))
                    event = make_event(raw, line_number)

                # При включенном skip_invalid пропускаем некорректную запись
                except (InvalidEventError, InvalidTimestampError) as error:
                    if not skip_invalid:
                        raise
                    if on_invalid is not None:
                        on_invalid(error)

                    continue
                
                yield event
    except OSError as error:
        raise InputFileError(
            f"Не удалось открыть файл {path}: {error}"
        ) from error


def parse_jsonl(
    path: str | Path,
    skip_invalid: bool = False,
    on_invalid: Callable[[Exception], None] | None = None
) -> Iterator[Event]:

    # Открываем файл и проверяем ошибки доступа
    try:
        with open(path, encoding="utf-8-sig") as file:
            for line_number, line in enumerate(file, start=1):
                try:
                    raw = json.loads(line)

                    if not isinstance(raw, dict):
                        raise InvalidEventError(
                            f"Строка {line_number}: JSON должен содержать "
                            "объект с данными события."
                        )

                    event = make_event(raw, line_number)

                except json.JSONDecodeError as json_error:
                    error = InvalidEventError(
                        f"Строка {line_number}: некорректный JSON."
                    )

                    if not skip_invalid:
                        raise error from json_error
                    if on_invalid is not None:
                        on_invalid(error)

                    continue

                # При включенном skip_invalid пропускаем некорректную запись
                except (InvalidEventError, InvalidTimestampError) as error:
                    if not skip_invalid:
                        raise
                    if on_invalid is not None:
                        on_invalid(error)

                    continue

                yield event
                
    except OSError as error:
        raise InputFileError(
            f"Не удалось открыть файл {path}: {error}"
        ) from error
    