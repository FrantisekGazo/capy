#!/usr/bin/env python

import os
import sys
import yaml
from device import AndroidDevice, IosDevice
from test import Test, TestWithReport


################################
# Setup
################################
class Config:
    def __init__(self, file_name):
        self.data = self.load_setup(file_name)

        self.config = self.load_config()

        self.devices = self.load_devices()

        self.tests = self.load_tests()

    def load_setup(self, file_name):
        if not os.path.exists(file_name):
            print "Current directory does not contain configuration file '%s'. Please create one and run again." % file_name
            sys.exit(1)

        with open(file_name, 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def load_config(self):
        return self.data['config']

    def load_devices(self):
        all = []

        apk_path = self.get_path(self.config['android']['apk'])
        ipa_path = self.get_path(self.config['ios']['ipa'])
        bundle_id = self.config['ios']['bundle']
        out_dir = self.get_path(self.config['output'], default='.')

        devices = self.data['devices']
        for key, value in devices.iteritems():
            if key == 'android':
                for device_name, _ in value.iteritems():
                    d = AndroidDevice(device_name, apk_path)
                    d.output_dir = out_dir
                    all.append(d)
            elif key == 'ios':
                for device_name, device_param in value.iteritems():
                    self.validate_device(device_name, device_param, 'uuid')
                    self.validate_device(device_name, device_param, 'ip')

                    d = IosDevice(device_name, device_param['uuid'], device_param['ip'], bundle_id, ipa_path)
                    d.output_dir = out_dir
                    all.append(d)

        return all

    def validate_device(self, name, params, param_name):
        if param_name not in params.keys():
            print "Device '%s' is missing parameter '%s'" % (name, param_name)
            sys.exit(1)

    def load_tests(self):
        return [Test(name, tags) for name, tags in self.data['tests'].iteritems()]

    def get_path(self, params, default=None):
        if 'path' in params:
            return params['path']
        elif 'env' in params:
            key = params['env']
            return os.environ.get(key, default)
        else:
            raise Exception('Wrong path')

    def get_device(self, name):
        for device in self.devices:
            if device.name == name:
                return device

        print "Device '%s' was not found" % name
        sys.exit(1)

    def get_test(self, name, report=False):
        for test in self.tests:
            if test.name == name:
                return TestWithReport(test) if report else test

        print "Test '%s' was not found" % name
        sys.exit(1)
