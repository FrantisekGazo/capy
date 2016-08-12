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

    def check_and_install(self):
        self.check_build()
        self.install()

    def install(self):
        pass  # implement

    def uninstall(self):
        pass  # implement

    # download build if not there
    def check_build(self):
        if self.platform.build_download_cmd and not os.path.exists(self.platform.build_path):
            print 'No build for %s was found. Downloading latest...' % self.name
            self.call(self.platform.build_download_cmd.split(' '))

    def show_and_run_commands(self, base_cmd, test):
        tmp = '.capy_temp/'
        tmp_out = self.current_report_dir(tmp)
        dir_out = self.reports_dir(self.platform.output_dir)

        cmd = base_cmd + test.create_command(tmp_out)
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

        # move files
        shutil.move(tmp_out, dir_out)
        shutil.rmtree(tmp)

    def show(self):
        print ' %s (%s)' % (self.name, self.platform.name)

    def reports_dir(self, parent=None):
        dir = 'reports/%s-%s/' % (self.platform.name, self.name)
        if parent:
            dir = os.path.join(parent, dir)
            if not os.path.exists(dir):
                os.makedirs(dir)
        return os.path.abspath(dir)

    def current_report_dir(self, parent=None):
        dir = os.path.join(self.reports_dir(parent), time.strftime('%Y_%m_%d-%H_%M_%S'))
        if not os.path.exists(dir):
            os.makedirs(dir)
        return dir


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
        self.call(['curl', '-O',
                   'https://raw.githubusercontent.com/FrantisekGazo/capy/master/scripts/transporter_chief.rb'])
        self.call(['ruby', 'transporter_chief.rb', self.platform.build_path])
        self.call(['rm', 'transporter_chief.rb'])
        self.call(['rm', 'ios-deploy'])

    def uninstall(self):
        print 'Not supported for now'


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
        self.call(['calabash-android', 'build', self.platform.build_path]) # rebuild test-server
        self.call(['adb', 'install', '-r', self.platform.build_path]) # install app

    def uninstall(self):
        self.call(['adb', 'uninstall', self.platform.app_id])
