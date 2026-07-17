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

import json
from pathlib import Path
import runpy
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


def test_main_invokes_standalone_typer_app(monkeypatch: pytest.MonkeyPatch):
    calls = []

    monkeypatch.setattr(cli, "antenna_app", lambda: calls.append("called"))

    cli.main()

    assert calls == ["called"]


def test_module_entry_point_delegates_to_cli_main(monkeypatch: pytest.MonkeyPatch):
    calls = []

    monkeypatch.setattr(cli, "main", lambda: calls.append("called"))

    runpy.run_module("ansys.aedt.toolkits.antenna.__main__", run_name="__main__")

    assert calls == ["called"]


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
    assert properties.design_list["bowtie_normal"] == []
    assert properties.active_design == "bowtie-normal"
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


def test_helper_functions_cover_alias_parsing_and_file_inputs(
    tmp_path: Path,
):
    assert cli._resolve_antenna_type("bowtie") == "BowTieNormal"
    assert cli._resolve_antenna_type("BowTieNormal") == "BowTieNormal"

    assert cli._parse_param_list(None) == {}
    assert cli._parse_param_list(["count=2", "enabled=true", 'meta={"x": 1}', "label=test"]) == {
        "count": 2,
        "enabled": True,
        "meta": {"x": 1},
        "label": "test",
    }

    with pytest.raises(Exception, match="Invalid --param format"):
        cli._parse_param_list(["invalid"])

    yaml_file = tmp_path / "params.yaml"
    yaml_file.write_text("frequency: 2.1\nlength_unit: mm\n", encoding="utf-8")
    assert cli._load_params_file(str(yaml_file)) == {"frequency": 2.1, "length_unit": "mm"}

    null_json = tmp_path / "params-null.json"
    null_json.write_text("null", encoding="utf-8")
    assert cli._load_params_file(str(null_json)) == {}


def test_load_params_file_and_file_override_error_paths(tmp_path: Path):
    missing_file = tmp_path / "missing.json"
    with pytest.raises(Exception, match="was not found"):
        cli._load_params_file(str(missing_file))

    invalid_json = tmp_path / "invalid.json"
    invalid_json.write_text("{", encoding="utf-8")
    with pytest.raises(Exception, match="Unable to parse parameter file"):
        cli._load_params_file(str(invalid_json))

    list_json = tmp_path / "list.json"
    list_json.write_text("[]", encoding="utf-8")
    with pytest.raises(Exception, match="must contain a mapping"):
        cli._load_params_file(str(list_json))

    with pytest.raises(Exception, match="'synthesis' section"):
        cli._collect_file_overrides({"synthesis": []}, is_create=False)

    with pytest.raises(Exception, match="'setup' section"):
        cli._collect_file_overrides({"setup": []}, is_create=True)

    with pytest.raises(Exception, match="'param' section"):
        cli._collect_file_overrides({"param": []}, is_create=True)


def test_collect_file_overrides_and_merge_create_inputs(tmp_path: Path):
    synth_values, setup_values, extra_values = cli._collect_file_overrides(
        {
            "synthesis": {"frequency": 1.1},
            "setup": {"create_setup": False},
            "param": {"feed": "coax"},
            "substrate_height": 1.6,
            "sweep": 30,
            "custom_flag": True,
        },
        is_create=True,
    )

    assert synth_values == {"frequency": 1.1, "substrate_height": 1.6}
    assert setup_values == {"create_setup": False, "sweep": 30}
    assert extra_values == {"feed": "coax", "custom_flag": True}

    params_file = tmp_path / "create.json"
    params_file.write_text(
        json.dumps(
            {
                "synthesis": {"frequency": 1.5},
                "setup": {"create_setup": False, "sweep": 10},
                "param": {"feed": "probe"},
            }
        ),
        encoding="utf-8",
    )

    overrides, merged_setup, extra = cli._merge_cli_inputs(
        {
            "params_file": str(params_file),
            "param": ['feed={"type": "wave"}'],
            "frequency": 2.2,
            "length_unit": None,
            "substrate_height": None,
            "create_setup": True,
            "component_3d": False,
            "lattice_pair": True,
            "sweep": None,
            "num_cores": 6,
        },
        is_create=True,
    )

    assert overrides == {"frequency": 2.2}
    assert merged_setup == {
        "create_setup": True,
        "sweep": 10,
        "component_3d": False,
        "lattice_pair": True,
        "num_cores": 6,
    }
    assert extra == {"feed": {"type": "wave"}}


