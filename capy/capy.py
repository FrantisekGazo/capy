#!/usr/bin/env python

import sys
import argparse
from datetime import datetime
from conf import Config


def get_config():
    return Config('capy_conf.yaml')


def run(device_name, test_name):
    config = get_config()

    # save execution start
    start_time = datetime.now().replace(microsecond=0)

    device = config.get_device(device_name)
    test = config.get_test(test_name, report=True)

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


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument('-r', '--run', nargs=2, metavar=('DEVICE', 'TEST'))
    parser.add_argument('-c', '--console', nargs=1, metavar='DEVICE')
    parser.add_argument('-l', '--list', action='store_true')
    parser.add_argument('-d', '--download', choices=['android', 'ios'])
    parser.add_argument('-i', '--install', nargs=1, metavar='DEVICE')
    args = parser.parse_args()

    if args.run:
        run(args.run[0], args.run[1])
    elif args.console:
        console(args.console[0])
    elif args.list:
        list()
    else:
        parser.parse_args(['--help'])


################################
# run
################################
if __name__ == '__main__':
    main()
