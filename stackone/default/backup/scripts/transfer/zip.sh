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

case "$command" in
    GZIP )
        #gzip -v <.tar file path>
        tar -Sczf "${destination}" "${source}"
        ;;
    BZIP2 )
        #bzip2 -v <.tar file path>
        tar -Scjf "${destination}" "${source}"
        ;;
    * )
    exit 1
esac
