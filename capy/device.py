#!/usr/bin/env python

import os
import time
import subprocess
import shutil


################################
# Base Device
################################
class BaseDevice(object):
    def __init__(self, name, platform, build_path, download_cmd):
        self.name = name
        self.platform = platform
        self.ENV = os.environ.copy()
        self.output_dir = None
        self.build_path = build_path
        self.build_download_cmd = download_cmd

    def call(self, cmd):
        subprocess.call(cmd, env=self.ENV)

    def run_console(self):
        self.check_build()
        cmd = self.get_console_cmd()
        self.call(cmd)

    def get_console_cmd(self):
        return []  # implement

    def run(self, test):
        self.check_build()
        cmd = self.get_run_cmd()
        self.show_and_run_commands(cmd, test)

    def get_run_cmd(self):
        return []  # implement

    # download build if not there
    def check_build(self):
        if self.build_download_cmd and not os.path.exists(self.build_path):
            self.call(self.build_download_cmd.split(" "))

    def show_and_run_commands(self, base_cmd, test):
        dir = self.report_dir()
        cmd = base_cmd + test.create_command(dir)
        # show commands
        print '--------------------------------------------------------------------------'
        print '| Commands: '
        print '|'
        print '|', " ".join(cmd)

        # show message for move if necessary
        if self.output_dir:
            dst_dir = self.report_dir(self.output_dir)
            print '|'
            print '| NOTE: output files will be moved into:', dst_dir
            print '|'

        print '--------------------------------------------------------------------------'

        # run command
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.ENV["SCREENSHOT_PATH"] = dir + '/'  # has to end with '/'
        self.call(cmd)

        # move reports if necessary
        if self.output_dir:
            dst_dir = self.report_dir(self.output_dir)
            shutil.move(dir, dst_dir)

    def show(self):
        print " ", self.name
        print "\t- Platform:", self.platform

    def report_dir(self, parent=None):
        dir = 'reports/%s-%s/%s/' % (self.platform, self.name, time.strftime('%Y_%m_%d-%H_%M_%S'))
        if parent:
            dir = os.path.join(parent, dir)
        return os.path.abspath(dir)


################################
# iOS Device
################################
class IosDevice(BaseDevice):
    def __init__(self, name, uuid, ip, bundle_id, build_path, download_cmd):
        super(IosDevice, self).__init__(name, 'iOS', build_path, download_cmd)
        self.ENV["BUNDLE_ID"] = bundle_id
        self.ENV["DEVICE_TARGET"] = uuid
        self.ENV["DEVICE_ENDPOINT"] = 'http://%s:37265' % ip

    def get_console_cmd(self):
        return ['calabash-ios', 'console', '-p', 'ios']

    def get_run_cmd(self):
        return ['cucumber', '-p', 'ios']

    def show(self):
        super(IosDevice, self).show()
        print "\t- UUID:", self.ENV["DEVICE_TARGET"]
        print "\t- IP:", self.ENV["DEVICE_ENDPOINT"]


################################
# Android Device
################################
class AndroidDevice(BaseDevice):
    def __init__(self, name, build_path, download_cmd):
        super(AndroidDevice, self).__init__(name, 'Android', build_path, download_cmd)

    def get_console_cmd(self):
        return ['calabash-android', 'console', self.build_path, '-p', 'android']

    def get_run_cmd(self):
        return ['calabash-android', 'run', self.build_path, '-p', 'android']
