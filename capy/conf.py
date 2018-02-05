#!/usr/bin/env python

from os import path
import sys
import yaml
from util import merge, get
from device import DeviceManager
from device_os import OS
from test import TestManager
from bds import BuildManager
from error import CapyException


################################
# Setup
################################
class Config:
    INCLUDE = 'include'

    def __init__(self, file_name, private_file_name=None):
        self.data = self.load_config(file_name, private_file_name)

        self.build_manager = BuildManager(get(self.data, 'bds', None), OS.all)
        self.device_manager = DeviceManager(get(self.data, 'devices', None), OS.all)
        self.test_manager = TestManager(get(self.data, 'tests', None))

    def load_yaml(self, file_name, check):
        if file_name is None:
            if check:
                raise CapyException("Missing configuration file.")
            else:
                return None

        if not path.exists(file_name):
            if check:
                raise CapyException("Current directory does not contain configuration file '%s'. Please create one and run again." % file_name)
            else:
                return None

        with open(file_name, 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as ex:
                raise CapyException(ex.message)

    def load_config(self, file_name, private_file_name):
        data = self.load_yaml(file_name, check=True)
        data = self.apply_includes(data)
        private_data = self.load_yaml(private_file_name, check=False)
        private_data = self.apply_includes(private_data)

        if private_data:
            private_data = merge(private_data, data)
            return private_data
        else:
            return data

    def apply_includes(self, data):
        result = {}

        if data is not None:
            for key, value in data.iteritems():
                if value is None:
                    raise CapyException("'%s:' is empty. Assign it a value!" % key)

                if self.INCLUDE in value and value[self.INCLUDE] is not None:
                    included_value = self.load_yaml(value[self.INCLUDE], True)
                    result[key] = merge(included_value, value)
                else:
                    result[key] = value

        return result

