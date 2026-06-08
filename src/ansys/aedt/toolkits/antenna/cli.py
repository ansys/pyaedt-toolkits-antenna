# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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

"""Antenna toolkit CLI extension for ``pyaedt``.

CLI options for the ``synthesize`` and ``create`` commands are **auto-generated**
from the :class:`Synthesis` Pydantic model.  Adding a new field to that model
automatically exposes it as a ``--<field-name>`` flag — no manual CLI changes
required.
"""

from __future__ import annotations

import inspect
import json
from pathlib import Path
import re
from typing import Dict
from typing import List
from typing import Optional
from typing import get_origin

from ansys.aedt.core.cli import common
import typer

from ansys.aedt.toolkits.antenna.backend import antenna_models
from ansys.aedt.toolkits.antenna.backend.models import Synthesis

_CAMEL_BOUNDARY_1 = re.compile(r"(.)([A-Z][a-z]+)")
_CAMEL_BOUNDARY_2 = re.compile(r"([a-z0-9])([A-Z])")

# Fields whose types are too complex for a simple CLI option.
_SKIP_FIELDS = {"material_properties", "origin"}


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def _python_type_for_annotation(annotation):
    """Return a scalar Python type for *annotation*, or ``None`` if unsupported."""
    origin = get_origin(annotation)
    if origin in (list, List, dict, Dict):
        return None
    type_map = {float: float, int: int, bool: bool, str: str}
    return type_map.get(annotation)


def _camel_to_kebab(value: str) -> str:
    """Convert ``CamelCase`` names to ``kebab-case``."""
    value = _CAMEL_BOUNDARY_1.sub(r"\1-\2", value)
    value = _CAMEL_BOUNDARY_2.sub(r"\1-\2", value)
    return value.replace("_", "-").lower()


def _normalize_cli_name(value: str) -> str:
    """Normalize user-facing antenna names for matching."""
    return value.strip().lower().replace("_", "-")


def _build_cli_name(module_slug: str, class_name: str) -> str:
    """Build a stable CLI name from an antenna class and its source module."""
    family_tokens = module_slug.split("-")
    family_camel = "".join(token.capitalize() for token in family_tokens)
    class_slug = _camel_to_kebab(class_name)

    if class_name.lower().startswith(family_camel.lower()):
        suffix_slug = _camel_to_kebab(class_name[len(family_camel) :]).strip("-")
        return module_slug if not suffix_slug else f"{module_slug}-{suffix_slug}"

    compact_family = module_slug.replace("-", "")
    compact_class = class_slug.replace("-", "")
    if compact_family in compact_class:
        return class_slug

    class_tokens = class_slug.split("-")
    overlap = 0
    for family_token, class_token in zip(family_tokens, class_tokens):
        if family_token != class_token:
            break
        overlap += 1

    if overlap:
        class_tokens = class_tokens[overlap:]

    return "-".join(family_tokens + class_tokens)


def _iter_antenna_classes():
    """Yield the antenna model classes exported by the backend package."""
    for name, value in vars(antenna_models).items():
        if not inspect.isclass(value):
            continue
        if value.__name__ != name:
            continue
        if not value.__module__.startswith("ansys.aedt.toolkits.antenna.backend.antenna_models"):
            continue
        yield value


def _discover_antennas() -> tuple[dict[str, str], dict[str, list[str]], dict[str, str]]:
    """Discover supported antennas from the exported backend models."""
    registry: dict[str, str] = {}
    categories: dict[str, list[str]] = {}
    aliases: dict[str, str] = {}

    for antenna_class in sorted(_iter_antenna_classes(), key=lambda cls: (cls.__module__, cls.__name__)):
        module_name = antenna_class.__module__.rsplit(".", 1)[-1]
        module_slug = module_name.replace("_", "-")
        category = module_name.replace("_", " ").title()
        class_name = antenna_class.__name__
        cli_name = _build_cli_name(module_slug, class_name)

        registry[cli_name] = class_name
        categories.setdefault(category, []).append(cli_name)

        for alias in {
            cli_name,
            class_name,
            class_name.lower(),
            _camel_to_kebab(class_name),
        }:
            aliases.setdefault(_normalize_cli_name(alias), class_name)

        if cli_name.endswith("-normal"):
            aliases.setdefault(cli_name[: -len("-normal")], class_name)

    ordered_categories = {name: sorted(entries) for name, entries in sorted(categories.items())}
    return registry, ordered_categories, aliases


