#!/usr/bin/env python

from setup import SETUP

print "####################################################################################"

print "# DEVICES:"
for device in SETUP.devices:
    device.show()

print "####################################################################################"

print "# TESTS:"
for test in SETUP.tests:
    test.show()

print "####################################################################################"
