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
while getopts v:s:m:d:g:o: a
do case "$a" in
    v)  backup_vm_path="$OPTARG";;
    s)  snapshot_file="$OPTARG";;
    m)  mount_dir="$OPTARG";;
    d)  disk="$OPTARG";;
    g)  volume_group="$OPTARG";;
    o)  command="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done

case "$command" in
    UMOUNT_SNAPSHOT )
        if [ "${snapshot_file}" != "NONE" ]; then
            #unmount snapshot. Provide <snapshot file path>
            umount "${snapshot_file}"
            #remove logical volume. Provide <snapshot file path>
            lvremove -f "${snapshot_file}"
        fi
        ;;
    UMOUNT_DEVICE )
        output=`umount "${mount_dir}"`
        echo "output=${output}"
        ;;
    DETACH_VOL_GROUP )
        #dactivate volume groups
        vgchange -an "${volume_group}"
        ;;
    REMOVE_MAPPER )
        #remove dev loop and dev mappers
        kpartx -d "${disk}"
        ;;
    CLEAN )
        if [ "${backup_vm_path}" != "NONE" ]; then
            #remove all directories/files recursively
            if [ "${backup_vm_path}" != "/" ]; then
                rm -rf "${backup_vm_path}" 2> /dev/null
            fi
        fi
        ;;
    * )
    exit 1
esac
