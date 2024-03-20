# Antenna toolkit example
#
# This example demonstrates how to use the ``ToolkitBackend`` class.
# It initiates AEDT through PyAEDT, sets up an empty HFSS design, and proceeds to create the antenna.


# ## Perform required imports
#
# Import the antenna toolkit class and PyAEDT.

import pyaedt

from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend
from ansys.aedt.toolkits.antenna.backend.models import properties

# ##  Set AEDT version
#
# Set AEDT version.

aedt_version = "2024.1"

# ## Set non-graphical mode
#
# Set non-graphical mode.

non_graphical = False

# ## Set default properties
#

properties.aedt_version = aedt_version
properties.non_graphical = non_graphical

# ## Initialize toolkit
#
# Initialize the toolkit.

toolkit_api = ToolkitBackend()

# ## Get available_antennas
#

print(toolkit_api.available_antennas)

# ## Get available_antennas
#

backend_properties = toolkit_api.get_properties()
frequency = backend_properties["antenna"]["synthesis"]["frequency"]
frequency_units = backend_properties["antenna"]["synthesis"]["frequency_unit"]
length_unit = backend_properties["antenna"]["synthesis"]["length_unit"]

# ## Create antenna object only for synthesis
#
# Create antenna object.

antenna_parameters0 = toolkit_api.get_antenna("RectangularPatchProbe", synth_only=True)

print(
    "Patch X length: {}{} at {}{}".format(
        str(antenna_parameters0["patch_x"]),
        length_unit,
        frequency,
        frequency_units,
    )
)

# ## Change synthesis frequency
#
# Modify resonance frequency and modify parameters with set_properties method.

new_frequency1 = 12.0
new_properties = {"frequency": new_frequency1}
toolkit_api.set_properties(new_properties)

antenna_parameters1 = toolkit_api.get_antenna("RectangularPatchProbe", synth_only=True)

print(
    "Patch X length: {}{} at {}{}".format(
        str(antenna_parameters1["patch_x"]),
        length_unit,
        new_frequency1,
        frequency_units,
    )
)

# ## Change synthesis frequency
#
# Modify resonance frequency with properties directly.

new_frequency2 = 15.0
properties.antenna.synthesis.frequency = new_frequency2

antenna_parameters2 = toolkit_api.get_antenna("RectangularPatchProbe", synth_only=True)

print(
    "Patch X length: {}{} at {}{}".format(
        str(antenna_parameters2["patch_x"]),
        length_unit,
        new_frequency2,
        frequency_units,
    )
)

# ## Create an empty HFSS design
#
# Create an empty HFSS design.

app = pyaedt.Hfss(specified_version=aedt_version, non_graphical=non_graphical)

# ## Create antenna in HFSS
#
# Create antenna object, change frequency synthesis, create antenna and setup in HFSS.

oantenna1 = BowTieRounded(app)

# Create antenna in HFSS.
oantenna1.model_hfss()

# Create antenna setup.

oantenna1.setup_hfss()

# Change default name.

oantenna1.name = "MyAmazingAntenna"

# ## Create antenna in HFSS
#
# Create antenna object, change origin parameter in the antenna definition, create antenna and setup in HFSS.

oantenna2 = BowTieRounded(app, origin=[200, 50, 0], name="MyAntenna")
oantenna2.model_hfss()
oantenna2.setup_hfss()

# ## Release AEDT
#
# Release AEDT.

app.release_desktop(True, True)
