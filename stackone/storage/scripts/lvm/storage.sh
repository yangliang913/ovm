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
function get_storage
{
    total_size=0
    for i in `lvs --nosuffix --units g ${volume_group} | grep -v "LSize" | awk '{sub(/G/,"",$4); print "OUTPUT=OUTPUT|VOLUME_GROUP="$2"|SIZE="$4"\n"}'`
    do
    v_group=`echo $i | awk -F'|' '{print $2}' | cut -d'=' -f2`
    size=`echo $i | awk -F'|' '{print $3}' | cut -d'=' -f2`
    total_size=`echo "scale=2; $total_size+$size" | bc`
    done;
    echo "OUTPUT=OUTPUT|VOLUME_GROUP=$v_group|SIZE=$total_size"
}

function get_disks
{
    for i in `lvs --nosuffix --units g ${volume_group} | grep -v "LSize" | awk '{sub(/G/,"",$4); print "DISK_DETAILS=DISK_DETAILS|LOGICAL_VOLUME="$1"|SIZE="$4"|uuid=/dev/"$2"/"$1"\n"}'`
    do
    logical_volume=`echo $i | awk -F'|' '{print $2}' | cut -d'=' -f2`
    size=`echo $i | awk -F'|' '{print $3}' | cut -d'=' -f2`
    uuid=`echo $i | awk -F'|' '{print $4}' | cut -d'=' -f2`
    echo "DISK_DETAILS=DISK_DETAILS|LOGICAL_VOLUME=$logical_volume|SIZE=$size|uuid=$uuid"
    done;
}

function get_summary
{
    total_size=0
    for i in `lvs --nosuffix --units g ${volume_group} | grep -v "LSize" | awk '{sub(/G/,"",$4); print "SUMMARY=SUMMARY|SIZE="$4"\n"}'`
    do
    size=`echo $i | awk -F'|' '{print $2}' | cut -d'=' -f2`
    total_size=`echo "scale=2; $total_size+$size" | bc`
    done;
    echo "SUMMARY=SUMMARY|TOTAL=$total_size"
}

while getopts t:o:p:c:s:l:w:r:d:y:z:f: a
do case "$a" in
    t)  storage_type="$OPTARG";;
    o)  command="$OPTARG";;
    p)  usernameAndpassword="$OPTARG";;
    c)  mountParams="$OPTARG";;
    l)  logfilename="$OPTARG";;
    s)  script_loc="$OPTARG";;
    w)  fileFilter="$OPTARG";;
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

parse_field_values $mountParams 'volume_group'
volume_group=$value

#check_prerequisite '' 'lvs'

echo "DateTime: $(date)" >>$logfilename
echo "$command $storage_type $volume_group" >>$logfilename

#isRequiedParamPresent ${command} 'command'

case "$storage_type" in 
    lvm )
    case "$command" in
        GET_DISKS | GET_DISKS_SUMMARY )
            output=`lvs ${volume_group}`
            if [ "${output}" = "" ]; then
                echo ${output}
                exit 1
            fi
            get_storage
            get_disks
            get_summary
            ;;
        ATTACH )
            #check whether the volume group is present or not. If not present then exit with 1.
            output=`vgs "${volume_group}" | grep -v "VG" | awk '{if ($1 != "") print;}'`
            if [ "${output}" != "" ] ; then
                echo "VolumeGroup exists..."
            else
                exit 1
            fi
            ;;
        DETACH )
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
                d_type="lvm"
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
                d_type="lvm"
            fi
            
            echo "remove_disk $d_type $d_name" >>$logfilename
            remove_disk "$d_type" "$d_name"
            ;;
        * )
        exit 1
    ;;
    esac
esac
