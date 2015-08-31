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
# This software is subject to the GNU General Public License, Version 2 (GPLv2)
# and for details, please consult it at:
#
#    http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
# 
#
# author : mkelkar@users.sourceforge.net
#



# parse the command line parameters
while getopts t:o:p:c:s:l:w:r:d:y:z:f: a
do case "$a" in
        t)      storage_type="$OPTARG";;
        o)      command="$OPTARG";;
        p)      usernameAndpassword="$OPTARG"
                ;;
        c)      serverAndstorageTarget="$OPTARG"
                ;;
	s)      script_loc="$OPTARG"
                ;;
        l)      logfilename="$OPTARG"
                ;;
        w)      fileFilter="$OPTARG"
                ;;
        r)      store="$OPTARG";;
        d)      d_name="$OPTARG";;
        y)      d_type="$OPTARG";;
        z)      d_size="$OPTARG";;
        f)      fs_type="$OPTARG";;
      * )
          echo "$OPTARG"
          ;;
        esac
done

# source common files
source "$script_loc/storage_functions"

check_prerequisite '' 'aoe-stat'

echo "$command $storage_type $username $password $server $target" >>$logfilename

if [ "$command" == "" ]; then
  echo "ERROR:The required parameter command is missing."
  exit 1
fi



case "$storage_type" in
  aoe )
    case "$command" in
      GET_DISKS | GET_DISKS_SUMMARY) output=`aoe-stat | awk '{print "OUTPUT=OUTPUT|uuid=/dev/etherd/"$1"|SIZE="$2"|INTERFACENAME="$3"|State="$4"\r\n"}' | sed 's/SIZE=\(.*\)GB/SIZE=\1/'`
                  check_function_return_value "Unable to get stat:$output"
                  echo $output
                  #;; Fall through
       #GET_DISKS_SUMMARY) 
                  total=0
                  for size in `aoe-stat | awk '{print $2}' | sed 's/GB//'`
                  do 
                    total=`echo $total + $size | bc`
                  done
                  echo "SUMMARY=SUMMARY|TOTAL=${total}"
                  ;;
      DETACH ) 
                  ;;
      ATTACH ) 
               ;;
        CREATE )
            common_loc="$store"/common
            
            # source common files
            source "$common_loc"/defs
            source "$common_loc"/functions

            if [ -z "$d_name" ]; then
                echo "Disk name not specified" >>$logfilename
                exit 1
            fi
            if [ -z "$d_type" ]; then
                d_type="file"
            fi
            if [ -z "$d_size" ]; then
                echo "Disk size not specified" >>$logfilename
                exit 1
            fi
            
            echo "create_disk $d_type $d_name $d_size " >>$logfilename
            create_disk "$d_type" "$d_name" "$d_size"
            
            # raw disk created now lets see if we need to create a fs
            if [ -n "$fs_type" ]; then
                make_fs "$d_name" "$fs_type"
                if [ ! "$?" = "0" ]; then
                    echo "Error creating $fs_type file system on $d_name" >>$logfilename
                    exit 1
                fi
                echo "File system $fs_type is created on $d_name" >>$logfilename
            fi
            ;;
        REMOVE )
            common_loc="$store"/common
            
            # source common files
            source "$common_loc"/defs
            source "$common_loc"/functions
            
            if [ -z "$d_name" ]; then
                echo "Disk name not specified" >>$logfilename
                exit 1
            fi
            if [ -z "$d_type" ]; then
                d_type="file"
            fi
            
            echo "remove_disk $d_type $d_name" >>$logfilename
            remove_disk "$d_type" "$d_name"
            ;;
      * )
          echo "Usage: -t{aoe} -o{GET_DISKS|DETACH|ATTACH}"
          exit 1
          ;;
  esac
esac
