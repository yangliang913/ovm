#!/bin/bash

while getopts d:v:o: a
do case "$a" in
    d)  disk="$OPTARG";;
    v)  volume_group="$OPTARG";;
    o)  command="$OPTARG";;
    * )
    echo "$OPTARG"
    ;;
    esac
done

case "$command" in
    PART_DETAILS )
        #declare array
        declare -a part_num
        declare -a dev_map
        declare -a dev_loop
        #purpose: get dev loop and dev mapper for the virtual disk
        #this will create mappers
        output=`kpartx -a "${disk}"`
        num=0
        for i in `kpartx "${disk}" print | awk '{print "mapper="$1 "|device=" $5}'`
        do
            num=`echo "${num}+1" | bc`
            dev_mapper=`echo $i | awk -F'|' '{print $1}' | cut -d'=' -f2`
            dev_loop=`echo $i | awk -F'|' '{print $2}' | cut -d'=' -f2`

            #here storing data in array
            part_num[${num}]="${num}"
            dev_map[${num}]="${dev_mapper}"
            dev_loop[${num}]="${dev_loop}"
        done;

        #purpose: get partition details of virtual disks like number of partitions and partition type.
        #get partition details
        #"num" is a variable for keeping sequential number.
        #"number" is a variable for keeping partition numbers created by parted command.
        num=0
        for i in `parted "${disk}" print | grep -v "Flags" | awk '{print "number="$1 "|type="$5 "|file_system="$6 "|flags="$7}'`
        do
            number=`echo $i | awk -F'|' '{print $1}' | cut -d'=' -f2`
            type=`echo $i | awk -F'|' '{print $2}' | cut -d'=' -f2`
            file_system=`echo $i | awk -F'|' '{print $3}' | cut -d'=' -f2`
            flags=`echo $i | awk -F'|' '{print $4}' | cut -d'=' -f2`
            
            if [ "${file_system}" != "ext2" ] && [ "${file_system}" != "ext3" ] && [ "${file_system}" != "swap" ]; then
                flags=`echo $file_system ${flags}`
                file_system=""
            fi
            if [ "${number}" != "" ] && [ "${number}" != "Model:" ] && [ "${number}" != "Disk" ] && [ "${number}" != "Sector" ] && [ "${number}" != "Partition" ]; then
                #get data from array created in kpartx command
                num=`echo "${num}+1" | bc`
                dev_mapper=${dev_map[${num}]}
                dev_loop=${dev_loop[${num}]}
                echo "PART_DETAILS=PART_DETAILS|PART_NAME=P$number|TYPE=$type|FILE_SYSTEM=$file_system|FLAGS=$flags|DEV_MAPPER=/dev/mapper/$dev_mapper|DEV_LOOP=$dev_loop"
            fi
        done;
        ;;
    VG_DETAILS )
        #declare array
        declare -a part_num

        #get partition numbers
        num=0
        for i in `parted "${disk}" print | grep -v "Flags" | grep -v "Model:" | grep -v "Disk" | grep -v "Sector" | grep -v "Partition" | awk '{if ($1 != "") print "number="$1}'`
        do
            #sequential number
            num=`echo "${num}+1" | bc`
            #partition number
            number=`echo $i | awk -F'|' '{print $1}' | cut -d'=' -f2`

            #here storing data in array
            part_num[${num}]="${number}"
        done;

        #purpose: get volume groups used by virtual disk
        #this will create mappers
        #output=`kpartx -a "${disk}"`
        output=`vgscan`
        num=0
        #get dev mappers and loop through it
        for i in `kpartx "${disk}" | awk '{print $1}'`
        do
            num=`echo "${num}+1" | bc`
            p_num=${part_num[${num}]}
            #get volume group for the dev mapper
            for j in `pvs | grep -w "${i}" | awk '{print $2}'`
            do
                #check whether it is volume group or not
                output=`vgs "${j}"`
                if [ "${output}" != "" ]; then
                    echo "VG_DETAILS=VG_DETAILS|PART_NAME=P${p_num}|VG_NAME=${j}"
                fi
            done;
        done;
        ;;
    LV_DETAILS )
        #purpose: get logical volumes of the volume group
        #activate volume group
        output=`vgchange -ay "${volume_group}"`
        output=""
        #get logical volumes
        vg_path="/dev/${volume_group}/"
        for i in `lvscan | grep -w "/dev/${volume_group}/*" | sed 's|'$vg_path'||' | sed "s|'||" | sed "s|'||" | awk '{print $2}'`
        do
            echo "LV_DETAILS=LV_DETAILS|LV_NAME=${i}"
        done
        ;;
    *)
    exit 1
    ;;
esac
