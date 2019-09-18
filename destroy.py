#!/usr/bin/python3 -u

from helper import *
import sys

name = sys.argv[1]

shell('./sargraph.py chart label \"'+name+' \"')
shell("docker-machine mount -u "+name+":/tmp "+name)
shell("docker-machine rm -f "+name)
shell("rm -rf "+name)
