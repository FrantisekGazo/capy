#!/usr/bin/env python

import argparse
import subprocess
from datetime import datetime
from conf import Config

DESCRIPTION = '''CAPY is a helper for running calabash tests on iOS and Android'''
LONG_DESCRIPTION = DESCRIPTION
NAME = 'capy'
VERSION = '0.5.5'


def get_config():
    return Config('capy_conf.yaml')


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
    print '--------------------------------------------------------------------------'
    print '| Total testing time is: ', diff
    print '--------------------------------------------------------------------------'


def console(device_name):
    config = get_config()

    device = config.get_device(device_name)
    device.show()
    device.run_console()


def list():
    config = get_config()

    print "####################################################################################"
    print "# DEVICES:"
    for device in config.devices:
        device.show()
    print "####################################################################################"
    print "# TESTS:"
    for test in config.tests:
        test.show()
    print "####################################################################################"


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
    device.install()


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
