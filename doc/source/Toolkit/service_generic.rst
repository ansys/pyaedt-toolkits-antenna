Generic service
===============
This section list the available generic methods in the backend, these methods are the same for all toolkits:

.. currentmodule:: ansys.aedt.toolkits.template.backend.common.service_generic

.. autosummary::
   :toctree: _autosummary

   ServiceGeneric

**ServiceGeneric** class is accessible directly from :doc:`service` because it is inherited, then
you can create an object as in the following example to use both classes:

.. code:: python

    # Import required modules for the example
    import time

    # Import backend services
    from ansys.aedt.toolkits.template.backend.service import ToolkitService

    # Backend object
    service = ToolkitService()

    # Get the default properties loaded from json file
    properties = service_generic.get_properties()

    # Set properties
    new_properties = {"aedt_version": "2022.2"}
    service_generic.set_properties(new_properties)
    properties = service_generic.get_properties()

    # Get AEDT sessions
    sessions = service.aedt_sessions()

    # Launch AEDT
    msg = service_generic.launch_aedt()

    # Wait until thread is finished
    response = service.get_thread_status()
    while response[0] == 0:
        time.sleep(1)
        response = service.get_thread_status()

    # Desktop is released here
    service_generic.release_aedt()


