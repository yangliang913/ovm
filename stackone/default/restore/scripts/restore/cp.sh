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

case "$command" in
    CP )
        #here cp has single quote because of this it will not prompt while overwritting the contents.
        output=`'cp' -ar "${source}" "${destination}"`
        if [ "${output}" != "" ]; then
            echo "${output}"
            exit 1
        fi
        ;;
    CONTENT_CP )
        #here cp has single quote because of this it will not prompt while overwritting the contents.
        output=`'cp' -arf "${source}" "${destination}"`
        if [ "${output}" != "" ]; then
            echo "${output}"
            exit 1
        fi
        ;;
    * )
    exit 1
esac