import logging
import os

from PySide6 import QtCore
import requests

logger = logging.getLogger("Global")


class FrontendThread(QtCore.QThread):
    status_changed = QtCore.Signal(bool)
    running = True

    def __int__(self):
        pass

    def run(self):
        while self.running:
            response = requests.get(self.url + "/get_status")
            if response.ok and response.json() != "Backend running":
                self.running = False
                properties = self.get_properties()
                if properties["active_project"] and "project_aedt_combo" in self.__dir__():
                    self.project_aedt_combo.clear()
                    if not properties["project_list"]:
                        self.project_aedt_combo.addItem("No project")
                    else:
                        cont = 0
                        for project in properties["project_list"]:
                            active_project_name = os.path.splitext(os.path.basename(project))[0]
                            self.project_aedt_combo.addItem(active_project_name)
                            if active_project_name == os.path.splitext(os.path.basename(project))[0]:
                                self.project_aedt_combo.setCurrentIndex(cont)
                            cont += 1

                if properties["active_design"] and "design_aedt_combo" in self.__dir__():
                    self.design_aedt_combo.clear()
                    if not properties["design_list"]:
                        self.design_aedt_combo.addItem("No design")
                    else:
                        cont = 0
                        design_name = properties["active_design"]
                        active_design_list = properties["design_list"][active_project_name]
                        for design in active_design_list:
                            self.design_aedt_combo.addItem(list(design.values())[0])
                            if list(design_name.values())[0] == design:
                                self.design_aedt_combo.setCurrentIndex(cont)
                            cont += 1

                # Emit the status_changed signal if the status changes
                self.status_changed.emit(self.running)

            # Sleep for a certain amount of time before checking again
            self.msleep(200)
