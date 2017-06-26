#!/usr/local/bin/python
#
# mount_option_of mount_point
#
# prints comma-separated mount(8) options of mount_point

import sys
import subprocess
import re

path = sys.argv[1]
proc = subprocess.Popen("mount", stdout=subprocess.PIPE)
for l in proc.stdout.readlines():
  fields = re.split(r"\s+", l)
  if fields[2] == path:
    options = re.sub(r"^.*\((.*)\)$", r"\1", l).replace(" ", "").split(",")
    options.remove("local") # "local" is not really an option
    print ",".join(options).rstrip()
    exit(0)

exit(1)
