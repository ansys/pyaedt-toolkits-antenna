# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#

from pathlib import Path
import sys

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


CATALOG_DIR = (
    Path(__file__).resolve().parents[1]
    / "src"
    / "ansys"
    / "aedt"
    / "toolkits"
    / "antenna"
    / "ui"
    / "windows"
    / "antenna_catalog"
)


def test_slot_catalog_assets():
    slot_models = ["SlotCavityBackedArray", "SlotGap", "SlotMicrostrip", "SlotTBar"]

    with (CATALOG_DIR / "antenna_catalog.toml").open("rb") as file_handler:
        catalog = tomllib.load(file_handler)

    assert catalog["Slot"]["models"] == slot_models

    for model in slot_models:
        antenna_path = CATALOG_DIR / "slot" / model.lower()
        assert (antenna_path / "parameters.toml").is_file()
        properties_path = antenna_path / "model" / "properties.toml"
        assert properties_path.is_file()
        assert any(path.suffix.lower() in {".jpg", ".jpeg", ".png"} for path in antenna_path.iterdir())

        with properties_path.open("rb") as file_handler:
            model_properties = tomllib.load(file_handler)

        object_entries = {key: value for key, value in model_properties.items() if key.startswith("object_")}
        assert object_entries

        obj_files = {path.stem for path in (antenna_path / "model").glob("*.obj")}
        assert obj_files == {entry["name"] for entry in object_entries.values()}
