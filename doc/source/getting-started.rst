===============
Getting started
===============

To run the Antenna Toolkit, you must have a licensed copy of AEDT installed.
You have multiple options for installing and launching this toolkit:

- You can install the toolkit directly in AEDT via an installation script and then launch it
  as a wizard. For more information, see :ref:`install-toolkit-AEDT`.
- You can install the toolkit from the AEDT console and then launch it as a wizard. For more
  information, see :ref:`install_toolkit_console_ui`.
- You can install and launch the toolkit directly from a Python console and then use the toolkit's APIs.
  For more information, see :ref:`install_toolkit_console_api`.

.. _install-toolkit-AEDT:

How to install directly in AEDT and launch as a wizard
------------------------------------------------------

You can install the Antenna Toolkit directly in AEDT using the base
interpreter from the AEDT installation.

#. From `Install from a Python file <https://aedt.docs.pyansys.com/version/stable//Getting_started/Installation.html#install-from-a-python-file>`_
   in the PyAEDT documentation, download the ``PyAEDTInstallerFromDesktop.py`` file and then run this Python script.

#. If this is the first toolkit being installed in AEDT, restart AEDT to update its **Tools** menu.

#. In AEDT, select **Tools > Toolkit > PyAEDT > Console** to load the PyAEDT console:

   .. image:: ./_static/console.png
      :width: 800
      :alt: PyAEDT console in AEDT

#. In the PyAEDT console, run these commands to add the Antenna Toolkit as a wizard (toolkit UI) in AEDT:

   .. code:: python

       desktop.add_custom_toolkit("AntennaWizard")
       exit()

#. Close the PyAEDT console.

#. In the AEDT toolbar, click the **AntennaWizard** button to open this wizard in AEDT:

   .. image:: ./_static/toolkit_in_AEDT.png
      :width: 800
      :alt: Antenna Toolkit in AEDT

   If the toolkit does not open, restart AEDT.

   .. image:: ./_static/design_connected.png
      :width: 800
      :alt: UI opened from AEDT, design tab

The Antenna Toolkit Wizard is connected directly to the AEDT session. For wizard usage information,
see :doc:`toolkit/ui`.

.. _install_toolkit_console_ui:

How to install from the AEDT console and launch as a wizard
-----------------------------------------------------------

You can install the Antenna Toolkit in a specific Python environment from the AEDT console.

- If you have an existing virtual environment, skip step 1.
- If you have already installed the toolkit in your virtual environment, skip step 2.

#. Create a fresh-clean Python environment and activate it:

   .. code:: text

       # Create a virtual environment
       python -m venv .venv

       # Activate it in a POSIX system
       source .venv/bin/activate

       # Activate it in a Windows CMD environment
       .venv\Scripts\activate.bat

       # Activate it in Windows PowerShell
       .venv\Scripts\Activate.ps1

#. Install the toolkit from the GitHub repository:

   .. code:: bash

       python -m pip install git+https://github.com/pyansys/pyaedt-toolkits-antenna.git

#. Launch the Antenna Toolkit Wizard:

   .. code:: bash

       python .venv\Lib\site-packages\ansys\aedt\toolkits\antenna\run_toolkit.py

#. On the **AEDT Settings** tab, create a new AEDT session or connect to an existing one:

   .. image:: ./_static/settings.png
        :width: 800
        :alt: UI opened from console, settings tab

For wizard usage information, see :doc:`toolkit/ui`.

.. _install_toolkit_console_api:

How to install from a Python console and use the toolkit's APIs
---------------------------------------------------------------

You can install the toolkit in a specific Python environment and use the toolkit's APIs.
The code example included in this topic shows how to use the APIs at the model level
and toolkit level.

.. note::
    The following procedure assumes that you have already performed steps 1 and 2 in
    :ref:`install_toolkit_console_ui`. These steps create and activate a virtual environment
    and install the toolkit from the GitHub repository.

#. Open a Python console in your virtual environment:

   .. code:: bash

       python

#. From the command line, use the toolkit to create an antenna.

   This code shows how to launch AEDT, create and synthesize a bowtie
   antenna, and run a simulation in HFSS:

   .. code:: python

       # Import required modules
       from pyaedt import Hfss
       from ansys.aedt.toolkits.antenna.backend.models.bowtie import BowTie

       # Open AEDT and create an HFSS design
       aedtapp = Hfss()

       # Create antenna object
       oantenna1 = BowTie(aedtapp)

       # Define parameters
       parameter_list = list(oantenna1.synthesis_parameters.__dict__.keys())

       # Change frequency
       oantenna1.frequency = 12.0

       # Create antenna in HFSS
       oantenna1.model_hfss()

       # Create setup in HFSS
       oantenna1.setup_hfss()

       # Release AEDT
       aedtapp.release_desktop()

#. To create an antenna from the toolkit level, use the :class:`Toolkit <ansys.aedt.toolkits.antenna.backend.api.Toolkit>`
   class.
   
   This code shows how to use the :class:`Toolkit <ansys.aedt.toolkits.antenna.backend.api.Toolkit>`
   class to get available antennas and their properties, open AEDT, update antenna properties,
   and create a bowtie antenna:

   .. code:: python

       # Import required modules
       import time
       from ansys.aedt.toolkits.antenna.backend.api import Toolkit

       # Backend object
       toolkit = Toolkit()

       # Get available antennas
       toolkit.available_antennas

       # Get properties
       properties = toolkit.get_properties()

       # Set properties
       properties = toolkit.set_properties({"length_unit": "cm"})

       # Launch AEDT in a thread
       toolkit.launch_aedt()

       # Wait until thread is finished
       response = toolkit.get_thread_status()

       while response[0] == 0:
           time.sleep(1)
           response = toolkit.get_thread_status()

       # Update antenna properties
       response = toolkit.set_properties({"substrate_height": 0.1575, "length_unit": "cm"})

       # Create a bowtie antenna
       toolkit.get_antenna("BowTie")

       # Release AEDT
       toolkit.release_aedt()
