#!/usr/bin/env python

import os
import sys
import yaml
from device import PlatformSetup, AndroidDevice, IosDevice
from test import Test, TestWithReport


def merge(user, default):
    if isinstance(user, dict) and isinstance(default, dict):
        for k, v in default.iteritems():
            if k not in user:
                user[k] = v
            else:
                user[k] = merge(user[k], v)
    return user


################################
# Setup
################################
class Config:
    def __init__(self, file_name, private_file_name):
        self.data = self.load_setup(file_name, private_file_name)
        # config
        self.config = self.load_config()
        # devices
        self.platform_setup = {
            'android': self.load_platform_setup('Android'),
            'ios': self.load_platform_setup('iOS')
        }
        self.devices = self.load_devices()
        # tests
        self.tests = self.load_tests()

    def load_yaml(self, file_name, check):
        if not os.path.exists(file_name):
            if check:
                print "Current directory does not contain configuration file '%s'. Please create one and run again." % file_name
                sys.exit(1)
            else:
                return None

        with open(file_name, 'r') as stream:
            try:
                return yaml.load(stream)
            except yaml.YAMLError as exc:
                print(exc)

    def load_setup(self, file_name, private_file_name):
        data = self.load_yaml(file_name, check=True)
        private_data = self.load_yaml(private_file_name, check=False)

        if private_data:
            private_data = merge(private_data, data)
            return private_data
        else:
            return data

    def load_config(self):
        return self.data['config']

    def load_platform_setup(self, platform_name):
        output_dir = self.config.get('output_path', '.')
        platform_config = self.config[platform_name.lower()]
        return PlatformSetup(
                name=platform_name,
                app_id=platform_config['app_id'],
                build_path=platform_config['build_path'],
                build_download_cmd=platform_config.get('download', ''),
                output_dir=output_dir
        )

    def load_devices(self):
        all = []

        devices = self.data['devices']
        for key, value in devices.iteritems():
            if key == 'android':
                for device_name, _ in value.iteritems():
                    d = AndroidDevice(self.platform_setup['android'], device_name)
                    all.append(d)
            elif key == 'ios':
                for device_name, device_param in value.iteritems():
                    self.validate_device(device_name, device_param, 'uuid')
                    self.validate_device(device_name, device_param, 'ip')

                    d = IosDevice(self.platform_setup['ios'], device_name, device_param['uuid'], device_param['ip'])
                    all.append(d)

        return all

    def validate_device(self, name, params, param_name):
        if param_name not in params.keys():
            print "Device '%s' is missing parameter '%s'" % (name, param_name)
            sys.exit(1)

    def load_tests(self):
        return [Test(name, tags) for name, tags in self.data['tests'].iteritems()]

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
