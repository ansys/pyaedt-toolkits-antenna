helix
=====
This section list the available helix antennas:

.. currentmodule:: ansys.aedt.toolkits.antennas.models.helix

.. autosummary::
   :toctree: _autosummary

   AxialMode

The API must be used using PyAEDT as in the following example:

.. code:: python

    from pyaedt import Hfss
    from ansys.aedt.toolkits.antennas.models.helix import AxialMode

    aedtapp = Hfss(specified_version="2023.1", non_graphical=False)
    # Create antenna
    ohorn = aedtapp.add_from_toolkit(AxialMode, draw=True)
    ...
    aedtapp.release_desktop()


