from dataclasses import dataclass
from datetime import datetime


@dataclass(frozen=True, slots=True)
class Event:
    timestamp: datetime
    level: str
    source: str
    message: str

# from streamstats.errors import (
#     InvalidEventError,
#     InvalidTimestampError,
# )


# class Event:
#     def __init__(self, timestamp, level, source, message):
#         allowed_levels = ("DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL")

#         # Проверка полей на ввод
#         # timestamp
#         if not isinstance(timestamp, str):
#             raise InvalidTimestampError(
#                 f"Некорректная временная метка: {timestamp}. "
#                 "Временная метка должна быть в строковом виде."
#             )
#         try:
#             datetime.fromisoformat(timestamp)
#         except ValueError:
#             raise InvalidTimestampError(
#                 f"Некорректная временная метка: {timestamp}. "
#                 "Формат должен соответствовать стандарту ISO 8601."
#             )

#         # level
#         if not isinstance(level, str):
#             raise InvalidEventError(
#                 f"Некорретный уровень события: {level}. "
#                 "Уровень должен быть в строковом виде."
#             )
#         if level not in allowed_levels:
#             raise InvalidEventError(
#                 f"Несуществующий уровень события: {level}."
#             )

#         # source
#         if not isinstance(source, str):
#             raise InvalidEventError(
#                 f"Некорректный источник: {source}. "
#                 "Источник должен быть в строковом виде."
#             )
#         if not source.strip():
#             raise InvalidEventError(
#                 f"Некорректный источник: {source}. "
#                 "Источник не может быть пустой строкой."
#             )

#         # message
#         if not isinstance(message, str):
#             raise InvalidEventError(
#                 f"Некорректное сообщение: {message}. "
#                 "Сообщение должно быть в строковом виде."
#             )

#         self.timestamp = timestamp
#         self.level = level
#         self.source = source
#         self.message = message
