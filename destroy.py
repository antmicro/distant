#!/usr/bin/python3 -u

from helper import *
import sys

prefname = sys.argv[1]
name = sys.argv[2]
shell("docker-machine mount -u "+prefname+":/tmp "+name)
shell("docker-machine rm -f "+prefname)
shell("rm -rf "+name)
