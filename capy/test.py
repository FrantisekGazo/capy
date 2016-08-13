#!/usr/bin/env python

import os
from util import Color


################################################################
# Test
#
# this won't generate report
#
# NOTE: Scenarios won't necessarily run in order of given tags
# (Calabash goes through all feature files and their scenarios
# a executes those scenarios that match the tags)
################################################################
class Test:
    def __init__(self, name, cmd):
        self.name = name
        self.cmd = cmd

    def show(self, line_start=''):
        s = line_start + Color.LIGHT_GREEN + self.name + ":\n"
        s += line_start + '\t' + self.cmd + Color.ENDC
        s = s.replace('@', Color.LIGHT_RED + '@' + Color.ENDC)
        s = s.replace('--tags', Color.YELLOW + '--tags')
        s = s.replace(',', Color.YELLOW + ',')
        return s

    def create_command(self, output_dir_path):
        return self.cmd.split(' ')


################################################################
#
# Report
#
# this will generate a report when test is done
#
################################################################
class TestWithReport:
    def __init__(self, test):
        self.test = test

    def create_command(self, output_dir_path):
        command = self.test.create_command(output_dir_path)

        report_file = os.path.join(output_dir_path, 'report.html')
        command.append('--format')
        command.append('html')
        command.append('--out')
        command.append(report_file)
        command.append('--format')
        command.append('pretty')

        return command
