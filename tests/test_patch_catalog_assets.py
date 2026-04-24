from pathlib import Path
import sys

import pytest

if sys.version_info >= (3, 11):
    import tomllib
else:
    import tomli as tomllib


PATCH_MODELS = {
    "ellipticaledge": {"catalog_name": "EllipticalEdge"},
    "ellipticalinset": {"catalog_name": "EllipticalInset"},
    "ellipticalprobe": {"catalog_name": "EllipticalProbe"},
    "mbynpatcharray": {"catalog_name": "MbyNPatchArray"},
    "seqrotated2patch": {"catalog_name": "SeqRotated2Patch"},
}


@pytest.mark.parametrize("folder_name,metadata", PATCH_MODELS.items())
def test_patch_catalog_assets(folder_name, metadata):
    base_path = (
        Path(__file__).parent.parent
        / "src"
        / "ansys"
        / "aedt"
        / "toolkits"
        / "antenna"
        / "ui"
        / "windows"
        / "antenna_catalog"
        / "patch"
        / folder_name
    )
    assert base_path.is_dir()

    preview_files = list(base_path.glob("*.jpg")) + list(base_path.glob("*.png"))
    assert len(preview_files) == 1
    assert preview_files[0].stat().st_size > 0

    parameters_file = base_path / "parameters.toml"
    assert parameters_file.is_file()

    model_properties = tomllib.loads((base_path / "model" / "properties.toml").read_text(encoding="utf-8"))
    object_names = [entry["name"] for key, entry in model_properties.items() if key.startswith("object_")]
    assert object_names

    for object_name in object_names:
        obj_file = base_path / "model" / f"{object_name}.obj"
        assert obj_file.is_file()
        obj_text = obj_file.read_text(encoding="utf-8")
        assert "Placeholder" not in obj_text
        assert sum(line.startswith("v ") for line in obj_text.splitlines()) >= 4


def test_patch_catalog_family_wiring():
    catalog = (
        Path(__file__).parent.parent
        / "src"
        / "ansys"
        / "aedt"
        / "toolkits"
        / "antenna"
        / "ui"
        / "windows"
        / "antenna_catalog"
        / "antenna_catalog.toml"
    )
    data = tomllib.loads(catalog.read_text(encoding="utf-8"))
    patch_models = data["Patch"]["models"]
    for metadata in PATCH_MODELS.values():
        assert metadata["catalog_name"] in patch_models
