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
import multiprocessing
import os
import sys

from PySide6.QtCore import QTimer
from PySide6.QtWidgets import QApplication
from ansys.aedt.toolkits.common.utils import check_backend_communication
from ansys.aedt.toolkits.common.utils import clean_python_processes
from ansys.aedt.toolkits.common.utils import find_free_port
from ansys.aedt.toolkits.common.utils import is_server_running
from ansys.aedt.toolkits.common.utils import process_desktop_properties

backend = None
ui = None

from ansys.aedt.toolkits.antenna.backend.models import properties as backend_properties
from ansys.aedt.toolkits.antenna.ui.models import properties as frontend_properties


def start_backend(pp):
    """Start the backend process."""
    from ansys.aedt.toolkits.antenna.backend.run_backend import run_backend

    print(f"Starting backend on port {pp}...")
    run_backend(pp)


def show_splash_and_start_frontend(qt_app, url_backend):
    from ansys.aedt.toolkits.antenna.ui.run_frontend import run_frontend
    from ansys.aedt.toolkits.antenna.ui.splash import show_splash_screen

    splash = show_splash_screen(qt_app)  # Should return the splash widget

    def check_backend():
        if check_backend_communication(url_backend):
            splash.close()
            run_frontend(url, port, qt_app)
        else:
            QTimer.singleShot(500, check_backend)  # Check again in 0.5s

    check_backend()


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
    splash_thread = None

    def terminate_processes():
        print("Terminating backend and frontend processes...")
        backend_process.terminate()
        backend_process.join()
        print("Processes terminated.")

    # Clean python processes when script ends
    atexit.register(clean_python_processes, url, port)

    # Check if backend is already running
    if is_server_running(server=url, port=port):
        raise Exception(f"A process is already running at: {url_call}")

    # Launch backend process
    backend_process = multiprocessing.Process(target=start_backend, args=(new_port,))
    backend_process.start()

    # Connect to AEDT session if necessary
    process_desktop_properties(is_linux, url_call)

    app = QApplication(sys.argv)
    show_splash_and_start_frontend(app, url_call)
    app.aboutToQuit.connect(terminate_processes)
    sys.exit(app.exec())
