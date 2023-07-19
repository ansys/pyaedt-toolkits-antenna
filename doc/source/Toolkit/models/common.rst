Common
======
This section list the available common methods:

.. currentmodule:: ansys.aedt.toolkits.antennas.backend.models.common

.. autosummary::
   :toctree: _autosummary

   TransmissionLine
   StandardWaveguide

The API must be used using PyAEDT as in the following example:

.. code:: python

    from ansys.aedt.toolkits.antennas.backend.models.common import TransmissionLine

    # Transmission line calculation
    tl_calc = TransmissionLine(frequency=2)
    tl_calc.stripline_calculator(substrate_height=10, permittivity=2.2, impedance=60)
