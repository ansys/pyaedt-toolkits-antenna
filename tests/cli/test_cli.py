# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

import json
from pathlib import Path
import sys
from types import ModuleType
from types import SimpleNamespace

import pytest
from typer.testing import CliRunner

from ansys.aedt.toolkits.antenna import cli


@pytest.fixture
def runner() -> CliRunner:
    return CliRunner()


@pytest.fixture
def mocked_cli_backend(monkeypatch: pytest.MonkeyPatch) -> dict:
    state = {
        "connect_design_result": True,
        "result": {"arm_length": 19.354, "port_gap": 0.968},
    }

    synthesis = SimpleNamespace(
        frequency=None,
        length_unit=None,
        substrate_height=None,
    )
    setup = SimpleNamespace(
        create_setup=False,
        component_3d=False,
        lattice_pair=False,
        sweep=None,
        num_cores=None,
    )
    properties = SimpleNamespace(
        antenna=SimpleNamespace(synthesis=synthesis, setup=setup),
        use_grpc=False,
        selected_process=None,
        project_list=["DemoProject.aedt"],
        active_project="DemoProject.aedt",
        design_list={"DemoProject": ["bowtie"]},
        active_design=None,
    )

    class DummyToolkitBackend:
        def launch_aedt(self):
            state["launch_aedt_called"] = True

        def wait_to_be_idle(self):
            state["wait_to_be_idle_called"] = True
            return True

        def connect_design(self, design_type: str):
            state["connect_design_called_with"] = design_type
            return state["connect_design_result"]

        def get_antenna(self, class_name: str, synth_only: bool):
            state["get_antenna_called_with"] = (class_name, synth_only)
            return state["result"]

    api_module = ModuleType("ansys.aedt.toolkits.antenna.backend.api")
    api_module.ToolkitBackend = DummyToolkitBackend

    models_module = ModuleType("ansys.aedt.toolkits.antenna.backend.models")
    models_module.properties = properties

    monkeypatch.setitem(sys.modules, "ansys.aedt.toolkits.antenna.backend.api", api_module)
    monkeypatch.setitem(sys.modules, "ansys.aedt.toolkits.antenna.backend.models", models_module)

    state["properties"] = properties
    return state


def test_list_command_displays_available_antennas(runner: CliRunner):
    cli_name, class_name = next(iter(cli.ANTENNA_REGISTRY.items()))

    result = runner.invoke(cli.antenna_app, ["list"])

    assert result.exit_code == 0
    assert "Available antenna types:" in result.output
    assert cli_name in result.output
    assert class_name in result.output


def test_synthesize_command_uses_params_file_and_cli_override(
    runner: CliRunner,
    mocked_cli_backend: dict,
    tmp_path: Path,
):
    params_file = tmp_path / "antenna.json"
    params_file.write_text(
        json.dumps({"frequency": 1.8, "substrate_height": 1.6, "length_unit": "mm"}),
        encoding="utf-8",
    )

    result = runner.invoke(
        cli.antenna_app,
        [
            "synthesize",
            "bowtie",
            "--params-file",
            str(params_file),
            "--frequency",
            "2.4",
        ],
    )

    properties = mocked_cli_backend["properties"]

    assert result.exit_code == 0
    assert "Synthesis results for bowtie (BowTieNormal):" in result.output
    assert mocked_cli_backend["get_antenna_called_with"] == ("BowTieNormal", True)
    assert properties.antenna.synthesis.frequency == 2.4
    assert properties.antenna.synthesis.substrate_height == 1.6
    assert properties.antenna.synthesis.length_unit == "mm"


def test_synthesize_command_returns_error_for_unknown_antenna(runner: CliRunner):
    result = runner.invoke(cli.antenna_app, ["synthesize", "not-an-antenna"])

    assert result.exit_code == 1
    assert "Unknown antenna type 'not-an-antenna'" in result.output


def test_create_command_initializes_connection_and_setup_options(
    runner: CliRunner,
    mocked_cli_backend: dict,
):
    result = runner.invoke(
        cli.antenna_app,
        [
            "create",
            "bowtie",
            "--port",
            "50051",
            "--project",
            "DemoProject",
            "--create-setup",
            "--component-3d",
            "--sweep",
            "25",
            "--num-cores",
            "8",
        ],
    )

    properties = mocked_cli_backend["properties"]

    assert result.exit_code == 0
    assert "Creating bowtie (BowTieNormal) on port 50051..." in result.output
    assert mocked_cli_backend["launch_aedt_called"] is True
    assert mocked_cli_backend["wait_to_be_idle_called"] is True
    assert mocked_cli_backend["connect_design_called_with"] == "HFSS"
    assert mocked_cli_backend["get_antenna_called_with"] == ("BowTieNormal", False)
    assert properties.use_grpc is True
    assert properties.selected_process == 50051
    assert properties.active_project == "DemoProject.aedt"
    assert properties.active_design == "bowtie"
    assert properties.antenna.setup.create_setup is True
    assert properties.antenna.setup.component_3d is True
    assert properties.antenna.setup.sweep == 25
    assert properties.antenna.setup.num_cores == 8


def test_create_command_creates_project_for_empty_session(
    runner: CliRunner,
    mocked_cli_backend: dict,
    monkeypatch: pytest.MonkeyPatch,
):
    properties = mocked_cli_backend["properties"]
    properties.project_list = []
    properties.active_project = ""
    properties.design_list = {}

    generated_project = "C:\\Temp\\bowtie_normal.aedt"
    monkeypatch.setattr(cli, "generate_unique_project_name", lambda project_name=None: generated_project)

    result = runner.invoke(cli.antenna_app, ["create", "bowtie", "--port", "50051"])

    assert result.exit_code == 0
    assert properties.active_project == generated_project
    assert properties.active_design == "bowtie"
    assert mocked_cli_backend["connect_design_called_with"] == "HFSS"
    assert mocked_cli_backend["get_antenna_called_with"] == ("BowTieNormal", False)


def test_create_command_returns_error_when_design_connection_fails(
    runner: CliRunner,
    mocked_cli_backend: dict,
):
    mocked_cli_backend["connect_design_result"] = False

    result = runner.invoke(cli.antenna_app, ["create", "bowtie", "--port", "50051"])

    assert result.exit_code == 1
    assert "Unable to connect to the selected HFSS design." in result.output
