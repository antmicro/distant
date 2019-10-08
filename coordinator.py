#!/usr/bin/python3 -u

from helper import *
import sys
import time

vmlist = vm_list()
locallist = local_list()
currenttime = time.time()

vmprefix = random_str(5)+"-"

exit_code = 0

shell("tar -cf all.tar "+os.getcwd()+"/*")

while(True):

    for vm in vmlist:
        if vm[4] == 0:
            vm[3] = subprocess.Popen(['python3',get_script_dir()+'/spin.py',vm[1],vmprefix+vm[0],vm[0]])
            print(gt()+"Creating machine "+vm[1]+" name: "+vm[0])
            vm[4] += 1

        if vm[4] == 1:
            if vm[3].poll() is not None:
                exit_code = max(exit_code,vm[3].returncode)
                print(gt()+"Machine "+vm[0]+" type "+vm[1]+" ready for "+vm[2])
                vm[3] = subprocess.Popen([get_script_dir()+'/work.sh {0} {1} \"{2}\" {3} {4}'.format(os.getcwd(),vmprefix+vm[0],vm[2],get_script_dir(),vm[0])],shell=True)
                vm[4] += 1

        if vm[4] == 2:
            if vm[3].poll() is not None:
                exit_code = max(exit_code,vm[3].returncode)
                print ("Saving machine "+vm[0]+" output to vmoutput project subdirectory")
                shell("mkdir -p vmoutput")
                shell("mv "+vm[0]+".log vmoutput/")
                print(gt()+"Machine "+vm[0]+" type "+vm[1]+" ready to be destroyed after task "+vm[2])
                shell("cp "+vm[0]+"/plot.png vmoutput/"+vm[0]+".png")
                vm[3] = subprocess.Popen(['python3',get_script_dir()+'/destroy.py',vmprefix+vm[0],vm[0]])
                vm[4] += 1

        if vm[4] == 3:
            if vm[3].poll() is not None:
                exit_code = max(exit_code,vm[3].returncode)
                vm[4] += 1

    for lcmd in locallist:
        if lcmd[2] == 0:
            lcmd[1] = subprocess.Popen("cd "+path+" && "+lcmd[0],shell=True)
            print(gt()+"Executing local command "+lcmd[0])
            lcmd[2] += 1

        if lcmd[2] == 1:
            if lcmd[1].poll() is not None:
                exit_code = max(exit_code,lcmd[1].returncode)
                print(gt()+"Local command completed:  "+lcmd[0])
                lcmd[2] += 1

    if check_finished_remote(vmlist) == True and check_finished_local(locallist) == True:
        print("All remote and local tasks finished, machines disposed")
        shell("rm -f all.tar")
        break

    time.sleep(1)

    if(currenttime + int(get_option('SETUP','TIMEOUT'))*60) < time.time():
        print("Timeout! Destroying worker machines")
        for vm in vmlist:
            if isinstance(vm[3],subprocess.Popen):
                vm[3].kill()
        shell(get_script_dir()+"/timeout.py")
        sys.exit(1)

sys.exit(exit_code)
