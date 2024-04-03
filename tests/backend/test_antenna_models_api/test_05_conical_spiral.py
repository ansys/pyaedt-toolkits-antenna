from conftest import BasisTest
from pyaedt.modeler.cad.object3d import Object3d

from ansys.aedt.toolkits.antenna.backend import antenna_models

test_project_name = "ConicalSpiral_test"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, test_project_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_archimidean(self):
        self.aedtapp.design_name = "Archimidean"

        antenna_module = getattr(antenna_models, "Archimedean")
        oantenna = antenna_module(None, start_frequency=2.0, stop_frequency=10.0, length_unit="mm")
        assert oantenna.synthesis_parameters

        oantenna = antenna_module(
            self.aedtapp, start_frequency=4.0, stop_frequency=10.0, length_unit=self.aedtapp.modeler.model_units
        )
        oantenna.init_model()
        oantenna.model_hfss()
        oantenna.setup_hfss()

        assert oantenna

        assert oantenna.object_list
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)
        oantenna2 = antenna_module(
            self.aedtapp, start_frequency=4.0, stop_frequency=10.0, length_unit=self.aedtapp.modeler.model_units
        )
        assert oantenna.name != oantenna2.name

    def test_02_log(self):
        self.aedtapp = self.add_app(design_name="Log")

        antenna_module = getattr(antenna_models, "Log")
        oantenna = antenna_module(None, start_frequency=2.0, stop_frequency=10.0, length_unit="mm")
        assert oantenna.synthesis_parameters

        oantenna = antenna_module(
            self.aedtapp, start_frequency=4.0, stop_frequency=10.0, length_unit=self.aedtapp.modeler.model_units
        )
        oantenna.init_model()
        oantenna.model_hfss()
        oantenna.setup_hfss()

        assert oantenna

        assert oantenna.object_list
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)
        oantenna2 = antenna_module(
            self.aedtapp, start_frequency=4.0, stop_frequency=10.0, length_unit=self.aedtapp.modeler.model_units
        )
        assert oantenna.name != oantenna2.name

    def test_03_sinuous(self):
        self.aedtapp = self.add_app(design_name="Sinuous")

        antenna_module = getattr(antenna_models, "Sinuous")
        oantenna = antenna_module(None, start_frequency=4.0, stop_frequency=10.0, length_unit="mm")
        assert oantenna.synthesis_parameters

        oantenna = antenna_module(
            self.aedtapp, start_frequency=4.0, stop_frequency=10.0, length_unit=self.aedtapp.modeler.model_units
        )
        oantenna.init_model()
        oantenna.model_hfss()
        oantenna.setup_hfss()

        assert oantenna

        assert oantenna.object_list
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)
        oantenna2 = antenna_module(
            self.aedtapp, start_frequency=4.0, stop_frequency=10.0, length_unit=self.aedtapp.modeler.model_units
        )
        assert oantenna.name != oantenna2.name
