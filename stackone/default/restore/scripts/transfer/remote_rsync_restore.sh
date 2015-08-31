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

# parse the command line parameters
while getopts s:d:n:u:p:t:o:k: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;
    n)  server="$OPTARG";;
    u)  user_name="$OPTARG";;
    p)  password="$OPTARG";;
    t)  script_path="$OPTARG";;
    o)  command="$OPTARG";;
    k)  use_key="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done
read pass
if [ "${use_key}" == "NONE" ]; then
#    output=`"${script_path}"/exp_rsync_restore "${user_name}" "${server}" "${source}" "${destination}" "${password}"`
    if [ -e "${script_path}"/exp_rsync_restore.py ]; then
        output=`echo $pass | python "${script_path}"/exp_rsync_restore.py "${user_name}" "${server}" "${source}" "${destination}"`
    else
        output=`echo $pass | python "${script_path}"/exp_rsync_restore.pyc "${user_name}" "${server}" "${source}" "${destination}"`
    fi
else
    output=`rsync -avb "${user_name}"@"${server}":"${source}" "${destination}"`
fi
echo "${output}"
