import os
import shutil
import sys
import time

from PySide6 import QtCore
from PySide6 import QtGui
from PySide6 import QtWidgets
import qdarkstyle
import requests

from ansys.aedt.toolkits.antenna.ui.common.frontend_ui import Ui_MainWindow
from ansys.aedt.toolkits.antenna.ui.common.logger_handler import logger
from ansys.aedt.toolkits.antenna.ui.common.properties import be_properties
from ansys.aedt.toolkits.antenna.ui.common.thread_manager import FrontendThread


class FrontendGeneric(QtWidgets.QMainWindow, Ui_MainWindow, FrontendThread):
    def __init__(self):
        logger.info("Frontend initialization...")
        super(FrontendGeneric, self).__init__()
        FrontendThread.__init__(self)

        self.setupUi(self)

        # Load toolkit icon
        self.images_path = os.path.join(os.path.dirname(__file__), "images")
        icon = self._load_icon(self.images_path)
        self.setWindowIcon(icon)

        # Set font style
        self.set_style(self)

        # Toolkit specific
        self.create_button = None

        # UI Logger
        XStream.stdout().messageWritten.connect(lambda value: self.write_log_line(value))
        XStream.stderr().messageWritten.connect(lambda value: self.write_log_line(value))

    def set_title(self, toolkit_title):
        # Toolkit name
        self.setWindowTitle(toolkit_title)
        return True

    def write_log_line(self, value):
        self.log_text.insertPlainText(value + "\n")
        tc = self.log_text.textCursor()
        tc.setPosition(self.log_text.document().characterCount())
        self.log_text.setTextCursor(tc)

    def update_progress(self, value):
        if 0 < value < 100:
            self.progress_bar.setStyleSheet(
                """
                QProgressBar {
                    background-color: transparent;  /* Set the background color */
                    color: #FFFFFF;  /* Set the text color */
                }
                QProgressBar::chunk {
                    background-color: #FF0000;  /* Set the progress color */
                }
            """
            )
        elif value == 100:
            self.progress_bar.setStyleSheet(
                """
                QProgressBar {
                    background-color: transparent;  /* Set the background color */
                    color: #FFFFFF;  /* Set the text color */
                 }
                QProgressBar::chunk {
                    background-color: #008000;  /* Set the progress color */
                }
                """
            )

        self.progress_bar.setValue(value)

        if self.progress_bar.isHidden():
            self.progress_bar.setVisible(True)

    def check_connection(self):
        try:
            logger.debug("Check backend connection")
            count = 0
            response = False
            while not response and count < 10:
                time.sleep(1)
                response = requests.get(self.url + "/health")
                count += 1

            if response.ok:
                logger.debug(response.json())
                return True
            logger.error(response.json())
            return False

        except requests.exceptions.RequestException as e:
            logger.error("Backend not running")
            return False

    def is_backend_busy(self):
        response = requests.get(self.url + "/get_status")
        if response.ok and response.json() == "Backend running":
            return True
        else:
            return False

    def installed_versions(self):
        try:
            response = requests.get(self.url + "/installed_versions")
            if response.ok:
                versions = response.json()
                return versions
        except requests.exceptions.RequestException:
            self.write_log_line("Get AEDT installed versions failed")
            return False

    def get_properties(self):
        try:
            response = requests.get(self.url + "/get_properties")
            if response.ok:
                data = response.json()
                logger.debug("Updating the properties from backend.")
                if data:
                    for key in data:
                        setattr(be_properties, key, data[key])
                    logger.debug("Properties from backend updated successfully.")
                    return True
                else:
                    logger.debug("body is empty!")
                    return False
        except requests.exceptions.RequestException:
            self.write_log_line("Get properties failed")

    def set_properties(self):
        try:
            response = requests.put(self.url + "/set_properties", json=be_properties.export_to_dict())
            if response.ok:
                response.json()
        except requests.exceptions.RequestException:
            self.write_log_line(f"Set properties failed")

    def change_thread_status(self):
        self.find_process_ids()
        logger.info("Frontend thread finished")
        self.update_progress(100)

    def browse_for_project(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        dialog.setOption(QtWidgets.QFileDialog.Option.DontConfirmOverwrite, True)
        dialog.setAcceptMode(QtWidgets.QFileDialog.AcceptSave)
        fileName, _ = dialog.getOpenFileName(
            self,
            "Open or create new aedt file",
            "",
            "Aedt Files (*.aedt)",
        )
        if fileName:
            self.project_name.setText(fileName)
            self.get_properties()
            be_properties.active_project = fileName
            self.set_properties()

    def find_process_ids(self):
        self.process_id_combo.clear()
        self.process_id_combo.addItem("Create New Session")
        try:
            # Modify selected version
            self.get_properties()
            if self.aedt_version_combo.currentText():
                be_properties.aedt_version = self.aedt_version_combo.currentText()
            self.set_properties()

            response = requests.get(self.url + "/aedt_sessions")
            if response.ok:
                sessions = response.json()
                for session in sessions:
                    if session[1] == -1:
                        self.process_id_combo.addItem("Process {}".format(session[0], session[1]))
                    else:
                        self.process_id_combo.addItem("Process {} on Grpc {}".format(session[0], session[1]))
            return True
        except requests.exceptions.RequestException:
            self.write_log_line(f"Find AEDT sessions failed")
            return False

    def find_design_names(self):
        response = requests.get(self.url + "/get_status")

        if response.ok and response.json() == "Backend running":
            self.write_log_line("Please wait, toolkit running")
        elif response.ok and response.json() == "Backend free":
            self.design_aedt_combo.clear()
            try:
                # Modify selected version
                self.get_properties()
                project_selected = self.project_aedt_combo.currentText()
                for project in be_properties.project_list:
                    if project_selected == os.path.basename(project)[:-5]:
                        be_properties.active_project = project

                response = requests.get(self.url + "/get_design_names")
                if response.ok:
                    designs = response.json()
                    for design in designs:
                        self.design_aedt_combo.addItem(list(design.values())[0])
                    if not designs:
                        self.design_aedt_combo.addItem("No design")

                return True
            except requests.exceptions.RequestException:
                self.write_log_line(f"Find AEDT designs failed")
                return False

    def launch_aedt(self):
        response = requests.get(self.url + "/get_status")

        if response.ok and response.json() == "Backend running":
            self.write_log_line("Please wait, toolkit running")
        elif response.ok and response.json() == "Backend free":
            self.update_progress(0)
            response = requests.get(self.url + "/health")
            if response.ok and response.json() == "Toolkit not connected to AEDT":
                self.get_properties()
                if be_properties.selected_process == 0:
                    be_properties.aedt_version = self.aedt_version_combo.currentText()
                    be_properties.non_graphical = True
                    if self.non_graphical_combo.currentText() == "False":
                        be_properties.non_graphical = False
                    if self.process_id_combo.currentText() == "Create New Session":
                        if not be_properties.active_project:
                            be_properties.selected_process = 0
                    else:
                        text_splitted = self.process_id_combo.currentText().split(" ")
                        if len(text_splitted) == 5:
                            be_properties.use_grpc = True
                            be_properties.selected_process = int(text_splitted[4])
                        else:
                            be_properties.use_grpc = False
                            be_properties.selected_process = int(text_splitted[1])
                    self.set_properties()

                response = requests.post(self.url + "/launch_aedt")

                if response.status_code == 200:
                    self.update_progress(50)
                    msg = "AEDT launched"
                    logger.debug(msg)
                    self.write_log_line(msg)
                    # Start the thread
                    self.running = True
                    logger.debug("Launching AEDT")
                    self.start()
                    if self.create_button:
                        self.create_button.setEnabled(True)
                    self.toolkit_tab.removeTab(0)
                else:
                    self.write_log_line(f"Failed backend call: {self.url}")
                    self.update_progress(100)
            else:
                self.write_log_line(response.json())
                self.update_progress(100)
        else:
            self.write_log_line(response.json())
            self.update_progress(100)

    def save_project(self):
        dialog = QtWidgets.QFileDialog()
        dialog.setOption(QtWidgets.QFileDialog.DontUseNativeDialog, True)
        dialog.setFileMode(QtWidgets.QFileDialog.FileMode.AnyFile)
        dialog.setOption(QtWidgets.QFileDialog.Option.DontConfirmOverwrite, True)
        file_name, _ = dialog.getSaveFileName(
            self,
            "Save new aedt file",
            "",
            "Aedt Files (*.aedt)",
        )

        if file_name:
            response = requests.get(self.url + "/get_status")
            if response.ok and response.json() == "Backend running":
                self.write_log_line("Please wait, toolkit running")
            elif response.ok and response.json() == "Backend free":
                self.project_name.setText(file_name)
                self.get_properties()
                # be_properties.active_project = file_name
                # self.set_properties()
                self.update_progress(0)
                response = requests.post(self.url + "/save_project", json=file_name)
                if response.ok:
                    self.update_progress(50)
                    # Start the thread
                    self.running = True
                    logger.debug("Saving project: {}".format(file_name))
                    self.start()
                    self.write_log_line("Saving project process launched")
                else:
                    msg = f"Failed backend call: {self.url}"
                    logger.debug(msg)
                    self.write_log_line(msg)
                    self.update_progress(100)

    def release_only(self):
        """Release desktop."""
        response = requests.get(self.url + "/get_status")

        if response.ok and response.json() == "Backend running":
            self.write_log_line("Please wait, toolkit running")
        else:
            arguments = {"close_projects": False, "close_on_exit": False}
            if self.close():
                requests.post(self.url + "/close_aedt", json=arguments)
                if self.plotter:
                    self.plotter.app_window.close()
                    self.plotter.close()
                    self.plotter = None
                shutil.rmtree(self.temp_folder)

    def release_and_close(self):
        """Release and close desktop."""
        response = requests.get(self.url + "/get_status")

        if response.ok and response.json() == "Backend running":
            self.write_log_line("Please wait, toolkit running")
        elif response.ok and response.json() == "Backend free":
            properties = {"close_projects": True, "close_on_exit": True}
            if self.close():
                requests.post(self.url + "/close_aedt", json=properties)
                if self.plotter:
                    self.plotter.app_window.close()
                    self.plotter.close()
                    self.plotter = None
                shutil.rmtree(self.temp_folder)

    def on_cancel_clicked(self):
        self.close()
        if self.plotter:
            self.plotter.app_window.close()
            self.plotter.close()
            self.plotter = None
        shutil.rmtree(self.temp_folder)

    @staticmethod
    def set_style(ui_obj):
        ui_obj.setStyleSheet(qdarkstyle.load_stylesheet(qt_api="pyside6"))

    @staticmethod
    def _load_icon(images_path):
        icon = QtGui.QIcon()
        icon.addFile(
            os.path.join(images_path, "logo_cropped.png"),
            QtCore.QSize(),
            QtGui.QIcon.Normal,
            QtGui.QIcon.Off,
        )
        icon.addFile(
            os.path.join(images_path, "logo_cropped.png"),
            QtCore.QSize(),
            QtGui.QIcon.Normal,
            QtGui.QIcon.On,
        )
        return icon


class XStream(QtCore.QObject):
    """User interface message streamer."""

    _stdout = None
    _stderr = None

    messageWritten = QtCore.Signal(str)

    def flush(self):
        """Pass."""
        pass

    def fileno(self):
        """File."""
        return -1

    def write(self, msg):
        """Write a message."""
        if not self.signalsBlocked():
            self.messageWritten.emit(msg)

    @staticmethod
    def stdout():
        """Info logger."""
        if not XStream._stdout:
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        """Error logger."""
        if not XStream._stderr:
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr
