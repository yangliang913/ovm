/*
*   stackone  -  Copyright (c) 2010 Cloud Corp.
*   ======

* stackone  is a Virtualization and Cloud Provider
   


* This software is subject to the GNU General Public License, Version 2 (GPLv2)
* and for details, please consult it at:

* http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
* author : Benf<yangbf@stackone.com.cn>
*/

var stackone={};

stackone.constants={
    DATA_CENTER : "DATA_CENTER",
    SERVER_POOL : "SERVER_POOL",
    MANAGED_NODE : "MANAGED_NODE",
    DOMAIN  : "DOMAIN",

    IMAGE_STORE : "IMAGE_STORE",
    IMAGE_GROUP : "IMAGE_GROUP",
    IMAGE : "IMAGE"

    ,MY_TEMPLATE:"MY_TEMPLATE"
    ,CLOUD_TEMP:"CLOUD_TEMPLATE"
    ,CLOUD_TMPGRP:"CLOUD_TMPGRP"
    ,TMP_LIB:"TMP_LIB"
    ,CLOUD_VM:"CLOUD_VM"
    ,VDC:"VDC"
    ,VDC_FOLDER:"VDC_FOLDER"
    ,VDC_VM_FOLDER:"VDC_VM_FOLDER"
    ,CLOUD_PROVIDER_FOLDER:"CLOUD_PROVIDER_FOLDER"
    ,CLOUD_PROVIDER:"CLOUD_PROVIDER"
    ,CPU : "CPU"
    ,MEM : "Memory"
    ,VMCPU : "VM CPU"
    ,STORAGE: 'Storage'
    ,METRIC_NETWORKIN:"Networkin"
    ,METRIC_NETWORKOUT:"Networkout"

    ,IAAS:"IaaS"

    ,VMW:"vmw"
    ,VCENTER:"vcenter"
    
    ,TOP5SERVERS:"TOP5SERVERS"
    ,TOP5VMS:"TOP5VMS"    	
    ,COMPARISONCHART:"COMPARISONCHART"

    ,DTD:"DTD"
    ,HRS12:"12HRS"
    ,HRS24:"24HRS"
    ,DAYS7:"7DAYS"
    ,DAYS30:"30DAYS"
    ,WTD:"WTD"
    ,MTD:"MTD"
    ,CUSTOM:"CUSTOM"

    ,VMS:"VMS"
    ,SERVERS:"SERVERS"


    ,RUNNING  : "0"
    ,BLOCKED  : "1"
    ,PAUSED   : "2"
    ,SHUTDOWN : "3"
    ,CRASHED  : "4"
    ,NOT_STARTED : "-1"
    ,UNKNOWN  : "-2"

    ,DOWN_RUNNING  : "D_0"
    ,DOWN_BLOCKED  : "D_1"
    ,DOWN_PAUSED  : "D_2"
    ,DOWN_SHUTDOWN  : "D_3"
    ,DOWN_CRASHED  : "D_4"
    ,DOWN_NOT_STARTED  : "D_-1"
    ,DOWN_UNKNOWN  : "D_-2"


    ,DWM_FREQUENCY:"5"
    ,DWM_THRESHOLD:"80"
    ,DWM_DATA_PERIOD:"5"
    ,DWM_PS_THRESHOLD:"10"

    ,TOP50BYCPU:"Top 50 Servers by Host CPU(%)"
    ,TOP50BYMEM:"Top 50 Servers by Host Memory(%)"
    ,DOWNSERVERS:"Down Servers"
    ,STANDBYSERVERS:"Standby Servers"

    ,TOP50BYCPUVM:"Top 50 VMs by CPU Util(%)"
    ,TOP50BYMEMVM:"Top 50 VMs by Memory Util(%)"
    ,DOWNVM:"Down VMs"
    ,RUNNINGVM:"Running VMs"

    ,POWER_SAVING : "POWER_SAVING"
    ,LOAD_BALANCING : "LOAD_BALANCING"

    ,POLICY_NAMES:{
        "POWER_SAVING":"Power Saving",
        "LOAD_BALANCING":"Even Distribution"
    }
    ,DWM: "DWM"

    ,SPECIAL_NODE:"SPECIAL_NODE"

    ,OUTSIDE_DOMAIN:"OUTSIDE"
    ,OS_FLAVORS:[
        ['Linux', 'Linux'],
        ['Windows', 'Windows']
    ]

    ,OS_NAMES :[
        ['SUSE', 'SUSE', 'Linux'],
        ['SLES', 'SLES', 'Linux'],
        ['CentOS', 'CentOS', 'Linux'],
        ['Ubuntu', 'Ubuntu', 'Linux'],
        ['RHEL', 'RHEL', 'Linux'],
        ['Debian', 'Debian', 'Linux'],
        ['Gentoo', 'Gentoo', 'Linux'],
        ['Fedora', 'Fedora', 'Linux'],
        ['Windows 2008', 'Windows 2008', 'Windows'],
        ['Windows XP', 'Windows XP', 'Windows'],
        ['Windows NT', 'Windows NT', 'Windows'],
        ['Windows 2003', 'Windows 2003', 'Windows'],
        ['Windows 7', 'Windows 7', 'Windows']
    ]
    ,VM_FAILOVER:1
    ,VM_SERVER_FAILOVER:2

   ,VM_CONSOLE:"VM_CONSOLE"
   ,VM_CONSOLE_REMEMBER:"VM_CONSOLE_REMEMBER"
   ,VM_CONSOLE_LOCAL_CMD:"VM_CONSOLE_LOCAL_CMD"
   ,CONNECT:"CONNECT"
   ,CONNECT_REMEMBER:"CONNECT_REMEMBER"
   ,CONNECT_LOCAL_CMD:"CONNECT_LOCAL_CMD"
   ,StackOne:"stackone"
   ,CLOUD:"cloud"
   ,EC2:"EC2"
   ,EUC:"EUC"
   ,CMS:"CMS"
   ,OPENSTACK:"OPENSTACK"
   ,DEFAULT_LOGIN:"DEFAULT_LOGIN"
   ,USER_NAME:"USER_NAME"
   ,KEY_LOCATION:"KEY_LOCATION"

   ,CF_SEC_GRP:"security_group"
   ,CF_KEY_PAIR:"keypair"
   ,CF_SINGLE_REGN:"single_region"
   ,CF_PUBLIC_IP:"public_ip"
  
   ,CF_GENERAL: 'general'
   ,CF_REGION: 'region'
   ,CF_REFRESH: 'refresh'
   ,CF_SERVICE_OFFERING: 'service_offering'
   ,CF_SERVER_POOL: 'server_pool'
   ,CF_STORAGE: 'storage'
   ,CF_VM_STORAGE_EDIT:'vm_storage_edit'
   ,CF_NETWORK: 'network'
   ,CF_PUBLIC_IP_REFRESH: 'refresh_public_ip'
   ,CF_TEMPLATE_GROUP: 'template_group'
   ,CF_NETWORKING_SERVICE: 'networking_service'
   ,CF_ACCOUNT: 'account'
   ,CF_PORT: 'port'
   ,CF_PATH: 'path'
   ,CF_END_POINT: 'end_point'
   ,CF_MEM_VCPU:'mem_vcpu'
   ,CF_KERNEL_RAM:'kernel_ram'
   ,CF_VDC_PRE_DEFINED_NW: 'vdc_pre_defined_nw'
   ,CF_VDC_PRIVATE_NW: 'vdc_private_nw'
   ,CF_VDC_PRIVATE_NW_POOL: 'vdc_private_nw_pool'
   ,CF_SNAPSHOT:'snapshot'
   ,CF_IMPORT_VM:'import_vm'
   ,IAAS_NAMES:{
       'EUC':'Eucalyptus',
       'CMS':'Local Infrastructure',
        'EC2':'Amazon',
        'OPENSTACK':'Openstack'
   }
   ,CMS_VM_STORAGE:'vm_storage'

   ,DB_DASHBOARD : "DASHBOARD"
   ,DB_TABS_CONFIG : "TABS.CONFIG"
   ,DB_GENERAL : "GENERAL"
   ,DB_TEMPLATE : "TEMPLATE"
   ,DB_DISPLAY : "DISPLAY"
   ,DB_USB : "USB"
   ,DB_BOOT : "BOOT"
   ,DB_ADVANCED : "ADVANCED"
   ,DB_STORAGE : "STORAGE"
   ,DB_NETWORK : "NETWORK"

}

