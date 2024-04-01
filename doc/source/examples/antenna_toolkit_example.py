# Antenna toolkit example
#
# This example demonstrates how to use the ``ToolkitBackend`` class.
# It initiates AEDT through PyAEDT, sets up an empty HFSS design, and proceeds to create the antenna.


# ## Perform required imports
#
# Import the backend toolkit class.
import tempfile

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

# ## Create temporary directory

temp_dir = tempfile.TemporaryDirectory(suffix="_ansys")
project_name = pyaedt.generate_unique_project_name(rootname=temp_dir.name, project_name="antenna_toolkit")

# ## Set default properties

properties.aedt_version = aedt_version
properties.non_graphical = non_graphical
properties.active_project = project_name

# ## Initialize toolkit
#
# Initialize the toolkit.

toolkit_api = ToolkitBackend()

# ## Get available_antennas

print(toolkit_api.available_antennas)

# ## Get default properties

backend_properties = toolkit_api.get_properties()
frequency = backend_properties["antenna"]["synthesis"]["frequency"]
frequency_units = backend_properties["antenna"]["synthesis"]["frequency_unit"]
length_unit = backend_properties["antenna"]["synthesis"]["length_unit"]

# ## Modify default length units

properties.antenna.synthesis.length_unit = "cm"

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

# ## Initialize AEDT
#
# Launch a new AEDT session in a thread.

thread_msg = toolkit_api.launch_thread(toolkit_api.launch_aedt)

# ## Wait for the toolkit thread to be idle
#
# Wait for the toolkit thread to be idle and ready to accept a new task.

idle = toolkit_api.wait_to_be_idle()
if not idle:
    print("AEDT not initialized.")
    sys.exit()

# ## Create setup when antenna is created
#
# Set create_setup property.

properties.antenna.setup.create_setup = True

# ## Create antenna in HFSS
#
# Create antenna and setup in HFSS.

antenna_parameter = toolkit_api.get_antenna("RectangularPatchProbe")

# ## Trying to create a new antenna
#
# The antenna toolkit API does not allow the creation of more than one antenna. The user can use the antenna models API
# to create more than one antenna.

toolkit_api.get_antenna("BowTie")

# ## Set properties
#
# Move antenna X position

toolkit_api.update_parameters("pos_x", "20")

# ## Analyze design in batch mode

toolkit_api.analyze()

# ## Get scattering results

scattering_data = toolkit_api.scattering_results()

# ## Get farfield  results

farfield_data = toolkit_api.farfield_results()

# ## Get antenna model

files = toolkit_api.export_aedt_model()

# ## Release AEDT
#
# Release AEDT.

toolkit_api.release_aedt(True, True)

pass

# ## Plot results

# Plot exported files using the following code
# from pyaedt.generic.plot import ModelPlotter
# model = ModelPlotter()
# for file in files:
#     model.add_object(file[0], file[1], file[2])

# ## Clean temporary directory

temp_dir.cleanup()