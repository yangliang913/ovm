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
# author : mkelkar@users.sourceforge.net
#

# parse the command line parameters
while getopts s: a
do case "$a" in
    s)  source="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done 

disk_size=`du -chb "${source}" 2> "/dev/null"| grep total | awk '{print $1}' `
disk_size=`echo "scale=2; $disk_size/1024/1024/1024" | bc`
echo "${disk_size}"
    
