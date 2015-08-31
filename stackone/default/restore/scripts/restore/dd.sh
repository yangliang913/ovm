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
    DD )
        output=`dd bs=4096k if="${source}" of="${destination}"`
        if [ "${output}" != "" ]; then
            echo "${output}"
            exit 1
        fi
        ;;
    DD_LOCAL )
        output=`dd bs=4096k if="${source}" of="${destination}"`
        if [ "${output}" != "" ]; then
            echo "${output}"
            exit 1
        fi
        ;;
    DD_REMOTE )
        if [ "${use_key}" == "NONE" ]; then
#            "${script_path}"/exp_dd bs=4096k "${source}" "${user_name}" "${server}" "${destination}" "${password}"
            if [ -e "${script_path}"/exp_dd.py ]; then
                echo $pass | python "${script_path}"/exp_dd.py "${source}" "${user_name}" "${server}" "${destination}"
            else
                echo $pass | python "${script_path}"/exp_dd.pyc "${source}" "${user_name}" "${server}" "${destination}"
            fi
        else
            output=`ssh "${user_name}"@"${server}" dd bs=4096k if="${source}"|dd bs=4096k of="${destination}"`
            echo "${output}"
        fi
        ;;
    * )
    exit 1
esac