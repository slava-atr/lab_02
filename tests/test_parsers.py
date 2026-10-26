import json

import pytest

from streamstats.errors import InvalidEventError
from streamstats.parsers import parse_csv, parse_jsonl


def test_parse_csv_success(tmp_path):
    path = tmp_path / "events.csv"

    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-25T10:00:00,INFO,api,Server started\n",
        encoding="utf-8",
    )

    events = list(parse_csv(path))

    assert len(events) == 1
    assert events[0].level == "INFO"
    assert events[0].source == "api"
    assert events[0].message == "Server started"


def test_parse_jsonl_success(tmp_path):
    path = tmp_path / "events.jsonl"

    event = {
        "timestamp": "2026-10-25T10:00:00",
        "level": "INFO",
        "source": "api",
        "message": "Server started",
    }
    path.write_text(
        json.dumps(event) + "\n",
        encoding="utf-8",
    )
    
    events = list(parse_jsonl(path))

    assert len(events) == 1
    assert events[0].level == "INFO"
    assert events[0].source == "api"
    assert events[0].message == "Server started"


def test_parse_empty_csv(tmp_path):
    path = tmp_path / "empty.csv"
    path.write_text("", encoding="utf-8")

    events = list(parse_csv(path))

    assert events == []


def test_parse_empty_jsonl(tmp_path):
    path = tmp_path / "empty.jsonl"
    path.write_text("", encoding="utf-8")

    events = list(parse_jsonl(path))

    assert events == []


def test_parse_invalid_csv(tmp_path):
    path = tmp_path / "invalid.csv"

    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-25T10:00:00,INVALID,api,Bad event\n",
        encoding="utf-8",
    )

    with pytest.raises(InvalidEventError):
        list(parse_csv(path))


def test_parse_invalid_jsonl(tmp_path):
    path = tmp_path / "invalid.jsonl"

    path.write_text(
        '{"timestamp":"2026-10-25T10:00:00",'
        '"level":"INVALID","source":"api","message":"Bad event"}\n',
        encoding="utf-8",
    )

    with pytest.raises(InvalidEventError):
        list(parse_jsonl(path))


def test_parse_csv_skip_invalid(tmp_path):
    path = tmp_path / "invalid.csv"

    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-25T10:00:00,INFO,api,Good event\n"
        "2026-10-25T10:01:00,INVALID,api,Bad event\n",
        encoding="utf-8",
    )

    errors = []
    events = list(
        parse_csv(path, skip_invalid=True, on_invalid=errors.append)
    )

    assert len(events) == 1
    assert events[0].message == "Good event"
    assert len(errors) == 1


def test_parse_jsonl_skip_invalid(tmp_path):
    path = tmp_path / "invalid.jsonl"

    path.write_text(
        '{"timestamp":"2026-10-25T10:00:00",'
        '"level":"INFO","source":"api","message":"Good event"}\n'
        '{"timestamp":"2026-10-25T10:01:00",'
        '"level":"INVALID","source":"api","message":"Bad event"}\n',
        encoding="utf-8",
    )

    errors = []
    events = list(
        parse_jsonl(path, skip_invalid=True, on_invalid=errors.append)
    )

    assert len(events) == 1
    assert events[0].message == "Good event"
    assert len(errors) == 1


def test_parse_csv_unicode(tmp_path):
    path = tmp_path / "unicode.csv"
    
    path.write_text(
        "timestamp,level,source,message\n"
        "2026-10-25T10:00:00,ERROR,служба,Ошибка подключения\n",
        encoding="utf-8",
    )

    events = list(parse_csv(path))

    assert events[0].source == "служба"
    assert events[0].message == "Ошибка подключения"


def test_parse_jsonl_unicode(tmp_path):
    path = tmp_path / "unicode.jsonl"

    path.write_text(
        '{"timestamp":"2026-10-25T10:00:00",'
        '"level":"ERROR","source":"служба",'
        '"message":"Ошибка подключения"}\n',
        encoding="utf-8",
    )

    events = list(parse_jsonl(path))

    assert events[0].source == "служба"
    assert events[0].message == "Ошибка подключения"

