Bowtie
======
This page list the classes available for bowtie antennas:

.. currentmodule:: ansys.aedt.toolkits.antenna.backend.models.bowtie

.. autosummary::
   :toctree: _autosummary

   BowTie
   BowTieRounded
   BowTieSlot

You must use these methods from PyAEDT as shown in this example:

.. code:: python

    from pyaedt import Hfss

    from ansys.aedt.toolkits.antenna.backend.models.bowtie import BowTie

    aedtapp = Hfss()

    # Create antenna
    oantenna1 = BowTie(app)
    oantenna1.frequency = 12.0
    oantenna1.model_hfss()
    oantenna1.setup_hfss()
    ...
    aedtapp.release_desktop()
