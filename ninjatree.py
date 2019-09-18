#!/usr/bin/python3 -u

import subprocess
import sys
import re
import time

def process_ninja_output(output):
    targets = re.search('input: phony(.*) outputs',output,re.DOTALL)
    if targets == None:
        return []
    targets = targets.group(1)
    targets = targets.splitlines()
    targets = list(map(str.strip, targets[1:-1]))
    for element in targets[:]:
        if element.startswith('||'):
            targets.remove(element)
    return targets

def get_ninja_query(target):
    cmd = subprocess.Popen("cd {} && ninja -t query {}".format(buildpath,target), shell=True, stdout=subprocess.PIPE)
    stdout = cmd.communicate()[0]
    if(cmd.returncode != 0):
        print("No ninja or ninja error.")
        sys.exit(1)
    output = stdout.decode('utf-8')
    return process_ninja_output(output)


def find_ninja_target(currenttarget,level):
    global track
    found = False
    if level >= maxlevel:
        return False
    targets = get_ninja_query(currenttarget)
    for target in targets:
        if target == aim:
            print("Target found...")
            branches.append(aim)
            track = branches.copy()
            return True
    #need to check whole list before recurency
    targets = get_ninja_query(currenttarget)
    for target in targets:
        if target not in knowntargets:
            branches.append(target)
            found = find_ninja_target(target,level+1)
            branches.pop()
            knowntargets.append(target)
        if found == True:
            print('...at:'+target)
            return True



def find_ninja_alias(currenttarget):
    targets = get_ninja_query(currenttarget)
    if len(targets) == 1:
        print("Found alias: "+targets[0]) 
        return targets[0]


if len(sys.argv) != 5:
    print("Usage: ./ninjatree.py <build_path> <start_target> <targets_list_file> <depth>")
    sys.exit(1)

buildpath = sys.argv[1]
starttarget = sys.argv[2]
aim = sys.argv[3]
maxlevel = int(sys.argv[4])
aimlist = []

lineList = [line.rstrip('\n') for line in open(sys.argv[3])]

for line in lineList:
    aimlist.append(line)

sumtargets = []
sumaim = []

for aim in aimlist:

    knowntargets = []
    branches = []
    track = []

    #We need to find aliases

    target = find_ninja_alias(aim)
    if target is not None:
        aim = target

    sumaim.append(aim)

    onetargets = []

    branches.append(starttarget)

    if find_ninja_target(starttarget,1) != True:
        print("Target not found")
    else:
        #We need to go all the way back and give output indicating all targets to make except found to hav ecomplete builds/tests set.
        while True:
            search = track.pop()
            targets = get_ninja_query(track[len(track)-1])
            for target in targets:
                if target != search:
                    onetargets.append(target)
            if (len(track) == 1):
                break
 
        sumtargets = sumtargets + onetargets


print(sumaim)

sumtargets = list(dict.fromkeys(sumtargets))

sumtargets = [x for x in sumtargets if x not in sumaim]

print(" ".join(sumtargets))
