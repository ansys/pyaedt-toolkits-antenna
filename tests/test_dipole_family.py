from pathlib import Path
import sys

from ansys.aedt.toolkits.antenna.backend import antenna_models
from ansys.aedt.toolkits.antenna.backend.api import ToolkitBackend

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


CATALOG_ROOT = (
    Path(__file__).resolve().parent
    / ".."
    / "src"
    / "ansys"
    / "aedt"
    / "toolkits"
    / "antenna"
    / "ui"
    / "windows"
    / "antenna_catalog"
)
CATALOG_ROOT = CATALOG_ROOT.resolve()


def test_dipole_models_are_exported_and_synthesize_without_aedt():
    planar = antenna_models.PlanarDipole(None, frequency=1.0, length_unit="mm")
    wire = antenna_models.WireDipole(None, frequency=1.0, length_unit="mm")

    assert planar.synthesis_parameters.dipole_length.value > 0
    assert planar.synthesis_parameters.sub_x.value > 0
    assert wire.synthesis_parameters.dipole_length.value > 0
    assert wire.synthesis_parameters.wire_rad.value > 0


def test_dipole_family_is_available_through_backend_synth_only_flow():
    toolkit = ToolkitBackend()
    toolkit.properties.antenna.synthesis.frequency = 1.0
    toolkit.properties.antenna.synthesis.frequency_unit = "GHz"
    toolkit.properties.antenna.synthesis.length_unit = "mm"

    planar = toolkit.get_antenna("PlanarDipole", synth_only=True)
    toolkit.oantenna = None
    wire = toolkit.get_antenna("WireDipole", synth_only=True)

    assert planar["dipole_length"] > 0
    assert planar["sub_y"] > 0
    assert wire["dipole_length"] > 0
    assert wire["wire_rad"] > 0


def test_dipole_catalog_files_are_wired():
    with (CATALOG_ROOT / "antenna_catalog.toml").open("rb") as file_handler:
        catalog = tomllib.load(file_handler)

    assert catalog["Dipole"]["models"] == ["PlanarDipole", "WireDipole"]

    for model in catalog["Dipole"]["models"]:
        model_dir = CATALOG_ROOT / "dipole" / model.lower()
        assert (model_dir / f"{model}.jpg").is_file()
        assert (model_dir / "parameters.toml").is_file()

        with (model_dir / "model" / "properties.toml").open("rb") as file_handler:
            properties = tomllib.load(file_handler)

        for key, value in properties.items():
            if key == "name":
                continue
            obj_file = model_dir / "model" / f"{value['name']}.obj"
            assert obj_file.is_file()
            assert obj_file.stat().st_size > 0
