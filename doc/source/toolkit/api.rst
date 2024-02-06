Toolkit API
===========

The Toolkit API contains the ``Toolkit`` class, which provides methods for
controlling the toolkit workflow. In addition to methods for creating an AEDT
session or connecting to an existing AEDT session, this API provides methods
for synthesizing and creating an antenna. You use the **Toolkit API** at the
toolkit level.

The frontend makes calls to the Toolkit API. This API wraps some of the methods
of the Antenna API.

.. currentmodule:: ansys.aedt.toolkits.antenna.backend.api

.. autosummary::
   :toctree: _autosummary

   Toolkit

You can use the Toolkit API as shown in this example:

.. code:: python

    # Import required modules for the example
    import time

    # Import backend
    from ansys.aedt.toolkits.template.backend.api import Toolkit

    # Initialize generic service
    service = Toolkit()

    # Get the default properties loaded from JSON file
    properties = service.get_properties()

    # Set properties
    new_properties = {"aedt_version": "2023.1"}
    service.set_properties(new_properties)
    properties = service.get_properties()

    # Launch AEDT
    msg = service.launch_aedt()

    # Wait until thread is finished
    response = service.get_thread_status()
    while response[0] == 0:
        time.sleep(1)
        response = service.get_thread_status()

    # Create geometry
    msg = service.create_geometry()

    # Wait until thread is finished
    response = service.get_thread_status()
    while response[0] == 0:
        time.sleep(1)
        response = service.get_thread_status()

    # Release AEDT
    service.release_aedt()
