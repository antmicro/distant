#!/bin/bash

eval $(docker-machine env --shell bash $2)
real=`realpath $1`

cp $4/all.tar $2/
python3 $4/singlejob.py $2 "$3" $real
exit $?
