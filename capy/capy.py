#!/usr/bin/env python

import sys
import argparse
import urllib, json
from datetime import datetime
from conf import Config
from util import Color, STDERR_LOG_MANAGER, STDOUT_LOG_MANAGER, check_cmd, log
from test import TestAction
from cmd import DeviceRunner
from error import CapyException

DESCRIPTION = '''CAPY is a helper for running calabash tests on iOS and Android'''
LONG_DESCRIPTION = DESCRIPTION
NAME = 'capy'
VERSION = '1.1.14'


####################################################################################################
# Version check
####################################################################################################
def check_version():
    msg = check_package(NAME, VERSION)
    if msg:
        c = Color.LIGHT_GREEN
        log.raw(c + '+----------------------------------------+')
        log.raw(c + '| {m:30}'.format(m=msg) + c + ' |')
        log.raw(c + '| {m:38}'.format(m=' ') + c + ' |')
        log.raw(c + '| {m:42}'.format(m='Please run: ' + Color.ENDC + 'pip install -U ' + NAME) + c + ' |')
        log.raw(c + '+----------------------------------------+' + Color.ENDC)


def check_package(name, current_version):
    try:
        response = urllib.urlopen('https://pypi.python.org/pypi/%s/json' % name)
        data = json.loads(response.read())
        latest_version = data['info']['version']
        if latest_version != current_version:
            return '%s has new release (%s) available' % (name, latest_version)
        else:
            return None
    except IOError:
        return None  # show nothing if request failed


def check_calabash():
    cmds = ['calabash-android', 'cucumber']
    for cmd in cmds:
        if not check_cmd(cmd):
            raise CapyException('Command %s was NOT found. Please make sure calabash is installed.' % cmd)


####################################################################################################
# Helper methods
####################################################################################################
def get_config():
    return Config(file_name='capy_conf', private_file_name='capy_private')


def read_build(args):
    return args.build[0] if args.build else None


def show_info():
    log.raw('%s %s' % (NAME, VERSION))
    log.raw(DESCRIPTION)


def console(build_name, device_name):
    check_calabash()

    config = get_config()
    device = config.device_manager.get_device(device_name)
    build = config.build_manager.check_and_get_build(device.os, build_name)
    log.raw(Color.GREEN + "Opening console for device '%s' with '%s'..." % (device.name, build.name) + Color.ENDC)
    DeviceRunner(device).open_console(build)


def run(build_name, device_name, test_name, with_report=False):
    check_calabash()

    # save execution start
    start_time = datetime.now().replace(microsecond=0)

    config = get_config()

    device = config.device_manager.get_device(device_name)
    build = config.build_manager.get_build(device.os, build_name)
    test = config.test_manager.get_test(test_name)

    if with_report:
        # use custom loggers
        sys.stdout = STDOUT_LOG_MANAGER
        STDOUT_LOG_MANAGER.start_for_device(device)
        sys.stderr = STDERR_LOG_MANAGER
        STDERR_LOG_MANAGER.start_for_device(device)

    if test.before:
        for action in test.before:
            exec_action(action, config, build, device)

    # just to make sure build is available (this will download it if not)
    build = config.build_manager.check_and_get_build(device.os, build_name)
    version_names_getter = lambda: config.build_manager.get_version_names(build)

    log.raw(Color.GREEN + "Running '%s' on device '%s' with '%s'..." % (test.name, device.name, build.name) + Color.ENDC)
    runner = DeviceRunner(device)
    runner.run_test(test, build, version_names_getter, report=with_report)

    if test.after:
        for action in test.after:
            exec_action(action, config, build, device)

    # show time
    end_time = datetime.now().replace(microsecond=0)
    diff = end_time - start_time
    log.raw('+-------------------------------------------------------------------------')
    log.raw('| Total testing time is: ' + str(diff))
    log.raw('+-------------------------------------------------------------------------')

    if with_report and runner.latest_report_dir:
        # move logs
        STDOUT_LOG_MANAGER.move_to(runner.latest_report_dir)
        STDERR_LOG_MANAGER.stop()
        STDERR_LOG_MANAGER.move_to(runner.latest_report_dir)
        STDERR_LOG_MANAGER.stop()


def exec_action(test_action, config, build, device):
    log.raw(Color.GREEN + "Running action '%s' on device '%s' with '%s'..." % (test_action, device.name, build.name) + Color.ENDC)
    if test_action == TestAction.DOWNLOAD:
        config.build_manager.download(build)
    elif test_action == TestAction.INSTALL:
        DeviceRunner(device).install(build)
    elif test_action == TestAction.UNINSTALL:
        DeviceRunner(device).uninstall(build)


