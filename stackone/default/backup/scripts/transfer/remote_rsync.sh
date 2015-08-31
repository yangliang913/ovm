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
while getopts s:d:n:u:p:o:t:f:c:i:k:r: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;
    n)  server="$OPTARG";;
    u)  user_name="$OPTARG";;
    p)  password="$OPTARG";;
    t)  script_path="$OPTARG";;
    f)  prev_bk_path="$OPTARG";;
    c)  cur_bk_path="$OPTARG";;
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
if [ "${prev_bk_path}" != "NONE" ]; then
    if [ "${use_key}" == "NONE" ]; then
#         cp_output=`"${script_path}"/exp_link_cp "${user_name}" "${server}" "${prev_bk_path}" "${cur_bk_path}" "${password}"`
        if [ -e "${script_path}"/exp_link_cp.py ]; then
            cp_output=`echo $pass | python "${script_path}"/exp_link_cp.py "${user_name}" "${server}" "${prev_bk_path}" "${cur_bk_path}"`
        else
            cp_output=`echo $pass | python "${script_path}"/exp_link_cp.pyc "${user_name}" "${server}" "${prev_bk_path}" "${cur_bk_path}"`
        fi
    else
        cp_output=`ssh "${user_name}"@"${server}" cp -al "${source}" "${destination}" "${password}"`
    fi
    #check the exit_code of command executed is not equal 0
    if [ $? -ne 0 ]; then
        exit 1
    fi
fi

if [ "${use_key}" == "NONE" ]; then
    if [ "${options}" == "NONE" ]; then
#        rsync_output=`"${script_path}"/exp_rsync2 "${source}" "${user_name}" "${server}" "${destination}" "${password}"`
         if [ -e "${script_path}"/exp_rsync2.py ]; then
            rsync_output=`echo $pass | python "${script_path}"/exp_rsync2.py "${source}" "${user_name}" "${server}" "${destination}" "${ssh_port}"`
         else
            rsync_output=`echo $pass | python "${script_path}"/exp_rsync2.pyc "${source}" "${user_name}" "${server}" "${destination}" "${ssh_port}"`
         fi
    else
#        rsync_output=`"${script_path}"/exp_rsync2 "${source}" "${user_name}" "${server}" "${destination}" "${password}" "${options}"`
         if [ -e "${script_path}"/exp_rsync2.py ]; then
            rsync_output=`echo $pass | python "${script_path}"/exp_rsync2.py "${source}" "${user_name}" "${server}" "${destination}" "${ssh_port}" "${options}"`
         else
            rsync_output=`echo $pass | python "${script_path}"/exp_rsync2.pyc "${source}" "${user_name}" "${server}" "${destination}" "${ssh_port}" "${options}"`
         fi
    fi
else
    if [ "${options}" == "NONE" ]; then
        rsync_output=`rsync -avb --port="${ssh_port}" "${source}" "${user_name}"@"${server}":"${destination}" "${password}"`
    else
        rsync_output=`rsync -avb --port="${ssh_port}" "${options}" "${source}" "${user_name}"@"${server}":"${destination}" "${password}"`
    fi
fi
echo "${rsync_output}"
