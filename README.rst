PyAEDT antenna toolkit
======================
|pyansys| |python| |pypi| |GH-CI| |codecov| |MIT| |black|

.. |pyansys| image:: https://img.shields.io/badge/Py-Ansys-ffc107.svg?logo=data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAABAAAAAQCAIAAACQkWg2AAABDklEQVQ4jWNgoDfg5mD8vE7q/3bpVyskbW0sMRUwofHD7Dh5OBkZGBgW7/3W2tZpa2tLQEOyOzeEsfumlK2tbVpaGj4N6jIs1lpsDAwMJ278sveMY2BgCA0NFRISwqkhyQ1q/Nyd3zg4OBgYGNjZ2ePi4rB5loGBhZnhxTLJ/9ulv26Q4uVk1NXV/f///////69du4Zdg78lx//t0v+3S88rFISInD59GqIH2esIJ8G9O2/XVwhjzpw5EAam1xkkBJn/bJX+v1365hxxuCAfH9+3b9/+////48cPuNehNsS7cDEzMTAwMMzb+Q2u4dOnT2vWrMHu9ZtzxP9vl/69RVpCkBlZ3N7enoDXBwEAAA+YYitOilMVAAAAAElFTkSuQmCC
   :target: https://docs.pyansys.com/
   :alt: PyAnsys

.. |python| image:: https://img.shields.io/pypi/pyversions/pypyaedt-toolkits-ansys-aedt-toolkits-antennas?logo=pypi
   :target: https://pypi.org/project/pypyaedt-toolkits-ansys-aedt-toolkits-antennas/
   :alt: Python

.. |pypi| image:: https://img.shields.io/pypi/v/pypyaedt-toolkits-ansys-aedt-toolkits-antennas.svg?logo=python&logoColor=white
   :target: https://pypi.org/project/pypyaedt-toolkits-ansys-aedt-toolkits-antennas
   :alt: PyPI

.. |codecov| image:: https://codecov.io/gh/pyansys/pypyaedt-toolkits-ansys-aedt-toolkits-antennas/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/pyansys/pypyaedt-toolkits-ansys-aedt-toolkits-antennas
   :alt: Codecov

.. |GH-CI| image:: https://github.com/pyansys/pypyaedt-toolkits-ansys-aedt-toolkits-antennas/actions/workflows/ci_cd.yml/badge.svg
   :target: https://github.com/pyansys/pypyaedt-toolkits-ansys-aedt-toolkits-antennas/actions/workflows/ci_cd.yml
   :alt: GH-CI

.. |MIT| image:: https://img.shields.io/badge/License-MIT-yellow.svg
   :target: https://opensource.org/licenses/MIT
   :alt: MIT

.. |black| image:: https://img.shields.io/badge/code%20style-black-000000.svg?style=flat
   :target: https://github.com/psf/black
   :alt: Black


The ``pyaedt-antenna-toolkit`` package provides a Python wrapper for modeling
antennas using Ansys Electronics Desktop (AEDT).


How to install
--------------

Two installation modes are provided: user and developer.

For users
^^^^^^^^^

Before installing the latest ``pyaedt-antenna-toolkit`` package
in user mode, ensure that you have the latest version of
`pip`_ by running this command:

.. code:: bash

    python -m pip install -U pip

Then, to install the latest package, run this command:

.. code:: bash

    python -m pip install ansys-aedt-toolkits-antennas

For developers
^^^^^^^^^^^^^^

Installing this package in developer mode allows you to modify and
enhance the source. As indicated in :ref:`contributing_aedt`, before
making a contribution, ensure that you are thoroughly familiar
with the *PyAnsys Developer's Guide*.

To install the latest package in develper mode, perform these steps:

#. Clone the repository:

   .. code:: bash

      git clone https://github.com/pyansys/pyaedt-toolkits.git

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

#. To ensure that you have the latest required build system and documentation,
   testing, and CI tools, run this code:

   .. code:: bash

      python -m pip install -U pip flit tox
      python -m pip install -r requirements/requirements_build.txt
      python -m pip install -r requirements/requirements_doc.txt
      python -m pip install -r requirements/requirements_tests.txt


#. Install the project in editable mode by run this command:

    .. code:: bash
    
      python -m pip install --editable ansys-aedt-toolkits-antennas
    
#. Verify your development installation by running this command:

   .. code:: bash
        
      tox


How to test
-----------

This project takes advantage of `tox`_, which is a tool for automating common
development tasks. While similar to Makefile, ``tox`` is oriented towards Python
development. It uses *environments*, which are similar to Makefile
rules, to make it highly customizable.. 

Using ``tox``
^^^^^^^^^^^^^

While Makefile has rules, `tox`_ has environments. In fact, ``tox`` creates its
own virtual environment to isolate anything being tested from the project
to guarantee the project's integrity. The following environments commands are provided:

- **tox -e style**: Checks the code style of your project.
- **tox -e py**: Runs your test suite.
- **tox -e py-coverage**: Checks your unit tests for code coverage.
- **tox -e doc**: Builds the documentation of your project.


Raw testing
^^^^^^^^^^^

If required, you can use Python tools like `black`_, `isort`_, `flake8`_
and `pytest`_ from the command line for code style checking, import sorting,
and testing. However, using these tools does not guarantee that your project
is being tested in an isolated environment, which is why tools like ``toc``_ exist.


Using ``pre-commit``
^^^^^^^^^^^^^^^^^^^^

The style checks take advantage of `pre-commit`_. While developers are not forced to
install this tool, they are are encouraged to run this command to install it:

.. code:: bash

    python -m pip install pre-commit && pre-commit install


Documentation
-------------

For building documentation, you can run the usual rules provided in the
`Sphinx`_ Makefile, like shown in this command:

.. code:: bash

    make -C doc/ html && your_browser_name doc/html/index.html

However, the recommended way of checking documentation integrity is by using
``tox``, like shown in this command:

.. code:: bash

    tox -e doc && your_browser_name .tox/doc_out/index.html


Distributing
------------

If you would like to create either source or wheel files, run
the following code to install the building requirements and
execute the build module:

.. code:: bash

    python -m pip install -r requirements/requirements_build.txt
    python -m build
    python -m twine check dist/*


.. LINKS AND REFERENCES
.. _black: https://github.com/psf/black
.. _flake8: https://flake8.pycqa.org/en/latest/
.. _isort: https://github.com/PyCQA/isort
.. _pip: https://pypi.org/project/pip/
.. _pre-commit: https://pre-commit.com/
.. _PyAnsys Developer's guide: https://dev.docs.pyansys.com/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _tox: https://tox.wiki/
