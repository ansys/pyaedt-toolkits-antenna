import time

import requests

from conftest import BasisTest

test_project_name = "Test"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_create_geometry(self):
        new_properties = {"geometry": "Box"}
        response = requests.put(self.url + "/set_properties", json=new_properties)
        assert response.ok

        response = requests.post(self.url + "/create_geometry")
        assert response.ok

        response = requests.get(self.url + "/get_status")
        while response.json() != "Backend free":
            time.sleep(1)
            response = requests.get(self.url + "/get_status")

        new_properties = {"geometry": "Sphere"}
        response = requests.put(self.url + "/set_properties", json=new_properties)
        assert response.ok

        response = requests.post(self.url + "/create_geometry")
        assert response.ok

        response = requests.get(self.url + "/get_status")
        while response.json() != "Backend free":
            time.sleep(1)
            response = requests.get(self.url + "/get_status")
