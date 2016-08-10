#!/usr/bin/env python

import os
import time
import subprocess
import shutil


################################
# Device Platform Setup
################################
class PlatformSetup(object):
    def __init__(self, name, app_id, build_path, build_download_cmd, output_dir):
        self.name = name
        self.app_id = app_id
        self.output_dir = output_dir
        self.build_path = build_path
        self.build_download_cmd = build_download_cmd


################################
# Base Device
################################
class BaseDevice(object):
    def __init__(self, platform, name):
        self.platform = platform
        self.name = name
        self.ENV = os.environ.copy()

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

    def install(self):
        pass  # implement

    # download build if not there
    def check_build(self):
        if self.platform.build_download_cmd and not os.path.exists(self.platform.build_path):
            self.call(self.platform.build_download_cmd.split(' '))

    def show_and_run_commands(self, base_cmd, test):
        dir = self.report_dir()
        cmd = base_cmd + test.create_command(dir)
        # show commands
        print '--------------------------------------------------------------------------'
        print '| Commands: '
        print '|'
        print '|', " ".join(cmd)

        # show message for move if necessary
        if self.platform.output_dir:
            dst_dir = self.report_dir(self.platform.output_dir)
            print '|'
            print '| NOTE: output files will be moved into:', dst_dir
            print '|'

        print '--------------------------------------------------------------------------'

        # run command
        if not os.path.exists(dir):
            os.makedirs(dir)
        self.ENV["SCREENSHOT_PATH"] = dir + '/'  # has to end with '/'
        # self.call(cmd)

        # move reports if necessary
        if self.platform.output_dir:
            dst_dir = self.report_dir(self.platform.output_dir)
            shutil.move(dir, dst_dir)

    def show(self):
        print ' %s (%s)' % (self.name, self.platform.name)

    def report_dir(self, parent=None):
        dir = 'reports/%s-%s/%s/' % (self.platform.name, self.name, time.strftime('%Y_%m_%d-%H_%M_%S'))
        if parent:
            dir = os.path.join(parent, dir)
        return os.path.abspath(dir)


################################
# iOS Device
################################
class IosDevice(BaseDevice):
    def __init__(self, platform, name, uuid, ip):
        super(IosDevice, self).__init__(platform, name)
        self.ENV["BUNDLE_ID"] = platform.app_id
        self.ENV["DEVICE_TARGET"] = uuid
        self.ENV["DEVICE_ENDPOINT"] = 'http://%s:37265' % ip

    def get_console_cmd(self):
        return ['calabash-ios', 'console', '-p', 'ios']

    def get_run_cmd(self):
        return ['cucumber', '-p', 'ios']

    def show(self):
        super(IosDevice, self).show()
        print '\t- UUID: %s' % self.ENV["DEVICE_TARGET"]
        print '\t- IP: %s' % self.ENV["DEVICE_ENDPOINT"]

    def install(self):
        self.call(['curl', '-O', 'https://raw.githubusercontent.com/FrantisekGazo/capy/master/scripts/transporter_chief.rb'])
        self.call(['ruby', 'transporter_chief.rb', self.platform.build_path])
        self.call(['rm', 'transporter_chief.rb'])
        self.call(['rm', 'ios-deploy'])


################################
# Android Device
################################
class AndroidDevice(BaseDevice):
    def __init__(self, platform, name):
        super(AndroidDevice, self).__init__(platform, name)

    def get_console_cmd(self):
        return ['calabash-android', 'console', self.platform.build_path, '-p', 'android']

    def get_run_cmd(self):
        return ['calabash-android', 'run', self.platform.build_path, '-p', 'android']

    def install(self):
        self.call(['adb', 'install', self.platform.build_path])
