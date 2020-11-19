#!/bin/bash

RV=`bundle platform --ruby`
IFS=', ' read -r -a array <<< $RV
echo $array[2]
V=${array[2]:-2.4.1}
echo $V
if [ $V == 'version' ]
then
  asdf local ruby 2.4.1
else
  asdf local ruby ${V}
fi
