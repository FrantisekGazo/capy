#!/usr/bin/env python

from util import Color, exit_error
from device_os import OS


################################
# Device Manager
################################
class DeviceManager(object):
    def __init__(self, conf, os_list):
        if not conf:
            conf = {}

        self.devices = {}
        for os in os_list:
            self.load_devices(conf, os=os)

    # private
    def load_devices(self, conf, os):
        for name, info in conf.get(os, {}).iteritems():
            if os == OS.Android:
                self.devices[name] = AndroidDevice(name)
            elif os == OS.iOS:
                self.validate_device(name, info, 'uuid')
                self.validate_device(name, info, 'ip')

                self.devices[name] = IosDevice(name, info['uuid'], info['ip'])

    # private
    def validate_device(self, name, params, param_name):
        if param_name not in params.keys():
            exit_error("Device '%s' is missing parameter '%s'" % (name, param_name))

    # public
    def get_device(self, name):
        device = self.devices.get(name, None)
        if device:
            return device
        else:
            exit_error("Device '%s' was not found" % name)


################################
# Base Device
################################
class BaseDevice(object):
    def __init__(self, os, name, env={}):
        self.os = os
        self.name = name
        self.env = env

    def get_os(self):
        return self.os

    def get_env(self):
        return self.env

    def get_cli_tools(self):
        return []  # implement

    def get_install_cmds(self, build):
        return []  # implement

    def get_uninstall_cmds(self, build):
        return []  # implement

    def get_console_cmd(self, build):
        return []  # implement

    def get_run_cmd(self, build):
        return []  # implement

    def get_build_env(self, build):
        return {}  # implement

    def show(self, line_start=''):
        return line_start + Color.LIGHT_GREEN + '%s ' % self.name + Color.YELLOW + '(%s)' % self.os + Color.ENDC


################################
# iOS Device
################################
class IosDevice(BaseDevice):
    CLI_TOOL = 'ideviceinstaller'

    def __init__(self, name, uuid, ip):
        env = {
            "DEVICE_TARGET": uuid,
            "DEVICE_ENDPOINT": 'http://%s:37265' % ip
        }
        super(IosDevice, self).__init__(OS.iOS, name, env)

    def get_console_cmd(self, build):
        return ['calabash-ios', 'console', '-p', 'ios']

    def get_run_cmd(self, build):
        return ['cucumber', '-p', 'ios']

    def get_build_env(self, build):
        return {
            "BUNDLE_ID": build.app_id,
            "CODE_SIGN_IDENTITY": build.csid
        }

    def get_cli_tools(self):
        return [self.CLI_TOOL]

    def get_install_cmds(self, build):
        return [
            [self.CLI_TOOL, '-i', build.get_path()]
        ]

    def get_uninstall_cmds(self, build):
        cmds = [
            [self.CLI_TOOL, '-U', build.app_id]
        ]
        if build.csid:
            cmds.append([self.CLI_TOOL, '-U', 'com.apple.test.DeviceAgent-Runner'])

        return cmds

    def show(self, line_start=''):
        s = super(IosDevice, self).show(line_start=line_start)
        s += '\n' + line_start + Color.YELLOW
        s += '  - UUID: ' + Color.ENDC + '%s' % self.env["DEVICE_TARGET"]
        s += Color.ENDC
        s += '\n' + line_start + Color.YELLOW
        s += '  - IP: ' + Color.ENDC + '%s' % self.env["DEVICE_ENDPOINT"]
        s += Color.ENDC
        return s


################################
# Android Device
################################
class AndroidDevice(BaseDevice):
    CLI_TOOL = 'adb'

    def __init__(self, name):
        super(AndroidDevice, self).__init__(OS.Android, name)

    def get_console_cmd(self, build):
        return ['calabash-android', 'console', build.get_path(), '-p', 'android']

    def get_run_cmd(self, build):
        return ['calabash-android', 'run', build.get_path(), '-p', 'android']

    def get_cli_tools(self):
        return [self.CLI_TOOL]

    def get_install_cmds(self, build):
        return [
            ['calabash-android', 'build', build.get_path()],  # rebuild test-server
            [self.CLI_TOOL, 'install', '-r', build.get_path()]  # install app
        ]

    def get_uninstall_cmds(self, build):
        return [
            [self.CLI_TOOL, 'uninstall', build.app_id]
        ]
