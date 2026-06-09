.. _cli_guide:

CLI guide
#########

The AEDT Antenna Toolkit provides a powerful command-line interface (CLI) for designing and
synthesizing antennas directly from the terminal. The CLI is integrated with PyAEDT and can be
accessed using the ``pyaedt antenna`` command.

Overview
========

The CLI offers three main commands:

* **list**: Display all available antenna types
* **synthesize**: Calculate antenna dimensions without connecting to AEDT
* **create**: Create an antenna in a running AEDT/HFSS session

Installation
============

The CLI is automatically available after installing the antenna toolkit:

.. code-block:: bash

   pip install ansys-aedt-toolkits-antenna

For development installations:

.. code-block:: bash

   pip install -e .

.. note::
   If the ``pyaedt antenna`` command is not recognized, you may need to modify update your PyAEDT version.


Basic commands
==============

List available antennas
-----------------------

To see all supported antenna types organized by category:

.. code-block:: bash

   pyaedt antenna list

This command displays antenna types in a readable format:

.. code-block:: text

   Available antenna types:

     Bowtie
       bowtie-normal                (BowTieNormal)
       bowtie-rounded               (BowTieRounded)
       bowtie-slot                  (BowTieSlot)
     Patch
       rectangular-patch-edge       (RectangularPatchEdge)
       rectangular-patch-inset      (RectangularPatchInset)
       ...

For JSON output (useful for scripts):

.. code-block:: bash

   pyaedt --json antenna list


Synthesize antenna
------------------

The ``synthesize`` command calculates antenna dimensions based on your specifications
**without requiring AEDT to be running**.

Basic example - Bowtie antenna at 2.4 GHz:

.. code-block:: bash

   pyaedt antenna synthesize bowtie --frequency 2.4

Example output:

.. code-block:: text

   Synthesis results for bowtie (BowTieNormal):

     arm_length                   19.354
     inner_width                  0.968
     outer_width                  17.427
     port_gap                     0.968
     sub_h                        1.6
     sub_x                        77.455
     sub_y                        77.455

Patch antenna example:

.. code-block:: bash

   pyaedt antenna synthesize rectangular-patch-edge \
       --frequency 5.8 \
       --substrate-height 1.524

Using parameter files (YAML or JSON):

.. code-block:: bash

   pyaedt antenna synthesize bowtie --params-file my-antenna.yaml

Example ``my-antenna.yaml``:

.. code-block:: yaml

   synthesis:
     frequency: 2.4
     substrate_height: 1.6
     permittivity: 4.4
     length_unit: "mm"


Create antenna in AEDT
----------------------

The ``create`` command creates an antenna in a running AEDT session via gRPC.

**Prerequisites:**

1. AEDT must be running
2. gRPC server must be enabled (check the port number in AEDT)
3. An HFSS project should be open

Basic example:

.. code-block:: bash

   pyaedt antenna create bowtie \
       --port 50051 \
       --frequency 2.4 \
       --substrate-height 1.6

With setup creation and analysis options:

.. code-block:: bash

   pyaedt antenna create rectangular-patch-edge \
       --port 50051 \
       --frequency 5.8 \
       --substrate-height 1.524 \
       --create-setup \
       --component-3d \
       --sweep 20 \
       --num-cores 8

Specifying project and design:

.. code-block:: bash

   pyaedt antenna create bowtie \
       --port 50051 \
       --project "MyAntennaProject" \
       --design "BowTie_Design" \
       --frequency 2.4

Advanced usage
==============

Command-line options
--------------------

All synthesis parameters from the ``Synthesis`` Pydantic model are automatically
exposed as CLI options. Common options include:

* ``--frequency``: Operating frequency in GHz
* ``--substrate-height``: Substrate thickness
* ``--permittivity``: Relative permittivity (εr)
* ``--length-unit``: Unit for dimensions (mm, cm, in, etc.)
* ``--outer-boundary``: Outer boundary condition

For setup-related options (``create`` command only):

* ``--create-setup``: Create an analysis setup and sweep (default: False)
* ``--component-3d``: Create a 3D component (default: False)
* ``--lattice-pair``: Create a lattice pair (default: False)
* ``--sweep``: Sweep percentage (default: 20)
* ``--num-cores``: Number of cores for analysis (default: 4)

.. note::
   For boolean flags, you can also use ``--no-create-setup``, ``--no-component-3d``, etc.
   to explicitly disable them, which is useful when overriding values from parameter files.

To see all available options for a specific command:

.. code-block:: bash

   pyaedt antenna synthesize --help
   pyaedt antenna create --help

Using parameter files
---------------------

For complex configurations, use YAML or JSON files:

**YAML format:**

.. code-block:: yaml

   # antenna-config.yaml
   synthesis:
     frequency: 2.4
     substrate_height: 1.6
     permittivity: 4.4
     length_unit: "mm"

   setup:
     create_setup: true
     component_3d: true
     sweep: 25
     num_cores: 4

   param:
     custom_param1: "value1"
     custom_param2: 42

**JSON format:**

.. code-block:: json

   {
     "synthesis": {
       "frequency": 2.4,
       "substrate_height": 1.6,
       "permittivity": 4.4
     },
     "setup": {
       "create_setup": true,
       "sweep": 25
     }
   }

Use with:

.. code-block:: bash

   pyaedt antenna create bowtie --port 50051 --params-file antenna-config.yaml

You can override specific parameters from the file using command-line options:

.. code-block:: bash

   # Override setup options from config file
   pyaedt antenna create bowtie \
       --port 50051 \
       --params-file antenna-config.yaml \
       --no-create-setup \
       --frequency 3.0

Extra parameters
----------------

For antenna-specific parameters not in the standard synthesis model, use ``--param``:

.. code-block:: bash

   pyaedt antenna synthesize horn-pyramidal \
       --frequency 10 \
       --param "flare_angle=15" \
       --param "waveguide_type=WR90"

JSON output mode
----------------

All commands support JSON output for integration with scripts and automation.
The ``--json`` flag is used at the PyAEDT level, before the ``antenna`` command:

.. code-block:: bash

   pyaedt --json antenna synthesize bowtie --frequency 2.4

Example JSON output:

.. code-block:: json

   {
     "data": {
       "antenna": "bowtie",
       "class": "BowTieNormal",
       "parameters": {
         "arm_length": 0.038715,
         "inner_width": 0.001936,
         "outer_width": 0.034854,
         "port_gap": 0.001936,
         "sub_h": 1.6,
         "sub_x": 0.154909,
         "sub_y": 0.154909
       }
     }
   }
