Patch
======
This section list the available patch antennas:

.. currentmodule:: ansys.aedt.toolkits.antennas.models.patch

.. autosummary::
   :toctree: _autosummary

   RectangularPatchEdge
   RectangularPatchProbe
   RectangularPatchInset

The API must be used using PyAEDT as in the following example:

.. code:: python

    from pyaedt import Hfss
    from ansys.aedt.toolkits.antennas.models.patch import RectangularPatchEdge

    aedtapp = Hfss(specified_version="2023.1", non_graphical=False)
    # Create antenna
    ohorn = aedtapp.add_from_toolkit(RectangularPatchEdge, draw=True)
    ...
    aedtapp.release_desktop()


