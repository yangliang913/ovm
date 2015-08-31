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
while getopts d:m:v:t:o: a
do case "$a" in
    d)  disk="$OPTARG";;        #file path
    m)  mountdir="$OPTARG";;    #dir path
    v)  device="$OPTARG";;
    t)  file_system="$OPTARG";;
    o)  command="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done

case "$command" in
    CONTENT_MOUNT )
#         output=`losetup "${device}" "${disk}"`
#         echo "output = ${output}"
#         if [ "${output}" != "" ]; then
#             echo "Inside the if loop"
#             output=`umount "${device}"`
#             output=`losetup -d "${device}"`
#             output=`losetup "${device}" "${disk}"`
#         fi
#         mount "${device}" "${mountdir}"
        fs=""
        if [ "${file_system}" == "NONE" ]; then
            mount "${disk}" "${mountdir}"
        else
            get_ntfs_fs_system
            #we have added file_system and changed the mount command for ntfs (ntfs-3g) file system.
            output=`mount -t "${fs}" "${disk}" "${mountdir}"`
        fi
        ;;
    CONTENT_UMOUNT )
#         #output=`umount ${mountdir}`
#         output=`umount "${device}"`
#         echo "output = ${output}"
#         output=`losetup -d "${device}"`
#         echo "output = ${output}"
        umount "${disk}"
        ;;
    * )
    exit 1
esac