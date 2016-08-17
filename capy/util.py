#!/usr/bin/env python

import sys
import subprocess
import re
from os import environ, path

TMP_DIR = '.capy/'


def merge(user, default):
    if isinstance(user, dict) and isinstance(default, dict):
        for k, v in default.iteritems():
            if k not in user:
                user[k] = v
            else:
                user[k] = merge(user[k], v)
    return user


def get(conf, prop, default):
    p = conf.get(prop, None)
    if p:
        return p
    else:
        return default


class Color:
    ENDC = '\033[0m'

    BOLD = '\033[1m'
    UNDERLINE = '\033[4m'

    DEFAULT = '\033[39m'
    BLACK = '\033[30m'
    RED = '\033[31m'
    GREEN = '\033[32m'
    YELLOW = '\033[33m'
    BLUE = '\033[34m'
    MANGETA = '\033[35m'
    CYAN = '\033[36m'
    LIGHT_GRAY = '\033[37m'
    DARK_GRAY = '\033[90m'
    LIGHT_RED = '\033[91m'
    LIGHT_GREEN = '\033[92m'
    LIGHT_YELLOW = '\033[93m'
    LIGHT_BLUE = '\033[94m'
    LIGHT_MANGETA = '\033[95m'
    LIGHT_CYAN = '\033[96m'
    WHITE = '\033[97m'


class Logger(object):
    def __init__(self):
        self.path = path.join(TMP_DIR, 'logfile.log')
        self.terminal = sys.stdout

    def write(self, message):
        self.terminal.write(message)
        colorless = re.sub(r"\[[0-9]{1,2}m", "", message)
        with open(self.path, "a") as log_file:
            log_file.write(colorless)

    def flush(self):
        # this flush method is needed for python 3 compatibility.
        # this handles the flush command by doing nothing.
        # you might want to specify some extra behavior here.
        pass

    def fileno(self):
        self.terminal.fileno()

SHARED_LOGGER = Logger()
