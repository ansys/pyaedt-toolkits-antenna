# Copyright (c) 2023, ANSYS Inc. unauthorised use, distribution or duplication is prohibited

import copy


class FrozenClass(object):
    __isfrozen = False

    def __setattr__(self, key, value):
        if self.__isfrozen:
            if key not in dir(self):
                raise AttributeError("{} is a frozen class. Not existing key: {}".format(type(self).__name__, key))
        object.__setattr__(self, key, value)

    def _freeze(self):
        self.__isfrozen = True

    def _unfreeze(self):
        self.__isfrozen = False


class Property:

    def __init__(self, value, owner, name):
        self.value = value
        self._owner = owner
        self._name = name

    # def __get__(self, instance, owner):
    #     return getattr(instance, self.value)

    @property
    def hfss_variable(self):
        return f"{self._name}_{self._owner.antenna_name}"

    @hfss_variable.setter
    def hfss_variable(self, var_name):
        raise AttributeError("hfss_variable is auto-generated and cannot be assigned directly.")

    @property
    def disco_variable(self):
        return f"{self._name}_{self._owner.antenna_name}"

    @disco_variable.setter
    def disco_variable(self, var_name):
        raise AttributeError("disco_variable is auto-generated and cannot be assigned directly.")


class SynthesisParameters:

    def __init__(self):
        self._antenna_name = ""

    def add_parameter(self, name, value):
        setattr(self, name, Property(copy.deepcopy(value), self, name))

    @property
    def antenna_name(self):
        return self._antenna_name

    @antenna_name.setter
    def antenna_name(self, name):
        if not self._antenna_name:
            self._antenna_name = name
        else:
            raise AttributeError("Parameter antenna_name can be set only once in the synthesis_parameters.")


class InputParameters(FrozenClass):

    def __init__(self, default_parameters):
        self.__default_properties = copy.deepcopy(default_parameters)
        for key, value in self.__default_properties.items():
            setattr(self, key, copy.deepcopy(value))
        self._freeze()  # no new attributes after this point.
