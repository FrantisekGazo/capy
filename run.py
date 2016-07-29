#!/usr/bin/env python

import sys
from datetime import datetime
from scripts.profile import get_profile
from scripts.test import get_test

# check args
if len(sys.argv) < 3:
    print 'Usage is : ./run.py <profile-name> <feature-list-name>'
    sys.exit()

profile_name = sys.argv[1]
test_name = sys.argv[2]

# save execution start
start_time = datetime.now().replace(microsecond=0)


# execute tests ----------------------------------------------------------------------------------


test = get_test(test_name)

profile = get_profile(profile_name)
profile.show()
profile.run(test)


# tests finished ---------------------------------------------------------------------------------


# show time
end_time = datetime.now().replace(microsecond=0)
diff = end_time - start_time
print '--------------------------------------------------------------------------'
print '| Total testing time is: ', diff
print '--------------------------------------------------------------------------'