def test_project_and_design_resolution_helpers(monkeypatch: pytest.MonkeyPatch):
    assert cli._project_key(None) == ""
    assert cli._project_key("C:/tmp/demo_project.aedt") == "demo_project"

    project_list = ["DemoProject.aedt", "OtherProject.aedt"]
    assert cli._resolve_project_name("demoproject", project_list) == "DemoProject.aedt"
    assert cli._resolve_project_name("other", project_list) == "OtherProject.aedt"

    ambiguous_exact = ["DemoProject.aedt", "demoproject"]
    with pytest.raises(RuntimeError, match="ambiguous"):
        cli._resolve_project_name("demoproject", ambiguous_exact)

    ambiguous_partial = ["AlphaProject.aedt", "ProjectBeta.aedt"]
    with pytest.raises(RuntimeError, match="ambiguous"):
        cli._resolve_project_name("project", ambiguous_partial)

    with pytest.raises(RuntimeError, match="not found"):
        cli._resolve_project_name("missing", project_list)

    monkeypatch.setattr(cli, "generate_unique_project_name", lambda project_name=None: f"generated:{project_name}")
    assert cli._default_project_name("BowTieNormal") == "generated:bowtie_normal"

    properties = SimpleNamespace(
        project_list=["OnlyProject.aedt"],
        active_project="",
        design_list={},
    )
    assert cli._resolve_target_project({"project": None}, "BowTieNormal", properties) == "OnlyProject.aedt"

    properties.active_project = "CurrentProject.aedt"
    assert cli._resolve_target_project({"project": None}, "BowTieNormal", properties) == "CurrentProject.aedt"
    assert cli._resolve_target_project({"project": "OnlyProject"}, "BowTieNormal", properties) == "OnlyProject.aedt"

    empty_properties = SimpleNamespace(project_list=[], active_project="", design_list={})
    assert cli._resolve_target_project({"project": None}, "BowTieNormal", empty_properties) == "generated:bowtie_normal"

    cli._bootstrap_project_design_state(empty_properties)
    assert empty_properties.design_list == {}

    empty_properties.active_project = "C:/tmp/generated_project.aedt"
    cli._bootstrap_project_design_state(empty_properties)
    assert empty_properties.design_list == {"generated_project": []}

    assert cli._designs_for_project({}, None) == []
    assert cli._designs_for_project({"OnlyProject": ["A"]}, "OnlyProject.aedt") == ["A"]
    assert cli._designs_for_project({"OnlyProject.aedt": ["B"]}, "OnlyProject.aedt") == ["B"]
    assert cli._designs_for_project({"Other": ["C"]}, "OnlyProject.aedt") == []

    design_properties = SimpleNamespace(
        active_project="OnlyProject.aedt", design_list={"OnlyProject": ["BowTieNormal", "custom"]}
    )
    assert (
        cli._resolve_target_design({"design": "manual", "antenna_type": "bowtie"}, "BowTieNormal", design_properties)
        == "manual"
    )
    assert (
        cli._resolve_target_design({"design": None, "antenna_type": "bowtie"}, "BowTieNormal", design_properties)
        == "BowTieNormal"
    )
    assert (
        cli._resolve_target_design(
            {"design": None, "antenna_type": "missing-name"},
            "MissingClass",
            SimpleNamespace(active_project="OnlyProject.aedt", design_list={"OnlyProject": ["missing-name"]}),
        )
        == "missing-name"
    )
    assert (
        cli._resolve_target_design(
            {"design": None, "antenna_type": "unknown"},
            "MissingClass",
            SimpleNamespace(active_project="OnlyProject.aedt", design_list={"OnlyProject": []}),
        )
        == "missing-class"
    )


