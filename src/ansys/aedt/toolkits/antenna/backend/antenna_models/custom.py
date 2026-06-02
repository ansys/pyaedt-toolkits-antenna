# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from collections import OrderedDict

import ansys.aedt.core.generic.constants as constants
from ansys.aedt.core.generic.general_methods import pyaedt_function_handler
from ansys.aedt.toolkits.antenna.backend.antenna_models.patch import CommonPatch
from ansys.aedt.toolkits.common.backend.logger_handler import logger


class GPSPatchCeramic(CommonPatch):
    """Manages the ACT-derived ceramic GPS patch antenna.

    This antenna is modeled after the ACT (ANSYS Customization Toolkit) reference
    design for a GPS L1-band (1.575 GHz) ceramic patch antenna with a coaxial feed.

    Parameters
    ----------
    *args : list
        Positional arguments forwarded to :class:`CommonPatch`.
    **kwargs : dict
        Keyword arguments forwarded to :class:`CommonPatch`.

    Examples
    --------
    Create a GPS ceramic patch antenna at the default frequency of 1.575 GHz:

    >>> from ansys.aedt.toolkits.antenna.backend.antenna_models.custom import GPSPatchCeramic
    >>> antenna = GPSPatchCeramic()
    """

    _default_input_parameters = {
        "name": "",
        "origin": [0, 0, 0],
        "length_unit": "mm",
        "coordinate_system": "Global",
        "frequency": 1.575,
        "frequency_unit": "GHz",
        "material": "Ceramic",
        "material_properties": {"permittivity": 68.0},
        "outer_boundary": "",
        "substrate_height": 2.0,
    }

    _reference_frequency_ghz = 1.575
    _reference_dimensions_mm = {
        "patch_x": 12.0,
        "patch_y": 12.0,
        "cutout": 1.1,
        "feed_x": -0.4,
        "feed_y": 0.9,
        "coax_inner_rad": 0.167,
        "coax_outer_rad": 0.565,
        "feed_length": 5.0,
        "sub_h": 2.0,
        "sub_x": 13.0,
        "sub_y": 13.0,
        "gnd_x": 60.0,
        "gnd_y": 60.0,
    }

    def __init__(self, *args, **kwargs):
        """Initialize the GPS ceramic patch antenna and compute synthesis parameters."""
        CommonPatch.__init__(self, self._default_input_parameters, *args, **kwargs)
        self._parameters = self.synthesis()
        self.update_synthesis_parameters(self._parameters)
        self.antenna_type = "GPSPatchCeramic"

    @pyaedt_function_handler()
    def synthesis(self):
        """Scale the ACT reference geometry from the nominal GPS center frequency.

        All reference dimensions defined in ``_reference_dimensions_mm`` are
        scaled by the ratio of the reference frequency (1.575 GHz) to the
        requested operating frequency and then converted to the active
        ``length_unit``.

        Returns
        -------
        collections.OrderedDict
            Alphabetically sorted mapping of parameter names to their scaled
            values expressed in ``self.length_unit``.  Also includes the
            position keys ``pos_x``, ``pos_y``, and ``pos_z`` taken directly
            from ``self.origin``.
        """
        freq_ghz = constants.unit_converter(self.frequency, "Freq", self.frequency_unit, "GHz")
        scale = self._reference_frequency_ghz / freq_ghz
        length_unit = self.length_unit

        parameters = {}
        for name, value in self._reference_dimensions_mm.items():
            scaled_value = value * scale
            parameters[name] = constants.unit_converter(scaled_value, "Length", "mm", length_unit)

        parameters["pos_x"] = self.origin[0]
        parameters["pos_y"] = self.origin[1]
        parameters["pos_z"] = self.origin[2]

        my_keys = list(parameters.keys())
        my_keys.sort()
        return OrderedDict([(i, parameters[i]) for i in my_keys])

    def _ensure_material(self):
        """Ensure the ceramic substrate material exists in the active HFSS project.

        If the material named by ``self.material`` is not already present in
        the AEDT material library, a new material is created and its
        ``permittivity`` and ``dielectric_loss_tangent`` properties are set
        from ``self.material_properties``.
        """
        if not self._app:
            return
        if (
            self.material in self._app.materials.mat_names_aedt
            or self.material in self._app.materials.mat_names_aedt_lower
        ):
            return

        material = self._app.materials.add_material(self.material)
        if self.material_properties:
            if "permittivity" in self.material_properties:
                material.permittivity = self.material_properties["permittivity"]
            if "dielectric_loss_tangent" in self.material_properties:
                material.dielectric_loss_tangent = self.material_properties["dielectric_loss_tangent"]

    @pyaedt_function_handler()
    def model_hfss(self):
        """Draw the ACT-derived ceramic GPS patch antenna in HFSS.

        Creates the following objects in the active HFSS design:

        * **sub** – ceramic dielectric substrate box.
        * **gnd** – ground-plane rectangle with a coaxial void.
        * **ant** – rectangular patch with a triangular polarisation cutout.
        * **feed_pin** – inner conductor cylinder through the substrate.
        * **feed_coax** – inner conductor extension below the ground plane.
        * **coax** – Teflon-filled outer coaxial cylinder.
        * **port_cap** – PEC end-cap closing the coaxial feed.
        * **port** – circular lumped-port face.

        All objects are moved to ``self.origin`` and grouped under
        ``self.name`` before the modeler view is fitted.

        Returns
        -------
        bool
            ``True`` when the antenna geometry was created successfully.
            ``False`` if the antenna already exists in ``self.object_list``.
        """
        if self.object_list:
            logger.debug("This antenna already exists")
            return False

        self._ensure_material()
        self.set_variables_in_hfss()

        patch_x = self.synthesis_parameters.patch_x.hfss_variable
        patch_y = self.synthesis_parameters.patch_y.hfss_variable
        cutout = self.synthesis_parameters.cutout.hfss_variable
        feed_x = self.synthesis_parameters.feed_x.hfss_variable
        feed_y = self.synthesis_parameters.feed_y.hfss_variable
        sub_h = self.synthesis_parameters.sub_h.hfss_variable
        sub_x = self.synthesis_parameters.sub_x.hfss_variable
        sub_y = self.synthesis_parameters.sub_y.hfss_variable
        coax_inner_rad = self.synthesis_parameters.coax_inner_rad.hfss_variable
        coax_outer_rad = self.synthesis_parameters.coax_outer_rad.hfss_variable
        feed_length = self.synthesis_parameters.feed_length.hfss_variable
        gnd_x = self.synthesis_parameters.gnd_x.hfss_variable
        gnd_y = self.synthesis_parameters.gnd_y.hfss_variable
        pos_x = self.synthesis_parameters.pos_x.hfss_variable
        pos_y = self.synthesis_parameters.pos_y.hfss_variable
        pos_z = self.synthesis_parameters.pos_z.hfss_variable

        antenna_name = self.name
        coordinate_system = self.coordinate_system

        sub = self._app.modeler.create_box(
            origin=["-" + sub_x + "/2", "-" + sub_y + "/2", "0"],
            sizes=[sub_x, sub_y, sub_h],
            name="sub_" + antenna_name,
            material=self.material,
            new_properties={"Coordinate System": coordinate_system},
        )
        sub.color = (0, 128, 0)
        sub.transparency = 0.8

        gnd = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + gnd_x + "/2", "-" + gnd_y + "/2", "0"],
            sizes=[gnd_x, gnd_y],
            name="gnd_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        gnd.color = (255, 128, 65)
        gnd.transparency = 0.1

        ant = self._app.modeler.create_rectangle(
            orientation=2,
            origin=["-" + patch_x + "/2", "-" + patch_y + "/2", sub_h],
            sizes=[patch_x, patch_y],
            name="ant_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        ant.color = (255, 128, 65)
        ant.transparency = 0.1

        cutout_triangle = self._app.modeler.create_polyline(
            [
                ["-" + patch_x + "/2", patch_y + "/2", sub_h],
                ["-" + patch_x + "/2+" + cutout, patch_y + "/2", sub_h],
                ["-" + patch_x + "/2", patch_y + "/2-" + cutout, sub_h],
                ["-" + patch_x + "/2", patch_y + "/2", sub_h],
            ],
            cover_surface=True,
            name="cutout_" + antenna_name,
        )

        # Set coordinate system of polyline
        cutout_obj = self._app.get_oo_object(self._app.oeditor, cutout_triangle.name)
        self._app.set_oo_property_value(
            aedt_object=cutout_obj,
            object_name="CreatePolyline:1",
            prop_name="Coordinate System",
            value=coordinate_system,
        )

        self._app.modeler.subtract(ant, cutout_triangle, False)

        void = self._app.modeler.create_circle(
            orientation=2,
            origin=[feed_x, feed_y, "0"],
            radius=coax_outer_rad,
            name="void_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        self._app.modeler.subtract(gnd, void, False)

        feed_pin = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[feed_x, feed_y, "0"],
            radius=coax_inner_rad,
            height=sub_h,
            name="feed_pin_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        feed_pin.color = (255, 128, 65)

        feed_coax = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[feed_x, feed_y, "0"],
            radius=coax_inner_rad,
            height="-" + feed_length,
            name="feed_coax_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        feed_coax.color = (255, 128, 65)

        coax = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[feed_x, feed_y, "0"],
            radius=coax_outer_rad,
            height="-" + feed_length,
            name="coax_" + antenna_name,
            material="Teflon (tm)",
            new_properties={"Coordinate System": coordinate_system},
        )
        coax.color = (128, 255, 255)

        port_cap = self._app.modeler.create_cylinder(
            orientation=2,
            origin=[feed_x, feed_y, "-" + feed_length],
            radius=coax_outer_rad,
            height="-1mm",
            name="port_cap_" + antenna_name,
            material="pec",
            new_properties={"Coordinate System": coordinate_system},
        )
        port_cap.color = (132, 132, 193)

        port = self._app.modeler.create_circle(
            orientation=2,
            origin=[feed_x, feed_y, "-" + feed_length],
            radius=coax_outer_rad,
            name="port_" + antenna_name,
            new_properties={"Coordinate System": coordinate_system},
        )
        port.color = (128, 0, 0)

        self.object_list[sub.name] = sub
        self.object_list[gnd.name] = gnd
        self.object_list[ant.name] = ant
        self.object_list[feed_pin.name] = feed_pin
        self.object_list[feed_coax.name] = feed_coax
        self.object_list[coax.name] = coax
        self.object_list[port_cap.name] = port_cap
        self.object_list[port.name] = port

        self._app.modeler.move(list(self.object_list.keys()), [pos_x, pos_y, pos_z])

        for antenna_obj in self.object_list.values():
            antenna_obj.group_name = antenna_name
        self._app.modeler.fit_all()
        return True

    @pyaedt_function_handler()
    def model_disco(self):
        """Model the antenna in PyDiscovery.

        .. note::
            Not yet implemented.
        """
        pass

    @pyaedt_function_handler()
    def setup_disco(self):
        """Set up the antenna model in PyDiscovery.

        .. note::
            Not yet implemented.
        """
        pass
