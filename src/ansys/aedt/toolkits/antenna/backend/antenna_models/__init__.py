# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from ansys.aedt.toolkits.antenna.backend.antenna_models.bowtie import BowTieNormal as BowTieNormal
from ansys.aedt.toolkits.antenna.backend.antenna_models.bowtie import BowTieRounded as BowTieRounded
from ansys.aedt.toolkits.antenna.backend.antenna_models.bowtie import BowTieSlot as BowTieSlot
from ansys.aedt.toolkits.antenna.backend.antenna_models.conical_spiral import Archimedean as Archimedean
from ansys.aedt.toolkits.antenna.backend.antenna_models.conical_spiral import Log as Log
from ansys.aedt.toolkits.antenna.backend.antenna_models.conical_spiral import Sinuous as Sinuous
from ansys.aedt.toolkits.antenna.backend.antenna_models.helix import AxialMode as AxialMode
from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Conical as Conical
from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Corrugated as Corrugated
from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Elliptical as Elliptical
from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import EPlane as EPlane
from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import HPlane as HPlane
from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import Pyramidal as Pyramidal
from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import PyramidalRidged as PyramidalRidged
from ansys.aedt.toolkits.antenna.backend.antenna_models.horn import QuadRidged as QuadRidged
from ansys.aedt.toolkits.antenna.backend.antenna_models.patch import RectangularPatchEdge as RectangularPatchEdge
from ansys.aedt.toolkits.antenna.backend.antenna_models.patch import RectangularPatchInset as RectangularPatchInset
from ansys.aedt.toolkits.antenna.backend.antenna_models.patch import RectangularPatchProbe as RectangularPatchProbe
from ansys.aedt.toolkits.antenna.backend.antenna_models.yagiuda import QuasiYagi as QuasiYagi
from ansys.aedt.toolkits.antenna.backend.antenna_models.yagiuda import WireYagiUda as WireYagiUda
