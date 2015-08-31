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

        #purpose: get dev loop and dev mapper for the virtual disk
        #this will create mappers
        output=`kpartx -a "${disk}"`
        num=0
        for i in `kpartx "${disk}" print | awk '{print "mapper="$1 "|device=" $5}'`
        do
            #sequential number
            num=`echo "${num}+1" | bc`
            #partition number
            p_num=${part_num[${num}]}
            dev_mapper=`echo $i | awk -F'|' '{print $1}' | cut -d'=' -f2`
            dev_loop=`echo $i | awk -F'|' '{print $2}' | cut -d'=' -f2`
            echo "PART_DETAILS=PART_DETAILS|PART_NAME=P$p_num|DEV_MAPPER=/dev/mapper/$dev_mapper|DEV_LOOP=$dev_loop"
        done;
        ;;
    VG_SCAN )
        #make the volume groups visible
        output=`vgscan`
        ;;
    VG_ACTIVATE )
        #activate volume group
        output=`vgchange -ay "${volume_group}"`
        ;;
    *)
    exit 1
    ;;
esac
