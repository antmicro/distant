#!/bin/bash


PREFIX=$1
PROJDIR=$2
SUBDIR=$3

if [ `whoami` = "root" ] ; then
	sudo=""
else
	sudo="sudo"
fi

gcloud version 2> /dev/null

if [ ! $? -eq 0 ] ; then
        exit $?
fi

echo "Trying to create disk '$PREFIX'."

time gcloud compute disks create $PREFIX --size 50 --type pd-ssd --zone europe-west4-a
time gcloud compute instances attach-disk $(hostname) --disk $PREFIX --device-name $PREFIX --zone europe-west4-a
DISKLABEL=`ls -l /dev/disk/by-id | grep -m 1 $PREFIX | sed "s/.*$PREFIX//" | cut -c 11-`
echo "DISKLABEL IS $DISKLABEL"
$sudo mkfs.ext4 -m 0 -F -E lazy_itable_init=0,lazy_journal_init=0,discard /dev/$DISKLABEL
$sudo mkdir -p $PROJDIR/$SUBDIR
$sudo mount -o discard,defaults /dev/$DISKLABEL $PROJDIR/$SUBDIR
$sudo chmod a+w $PROJDIR/$SUBDIR
$sudo rm -rf $PROJDIR/$SUBDIR/lost+found