def list(builds=False, devices=False, tests=False):
    config = get_config()

    line_start = Color.GREEN

    log.raw(line_start + '+------------------------------------------------------------------------------------' + Color.ENDC)
    if builds:
        log.raw(line_start + '| ' + Color.LIGHT_YELLOW + 'BUILDS:')
        log.raw(line_start + '|')
        for os, builds_dict in config.build_manager.builds.iteritems():
            log.raw(line_start + '| ' + os)
            for name, build in sorted(builds_dict.iteritems()):
                log.raw(build.show(line_start + '|    '))
        log.raw(line_start + '|------------------------------------------------------------------------------------' + Color.ENDC)
    if devices:
        log.raw(line_start + '| ' + Color.LIGHT_YELLOW + 'DEVICES:')
        log.raw(line_start + '|')
        for name, device in sorted(config.device_manager.devices.iteritems()):
            log.raw(device.show(line_start + '| '))
        log.raw(line_start + '|------------------------------------------------------------------------------------' + Color.ENDC)
    if tests:
        log.raw(line_start + '| ' + Color.LIGHT_YELLOW + 'TESTS:')
        log.raw(line_start + '|')
        for name, test in sorted(config.test_manager.tests.iteritems()):
            log.raw(test.show(line_start + '| '))
        log.raw(line_start + '+------------------------------------------------------------------------------------' + Color.ENDC)


def download(build_name, os):
    check_calabash()

    config = get_config()
    build = config.build_manager.get_build(os, build_name)
    log.raw(Color.GREEN + "Downloading build '%s' for '%s'..." % (build.name, build.os) + Color.ENDC)
    config.build_manager.download(build)


def install(build_name, device_name):
    check_calabash()

    config = get_config()
    device = config.device_manager.get_device(device_name)
    build = config.build_manager.check_and_get_build(device.os, build_name)
    log.raw(Color.GREEN + "Installing '%s' to device '%s'..." % (build.name, device.name) + Color.ENDC)
    DeviceRunner(device).install(build)


def uninstall(build_name, device_name):
    check_calabash()

    config = get_config()
    device = config.device_manager.get_device(device_name)
    build = config.build_manager.check_and_get_build(device.os, build_name)
    log.raw(Color.GREEN + "Uninstalling '%s' from device '%s'..." % (build.name, device.name) + Color.ENDC)
    DeviceRunner(device).uninstall(build)


###########################################################
# Main
###########################################################
def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-b', '--build', nargs=1, metavar='B',
                        help="Choose different build B to use for tests")
    parser.add_argument('-c', '--console', nargs=1, metavar='D',
                        help="Open calabash console for device D")
    parser.add_argument('-d', '--download', choices=['android', 'ios'],
                        help="Download build for given platform")
    parser.add_argument('-i', '--install', nargs=1, metavar='D',
                        help="Install current build on device D")
    parser.add_argument('-l', '--list', action='store_true',
                        help="List all supported builds, devices and tests")
    parser.add_argument('-lb', '--list-build', action='store_true',
                        help="List all supported builds")
    parser.add_argument('-ld', '--list-device', action='store_true',
                        help="List all supported devices")
    parser.add_argument('-lt', '--list-test', action='store_true',
                        help="List all supported tests")
    parser.add_argument('-r', '--run', nargs=2, metavar=('D', 'T'),
                        help="Run test T on device D")
    parser.add_argument('-rr', '--run-report', nargs=2, metavar=('D', 'T'),
                        help="Run test T on device D and create HTML report")
    parser.add_argument('-v', '--verbose', action='store_true',
                        help="Use verbose mode")
    parser.add_argument('--version', action='store_true',
                        help="Show version info")
    parser.add_argument('-u', '--uninstall', nargs=1, metavar='D',
                        help="Uninstall build from device D")
    args = parser.parse_args()
    try:
        main_run(parser, args)
    except CapyException as ex:
        log.error(ex.message)
        sys.exit(1)


def main_run(parser, args):
    log.setup_verbosity(args.verbose is True)

    # run
    if args.run:
        run(build_name=read_build(args), device_name=args.run[0], test_name=args.run[1])
    elif args.run_report:
        run(build_name=read_build(args), device_name=args.run_report[0], test_name=args.run_report[1], with_report=True)
    # console
    elif args.console:
        console(build_name=read_build(args), device_name=args.console[0])
    # list
    elif args.list:
        list(builds=True, devices=True, tests=True)
    elif args.list_build:
        list(builds=True)
    elif args.list_device:
        list(devices=True)
    elif args.list_test:
        list(tests=True)
    # version
    elif args.version:
        show_info()
    # download
    elif args.download:
        download(build_name=read_build(args), os=args.download)
    # install
    elif args.install:
        install(build_name=read_build(args), device_name=args.install[0])
    # uninstall
    elif args.uninstall:
        uninstall(build_name=read_build(args), device_name=args.uninstall[0])
    # show help by default
    else:
        parser.parse_args(['--help'])

    # check for updates
    check_version()


################################
# run main
################################
if __name__ == '__main__':
    main()
