import json
import subprocess
import sys


def test_cli_json_report(tmp_path):
    input_file = tmp_path / "events.csv"
    report_file = tmp_path / "report.json"

    input_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-25T10:00:00,INFO,api,Server started\n",
        encoding="utf-8"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "streamstats",
            "analyze",
            str(input_file),
            "--format",
            "csv",
            "--output",
            str(report_file)
        ],
        capture_output=True,
        text=True,
        check=False
    )

    assert result.returncode == 0
    assert report_file.exists()

    report = json.loads(report_file.read_text(encoding="utf-8"))
    assert report["total"] == 1
    assert report["levels"] == {"INFO": 1}


def test_cli_report_to_console(tmp_path):
    input_file = tmp_path / "events.csv"

    input_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-25T10:00:00,INFO,api,Server started\n",
        encoding="utf-8"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "streamstats",
            "analyze",
            str(input_file),
            "--format",
            "csv"
        ],
        capture_output=True,
        text=True,
        check=False
    )

    assert result.returncode == 0

    report = json.loads(result.stdout)
    assert report["total"] == 1


def test_cli_multiple_files(tmp_path):
    first_file = tmp_path / "first.csv"
    second_file = tmp_path / "second.csv"

    first_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-25T10:00:00,INFO,api,Started\n",
        encoding="utf-8"
    )

    second_file.write_text(
        "timestamp,level,source,message\n"
        "2026-10-25T11:00:00,ERROR,database,Failed\n",
        encoding="utf-8"
    )

    result = subprocess.run(
        [
            sys.executable,
            "-m",
            "streamstats",
            "analyze",
            str(first_file),
            str(second_file),
            "--format",
            "csv"
        ],
        capture_output=True,
        text=True,
        check=False
    )

    assert result.returncode == 0

    report = json.loads(result.stdout)

    assert report["total"] == 2
    assert report["levels"] == {"INFO": 1, "ERROR": 1}
    assert report["by_source"]["api"]["total"] == 1
    assert report["by_source"]["database"]["total"] == 1
