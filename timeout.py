#!/usr/bin/python3 -u

import docker
import subprocess
import os
import configparser
from helper import *

lineList = [line.rstrip('\n') for line in open('machines.txt')]



i = 0
for line in lineList:
    splitted = line.split(" ",1)
    if len(splitted) == 2:
        i += 1
        name = get_vm(i)

        shell("docker-machine mount -u "+name+":/tmp "+name)
        shell("docker-machine rm -f "+name)
        shell("rm -rf "+name)
