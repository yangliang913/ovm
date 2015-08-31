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
while getopts s:d:v:m:n:u:p:t:o:z: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;
    v)  backup_vm_path="$OPTARG";;
    m)  vm_name="$OPTARG";;
    n)  server="$OPTARG";;
    u)  user_name="$OPTARG";;
    p)  password="$OPTARG";;
    t)  script_path="$OPTARG";;
    z)  snapshot_size="$OPTARG";;
    o)  command="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done

#create snapshot volume
#lvcreate -L<size><unit> -s -n <New logical volume name> <existing logical volume path>
lvcreate -L"${snapshot_size}" -s -n "${vm_name}" "${source}"
#mkfs.ext3 <newly created logical volume path>
#mkfs.ext3 ${destination}"/"${vm_name}
