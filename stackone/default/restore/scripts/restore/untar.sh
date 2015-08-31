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

    #go to root/ user terminal entry
    cd
    #go to "/"
    cd ..
    #untar file
    #tar -xvf <file path>
    tar -xvf "${source}"
