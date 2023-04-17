PyAEDT Antenna toolkit
======================

|pyansys| |PythonVersion| |GH-CI| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |PythonVersion| image:: https://img.shields.io/badge/python-3.7+-blue.svg
   :target: https://www.python.org/downloads/

.. |GH-CI| image:: https://github.com/pyansys/pyaedt-antenna-toolkit/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/pyansys/pyaedt-antenna-toolkit/actions/workflows/ci_cd.yml

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
  :target: https://github.com/psf/black
  :alt: black

The ``pyaedt-antenna-toolkit`` package provides a Python wrapper for modeling
antennas using Ansys Electronics Desktop (AEDT). The toolkit could be launched
from AEDT or from a python console, and it could be used through the user interface or in standalone mode.

Requirements
~~~~~~~~~~~~
In addition to the runtime dependencies listed in the installation information, this toolkit
requires Ansys Electronics Desktop (AEDT) 2022 R1 or later. The AEDT Student Version is also supported.

How to install
~~~~~~~~~~~~~~

How to install the toolkit inside AEDT
--------------------------------------

The toolkit could be installed inside AEDT using
`PyAEDT <https://aedt.docs.pyansys.com/version/stable//>`_.

If you have an existing virtual environment, you can skip step 1, and
if you have PyAEDT installed, you can skip step 2:

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

#. Install PyAEDT by run this command:

    .. code:: bash

      python -m pip install pyaedt

#. Open python console:

    .. code:: bash

      python

#. Open AEDT by run this command:

    .. code:: python

        # Launch AEDT
        from pyaedt import Desktop

        aedtapp = Desktop(
            specified_version="2023.1",
            non_graphical=False,
            new_desktop_session=True,
            close_on_exit=True,
            student_version=False,
        )
        # Install toolkit inside AEDT
        aedtapp.add_custom_toolkit("AntennaWizard")
        # Desktop is released here
        aedtapp.release_desktop()

#. If you are using Python 3.7 base interpreter from AEDT 2023R1 in Windows, uninstall pywin32 module by run this command:

    .. code:: bash

        python -m pip uninstall pywin32

#. Open AEDT manually, create an HFSS design and run the toolkit:

.. image:: ./Resources/toolkit_in_AEDT.png
  :width: 800
  :alt: PyAEDT toolkit installed

How to install the toolkit in the console and run the UI
--------------------------------------------------------

If you have an existing virtual environment you can skip step 1,
if you have installed the toolkit in the virtual environment you can skip step 2:

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

      python -m pip install git+https://github.com/pyansys/pyaedt-antenna-toolkit.git

#. Launch the toolkit UI:

    .. code:: bash

      python .venv\Lib\site-packages\ansys\aedt\toolkits\antennas\antenna_toolkit.py

.. 






.. image:: ./Resources/antenna_toolkit.png
  :width: 800
  :alt: Antenna Toolkit UI, Design Tab

How to install the toolkit in the console and use the API
---------------------------------------------------------

If you have an existing virtual environment you can skip step 1,
if you have installed the toolkit in the virtual environment you can skip step 2:

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

      python -m pip install git+https://github.com/pyansys/pyaedt-antenna-toolkit.git

#. Open a python console:

    .. code:: bash

      python

#. Open AEDT and create a conical horn antenna by run this command:

    .. code:: python

        # Launch AEDT
        from pyaedt import Hfss

        aedtapp = Hfss(
            specified_version="2023.1",
            non_graphical=False,
            new_desktop_session=True,
            close_on_exit=True,
        )
        # Import conical horn antenna
        from ansys.aedt.toolkits.antennas.models.horn import Conical

        # Create antenna
        ohorn = aedtapp.add_from_toolkit(Conical, draw=True, frequency=1.0, huygens_box=True)
        # Desktop is released here
        aedtapp.release_desktop()

.. image:: ./Resources/horn_hfss.png
  :width: 800
  :alt: Conical horn in HFSS

Documentation and issues
------------------------
In addition to installation and usage information, the toolkit
documentation provides
`API reference <https://aedt.antenna.toolkit.docs.pyansys.com/version/dev/Antennas/antennas.html>`_,
and `Contribute
<https://aedt.antenna.toolkit.docs.pyansys.com/version/dev/Contributing.html>`_ sections.

On the `PyAEDT Antenna toolkit Issues <https://github.com/pyansys/pyaedt-antenna-toolkit/issues>`_ page, you can
create issues to submit questions, report bugs, and request new features.

License
-------
PyAEDT Antenna toolkit is licensed under the MIT license.

This module makes no commercial claim over Ansys whatsoever.
The use of the interactive control of PyAEDT Antenna toolkit requires a legally licensed
local copy of AEDT. For more information about AEDT, 
visit the `AEDT page <https://www.ansys.com/products/electronics>`_ 
on the Ansys website.
