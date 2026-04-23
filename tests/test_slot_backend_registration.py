# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#

from ansys.aedt.toolkits.antenna.backend import antenna_models
from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend


def test_slot_models_are_registered():
    backend = ToolkitBackend()
    model_inputs = {
        "SlotGap": {"frequency": 1.0, "length_unit": "mm"},
        "SlotMicrostrip": {"frequency": 1.0, "length_unit": "mm"},
        "SlotTBar": {"frequency": 1.0, "length_unit": "mm"},
        "SlotCavityBackedArray": {"frequency": 3.0, "length_unit": "mm"},
    }

    for model_name, kwargs in model_inputs.items():
        antenna_class = getattr(antenna_models, model_name)
        antenna = antenna_class(None, **kwargs)
        assert antenna.synthesis_parameters
        assert model_name in backend.available_antennas
        assert backend.get_antenna(model_name, synth_only=True)
