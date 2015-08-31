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
while getopts d:n:u:p:t:r: a
do case "$a" in
    d)  destination="$OPTARG";;
    n)  server="$OPTARG";;
    u)  user_name="$OPTARG";;
    p)  password="$OPTARG";;
    t)  script_path="$OPTARG";;
    r)  ssh_port="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done
read pass

#output=`"${script_path}"/exp_du "${user_name}" "${server}" "${destination}" "${password}" 2> "/dev/null"| grep total | awk '{print $1}'`
if [ -e "${script_path}"/exp_du.py ]; then
    output=`echo $pass | python "${script_path}"/exp_du.py "${user_name}" "${server}" "${destination}" "${ssh_port}" 2> "/dev/null"| grep total | awk '{print $1}'`
else
    output=`echo $pass | python "${script_path}"/exp_du.pyc "${user_name}" "${server}" "${destination}" "${ssh_port}" 2> "/dev/null"| grep total | awk '{print $1}'`
fi
#output none type check is to avoid "(standard_in) 1: parse error"
if [ "${output}" == "" ]; then
    output=0
fi
output=`echo "scale=2; $output/1024/1024/1024" | bc`
echo "${output}"




