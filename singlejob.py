#!/usr/bin/python3 -u

import docker
import sys
from helper import *


vm_name_pref=sys.argv[1]
command=sys.argv[2]
projdir=sys.argv[3]
vmname=sys.argv[4]


client = docker.from_env()
print(gt()+"Started task "+sys.argv[2])
#image = client.images.pull("antmicro/ubuntu-build-measure-tools:latest")
ret = subprocess.run(['docker','pull','-q','antmicro/ubuntu-build-measure-tools:latest'])

comm='/bin/bash -c \"cd / && tar -xf %s/all.tar && cd %s && sargraph.py chart start && %s && sargraph.py chart stop\"' % (sys.argv[3],sys.argv[3],sys.argv[2])

container = client.containers.run('antmicro/ubuntu-build-measure-tools:latest',command=comm ,volumes= { "/tmp": {'bind': sys.argv[3], 'mode': 'rw' }}, detach=True, privileged=True)

while True:
    container.reload()
    if container.status == 'exited':
        break
    time.sleep(1)

result = container.wait()

exit_code = result["StatusCode"]


with open(sys.argv[4]+".log","w") as logfile:
    print(container.logs().decode("utf-8"),file=logfile)
    logfile.close()
print(gt()+"Finished task "+sys.argv[2]+" with exit code: "+str(exit_code))
print(gt()+"Task "+sys.argv[2]+" logs:\n"+container.logs().decode("utf-8"))
sys.exit(exit_code)
