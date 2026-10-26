class StreamStatsError(Exception):
    """Базовое исключение проекта StreamStats."""


class UnsupportedFormatError(StreamStatsError):
    """Исключение для неподдерживаемого формата файла."""


class InvalidEventError(StreamStatsError):
    """Исключение для неверного события."""


class InvalidTimestampError(StreamStatsError):
    """Исключение для неверной временной метки."""


class CLIConfigError(StreamStatsError):
    """Исключение для ошибки конфигурации CLI."""


class InputFileError(StreamStatsError):
    """Исключение при ошибке доступа к файлу."""
