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
while getopts s:d:f:c:i: a
do case "$a" in
    s)  source="$OPTARG";;
    d)  destination="$OPTARG";;  
    f)  prev_bk_path="$OPTARG";;
    c)  cur_bk_path="$OPTARG";;
    i)  options="$OPTARG";; 
    * )
    echo "$OPTARG"
    ;;
    esac
done
	


#backup operation
#if [${full_bk_dest}]; then
	#echo "backup"

	# step 1: make a hard-link-only (except for dirs) copy of the latest snapshot,
	# if that exists
    if [ "${prev_bk_path}" != "NONE" ]; then
        cp_output=`cp -al "${prev_bk_path}" "${cur_bk_path}" ;`
        if [ "${cp_output}" != "" ]; then
            echo "Error: ${cp_output}"
            exit 1
        fi
    fi

	# step 2: rsync from the system into the latest snapshot (notice that
	# rsync behaves like cp --remove-full_bk_dest by default, so the full_bk_dest
	# is unlinked first.  If it were not so, this would copy over the other
	# snapshot(s) too!

    if [ "${options}" == "NONE" ]; then
        options=""
        rsync_output=`rsync -avb --delete "${source}" "${destination}"`
        echo "${rsync_output}"
        exit
    fi
    
    rsync_output=`rsync -avb --delete "${options}" "${source}" "${destination}"`
    echo "${rsync_output}"
    exit

	#	-va --delete --delete-excluded				\
	#	--exclude-from="$EXCLUDES"				
	#	/root/Nandan ${full_bk_dest}/hourly_0/ ;
	#if [ "${rsync_output}" != "" ]; then
	#	echo ${rsync_output}
	#        exit 1
	#fi

	# step 2: update the mtime of hourly_0/ to reflect the snapshot time
	#$TOUCH ${full_bk_dest}/ ;

	#step3: hard-link-only (except for dirs) copy of the latest snapshot to user destination,
	#$CP -al ${full_bk_dest}/ ${destination}/ ;	



#restore operation
#else
	#echo "restore"
	#rsync_restore=`$RSYNC -va ${source} ${destination}/ ;`
	#if [ "${rsync_restore}" != "" ]; then
	#	echo ${rsync_restore}
	#        exit 1
	#fi

#fi


