import logging
import sys
import time

from PySide6 import QtCore
import psutil
from pyaedt import Hfss
from pyaedt import settings

logger = logging.getLogger("Global")
line_colors = ["g", "b", "r", "y", "w"]


class RunnerSignals(QtCore.QObject):
    progressed = QtCore.Signal(int)
    messaged = QtCore.Signal(str)
    completed = QtCore.Signal()


class RunnerHfss(QtCore.QRunnable):
    def __init__(self):
        super(RunnerHfss, self).__init__()
        self.signals = RunnerSignals()
        self.hfss_args = {
            "non_graphical": False,
            "version": "2023.2",
            "selected_process": "Create New Session",
            "projectname": None,
            "process_id_combo_splitted": [],
        }

    def run(self):
        self.signals.progressed.emit(int(25))
        self.signals.messaged.emit(str(25))
        selected_process = self.hfss_args["selected_process"]
        projectname = self.hfss_args["projectname"]
        version = self.hfss_args["version"]
        non_graphical = self.hfss_args["non_graphical"]
        process_id_combo_splitted = self.hfss_args["process_id_combo_splitted"]
        self.signals.progressed.emit(int(50))
        if selected_process == "Create New Session":
            settings.use_grpc_api = True
            self.hfss = Hfss(
                projectname=projectname,
                specified_version=version,
                non_graphical=non_graphical,
                new_desktop_session=True,
            )
        elif len(process_id_combo_splitted) == 5:
            settings.use_grpc_api = True
            self.hfss = Hfss(
                projectname=projectname,
                specified_version=version,
                non_graphical=non_graphical,
                port=int(process_id_combo_splitted[-1]),
            )
        else:
            settings.use_grpc_api = False
            self.hfss = Hfss(
                projectname=projectname,
                specified_version=version,
                non_graphical=non_graphical,
                aedt_process_id=int(process_id_combo_splitted[1]),
            )
        if "non_graphical" in self.hfss_args:
            if not settings.use_grpc_api:
                self.pid = self.hfss.odesktop.GetProcessID()
                self.projectname = self.hfss.project_name
                self.designname = self.hfss.design_name
                self.hfss.release_desktop(False, False)
            else:
                self.pid = -1
        time.sleep(5)
        self.signals.completed.emit()


class RunnerAnalsysis(QtCore.QRunnable):
    def __init__(self):
        super(RunnerAnalsysis, self).__init__()
        self.signals = RunnerSignals()
        self.logger_file = ""
        self.lines = []

    def run(self):
        finished = False
        while not finished:
            with open(self.logger_file, "r") as f:
                lines = f.readlines()
                if len(lines) > len(self.lines):
                    for line in lines[len(self.lines) :]:
                        line_str = line.strip()
                        if line_str:
                            self.signals.messaged.emit(line.strip())
                            if "Stopping Batch Run" in line:
                                finished = True
                                self.signals.completed.emit()
                    self.lines.extend(lines[len(self.lines) :])
                time.sleep(3)


class QtHandler(logging.Handler):
    def __init__(self):
        logging.Handler.__init__(self)

    def emit(self, record):
        record = self.format(record)
        XStream.stdout().write("{}\n".format(record))


handler = QtHandler()


def active_sessions(version=None):
    """Get information for the active COM AEDT sessions.

    Parameters
    ----------
    version : str, optional
        Version to check. The default is ``None``, in which case all versions are checked.
        When specifying a version, you can use a three-digit format like ``"222"`` or a
        five-digit format like ``"2022.2"``.


    Returns
    -------
    list
        List of AEDT PIDs.
    """
    keys = ["ansysedt.exe"]
    if version and "." in version:
        version = version[-4:].replace(".", "")
    if version < "222":
        version = version[:2] + "." + version[2]
    sessions = []
    for p in psutil.process_iter():
        try:
            if p.name() in keys:
                cmd = p.cmdline()
                if not version or (version and version in cmd[0]):
                    if "-grpcsrv" in cmd:
                        if not version or (version and version in cmd[0]):
                            try:
                                sessions.append(
                                    [
                                        p.pid,
                                        int(cmd[cmd.index("-grpcsrv") + 1]),
                                    ]
                                )
                            except IndexError:
                                sessions.append(
                                    [
                                        p.pid,
                                        -1,
                                    ]
                                )
                    else:
                        sessions.append(
                            [
                                p.pid,
                                -1,
                            ]
                        )
        except:
            pass
    return sessions


class XStream(QtCore.QObject):
    _stdout = None
    _stderr = None

    messageWritten = QtCore.Signal(str)

    def flush(self):
        pass

    def fileno(self):
        return -1

    def write(self, msg):
        if not self.signalsBlocked():
            self.messageWritten.emit(msg)

    @staticmethod
    def stdout():
        if not XStream._stdout:
            XStream._stdout = XStream()
            sys.stdout = XStream._stdout
        return XStream._stdout

    @staticmethod
    def stderr():
        if not XStream._stderr:
            XStream._stderr = XStream()
            sys.stderr = XStream._stderr
        return XStream._stderr
