#!/usr/bin/env python

import sys
from os import path, makedirs
import subprocess
import json
from device_os import OS
from util import Color, TMP_DIR, exit_error, get


################################
# Build Manager
#
# cli command: curl -O $(curl -u 'token':'' -s http://inloop-bds.test.inloop.eu/api/v1/customers/medrio/projects/mcapture/applications/ios/environments/internal-calabash/builds/ | python -c 'import sys, json; print json.load(sys.stdin)["builds"][0]["download_url"]')
#
################################
class BuildManager(object):
    API_ENDPOINT = 'https://inloop-bds.inloop.eu/api/v1'

    def __init__(self, conf, os_list):
        if not conf:
            exit_error('BDS configuration is missing')

        conf['build_dir'] = conf.get('build_dir', path.join(TMP_DIR + 'builds/'))
        self.token = get(conf, 'token', None) # don't check token until it's needed
        self.customer = self.load(conf, 'customer')
        self.project = self.load(conf, 'project')

        self.builds = {}
        for os in os_list:
            self.load_builds(conf, os=os)

    # private
    def get_token(self):
        if not self.token:
            exit_error("BDS configuration is missing a 'token'")
        return self.token

    # public
    def download(self, build):
        # load build from BDS
        bds_build = self.get_latest_bds_build(build)
        download_url = bds_build['download_url']
        print Color.BLUE + 'Downloading from url %s...' % download_url + Color.ENDC
        # download
        download_to = build.get_path()

        if path.exists(download_to):
            print Color.BLUE + 'Removing previous %s...' % download_to + Color.ENDC
            subprocess.call(['rm', download_to])

        # execute download
        download_proc = subprocess.Popen(['curl', '-o', download_to, download_url], stdout=sys.stdout, stderr=sys.stderr)
        download_proc.wait()
        download_proc.communicate()

        if path.exists(download_to):
            print Color.BLUE + 'Downloaded to ' + download_to + Color.ENDC
            if build.os == OS.Android:
                # resign build for Android
                print Color.BLUE + 'Resigning apk...' + Color.ENDC
                subprocess.call(['calabash-android', 'resign', download_to])
        else:
            exit_error('BDS build could not be downloaded')

    # public
    def check_and_get_build(self, os, build_name):
        build = self.get_build(os, build_name)

        build_path = build.get_path()
        if not path.exists(build_path):
            self.download(build)

        return build

    # public
    def get_build(self, os, build_name):
        if build_name:
            build = self.get_builds(os).get(build_name, None)
        else:
            build = self.get_default_build(os)

        if build:
            return build
        else:
            exit_error("Build with name '%s' does not exists for '%s'!" % (build_name, os))

    # public
    def get_builds(self, os):
        builds = self.builds.get(os, None)
        if builds:
            return builds
        else:
            exit_error("No %s builds were found!" % os)

    # private
    def get_default_build(self, os):
        for name, build in self.get_builds(os).iteritems():
            if build.is_default:
                return build

        exit_error("'%s' has no default build! Please add 'default: true' to one of the builds." % os)

    # private
    def load(self, conf, prop):
        p = conf.get(prop, None)
        if not p:
            exit_error("BDS configuration is missing a '%s'" % prop)
        return p

    # private
    def load_builds(self, conf, os):
        builds = {}

        os_conf = get(conf, os, None)
        if not os_conf:
            return

        default_build_found = False
        default_build_name = get(os_conf, 'default', None)
        if not default_build_name:
            exit_error("BDS is missing default build for '%s'" % os)

        for name, info in os_conf.iteritems():
            if name == 'default':
                continue

            info['build_dir'] = info.get('build_dir', conf['build_dir'])
            build = Build(os, name, info)
            if name == default_build_name:
                build.is_default = True
                default_build_found = True
            builds[name] = build

        if not default_build_found:
            exit_error("'%s' default build '%s' was not found" % (os, default_build_name))

        self.builds[os] = builds

    # private
    def get_latest_bds_build(self, build):
        token = "%s:\'\'" % self.get_token()

        url = '{api}/customers/{customer}/projects/{project}/applications/{os}/'.format(
                api=self.API_ENDPOINT, customer=self.customer, project=self.project, os=build.os
        )
        if build.env:
            url += 'environments/{env}/'.format(env=build.env)
        if build.conf:
            url += 'configurations/{conf}/'.format(conf=build.conf)
        url += 'builds/'

        cmd = ['curl', '-u', token, '-s', url]
        c = ' '.join(cmd)

        proc = subprocess.Popen(c, shell=True, stdout=subprocess.PIPE)
        proc.wait()
        response = proc.communicate()[0]
        try:
            return json.loads(response)['builds'][0] # get 1st build
        except:
            exit_error('No BDS build was found')


class Build(object):
    def __init__(self, os, name, info):
        self.os = os
        self.name = name
        self.is_default = False
        self.app_id = info.get('app_id', None)
        if not self.app_id:
            exit_error("BDS Build '%s' must specify an 'app_id'" % self.name)
        self.csid = info.get('csid', None)
        if os == OS.iOS and not self.csid:
            exit_error("BDS iOS Build '%s' must specify a 'csid' (Code Sign Identity)" % self.name)
        self.env = info.get('env', None)
        self.conf = info.get('conf', None)
        self.build_dir = info['build_dir']
        # prepare path
        extension = '.apk' if os == OS.Android else '.ipa'
        self.file_name = name + extension

    # public
    def get_path(self):
        build_path = path.join(self.build_dir, self.os)
        if not path.exists(build_path):
            makedirs(build_path)
        return path.join(build_path, self.file_name)

    # public
    def show(self, line_start=''):
        if self.is_default:
            s = line_start + Color.LIGHT_RED + self.name + Color.RED + ' (default)'
        else:
            s = line_start + Color.LIGHT_GREEN + self.name

        s += '\n' + line_start + Color.YELLOW + '  - app ID: ' + Color.ENDC + self.app_id
        if self.env:
            s += '\n' + line_start + Color.YELLOW + '  - env: ' + Color.ENDC + self.env
        if self.conf:
            s += '\n' + line_start + Color.YELLOW + '  - conf: ' + Color.ENDC + self.conf
        if self.csid:
            s += '\n' + line_start + Color.YELLOW + '  - csid: ' + Color.ENDC + self.csid
        return s
