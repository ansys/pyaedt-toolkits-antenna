import copy
import json


class FrozenClass(object):
    """Frozen properties."""

    __isfrozen = False

    def __setattr__(self, key, value):
        if self.__isfrozen:
            if key not in dir(self):
                raise AttributeError("{} is a frozen class. Not existing key: {}".format(type(self).__name__, key))
            if type(value) == int and type(self.__dict__[key]) == float:
                value = float(value)
            if not isinstance(value, type(self.__dict__[key])):
                raise TypeError("{} is a frozen class. Wrong type for key: {}".format(type(self).__name__, key))
        object.__setattr__(self, key, value)

    def _freeze(self):
        self.__isfrozen = True

    def _unfreeze(self):
        self.__isfrozen = False


class PropertiesData(FrozenClass):
    """Properties data model."""

    def __init__(self, default_properties):
        self.__default_properties = copy.deepcopy(default_properties)
        for key, value in self.__default_properties.items():
            setattr(self, key, copy.deepcopy(value))
        self._freeze()  # no new attributes after this point.

    def write_to_file(self, file_name):
        with open(file_name, "w") as write_file:
            temp_dict = {}
            for key in self.__default_properties:
                temp_dict[key] = self.__dict__[key]
            json.dump(temp_dict, write_file, indent=4)

    def read_from_file(self, file_name):
        with open(file_name, "r") as read_file:
            temp_dict = json.load(read_file)
            for key, value in temp_dict.items():
                setattr(self, key, value)

    def reload_defaults(self):
        for key, value in self.__default_properties.items():
            setattr(self, key, copy.deepcopy(value))

    def export_to_dict(self):
        temp_dict = {}
        for key in self.__default_properties:
            temp_dict[key] = self.__dict__[key]
        return temp_dict

    def __eq__(self, other):
        if not isinstance(other, PropertiesData):
            # don't attempt to compare against unrelated types
            return False

        for attr in self.__default_properties.keys():
            if hasattr(other, attr) and self.attr == other.attr:
                continue
            else:
                return False
        return True
