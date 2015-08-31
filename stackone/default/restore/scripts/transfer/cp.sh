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
while getopts s:d:o: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;
    o)  command="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done

    output=`cp -ar "${source}" "${destination}"`
    if [ "${output}" != "" ]; then
        echo "${output}"
        exit 1
    fi
