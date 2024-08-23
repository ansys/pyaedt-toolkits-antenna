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

import pytest

pytestmark = [pytest.mark.antenna_models_api]

from ansys.aedt.core.modeler.cad.object_3d import Object3d
from ansys.aedt.core.modeler.geometry_operators import GeometryOperators

from ansys.aedt.toolkits.antenna.backend import antenna_models


class TestClass:
    """Class defining a workflow to test antenna models horn."""

    def test_01a_conical(self, aedt_common):
        antenna_module = getattr(antenna_models, "Conical")
        ohorn0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert ohorn0.synthesis_parameters

        aedt_common.connect_design()
        aedt_common.aedtapp.design_name = "conical_horn"
        aedt_common.aedtapp.solution_type = "Modal"
        aedt_common.save_project(release_aedt=False)

        antenna_module = getattr(antenna_models, "Conical")
        ohorn1 = antenna_module(aedt_common.aedtapp,
                                frequency=1.0,
                                length_unit=aedt_common.aedtapp.modeler.model_units)
        ohorn1.init_model()
        ohorn1.model_hfss()
        ohorn1.setup_hfss()

        assert ohorn1
        assert ohorn1.object_list
        for comp in ohorn1.object_list.values():
            assert isinstance(comp, Object3d)
        face_center = list(ohorn1.object_list.values())[0].faces[0].center
        assert ohorn1.origin == [0, 0, 0]
        ohorn1.origin = [10, 20, 50]
        assert ohorn1.origin == [10, 20, 50]
        face_center_new = list(ohorn1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3
        antenna_module = getattr(antenna_models, "Conical")
        ohorn2 = antenna_module(aedt_common.aedtapp, name=ohorn1.name)

        assert ohorn1.name != ohorn2.name
        aedt_common.release_aedt(False, False)

    def test_01b_conical_duplicate_along_line(self, aedt_common):
        aedt_common.connect_design()
        antenna_module = getattr(antenna_models, "Conical")
        ohorn = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            length_unit=aedt_common.aedtapp.modeler.model_units,
            origin=[500, 20, 50]
        )
        ohorn.init_model()
        ohorn.model_hfss()
        ohorn.setup_hfss()

        new = ohorn.duplicate_along_line([0, 500, 0], 4)
        assert len(new) == 3
        aedt_common.release_aedt(False, False)

    def test_01c_conical_create_3dcomponent(self, aedt_common):
        aedt_common.connect_design()
        antenna_module = getattr(antenna_models, "Conical")
        ohorn = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            length_unit=aedt_common.aedtapp.modeler.model_units,
            origin=[500, 500, 0]
        )
        ohorn.init_model()
        ohorn.model_hfss()
        ohorn.setup_hfss()

        component = ohorn.create_3dcomponent(replace=True)
        assert list(aedt_common.aedtapp.modeler.user_defined_components.keys())[0] == component.name
        aedt_common.release_aedt(False, False)

    def test_01d_conical_lattice_pair(self, aedt_common):
        aedt_common.connect_design()
        antenna_module = getattr(antenna_models, "Conical")
        ohorn1 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            length_unit=aedt_common.aedtapp.modeler.model_units,
            origin=[500, 500, 0]
        )
        ohorn1.init_model()
        ohorn1.model_hfss()
        ohorn1.setup_hfss()

        ohorn1.create_lattice_pair(lattice_height=None, bottom_extend=False)

        assert len(ohorn1.boundaries) == 2

        antenna_module = getattr(antenna_models, "Conical")
        ohorn2 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            length_unit=aedt_common.aedtapp.modeler.model_units,
            origin=[1500, 500, 0]
        )
        ohorn2.init_model()
        ohorn2.model_hfss()
        ohorn2.setup_hfss()

        ohorn2.create_lattice_pair(lattice_height="20mm", bottom_extend=False)

        assert ohorn2.create_3dcomponent(replace=True)

        ohorn3 = antenna_module(
            aedt_common.aedtapp,
            frequency=1.0,
            length_unit=aedt_common.aedtapp.modeler.model_units,
            origin=[1500, 1500, 0]
        )
        ohorn3.init_model()
        ohorn3.model_hfss()
        ohorn3.setup_hfss()

        assert ohorn3.create_lattice_pair(lattice_height="20mm", bottom_extend=True)

        aedt_common.release_aedt(False, False)

    def test_02_pyramidal_ridged(self, aedt_common):
        antenna_module = getattr(antenna_models, "PyramidalRidged")
        ohorn0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert ohorn0.synthesis_parameters

        aedt_common.properties.active_design = "pyramidal_ridged_horn"
        aedt_common.connect_design()
        aedt_common.aedtapp.solution_type = "Modal"

        ohorn1 = antenna_module(aedt_common.aedtapp, frequency=1.0, length_unit=aedt_common.aedtapp.modeler.model_units)
        ohorn1.init_model()
        ohorn1.model_hfss()
        ohorn1.setup_hfss()
        assert ohorn1
        assert ohorn1.object_list
        for comp in ohorn1.object_list.values():
            assert isinstance(comp, Object3d)
        face_center = list(ohorn1.object_list.values())[0].faces[0].center
        assert ohorn1.origin == [0, 0, 0]
        ohorn1.origin = [10, 20, 50]
        assert ohorn1.origin == [10, 20, 50]
        face_center_new = list(ohorn1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3
        ohorn2 = antenna_module(
            aedt_common.aedtapp,
            frequency=10.0,
            length_unit=aedt_common.aedtapp.modeler.model_units, 
            name=ohorn1.name
        )
        assert ohorn1.name != ohorn2.name
        aedt_common.release_aedt(False, False)

    def test_03_corrugated(self, aedt_common):
        antenna_module = getattr(antenna_models, "Corrugated")
        ohorn0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert ohorn0.synthesis_parameters

        aedt_common.properties.active_design = "corrugated_horn"
        aedt_common.connect_design()
        aedt_common.aedtapp.solution_type = "Modal"

        ohorn1 = antenna_module(aedt_common.aedtapp, frequency=10.0, length_unit=aedt_common.aedtapp.modeler.model_units)
        ohorn1.init_model()
        ohorn1.model_hfss()
        ohorn1.setup_hfss()
        assert ohorn1
        assert ohorn1.object_list
        for comp in ohorn1.object_list.values():
            assert isinstance(comp, Object3d)
        face_center = list(ohorn1.object_list.values())[0].faces[0].center
        assert ohorn1.origin == [0, 0, 0]
        ohorn1.origin = [10, 20, 50]
        assert ohorn1.origin == [10, 20, 50]
        face_center_new = list(ohorn1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3
        ohorn2 = antenna_module(
            aedt_common.aedtapp,
            frequency=10.0,
            length_unit=aedt_common.aedtapp.modeler.model_units,
            name=ohorn1.name
        )

        assert ohorn1.name != ohorn2.name
        aedt_common.release_aedt(False, False)

    def test_04_elliptical(self, aedt_common):
        antenna_module = getattr(antenna_models, "Elliptical")
        ohorn0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert ohorn0.synthesis_parameters

        aedt_common.properties.active_design = "elliptical_horn"
        aedt_common.connect_design()
        aedt_common.aedtapp.solution_type = "Modal"

        ohorn1 = antenna_module(aedt_common.aedtapp,
                                frequency=10.0,
                                length_unit=aedt_common.aedtapp.modeler.model_units)
        ohorn1.init_model()
        ohorn1.model_hfss()
        ohorn1.setup_hfss()
        assert ohorn1
        assert ohorn1.object_list
        for comp in ohorn1.object_list.values():
            assert isinstance(comp, Object3d)
        face_center = list(ohorn1.object_list.values())[0].faces[0].center
        assert ohorn1.origin == [0, 0, 0]
        ohorn1.origin = [10, 20, 50]
        assert ohorn1.origin == [10, 20, 50]
        face_center_new = list(ohorn1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3
        ohorn2 = antenna_module(
            aedt_common.aedtapp,
            frequency=10.0,
            name=ohorn1.name,
            length_unit=aedt_common.aedtapp.modeler.model_units
        )

        assert ohorn1.name != ohorn2.name
        aedt_common.release_aedt(False, False)

    def test_05_eplane(self, aedt_common):
        antenna_module = getattr(antenna_models, "EPlane")
        ohorn0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert ohorn0.synthesis_parameters

        aedt_common.properties.active_design = "eplane_horn"
        aedt_common.connect_design()
        aedt_common.aedtapp.solution_type = "Modal"

        ohorn1 = antenna_module(aedt_common.aedtapp,
                                frequency=10.0,
                                length_unit=aedt_common.aedtapp.modeler.model_units)
        ohorn1.init_model()
        ohorn1.model_hfss()
        ohorn1.setup_hfss()
        assert ohorn1
        assert ohorn1.object_list
        for comp in ohorn1.object_list.values():
            assert isinstance(comp, Object3d)
        face_center = list(ohorn1.object_list.values())[0].faces[0].center
        assert ohorn1.origin == [0, 0, 0]
        ohorn1.origin = [10, 20, 50]
        assert ohorn1.origin == [10, 20, 50]
        face_center_new = list(ohorn1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3

        ohorn2 = antenna_module(
            aedt_common.aedtapp,
            frequency=10.0,
            length_unit=aedt_common.aedtapp.modeler.model_units,
            name=ohorn1.name
        )
        assert ohorn1.name != ohorn2.name
        aedt_common.release_aedt(False, False)

    def test_06_hplane(self, aedt_common):
        antenna_module = getattr(antenna_models, "HPlane")
        ohorn0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert ohorn0.synthesis_parameters

        aedt_common.properties.active_design = "hplane_horn"
        aedt_common.connect_design()
        aedt_common.aedtapp.solution_type = "Modal"

        ohorn1 = antenna_module(aedt_common.aedtapp,
                                frequency=10.0,
                                length_unit=aedt_common.aedtapp.modeler.model_units)
        ohorn1.init_model()
        ohorn1.model_hfss()
        ohorn1.setup_hfss()
        assert ohorn1
        assert ohorn1.object_list
        for comp in ohorn1.object_list.values():
            assert isinstance(comp, Object3d)
        face_center = list(ohorn1.object_list.values())[0].faces[0].center
        assert ohorn1.origin == [0, 0, 0]
        ohorn1.origin = [10, 20, 50]
        assert ohorn1.origin == [10, 20, 50]
        face_center_new = list(ohorn1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3
        ohorn2 = antenna_module(
            aedt_common.aedtapp,
            frequency=10.0,
            length_unit=aedt_common.aedtapp.modeler.model_units,
            name=ohorn1.name
        )

        assert ohorn1.name != ohorn2.name
        aedt_common.release_aedt(False, False)

    def test_07_pyramidal(self, aedt_common):
        antenna_module = getattr(antenna_models, "Pyramidal")
        ohorn0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert ohorn0.synthesis_parameters

        aedt_common.properties.active_design = "pyramidal_horn"
        aedt_common.connect_design()
        aedt_common.aedtapp.solution_type = "Modal"

        ohorn1 = antenna_module(aedt_common.aedtapp,
                                frequency=10.0,
                                length_unit=aedt_common.aedtapp.modeler.model_units)
        ohorn1.init_model()
        ohorn1.model_hfss()
        ohorn1.setup_hfss()
        assert ohorn1
        assert ohorn1.object_list
        for comp in ohorn1.object_list.values():
            assert isinstance(comp, Object3d)
        face_center = list(ohorn1.object_list.values())[0].faces[0].center
        assert ohorn1.origin == [0, 0, 0]
        ohorn1.origin = [10, 20, 50]
        assert ohorn1.origin == [10, 20, 50]
        face_center_new = list(ohorn1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3
        ohorn2 = antenna_module(
            aedt_common.aedtapp,
            frequency=10.0,
            length_unit=aedt_common.aedtapp.modeler.model_units, name=ohorn1.name
        )

        assert ohorn1.name != ohorn2.name
        aedt_common.release_aedt(False, False)

    def test_08_quadridged(self, aedt_common):
        antenna_module = getattr(antenna_models, "QuadRidged")
        ohorn0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert ohorn0.synthesis_parameters

        aedt_common.properties.active_design = "quadridge_horn"
        aedt_common.connect_design()
        aedt_common.aedtapp.solution_type = "Modal"

        ohorn1 = antenna_module(aedt_common.aedtapp,
                                frequency=10.0,
                                length_unit=aedt_common.aedtapp.modeler.model_units)
        ohorn1.init_model()
        ohorn1.model_hfss()
        ohorn1.setup_hfss()
        assert ohorn1
        assert ohorn1.object_list
        for comp in ohorn1.object_list.values():
            assert isinstance(comp, Object3d)
        face_center = list(ohorn1.object_list.values())[0].faces[0].center
        assert ohorn1.origin == [0, 0, 0]
        ohorn1.origin = [10, 20, 50]
        assert ohorn1.origin == [10, 20, 50]
        face_center_new = list(ohorn1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3
        ohorn2 = antenna_module(aedt_common.aedtapp,
                                frequency=10.0,
                                name=ohorn1.name)

        assert ohorn1.name != ohorn2.name
        aedt_common.release_aedt(False, False)
