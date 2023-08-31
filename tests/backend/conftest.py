import datetime
import gc
import json
import os
import shutil
import signal
import subprocess
import sys
import tempfile
import threading
import time

import psutil
from pyaedt import settings
from pyaedt.aedt_logger import pyaedt_logger
from pyaedt.generic.filesystem import Scratch
import pytest
import requests

settings.enable_error_handler = False
settings.enable_desktop_logs = False
local_path = os.path.dirname(os.path.realpath(__file__))
sys.path.append(local_path)

from ansys.aedt.toolkits.antenna import backend

is_linux = os.name == "posix"

# Initialize default configuration
config = {
    "aedt_version": "2023.1",
    "non_graphical": True,
    "use_grpc": True,
    "url": "127.0.0.1",
    "port": "5001",
}

# Check for the local config file, override defaults if found
local_config_file = os.path.join(local_path, "local_config.json")
if os.path.exists(local_config_file):
    with open(local_config_file) as f:
        local_config = json.load(f)
    config.update(local_config)

settings.use_grpc_api = config["use_grpc"]
settings.non_graphical = config["non_graphical"]

url = config["url"]
port = config["port"]
url_call = "http://" + url + ":" + str(port)

# Path to Python interpreter with Flask and Pyside6 installed
python_path = sys.executable

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
        self.test_config = config
        self.local_path = local_scratch
        self._main = sys.modules["__main__"]
        self.url = "http://" + url + ":" + str(port)

    def my_teardown(self):
        try:
            properties = {"close_projects": False, "close_on_exit": False}
            requests.post(url_call + "/close_aedt", json=properties)
        except Exception as e:
            pass

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
desktop_version = config["aedt_version"]
non_graphical = config["non_graphical"]
local_scratch = Scratch(scratch_path)

example_project = shutil.copy(
    os.path.join(local_path, "example_models", "Test.aedt"), os.path.join(local_scratch.path, "Test.aedt")
)


# Define a function to run the subprocess command
def run_command(*command):
    if is_linux:
        process = subprocess.Popen(
            command,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
        )
    else:
        CREATE_NO_WINDOW = 0x08000000
        process = subprocess.Popen(
            " ".join(command),
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            creationflags=CREATE_NO_WINDOW,
        )
    stdout, stderr = process.communicate()
    print(stdout.decode())
    print(stderr.decode())


@pytest.fixture(scope="session", autouse=True)
def desktop_init():
    if is_linux:
        initial_pids = psutil.pids()
    else:
        initial_pids = psutil.Process().children(recursive=True)

    # Define the command to start the Flask application
    backend_file = os.path.join(backend.__path__[0], "rest_api.py")
    backend_command = [python_path, backend_file]
    # Create a thread to run the Flask application
    flask_thread = threading.Thread(target=run_command, args=backend_command)
    flask_thread.daemon = True
    flask_thread.start()

    time.sleep(1)

    if is_linux:
        current_process = len(psutil.pids())
        count = 0
        while current_process < len(initial_pids) and count < 10:
            time.sleep(1)
            current_process = len(psutil.pids())
            count += 1
    else:
        current_process = len(psutil.Process().children(recursive=True))
        count = 0
        while current_process < len(initial_pids) and count < 10:
            time.sleep(1)
            current_process = len(psutil.Process().children(recursive=True))
            count += 1

    if current_process <= len(initial_pids):
        raise "Backend not running"

    if is_linux:
        flask_pids = [element for element in psutil.pids() if element not in initial_pids]
    else:
        flask_pids = [element for element in psutil.Process().children(recursive=True) if element not in initial_pids]

    # Wait for the Flask application to start
    response = requests.get(url_call + "/get_status")

    while response.json() != "Backend free":
        time.sleep(1)
        response = requests.get(url_call + "/get_status")

    properties = {
        "aedt_version": desktop_version,
        "non_graphical": non_graphical,
        "use_grpc": True,
        "active_project": example_project,
    }
    requests.put(url_call + "/set_properties", json=properties)
    requests.post(url_call + "/launch_aedt", json=properties)
    response = requests.get(url_call + "/get_status")
    while response.json() != "Backend free":
        time.sleep(1)
        response = requests.get(url_call + "/get_status")
    yield
    properties = {"close_projects": True, "close_on_exit": True}
    requests.post(url_call + "/close_aedt", json=properties)

    logger.remove_all_project_file_logger()
    shutil.rmtree(scratch_path, ignore_errors=True)

    # Register the cleanup function to be called on script exit
    gc.collect()

    if is_linux:
        pids = psutil.pids()
        for process in flask_pids:
            if process in pids:
                os.kill(process, signal.SIGKILL)
    else:
        for process in flask_pids:
            if (process.name() == "python.exe" or process.name() == "python") and process.pid in psutil.pids():
                process.terminate()
