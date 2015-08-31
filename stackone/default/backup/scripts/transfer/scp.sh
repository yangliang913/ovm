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
while getopts s:d:n:u:p:o:t:f:i:k:r: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;
    n)  server="$OPTARG";;
    u)  user_name="$OPTARG";;
    p)  password="$OPTARG";;
    t)  script_path="$OPTARG";;
    f)  full_bk_dest="$OPTARG";;
    i)  options="$OPTARG";;
    o)  command="$OPTARG";;
    k)  use_key="$OPTARG";;
    r)  ssh_port="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done
read pass

if [ "${options}" == "NONE" ]; then
    options=""
fi

if [ "${use_key}" == "NONE" ]; then
 #   "${script_path}"/exp_scp "${source}" "${user_name}" "${server}" "${destination}" "${password}" "${options}"
    if [ -e "${script_path}"/exp_scp.py ]; then
        echo $pass | python "${script_path}"/exp_scp.py "${source}" "${user_name}" "${server}" "${destination}" "${ssh_port}" "${options}"
    else
        echo $pass | python "${script_path}"/exp_scp.pyc "${source}" "${user_name}" "${server}" "${destination}" "${ssh_port}" "${options}"
    fi
else
    scp -prq -P "${ssh_port}" "${options}" "${source}" "${user_name}"@"${server}":"${destination}"
fi
