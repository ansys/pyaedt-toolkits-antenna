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
        self.aedtapp.design_name = "rectangular_patch_probe"
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
        self.aedtapp.design_name = "rectangular_patch_probe"
        opatch = self.aedtapp.add_from_toolkit(
            RectangularPatchProbe, draw=True, frequency=1.0, origin=[500, 20, 50]
        )
        new = opatch.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3

    def test_01c_rectangular_patch_probe_create_3dcomponent(self):
        self.aedtapp.design_name = "rectangular_patch_probe"
        opatch = self.aedtapp.add_from_toolkit(
            RectangularPatchProbe, draw=True, frequency=1.0, origin=[500, 500, 0]
        )
        component_name = opatch.create_3dcomponent(replace=True)
        assert list(self.aedtapp.modeler.user_defined_components.keys())[0] == component_name

    def test_01d_rectangular_patch_probe_lattice_pair(self):
        self.aedtapp.design_name = "rectangular_patch_probe"
        opatch1 = self.aedtapp.add_from_toolkit(
            RectangularPatchProbe,
            draw=True,
            frequency=1.0,
            origin=[1500, 500, 0],
            outer_boundary="Radiation",
        )

        opatch1.create_lattice_pair(lattice_height=None, bottom_extend=False)

        assert len(opatch1.boundaries) == 3

        opatch2 = self.aedtapp.add_from_toolkit(
            RectangularPatchProbe,
            draw=True,
            frequency=1.0,
            origin=[1500, 1000, 0],
            outer_boundary="Radiation",
        )

        opatch2.create_lattice_pair(lattice_height="20mm", bottom_extend=False)

        opatch2.create_3dcomponent(replace=True)
        assert len(self.aedtapp.modeler.user_defined_components) == 2

        opatch3 = self.aedtapp.add_from_toolkit(
            RectangularPatchProbe,
            draw=True,
            frequency=1.0,
            origin=[1500, 1500, 0],
            outer_boundary="Radiation",
        )

        opatch3.create_lattice_pair(lattice_height="20mm", bottom_extend=True)

        assert len(opatch3.boundaries) == 3

    def test_02a_rectangular_patch_inset_model_hfss(self):
        self.aedtapp = self.add_app(design_name="rectangular_patch_inset")
        opatch1 = self.aedtapps[1].add_from_toolkit(RectangularPatchInset, draw=True, frequency=1.0)
        assert opatch1
        assert opatch1.object_list
        for comp in opatch1.object_list.values():
            assert isinstance(comp, Object3d)
        opatch1.substrate_height = 1.575
        face_center = list(opatch1.object_list.values())[0].faces[0].center
        assert opatch1.origin == [0, 0, 0]
        opatch1.origin = [10, 20, 500]
        assert opatch1.origin == [10, 20, 500]
        face_center_new = list(opatch1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [10, 20, 500])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3
        opatch2 = self.aedtapps[1].add_from_toolkit(
            RectangularPatchInset, draw=True, antenna_name=opatch1.antenna_name
        )
        assert opatch1.antenna_name != opatch2.antenna_name

    def test_02b_rectangular_patch_inset_duplicate_along_line(self):
        opatch = self.aedtapps[1].add_from_toolkit(
            RectangularPatchInset, draw=True, frequency=1.0, origin=[500, 20, 50]
        )
        new = opatch.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3

    def test_02c_rectangular_patch_inset_create_3dcomponent(self):
        opatch = self.aedtapps[1].add_from_toolkit(
            RectangularPatchInset, draw=True, frequency=1.0, origin=[500, 500, 0]
        )
        component_name = opatch.create_3dcomponent(replace=True)
        assert list(self.aedtapps[1].modeler.user_defined_components.keys())[0] == component_name

    def test_02d_rectangular_patch_inset_lattice_pair(self):
        opatch1 = self.aedtapps[1].add_from_toolkit(
            RectangularPatchInset,
            draw=True,
            frequency=1.0,
            origin=[1500, 500, 0],
            outer_boundary="Radiation",
        )

        opatch1.create_lattice_pair(lattice_height=None, bottom_extend=False)

        assert len(opatch1.boundaries) == 2

        opatch2 = self.aedtapps[1].add_from_toolkit(
            RectangularPatchInset,
            draw=True,
            frequency=1.0,
            origin=[1500, 1000, 0],
            outer_boundary="Radiation",
        )

        opatch2.create_lattice_pair(lattice_height="20mm", bottom_extend=False)

        opatch2.create_3dcomponent(replace=True)
        assert len(self.aedtapps[1].modeler.user_defined_components) == 2

        opatch3 = self.aedtapps[1].add_from_toolkit(
            RectangularPatchInset,
            draw=True,
            frequency=1.0,
            origin=[1500, 1500, 0],
            outer_boundary="Radiation",
        )

        opatch3.create_lattice_pair(lattice_height="20mm", bottom_extend=True)

        assert len(opatch3.boundaries) == 2

    def test_03a_rectangular_patch_edge_model_hfss(self):
        self.aedtapp = self.add_app(design_name="rectangular_patch_edge")
        opatch1 = self.aedtapps[2].add_from_toolkit(RectangularPatchEdge, draw=True, frequency=1.0)
        assert opatch1
        assert opatch1.object_list
        for comp in opatch1.object_list.values():
            assert isinstance(comp, Object3d)
        opatch1.substrate_height = 1.575
        face_center = list(opatch1.object_list.values())[0].faces[0].center
        assert opatch1.origin == [0, 0, 0]
        opatch1.origin = [-100, 20, -500]
        assert opatch1.origin == [-100, 20, -500]
        face_center_new = list(opatch1.object_list.values())[0].faces[0].center
        face_center_eval = GeometryOperators.v_sum(face_center, [-100, 20, -500])
        assert GeometryOperators.points_distance(face_center_eval, face_center_new) < 1e-3
        opatch2 = self.aedtapps[2].add_from_toolkit(
            RectangularPatchEdge, draw=True, antenna_name=opatch1.antenna_name
        )
        assert opatch1.antenna_name != opatch2.antenna_name

    def test_03b_rectangular_patch_edge_duplicate_along_line(self):
        opatch = self.aedtapps[2].add_from_toolkit(RectangularPatchEdge, draw=True, frequency=1.0)
        new = opatch.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3

    def test_03c_rectangular_patch_edge_create_3dcomponent(self):
        opatch = self.aedtapps[2].add_from_toolkit(
            RectangularPatchEdge, draw=True, frequency=1.0, origin=[500, 500, 0]
        )
        component_name = opatch.create_3dcomponent(replace=True)
        assert list(self.aedtapps[2].modeler.user_defined_components.keys())[0] == component_name

    def test_03d_rectangular_patch_inset_lattice_pair(self):
        opatch1 = self.aedtapps[2].add_from_toolkit(
            RectangularPatchEdge,
            draw=True,
            frequency=1.0,
            origin=[1500, 500, 0],
            outer_boundary="Radiation",
        )

        opatch1.create_lattice_pair(lattice_height=None, bottom_extend=False)

        assert len(opatch1.boundaries) == 2

        opatch2 = self.aedtapps[2].add_from_toolkit(
            RectangularPatchEdge,
            draw=True,
            frequency=1.0,
            origin=[1500, 1000, 0],
            outer_boundary="Radiation",
        )

        opatch2.create_lattice_pair(lattice_height="20mm", bottom_extend=False)

        opatch2.create_3dcomponent(replace=True)
        assert len(self.aedtapps[2].modeler.user_defined_components) == 2

        opatch3 = self.aedtapps[2].add_from_toolkit(
            RectangularPatchEdge,
            draw=True,
            frequency=1.0,
            origin=[1500, 1500, 0],
            outer_boundary="Radiation",
        )

        opatch3.create_lattice_pair(lattice_height="20mm", bottom_extend=True)

        assert len(opatch3.boundaries) == 2
