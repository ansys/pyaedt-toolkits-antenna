===============
Getting started
===============

To run this toolkit, you must have a licensed copy of Ansys Electronics Desktop (AEDT) installed.

The toolkit could be launched from:

- AEDT, see :ref:`install-toolkit-AEDT`.

- From a python console, see :ref:`install_toolkit_console_ui` or :ref:`install_toolkit_console_api`

The toolkit features can be accessed from:

- The user interface (UI), see :doc:`Toolkit/ui`.

- The API, see :doc:`Toolkit/index`.

.. _install-toolkit-AEDT:

How to install inside AEDT and run the UI
-----------------------------------------

This section shows how to install the toolkit inside the Ansys Electronics Desktop (AEDT) using the base
interpreter from AEDT installation.

The toolkit can be installed inside AEDT using
`PyAEDT <https://aedt.docs.pyansys.com/version/stable//>`_.

#. Download and run the install script from the `PyAEDT documentation <https://aedt.docs.pyansys.com/version/stable//Getting_started/Installation.html>`_.
   Note that **AEDT must be restarted**
   to update the **Tools** menu if this is the first time a Toolkit has been installed in AEDT.


#. Open the console:

    .. image:: ./_static/toolkits.png
      :width: 800
      :alt: PyAEDT toolkits in AEDT

    .. image:: ./_static/console.png
      :width: 800
      :alt: PyAEDT console in AEDT


#. Run the PyAEDT command: `add custom toolkit method <https://aedt.docs.pyansys.com/version/stable/API/_autosummary/pyaedt.desktop.Desktop.add_custom_toolkit.html#pyaedt.desktop.Desktop.add_custom_toolkit>`_:

    .. code:: python

      desktop.add_custom_toolkit("TemplateToolkit")
      exit()

#. Close the console and open the toolkit, if you do not restart AEDT, you need to *Update Menu*:

    .. image:: ./_static/toolkit_in_AEDT.png
      :width: 800
      :alt: Template toolkit in AEDT

#. The toolkit UI is connected directly to the AEDT session:

    .. image:: ./_static/design_connected.png
      :width: 800
      :alt: UI opened from AEDT, design tab

.. _install_toolkit_console_ui:

How to install in the console and run the UI
--------------------------------------------

This section shows how to install the toolkit in an specific python environment.

If you have an existing virtual environment you can skip step 1.

If you have installed the toolkit in the virtual environment you can skip step 2.

#. Create a fresh-clean Python environment and activate it:

   .. code:: bash

      # Create a virtual environment
      python -m venv .venv

      # Activate it in a POSIX system
      source .venv/bin/activate

      # Activate it in a Windows CMD environment
      .venv\Scripts\activate.bat

      # Activate it in Windows PowerShell
      .venv\Scripts\Activate.ps1

#. Install the toolkit from git:

    .. code:: bash

      python -m pip install git+https://github.com/pyansys/pyaedt-toolkit-template.git

#. Launch the toolkit UI:

    .. code:: bash

      python .venv\Lib\site-packages\ansys\aedt\toolkits\template\run_toolkit.py

#. Settings tab to create a new AEDT session or connect to an existing one:

    .. image:: ./_static/settings.png
      :width: 800
      :alt: UI opened from console, settings tab

.. _install_toolkit_console_api:

How to install in the console and use the API
---------------------------------------------

This section shows how to install the toolkit in an specific python environment and use the API.

#. Follow the step 1 and 2 described in :ref:`install_toolkit_console_ui`.

#. Open a python console in the corresponding virtual environment:

    .. code:: bash

      python

#. Open AEDT and draw a sphere in a random position by run these commands:

    .. code:: python

      # Import required modules for the example
      import time

      # Import backend services
      from ansys.aedt.toolkits.template.backend.api import Toolkit

      # Backend object
      service = Toolkit()

      # Get service properties
      properties = service.get_properties()

      # Change geometry type
      new_properties = {"geometry": "Sphere"}
      service.set_properties(new_properties)

      # Launch AEDT in a thread
      service.launch_aedt()

      # Wait until thread is finished
      response = service.get_thread_status()

      while response[0] == 0:
          time.sleep(1)
          response = service.get_thread_status()

      # Create a sphere in a random position in a thread
      b = service.create_geometry()

      # Wait until thread is finished
      response = service.get_thread_status()
      while response[0] == 0:
          time.sleep(1)
          response = service.get_thread_status()

      # Get number of solids added
      len(service.comps)

      # Desktop is released here
      service.release_aedt()
