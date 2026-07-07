# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 Synopsys, Inc. and ANSYS, Inc. All rights reserved.
# SPDX-License-Identifier: MIT
#
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from __future__ import annotations

import sys
from types import ModuleType

import pytest

from ansys.aedt.toolkits.antenna import run_toolkit


@pytest.mark.parametrize(
    ("argv", "expected"),
    [
        ([], False),
        (["list"], True),
        (["synthesize", "--help"], True),
        (["--help"], True),
        (["gui"], False),
        (["--gui"], False),
    ],
)
def test_should_run_cli(argv: list[str], expected: bool):
    assert run_toolkit._should_run_cli(argv) is expected


def test_run_cli_delegates_to_cli_main_and_restores_sys_argv(monkeypatch: pytest.MonkeyPatch):
    cli_calls = []
    fake_cli_module = ModuleType("ansys.aedt.toolkits.antenna.cli")
    fake_cli_module.main = lambda: cli_calls.append(list(sys.argv))
    monkeypatch.setitem(sys.modules, "ansys.aedt.toolkits.antenna.cli", fake_cli_module)

    original_argv = ["launcher.exe", "original"]
    monkeypatch.setattr(sys, "argv", original_argv[:])

    exit_code = run_toolkit.run_cli(["list"])

    assert exit_code == 0
    assert cli_calls == [["launcher.exe", "list"]]
    assert sys.argv == original_argv


def test_main_routes_cli_arguments_to_run_cli(monkeypatch: pytest.MonkeyPatch):
    calls = []
    monkeypatch.setattr(run_toolkit, "run_cli", lambda argv=None: calls.append(("cli", argv)) or 0)
    monkeypatch.setattr(run_toolkit, "run_gui", lambda: calls.append(("gui", None)) or 0)

    exit_code = run_toolkit.main(["list"])

    assert exit_code == 0
    assert calls == [("cli", ["list"])]


def test_main_calls_freeze_support_before_dispatch(monkeypatch: pytest.MonkeyPatch):
    calls = []

    monkeypatch.setattr(run_toolkit.multiprocessing, "freeze_support", lambda: calls.append("freeze"))
    monkeypatch.setattr(run_toolkit, "run_cli", lambda argv=None: calls.append(("cli", argv)) or 0)
    monkeypatch.setattr(run_toolkit, "run_gui", lambda: calls.append(("gui", None)) or 0)

    exit_code = run_toolkit.main(["list"])

    assert exit_code == 0
    assert calls == ["freeze", ("cli", ["list"])]


def test_main_does_not_dispatch_pyinstaller_multiprocessing_args(monkeypatch: pytest.MonkeyPatch):
    calls = []

    def fake_freeze_support():
        calls.append("freeze")
        raise SystemExit(0)

    monkeypatch.setattr(run_toolkit.multiprocessing, "freeze_support", fake_freeze_support)
    monkeypatch.setattr(run_toolkit, "run_cli", lambda argv=None: calls.append(("cli", argv)) or 0)
    monkeypatch.setattr(run_toolkit, "run_gui", lambda: calls.append(("gui", None)) or 0)

    with pytest.raises(SystemExit, match="0"):
        run_toolkit.main(["--multiprocessing-fork", "parent_pid=1", "pipe_handle=2"])

    assert calls == ["freeze"]


@pytest.mark.parametrize("argv", [[], ["gui"], ["--gui"]])
def test_main_routes_gui_launches_to_run_gui(monkeypatch: pytest.MonkeyPatch, argv: list[str]):
    calls = []
    monkeypatch.setattr(run_toolkit, "run_cli", lambda argv=None: calls.append(("cli", argv)) or 0)
    monkeypatch.setattr(run_toolkit, "run_gui", lambda: calls.append(("gui", None)) or 0)

    exit_code = run_toolkit.main(argv)

    assert exit_code == 0
    assert calls == [("gui", None)]
