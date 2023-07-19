import time

from conftest import BasisTest
import requests

test_project_name = "Test"


class TestClass(BasisTest, object):
    def setup_class(self):
        BasisTest.my_setup(self)

    def teardown_class(self):
        BasisTest.my_teardown(self)

    def test_01_create_antenna(self):
        new_properties = {"antenna_type": "Bowtie", "synth_only": False}

        response = requests.put(self.url + "/set_properties", json=new_properties)
        assert response.ok

        response = requests.post(self.url + "/create_antenna")
        assert not response.ok

        new_properties = {
            "antenna_type": "BowTie",
            "synth_only": False,
            "active_design": {},
            "substrate_height": 2,
            "material": "FR4_epoxy",
        }

        response = requests.put(self.url + "/set_properties", json=new_properties)
        assert response.ok

        response = requests.post(self.url + "/connect_design", json={"aedtapp": "HFSS"})
        assert response.ok

        response = requests.post(self.url + "/create_antenna")
        assert response.ok

        response = requests.get(self.url + "/get_status")
        while response.json() != "Backend free":
            time.sleep(1)
            response = requests.get(self.url + "/get_status")
