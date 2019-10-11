#!/bin/bash


PROJDIR=$1
PREFIX=$2
COMMAND=$3
SCRIPTDIR=$4
VMNAME=$5
STORAGE=$6
SUBDIR=$7

echo "work.sh vmname=$VMNAME"

eval $(docker-machine env --shell bash $PREFIX-$VMNAME)
real=`realpath $PROJDIR`
if [ "$STORAGE" == "yes" ]; then
	docker-machine ssh $PREFIX-$VMNAME "gcloud compute instances attach-disk $PREFIX-$VMNAME --disk $PREFIX --mode=ro --zone europe-west4-a && sudo mkdir -p /mnt/disks/data && sudo mount -o discard,defaults /dev/sdb /mnt/disks/data"
	docker-machine ssh $PREFIX-$VMNAME "mkdir /tmp/upper /tmp/work /tmp/merged && sudo mount -t overlay overlay -o lowerdir=/mnt/disks/data,upperdir=/tmp/upper,workdir=/tmp/work /tmp/merged"
else
	echo "$VMNAME: Copying all.tar, `ls -alh all.tar`"
	time cp all.tar $PREFIX-$VMNAME/
	echo "$VMNAME: Finished copying."
fi

echo "running singlejob.py vmname=$VMNAME"

DOCKER_TLS_VERIFY=0 python3 -u $SCRIPTDIR/singlejob.py $PREFIX-$VMNAME "$COMMAND" $real $VMNAME $STORAGE $SUBDIR

RESULT=$?

( sargraph.py chart label $VMNAME || true ) 2> /dev/null

exit $RESULT
