from conftest import BasisTest
from pyaedt.modeler.cad.object3d import Object3d

from ansys.aedt.toolkits.antenna.backend import models

test_project_name = "Helix_test"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, test_project_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_helix_axial(self):
        self.aedtapp.design_name = "myname"
        self.aedtapp.solution_type = "Modal"
        antenna_module = getattr(models, "AxialMode")
        oantenna = antenna_module(None, frequency=1.0, length_unit="mm")
        assert oantenna.synthesis_parameters

        oantenna = antenna_module(self.aedtapp, frequency=1.0, length_unit=self.aedtapp.modeler.model_units)
        oantenna.init_model()
        oantenna.model_hfss()
        oantenna.setup_hfss()

        assert oantenna
        assert oantenna.object_list
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)

        oantenna2 = antenna_module(
            self.aedtapp, frequency=1.0, length_unit=self.aedtapp.modeler.model_units, outer_boundary="Radiation"
        )

        assert oantenna.antenna_name != oantenna2.antenna_name
