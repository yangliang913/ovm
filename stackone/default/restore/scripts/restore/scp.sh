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
while getopts s:d:n:u:p:t:k:o: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;
    n)  server="$OPTARG";;
    u)  user_name="$OPTARG";;
    p)  password="$OPTARG";;
    t)  script_path="$OPTARG";;
    k)  use_key="$OPTARG";;
    o)  command="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done
read pass
case "$command" in
    SCP )
        if [ "${use_key}" == "NONE" ]; then
#            "${script_path}"/exp_scp "${source}" "${user_name}" "${server}" "${destination}" "${password}" "${command}"
            if [ -e "${script_path}"/exp_scp.py ]; then
                echo $pass | python "${script_path}"/exp_scp.py "${source}" "${user_name}" "${server}" "${destination}" "${command}"
            else
                echo $pass | python "${script_path}"/exp_scp.pyc "${source}" "${user_name}" "${server}" "${destination}" "${command}"
            fi
        else
            scp -prq "${user_name}"@"${server}":"${source}" "${destination}"
        fi
        ;;
    CONTENT_SCP )
        if [ "${use_key}" == "NONE" ]; then
#            "${script_path}"/exp_scp "${source}" "${user_name}" "${server}" "${destination}" "${password}" "${command}"
            if [ -e "${script_path}"/exp_scp.py ]; then
                echo $pass | python "${script_path}"/exp_scp.py "${source}" "${user_name}" "${server}" "${destination}" "${command}"
            else
                echo $pass | python "${script_path}"/exp_scp.pyc "${source}" "${user_name}" "${server}" "${destination}" "${command}"
            fi
        else
            scp -r "${user_name}"@"${server}":"${source}" "${destination}"
        fi
        ;;
    * )
    exit 1
esac
