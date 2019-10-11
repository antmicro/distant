#!/usr/bin/python3 -u

from helper import *
import sys
import time


parser=add_parser()

if not parser.prepare and not parser.fork:
    print("No args given, use -h for help.")
    sys.exit(1)


vmlist = vm_list()
locallist = local_list()
currenttime = time.time()

vmprefix = random_str(5)

if parser.prepare != None:
    print("Prepare stage! Dir:"+parser.prepare) 
    shell(get_script_dir()+'/storage.sh {0} {1} {2}'.format(vmprefix,os.getcwd(),parser.prepare))
    print("Prepare stage completed! Dir:"+parser.prepare) 
    sys.exit(0)
elif parser.fork != None:
    print("Fork phase")
    if get_option('SETUP','GCPSTORAGE') == "yes":
        print("GCP storage enabled, checking attached disk")
        prefix = soutput("ls -l /dev/disk/by-id | grep -m 1 sdb | sed s/.*google-\(.*\)sdb.*/\\1/ | cut -c 1-5")
        if prefix == None:
             print("Attached disk not found, exiting")
             sys.exit(1)
        else:
             print("Attached disk with prefix "+prefix+" found.")
             vmprefix = prefix
             print("Reattaching disk in ro mode")
             shell("sudo umount /dev/sdb")
             shell("gcloud compute instances detach-disk $(hostname) --disk="+prefix+" --zone europe-west4-a")
             shell("gcloud compute instances attach-disk $(hostname) --disk="+prefix+" --device-name="+prefix+" --zone europe-west4-a --mode=ro")
             shell("mkdir -p /tmp/"+prefix+"/lower /tmp/"+prefix+"/work /tmp/"+prefix+"/upper")
             shell("sudo mount /dev/sdb /tmp/"+prefix+"/lower")
             shell("sudo mount -t overlay overlay -o lowerdir=/tmp/"+prefix+"/lower,upperdir=/tmp/"+prefix+"/upper,workdir=/tmp/"+prefix+"/work "+os.getcwd()+"/"+parser.fork)



exit_code = 0

SARGRAPH = 1

def sargraph_start():
    if SARGRAPH == 1:
        shell("sargraph.py graph start") 
    else:
        pass

def sargraph_stop():
    if SARGRAPH == 1:
        shell("sargraph.py graph stop")
    else:
        pass
def sargraph_label(s):
    if SARGRAPH == 1:
        shell("sargraph.py graph label '%s'" % s)
    else:
        pass

try:
    result = subprocess.call(["gcloud", "--version"])
except:
    result = 1

try:
    result = subprocess.call(["sargraph.py", "--version"])
except:
    result = 1

if result != 0:
    print(gt()+"Warning: sargraph not found.")
    SARGRAPH = 0

if get_option('SETUP','GCPSTORAGE') == 'no':
    sargraph_label("tar")
    shell("time -p tar --exclude=plot.png --exclude=all.tar --exclude=data.txt -cf all.tar *")
    sargraph_label("tardone")

message = currenttime

def state_to_string(st):
    if st == 0:
            return "non-existant"
    elif st == 1:
            return "creating"
    elif st == 2:
            return "executing"
    elif st == 3:
            return "stopping"
    elif st == 0xFFFF:
            return "stopped"
    else:
            return "unknown"

def start_first():
    first = 1
    if get_option('SETUP','SEQUENTIAL') == 'yes':
        for vm in vmlist:
            if (vm[4] == 0) and (first == 1):
                first = 0
                vm[7] = 0
                continue
            vm[7] = 1

start_first()

if get_option('SETUP','SEQUENTIAL') == 'yes':
    print(gt()+"Warning! Sequential mode enabled.")

