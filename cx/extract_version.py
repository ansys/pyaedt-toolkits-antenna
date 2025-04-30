import re

with open("src/ansys/aedt/toolkits/antenna/__init__.py", "r") as f:
    content = f.read()

match = re.search(r'__version__\s*=\s*["\']([^"\']+)["\']', content)
if match:
    with open("VERSION", "w") as v:
        v.write(match.group(1))
