import base64
import os

import psutil
import pyaedt

from ansys.aedt.toolkits.antenna.backend.common.logger_handler import logger
from ansys.aedt.toolkits.antenna.backend.common.properties import properties
from ansys.aedt.toolkits.antenna.backend.common.thread_manager import ThreadManager

thread = ThreadManager()


class ToolkitGeneric(object):
    """Generic API to control the toolkits.

    It provides basic functions to control AEDT and properties to share between backend and frontend.

    Examples
    --------
    >>> import time
    >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
    >>> toolkit = Toolkit()
    >>> properties = toolkit.get_properties()
    >>> new_properties = {"aedt_version": "2022.2"}
    >>> toolkit.set_properties(new_properties)
    >>> new_properties = toolkit.get_properties()
    >>> msg = toolkit.launch_aedt()
    >>> response = toolkit.get_thread_status()
    >>> while response[0] == 0:
    >>>     time.sleep(1)
    >>>     response = toolkit.get_thread_status()

    """

    def __init__(self):
        self.desktop = None
        self.aedtapp = None
        self.aedt_apps = {
            "Circuit Design": "Circuit",
            "HFSS": "Hfss",
            "EMIT": "Emit",
            "HFSS 3D Layout Design": "Hfss3dLayout",
            "Icepak": "Icepak",
            "Maxwell 2D": "Maxwell2d",
            "Maxwell 3D": "Maxwell3d",
            "Maxwell Circuit": "MaxwellCircuit",
            "2D Extractor": "Q2d",
            "Q3D Extractor": "Q3d",
            "RMxprt": "Rmxprt",
            "Twin Builder": "Simplorer",
            "Mechanical": "Mechanical",
        }

    @staticmethod
    def set_properties(data):
        """Assign the passed data to the internal data model.

        Parameters
        ----------
        data : dict
            The dictionary containing the properties to be updated.

        Returns
        -------
        tuple[bool, str]
            A tuple indicating the success status and a message.

        Examples
        --------
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.set_properties({"property1": value1, "property2": value2})

        """

        logger.debug("Updating the internal properties.")
        if data:
            try:
                for key in data:
                    setattr(properties, key, data[key])
                msg = "properties updated successfully"
                logger.debug(msg)
                return True, msg
            except:
                return False, "Frozen property access"
        else:
            msg = "body is empty!"
            logger.debug(msg)
            return False, msg

    @staticmethod
    def get_properties():
        """Get toolkit properties.

        Returns
        -------
        dict
            Dictionary containing the toolkit properties.

        Examples
        --------
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.get_properties()
        {"property1": value1, "property2": value2}
        """
        return properties.export_to_dict()

    @staticmethod
    def get_thread_status():
        """Get toolkit thread status.

        Returns
        -------
        bool
            ``True`` when active, ``False`` when not active.

        Examples
        --------
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.get_thread_status()
        """
        thread_running = thread.is_thread_running()
        is_toolkit_busy = properties.is_toolkit_busy
        if thread_running and is_toolkit_busy:  # pragma: no cover
            msg = "Backend running"
            logger.debug(msg)
            return 0, msg
        elif (not thread_running and is_toolkit_busy) or (thread_running and not is_toolkit_busy):  # pragma: no cover
            msg = "Backend crashed"
            logger.error(msg)
            return 1, msg
        else:
            msg = "Backend free"
            logger.debug(msg)
            return -1, msg

    def aedt_connected(self):
        """Check if AEDT is connected.

        Returns
        -------
        tuple[bool, str]
            A tuple indicating the connection status and a message.

        Examples
        --------
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> msg = toolkit.launch_aedt()
        >>> response = toolkit.get_thread_status()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = toolkit.get_thread_status()
        >>> toolkit.connect_aedt()
        >>> toolkit.aedt_connected()
        (True, "Toolkit connected to process <process_id> on Grpc <grpc_port>")
        >>> toolkit.release_aedt()
        """
        if self.desktop:
            if self.desktop.port != 0:
                msg = "Toolkit connected to process {} on Grpc {}".format(
                    str(self.desktop.aedt_process_id),
                    str(self.desktop.port),
                )
                logger.debug(msg)
            else:
                msg = "Toolkit connected to process {}".format(str(self.desktop.aedt_process_id))
                logger.debug(msg)
            connected = True
        else:
            msg = "Toolkit not connected to AEDT"
            logger.debug(msg)
            connected = False
        return connected, msg

    @staticmethod
    def installed_aedt_version():
        """
        Get a list of installed AEDT versions.

        Returns
        -------
        list
            List of installed AEDT versions.

        Examples
        --------
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.installed_aedt_version()
        ["2021.1", "2021.2", "2022.1"]
        """

        # Detect existing AEDT installation
        installed_versions = []
        for ver in pyaedt.misc.list_installed_ansysem():
            installed_versions.append(
                "20{}.{}".format(ver.replace("ANSYSEM_ROOT", "")[:2], ver.replace("ANSYSEM_ROOT", "")[-1])
            )
        logger.debug(str(installed_versions))
        return installed_versions

    @staticmethod
    def aedt_sessions():
        """Get information for the active AEDT sessions.

        Returns
        -------
        list
            List of AEDT process IDs (PIDs).

        Examples
        --------
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.aedt_sessions()
        [[pid1, grpc_port1], [pid2, grpc_port2]]
        """
        if not properties.is_toolkit_busy:
            version = properties.aedt_version
            keys = ["ansysedt.exe"]
            if not version:
                return []
            if version and "." in version:
                version = version[-4:].replace(".", "")
            if version < "222":  # pragma: no cover
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
            logger.debug(str(sessions))
            return sessions
        else:
            logger.debug("No active sessions")
            return []

    @staticmethod
    def get_design_names():
        """Get design names for the active project.

        The first project is the active project.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> import time
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.launch_aedt()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = toolkit.get_thread_status()
        >>> toolkit.get_design_names()
        """
        if properties.selected_process == 0:
            logger.error("Process ID not defined")
            return False

        design_list = []
        active_project = os.path.splitext(os.path.basename(properties.active_project))[0]
        if active_project and active_project != "No project":
            for design in properties.design_list[active_project]:
                design_list.append(design)

            if properties.active_design and properties.active_design in design_list:
                index = design_list.index(properties.active_design)
                design_list.insert(0, design_list.pop(index))

        return design_list

    @thread.launch_thread
    def launch_aedt(self):
        """Launch AEDT.

        This method is launched in a thread if gRPC is enabled. AEDT is released once it is opened.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> import time
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.launch_aedt()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = toolkit.get_thread_status()
        >>> toolkit_free = toolkit.get_thread_status()
        """
        # Check if the backend is already connected to an AEDT session
        connected, msg = self.aedt_connected()
        if not connected:
            version = properties.aedt_version
            non_graphical = properties.non_graphical
            selected_process = properties.selected_process
            use_grpc = properties.use_grpc

            pyaedt.settings.use_grpc_api = use_grpc
            if selected_process == 0:  # pragma: no cover
                # Launch AEDT with COM
                self.desktop = pyaedt.Desktop(
                    specified_version=version,
                    non_graphical=non_graphical,
                    new_desktop_session=True,
                )
            elif use_grpc:
                # Launch AEDT with GRPC
                self.desktop = pyaedt.Desktop(
                    specified_version=version,
                    non_graphical=non_graphical,
                    port=selected_process,
                    new_desktop_session=False,
                )
            else:  # pragma: no cover
                self.desktop = pyaedt.Desktop(
                    specified_version=version,
                    non_graphical=non_graphical,
                    aedt_process_id=selected_process,
                    new_desktop_session=False,
                )

            if not self.desktop:
                msg = "AEDT not launched"
                logger.error(msg)
                return False

            msg = "AEDT launched"
            logger.debug(msg)

            # Open project
            if properties.active_project:
                if not os.path.exists(properties.active_project + ".lock"):  # pragma: no cover
                    self.open_project(os.path.abspath(properties.active_project))

            # Save AEDT session properties
            if use_grpc:
                new_properties = {"selected_process": self.desktop.port}
                logger.debug("Grpc port {}".format(str(self.desktop.port)))
            else:
                new_properties = {"selected_process": self.desktop.aedt_process_id}
                logger.debug("Process ID {}".format(str(self.desktop.aedt_process_id)))
            self.set_properties(new_properties)

            self._save_project_info()
            if self.desktop.project_list():
                self.desktop.save_project()

            self.desktop.release_desktop(False, False)
            self.desktop = None

            logger.debug("Desktop released and project properties loaded")

        return True

    def connect_aedt(self):
        """Connect to an existing AEDT session.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> import time
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.launch_aedt()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = toolkit.get_thread_status()
        >>> toolkit.connect_aedt()
        >>> toolkit.release_aedt()
        """
        if properties.selected_process == 0:
            logger.error("Process ID not defined")
            return False

        version = properties.aedt_version
        non_graphical = properties.non_graphical
        selected_process = properties.selected_process
        use_grpc = properties.use_grpc

        # Connect to AEDT
        pyaedt.settings.use_grpc_api = use_grpc
        logger.debug("Connecting AEDT")
        if use_grpc:
            # Launch AEDT with GRPC
            self.desktop = pyaedt.Desktop(
                specified_version=version,
                non_graphical=non_graphical,
                port=selected_process,
                new_desktop_session=False,
            )

        else:  # pragma: no cover
            self.desktop = pyaedt.Desktop(
                specified_version=version,
                non_graphical=non_graphical,
                aedt_process_id=selected_process,
                new_desktop_session=False,
            )

        if not self.desktop:  # pragma: no cover
            logger.debug("AEDT not connected")
            return False

        logger.debug("AEDT connected")
        return True

    def connect_design(self, app_name=None):
        """Connect to an application design.

        If a design exists, this method takes the active project and design. If a design does
        not exist, this method creates a design of the specified type.

        Parameters
        ----------
        app_name : str, optional
            AEDT app name.  If no application is specified, the default is ``"Hfss"``.
            Options are::

            * Circuit Design
            * HFSS
            * Edb
            * EMIT
            * HFSS 3D Layout Design
            * Icepak
            * Maxwell 2D
            * Maxwell 3D
            * 2D Extractor
            * Q3D Extractor
            * Rmxprt
            * Twin Builder
            * Mechanical

        Returns
        -------
        bool
            Returns ``True`` if the connection is successful, ``False`` otherwise.

        Examples
        --------
        >>> import time
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.launch_aedt()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = toolkit.get_thread_status()
        >>> toolkit.connect_design()

        """

        project_name = properties.active_project
        design_name = "No design"
        if properties.active_design:
            design_name = list(properties.active_design.values())[0]
            app_name = list(properties.active_design.keys())[0]

        pyaedt.settings.use_grpc_api = properties.use_grpc
        if design_name != "No design":
            aedt_app_attr = getattr(pyaedt, self.aedt_apps[app_name])
            if properties.use_grpc:
                self.aedtapp = aedt_app_attr(
                    specified_version=properties.aedt_version,
                    port=properties.selected_process,
                    non_graphical=properties.non_graphical,
                    new_desktop_session=False,
                    projectname=project_name,
                    designname=design_name,
                )
            else:
                self.aedtapp = aedt_app_attr(
                    specified_version=properties.aedt_version,
                    aedt_process_id=properties.selected_process,
                    non_graphical=properties.non_graphical,
                    new_desktop_session=False,
                    projectname=project_name,
                    designname=design_name,
                )
            active_design = {app_name: design_name}

        elif app_name in list(self.aedt_apps.keys()):
            design_name = pyaedt.generate_unique_name(app_name)
            aedt_app_attr = getattr(pyaedt, self.aedt_apps[app_name])
            if properties.use_grpc:
                self.aedtapp = aedt_app_attr(
                    specified_version=properties.aedt_version,
                    port=properties.selected_process,
                    non_graphical=properties.non_graphical,
                    new_desktop_session=False,
                    projectname=project_name,
                    designname=design_name,
                )
            else:
                self.aedtapp = aedt_app_attr(
                    specified_version=properties.aedt_version,
                    aedt_process_id=properties.selected_process,
                    non_graphical=properties.non_graphical,
                    new_desktop_session=False,
                    projectname=project_name,
                    designname=design_name,
                )

            active_design = {app_name: design_name}
        else:
            design_name = pyaedt.generate_unique_name("Hfss")
            if properties.use_grpc:
                self.aedtapp = pyaedt.Hfss(
                    specified_version=properties.aedt_version,
                    port=properties.selected_process,
                    non_graphical=properties.non_graphical,
                    new_desktop_session=False,
                    projectname=project_name,
                    designname=design_name,
                )
            else:
                self.aedtapp = pyaedt.Hfss(
                    specified_version=properties.aedt_version,
                    aedt_process_id=properties.selected_process,
                    non_graphical=properties.non_graphical,
                    new_desktop_session=False,
                    projectname=project_name,
                    designname=design_name,
                )
            self.aedtapp.save_project()

            active_design = {"HFSS": design_name}

        if self.aedtapp:
            project_name = self.aedtapp.project_file
            if self.aedtapp.project_file not in properties.project_list:
                properties.project_list.append(project_name)
                properties.design_list[self.aedtapp.project_name] = [active_design]

            if self.aedtapp.design_list and active_design not in properties.design_list[self.aedtapp.project_name]:
                properties.design_list[self.aedtapp.project_name].append(active_design)
            properties.active_project = project_name
            properties.active_design = active_design

            return True

    def release_aedt(self, close_projects=False, close_on_exit=False):
        """Release AEDT.

        Parameters
        ----------
        close_projects : bool, optional
            Whether to close the AEDT projects that are open in the session.
            The default is ``True``.
        close_on_exit : bool, optional
            Whether to close the active AEDT session on exiting AEDT.
            The default is ``True``.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> import time
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.launch_aedt()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = toolkit.get_thread_status()
        >>> toolkit.release_aedt(True, True)

        """
        released = False
        if self.desktop:
            try:
                released = self.desktop.release_desktop(close_projects, close_on_exit)
                self.desktop = None
            except:
                logger.error("Desktop not released")
                return False

        if self.aedtapp:
            try:
                released = self.aedtapp.release_desktop(close_projects, close_on_exit)
                self.aedtapp = None
            except:
                logger.error("Desktop not released")
                return False

        if not released and close_projects and close_on_exit:
            if self.connect_aedt():
                self.desktop.release_desktop(close_projects, close_on_exit)
        return True

    def open_project(self, project_name=None):
        """Open AEDT project.

        Parameters
        ----------
        project_name : str, optional
            Full path for the project.

        Returns
        -------
        bool
            ``True`` when successful, ``False`` when failed.

        Examples
        --------
        >>> import time
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.launch_aedt()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = toolkit.get_thread_status()
        >>> toolkit.open_project("path/to/file")
        >>> toolkit.release_aedt()

        """
        if self.desktop and project_name:
            self.desktop.odesktop.OpenProject(project_name)
            logger.debug("Project {} opened".format(project_name))
            return True
        else:
            return False

    @thread.launch_thread
    def save_project(self, project_path=None):
        """Save the AEDT project.

        This method, which is launched in a thread, uses the project's properties to get the project path.

        Parameters
        ----------
        project_path : str, optional
            Path for saving the project to.
            The default value is ``None``, in which case the current project is overwritten.

        Returns
        -------
        bool
            Returns ``True`` if the connection is successful, ``False`` otherwise.

        Examples
        --------
        >>> import time
        >>> from ansys.aedt.toolkits.antenna.backend.api import Toolkit
        >>> toolkit = Toolkit()
        >>> toolkit.launch_aedt()
        >>> while response[0] == 0:
        >>>     time.sleep(1)
        >>>     response = toolkit.get_thread_status()
        >>> toolkit.connect_aedt()
        >>> toolkit.save_project()
        """
        if self.connect_design():
            if project_path and properties.active_project != project_path:
                old_project_name = os.path.splitext(os.path.basename(properties.active_project))[0]
                self.aedtapp.save_project(project_file=os.path.abspath(project_path))
                index = properties.project_list.index(properties.active_project)
                properties.project_list.pop(index)
                properties.active_project = project_path
                properties.project_list.append(project_path)
                new_project_name = os.path.splitext(os.path.basename(properties.active_project))[0]
                properties.design_list[new_project_name] = properties.design_list[old_project_name]
                if old_project_name != new_project_name:
                    del properties.design_list[old_project_name]
            self.aedtapp.release_desktop(False, False)
            logger.debug("Project saved: {}".format(project_path))
            return True
        else:  # pragma: no cover
            logger.error("Project not saved")
            return False

    def _save_project_info(self):
        # Save project and design info
        new_properties = {}
        project_list = self.desktop.odesktop.GetProjectList()

        if project_list:
            new_properties["project_list"] = []
            active_project = self.desktop.odesktop.GetActiveProject()
            if not active_project:
                active_project = self.desktop.odesktop.SetActiveProject(project_list[0])
            active_project_name = active_project.GetName()
            active_design = active_project.GetActiveDesign()
            # Save active design info
            if active_design:
                active_design_name = active_design.GetName()
                active_design_name = (
                    active_design_name if ";" not in active_design_name else active_design_name.split(";")[1]
                )
                app_name = active_design.GetDesignType()
                if app_name in list(self.aedt_apps.keys()):
                    new_properties["active_design"] = {app_name: active_design_name}
                else:
                    logger.error("Application {} not available".format(app_name))
                    self.desktop.release_desktop(True, True)
                    return False
            elif active_project.GetChildNames():
                active_design_name = active_project.GetChildNames()[0]
                active_design = active_project.SetActiveDesign(active_design_name)
                app_name = active_design.GetDesignType()
                new_properties["active_design"] = {app_name: active_design_name}

            # Save active project
            active_project_path = active_project.GetPath()
            new_properties["active_project"] = os.path.join(active_project_path, active_project_name + ".aedt")
            # Save projects info
            new_properties["design_list"] = {}
            for project in project_list:
                oproject = self.desktop.odesktop.SetActiveProject(project)
                project_name = oproject.GetName()
                project_path = oproject.GetPath()
                logger.debug("Project name: {}".format(project_name))
                new_properties["project_list"].append(os.path.join(project_path, project_name + ".aedt"))

                new_properties["design_list"][project_name] = []

                design_list = oproject.GetChildNames()

                if design_list:
                    for design_name in design_list:
                        odesign = oproject.SetActiveDesign(design_name)
                        app_name = odesign.GetDesignType()
                        if app_name in list(self.aedt_apps.keys()):
                            new_properties["design_list"][project_name].append({app_name: design_name})
                        else:
                            logger.error("Application {} not available".format(app_name))
                            self.desktop.release_desktop(True, True)
                            return False

        if new_properties:
            self.set_properties(new_properties)

    @staticmethod
    def _serialize_obj_base64(file_path):
        with open(file_path, "rb") as f:
            data = f.read()
        encoded_data = base64.b64encode(data)
        return encoded_data
