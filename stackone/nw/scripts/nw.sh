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

#echo "Invoked with ", $*
# parse the command line parameters
while getopts t:v:i:p:d:n:l:o:s:b:r: a
do case "$a" in
        t)      network_type="$OPTARG";;
        v)      vlan_info="$OPTARG";;
        i)      ipv4_info="$OPTARG";;
        p)      bondinfo="$OPTARG" ;;
        d)      dhcp_info="$OPTARG";;
        n)      nat_info="$OPTARG";;
        l)      logfilename="$OPTARG" ;;
        o)      command="$OPTARG" ;;
        s)      script_loc="$OPTARG" ;;
        b)      bridge_info="$OPTARG";;
        r)      node_ip_address="$OPTARG";;
      * )
          echo "$OPTARG"
          ;;
   esac
done
echo "DateTime: $(date)" >>$logfilename
echo $script_loc
echo $network_type $ip_network $ip_address $dhcp_start $dhcp_end $intefaceName $bridge_name >>$logfilename

# source common files
common_scripts=$script_loc/../../common/scripts
source "$common_scripts/utils"
source "$common_scripts/functions"
source "$common_scripts/nw_functions"
detect_distro
if [ "$?" != "0" ]; then
   echo "Error detecting Linux distribution.Exiting."
   exit 1
fi

#vlan_info
parse_field_values $vlan_info 'vlan_id'
vlan_id=$value
parse_field_values $vlan_info 'interface'
interfaceName=$value
#ipv4_info
parse_field_values $ipv4_info 'ip_network'
ip_network=$value
parse_field_values $ipv4_info 'gateway'
gateway=$value
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
#nat_info
parse_field_values $nat_info 'interface'
nat_interface=$value

# dump information
echo "DISTRO ${DIST}" >>$logfilename
echo "VER ${VER}" >>$logfilename
echo "CODENAME ${CODE_NAME}" >>$logfilename
echo "KERNEL ${KERNEL}" >>$logfilename
echo "ARCH ${ARCH}" >>$logfilename

if [ "$dhcp_start" == "" ]; then
    dhcp_start="NONE"
fi
if [ "$dhcp_end" == "" ]; then
    dhcp_end="NONE"
fi

# include the distro specific file if it exists.
distro_functions=$common_scripts/${DIST}_functions
if [ -r $distro_functions ]; then
    echo "Info: Sourcing $distro_functions"
    source $distro_functions >>$logfilename
else
   echo "Info: $distro_functions not found." >>$logfilename
fi



NETWORK_CONF_FILE=$script_loc/../../networks/privatenw.conf

add_bridge_information() {
  if [ ! -e "$NETWORK_CONF_FILE" ]; then
    mkdir -p `dirname $NETWORK_CONF_FILE`
    touch $NETWORK_CONF_FILE 
  fi
  #when virtual network would be added using interface and vlan id then ip_network would be blank and also below mentioned fields would be blank.
  if [ `grep -c1 "$bridge_name" $NETWORK_CONF_FILE` -eq 0 ]; then
    if [ "$dhcp_start" == "NONE" ] && [ "$dhcp_end" == "NONE" ]; then
        echo "BRIDGE_NAME=$bridge_name;IP_NETWORK=$ip_network;IP_ADDRESS=$ip_address;DHCP_START=;DHCP_END=;NET_MASK=$netmask;GATEWAY=$gateway;INTERFACE_NAME=$interfaceName;VLAN_ID=$vlan_id"  >> $NETWORK_CONF_FILE

    else
        echo "BRIDGE_NAME=$bridge_name;IP_NETWORK=$ip_network;IP_ADDRESS=$ip_address;DHCP_START=$dhcp_start;DHCP_END=$dhcp_end;NET_MASK=$netmask;GATEWAY=$gateway;INTERFACE_NAME=$interfaceName;VLAN_ID=$vlan_id"  >> $NETWORK_CONF_FILE
    fi
  fi
}
remove_bridge_information() {
  if [  -e $NETWORK_CONF_FILE ]; then
    if [ `grep -c1 "$bridge_name" $NETWORK_CONF_FILE` -eq 1 ]; then 
      cp $NETWORK_CONF_FILE $NETWORK_CONF_FILE.orig
      sed "/BRIDGE_NAME=$bridge_name/d" < $NETWORK_CONF_FILE > $NETWORK_CONF_FILE.new
      mv $NETWORK_CONF_FILE.new $NETWORK_CONF_FILE
      rm $NETWORK_CONF_FILE.orig
    fi
  fi
}

# validate params
if [ "$network_type" == "" ]; then
  echo "ERROR:The required parameter network type is missing."
  exit 1
fi
if [ "$command" == "" ]; then
  echo "ERROR:The required parameter command is missing."
  exit 1
fi

exit_code=""

case "$command" in
  GET_DETAILS )
    case "$network_type" in
      HOST_PRIVATE_NW ) 
                  bridges=`brctl show | awk '{print $1=$4}'`
                  ;;
       PUBLIC_NW ) 
               ;;
    esac
    ;;
  ATTACH )
    case "$network_type" in
      HOST_PRIVATE_NW ) 
              check_prerequisite '' 'brctl'
              check_prerequisite '' 'dnsmasq'
              setup_privatenw "$bridge_name" "$ip_network" "$ip_address" "$dhcp_start" "$dhcp_end" "$netmask" "$gateway" "$interfaceName" "$logfileName" "$vlan_id"
              # add bridge information to the configuration file
              add_bridge_information
              ;;
      PUBLIC_NW ) 
               ;;

      VLAN_NW ) #this would be called on associate with SP
            check_prerequisite '' 'vconfig'
            check_prerequisite '' 'brctl'
            add_vlan "$interfaceName" "$vlan_id" "$bridge_name" "$ip_network" "$ip_address" "$netmask"
            # add bridge information to the configuration file
            add_bridge_information
            ;;
    esac
     ;;
  DETACH  )
    case "$network_type" in
      HOST_PRIVATE_NW ) 
              check_prerequisite '' 'brctl'
              remove_bridge_information
              remove_privatenw "$bridge_name" "$ip_network" "$ip_address" "$dhcp_start" "$dhcp_end" "$netmask" "$gateway" "$interfaceName" "$logfilename" "$vlan_id" "$node_ip_address"
            echo "exit_code is $exit_code"
            if [ "$exit_code" != "" ]; then
                exit $exit_code
            fi
              ;;
      PUBLIC_NW ) 
               ;;

      VLAN_NW ) #this would be called on disassociate from SP
            check_prerequisite '' 'vconfig'
            check_prerequisite '' 'brctl'
            remove_bridge_information
            remove_vlan "$interfaceName" "$vlan_id" "$bridge_name" "$ip_address" "$node_ip_address"
            echo "exit_code is $exit_code"
            if [ "$exit_code" != "" ]; then
                exit $exit_code
            fi
            ;;
    esac
   ;;
esac
