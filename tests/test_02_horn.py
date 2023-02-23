from pyaedt.modeler.cad.object3d import Object3d
from pyaedt.modeler.geometry_operators import GeometryOperators

from ansys.aedt.toolkits.antennas.horn import ConicalHorn
from ansys.aedt.toolkits.antennas.horn import PyramidalRidged
from conftest import BasisTest

test_project_name = "Horn_test"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, test_project_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_conical_horn(self):
        self.aedtapp.design_name = "myname"
        ohorn1 = self.aedtapp.add_from_toolkit(ConicalHorn, draw=True, frequency=1.0)
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
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-6
        ohorn2 = self.aedtapp.add_from_toolkit(
            ConicalHorn, draw=True, antenna_name=ohorn1.antenna_name
        )
        assert ohorn1.antenna_name != ohorn2.antenna_name

    def test_02_pyramidal_ridged_horn(self):
        self.aedtapp.design_name = "myname"
        ohorn1 = self.aedtapp.add_from_toolkit(PyramidalRidged, draw=True, frequency=10.0)
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
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-6
        ohorn2 = self.aedtapp.add_from_toolkit(
            PyramidalRidged, draw=True, antenna_name=ohorn1.antenna_name
        )
        assert ohorn1.antenna_name != ohorn2.antenna_name
