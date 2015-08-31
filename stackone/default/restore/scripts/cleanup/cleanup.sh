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
while getopts v:s:d:g:o: a
do case "$a" in
    v)  backup_vm_path="$OPTARG";;
    s)  snapshot_location="$OPTARG";;
    d)  disk="$OPTARG";;
    g)  volume_group="$OPTARG";;
    o)  command="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done

case "$command" in
    DETACH_VOL_GROUP )
        #dactivate volume groups
        vgchange -an "${volume_group}"
        ;;
    REMOVE_MAPPER )
        #remove dev loop and dev mappers
        kpartx -ad "${disk}"
        ;;
    CLEAN )
        if [ "${snapshot_location}" != "NONE" ]; then
            #unmount snapshot. Provide <directory path>
            umount "${snapshot_location}"
        fi
        #remove all directories/files recursively
        if [ "${backup_vm_path}" != "/" ]; then
            rm -rf "${backup_vm_path}" 2>/dev/null
        fi
        ;;
    * )
    exit 1
esac
