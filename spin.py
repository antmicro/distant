#!/usr/bin/python3 -u

import docker
import os
import configparser
from helper import *
import sys

type = sys.argv[1]
name = sys.argv[2]

shell("docker-machine create --driver google --google-project distributed-build --google-disk-size 50 --google-zone europe-west4-a --google-machine-type "+type+" "+name)
shell("mkdir -p "+name)
shell("docker-machine mount "+name+":/tmp "+name)