ANTENNA_REGISTRY, _CATEGORIES, _ANTENNA_ALIASES = _discover_antennas()
_CLASS_TO_CLI = {value: key for key, value in ANTENNA_REGISTRY.items()}


def _resolve_antenna_type(antenna_type: str) -> str:
    """Convert a CLI antenna name to its class name, or raise."""
    normalized = _normalize_cli_name(antenna_type)
    if normalized in _ANTENNA_ALIASES:
        return _ANTENNA_ALIASES[normalized]
    if antenna_type in _CLASS_TO_CLI:
        return antenna_type
    available = ", ".join(sorted(ANTENNA_REGISTRY.keys()))
    raise typer.BadParameter(f"Unknown antenna type '{antenna_type}'. Available: {available}")


def _parse_param_list(params: Optional[list[str]]) -> dict:
    """Parse ``--param key=value`` pairs, applying JSON decoding for complex values."""
    result: dict = {}
    if not params:
        return result
    for item in params:
        if "=" not in item:
            raise typer.BadParameter(f"Invalid --param format: '{item}'. Expected key=value.")
        key, _, raw = item.partition("=")
        key, raw = key.strip(), raw.strip()
        try:
            value = json.loads(raw)
        except (json.JSONDecodeError, ValueError):
            value = raw
        result[key] = value
    return result


def _load_params_file(file_path: Optional[str]) -> dict:
    """Load parameter values from a YAML or JSON file."""
    if not file_path:
        return {}

    path = Path(file_path).expanduser()
    if not path.is_file():
        raise typer.BadParameter(f"Parameter file '{file_path}' was not found.")

    try:
        content = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise typer.BadParameter(f"Unable to read parameter file '{file_path}': {exc}") from exc

    suffix = path.suffix.lower()
    try:
        if suffix == ".json":
            data = json.loads(content)
        else:
            import yaml

            data = yaml.safe_load(content)
    except ImportError as exc:
        raise typer.BadParameter("YAML parameter files require the 'PyYAML' package.") from exc
    except Exception as exc:
        raise typer.BadParameter(f"Unable to parse parameter file '{file_path}': {exc}") from exc

    if data is None:
        return {}
    if not isinstance(data, dict):
        raise typer.BadParameter(f"Parameter file '{file_path}' must contain a mapping of parameter names to values.")
    return data


def _collect_file_overrides(file_data: dict, is_create: bool) -> tuple[dict, dict, dict]:
    """Split file data into synthesis overrides, create setup options, and extra parameters."""
    synthesis_values: dict = {}
    setup_values: dict = {}
    extra_values: dict = {}

    synthesis_section = file_data.get("synthesis")
    if synthesis_section is not None:
        if not isinstance(synthesis_section, dict):
            raise typer.BadParameter("The 'synthesis' section in a parameter file must be a mapping.")
        synthesis_values.update(synthesis_section)

    setup_section = file_data.get("setup")
    if setup_section is not None:
        if not isinstance(setup_section, dict):
            raise typer.BadParameter("The 'setup' section in a parameter file must be a mapping.")
        setup_values.update(setup_section)

    extra_section = file_data.get("param")
    if extra_section is not None:
        if not isinstance(extra_section, dict):
            raise typer.BadParameter("The 'param' section in a parameter file must be a mapping.")
        extra_values.update(extra_section)

    reserved_keys = {"synthesis", "setup", "param"}
    for key, value in file_data.items():
        if key in reserved_keys:
            continue
        if key in _SYNTH_FIELD_NAMES:
            synthesis_values[key] = value
        elif is_create and key in _SETUP_FIELD_NAMES:
            setup_values[key] = value
        else:
            extra_values[key] = value

    return synthesis_values, setup_values, extra_values


