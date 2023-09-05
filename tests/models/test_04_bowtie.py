from conftest import BasisTest
from pyaedt.modeler.cad.object3d import Object3d

from ansys.aedt.toolkits.antenna.backend import models

test_project_name = "Bowtie_test"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, test_project_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_bowtie(self):
        self.aedtapp.design_name = "Bowtie"

        antenna_module = getattr(models, "BowTie")
        oantenna0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert oantenna0.synthesis_parameters

        oantenna1 = antenna_module(self.aedtapp, frequency=1.0, length_unit="mm")
        oantenna1.init_model()
        oantenna1.model_hfss()
        oantenna1.setup_hfss()

        assert oantenna1
        assert oantenna1.object_list
        for comp in oantenna1.object_list.values():
            assert isinstance(comp, Object3d)

        oantenna2 = antenna_module(self.aedtapp, frequency=1.0, outer_boundary="Radiation", length_unit="mm")

        assert oantenna1.antenna_name != oantenna2.antenna_name

    def test_02_bowtie_rounded(self):
        self.aedtapp = self.add_app(design_name="BowTieRounded")

        antenna_module = getattr(models, "BowTieRounded")
        oantenna0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert oantenna0.synthesis_parameters

        oantenna1 = antenna_module(self.aedtapp, frequency=1.0, length_unit="mm")
        oantenna1.init_model()
        oantenna1.model_hfss()
        oantenna1.setup_hfss()

        assert oantenna1
        assert oantenna1.object_list
        for comp in oantenna1.object_list.values():
            assert isinstance(comp, Object3d)

        oantenna2 = antenna_module(self.aedtapp, frequency=1.0, length_unit="mm", outer_boundary="Radiation")

        assert oantenna1.antenna_name != oantenna2.antenna_name

    def test_03_bowtie_slot(self):
        self.aedtapp = self.add_app(design_name="BowTieSlot")
        antenna_module = getattr(models, "BowTieSlot")
        oantenna0 = antenna_module(None, frequency=1.0, length_unit="mm")
        assert oantenna0.synthesis_parameters

        oantenna1 = antenna_module(self.aedtapp, frequency=1.0, length_unit="mm")
        oantenna1.init_model()
        oantenna1.model_hfss()
        oantenna1.setup_hfss()

        assert oantenna1
        assert oantenna1.object_list
        for comp in oantenna1.object_list.values():
            assert isinstance(comp, Object3d)
        oantenna2 = antenna_module(self.aedtapp, frequency=1.0, length_unit="mm", outer_boundary="Radiation")

        assert oantenna1.antenna_name != oantenna2.antenna_name
