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
while getopts s:o: a
do case "$a" in
    s)  source="$OPTARG";;
    o)  command="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done

case "$command" in
    GZIP )
        #go to root/ user terminal entry
        cd
        #go to "/"
        cd ..
        #unzip gzip file
        #tar -xvzf <file path>
        tar -xvzf "${source}"
        ;;
    BZIP2 )
        #go to root/ user terminal entry
        cd
        #go to "/"
        cd ..
        #unzip bz2 file
        #tar -xvjf <file path>
        tar -xvjf "${source}"
        ;;
    * )
    exit 1
esac