def _merge_cli_inputs(kwargs: dict, *, is_create: bool) -> tuple[dict, dict, dict]:
    """Merge file-based values with explicit CLI options."""
    file_data = _load_params_file(kwargs.get("params_file"))
    file_synth, file_setup, file_extra = _collect_file_overrides(file_data, is_create=is_create)
    cli_synth = _collect_overrides(kwargs)
    cli_extra = _parse_param_list(kwargs.get("param"))

    merged_setup = file_setup if is_create else {}
    if is_create:
        for name in _SETUP_FIELD_NAMES:
            if kwargs.get(name) is not None:
                merged_setup[name] = kwargs[name]

    return {**file_synth, **cli_synth}, merged_setup, {**file_extra, **cli_extra}


def _project_key(project_name: Optional[str]) -> str:
    """Return the short project name used by AEDT design lists."""
    if not project_name:
        return ""
    project_path = Path(project_name)
    return project_path.stem or project_name


def _resolve_project_name(project_name: Optional[str], project_list: list[str]) -> Optional[str]:
    """Resolve a project CLI argument against the AEDT project list."""
    if not project_name:
        return None

    normalized = project_name.lower()
    exact_matches = [
        project
        for project in project_list
        if project.lower() == normalized or _project_key(project).lower() == normalized
    ]
    if len(exact_matches) == 1:
        return exact_matches[0]
    if len(exact_matches) > 1:
        raise RuntimeError(f"Project '{project_name}' is ambiguous. Matches: {exact_matches}")

    partial_matches = [project for project in project_list if normalized in project.lower()]
    if len(partial_matches) == 1:
        return partial_matches[0]
    if len(partial_matches) > 1:
        raise RuntimeError(f"Project '{project_name}' is ambiguous. Matches: {partial_matches}")

    raise RuntimeError(f"Project '{project_name}' not found. Available: {project_list}")


def _designs_for_project(design_list: dict, project_name: Optional[str]) -> list[str]:
    """Return the known designs for the selected project."""
    if not project_name:
        return []

    project_keys = {_project_key(project_name), project_name}
    for key in project_keys:
        if key in design_list:
            return design_list[key]
    return []


def _resolve_target_design(kwargs: dict, class_name: str, properties) -> str:
    """Pick the design to use, creating an antenna-named design when absent."""
    requested_design = kwargs.get("design")
    if requested_design:
        return requested_design

    existing_designs = {
        design.lower(): design for design in _designs_for_project(properties.design_list, properties.active_project)
    }
    for candidate in (
        _CLASS_TO_CLI.get(class_name, _camel_to_kebab(class_name)),
        kwargs["antenna_type"],
        class_name,
    ):
        match = existing_designs.get(candidate.lower())
        if match:
            return match

    return _CLASS_TO_CLI.get(class_name, _camel_to_kebab(class_name))


# ---------------------------------------------------------------------------
# Dynamic command factory — auto-generates Typer params from Synthesis model
# ---------------------------------------------------------------------------

# Collect the names of Synthesis fields that map to scalar CLI options.
_SYNTH_FIELD_NAMES: list[str] = []
for _name, _fi in Synthesis.model_fields.items():
    if _name not in _SKIP_FIELDS and _python_type_for_annotation(_fi.annotation) is not None:
        _SYNTH_FIELD_NAMES.append(_name)

_SETUP_FIELD_NAMES = ("create_setup", "component_3d", "lattice_pair", "sweep", "num_cores")

_P = inspect.Parameter.POSITIONAL_OR_KEYWORD


