import os
import re

try:
    THIS_PATH = os.path.dirname(__file__)
except NameError:
    THIS_PATH = os.getcwd()

with open("src/ansys/aedt/toolkits/antenna/__init__.py", "r") as f:
    content = f.read()

match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
if match:
    with open(os.path.join(THIS_PATH, "VERSION"), "w") as v:
        v.write(match.group(1))
