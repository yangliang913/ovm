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
while getopts s:d:v:o:m:f: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;
    v)  backup_vm_path="$OPTARG";;
    m)  vm_name="$OPTARG";;
    f)  snapshot_file="$OPTARG";;		
    o)  command="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done

#create tar file
#tar -cvf <destination file path> <source folder path>
tar -Scvf "${destination}" "${source}"
