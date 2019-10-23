#!/usr/bin/python3 -u

from helper import *
import sys

prefix = sys.argv[1]
name = prefix + "-" + sys.argv[2]
gcpstorage = sys.argv[3]
shell("docker-machine mount -u "+name+":/tmp "+name)
shell("docker-machine rm -f "+name)
shell("rm -rf "+name)
