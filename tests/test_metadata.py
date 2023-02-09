from ansys.pyaedt_toolkits.ansys_aedt_toolkits_antennas import __version__


def test_pkg_version():
    assert __version__ == "0.1.dev0"
