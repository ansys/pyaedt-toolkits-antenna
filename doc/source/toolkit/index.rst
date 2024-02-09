
.. _antenna_toolkit_api_ref:

=============
API reference
=============

This section provides descriptions of the three APIs available for the Antenna Toolkit:

- **Toolkit API**: Contains the ``Toolkit`` class, which provides methods for
  controlling the toolkit workflow. In addition to methods for creating an AEDT
  session or connecting to an existing AEDT session, this API provides methods
  for synthesizing and creating an antenna. You use the Toolkit API at the
  toolkit level.

- **Antenna API**: Contains classes for all antenna types available in the toolkit.
  You use the Antenna API at the model level.

- **ToolkitGeneric**: Contains the ``ToolkitGeneric`` class, which provides basic
  functions for controlling AEDT that are shared between the backend and frontend.
  These functions are the same for all AEDT toolkits. You use the ToolkitGeneric API
  at the toolkit level.


.. toctree::
   :maxdepth: 2

   api
   models/index
   api_generic
