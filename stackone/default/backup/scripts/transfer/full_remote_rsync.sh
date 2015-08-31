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
while getopts s:d:n:u:p:t:i:k:r: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;
    n)  server="$OPTARG";;
    u)  user_name="$OPTARG";;
    p)  password="$OPTARG";;
    t)  script_path="$OPTARG";;
    i)  options="$OPTARG";;
    k)  use_key="$OPTARG";;
    r)  ssh_port="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done
read pass
if [ "${use_key}" == "NONE" ]; then
    if [ "${options}" == "NONE" ]; then
        #output=`"${script_path}"/exp_full_rsync "${source}" "${user_name}" "${server}" "${destination}" "${password}"`
        if [ -e "${script_path}"/exp_full_rsync.py ]; then
            output=`echo $pass | python "${script_path}"/exp_full_rsync.py "${source}" "${user_name}" "${server}" "${destination}" "${ssh_port}"`
        else
            output=`echo $pass | python "${script_path}"/exp_full_rsync.pyc "${source}" "${user_name}" "${server}" "${destination}" "${ssh_port}"`
        fi
    else
#        output=`"${script_path}"/exp_full_rsync "${source}" "${user_name}" "${server}" "${destination}" "${password}" "${options}"`
        if [ -e "${script_path}"/exp_full_rsync.py ]; then
            output=`echo $pass | python "${script_path}"/exp_full_rsync.py "${source}" "${user_name}" "${server}" "${destination}" "${ssh_port}" "${password}" "${options}"`
        else
            output=`echo $pass | python "${script_path}"/exp_full_rsync.pyc "${source}" "${user_name}" "${server}" "${destination}" "${ssh_port}" "${password}" "${options}"`
        fi
    fi
else
    if [ "${options}" == "NONE" ]; then
        output=`rsync -avb --port="${ssh_port}" "${source}" "${user_name}"@"${server}":"${destination}"`
    else
        output=`rsync -avb --port="${ssh_port}" "${options}" "${source}" "${user_name}"@"${server}":"${destination}"`
    fi
fi
echo "${output}"