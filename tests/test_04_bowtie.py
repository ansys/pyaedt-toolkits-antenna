from pyaedt.modeler.cad.object3d import Object3d

from ansys.aedt.toolkits.antennas.models.bowtie import BowTie
from ansys.aedt.toolkits.antennas.models.bowtie import BowTieRounded
from ansys.aedt.toolkits.antennas.models.bowtie import BowTieSlot
from conftest import BasisTest

test_project_name = "Bowtie_test"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, test_project_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_bowtie(self):
        self.aedtapp.design_name = "Bowtie"
        oantenna = self.aedtapp.add_from_toolkit(BowTie, draw=True, frequency=1.0, huygens_box=True)
        assert oantenna
        assert oantenna.object_list
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)
        ohorn2 = self.aedtapp.add_from_toolkit(
            BowTie, draw=True, antenna_name=oantenna.antenna_name, outer_boundary="Radiation"
        )
        assert oantenna.antenna_name != ohorn2.antenna_name

    def test_02_bowtie_rounded(self):
        self.aedtapp = self.add_app(design_name="BowTieRounded")
        oantenna = self.aedtapp.add_from_toolkit(
            BowTieRounded, draw=True, frequency=1.0, huygens_box=True
        )
        assert oantenna
        assert oantenna.object_list
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)
        ohorn2 = self.aedtapp.add_from_toolkit(
            BowTieRounded, draw=True, antenna_name=oantenna.antenna_name, outer_boundary="Radiation"
        )
        assert oantenna.antenna_name != ohorn2.antenna_name

    def test_03_bowtie_slot(self):
        self.aedtapp = self.add_app(design_name="BowTieSlot")
        oantenna = self.aedtapp.add_from_toolkit(
            BowTieSlot, draw=True, frequency=1.0, huygens_box=True
        )
        assert oantenna
        assert oantenna.object_list
        for comp in oantenna.object_list.values():
            assert isinstance(comp, Object3d)
        ohorn2 = self.aedtapp.add_from_toolkit(
            BowTieSlot, draw=True, antenna_name=oantenna.antenna_name, outer_boundary="Radiation"
        )
        assert oantenna.antenna_name != ohorn2.antenna_name
