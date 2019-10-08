#!/bin/bash


PROJDIR=$1
VM_NAME_PREF=$2
COMMAND=$3
SCRIPTDIR=$4
VMNAME=$5

eval $(docker-machine env --shell bash $VM_NAME_PREF)
real=`realpath $PROJDIR`

cp all.tar $VMNAME/
python3 $SCRIPTDIR/singlejob.py $VM_NAME_PREF "$COMMAND" $real $VMNAME
exit $?
