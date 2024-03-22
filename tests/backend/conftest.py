"""
REST API Test Configuration Module
----------------------------------

Description
===========
This module contains the configuration and fixture for the pytest-based tests for the REST API.

The default configuration can be changed by placing a file called local_config.json in the same
directory as this module. An example of the contents of local_config.json
{
  "desktop_version": "2024.1",
  "non_graphical": false,
  "use_grpc": true
}

You can enable the API log file in the backend_properties.json.

"""

import json
import logging
from logging import Logger
import os
import pathlib
import shutil
from typing import Optional

from pyaedt import settings
import pytest

DEFAULT_CONFIG = {
    "desktop_version": "2024.1",
    "non_graphical": True,
    "use_grpc": True,
    "debug": False
}
LOCAL_CFG_FILE = "local_config.json"
PROJECT_NAME = "Test"


def read_local_config() -> dict:
    """Read local configuration from JSON file.
    
    Returns
    -------
    Dict
        Empty dictionary if no local JSON file is found, else the file content.
    """
    res = {}
    local_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), LOCAL_CFG_FILE)
    if os.path.exists(local_path):
        with open(local_path) as f:
            local_config = json.load(f)
        res.update(local_config)
    return res


def setup_aedt_settings(config: Optional[dict] = None):
    """Set up AEDT settings.
    
    If no configuration is provided, use default configuration.
    """
    # Common expected behavior
    settings.enable_error_handler = False
    settings.enable_desktop_logs = False

    # Customizable behavior through config
    if config is None:
        settings.use_grpc_api = DEFAULT_CONFIG["use_grpc"]
        settings.non_graphical = DEFAULT_CONFIG["non_graphical"]
    else:
        settings.use_grpc_api = config["use_grpc"]
        settings.non_graphical = config["non_graphical"]


failed_tests = set()


def pytest_runtest_makereport(item, call):
    if call.excinfo is not None and call.excinfo.typename == "AssertionError":
        failed_tests.add(item)


@pytest.fixture(scope="session")
def common_temp_dir(tmp_path_factory, request):
    tmp_dir = tmp_path_factory.mktemp("test_common", numbered=True)
    src_folder = os.path.join(pathlib.Path(__file__).parent.parent, "input_data")
    shutil.copytree(src_folder, os.path.join(tmp_dir, "input_data"))

    def remove_temp_dir_finalizer():
        """Remove temporary directory when no test failed."""
        if request.session.testsfailed == 0:
            shutil.rmtree(str(tmp_dir), ignore_errors=True)

    request.addfinalizer(remove_temp_dir_finalizer)

    yield tmp_dir


@pytest.fixture(scope="session", autouse=True)
def logger(request, common_temp_dir) -> Logger:
    """Logger fixture."""

    logger = logging.getLogger(__name__)
    logger.setLevel(logging.DEBUG)
    formatter = logging.Formatter("%(levelname)s - %(message)s")

    # Create a file handler
    log_file = common_temp_dir.joinpath("pytest_run.log")
    file_handler = logging.FileHandler(log_file)
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    def log_finalizer():
        """Log failed tests if any."""
        logger.info("Test Teardown")
        if request.session.testsfailed != 0:
            for failed_test in failed_tests:
                logger.error(f"FAILED: {failed_test.nodeid}")
        for handler in logger.handlers[:]:
            handler.close()
            logger.removeHandler(handler)

    request.addfinalizer(log_finalizer)

    # Create a stream handler for logging to the console
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    return logger
