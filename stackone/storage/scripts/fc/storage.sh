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


declare -a devarr
declare -a mpatharr
declare -a uniq_arr
function get_mp_map()
{
    let count=0
    tmpfile=`mktemp`
    multipath -ll > $tmpfile
    while read line
    do
        if echo $line | grep -q 'dm-[0-9][0-9]*'
        then
            mpath=`echo $line | sed 's/\s.*//' | sed 's/\(.*\)dm-[0-9][0-9]*/\1/'`
            #mpath=`echo $line | sed 's/\(.*\) \(dm-[0-9][0-9]*\).*/\2/'`
        elif echo $line | grep -q '[0-9]*:[0-9]*:[0-9]*:[0-9]* sd*'
        then
            dev=`echo $line | sed 's/\(.*\s\)\(sd[a-z][a-z]*\)\(\s.*\)/\2/'`
                devarr[$count]=$dev
                mpatharr[$count]=$mpath
               ((count++))
        fi
    done < $tmpfile
    rm $tmpfile
}


function get_map()
{
   for f in `ls /dev/disk/by-id/*`
   do
      if [ "" = "`echo $f | grep '\-part'`" ]; then
         echo "$f=`readlink -f $f`" 
      fi
   done
}


function get_path()
{
  map=$1
  device=$2

  # Check if this is part of multipath
  mpath=""
  for (( i = 0 ; i < ${#devarr[@]} ; i++ ))
  do
     if [ "$device" == "/dev/${devarr[$i]}" ]; then
        mpath=${mpatharr[$i]}
        break;
     fi
  done
  if [ "$mpath" != "" ]; then
     #uuid=/dev/mapper/${mpath};
     echo "/dev/mapper/${mpath}"
     return 0
  fi

  for map_entry in $map
  do
     p=${map_entry%%=*}
     d=${map_entry##*=}
     
     if [ "$d" == "$device" ]; then
        echo "$p"
        return 0
     fi
  done
  # path not found. Lets return the $device
  echo $device
  return 1
}

get_lun()
{
   hbtl=$1
   lun=${hbtl##*:}
   if [ "${lun:(-1)}" == "]" ]; then
      lun=${lun:0:${#lun}-1}
      echo $lun
   fi
}

function already_in_output()
{
   u_dev="$1"

   for (( i = 0 ; i < ${#uniq_arr[@]} ; i++ ))
   do
     if [ "$u_dev" == "${uniq_arr[$i]}" ]; then
        return 0
        break;
     fi
   done
   return 1
}


function get_disk_details()
{
    hbtl_spec=$1

    let u_count=0
    total=0
    map=`get_map`
    get_mp_map
    lsscsi $hbtl_spec | {
    while read line
    do
#       echo "LINE=$line"
      dev_type=`echo $line | awk '{ print $2 }'`
      if [ "$dev_type" != "disk" ]; then
         continue  # skip the storage controller
      fi
      
      dev=`echo $line | awk '{ print $NF }'`
      if [ "$dev" != "" ]; then
         # Get lun number
         hbtl=`echo $line | awk '{ print $1 }'`
         lun=`get_lun "$hbtl"`

         # get unique path
         dev_path=`get_path "$map" "$dev"`

         # get size in GB
         disk_size=`blockdev --getsize64 $dev`
         disk_size_in_GB=`echo "scale=2; $disk_size / 1024 /1024 /1024" | bc`

         state="unknown" # for now

         already_in_output "$dev_path"
         if [ "$?" == "1" ]; then
            uniq_arr[u_count]=$dev_path
            ((u_count++))
            echo "OUTPUT=OUTPUT|Target=$target|CurrentPortal=$portal|Lun=$lun|mount_point=${dev}|SIZE=$disk_size_in_GB|State=$state|uuid=$dev_path"
            total=`echo "$total + $disk_size_in_GB" | bc`
         fi
      fi
    done
    echo "SUMMARY=SUMMARY|TOTAL=${total}"
    }
}




# parse the command line parameters
while getopts t:o:p:c:s:l:w:r:d:y:z:f: a
do case "$a" in
    t)  storage_type="$OPTARG";;
    o)  command="$OPTARG";;
    c)  hbtl_spec="$OPTARG";;
    s)  script_loc="$OPTARG";;
    l)  logfilename="$OPTARG";;
    r)  store="$OPTARG";;
    d)  d_name="$OPTARG";;
    y)  d_type="$OPTARG";;
    z)  d_size="$OPTARG";;
    f)  fs_type="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done

# source common files
source "$script_loc/storage_functions"


# parse the host, bus/channel, target, lun specification 
parse_field_values $hbtl_spec 'host_adapter'
host_adapter=$value
parse_field_values $hbtl_spec 'bus_channel'
bus_channel=$value
parse_field_values $hbtl_spec 'target'
target=$value
parse_field_values $hbtl_spec 'lun'
lun=$value

# run prereqs
check_prerequisite '' 'lsscsi'
check_prerequisite '' 'blockdev'

# validate params
if [ "$storage_type" == "" ]; then
  echo "ERROR:The required parameter storage type is missing."
  exit 1
fi
if [ "$command" == "" ]; then
  echo "ERROR:The required parameter command is missing."
  exit 1
fi

if [ "$host_adapter" == "" ]; then
    echo "ERROR:The required parameter Host Adapter specification is missing."
    exit 1
fi
if [ "$bus_channel" == "" ]; then
    bus_channel="-"
fi
if [ "$target" == "" ]; then
    target="-"
fi
if [ "$lun" == "" ]; then
    lun="-"
fi

case "$storage_type" in
  fc )
    case "$command" in
      GET_DISKS | GET_DISKS_SUMMARY) 

                  get_disk_details "$host_adapter:$bus_channel:$target:$lun"   #"$hbtl_spec"
                  check_function_return_value "Unable to get disks for $host_adapter" #$hbtl_spec
                  ;;

      DETACH )
              # Nothing to do here for now.
               ;;

      ATTACH )
              # Nothing to do here for now.
              # may be do a rescan
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
          #echo "Usage: -t{fc} -o{GET_DISKS|DETACH|ATTACH}"
          exit 1
          ;;
  esac
esac
