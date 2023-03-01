"""
Unit Test Configuration Module
-------------------------------

Description
===========

This module contains the configuration and fixture for the pytest-based unit tests for pyaedt.

The default configuration can be changed by placing a file called local_config.json in the same
directory as this module. An example of the contents of local_config.json
{
  "desktopVersion": "2023.1",
  "NonGraphical": false,
  "NewThread": false,
  "test_desktops": true
}

"""
import datetime
import gc
import json
import os
import shutil
import sys
import tempfile

from pyaedt import pyaedt_logger
from pyaedt import settings

settings.enable_error_handler = False
settings.enable_desktop_logs = False

import pytest

local_path = os.path.dirname(os.path.realpath(__file__))

from pyaedt import Desktop
from pyaedt import Hfss
from pyaedt.generic.filesystem import Scratch

test_project_name = "test_antenna"

sys.path.append(local_path)
# from _unittest.launch_desktop_tests import run_desktop_tests

# Initialize default desktop configuration
default_version = "2023.1"

config = {
    "desktopVersion": default_version,
    "NonGraphical": True,
    "NewThread": True,
    "use_grpc": True,
}

# Check for the local config file, override defaults if found
local_config_file = os.path.join(local_path, "local_config.json")
if os.path.exists(local_config_file):
    with open(local_config_file) as f:
        local_config = json.load(f)
    config.update(local_config)

settings.use_grpc_api = config.get("use_grpc", True)
settings.non_graphical = config["NonGraphical"]

test_folder = "unit_test" + datetime.datetime.now().strftime("%Y%m%d-%H%M%S")
scratch_path = os.path.join(tempfile.gettempdir(), test_folder)
if not os.path.exists(scratch_path):
    try:
        os.makedirs(scratch_path)
    except:
        pass

logger = pyaedt_logger


class BasisTest(object):
    def my_setup(self):
        scratch_path = tempfile.gettempdir()
        self.local_scratch = Scratch(scratch_path)
        self.aedtapps = []
        self._main = sys.modules["__main__"]

    def my_teardown(self):
        if self.aedtapps:
            try:
                oDesktop = self._main.oDesktop
                proj_list = oDesktop.GetProjectList()
            except Exception as e:
                oDesktop = None
                proj_list = []
            if oDesktop and not settings.non_graphical:
                oDesktop.ClearMessages("", "", 3)
            for proj in proj_list:
                oDesktop.CloseProject(proj)
            del self.aedtapps

        logger.remove_all_project_file_logger()
        shutil.rmtree(self.local_scratch.path, ignore_errors=True)

    def add_app(
        self,
        project_name=None,
        design_name=None,
        solution_type=None,
        application=None,
        subfolder="",
    ):
        if "oDesktop" not in dir(self._main):
            self.desktop = Desktop(desktop_version, settings.non_graphical, new_thread)
            self.desktop.disable_autosave()
        if project_name:
            example_project = os.path.join(
                local_path, "example_models", subfolder, project_name + ".aedt"
            )
            example_folder = os.path.join(
                local_path, "example_models", subfolder, project_name + ".aedb"
            )
            if os.path.exists(example_project):
                self.test_project = self.local_scratch.copyfile(example_project)
            elif os.path.exists(example_project + "z"):
                example_project = example_project + "z"
                self.test_project = self.local_scratch.copyfile(example_project)
            else:
                self.test_project = os.path.join(self.local_scratch.path, project_name + ".aedt")
            if os.path.exists(example_folder):
                target_folder = os.path.join(self.local_scratch.path, project_name + ".aedb")
                self.local_scratch.copyfolder(example_folder, target_folder)
        else:
            self.test_project = None
        if not application:
            application = Hfss
        self.aedtapps.append(
            application(
                projectname=self.test_project,
                designname=design_name,
                solution_type=solution_type,
                specified_version=desktop_version,
            )
        )
        return self.aedtapps[-1]

    def teardown_method(self):
        """
        Could be redefined
        """
        pass

    def setup_method(self):
        """
        Could be redefined
        """
        pass


# Define desktopVersion explicitly since this is imported by other modules
desktop_version = config["desktopVersion"]
new_thread = config["NewThread"]


@pytest.fixture(scope="session", autouse=True)
def desktop_init():
    desktop = Desktop(desktop_version, settings.non_graphical, new_thread)
    yield
    desktop.release_desktop(True, True)
    del desktop
    gc.collect()
