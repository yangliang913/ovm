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

function get_ntfs_fs_system
{
    echo "Getting file system..."
    if [ -x /sbin/mount.ntfs ]; then
        fs='ntfs'
    elif [ -x /sbin/mount.ntfs-3g ]; then
        fs='ntfs-3g'
    else
        echo "Could not find mount.ntfs, please validate that ntfs-3g package is installed."
        return 1
    fi
    echo "file system is '$fs'"
    return 0
}

# parse the command line parameters
while getopts s:d:v:o:m:f:l:t: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;
    v)  backup_vm_path="$OPTARG";;
    m)  device_name="$OPTARG";;
    f)  snapshot_file="$OPTARG";;
    l)  logical_volume="$OPTARG";;
    t)  file_system="$OPTARG";;
    o)  command="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done

fs=""
#mount <device> <mount directory>
if [ "${file_system}" == "NONE" ]; then
    output=`mount -r "${source}" "${destination}"`
else
    get_ntfs_fs_system
    #we have added file_system and changed the mount command for ntfs (ntfs-3g) file system.
    output=`mount -rt "${fs}" "${source}" "${destination}"`
fi

# #check the exit_code of command executed is not equal 0
# if [ $? -ne 0 ]; then
# 
#     #check the exit_code of command executed is less than or equal to 0
#     while [ $? -le 0 ];
#     do
#         #umount the device
#         output=`umount "${source}"`
#     done
# #mount the device
# output=`mount -r "${source}" "${destination}"`
# fi
