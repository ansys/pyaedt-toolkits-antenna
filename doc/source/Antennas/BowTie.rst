BowTie
======
This section list the available bowtie antennas:

.. currentmodule:: ansys.aedt.toolkits.antennas.models.bowtie

.. autosummary::
   :toctree: _autosummary

   BowTie
   BowTieRounded
   BowTieSlot

The API must be used using PyAEDT as in the following example:

.. code:: python

    from pyaedt import Hfss
    from ansys.aedt.toolkits.antennas.models.bowtie import BowTie
    aedtapp = Hfss(specified_version="2023.1",
                      non_graphical=False,
                      new_desktop_session=True,
                      close_on_exit=True,
                      student_version=False):
    # Create antenna
    ohorn = aedtapp.add_from_toolkit(BowTie, draw=True)
    ...
    aedtapp.release_desktop()


