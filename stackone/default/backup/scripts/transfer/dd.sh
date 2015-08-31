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
while getopts s:d:n:u:p:o:t:f:z:v:m: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;
    n)  server="$OPTARG";;
    u)  user_name="$OPTARG";;
    p)  password="$OPTARG";;
    t)  script_path="$OPTARG";;
    f)  full_bk_dest="$OPTARG";;
    z)  snapshot_size="$OPTARG";; 
    o)  command="$OPTARG";;
    v)  backup_vm_path="$OPTARG";;
    m)  vm_name="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done

dd bs=4096k if="${source}" of="${destination}"
