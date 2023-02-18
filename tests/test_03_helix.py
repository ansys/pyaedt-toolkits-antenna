from pyaedt.modeler.cad.object3d import Object3d
from pyaedt.modeler.geometry_operators import GeometryOperators

from ansys.aedt.toolkits.antennas.helix import AxialMode
from conftest import BasisTest

test_project_name = "Helix_test"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, test_project_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_conical_horn(self):
        self.aedtapp.design_name = "myname"
        oantenna = self.aedtapp.add_from_toolkit(AxialMode, draw=True, frequency=1.0)
        assert oantenna
        assert oantenna.object_list
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)
        face_center = list(oantenna.object_list.values())[0].faces[0].center
        assert oantenna.origin == [0, 0, 0]
        oantenna.origin = [10, 20, 50]
        assert oantenna.origin == [10, 20, 50]
        face_center_new = list(oantenna.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 50])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-6
        ohorn2 = self.aedtapp.add_from_toolkit(
            AxialMode, draw=True, antenna_name=oantenna.antenna_name
        )
        assert oantenna.antenna_name != ohorn2.antenna_name
