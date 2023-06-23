from pyaedt.modeler.cad.object3d import Object3d
from pyaedt.modeler.geometry_operators import GeometryOperators
from ansys.aedt.toolkits.antennas.backend import models

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
        antenna_module = getattr(models, "RectangularPatchProbe")
        opatch1 = antenna_module(
            self.aedtapp,
            frequency=1.0,
            length_unit=self.aedtapp.modeler.model_units
        )
        opatch1.init_model()
        opatch1.model_hfss()
        opatch1.setup_hfss()

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
        antenna_module = getattr(models, "RectangularPatchProbe")
        opatch2 = antenna_module(
            self.aedtapp,
            antenna_name=opatch1.antenna_name
        )

        assert opatch1.antenna_name != opatch2.antenna_name

    def test_01b_rectangular_patch_probe_duplicate_along_line(self):
        self.aedtapp.design_name = "rectangular_patch_probe"
        antenna_module = getattr(models, "RectangularPatchProbe")
        opatch = antenna_module(
            self.aedtapp,
            frequency=1.0,
            origin=[500, 20, 50]
        )
        opatch.init_model()
        opatch.model_hfss()
        opatch.setup_hfss()

        new = opatch.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3

    def test_01c_rectangular_patch_probe_create_3dcomponent(self):
        self.aedtapp.design_name = "rectangular_patch_probe"
        antenna_module = getattr(models, "RectangularPatchProbe")
        opatch = antenna_module(
            self.aedtapp,
            frequency=1.0,
            origin=[500, 500, 0]
        )
        opatch.init_model()
        opatch.model_hfss()
        opatch.setup_hfss()

        component = opatch.create_3dcomponent(replace=True)
        assert list(self.aedtapp.modeler.user_defined_components.keys())[0] == component.name

    def test_01d_rectangular_patch_probe_lattice_pair(self):
        self.aedtapp.design_name = "rectangular_patch_probe"
        antenna_module = getattr(models, "RectangularPatchProbe")
        opatch1 = antenna_module(
            self.aedtapp,
            frequency=1.0,
            origin=[500, 500, 0],
            outer_boundary="Radiation",
        )
        opatch1.init_model()
        opatch1.model_hfss()
        opatch1.setup_hfss()

        opatch1.create_lattice_pair(lattice_height=None, bottom_extend=False)

        assert len(opatch1.boundaries) == 5

        opatch2 = antenna_module(
            self.aedtapp,
            frequency=1.0,
            origin=[1500, 1000, 0],
            outer_boundary="Radiation",
        )
        opatch2.init_model()
        opatch2.model_hfss()
        opatch2.setup_hfss()

        opatch2.create_lattice_pair(lattice_height="20mm", bottom_extend=False)

        opatch2.create_3dcomponent(replace=True)
        assert len(self.aedtapp.modeler.user_defined_components) == 2

        opatch3 = antenna_module(
            self.aedtapp,
            frequency=1.0,
            origin=[1500, 1500, 0],
            outer_boundary="Radiation",
        )
        opatch3.init_model()
        opatch3.model_hfss()
        opatch3.setup_hfss()

        opatch3.create_lattice_pair(lattice_height="20mm", bottom_extend=True)

        assert len(opatch3.boundaries) == 5

    def test_02a_rectangular_patch_inset_model_hfss(self):
        self.aedtapp = self.add_app(design_name="rectangular_patch_inset")
        antenna_module = getattr(models, "RectangularPatchInset")
        opatch1 = antenna_module(
            self.aedtapps[1],
            frequency=1.0,
            length_unit=self.aedtapps[1].modeler.model_units
        )
        opatch1.init_model()
        opatch1.model_hfss()
        opatch1.setup_hfss()

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
        opatch2 = antenna_module(
            self.aedtapps[1],
            antenna_name=opatch1.antenna_name
        )
        opatch2.init_model()
        opatch2.model_hfss()
        opatch2.setup_hfss()
        assert opatch1.antenna_name != opatch2.antenna_name

    def test_02b_rectangular_patch_inset_duplicate_along_line(self):
        antenna_module = getattr(models, "RectangularPatchInset")
        opatch = antenna_module(
            self.aedtapps[1],
            frequency=1.0,
            origin=[500, 20, 50]
        )
        opatch.init_model()
        opatch.model_hfss()
        opatch.setup_hfss()
        new = opatch.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3

    def test_02c_rectangular_patch_inset_create_3dcomponent(self):
        antenna_module = getattr(models, "RectangularPatchInset")
        opatch = antenna_module(
            self.aedtapps[1],
            frequency=1.0,
            origin=[500, 500, 0]
        )
        opatch.init_model()
        opatch.model_hfss()
        opatch.setup_hfss()
        component = opatch.create_3dcomponent(replace=True)
        assert list(self.aedtapps[1].modeler.user_defined_components.keys())[0] == component.name

    def test_02d_rectangular_patch_inset_lattice_pair(self):
        antenna_module = getattr(models, "RectangularPatchInset")
        opatch1 = antenna_module(
            self.aedtapps[1],
            frequency=1.0,
            origin=[1500, 500, 0],
            outer_boundary="Radiation",
        )
        opatch1.init_model()
        opatch1.model_hfss()
        opatch1.setup_hfss()

        opatch1.create_lattice_pair(lattice_height=None, bottom_extend=False)

        assert len(opatch1.boundaries) == 4
        opatch2 = antenna_module(
            self.aedtapps[1],
            frequency=1.0,
            origin=[1500, 1000, 0],
            outer_boundary="Radiation",
        )
        opatch2.init_model()
        opatch2.model_hfss()
        opatch2.setup_hfss()

        opatch2.create_lattice_pair(lattice_height="20mm", bottom_extend=False)

        opatch2.create_3dcomponent(replace=True)
        assert len(self.aedtapps[1].modeler.user_defined_components) == 2

        opatch3 = antenna_module(
            self.aedtapp,
            frequency=1.0,
            origin=[1500, 1500, 0],
            outer_boundary="Radiation",
        )
        opatch3.init_model()
        opatch3.model_hfss()
        opatch3.setup_hfss()

        opatch3.create_lattice_pair(lattice_height="20mm", bottom_extend=True)

        assert len(opatch3.boundaries) == 4

    def test_03a_rectangular_patch_edge_model_hfss(self):
        self.aedtapp = self.add_app(design_name="rectangular_patch_edge")
        antenna_module = getattr(models, "RectangularPatchInset")
        opatch1 = antenna_module(
            self.aedtapps[2],
            frequency=1.0,
            length_unit=self.aedtapps[2].modeler.model_units,
        )
        opatch1.init_model()
        opatch1.model_hfss()
        opatch1.setup_hfss()

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

        opatch2 = antenna_module(
            self.aedtapps[2],
            frequency=1.0,
            antenna_name=opatch1.antenna_name
        )
        assert opatch1.antenna_name != opatch2.antenna_name

    def test_03b_rectangular_patch_edge_duplicate_along_line(self):
        antenna_module = getattr(models, "RectangularPatchInset")
        opatch = antenna_module(
            self.aedtapps[2],
            frequency=1.0
        )
        opatch.init_model()
        opatch.model_hfss()
        opatch.setup_hfss()
        new = opatch.duplicate_along_line([0, 200, 0], 4)
        assert len(new) == 3

    def test_03c_rectangular_patch_edge_create_3dcomponent(self):
        antenna_module = getattr(models, "RectangularPatchInset")
        opatch = antenna_module(
            self.aedtapps[2],
            frequency=1.0,
            origin=[500, 500, 0]
        )
        opatch.init_model()
        opatch.model_hfss()
        opatch.setup_hfss()
        component = opatch.create_3dcomponent(replace=True)
        assert list(self.aedtapps[2].modeler.user_defined_components.keys())[0] == component.name

    def test_03d_rectangular_patch_inset_lattice_pair(self):
        antenna_module = getattr(models, "RectangularPatchInset")
        opatch1 = antenna_module(
            self.aedtapps[2],
            frequency=1.0,
            origin=[1500, 500, 0],
            outer_boundary="Radiation",
        )
        opatch1.init_model()
        opatch1.model_hfss()
        opatch1.setup_hfss()

        opatch1.create_lattice_pair(lattice_height=None, bottom_extend=False)

        assert len(opatch1.boundaries) == 4
        opatch2 = antenna_module(
            self.aedtapps[2],
            frequency=1.0,
            origin=[1500, 1000, 0],
            outer_boundary="Radiation",
        )
        opatch2.init_model()
        opatch2.model_hfss()
        opatch2.setup_hfss()

        opatch2.create_lattice_pair(lattice_height="20mm", bottom_extend=False)

        opatch2.create_3dcomponent(replace=True)
        assert len(self.aedtapps[2].modeler.user_defined_components) == 2

        opatch3 = antenna_module(
            self.aedtapps[2],
            frequency=1.0,
            origin=[1500, 1500, 0],
            outer_boundary="Radiation",
        )
        opatch3.init_model()
        opatch3.model_hfss()
        opatch3.setup_hfss()

        opatch3.create_lattice_pair(lattice_height="20mm", bottom_extend=True)

        assert len(opatch3.boundaries) == 4
