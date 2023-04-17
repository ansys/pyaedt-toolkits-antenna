Horn
====
This section list the available horns:

.. currentmodule:: ansys.aedt.toolkits.antennas.models.horn

.. autosummary::
   :toctree: _autosummary

   Conical
   Corrugated
   Elliptical
   EPlane
   HPlane
   Pyramidal
   PyramidalRidged
   QuadRidged

The API must be used using PyAEDT as in the following example:

.. code:: python

    from pyaedt import Hfss
    from ansys.aedt.toolkits.antennas.models.horn import Conical

    aedtapp = Hfss(specified_version="2023.1", non_graphical=False)
    # Create antenna
    ohorn = aedtapp.add_from_toolkit(Conical, draw=True)
    ...
    aedtapp.release_desktop()


