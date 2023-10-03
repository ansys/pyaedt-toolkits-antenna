import json
import os

from ansys.aedt.toolkits.antenna.backend.common.properties_data import PropertiesData

with open(os.path.join(os.path.dirname(__file__), "general_properties.json")) as fh:
    _general_properties = json.load(fh)

general_settings = PropertiesData(_general_properties)

be_properties = PropertiesData({})
be_properties._unfreeze()