def _build_signature(is_create: bool) -> inspect.Signature:
    """Build an ``inspect.Signature`` with auto-generated Typer params."""
    params: list[inspect.Parameter] = []

    # -- positional: antenna_type
    params.append(
        inspect.Parameter(
            "antenna_type",
            _P,
            annotation=str,
            default=typer.Argument(..., help="Antenna type (run 'pyaedt antenna list')."),
        )
    )

    # -- create-only: --port
    if is_create:
        params.append(
            inspect.Parameter(
                "port",
                _P,
                annotation=int,
                default=typer.Option(..., "--port", help="gRPC port of the running AEDT instance."),
            )
        )
        params.append(
            inspect.Parameter(
                "project",
                _P,
                annotation=Optional[str],
                default=typer.Option(None, "--project", help="Project name (auto-detected if only one is open)."),
            )
        )
        params.append(
            inspect.Parameter(
                "design",
                _P,
                annotation=Optional[str],
                default=typer.Option(None, "--design", help="Design name (auto-detected if only one exists)."),
            )
        )

    # -- auto-generated from Synthesis fields
    for name in _SYNTH_FIELD_NAMES:
        fi = Synthesis.model_fields[name]
        py_type = _python_type_for_annotation(fi.annotation)
        opt_flag = "--" + name.replace("_", "-")
        params.append(
            inspect.Parameter(
                name,
                _P,
                annotation=Optional[py_type],
                default=typer.Option(None, opt_flag, help=f"Default: {fi.default}"),
            )
        )

    # -- create-only: setup flags
    if is_create:
        params.append(
            inspect.Parameter(
                "create_setup",
                _P,
                annotation=Optional[bool],
                default=typer.Option(
                    None,
                    "--create-setup/--no-create-setup",
                    help="Create an analysis setup and sweep.",
                ),
            )
        )
        params.append(
            inspect.Parameter(
                "component_3d",
                _P,
                annotation=Optional[bool],
                default=typer.Option(
                    None,
                    "--component-3d/--no-component-3d",
                    help="Create a 3-D component.",
                ),
            )
        )
        params.append(
            inspect.Parameter(
                "lattice_pair",
                _P,
                annotation=Optional[bool],
                default=typer.Option(
                    None,
                    "--lattice-pair/--no-lattice-pair",
                    help="Create a lattice pair.",
                ),
            )
        )
        params.append(
            inspect.Parameter(
                "sweep",
                _P,
                annotation=Optional[int],
                default=typer.Option(None, "--sweep", help="Sweep percentage (default: 20)."),
            )
        )
        params.append(
            inspect.Parameter(
                "num_cores",
                _P,
                annotation=Optional[int],
                default=typer.Option(None, "--num-cores", help="Number of cores for analysis (default: 4)."),
            )
        )

    # -- repeatable --param for complex / antenna-specific values
    params.append(
        inspect.Parameter(
            "params_file",
            _P,
            annotation=Optional[str],
            default=typer.Option(None, "--params-file", help="YAML or JSON file with parameter values."),
        )
    )
    params.append(
        inspect.Parameter(
            "param",
            _P,
            annotation=Optional[list[str]],
            default=typer.Option(None, "--param", help="Extra key=value parameter (repeatable)."),
        )
    )

    return inspect.Signature(params)


def _collect_overrides(kwargs: dict) -> dict:
    """Return only Synthesis fields that the user explicitly provided."""
    return {name: kwargs[name] for name in _SYNTH_FIELD_NAMES if kwargs.get(name) is not None}


# ---------------------------------------------------------------------------
# Typer application
# ---------------------------------------------------------------------------

antenna_app = typer.Typer(help="Antenna design and synthesis commands.")


# -- list -----------------------------------------------------------------


@antenna_app.command(name="list")
def list_antennas() -> None:
    """List available antenna types."""
    if common.json_mode:
        common.print_output(data={"antennas": ANTENNA_REGISTRY, "categories": _CATEGORIES})
    else:
        typer.secho("Available antenna types:\n", fg="green")
        for category, names in _CATEGORIES.items():
            typer.secho(f"  {category}", fg="cyan", bold=True)
            for cli_name in names:
                class_name = ANTENNA_REGISTRY[cli_name]
                typer.echo(f"    {cli_name:<28s} ({class_name})")
        typer.echo()


# -- synthesize -----------------------------------------------------------


