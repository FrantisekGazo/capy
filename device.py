#!/usr/bin/env python

import os
import sys
import time
import subprocess
import shutil


################################
# Base Device
################################
class BaseDevice(object):
    def __init__(self, name, platform):
        self.name = name
        self.platform = platform
        self.ENV = os.environ.copy()

    def call(self, cmd):
        subprocess.call(cmd, env=self.ENV)

    def run_console(self):
        self.check_build()

    def run(self, test):
        self.check_build()

    def check_build(self):
        pass  # download build if not there

    def show_and_run_commands(self, cmd, test):
        dir = self.report_dir()
        cmds = test.create_command(cmd, dir)
        # show commands
        print '--------------------------------------------------------------------------'
        print '| Commands: '
        print '|'

        for cmd in cmds:
            print '|', " ".join(cmd)

        # show message for move if necessary
        output = SETUP.output_dir
        if output:
            dst_dir = self.report_dir(output)
            print '|'
            print '| NOTE: output files will be moved into:', dst_dir
            print '|'

        print '--------------------------------------------------------------------------'

        # run commands
        for cmd in cmds:
            if not os.path.exists(dir):
                os.makedirs(dir)

            self.ENV["SCREENSHOT_PATH"] = dir + '/'  # has to end with '/'

            self.call(cmd)

        # move reports if necessary
        if output:
            dst_dir = self.report_dir(output)
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
    def __init__(self, name, uuid, ip, bundle_id, ipa_path):
        super(IosDevice, self).__init__(name, 'iOS')
        self.ENV["BUNDLE_ID"] = bundle_id
        self.ENV["DEVICE_TARGET"] = uuid
        self.ENV["DEVICE_ENDPOINT"] = 'http://%s:37265' % ip
        self.ipa_path = ipa_path

    def run_console(self):
        super(IosDevice, self).run_console()
        self.call(['calabash-ios', 'console', '-p', 'ios'])

    def run(self, test):
        super(IosDevice, self).run(test)
        cmd = ['cucumber', '-p', 'ios']
        self.show_and_run_commands(cmd, test)

    def show(self):
        super(IosDevice, self).show()
        print "\t- UUID:", self.ENV["DEVICE_TARGET"]
        print "\t- IP:", self.ENV["DEVICE_ENDPOINT"]

    def check_build(self):
        if not os.path.exists(self.ipa_path):
            self.call(['bash', 'download_ios.sh'])


################################
# Android Device
################################
class AndroidDevice(BaseDevice):
    def __init__(self, name, apk_path):
        super(AndroidDevice, self).__init__(name, 'Android')
        self.apk_path = apk_path

    def run_console(self):
        super(AndroidDevice, self).run_console()
        self.call(['calabash-android', 'console', self.apk_path, '-p', 'android'])

    def run(self, test):
        super(AndroidDevice, self).run(test)
        cmd = ['calabash-android', 'run', self.apk_path, '-p', 'android']
        self.show_and_run_commands(cmd, test)

    def check_build(self):
        if not os.path.exists(self.apk_path):
            self.call(['bash', 'download_android.sh'])
