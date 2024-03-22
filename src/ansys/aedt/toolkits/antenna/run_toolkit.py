# Copyright (C) 2023 - 2024 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
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

import atexit
import os
import socket
import subprocess
import sys
import threading
import time

import psutil
import requests

from ansys.aedt.toolkits.antenna import backend
from ansys.aedt.toolkits.antenna import ui
from ansys.aedt.toolkits.antenna.ui.common.properties import general_settings

# Define global variables or constants
BACKEND_FILE = os.path.join(backend.__path__[0], "rest_api.py")
FRONTEND_FILE = os.path.join(ui.__path__[0], "frontend_actions.py")
IS_LINUX = os.name == "posix"
URL = general_settings.backend_url
PORT = general_settings.backend_port
PYTHON_PATH = sys.executable
KILL_BACKEND = True
BACKEND_COMMAND = [PYTHON_PATH, BACKEND_FILE]
FRONTEND_COMMAND = [PYTHON_PATH, FRONTEND_FILE]
URL_CALL = f"http://{URL}:{PORT}"


# Global functions
def run_command(*command):
    create_no_window = 0x08000000 if not IS_LINUX else 0
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
    if KILL_BACKEND:
        for conn in psutil.net_connections():
            (ip, port) = conn.laddr
            pid = conn.pid
            if ip == URL and port == PORT and pid and pid != 0:
                process = psutil.Process(pid)
                print(f"Killing process {process.pid} on {ip}:{port}")
                process.terminate()


def check_backend_communication():
    response = requests.get(URL_CALL + "/health")
    if response.ok:
        return True
    return False


def process_desktop_properties():
    desktop_pid = None
    desktop_version = None
    grpc = False
    if "PYAEDT_SCRIPT_VERSION" in os.environ and (
        "PYAEDT_SCRIPT_PROCESS_ID" in os.environ or "PYAEDT_SCRIPT_PORT" in os.environ
    ):
        desktop_version = os.environ["PYAEDT_SCRIPT_VERSION"]
        desktop_pid = os.environ[
            "PYAEDT_SCRIPT_PORT" if desktop_version > "2023.2" or IS_LINUX else "PYAEDT_SCRIPT_PROCESS_ID"
        ]
        grpc = desktop_version > "2023.2" or IS_LINUX

    elif len(sys.argv) == 3:
        desktop_pid, desktop_version = sys.argv[1], sys.argv[2]

    if desktop_pid and desktop_version:
        properties = {
            "selected_process": int(desktop_pid),
            "aedt_version": desktop_version,
            "use_grpc": grpc,
        }
        requests.put(URL_CALL + "/set_properties", json=properties)
        # requests.post(URL_CALL + "/launch_aedt")


# Main Execution

# Clean python process when script ends
atexit.register(clean_python_processes)

# Check if backend is already running
is_server_busy = is_server_running(server=URL, port=PORT)
if is_server_busy:
    KILL_BACKEND = False
    raise Exception("There is a process running in: {}".format(URL_CALL))

# Launch backend thread
backend_thread = server_actions(BACKEND_COMMAND, "template_backend")

# Connect to AEDT session if arguments or environment variables are passed
process_desktop_properties()

# Launch frontend thread
frontend_thread = server_actions(FRONTEND_COMMAND, "template_frontend")

# Check if backend is running. Try every 1 second with a timeout of 10 seconds
is_server_running = wait_for_server(server=URL, port=PORT)
if not is_server_running:
    raise Exception("There is a process running in: {}".format(URL_CALL))

# Make a first call to the backend to check the communication
backend_communication_flag = check_backend_communication()
if not backend_communication_flag:
    raise Exception("Backend communication is not working.")

# Keep frontend thread alive until it is closed
frontend_thread.join()
