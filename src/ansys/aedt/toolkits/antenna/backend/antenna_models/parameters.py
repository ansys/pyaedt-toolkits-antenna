# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 - 2025 ANSYS, Inc. and/or its affiliates.
# SPDX-License-Identifier: MIT
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

import copy


class FrozenClass(object):
    __isfrozen = False

    def __setattr__(self, key, value):
        if self.__isfrozen:
            if key not in dir(self):
                raise AttributeError(
                    "{} is a frozen class. This key does not exist: {}".format(type(self).__name__, key)
                )
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

    @property
    def name(self):
        return self._name

    @property
    def hfss_variable(self):
        return f"{self._name}_{self._owner.name}"

    @hfss_variable.setter
    def hfss_variable(self, var_name):
        raise AttributeError("hfss_variable is auto-generated and cannot be assigned directly.")

    @property
    def disco_variable(self):
        return f"{self._name}_{self._owner.name}"

    @disco_variable.setter
    def disco_variable(self, var_name):
        raise AttributeError("disco_variable is auto-generated and cannot be assigned directly.")


class SynthesisParameters:
    def __init__(self):
        self._name = ""

    def add_parameter(self, name, value):
        setattr(self, name, Property(copy.deepcopy(value), self, name))

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, name):
        if not self._name:
            self._name = name
        else:
            raise AttributeError("Parameter name can be set only once in the synthesis parameters.")


class InputParameters(FrozenClass):
    def __init__(self, default_parameters):
        self.__default_properties = copy.deepcopy(default_parameters)
        for key, value in self.__default_properties.items():
            setattr(self, key, copy.deepcopy(value))
        self._freeze()  # no new attributes after this point.