while(True):
    for vm in vmlist:
        if vm[4] == 0:
            if vm[7] == 0:
                print(gt()+"Creating machine '%s' of type '%s'" % (vm[0], vm[1]))
                vm[3] = subprocess.Popen(['python3',get_script_dir()+'/spin.py',vm[1],vmprefix,vm[0]])
                vm[4] += 1
                vm[5] = time.time()
                vm[6] = 0
        elif vm[4] == 1:
            if vm[3].poll() is not None:
                exit_code = max(exit_code,vm[3].returncode)
                if vm[3].returncode == 0:
                    print(gt()+"Machine '"+vm[0]+"' of type '"+vm[1]+"' ready for executing '"+vm[2]+"'")
                    if parser.fork == None:
                        parser.fork == 0
                    vm[3] = subprocess.Popen(["bash", get_script_dir()+"/work.sh", os.getcwd(), vmprefix, vm[2], get_script_dir(), vm[0], get_option('SETUP', 'GCPSTORAGE'),parser.fork])
                    vm[4] += 1
                else:
                    print(gt()+"Error: failed to start machine '%s'" % vm[0])
                    vm[4] = 0xFFFF
                    vm[6] = time.time()
        elif vm[4] == 2:
            if vm[3].poll() is not None:
                exit_code = max(exit_code,vm[3].returncode)
                print(gt()+"Saving machine '"+vm[0]+"' output to vmoutput project subdirectory")
                shell("mkdir -p vmoutput")
                shell("mv "+vm[0]+".log vmoutput/")
                print(gt()+"Machine '"+vm[0]+"' ready to be destroyed after task '"+vm[2]+"'")
                shell("cp "+vmprefix+"-"+vm[0]+"/plot.png vmoutput/"+vm[0]+".png")
                vm[3] = subprocess.Popen(['python3',get_script_dir()+'/destroy.py',vmprefix,vm[0],get_option('SETUP','GCPSTORAGE')])
                vm[4] += 1
        elif vm[4] == 3:
            if vm[3].poll() is not None:
                exit_code = max(exit_code,vm[3].returncode)
                print(gt()+"Machine '"+vm[0]+"' succesfully destroyed.")
                vm[4] = 0xFFFF
                vm[6] = time.time()
        elif vm[4] == 0xFFFF:
            start_first()
            continue
        else:
            print(gt()+"Machine '%s' is in unknown state=%d" % (vm[0], vm[4]))

    for lcmd in locallist:
        if lcmd[2] == 0:
            lcmd[1] = subprocess.Popen("cd "+path+" && "+lcmd[0],shell=True)
            print(gt()+"Executing local command "+lcmd[0])
            lcmd[2] += 1
        elif lcmd[2] == 1:
            if lcmd[1].poll() is not None:
                exit_code = max(exit_code,lcmd[1].returncode)
                print(gt()+"Local command completed:  "+lcmd[0])
                lcmd[2] = 0xFFFF
        elif lcmd[2] == 0xFFFF:
            continue
        else:
            print(gt()+"Unkown state=%d" % lcmd[2])

    if (message + 30) < time.time() or (check_finished_remote(vmlist) == True and check_finished_local(locallist) == True):
        message = time.time()
        print(gt()+"Current vm state is:")
        for vm in vmlist:
            if (vm[4] == 0xFFFF):
                end_date = vm[6]
            else:
                end_date = time.time()
            start_date = vm[5]
            if end_date != 0 and start_date != 0:
                duration = ", active: %.2f minutes" % ((end_date - start_date)/60.0)
            else:
                duration = ""
            print(gt()+"  -> 0x%04x [%15s] %s%s" % (vm[4], state_to_string(vm[4]), "%s / %s" %(vm[0], vm[1]), duration))

    if check_finished_remote(vmlist) == True and check_finished_local(locallist) == True:
        print(gt()+"All remote and local tasks finished, machines disposed")
        shell("rm -f all.tar")
        if get_option('SETUP','GCPSTORAGE') == 'yes':
            shell("sudo umount overlay")
            shell("sudo umount /dev/sdb") 
            shell("gcloud compute instances detach-disk $(hostname) --disk="+vmprefix+" --zone europe-west4-a")
            shell("gcloud compute disks delete "+vmprefix+" --zone europe-west4-a --quiet")
        break
    time.sleep(0.1)

    if(currenttime + int(get_option('SETUP','TIMEOUT'))*60) < time.time():
        print("Timeout! Destroying worker machines")
        for vm in vmlist:
            if isinstance(vm[3],subprocess.Popen):
                vm[3].kill()
        shell(get_script_dir()+"/timeout.py")
        sys.exit(1)

print(gt()+"Returning with exit code=%d" % exit_code)
sys.exit(exit_code)
