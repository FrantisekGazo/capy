#!/usr/bin/env python

import sys
import os
import subprocess
import json


################################
# Build Manager
#
# cli command: curl -O $(curl -u 77df53ebc3234f21862c4be0182dfd0a:'' -s http://inloop-bds.test.inloop.eu/api/v1/customers/medrio/projects/mcapture/applications/ios/environments/internal-calabash/builds/ | python -c 'import sys, json; print json.load(sys.stdin)["builds"][0]["download_url"]')
#
################################
class BuildManager(object):
    API_ENDPOINT = 'http://inloop-bds.test.inloop.eu/api/v1'

    def __init__(self, conf):
        if not conf:
            print 'BDS configuration is missing'
            sys.exit(1)

        self.path = self.load(conf, 'path')
        self.token = self.load(conf, 'token')
        self.customer = self.load(conf, 'customer')
        self.project = self.load(conf, 'project')

        self.builds = {}
        self.load_builds(conf, platform_name='android')
        self.load_builds(conf, platform_name='ios')

    def load(self, conf, prop):
        p = conf.get(prop, None)
        if not p:
            print "BDS configuration is missing a '%s'" % prop
            sys.exit(1)
        return p

    def load_builds(self, conf, platform_name):
        builds = {}

        for name, info in conf.get(platform_name, {}).iteritems():
            build = Build(name, info)
            builds[name] = build

        self.builds[platform_name] = builds

    def download(self, platform_name, build_name):
        # load build from BDS
        bds_build = self.get_latest_bds_build(platform_name, build_name)
        download_url = bds_build['download_url']
        # download
        download_to = self.get_build_path(platform_name, build_name)
        subprocess.call(['curl', '-o', download_to, download_url])

    def get_build_path(self, platform_name, build_name):
        download_path = os.path.join(self.path, platform_name)
        if not os.path.exists(download_path):
            os.makedirs(download_path)
        extension = '.apk' if platform_name == 'android' else '.ipa'
        return os.path.join(download_path, build_name + extension)

    def check_and_get_build_path(self, platform_name, build_name):
        build_path = self.get_build_path(platform_name, build_name)
        if not os.path.exists(build_path):
            self.download(platform_name, build_name)
        return build_name

    def get_latest_bds_build(self, platform_name, build_name):
        build = self.builds[platform_name][build_name]

        token = "%s:\'\'" % self.token

        url = '{api}/customers/{customer}/projects/{project}/applications/{platform}/'.format(
                api=self.API_ENDPOINT, customer=self.customer, project=self.project, platform=platform_name
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

        return json.loads(response)['builds'][0]


class Build(object):
    def __init__(self, name, info):
        self.name = name
        self.app_id = info.get('app_id', None)
        if not self.app_id:
            print "BDS Build '%s' must specify an 'app_id'" % self.name
            sys.exit(1)
        self.env = info.get('env', None)
        self.conf = info.get('conf', None)
