#!/usr/bin/python3 -u

import docker
import sys
from helper import *

vm_name_pref=sys.argv[1]
command=sys.argv[2]
projdir=sys.argv[3]
vmname=sys.argv[4]
gcpstorage=sys.argv[5]
subdir=sys.argv[6]

print(gt()+"Machine '"+vmname+"' started task "+sys.argv[2])

client = docker.from_env()

#client = docker.Client(base_url='unix://var/run/docker.sock')
print(gt()+"Machine '"+vmname+"' docker image pull.")
ret = subprocess.run(['docker','pull','-q','antmicro/ubuntu-build-measure-tools:latest'])
print(gt()+"Machine '"+vmname+"' docker image pull finished.")

if gcpstorage == 'yes':
#    get_data = "time rsync -a /mnt/disks/data/ %s/" % projdir
    get_data = ":"
    volumes = { "/tmp/build": {'bind': projdir, 'mode': 'rw' }, "/tmp/merged": {'bind': projdir+"/"+subdir, 'mode': 'rw'}}
else:
    get_data = "cd %s && time tar -xf all.tar" % projdir
    volumes = { "/tmp/build": {'bind': projdir, 'mode': 'rw' }}

comm='/bin/bash -c \"cd %s && sargraph.py chart start && sargraph.py chart label copy && %s && cd %s && sargraph.py chart label job && %s && cd %s && sync && sargraph.py chart stop && sync\"' % (projdir, get_data, projdir, command, projdir)
container = client.containers.run('antmicro/ubuntu-build-measure-tools:latest',command=comm ,volumes=volumes, detach=True, privileged=True)

while True:
    container.reload()
    if container.status == 'exited':
        break
    #print(gt()+"Machine '"+vmname+"' - container status = '%s'" % container.status)
    time.sleep(1)

result = container.wait()

exit_code = result["StatusCode"]

with open(sys.argv[4]+".log","w") as logfile:
    print(container.logs().decode("utf-8"),file=logfile)
    logfile.close()
print(gt()+"Machine '"+vmname+"' finished task "+sys.argv[2]+" with exit code: "+str(exit_code))
print(gt()+"Machine '"+vmname+"' task "+sys.argv[2]+" logs:\n"+container.logs().decode("utf-8"))
sys.exit(exit_code)
