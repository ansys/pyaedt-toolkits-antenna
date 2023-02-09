from _unittest.conftest import BasisTest
from pyaedt.modeler.cad.object3d import Object3d
from pyaedt.modeler.geometry_operators import GeometryOperators
from ansys.aedt.toolkits.antennas.patch import RectangularPatchProbe

test_project_name = "Patch_test"

class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, test_project_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_rectangular_patch_probe(self):
        self.aedtapp.design_name = "myname"
        opatch1 = self.aedtapp.add_from_toolkit(RectangularPatchProbe, frequency=1.0)
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
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-6
        opatch2 = self.aedtapp.add_from_toolkit(RectangularPatchProbe, antenna_name=opatch1.antenna_name)
        assert opatch1.antenna_name != opatch2.antenna_name
