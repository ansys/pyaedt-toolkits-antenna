.. _installation:

Installation
============

For users
^^^^^^^^^

If you are looking for a stable version of the AEDT Antenna Toolkit, we recommend using the
installer available in:

`Download stable version |release| <|github_release_url|>`_

If you prefer the latest development version, you can download the automatically generated
files from the continuous integration (CI) workflow. These artifacts are available from the
latest runs on the `main` branch:

`View CI artifacts from main branch <https://github.com/ansys/pyaedt-toolkits-antenna/actions/workflows/ci_cd.yml?query=branch%3Amain>`_

.. warning::

   CI artifacts are generated from the latest commits on the `main` branch and may contain experimental or unstable features.
   They are ideal for advanced users who want to try out the latest developments and provide early feedback.

For developers
^^^^^^^^^^^^^^

The AEDT Antenna Toolkit can be installed like any other open source package.

You can either install both the backend and user interface (UI) methods or install only the backend methods.

To install both the backend and UI methods, run this command:

.. code:: bash

    pip install pyaedt-toolkits-antenna[all]

If you only need the common API, install only the backend methods with this
command:

.. code:: bash

    pip install pyaedt-toolkits-antenna

To install the toolkit offline, you can use a wheelhouse.
On the `Releases <https://github.com/ansys/pyaedt-toolkits-antenna/releases>`_ page, you can find the wheelhouses for
specific release in its asserts and download the wheelhouse.

You can then install the toolkit with this command:

.. code:: bash

    pip install --no-cache-dir --no-index --find-links=<path_to_wheelhouse>/ansys-aedt-toolkits-antenna-v0.1.3-wheelhouse-windows-latest-3.10 ansys_aedt_toolkits_antenna

You can also install the toolkit using the toolkit manager. For more information,
see the toolkit manager (TBD).
