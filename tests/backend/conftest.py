import datetime
import gc
import json
import os
import shutil
import socket
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

# Initialize default desktop configuration
default_version = "2023.2"

# Initialize default configuration
config = {
    "aedt_version": default_version,
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


# Global functions
def run_command(*command):
    create_no_window = 0x08000000 if not is_linux else 0
    process = subprocess.Popen(
        command,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        creationflags=create_no_window,
    )
    stdout, stderr = process.communicate()
    print(stdout.decode())


def server_actions(command, name):
    thread = threading.Thread(target=run_command, args=command, name=name)
    thread.daemon = True
    thread.start()
    return thread


def wait_for_server(server="localhost", port=5001, timeout=10.0):
    start_time = time.time()
    first_time = True
    result = None
    while time.time() - start_time < timeout:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            result = sock.connect_ex((server, port))
        except socket.error as e:
            print(f"Socket error occurred: {e}")
        finally:
            sock.close()
        if result == 0:
            print("\nServer is ready.")
            return True
        if first_time:
            print("Server not ready yet. Retrying...", end="")
            first_time = False
        else:
            print(".", end="")
        time.sleep(1)
    print("\nTimed out waiting for server.")
    return False


def is_server_running(server="localhost", port=5001):
    result = None
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    try:
        result = sock.connect_ex((server, port))
    except socket.error as e:
        print(f"Socket error occurred: {e}")
    finally:
        sock.close()
    if result == 0:
        return True
    return False


def clean_python_processes():
    for conn in psutil.net_connections():
        (ip, port_process) = conn.laddr
        pid = conn.pid
        if ip == url and int(float(port)) == int(float(port_process)) and pid and pid != 0:
            process = psutil.Process(pid)
            print(f"Killing process {process.pid} on {ip}:{port}")
            process.terminate()


def check_backend_communication():
    response = requests.get(url_call + "/health")
    if response.ok:
        return True
    return False


@pytest.fixture(scope="session", autouse=True)
def desktop_init():
    # Define the command to start the Flask application
    backend_file = os.path.join(backend.__path__[0], "rest_api.py")
    backend_command = [python_path, backend_file]

    # Check if backend is already running
    is_server_busy = is_server_running(server=url, port=int(float(port)))
    if is_server_busy:
        raise Exception("There is a process running in: {}".format(url_call))

    # Create a thread to run the Flask application
    flask_thread = threading.Thread(target=run_command, args=backend_command)
    flask_thread.daemon = True
    flask_thread.start()

    # Check if backend is running. Try every 1 second with a timeout of 10 seconds
    is_server_backend_running = wait_for_server(server=url, port=int(float(port)))
    if not is_server_backend_running:
        raise Exception("There is a process running in: {}".format(url_call))

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

    clean_python_processes()
