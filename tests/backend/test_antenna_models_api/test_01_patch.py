# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
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

import os
import pytest

from tests.backend.conftest import PROJECT_NAME

pytestmark = [pytest.mark.antenna_models_api]

from pyaedt.modeler.cad.object3d import Object3d
from pyaedt.modeler.geometry_operators import GeometryOperators

from ansys.aedt.toolkits.antenna.backend import antenna_models


class TestClass:
    """Class defining a workflow to test antenna models patch."""
    def test_01a_rectangular_patch_probe_model_hfss(self, aedt_common):
        antenna_module = getattr(antenna_models, "RectangularPatchProbe")
        opatch0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert opatch0.synthesis_parameters.coax_inner_rad.value

        aedt_common.connect_design()
        aedt_common.aedtapp.design_name = "rectangular_patch_probe"
        aedt_common.save_project(release_aedt=False)

        opatch1 = antenna_module(aedt_common.aedtapp,
                                 frequency=1.0,
                                 length_unit=aedt_common.aedtapp.modeler.model_units
                                 )
        opatch1.init_model()
        opatch1.model_hfss()
        opatch1.setup_hfss()

        assert opatch1
        assert opatch1.object_list
        for comp in opatch1.object_list.values():
            assert isinstance(comp, Object3d)
        face_center = list(opatch1.object_list.values())[0].faces[0].center
        assert opatch1.origin == [0, 0, 0]
        opatch1.origin = [10, 20, 50]
        assert opatch1.origin == [10, 20, 50]

        face_center_new = list(opatch1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3
        antenna_module = getattr(antenna_models, "RectangularPatchProbe")
        opatch2 = antenna_module(aedt_common.aedtapp, name=opatch1.name)

        assert opatch1.name != opatch2.name

        aedt_common.release_aedt(False, False)

    def test_01b_rectangular_patch_probe_duplicate_along_line(self, aedt_common):
        aedt_common.connect_design()
        antenna_module = getattr(antenna_models, "RectangularPatchProbe")
        opatch = antenna_module(aedt_common.aedtapp, frequency=1.0, origin=[500, 20, 50])
        opatch.init_model()
        opatch.model_hfss()
        opatch.setup_hfss()

        new = opatch.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3
        aedt_common.release_aedt(False, False)

    def test_01c_rectangular_patch_probe_create_3dcomponent(self, aedt_common):
        aedt_common.connect_design()
        antenna_module = getattr(antenna_models, "RectangularPatchProbe")
        opatch = antenna_module(aedt_common.aedtapp, frequency=1.0, origin=[500, 500, 0])
        opatch.init_model()
        opatch.model_hfss()
        opatch.setup_hfss()

        component = opatch.create_3dcomponent(replace=True)
        assert list(aedt_common.aedtapp.modeler.user_defined_components.keys())[0] == component.name
        aedt_common.release_aedt(False, False)

    def test_01d_rectangular_patch_probe_lattice_pair(self, aedt_common):
        aedt_common.connect_design()
        antenna_module = getattr(antenna_models, "RectangularPatchProbe")
        opatch1 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            origin=[500, 500, 0],
            outer_boundary="Radiation",
        )
        opatch1.init_model()
        opatch1.model_hfss()
        opatch1.setup_hfss()

        opatch1.create_lattice_pair(lattice_height=None, bottom_extend=False)

        assert len(opatch1.boundaries) == 5

        opatch2 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            origin=[1500, 1000, 0],
            outer_boundary="Radiation",
        )
        opatch2.init_model()
        opatch2.model_hfss()
        opatch2.setup_hfss()

        opatch2.create_lattice_pair(lattice_height="20mm", bottom_extend=False)

        opatch2.create_3dcomponent(replace=True)
        assert len(aedt_common.aedtapp.modeler.user_defined_components) == 2

        opatch3 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            origin=[1500, 1500, 0],
            outer_boundary="Radiation",
        )
        opatch3.init_model()
        opatch3.model_hfss()
        opatch3.setup_hfss()

        opatch3.create_lattice_pair(lattice_height="20mm", bottom_extend=True)

        assert len(opatch3.boundaries) == 5
        aedt_common.release_aedt(False, False)

    def test_02a_rectangular_patch_inset_model_hfss(self, aedt_common):

        antenna_module = getattr(antenna_models, "RectangularPatchInset")
        opatch0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert opatch0.synthesis_parameters.feed_width.value

        aedt_common.properties.active_design = "rectangular_patch_inset"
        aedt_common.connect_design()

        antenna_module = getattr(antenna_models, "RectangularPatchInset")
        opatch1 = antenna_module(aedt_common.aedtapp,
                                 frequency=1.0,
                                 length_unit=aedt_common.aedtapp.modeler.model_units)
        opatch1.init_model()
        opatch1.model_hfss()
        opatch1.setup_hfss()

        assert opatch1
        assert opatch1.object_list
        for comp in opatch1.object_list.values():
            assert isinstance(comp, Object3d)
        opatch1.substrate_height = 1.575
        face_center = list(opatch1.object_list.values())[0].faces[0].center
        assert opatch1.origin == [0, 0, 0]
        opatch1.origin = [10, 20, 500]
        assert opatch1.origin == [10, 20, 500]
        face_center_new = list(opatch1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 500])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3
        opatch2 = antenna_module(aedt_common.aedtapp, name=opatch1.name)
        opatch2.init_model()
        opatch2.model_hfss()
        opatch2.setup_hfss()
        assert opatch1.name != opatch2.name
        aedt_common.release_aedt(False, False)

    def test_02b_rectangular_patch_inset_duplicate_along_line(self, aedt_common):
        aedt_common.connect_design()
        antenna_module = getattr(antenna_models, "RectangularPatchInset")
        opatch = antenna_module(aedt_common.aedtapp, frequency=1.0, origin=[500, 20, 50])
        opatch.init_model()
        opatch.model_hfss()
        opatch.setup_hfss()
        new = opatch.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3
        aedt_common.release_aedt(False, False)

    def test_02c_rectangular_patch_inset_create_3dcomponent(self, aedt_common):
        aedt_common.connect_design()
        antenna_module = getattr(antenna_models, "RectangularPatchInset")
        opatch = antenna_module(aedt_common.aedtapp, frequency=1.0, origin=[500, 500, 0])
        opatch.init_model()
        opatch.model_hfss()
        opatch.setup_hfss()
        component = opatch.create_3dcomponent(replace=True)
        assert list(aedt_common.aedtapp.modeler.user_defined_components.keys())[0] == component.name
        aedt_common.release_aedt(False, False)

    def test_02d_rectangular_patch_inset_lattice_pair(self, aedt_common):
        aedt_common.connect_design()
        antenna_module = getattr(antenna_models, "RectangularPatchInset")
        opatch1 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            origin=[1500, 500, 0],
            outer_boundary="Radiation",
        )
        opatch1.init_model()
        opatch1.model_hfss()
        opatch1.setup_hfss()

        opatch1.create_lattice_pair(lattice_height=None, bottom_extend=False)

        assert len(opatch1.boundaries) == 4
        opatch2 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            origin=[1500, 1000, 0],
            outer_boundary="Radiation",
        )
        opatch2.init_model()
        opatch2.model_hfss()
        opatch2.setup_hfss()

        opatch2.create_lattice_pair(lattice_height="20mm", bottom_extend=False)

        opatch2.create_3dcomponent(replace=True)
        assert len(aedt_common.aedtapp.modeler.user_defined_components) == 2

        opatch3 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            origin=[1500, 1500, 0],
            outer_boundary="Radiation",
        )
        opatch3.init_model()
        opatch3.model_hfss()
        opatch3.setup_hfss()

        opatch3.create_lattice_pair(lattice_height="20mm", bottom_extend=True)

        assert len(opatch3.boundaries) == 4
        aedt_common.release_aedt(False, False)

    def test_03a_rectangular_patch_edge_model_hfss(self, aedt_common):
        antenna_module = getattr(antenna_models, "RectangularPatchEdge")
        opatch0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert opatch0.synthesis_parameters.patch_x.value

        aedt_common.properties.active_design = "rectangular_patch_edge"
        aedt_common.connect_design()

        antenna_module = getattr(antenna_models, "RectangularPatchEdge")
        opatch1 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            length_unit=aedt_common.aedtapp.modeler.model_units,
        )
        opatch1.init_model()
        opatch1.model_hfss()
        opatch1.setup_hfss()

        assert opatch1
        assert opatch1.object_list
        for comp in opatch1.object_list.values():
            assert isinstance(comp, Object3d)
        opatch1.substrate_height = 1.575
        face_center = list(opatch1.object_list.values())[0].faces[0].center
        assert opatch1.origin == [0, 0, 0]
        opatch1.origin = [-100, 20, -500]
        assert opatch1.origin == [-100, 20, -500]
        face_center_new = list(opatch1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [-100, 20, -500])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3

        opatch2 = antenna_module(aedt_common.aedtapp, frequency=1.0, name=opatch1.name)
        assert opatch1.name != opatch2.name
        aedt_common.release_aedt(False, False)

    def test_03b_rectangular_patch_edge_duplicate_along_line(self, aedt_common):
        aedt_common.connect_design()
        antenna_module = getattr(antenna_models, "RectangularPatchEdge")
        opatch = antenna_module(aedt_common.aedtapp, frequency=1.0)
        opatch.init_model()
        opatch.model_hfss()
        opatch.setup_hfss()
        new = opatch.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3
        aedt_common.release_aedt(False, False)

    def test_03c_rectangular_patch_edge_create_3dcomponent(self, aedt_common):
        aedt_common.connect_design()
        antenna_module = getattr(antenna_models, "RectangularPatchInset")
        opatch = antenna_module(aedt_common.aedtapp, frequency=1.0, origin=[500, 500, 0])
        opatch.init_model()
        opatch.model_hfss()
        opatch.setup_hfss()
        component = opatch.create_3dcomponent(replace=True)
        assert list(aedt_common.aedtapp.modeler.user_defined_components.keys())[0] == component.name
        aedt_common.release_aedt(False, False)

    def test_03d_rectangular_patch_inset_lattice_pair(self, aedt_common):
        aedt_common.connect_design()
        antenna_module = getattr(antenna_models, "RectangularPatchEdge")
        opatch1 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            origin=[1500, 500, 0],
            outer_boundary="Radiation",
        )
        opatch1.init_model()
        opatch1.model_hfss()
        opatch1.setup_hfss()

        opatch1.create_lattice_pair(lattice_height=None, bottom_extend=False)

        assert len(opatch1.boundaries) == 4
        opatch2 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            origin=[1500, 1000, 0],
            outer_boundary="Radiation",
        )
        opatch2.init_model()
        opatch2.model_hfss()
        opatch2.setup_hfss()

        opatch2.create_lattice_pair(lattice_height="20mm", bottom_extend=False)

        opatch2.create_3dcomponent(replace=True)
        assert len(aedt_common.aedtapp.modeler.user_defined_components) == 2

        opatch3 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            origin=[1500, 1500, 0],
            outer_boundary="Radiation",
        )
        opatch3.init_model()
        opatch3.model_hfss()
        opatch3.setup_hfss()

        opatch3.create_lattice_pair(lattice_height="20mm", bottom_extend=True)

        assert len(opatch3.boundaries) == 4
        aedt_common.release_aedt(False, False)
