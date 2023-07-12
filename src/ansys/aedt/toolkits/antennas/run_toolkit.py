import atexit
import json
import os
import signal
import sys
import threading
import time

import psutil
import requests

from ansys.aedt.toolkits.antennas import backend
from ansys.aedt.toolkits.antennas import ui

with open(os.path.join(os.path.dirname(__file__), "ui", "common", "general_properties.json")) as fh:
    general_settings = json.load(fh)

url = general_settings["backend_url"]
port = general_settings["backend_port"]
url_call = "http://" + url + ":" + str(port)

is_linux = os.name == "posix"

import subprocess

# Path to Python interpreter with Flask and Pyside6 installed
python_path = sys.executable

# Define the command to start the Flask application
backend_file = os.path.join(backend.__path__[0], "rest_api.py")
backend_command = [python_path, backend_file]


# Define the command to start the PySide6 UI
frontend_file = os.path.join(ui.__path__[0], "frontend_actions.py")
frontend_command = [python_path, frontend_file]


# Clean up python processes
def clean_python_processes():
    # Terminate backend processes
    if is_linux:
        for process in flask_pids:
            os.kill(process, signal.SIGKILL)
    else:
        for process in flask_pids:
            if process.name() == "python.exe" or process.name() == "python":
                process.terminate()


# Define a function to run the subprocess command
def run_command(*command):
    myenv = os.environ.copy()
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
            env=myenv,
        )
    stdout, stderr = process.communicate()
    print(stdout.decode())
    print(stderr.decode())


# Take initial running processes
if is_linux:
    initial_pids = psutil.pids()
else:
    initial_pids = psutil.Process().children(recursive=True)

# Create a thread to run the Flask application
flask_process = None
flask_thread = threading.Thread(target=run_command, args=backend_command, name="backend")
flask_thread.daemon = True
flask_thread.start()
time.sleep(1)

# Wait until flask processes are running
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

# Take backend running processes
if is_linux:
    flask_pids = [element for element in psutil.pids() if element not in initial_pids]
else:
    flask_pids = [element for element in psutil.Process().children(recursive=True) if element not in initial_pids]


# Check if the backend is running
response = requests.get(url_call + "/get_status")
while response.json() != "Backend free":
    time.sleep(1)
    response = requests.get(url_call + "/get_status")

# User can pass the desktop ID and version to connect to a specific AEDT session
if len(sys.argv) == 3:
    desktop_pid = sys.argv[1]
    desktop_version = sys.argv[2]
    properties = {
        "selected_process": int(desktop_pid),
        "aedt_version": desktop_version,
        "use_grpc": False,
    }
    requests.put(url_call + "/set_properties", json=properties)
    requests.post(url_call + "/launch_aedt")

    response = requests.get(url_call + "/get_status")
    while response.json() != "Backend free":
        time.sleep(1)
        response = requests.get(url_call + "/get_status")

# Create a thread to run the PySide6 UI
ui_thread = threading.Thread(target=run_command, args=frontend_command, name="frontend")
ui_thread.start()

# Wait for the UI thread to complete
ui_thread.join()

# When the script closes, it terminates all flask processes
atexit.register(clean_python_processes)
