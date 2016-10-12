#!/usr/bin/env python

from os import environ, makedirs, path
import time
import sys
import subprocess
import shutil
from util import Color, merge, TMP_DIR, STDERR_LOGGER, STDOUT_LOGGER, check_cmd, exit_error
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
    def __init__(self, os, name):
        self.os = os
        self.name = name
        self.ENV = environ.copy()
        self.latest_report_dir = None

    def call(self, cmd):
        if STDOUT_LOGGER.is_used:
            # if custom logger is used, use it too
            main_proc = subprocess.Popen(cmd, env=self.ENV, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            tee_proc = subprocess.Popen(['tee', '-a', STDOUT_LOGGER.file_path], stdin=main_proc.stdout, stdout=STDOUT_LOGGER, stderr=STDERR_LOGGER)
            tee_proc.wait()
            tee_proc.communicate()
        else:
            subprocess.call(cmd, env=self.ENV)

    def run_console(self, build):
        cmd = self.get_console_cmd(build)
        self.call(cmd)

    def get_console_cmd(self, build):
        return []  # implement

    def run(self, build, test, report=False):
        cmd = self.get_run_cmd(build)
        self.show_and_run(cmd, test, report)

    def get_run_cmd(self, build):
        return []  # implement

    def install(self, build):
        pass  # implement

    def uninstall(self, build):
        pass  # implement

    def show_and_run(self, base_cmd, test, report):
        tmp = TMP_DIR
        timestamp = time.strftime('%Y_%m_%d-%H_%M_%S')
        tmp_out = self.current_report_dir(parent=tmp, timestamp=timestamp)
        dir_out = self.device_reports_dir(parent=test.output_dir)

        cmd = base_cmd + test.create_command(tmp_out, report)
        self.ENV = merge(test.env, self.ENV)
        # show commands
        print '--------------------------------------------------------------------------'
        print '| Commands: '
        print '|'
        print '|', " ".join(cmd)
        print '|'
        print '| NOTE: output files will be moved to:', dir_out
        print '|'
        print '--------------------------------------------------------------------------'

        # run command
        self.ENV["SCREENSHOT_PATH"] = tmp_out + '/'  # has to end with '/'
        self.call(cmd)

        # move files if necessary
        if tmp != test.output_dir:
            shutil.move(tmp_out, dir_out)
            shutil.rmtree(self.reports_dir(tmp))

        self.latest_report_dir = self.current_report_dir(parent=test.output_dir, timestamp=timestamp)

    def show(self, line_start=''):
        return line_start + Color.LIGHT_GREEN + '%s ' % self.name + Color.YELLOW + '(%s)' % self.os + Color.ENDC

    def reports_dir(self, parent):
        dir = path.join(parent, 'reports/')
        if not path.exists(dir):
            makedirs(dir)
        return path.abspath(dir)

    def device_reports_dir(self, parent):
        dir = path.join(self.reports_dir(parent), '%s-%s/' % (self.os, self.name))
        if not path.exists(dir):
            makedirs(dir)
        return path.abspath(dir)

    def current_report_dir(self, parent, timestamp):
        dir = path.join(self.device_reports_dir(parent), timestamp)
        if not path.exists(dir):
            makedirs(dir)
        return dir


################################
# iOS Device
################################
class IosDevice(BaseDevice):
    CLI_TOOL = 'ideviceinstaller'

    def __init__(self, name, uuid, ip):
        super(IosDevice, self).__init__(OS.iOS, name)
        self.ENV["DEVICE_TARGET"] = uuid
        self.ENV["DEVICE_ENDPOINT"] = 'http://%s:37265' % ip

    def get_console_cmd(self, build):
        self.ENV["BUNDLE_ID"] = build.app_id
        self.ENV["CODE_SIGN_IDENTITY"] = build.csid
        return ['calabash-ios', 'console', '-p', 'ios']

    def get_run_cmd(self, build):
        self.ENV["BUNDLE_ID"] = build.app_id
        self.ENV["CODE_SIGN_IDENTITY"] = build.csid
        return ['cucumber', '-p', 'ios']

    def show(self, line_start=''):
        s = super(IosDevice, self).show(line_start=line_start)
        s += '\n' + line_start + Color.YELLOW + '  - UUID: ' + Color.ENDC + '%s' % self.ENV[
            "DEVICE_TARGET"] + Color.ENDC
        s += '\n' + line_start + Color.YELLOW + '  - IP: ' + Color.ENDC + '%s' % self.ENV[
            "DEVICE_ENDPOINT"] + Color.ENDC
        return s

    def check_cli_tool(self):
        if not check_cmd(self.CLI_TOOL):
            self.call(['brew', 'install', self.CLI_TOOL])

    def install(self, build):
        self.check_cli_tool()
        self.call([self.CLI_TOOL, '-i', build.get_path()])

    def uninstall(self, build):
        self.check_cli_tool()
        self.call([self.CLI_TOOL, '-U', build.app_id])
        if build.csid:
            self.call([self.CLI_TOOL, '-U', 'com.apple.test.DeviceAgent-Runner'])


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

    def check_cli_tool(self):
        if not check_cmd(self.CLI_TOOL):
            self.call(['brew', 'install', self.CLI_TOOL])

    def install(self, build):
        self.call(['calabash-android', 'build', build.get_path()])  # rebuild test-server
        self.call([self.CLI_TOOL, 'install', '-r', build.get_path()])  # install app

    def uninstall(self, build):
        self.call([self.CLI_TOOL, 'uninstall', build.app_id])
