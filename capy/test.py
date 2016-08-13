#!/usr/bin/env python

from os import path
from util import Color, merge, TMP_DIR


################################
# Test Manager
################################
class TestManager(object):
    def __init__(self, conf):
        if not conf:
            print Color.LIGHT_RED + 'TESTS configuration is missing' + Color.ENDC
            sys.exit(1)

        self.output_dir = conf.get('output_dir', path.join(TMP_DIR))
        conf['output_dir'] = self.output_dir
        self.tests = self.load_tests(conf)

    def load_tests(self, conf):
        tests = {}

        for name, info in conf.iteritems():
            if name == 'output_dir':
                continue

            info = merge(info, conf)
            tests[name] = Test(name, info)

        return tests

    def get_test(self, name, report=False):
        test = self.tests.get(name, None)
        if test:
            return TestWithReport(test) if report else test
        else:
            print Color.LIGHT_RED + "Test '%s' was not found" % name + Color.ENDC
            sys.exit(1)


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
    def __init__(self, name, conf):
        self.name = name
        self.output_dir = conf['output_dir']
        self.cmd = conf['run']

    def show(self, line_start=''):
        s = line_start + Color.LIGHT_GREEN + self.name + ":\n"
        s += line_start + '  ' + self.cmd + Color.ENDC
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

        report_file = path.join(output_dir_path, 'report.html')
        command.append('--format')
        command.append('html')
        command.append('--out')
        command.append(report_file)
        command.append('--format')
        command.append('pretty')

        return command
