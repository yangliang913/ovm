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
# author : Convirt Team
#

#echo "Invoked with ", $*
# parse the command line parameters
while getopts i:v:l:s:b:d:p:r:g:t:f:c: a
do case "$a" in
    i)ipv4_info="$OPTARG";;
    v)vlan_info="$OPTARG";;
    l)logfilename="$OPTARG" ;;
    s)script_loc="$OPTARG" ;;
    b)bridge_info="$OPTARG";;
    d)dhcp_info="$OPTARG";;
    p)public_ip="$OPTARG" ;;
    r)private_ip="$OPTARG" ;;
    g)b_name="$OPTARG" ;;
    t)public_interface="$OPTARG" ;;
    f)add_flag="$OPTARG" ;;
    c)command="$OPTARG" ;;
    * )
    echo "$OPTARG" ;;
   esac
done

# source common files
common_scripts=$script_loc/../../common/scripts
# source "$common_scripts/utils"
# source "$common_scripts/functions"
source "$common_scripts/nw_functions"

#vlan_info
parse_field_values $vlan_info 'vlan_id'
vlan_id=$value
parse_field_values $vlan_info 'interface'
interfaceName=$value
#ipv4_info
parse_field_values $ipv4_info 'ip_network'
ip_network=$value
#dhcp_info
parse_field_values $dhcp_info 'dhcp_start'
dhcp_start=$value
parse_field_values $dhcp_info 'dhcp_end'
dhcp_end=$value
#bridge_info
parse_field_values $bridge_info 'name'
bridge_name=$value
parse_field_values $bridge_info 'netmask'
netmask=$value
parse_field_values $bridge_info 'ip_address'
ip_address=$value

echo "DateTime: $(date)" >>$logfilename
echo $ip_network $intefaceName $logfilename $script_loc $bridge_name $netmask $ip_address $dhcp_start $dhcp_end >>$logfilename
echo $public_ip $private_ip $public_interface $bridge_name $logfilename $script_loc >>$logfilename

# source common files
common_scripts=$script_loc/../../common/scripts
source "$common_scripts/utils"
source "$common_scripts/functions"
source "$common_scripts/nw_functions"

# validate params
case "$command" in
    DNS_SERVICE )
        if [ "$bridge_name" == "" ]; then
            echo "ERROR:The required parameter bridge name is missing."
            exit 1
        fi
        if [ "$ip_network" == "" ]; then
            echo "ERROR:The required parameter IP is missing."
            exit 1
        fi
        if [ "$interfaceName" == "" ]; then
            echo "ERROR:The required parameter interface name is missing."
            exit 1
        fi
        if [ "$ip_address" == "" ]; then
            echo "ERROR:The required parameter ip address is missing."
            exit 1
        fi
        if [ "$dhcp_start" == "" ]; then
            echo "ERROR:The required parameter dhcp start is missing."
            exit 1
        fi
        if [ "$dhcp_end" == "" ]; then
            echo "ERROR:The required parameter dhcp end is missing."
            exit 1
        fi
        if [ "$vlan_id" == "" ]; then
            echo "ERROR:The required parameter vlan id is missing."
            exit 1
        fi
        ;;
    MANAGE_PUBLIC_IP  )
        if [ "$public_ip" == "" ]; then
            echo "ERROR:The required parameter public ip is missing."
            exit 1
        fi
        
        if [ "$private_ip" == "" ]; then
            echo "ERROR:The required parameter private ip is missing."
            exit 1
        fi
        
        if [ "$public_interface" == "" ]; then
            echo "ERROR:The required parameter public interface is missing."
            exit 1
        fi
        if [ "$b_name" == "" ]; then
            echo "ERROR:The required parameter bridge name is missing."
            exit 1
        fi
        ;;
    * )
    exit 1
    ;;
esac

case "$command" in
    MANAGE_PUBLIC_IP )
        manage_public_ip "$public_ip" "$private_ip" "$public_interface" "$b_name" "$add_flag"
        ;;
    DNS_SERVICE )
        setup_dns_service "$bridge_name" "$ip_network" "$interfaceName" "$ip_address" "$dhcp_start" "$dhcp_end" "$vlan_id" "$netmask"
        ;;
    * )
    exit 1
    ;;
esac
