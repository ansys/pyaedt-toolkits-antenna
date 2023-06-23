import os
import time

import requests

from conftest import BasisTest


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_get_status(self):
        response = requests.get(self.url + "/get_status")
        assert response.ok
        assert response.json() == "Backend free"

    def test_02_get_properties(self):
        response = requests.get(self.url + "/get_properties")
        assert response.ok
        assert len(response.json()) == 16

    def test_03_set_properties(self):
        new_properties = {
            "aedt_version": self.test_config["aedt_version"],
            "non_graphical": self.test_config["non_graphical"],
            "use_grpc": True,
        }
        response = requests.put(self.url + "/set_properties", json=new_properties)
        assert response.ok
        new_properties = {"use_grpc": 1}
        response = requests.put(self.url + "/set_properties", json=new_properties)
        assert not response.ok
        response = requests.put(self.url + "/set_properties")
        assert not response.ok

    def test_04_installed_versions(self):
        response = requests.get(self.url + "/installed_versions")
        assert response.ok

    def test_05_aedt_sessions(self):
        response = requests.get(self.url + "/aedt_sessions")
        assert response.ok
        assert isinstance(response.json(), list)

    def test_06_connect_design(self):
        response = requests.post(self.url + "/connect_design", json={"aedtapp": "Icepak"})
        assert response.ok

    def test_07_save_project(self):
        file_name = os.path.join(self.local_path.path, "Test.aedt")
        response = requests.post(self.url + "/save_project", json=file_name)
        assert response.ok
        response = requests.get(self.url + "/get_status")
        while response.json() != "Backend free":
            time.sleep(1)
            response = requests.get(self.url + "/get_status")

    def test_08_get_design_names(self):
        response = requests.get(self.url + "/get_design_names")
        assert response.ok
        assert len(response.json()) == 1
