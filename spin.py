#!/usr/bin/python3 -u

import docker
import os
import configparser
from helper import *
import sys
import subprocess

mach_type = sys.argv[1]
prefname = sys.argv[2]
name = prefname + "-" + sys.argv[3]

print(gt()+"Trying to spin machine '%s' of type '%s'" % (name, mach_type))

result = subprocess.call(["docker-machine", "create", "--driver", "google", "--google-project", get_option('SETUP','GCPPROJECT'), "--google-disk-size", "50", "--google-scopes", "https://www.googleapis.com/auth/compute", "--google-zone", "europe-west4-a", "--google-machine-type", mach_type,name])

if result != 0:
    sys.exit(result)

shell("mkdir -p "+name)

print("Trying to mount name=%s:/tmp to %s" % (name,name))

shell("docker-machine ssh "+name+" mkdir -p /tmp/build")
result = subprocess.call(["docker-machine", "mount", name+":/tmp/build", name])

sys.exit(result)
