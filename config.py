#!/usr/bin/env python

import os

##################################################################################
#
# Usage:
#   Just add specific variables to your ~/.bash_profile or default will be used
#
# Example:
#   If you want to set custom 'OUTPUT_DIR' add this line to the ~/.bash_profile:
#       export medrio_mcapture_CALABASH_OUTPUT_DIR='/some/other/dir'
#   ^ whitespaces are permitted (do NOT escape them with '\')
#
##################################################################################

CONFIG = {
    # this directory will contain all reports, screenshots, etc.
    'OUTPUT_DIR': os.environ.get('medrio_mcapture_CALABASH_OUTPUT_DIR', '.') # default is current directory
}

