# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2026 ANSYS, Inc. and/or its affiliates.
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

from ansys.aedt.toolkits.common.utils import clean_python_processes
from ansys.aedt.toolkits.common.utils import find_free_port
from ansys.aedt.toolkits.common.utils import is_server_running
from ansys.aedt.toolkits.common.utils import process_desktop_properties


def start_backend(pp):
    """Start the backend process."""
    from ansys.aedt.toolkits.antenna.backend.run_backend import run_backend

    print(f"Starting backend on port {pp}...")
    run_backend(pp)


def _hide_console_window() -> None:
    """Hide the console window for frozen Windows GUI launches."""
    if os.name != "nt" or not getattr(sys, "frozen", False):
        return

    try:
        import ctypes

        hwnd = ctypes.windll.kernel32.GetConsoleWindow()
        if hwnd:
            ctypes.windll.user32.ShowWindow(hwnd, 0)
    except Exception:
        pass


def _should_run_cli(argv: list[str]) -> bool:
    """Return ``True`` when the packaged launcher should behave as the CLI."""
    if not argv:
        return False

    return argv[0] not in {"gui", "--gui"}


def run_cli(argv: list[str] | None = None) -> int:
    """Delegate execution to the standalone antenna CLI."""
    cli_args = list(sys.argv[1:] if argv is None else argv)
    cli = importlib.import_module("ansys.aedt.toolkits.antenna.cli")
    original_argv = sys.argv[:]
    sys.argv = [sys.argv[0], *cli_args]
    try:
        try:
            cli.main()
        except SystemExit as exc:
            return exc.code if isinstance(exc.code, int) else 0
    finally:
        sys.argv = original_argv
    return 0


def show_splash_and_start_frontend(qt_app, url_backend, url, port):
    """Wait for the backend to be ready and then open the frontend."""
    from ansys.aedt.toolkits.common.utils import check_backend_communication
    from PySide6.QtCore import QTimer

    from ansys.aedt.toolkits.antenna.ui.splash import show_splash_screen

    splash = show_splash_screen(qt_app)  # Should return the splash widget

    def check_backend():
        if check_backend_communication(url_backend):
            # Import here to avoid circular imports and speed up initial loading
            from ansys.aedt.toolkits.antenna.ui.run_frontend import run_frontend

            splash.close()
            run_frontend(url, port, qt_app)
        else:  # pragma: no cover
            # Check again in 0.5s
            QTimer.singleShot(500, check_backend)

    check_backend()


def terminate_processes(backend_process):
    """Terminate the spawned backend process on exit."""
    print("Terminating backend and frontend processes...")
    backend_process.terminate()
    backend_process.join()
    print("Processes are terminated.")


def run_gui() -> int:
    """Start the Antenna Toolkit GUI application."""
    from PySide6.QtWidgets import QApplication

    from ansys.aedt.toolkits.antenna.backend.models import properties as backend_properties
    from ansys.aedt.toolkits.antenna.ui.models import properties as frontend_properties

    _hide_console_window()

    is_linux = os.name == "posix"
    new_port = find_free_port(backend_properties.url, backend_properties.port)
    if not new_port:
        raise Exception(f"No free ports available in {backend_properties.url}.")

    backend_properties.port = new_port
    frontend_properties.backend_port = new_port
    url = frontend_properties.backend_url
    port = frontend_properties.backend_port
    url_call = f"http://{url}:{port}"

    # Clean Python processes when script ends
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
    show_splash_and_start_frontend(app, url_call, url, port)
    app.aboutToQuit.connect(lambda: terminate_processes(backend_process))
    return app.exec()


def main(argv: list[str] | None = None) -> int:
    """Run either the packaged CLI or the GUI launcher depending on arguments."""
    multiprocessing.freeze_support()
    entry_args = list(sys.argv[1:] if argv is None else argv)
    if _should_run_cli(entry_args):
        return run_cli(entry_args)
    return run_gui()


if __name__ == "__main__":  # pragma: no cover
    sys.exit(main())
