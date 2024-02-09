ToolkitGeneric API
==================
The ToolkitGeneric API contains the ```ToolkitGeneric`` class, which provides the generic methods
available in the backend. These methods are the same for all toolkits.

.. currentmodule:: ansys.aedt.toolkits.antenna.backend.common.api_generic

.. autosummary::
   :toctree: _autosummary

   ToolkitGeneric

The ``ToolkitGeneric`` class is accessible directly from the :doc:`api` because it is inherited.
The following code shows you can use both classes to create an object:

.. code:: python

    # Import required modules
    import time

    # Import backend services
    from ansys.aedt.toolkits.template.backend.api import Toolkit

    # Get backend object
    service = Toolkit()

    # Load default properties from a JSON file
    properties = service.get_properties()

    # Set properties
    new_properties = {"aedt_version": "2022.2"}
    service.set_properties(new_properties)
    properties = service.get_properties()

    # Get AEDT sessions
    sessions = service.aedt_sessions()

    # Launch AEDT
    msg = service.launch_aedt()

    # Wait until thread is finished
    response = service.get_thread_status()
    while response[0] == 0:
        time.sleep(1)
        response = service.get_thread_status()

    # Release AEDT
    service.release_aedt()


