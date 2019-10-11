import subprocess
import time
import datetime
import random
import string
import configparser
import os
from shutil import copyfile
import sys
import argparse


def add_parser():
    parser = argparse.ArgumentParser()
    parser.add_argument("--prepare","-p", action='store', dest='prepare')
    parser.add_argument("--fork","-f", action='store', dest='fork')
    return parser.parse_args()


def shell(cmd):
    subprocess.call(cmd,shell=True)


def soutput(inputcmd):
    cmds = inputcmd.split("|")
    stdin = None
    for cmd in cmds:
        print ("Processing: "+cmd)
        if stdin == None:
            out = subprocess.Popen((cmd.split()),stdout=subprocess.PIPE)
        else:
            out = subprocess.Popen((cmd.split()),stdout=subprocess.PIPE,stdin=stdin)
        #last command in pipes
        if cmds.index(cmd) == len(cmds)-1:
            return out.stdout.read().decode('utf-8').rstrip()
        else:
            stdin = out.stdout


def gt():
    return '['+str(datetime.datetime.now())+'] '

def random_str(strlength=20):
    letters = string.ascii_lowercase
    return ''.join(random.choice(letters) for i in range(strlength))

def get_script_dir():
    return os.path.dirname(os.path.realpath(__file__))

def get_option(csection, coption):
    config = configparser.ConfigParser()

    exists = os.path.isfile(get_script_dir()+'/config.ini')
    if not exists:
        copyfile(get_script_dir()+'/config.ini.example',get_script_dir()+'/config.ini')
    config.read(get_script_dir()+'/config.ini')

    if config.has_option(csection, coption):
        return config.get(csection, coption)



def get_vm(i):
    return get_option('SETUP','VMPREFIX')+'0'+str(i) if i < 10 else get_option('SETUP','VMPREFIX')+str(i)



def get_machines_def():
    if os.path.exists(os.getcwd()+"/machines.conf"):
        print(gt()+"machines.conf found in PROJECT dir.")
        return os.getcwd()+"/machines.conf"
    else:
        print(gt()+"machines.conf not found.")
        return None

def get_local_def():
    if os.path.exists(os.getcwd()+"/local.conf"):
        print(gt()+"local.conf found in PROJECT dir.")
        return os.getcwd()+"/local.conf"
    else:
        print(gt()+"local.conf not found.")
        return None


def vm_list():
    vmlist = []
    machines_def = get_machines_def()
    if machines_def == None:
        return vmlist
    lineList = [line.rstrip('\n') for line in open(machines_def)]

    i = 1
    for line in lineList:
        splitted = line.split(" ",1)
        if len(splitted) == 2:
            vmlist.append([get_vm(i),splitted[0],splitted[1],'',0,0,0,0])
            i += 1
    return vmlist


def local_list():
    locallist = []

    if get_local_def() == None:
        return []

    lineList = [line.rstrip('\n') for line in open(get_local_def())]

    i = 1
    for line in lineList:
            locallist.append([line,'',0])
            i += 1
    return locallist


def check_finished_remote(vmlist):
    if vmlist == None:
        return True
    i = 0
    for vm in vmlist:
        if vm[4] == 0xFFFF:
            i += 1
    if i == len(vmlist):
        return True
    else:
        return False

def check_finished_local(locallist):
    if locallist == None:
        return True
    i = 0
    for lcmd in locallist:
        if lcmd[2] == 0xFFFF:
            i += 1
    if i == len(locallist):
        return True
    else:
        return False
