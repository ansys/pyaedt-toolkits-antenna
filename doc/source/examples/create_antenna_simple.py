# Bowtie antenna synthesis
#
# This example demonstrates how to synthesize a bowtie antenna using the ``ToolkitBackend`` class.
# It initiates AEDT through PyAEDT, sets up an empty HFSS design, and proceeds to create the antenna.


# ## Perform required imports
#
# Import the antenna toolkit class and PyAEDT.

import pyaedt

from ansys.aedt.toolkits.antenna.backend.antenna_models.bowtie import BowTieRounded

# ##  Set AEDT version
#
# Set AEDT version.

aedt_version = "2024.1"

# ## Set non-graphical mode
#
# Set non-graphical mode.

non_graphical = False

# ## Create antenna object only for synthesis
#
# Create antenna object.

oantenna1 = BowTieRounded(None)
print(
    "Arm length: {}{} at {}{}".format(
        str(oantenna1.synthesis_parameters.arm_length.value),
        oantenna1.length_unit,
        oantenna1.frequency,
        oantenna1.frequency_unit,
    )
)

# ## Change synthesis frequency
#
# Modify resonance frequency and modify parameters.

oantenna1.frequency = 12.0
print(
    "Arm length: {}{} at {}{}".format(
        str(oantenna1.synthesis_parameters.arm_length.value),
        oantenna1.length_unit,
        oantenna1.frequency,
        oantenna1.frequency_unit,
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
oantenna1.frequency = 12.0
oantenna1.model_hfss()
oantenna1.setup_hfss()

# ## Create antenna in HFSS
#
# Create antenna object, change origin parameter in the antenna definition, create antenna and setup in HFSS.

oantenna2 = BowTieRounded(app, origin=[200, 50, 0])
oantenna2.model_hfss()
oantenna2.setup_hfss()

# ## Release AEDT
#
# Release AEDT.

app.release_desktop(False, False)
