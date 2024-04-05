import atexit
import os
import sys

from ansys.aedt.toolkits.common.backend.rest_api import logger
import ansys.aedt.toolkits.common.utils
from ansys.aedt.toolkits.common.utils import check_backend_communication
from ansys.aedt.toolkits.common.utils import clean_python_processes
from ansys.aedt.toolkits.common.utils import find_free_port
from ansys.aedt.toolkits.common.utils import is_server_running
from ansys.aedt.toolkits.common.utils import process_desktop_properties
from ansys.aedt.toolkits.common.utils import server_actions
from ansys.aedt.toolkits.common.utils import wait_for_server
import ui
from ui.models import properties as frontend_properties

import backend
from backend.models import properties as backend_properties

# Define global variables or constants
backend_file = os.path.join(backend.__path__[0], "run_backend.py")
frontend_file = os.path.join(ui.__path__[0], "run_frontend.py")

is_linux = os.name == "posix"
new_port = find_free_port(backend_properties.url, backend_properties.port)
if not new_port:
    raise Exception("No free ports in {}".format(backend_properties.url))

frontend_properties.backend_port = new_port
url = frontend_properties.backend_url
port = frontend_properties.backend_port
python_path = sys.executable
backend_command = [python_path, backend_file, url, str(port)]
frontend_command = [python_path, frontend_file, url, str(port)]
url_call = f"http://{url}:{port}"

# Main Execution

# Clean python process when script ends
atexit.register(clean_python_processes, url, port)

# Check if backend is already running
is_server_busy = is_server_running(server=url, port=port)
if is_server_busy:
    raise Exception("There is a process running in: {}".format(url_call))

# Launch backend thread
backend_thread = server_actions(backend_command, "template_backend", is_linux)

# Connect to AEDT session if arguments or environment variables are passed
process_desktop_properties(is_linux, url_call)

# Launch frontend thread
frontend_thread = server_actions(frontend_command, "template_frontend", is_linux)

# Check if backend is running. Try every 1 second with a timeout of 10 seconds
backend_flag = wait_for_server(server=url, port=port)
if not backend_flag:
    raise Exception("There is a process running in: {}".format(url_call))

# Make a first call to the backend to check the communication
backend_communication_flag = check_backend_communication(url_call)
if not backend_communication_flag:
    raise Exception("Backend communication is not working.")

# Keep frontend thread alive until it is closed
frontend_thread.join()
