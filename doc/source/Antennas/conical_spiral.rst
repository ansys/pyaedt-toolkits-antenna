Conical spiral
==============
This section list the available conical spiral antennas:

.. currentmodule:: ansys.aedt.toolkits.antennas.models.conical_spiral

.. autosummary::
   :toctree: _autosummary

   Archimedean

The API must be used using PyAEDT as in the following example:

.. code:: python

    from pyaedt import Hfss
    from ansys.aedt.toolkits.antennas.models.conical_spiral import Archimedean

    aedtapp = Hfss(specified_version="2023.1", non_graphical=False)
    # Create antenna
    oantenna = aedtapp.add_from_toolkit(Archimedean, draw=True)
    ...
    aedtapp.release_desktop()


