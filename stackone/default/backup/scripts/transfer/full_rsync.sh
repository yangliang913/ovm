#!/bin/bash 
#
#   stackone   -  Copyright (c) 2008 stackone Corp.
#   ======
#
# stackone is a Virtualization management tool with a graphical user
# interface that allows for performing the standard set of VM operations
# (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
# also attempts to simplify various aspects of VM lifecycle management.
#
#
# 
#
# author : mkelkar@users.sourceforge.net
#

# parse the command line parameters
while getopts s:d:i: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;
    i)  options="$OPTARG";;
    
    * )
    echo "$OPTARG"
    ;;
    esac
done

if [ "${options}" == "NONE" ]; then
    options=""
    rsync_output=`rsync -avb --delete "${source}" "${destination}"`
    echo "${rsync_output}"
    exit
fi
rsync_output=`rsync -avb --delete "${options}" "${source}" "${destination}"`
echo "${rsync_output}"
exit

#if [ "${rsync_output}" != "" ]; then
#	echo ${rsync_output}
#        exit 1
#fi

	
