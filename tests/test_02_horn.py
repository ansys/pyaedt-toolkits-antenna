from pyaedt.modeler.cad.object3d import Object3d
from pyaedt.modeler.geometry_operators import GeometryOperators

from ansys.aedt.toolkits.antennas.models.horn import Conical
from ansys.aedt.toolkits.antennas.models.horn import Corrugated
from ansys.aedt.toolkits.antennas.models.horn import EPlane
from ansys.aedt.toolkits.antennas.models.horn import Elliptical
from ansys.aedt.toolkits.antennas.models.horn import HPlane
from ansys.aedt.toolkits.antennas.models.horn import Pyramidal
from ansys.aedt.toolkits.antennas.models.horn import PyramidalRidged
from ansys.aedt.toolkits.antennas.models.horn import QuadRidged
from conftest import BasisTest

test_project_name = "Horn_test"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)
        self.aedtapp = BasisTest.add_app(self, test_project_name)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01a_conical(self):
        self.aedtapp.design_name = "conical_horn"
        ohorn1 = self.aedtapp.add_from_toolkit(Conical, draw=True, frequency=1.0, huygens_box=True)
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
        ohorn2 = self.aedtapp.add_from_toolkit(Conical, draw=True, antenna_name=ohorn1.antenna_name)
        assert ohorn1.antenna_name != ohorn2.antenna_name

    def test_01b_conical_duplicate_along_line(self):
        self.aedtapp.design_name = "conical_horn"
        ohorn = self.aedtapp.add_from_toolkit(
            Conical, draw=True, frequency=1.0, origin=[500, 20, 50]
        )
        new = ohorn.duplicate_along_line([0, 500, 0], 4)
        assert len(new) == 3

    def test_01c_conical_create_3dcomponent(self):
        self.aedtapp.design_name = "conical_horn"
        ohorn = self.aedtapp.add_from_toolkit(
            Conical, draw=True, frequency=1.0, origin=[500, 500, 0]
        )
        component = ohorn.create_3dcomponent(replace=True)
        assert list(self.aedtapp.modeler.user_defined_components.keys())[0] == component.name

    def test_01d_conical_lattice_pair(self):
        self.aedtapp.design_name = "conical_horn"
        ohorn1 = self.aedtapp.add_from_toolkit(
            Conical,
            draw=True,
            frequency=1.0,
            origin=[1500, 500, 0],
            outer_boundary="Radiation",
        )

        ohorn1.create_lattice_pair(lattice_height=None, bottom_extend=False)

        assert len(ohorn1.boundaries) == 2

        ohorn2 = self.aedtapp.add_from_toolkit(
            ConicalHorn,
            draw=True,
            frequency=1.0,
            origin=[1500, 1000, 0],
            outer_boundary="Radiation",
        )

        ohorn2.create_lattice_pair(lattice_height="20mm", bottom_extend=False)

        assert ohorn2.create_3dcomponent(replace=True)

        ohorn3 = self.aedtapp.add_from_toolkit(
            ConicalHorn,
            draw=True,
            frequency=1.0,
            origin=[1500, 1500, 0],
            outer_boundary="Radiation",
        )

        assert ohorn3.create_lattice_pair(lattice_height="20mm", bottom_extend=True)

    def test_02_pyramidal_ridged(self):
        self.aedtapp = self.add_app(design_name="pyramidal_ridged_horn")
        ohorn1 = self.aedtapp.add_from_toolkit(
            PyramidalRidged, draw=True, frequency=10.0, huygens_box=True
        )
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
        ohorn2 = self.aedtapp.add_from_toolkit(
            PyramidalRidged, draw=True, antenna_name=ohorn1.antenna_name
        )
        assert ohorn1.antenna_name != ohorn2.antenna_name

    def test_03_corrugated(self):
        self.aedtapp = self.add_app(design_name="corrugated_horn")
        self.aedtapp.solution_type = "Modal"
        ohorn1 = self.aedtapp.add_from_toolkit(
            Corrugated, draw=True, frequency=10.0, huygens_box=True
        )
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
        ohorn2 = self.aedtapp.add_from_toolkit(
            Corrugated, draw=True, antenna_name=ohorn1.antenna_name
        )
        assert ohorn1.antenna_name != ohorn2.antenna_name

    def test_04_elliptical(self):
        self.aedtapp = self.add_app(design_name="elliptical_horn")
        self.aedtapp.solution_type = "Modal"
        ohorn1 = self.aedtapp.add_from_toolkit(
            Elliptical, draw=True, frequency=10.0, huygens_box=True
        )
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
        ohorn2 = self.aedtapp.add_from_toolkit(
            Elliptical, draw=True, antenna_name=ohorn1.antenna_name
        )
        assert ohorn1.antenna_name != ohorn2.antenna_name

    def test_05_eplane(self):
        self.aedtapp = self.add_app(design_name="eplane_horn")
        self.aedtapp.solution_type = "Modal"
        ohorn1 = self.aedtapp.add_from_toolkit(EPlane, draw=True, frequency=10.0, huygens_box=True)
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
        ohorn2 = self.aedtapp.add_from_toolkit(EPlane, draw=True, antenna_name=ohorn1.antenna_name)
        assert ohorn1.antenna_name != ohorn2.antenna_name

    def test_06_hplane(self):
        self.aedtapp = self.add_app(design_name="hplane_horn")
        self.aedtapp.solution_type = "Modal"
        ohorn1 = self.aedtapp.add_from_toolkit(HPlane, draw=True, frequency=10.0, huygens_box=True)
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
        ohorn2 = self.aedtapp.add_from_toolkit(HPlane, draw=True, antenna_name=ohorn1.antenna_name)
        assert ohorn1.antenna_name != ohorn2.antenna_name

    def test_07_pyramidal(self):
        self.aedtapp = self.add_app(design_name="pyramidal_horn")
        self.aedtapp.solution_type = "Modal"
        ohorn1 = self.aedtapp.add_from_toolkit(
            Pyramidal, draw=True, frequency=10.0, huygens_box=True
        )
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
        ohorn2 = self.aedtapp.add_from_toolkit(
            Pyramidal, draw=True, antenna_name=ohorn1.antenna_name
        )
        assert ohorn1.antenna_name != ohorn2.antenna_name

    def test_08_quadridged(self):
        self.aedtapp = self.add_app(design_name="quadridge_horn")
        self.aedtapp.solution_type = "Modal"
        ohorn1 = self.aedtapp.add_from_toolkit(
            QuadRidged, draw=True, frequency=10.0, huygens_box=True
        )
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
        ohorn2 = self.aedtapp.add_from_toolkit(
            QuadRidged, draw=True, antenna_name=ohorn1.antenna_name
        )
        assert ohorn1.antenna_name != ohorn2.antenna_name
