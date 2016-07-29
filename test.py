#!/usr/bin/env python

import sys, os, time


################################################################
# Test
################################################################
class Test:
    def __init__(self, name, tags):
        self.name = name
        self.tags = tags

    def show(self):
        print " ", self.name, "->", ', '.join(self.tags)


################################################################
# Feature
################################################################
class Feature:
    def __init__(self, tag):
        self.feature_tag = '@%s' % tag
        self.tags = []

    def scenarios(self, *tags):
        self.tags = ['@%s' % tag for tag in tags]
        return self

    def create_command(self, cmd):
        command = []

        command.extend(cmd)

        command.append('--tags')
        command.append(self.feature_tag)

        if self.tags:
            command.append('--tags')
            command.append(','.join(self.tags))

        return command


################################################################
#
# No Report - pass any number of Feature-s into constructor
#
# this won't generate report
#
################################################################
class NoReport:
    def __init__(self, *features):
        self.features = features

    def create_command(self, cmd, output_dir_path):
        cmds = []

        for feature in self.features:
            cmd = feature.create_command(cmd)
            cmds.append(cmd)

        return cmds


################################################################
#
# Report - pass any number of unique tags into constructor
#
# this will generate a report when test is done
#
# NOTE: Scenarios won't necessarily run in order of given tags
# (Calabash goes through all feature files and their scenarios
# a executes those scenarios that match the tags)
#
################################################################
class Report:
    def __init__(self, *unique_tags):
        self.tags = ['@%s' % tag for tag in unique_tags]

    def create_command(self, cmd, output_dir_path):
        command = []

        command.extend(cmd)

        if self.tags:
            command.append('--tags')
            command.append(','.join(self.tags))

        report_file = os.path.join(output_dir_path, 'report.html')
        command.append('--format')
        command.append('html')
        command.append('--out')
        command.append(report_file)
        command.append('--format')
        command.append('pretty')

        return [command]
