# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
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
import importlib
import multiprocessing
import os
import sys
import time

from ansys.aedt.toolkits.common.utils import check_backend_communication
from ansys.aedt.toolkits.common.utils import clean_python_processes
from ansys.aedt.toolkits.common.utils import find_free_port
from ansys.aedt.toolkits.common.utils import is_server_running
from ansys.aedt.toolkits.common.utils import process_desktop_properties
from ansys.aedt.toolkits.common.utils import wait_for_server

backend = None
ui = None


def get_backend():
    global backend
    if backend is None:
        backend = importlib.import_module("ansys.aedt.toolkits.antenna.backend.run_backend")
    return backend


def get_ui():
    global ui
    if ui is None:
        ui = importlib.import_module("ansys.aedt.toolkits.antenna.ui.run_frontend")
    return ui


from ansys.aedt.toolkits.antenna.backend.models import properties as backend_properties
from ansys.aedt.toolkits.antenna.ui.models import properties as frontend_properties
from ansys.aedt.toolkits.antenna.ui.splash import show_splash_screen

# # Set environment variables
# os.environ["AEDT_TOOLKIT_HIGH_RESOLUTION"] = "False"
# os.environ["AEDT_TOOLKIT_THEME"] = "ansys_dark.json"


def start_backend(pp):
    """Start the backend process."""
    backend_imported = get_backend()

    print(f"Starting backend on port {pp}...")
    backend_imported.run_backend(pp)


def start_frontend(backend_url, backend_port):
    """Start the frontend process."""
    ui_imported = get_ui()
    print("Starting frontend...")
    ui_imported.run_frontend(backend_url, backend_port)


if __name__ == "__main__":
    multiprocessing.freeze_support()

    is_linux = os.name == "posix"
    new_port = find_free_port(backend_properties.url, backend_properties.port)
    if not new_port:
        raise Exception(f"No free ports available in {backend_properties.url}")

    backend_properties.port = new_port
    frontend_properties.backend_port = new_port
    url = frontend_properties.backend_url
    port = frontend_properties.backend_port
    url_call = f"http://{url}:{port}"
    python_path = sys.executable

    def terminate_processes():
        print("Terminating backend and frontend processes...")
        backend_process.terminate()
        frontend_process.terminate()
        backend_process.join()
        frontend_process.join()
        print("Processes terminated.")

    # Clean python processes when script ends
    atexit.register(clean_python_processes, url, port)

    # Check if backend is already running
    if is_server_running(server=url, port=port):
        raise Exception(f"A process is already running at: {url_call}")

    if not is_linux:
        # Launch splash
        splash_process = multiprocessing.Process(target=show_splash_screen)
        splash_process.start()

    # Launch backend process
    backend_process = multiprocessing.Process(target=start_backend, args=(new_port,))
    backend_process.start()

    # Wait for backend to start
    count = 0
    while not check_backend_communication(url_call) and count < 10:
        time.sleep(1)
        count += 1

    if not check_backend_communication(url_call):
        raise Exception("Backend communication is not working.")

    # Connect to AEDT session if necessary
    process_desktop_properties(is_linux, url_call)

    if not is_linux:
        splash_process.join()

    # Launch frontend process
    frontend_process = multiprocessing.Process(target=start_frontend, args=(url, port))
    frontend_process.start()

    # Wait for backend confirmation
    if not wait_for_server(server=url, port=port):
        raise Exception(f"Backend did not start properly at {url_call}")

    # Keep frontend running
    frontend_process.join()

    terminate_processes()
