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

from pathlib import Path

from ansys.aedt.toolkits.antenna.backend.antenna_models.yagiuda import QuasiYagi
from ansys.aedt.toolkits.antenna.backend.antenna_models.yagiuda import WireYagiUda

REPO = Path(r"D:\AnsysDev\Repos\wt-antenna-yagiuda")
CATALOG_DIR = REPO / "src" / "ansys" / "aedt" / "toolkits" / "antenna" / "ui" / "windows" / "antenna_catalog"


def _export(toolkit, cls, name, kwargs, output_dir, object_names):
    output_dir.mkdir(parents=True, exist_ok=True)
    for obj_path in output_dir.glob("*.obj"):
        obj_path.unlink()
    toolkit.connect_design("HFSS")
    toolkit.aedtapp.solution_type = "Terminal"
    antenna = cls(toolkit.aedtapp, name=name, **kwargs)
    antenna.init_model()
    assert antenna.model_hfss()
    assert antenna.setup_hfss()
    exported = toolkit.aedtapp.post.export_model_obj(
        assignment=object_names,
        export_path=output_dir,
        export_as_multiple_objects=True,
        air_objects=True,
    )
    assert exported
    for object_name in object_names:
        assert (output_dir / f"{object_name}.obj").is_file()
    toolkit.release_aedt(False, False)


def test_yagiuda_catalog_assets_exist():
    quasi_dir = CATALOG_DIR / "yagiuda" / "quasiyagi"
    wire_dir = CATALOG_DIR / "yagiuda" / "wireyagiuda"
    expected_files = [
        quasi_dir / "QuasiYagi.jpg",
        quasi_dir / "parameters.toml",
        quasi_dir / "model" / "properties.toml",
        quasi_dir / "model" / "sub_QuasiYagi.obj",
        quasi_dir / "model" / "gnd_QuasiYagi.obj",
        quasi_dir / "model" / "ant_director_QuasiYagi.obj",
        quasi_dir / "model" / "ant_driver_QuasiYagi.obj",
        quasi_dir / "model" / "ant_launcher_QuasiYagi.obj",
        quasi_dir / "model" / "port_lump_QuasiYagi.obj",
        wire_dir / "WireYagiUda.png",
        wire_dir / "parameters.toml",
        wire_dir / "model" / "properties.toml",
        wire_dir / "model" / "ant_reflector_WireYagiUda.obj",
        wire_dir / "model" / "ant_driven_top_WireYagiUda.obj",
        wire_dir / "model" / "ant_driven_bottom_WireYagiUda.obj",
        wire_dir / "model" / "ant_director_01_WireYagiUda.obj",
        wire_dir / "model" / "port_lump_WireYagiUda.obj",
    ]

    for file_path in expected_files:
        assert file_path.is_file()


def test_export_quasi_yagi_assets(toolkit):
    output_dir = CATALOG_DIR / "yagiuda" / "quasiyagi" / "model"
    _export(
        toolkit,
        QuasiYagi,
        "QuasiYagi",
        {"frequency": 2.0, "frequency_unit": "GHz", "length_unit": "mm"},
        output_dir,
        [
            "sub_QuasiYagi",
            "gnd_QuasiYagi",
            "ant_director_QuasiYagi",
            "ant_driver_QuasiYagi",
            "ant_launcher_QuasiYagi",
            "port_lump_QuasiYagi",
        ],
    )


def test_export_wire_yagi_assets(toolkit):
    output_dir = CATALOG_DIR / "yagiuda" / "wireyagiuda" / "model"
    _export(
        toolkit,
        WireYagiUda,
        "WireYagiUda",
        {"frequency": 1.0, "frequency_unit": "GHz", "length_unit": "cm", "gain": 9.26},
        output_dir,
        [
            "ant_reflector_WireYagiUda",
            "ant_driven_top_WireYagiUda",
            "ant_driven_bottom_WireYagiUda",
            "ant_director_01_WireYagiUda",
            "port_lump_WireYagiUda",
        ],
    )
