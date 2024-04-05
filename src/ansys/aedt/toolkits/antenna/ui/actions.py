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

from ansys.aedt.toolkits.common.ui.actions_generic import FrontendGeneric
from ansys.aedt.toolkits.common.ui.logger_handler import logger
from pyaedt.generic.general_methods import generate_unique_project_name
import requests


class Frontend(FrontendGeneric):
    def __init__(self):
        FrontendGeneric.__init__(self)

    def create_geometry_toolkit(self, project_selected=None, design_selected=None):
        # Set active project and design
        be_properties = self.get_properties()
        if project_selected and design_selected:
            if project_selected == "No Project":
                project_selected = generate_unique_project_name()
                project_selected = self.get_project_name(project_selected)
                be_properties["active_project"] = project_selected

            for project in be_properties["project_list"]:
                if self.get_project_name(project) == project_selected:
                    be_properties["active_project"] = project
                    if project_selected in list(be_properties["design_list"].keys()):
                        designs = be_properties["design_list"][project_selected]
                        for design in designs:
                            if design_selected == design:
                                be_properties["active_design"] = design
                                break
                    break
        else:
            project_selected = generate_unique_project_name()
            project_selected = self.get_project_name(project_selected)
            be_properties["active_project"] = project_selected

        self.set_properties(be_properties)

        response = requests.post(self.url + "/create_geometry")

        self.properties.example.primitives_created.append(response.text)

        if response.ok:
            msg = "Geometry created."
            logger.info(msg)
            return True
        else:
            msg = f"Failed backend call: {self.url}"
            logger.error(msg)
            return False
