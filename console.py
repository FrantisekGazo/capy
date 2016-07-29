#!/usr/bin/env python

import sys
from scripts.profile import get_profile

# check args
if len(sys.argv) < 2:
    print 'Usage is : ./console.py <profile-name>'
    sys.exit()

profile_name = sys.argv[1]

profile = get_profile(profile_name)
profile.show()
profile.run_console()
