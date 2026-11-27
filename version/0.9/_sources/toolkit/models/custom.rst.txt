Custom
======

This page list the classes available for custom antennas:

.. currentmodule:: ansys.aedt.toolkits.antenna.backend.antenna_models.custom

.. autosummary::
   :toctree: _autosummary

   GPSPatchCeramic


You must use these methods from PyAEDT as shown in this example:

.. code:: python

    from ansys.aedt.core import Hfss

    from ansys.aedt.toolkits.antenna.backend.antenna_models.custom import GPSPatchCeramic

    aedtapp = Hfss()

    # Create antenna
    oantenna1 = GPSPatchCeramic(app)
    oantenna1.frequency = 12.0
    oantenna1.model_hfss()
    oantenna1.setup_hfss()
    ...
    aedtapp.release_desktop()