def test_build_signature_exposes_create_specific_options():
    synth_signature = cli._build_signature(is_create=False)
    create_signature = cli._build_signature(is_create=True)

    assert "port" not in synth_signature.parameters
    assert "create_setup" not in synth_signature.parameters
    assert "port" in create_signature.parameters
    assert "project" in create_signature.parameters
    assert "design" in create_signature.parameters
    assert "create_setup" in create_signature.parameters
    assert "component_3d" in create_signature.parameters
    assert "lattice_pair" in create_signature.parameters
    assert "sweep" in create_signature.parameters
    assert "num_cores" in create_signature.parameters
    assert "params_file" in create_signature.parameters
    assert "param" in create_signature.parameters


def test_list_and_synthesize_commands_support_json_mode(
    runner: CliRunner,
    mocked_cli_backend: dict,
    monkeypatch: pytest.MonkeyPatch,
):
    calls = []
    monkeypatch.setattr(cli.common, "json_mode", True)
    monkeypatch.setattr(cli.common, "print_output", lambda **kwargs: calls.append(kwargs))

    list_result = runner.invoke(cli.antenna_app, ["list"])
    synth_result = runner.invoke(cli.antenna_app, ["synthesize", "bowtie"])

    assert list_result.exit_code == 0
    assert synth_result.exit_code == 0
    assert calls[0]["data"]["antennas"] == cli.ANTENNA_REGISTRY
    assert calls[1]["data"] == {
        "antenna": "bowtie",
        "class": "BowTieNormal",
        "parameters": mocked_cli_backend["result"],
    }


def test_synthesize_and_create_commands_report_json_errors(
    runner: CliRunner,
    mocked_cli_backend: dict,
    monkeypatch: pytest.MonkeyPatch,
):
    calls = []
    monkeypatch.setattr(cli.common, "json_mode", True)
    monkeypatch.setattr(cli.common, "print_output", lambda **kwargs: calls.append(kwargs))

    mocked_cli_backend["result"] = False
    synth_result = runner.invoke(cli.antenna_app, ["synthesize", "bowtie"])
    create_result = runner.invoke(cli.antenna_app, ["create", "bowtie", "--port", "50051"])

    assert synth_result.exit_code == 1
    assert create_result.exit_code == 1
    assert calls[0] == {"error": "Synthesis failed for BowTieNormal."}
    assert calls[1] == {"error": "Antenna creation failed. Check AEDT connection and design state."}


def test_create_command_supports_json_mode_and_param_sections(
    runner: CliRunner,
    mocked_cli_backend: dict,
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
):
    calls = []
    monkeypatch.setattr(cli.common, "json_mode", True)
    monkeypatch.setattr(cli.common, "print_output", lambda **kwargs: calls.append(kwargs))

    params_file = tmp_path / "create.json"
    params_file.write_text(
        json.dumps(
            {
                "synthesis": {"frequency": 3.5},
                "setup": {"create_setup": False, "component_3d": True, "sweep": 15},
                "param": {"ignored_extra": "value"},
            }
        ),
        encoding="utf-8",
    )

    result = runner.invoke(
        cli.antenna_app,
        [
            "create",
            "bowtie",
            "--port",
            "50051",
            "--params-file",
            str(params_file),
            "--lattice-pair",
        ],
    )

    properties = mocked_cli_backend["properties"]

    assert result.exit_code == 0
    assert calls[-1]["data"] == {
        "antenna": "bowtie",
        "class": "BowTieNormal",
        "parameters": mocked_cli_backend["result"],
    }
    assert properties.antenna.synthesis.frequency == 3.5
    assert properties.antenna.setup.create_setup is False
    assert properties.antenna.setup.component_3d is True
    assert properties.antenna.setup.lattice_pair is True
    assert properties.antenna.setup.sweep == 15
