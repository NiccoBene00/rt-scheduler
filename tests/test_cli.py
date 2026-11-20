"""Tests for the command line: exit codes and printed verdict, one core."""

import pytest

from rtsched.cli import main


def write(tmp_path, text):
    """Write `text` to a temporary task file and return its path."""
    path = tmp_path / "taskset"
    path.write_text(text, encoding="utf-8")
    return str(path)


SYSTEM_30 = "0;2;8;8\n0;3;11;11\n0;5;15;15\n"
SYSTEM_47 = "0;7;10;10\n0;1;16;16\n4;3;15;15\n"


@pytest.mark.parametrize("text, algorithm, code, verdict", [
    (SYSTEM_30, "rm", 0, "schedulable: response times"),
    ("0;1;30;10\n3;1;5;10\n", "dm", 2, "unsupported: DM on an asynchronous"),
    ("0;3;4;4\n0;2;4;4\n", "edf", 3, "not schedulable (without simulation): U = 5/4 > 1"),
    (SYSTEM_47, "rm", 4, "not schedulable (simulation): tau2 misses"),
    (SYSTEM_47, "edf", 0, "schedulable: implicit deadlines"),
])
def test_exit_code_and_verdict(tmp_path, capsys, text, algorithm, code, verdict):
    assert main([write(tmp_path, text), "-a", algorithm]) == code
    assert verdict in capsys.readouterr().out # capsys is a pytest fixture that captures what the program prints. capsys.readouterr().out is the stdout text


def test_missing_file_is_invalid_input(tmp_path):
    assert main([str(tmp_path / "missing"), "-a", "rm"]) == 5


def test_bad_algorithm_is_invalid_input(tmp_path):
    with pytest.raises(SystemExit) as exit_info:
        main([write(tmp_path, SYSTEM_30), "-a", "llf"])
    assert exit_info.value.code == 5
