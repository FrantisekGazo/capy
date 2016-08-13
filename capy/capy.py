#!/usr/bin/env python

import argparse
import subprocess
import xmlrpclib
from datetime import datetime
from conf import Config
from util import Color

DESCRIPTION = '''CAPY is a helper for running calabash tests on iOS and Android'''
LONG_DESCRIPTION = DESCRIPTION
NAME = 'capy'
VERSION = '0.6.0'


def check_version():
    msg = check_package(NAME, VERSION)
    if msg:
        c = Color.LIGHT_GREEN
        print c + '+-----------------------------------------'
        print c + '| ' + msg
        print c + '|'
        print c + '| Please run: ' + Color.ENDC + 'pip install -U ' + NAME
        print c + '+-----------------------------------------' + Color.ENDC


def check_package(name, current_version):
    pypi = xmlrpclib.ServerProxy('https://pypi.python.org/pypi')
    available = pypi.package_releases(name)
    if not available:
        # Try to capitalize pkg name
        available = pypi.package_releases(name.capitalize())

    msg = name
    if not available:
        msg = None
    elif available[0] != current_version:
        msg += ' has new release (%s) available' % available[0]
    else:
        msg = None
    return msg


def get_config():
    return Config(file_name='capy_conf.yaml', private_file_name='capy_private.yaml')


def run(device_name, test_name, with_report=False):
    config = get_config()

    # save execution start
    start_time = datetime.now().replace(microsecond=0)

    device = config.get_device(device_name)
    test = config.get_test(test_name, report=with_report)

    device.run(test)

    # show time
    end_time = datetime.now().replace(microsecond=0)
    diff = end_time - start_time
    print '+-------------------------------------------------------------------------'
    print '| Total testing time is: ', diff
    print '+-------------------------------------------------------------------------'


def console(device_name):
    config = get_config()

    device = config.get_device(device_name)
    print device.show()
    device.run_console()


def list():
    config = get_config()

    line_start = Color.GREEN

    print line_start + '+------------------------------------------------------------------------------------'
    print line_start + '| DEVICES:'
    print line_start + '|'
    for device in config.devices:
        print device.show(line_start + '| ')
    print line_start + '|------------------------------------------------------------------------------------'
    print line_start + '| TESTS:'
    print line_start + '|'
    for test in config.tests:
        print test.show(line_start + '| ')
    print line_start + '+------------------------------------------------------------------------------------' + Color.ENDC


def version():
    print '%s %s' % (NAME, VERSION)
    print DESCRIPTION


def download(platform_name):
    config = get_config()
    cmd = config.platform_setup[platform_name].build_download_cmd
    print 'Download cmd is: %s' % cmd
    subprocess.call(cmd.split(' '))


def install(device_name):
    config = get_config()
    device = config.get_device(device_name)
    print 'Installing to device %s...' % device.name
    device.check_and_install()


def uninstall(device_name):
    config = get_config()
    device = config.get_device(device_name)
    print 'Uninstalling from device %s...' % device.name
    device.uninstall()


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run', nargs=2, metavar=('DEVICE', 'TEST'),
                        help="Run TEST on DEVICE")
    parser.add_argument('-rr', '--run-report', nargs=2, metavar=('DEVICE', 'TEST'),
                        help="Run TEST on DEVICE and create HTML report")
    parser.add_argument('-c', '--console', nargs=1, metavar='DEVICE',
                        help="Open calabash console for DEVICE")
    parser.add_argument('-l', '--list', action='store_true',
                        help="List all supported devices and tests")
    parser.add_argument('-v', '--version', action='store_true',
                        help="Show version")
    parser.add_argument('-d', '--download', choices=['android', 'ios'],
                        help="Download build for given platform")
    parser.add_argument('-i', '--install', nargs=1, metavar='DEVICE',
                        help="Install current build on DEVICE")
    parser.add_argument('-u', '--uninstall', nargs=1, metavar='DEVICE',
                        help="Uninstall build from DEVICE")
    args = parser.parse_args()

    if args.run:
        run(device_name=args.run[0], test_name=args.run[1])
    elif args.run_report:
        run(device_name=args.run_report[0], test_name=args.run_report[1], with_report=True)
    elif args.console:
        console(device_name=args.console[0])
    elif args.list:
        list()
    elif args.version:
        version()
    elif args.download:
        download(platform_name=args.download)
    elif args.install:
        install(device_name=args.install[0])
    elif args.uninstall:
        uninstall(device_name=args.uninstall[0])
    else:  # show help by default
        parser.parse_args(['--help'])


################################
# run
################################
if __name__ == '__main__':
    main()
    check_version()
