#!/usr/bin/python3 -u

import docker
import os
import configparser
from helper import *
import sys

type = sys.argv[1]
prefname = sys.argv[2]
name = sys.argv[3]

shell("docker-machine create --driver google --google-project "+get_option('SETUP','GCPPROJECT')+"  --google-disk-size 50 --google-zone europe-west4-a --google-machine-type "+type+" "+prefname)
shell("mkdir -p "+name)
shell("docker-machine mount "+prefname+":/tmp "+name)
