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

# --- several cores -----------------------------------------------------------------

def test_cores_are_checked_one_by_one(tmp_path, capsys):
    # U = 0.1, 0.1, 0.4, 0.5, 0.7 with wf on 3 cores: [tau5], [tau2, tau4], [tau1, tau3]
    path = write(tmp_path, "0;1;10;10\n0;1;10;10\n0;4;10;10\n0;5;10;10\n0;7;10;10\n")
    assert main([path, "-a", "edf", "-m", "3", "-h", "wf"]) == 0
    out = capsys.readouterr().out
    assert "core 1 (tau5): schedulable" in out
    assert "core 3 (tau1, tau3): schedulable" in out


def test_empty_cores_are_skipped(tmp_path, capsys):
    assert main([write(tmp_path, "0;1;4;4\n"), "-a", "rm", "-m", "4"]) == 0
    assert "core 2" not in capsys.readouterr().out


def test_partitioning_fails(tmp_path, capsys):
    # du order 0.6, 0.5, 0.5, 0.4 on 2 cores: next fit cannot place 0.4
    path = write(tmp_path, "0;5;10;10\n0;6;10;10\n0;4;10;10\n0;5;10;10\n")
    assert main([path, "-a", "edf", "-m", "2", "-h", "nf"]) == 1
    assert "partitioning failed" in capsys.readouterr().out


def test_heuristic_changes_the_verdict(tmp_path, capsys):
    # two tasks of U = 1/2: ff packs both on core 1, where RM misses (U = 1);
    # wf puts one on each core
    path = write(tmp_path, "0;2;4;4\n0;3;6;6\n")
    assert main([path, "-a", "rm", "-m", "2", "-h", "ff"]) == 3
    assert main([path, "-a", "rm", "-m", "2", "-h", "wf"]) == 0
    assert "core 2 (tau2): schedulable" in capsys.readouterr().out


def test_stops_at_the_first_failing_core(tmp_path, capsys):
    # wf on 2 cores: core 1 gets tau1 (C > D, exit 3), core 2 is never printed
    path = write(tmp_path, "0;3;2;10\n0;1;10;10\n")
    assert main([path, "-a", "edf", "-m", "2", "-h", "wf"]) == 3
    assert "core 2" not in capsys.readouterr().out


# --- bonus: Gantt chart --------------------------------------------------------------

def test_plot_one_core(tmp_path):
    png = tmp_path / "gantt.png"
    assert main([write(tmp_path, SYSTEM_30), "-a", "rm", "--plot", str(png)]) == 0
    assert png.is_file()


def test_plot_one_file_per_core(tmp_path):
    png = tmp_path / "gantt.png"
    path = write(tmp_path, "0;2;4;4\n0;3;6;6\n")
    assert main([path, "-a", "rm", "-m", "2", "-h", "wf", "--plot", str(png)]) == 0
    assert (tmp_path / "gantt-core1.png").is_file()
    assert (tmp_path / "gantt-core2.png").is_file()


def test_plot_does_not_change_the_verdict(tmp_path):
    # system 47 under RM: 4 with or without the chart (the chart has its own simulation)
    path = write(tmp_path, SYSTEM_47)
    assert main([path, "-a", "rm", "--plot", str(tmp_path / "gantt.png")]) == main([path, "-a", "rm"]) == 4


def test_no_plot_when_unsupported(tmp_path):
    png = tmp_path / "gantt.png"
    assert main([write(tmp_path, "0;1;30;10\n3;1;5;10\n"), "-a", "dm", "--plot", str(png)]) == 2
    assert not png.exists()
