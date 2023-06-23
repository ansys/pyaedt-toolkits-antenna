from pyaedt.modeler.cad.object3d import Object3d

from ansys.aedt.toolkits.antennas.backend.models.conical_spiral import Archimedean
from conftest import BasisTest

test_project_name = "ConicalSpiral_test"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, test_project_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_archimidean(self):
        self.aedtapp.design_name = "Archimidean"
        oantenna = self.aedtapp.add_from_toolkit(
            Archimedean, draw=True, start_frequency=4.0, stop_frequency=10.0
        )
        assert oantenna
        assert oantenna.object_list
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)
        ohorn2 = self.aedtapp.add_from_toolkit(
            Archimedean, draw=True, antenna_name=oantenna.antenna_name, outer_boundary="Radiation"
        )
        assert oantenna.antenna_name != ohorn2.antenna_name
