import os
import sys

from cx_Freeze import Executable
from cx_Freeze import setup
import numpy

# General configuration
company_name = "Ansys Inc"
product_name = "Antenna Toolkit"

# Generate a random GUID
# import uuid
# random_guid = "{" + str(uuid.uuid4()) + "}"
random_guid = "{70a724f2-2396-4264-94ce-5edff0d7fbc1}"

# Requisites and directories
build_dir = "build"
dist_dir = "dist"
exe_name = f"AntennaToolkit.exe"
icon_path = r"cx\splash_icon.ico"
logo_path = r"cx\antenna.png"
run_script = r"src\ansys\aedt\toolkits\antenna\run_toolkit.py"
nsi_script = "setup.nsi"
license_file = "LICENSE"

# Create dist
os.makedirs(dist_dir, exist_ok=True)

# LICENSE verification
if not os.path.isfile(license_file):
    print(f"ERROR: LICENSE not found requires by: {nsi_script}")
    sys.exit(1)

# Packages
numpy_dir = os.path.dirname(numpy.__file__)
packages = [
    "pyaedt",
    "numpy",
    "pyedb",
    "matplotlib",
    "ansys.aedt.toolkits.common",
    "ansys.aedt.toolkits.antenna",
    "fileinput",
]

build_options = {
    "packages": packages,
    "includes": ["numpy", "numpy.f2py", "fileinput"],
    "excludes": ["tkinter*", "*sphinx*", "pyvista*", "vtk*", "sci*"],
    "include_msvcr": False,
    "include_files": [(numpy_dir, "lib/numpy"), icon_path, logo_path],
}

base = "Win32GUI" if sys.platform == "win32" else None

executables = [
    Executable(
        script=run_script,
        base=base,
        target_name=exe_name,
        icon=icon_path,
    )
]

# Build
setup(
    name=product_name,
    version="1",
    description="Ansys Antenna Toolkit",
    options={"build_exe": build_options},
    executables=executables,
)