def _synthesize_impl(**kwargs) -> None:
    try:
        class_name = _resolve_antenna_type(kwargs["antenna_type"])
        overrides, _, extra = _merge_cli_inputs(kwargs, is_create=False)

        from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend
        from ansys.aedt.toolkits.antenna.backend.models import properties

        for key, value in {**overrides, **extra}.items():
            if hasattr(properties.antenna.synthesis, key):
                setattr(properties.antenna.synthesis, key, value)

        toolkit = ToolkitBackend()
        result = toolkit.get_antenna(class_name, synth_only=True)
        if result is False:
            raise RuntimeError(f"Synthesis failed for {class_name}.")

        if common.json_mode:
            common.print_output(data={"antenna": kwargs["antenna_type"], "class": class_name, "parameters": result})
        else:
            typer.secho(f"\nSynthesis results for {kwargs['antenna_type']} ({class_name}):\n", fg="green")
            for k, v in result.items():
                typer.echo(f"  {k:<28s} {v}")
            typer.echo()
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


_synthesize_impl.__name__ = "synthesize"
_synthesize_impl.__doc__ = (
    "Compute antenna dimensions without connecting to AEDT.\n\n"
    "ANTENNA_TYPE is one of the names shown by 'pyaedt antenna list'."
)
_synthesize_impl.__signature__ = _build_signature(is_create=False)
antenna_app.command(name="synthesize")(_synthesize_impl)


# -- create ---------------------------------------------------------------


def _create_impl(**kwargs) -> None:
    try:
        class_name = _resolve_antenna_type(kwargs["antenna_type"])
        port = kwargs["port"]
        overrides, setup_values, extra = _merge_cli_inputs(kwargs, is_create=True)

        from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend
        from ansys.aedt.toolkits.antenna.backend.models import properties

        # Connection
        properties.use_grpc = True
        properties.selected_process = port

        toolkit = ToolkitBackend()

        # Connect to AEDT session and populate project/design lists
        toolkit.launch_aedt()
        toolkit.wait_to_be_idle()

        project_name = _resolve_project_name(kwargs.get("project"), properties.project_list)
        if project_name:
            properties.active_project = project_name

        properties.active_design = _resolve_target_design(kwargs, class_name, properties)
        if not toolkit.connect_design("HFSS"):
            raise RuntimeError("Unable to connect to the selected HFSS design.")

        # Synthesis
        for key, value in {**overrides, **extra}.items():
            if hasattr(properties.antenna.synthesis, key):
                setattr(properties.antenna.synthesis, key, value)

        # Setup
        properties.antenna.setup.create_setup = setup_values.get("create_setup", False)
        properties.antenna.setup.component_3d = setup_values.get("component_3d", False)
        properties.antenna.setup.lattice_pair = setup_values.get("lattice_pair", False)
        if setup_values.get("sweep") is not None:
            properties.antenna.setup.sweep = setup_values["sweep"]
        if setup_values.get("num_cores") is not None:
            properties.antenna.setup.num_cores = setup_values["num_cores"]

        if not common.json_mode:
            typer.echo(f"Creating {kwargs['antenna_type']} ({class_name}) on port {port}...")

        result = toolkit.get_antenna(class_name, synth_only=False)
        if result is False:
            raise RuntimeError("Antenna creation failed. Check AEDT connection and design state.")

        if common.json_mode:
            common.print_output(data={"antenna": kwargs["antenna_type"], "class": class_name, "parameters": result})
        else:
            typer.secho(f"\nAntenna {kwargs['antenna_type']} created successfully!\n", fg="green")
            for k, v in result.items():
                typer.echo(f"  {k:<28s} {v}")
            typer.echo()
    except typer.Exit:
        raise
    except Exception as e:
        if common.json_mode:
            common.print_output(error=str(e))
        else:
            typer.secho(f"Error: {e}", fg="red")
        raise typer.Exit(code=1)


_create_impl.__name__ = "create"
_create_impl.__doc__ = (
    "Create an antenna in a running AEDT/HFSS session.\n\n"
    "ANTENNA_TYPE is one of the names shown by 'pyaedt antenna list'."
)
_create_impl.__signature__ = _build_signature(is_create=True)
antenna_app.command(name="create")(_create_impl)
