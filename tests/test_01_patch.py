from pyaedt.modeler.cad.object3d import Object3d
from pyaedt.modeler.geometry_operators import GeometryOperators

from ansys.aedt.toolkits.antennas.models.patch import RectangularPatchEdge
from ansys.aedt.toolkits.antennas.models.patch import RectangularPatchInset
from ansys.aedt.toolkits.antennas.models.patch import RectangularPatchProbe
from conftest import BasisTest

test_project_name = "Patch_test"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, test_project_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01a_rectangular_patch_probe_model_hfss(self):
        opatch1 = self.aedtapp.add_from_toolkit(RectangularPatchProbe, draw=True, frequency=1.0)
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
        opatch2 = self.aedtapp.add_from_toolkit(
            RectangularPatchProbe, draw=True, antenna_name=opatch1.antenna_name
        )
        assert opatch1.antenna_name != opatch2.antenna_name

    def test_01b_rectangular_patch_probe_duplicate_along_line(self):
        opatch = self.aedtapp.add_from_toolkit(
            RectangularPatchProbe, draw=True, frequency=1.0, origin=[500, 20, 50]
        )
        new = opatch.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3

    def test_01c_rectangular_patch_probe_create_3dcomponent(self):
        opatch = self.aedtapp.add_from_toolkit(
            RectangularPatchProbe, draw=True, frequency=1.0, origin=[500, 500, 0]
        )
        component_name = opatch.create_3dcomponent(replace=True)
        assert list(self.aedtapp.modeler.user_defined_components.keys())[0] == component_name

    def test_02a_rectangular_patch_inset_model_hfss(self):
        opatch1 = self.aedtapp.add_from_toolkit(RectangularPatchInset, draw=True, frequency=1.0)
        assert opatch1
        assert opatch1.object_list
        for comp in opatch1.object_list.values():
            assert isinstance(comp, Object3d)
        face_center = list(opatch1.object_list.values())[0].faces[0].center
        assert opatch1.origin == [0, 0, 0]
        opatch1.origin = [10, 20, 500]
        assert opatch1.origin == [10, 20, 500]
        face_center_new = list(opatch1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3
        opatch2 = self.aedtapp.add_from_toolkit(
            RectangularPatchInset, draw=True, antenna_name=opatch1.antenna_name
        )
        assert opatch1.antenna_name != opatch2.antenna_name

    def test_02b_rectangular_patch_inset_duplicate_along_line(self):
        opatch = self.aedtapp.add_from_toolkit(
            RectangularPatchInset, draw=True, frequency=1.0, origin=[500, 20, 50]
        )
        new = opatch.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3

    def test_02c_rectangular_patch_inset_create_3dcomponent(self):
        opatch = self.aedtapp.add_from_toolkit(
            RectangularPatchInset, draw=True, frequency=1.0, origin=[500, 500, 0]
        )
        component_name = opatch.create_3dcomponent(replace=True)
        assert list(self.aedtapp.modeler.user_defined_components.keys())[0] == component_name

    def test_03a_rectangular_patch_edge_model_hfss(self):
        opatch1 = self.aedtapp.add_from_toolkit(RectangularPatchEdge, draw=True, frequency=1.0)
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
        opatch2 = self.aedtapp.add_from_toolkit(
            RectangularPatchEdge, draw=True, antenna_name=opatch1.antenna_name
        )
        assert opatch1.antenna_name != opatch2.antenna_name

    def test_02b_rectangular_patch_edge_duplicate_along_line(self):
        opatch = self.aedtapp.add_from_toolkit(RectangularPatchEdge, draw=True, frequency=1.0)
        new = opatch.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3

    def test_02c_rectangular_patch_edge_create_3dcomponent(self):
        opatch = self.aedtapp.add_from_toolkit(
            RectangularPatchEdge, draw=True, frequency=1.0, origin=[500, 500, 0]
        )
        component_name = opatch.create_3dcomponent(replace=True)
        assert list(self.aedtapp.modeler.user_defined_components.keys())[0] == component_name
