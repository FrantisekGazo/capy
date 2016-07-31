#!/usr/bin/env python

import sys
import argparse
from datetime import datetime
from setup import SETUP


def run(device_name, test_name):
    # save execution start
    start_time = datetime.now().replace(microsecond=0)

    device = SETUP.get_device(device_name)
    test = SETUP.get_test(test_name, report=True)

    device.run(test)

    # show time
    end_time = datetime.now().replace(microsecond=0)
    diff = end_time - start_time
    print '--------------------------------------------------------------------------'
    print '| Total testing time is: ', diff
    print '--------------------------------------------------------------------------'


def console(device_name):
    device = SETUP.get_device(device_name)
    device.show()
    device.run_console()


def list():
    print "####################################################################################"
    print "# DEVICES:"
    for device in SETUP.devices:
        device.show()
    print "####################################################################################"
    print "# TESTS:"
    for test in SETUP.tests:
        test.show()
    print "####################################################################################"


# if __name__ == '__main__':
#     if len(sys.argv) == 1:
#         print 'Specify what to do! (run / console / list)'
#         sys.exit()
#
#     action = sys.argv[1]
#
#     if action == 'run':
#         if len(sys.argv) != 4:
#             print 'Usage is: run <device-name> <test-name>'
#             sys.exit()
#
#         device = sys.argv[2]
#         test = sys.argv[3]
#         run(device, test)
#
#     elif action == 'console':
#         if len(sys.argv) != 3:
#             print 'Usage is: console <device-name>'
#             sys.exit()
#
#         device = sys.argv[2]
#         console(device)
#
#     elif action == 'list':
#         if len(sys.argv) != 2:
#             print 'Usage is: list'
#             sys.exit()
#
#         list()
#
#     else:
#         print 'Choose one of these actions: run / console / list'
#         sys.exit()


################################
# run
################################
if __name__ == '__main__':
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
