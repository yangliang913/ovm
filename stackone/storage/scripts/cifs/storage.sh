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
function remove_mount
{
    echo "Removing entry from fstab..."
    temp_share=//"${server}"/"${share}"
    sed -i "s|${temp_share} ${mountpoint} ${storage_type} defaults||" /etc/fstab
}

function scan_disks
{
    for i in `find ${mountpoint} -type f -name "${fileFilter}" -printf "%p %k %s\n" 2>/dev/null | awk '{print "Disk="$1"|Used="$2"|Available="$3""}'`
    do
    disk_name=`echo $i | awk -F'|' '{print $1}' | cut -d'=' -f2`
    used_size=`echo $i | awk -F'|' '{print $2}' | cut -d'=' -f2`
    size=`echo $i | awk -F'|' '{print $3}' | cut -d'=' -f2`
    disk_size=`echo "scale=2; $size/1024/1024/1024" | bc`
    disk_used_size=`echo "scale=2; $used_size/1024/1024" | bc`
    echo "DISK_DETAILS=DISK_DETAILS|uuid=$disk_name|USED=$disk_used_size|SIZE=$disk_size"
    done;
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

parse_field_values $mountParams 'server'
server=$value
parse_field_values $mountParams 'mount_point'
mountpoint=$value
parse_field_values $mountParams 'windows_share'
share=$value
parse_field_values $mountParams 'windows_username'
win_username=$value
parse_field_values $mountParams 'windows_password'
win_password=$value
parse_field_values $mountParams 'domain'
domain=$value

check_prerequisite '' 'df'

echo "DateTime: $(date)" >>$logfilename
echo "$command $storage_type $server $share $mountpoint $win_username $win_password $domain" >>$logfilename

isRequiedParamPresent ${command} 'command'

case "$storage_type" in
    cifs )
    case "$command" in

        GET_DISKS | GET_DISKS_SUMMARY ) output=`df --block-size=G | grep -v "Used" |  awk '{ if (NF == 1)  printf("%s ", $0); else print;}' |   grep -w ${server} | awk '{ if ($6 == "'${mountpoint}'") print; }' |  awk '{sub(/G/,"",$2); sub(/G/,"",$3); sub(/G/,"",$4); print "OUTPUT=OUTPUT|FILESYSTEM="$1"|SIZE="$2"|USED="$3"|AVAILABLE="$4"|MOUNT="$6""}'`
            if [ "${output}" = "" ]; then
                echo $output
                exit 1
            fi
            echo $output
            scan_disks
            total=0
            output=`df --block-size=G | grep -v "Used" |  awk '{ if (NF == 1)  printf("%s ", $0); else print;}' |   grep -w ${server} | awk '{ if ($6 == "'${mountpoint}'") print; }' |  awk '{sub(/G/,"",$2); sub(/G/,"",$3); sub(/G/,"",$4); print "SUMMARY=SUMMARY|TOTAL="$2""}'`
            echo $output
            ;;
        DETACH ) umount ${mountpoint}
                 remove_mount
                ;;
        ATTACH ) #check whether mountpoint exists or not, if not then mount storage.
                temp_share=//"${server}"/"${share}"
                output=`mount | awk '{if ($1 == "'${temp_share}'" && $3 == "'${mountpoint}'") print;}'`
                if [ "${output}" == "" ] ; then
                    echo "Mounting cifs storage..."
                    mount -t ${storage_type} //${server}/${share} ${mountpoint} -o username=${win_username},password=${win_password},domain=${domain}

                    #check mountpoint entry in fstab
                    output=`grep "'${temp_share}'" /etc/fstab | awk '{if($2 == "'${mountpoint}'") print};'`
                    if [ "${output}" == "" ] ; then
                        #add to fstab
                        echo "Adding entry to fstab..."
                        echo "${temp_share} ${mountpoint} ${storage_type} defaults" >> /etc/fstab
                    fi
                else
                    echo "cifs storage already mounted..."
                fi
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
        echo "Usage: -t{cifs} -o{GET_DISKS|DETACH|ATTACH}"
        exit 1
        ;;
  esac
esac
