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

# parse the command line parameters
while getopts s:d: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;  
    
    * )
    echo "$OPTARG"
    ;;
    esac
done

	
rsync_output=`rsync -av --delete "${source}" "${destination}" ;`	
echo "${rsync_output}"

