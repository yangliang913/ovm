# -*- coding: utf-8 -*-
from stackone.core.utils.utils import PyConfig, getHexID
from stackone.core.utils.utils import to_unicode, to_str
from stackone.model.ManagedNode import ManagedNode
from stackone.model.PlatformRegistry import PlatformRegistry
from stackone.model.ImageStore import ImageStore, ImageGroup, Image
##from stackone.cloud.DbModel.CPTypes import CPType
from stackone.model.PlatformType import PlatformType
from datetime import datetime
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import os
from stackone import model
def initialise_auth():
    admin = model.User()
    admin.user_name = u'admin'
    admin.display_name = u'Administrator'
    admin.email_address = u'admin@stackone.com.cn'
    admin.password = u'admin'
    admin.firstname = u'Administrator'
    admin.lastname = u'admin'
    admin.status = True
    admin.created_by = u''
    admin.modified_by = u''
    admin.created_date = datetime.now()
    admin.modified_date = datetime.now()
    admin.type = constants.StackOne
    model.DBSession.add(admin)
    manager = model.User()
    manager.user_name = u'operator'
    manager.display_name = u'Operator'
    manager.email_address = u'operator@stackone.com.cn'
    manager.password = u'operator'
    manager.firstname = u'Operator'
    manager.lastname = u'manager'
    manager.status = True
    manager.created_by = u''
    manager.modified_by = u''
    manager.created_date = datetime.now()
    manager.modified_date = datetime.now()
    manager.type = constants.StackOne
    model.DBSession.add(manager)
    user = model.User()
    user.user_name = u'user'
    user.display_name = u'user'
    user.email_address = u'user@stackone.com.cn'
    user.password = u'user'
    user.firstname = u'User'
    user.lastname = u'user'
    user.status = True
    user.created_by = u''
    user.modified_by = u''
    user.created_date = datetime.now()
    user.modified_date = datetime.now()
    user.type = constants.StackOne
    model.DBSession.add(user)
    group1 = model.Group()
    group1.group_name = u'adminGroup'
    group1.display_name = u'Administrator Group'
    group1.description = u'此组用户有管理的权限'
    group1.created_by = u''
    group1.modified_by = u''
    group1.created_date = datetime.now()
    group1.modified_date = datetime.now()
    group1.type = constants.StackOne
    group1.users.append(admin)
    model.DBSession.add(group1)
    group2 = model.Group()
    group2.group_name = u'operatorGroup'
    group2.display_name = u'Operators Group'
    group2.description = u'此组用户有操作的权限'
    group2.created_by = u''
    group2.modified_by = u''
    group2.created_date = datetime.now()
    group2.modified_date = datetime.now()
    group2.type = constants.StackOne
    group2.users.append(manager)
    model.DBSession.add(group2)
    permission = model.Permission()
    permission.permission_id = 1L
    permission.permission_name = u'manage'
    permission.description = u'This permission give an administrative right to the bearer'
    permission.groups.append(group2)
    model.DBSession.add(permission)
    group3 = model.Group()
    group3.group_name = u'usersGroup'
    group3.display_name = u'Users Group'
    group3.description = u'此组用户有查看的权限'
    group3.created_by = u''
    group3.modified_by = u''
    group3.created_date = datetime.now()
    group3.modified_date = datetime.now()
    group3.type = constants.StackOne
    group3.users.append(user)
    model.DBSession.add(group3)
    groups = [group1, group2, group3]
    ent_types = [{'id': 1L, 'name': 'DATA_CENTER', 'disp': 'Data Center'}, {'id': 2L, 'name': 'IMAGE_STORE', 'disp': 'Template Library'}, {'id': 3L, 'name': 'SERVER_POOL', 'disp': 'Server Pool'}, {'id': 4L, 'name': 'MANAGED_NODE', 'disp': 'Server'}, {'id': 5L, 'name': 'DOMAIN', 'disp': 'Virtual Machine'}, {'id': 6L, 'name': 'IMAGE_GROUP', 'disp': 'Template Group'}, {'id': 7L, 'name': 'IMAGE', 'disp': 'Template'}, {'id': 8L, 'name': 'APPLIANCE', 'disp': 'Appliance'}, {'id': 9L, 'name': 'EMAIL', 'disp': 'Email'}, {'id': 10L, 'name': 'CLOUD_VM', 'disp': 'Cloud VM'}, {'id': 11L, 'name': 'CLOUD_TEMPLATE', 'disp': 'Cloud Template'}, {'id': 12L, 'name': 'CLOUD_OUT_OF_BOX_TEMPLATE', 'disp': 'Cloud out of box Template'}, {'id': 13L, 'name': 'VDC_FOLDER', 'disp': 'VDC Folder'}, {'id': 14L, 'name': 'CLOUD_PROVIDER_FOLDER', 'disp': 'IaaS Folder'}, {'id': 15L, 'name': 'CLOUD_PROVIDER', 'disp': 'IaaS'}, {'id': 16L, 'name': 'VDC', 'disp': 'Virtual Data Center'}, {'id': 17L, 'name': 'TMP_LIB', 'disp': 'Cloud Template Library'}, {'id': 18L, 'name': 'CLOUD_TMPGRP', 'disp': 'Cloud Template Group'}, {'id': 19L, 'name': 'CMS_SERVICE_POINT', 'disp': 'CMS Service Point'}, {'id': 20L, 'name': 'VDC_VM_FOLDER', 'disp': 'Cloud Virtual Machines Folder'}]
    entity_types = {}
    for ent in ent_types:
        et=model.EntityType()
        et.name=_(ent['name'])
        et.display_name=_(ent['disp'])
        et.created_by=_("")
        et.modified_by=_("")
        et.created_date=datetime.now()
        et.modified_date=datetime.now()
        model.DBSession.add(et)
        entity_types[ent['name']]=et
    operations_group = [{'id': 1L, 'name': 'FULL_DATA_CENTER', 'desc': 'Full Privilege on Data Center'}, {'id': 2L, 'name': 'FULL_SERVER_POOL', 'desc': 'Full Privilege on Server Pools'}, {'id': 3L, 'name': 'FULL_MANAGED_NODE', 'desc': 'Full Privilege on Managed Node'}, {'id': 4L, 'name': 'FULL_DOMAIN', 'desc': 'Full Privilege on Domains'}, {'id': 5L, 'name': 'FULL_IMAGE_STORE', 'desc': 'Full Privilege on Image Store'}, {'id': 6L, 'name': 'FULL_IMAGE_GROUP', 'desc': 'Full Privilege on Image Groups'}, {'id': 7L, 'name': 'FULL_IMAGE', 'desc': 'Full Privilege on Images'}, {'id': 8L, 'name': 'OP_IMAGE_STORE', 'desc': 'Full Privilege on Image Store'}, {'id': 9L, 'name': 'OP_SERVER_POOL', 'desc': 'Operator Privilege on Server Pools'}, {'id': 10L, 'name': 'OP_MANAGED_NODE', 'desc': 'Operator Privilege on Managed Node'}, {'id': 11L, 'name': 'OP_DOMAIN', 'desc': 'Operator Privilege on Domains'}, {'id': 12L, 'name': 'OP_IMAGE_GROUP', 'desc': 'Operator Privilege on Image Groups'}, {'id': 13L, 'name': 'OP_IMAGE', 'desc': 'Operator Privilege on Images'}, {'id': 14L, 'name': 'VIEW_SERVER_POOL', 'desc': 'View Privilege on Server Pools'}, {'id': 15L, 'name': 'VIEW_MANAGED_NODE', 'desc': 'View Privilege on Managed Node'}, {'id': 16L, 'name': 'VIEW_DOMAIN', 'desc': 'View Privilege on Domains'}, {'id': 17L, 'name': 'VIEW_IMAGE_STORE', 'desc': 'View Privilege on Image Store'}, {'id': 18L, 'name': 'VIEW_IMAGE_GROUP', 'desc': 'View Privilege on Image Groups'}, {'id': 19L, 'name': 'VIEW_IMAGE', 'desc': 'View Privilege on Images'}, {'id': 20L, 'name': 'OP_DATA_CENTER', 'desc': 'Operator Privilege on Data Center'}, {'id': 21L, 'name': 'VIEW_DATA_CENTER', 'desc': 'View Privilege on Data Center'}, {'id': 22L, 'name': 'FULL_VDC_STORE', 'desc': 'Full Privilege on Vdc'}, {'id': 23L, 'name': 'OP_VDC_STORE', 'desc': 'Operator Privilege on Vdc'}, {'id': 24L, 'name': 'VIEW_VDC_STORE', 'desc': 'View Privilege on Vdc'}, {'id': 22L, 'name': 'FULL_VDC', 'desc': 'Full Privilege on Vdc'}, {'id': 23L, 'name': 'OP_VDC', 'desc': 'Operator Privilege on Vdc'}, {'id': 24L, 'name': 'VIEW_VDC', 'desc': 'View Privilege on Vdc'}, {'id': 25L, 'name': 'VM_FULL_OPS', 'desc': 'Full privilege on vm operations'}, {'id': 26L, 'name': 'VM_OP_OPS', 'desc': 'Operator privilege on vm operations'}, {'id': 27L, 'name': 'FULL_CLOUD_PROVIDER_FOLDER', 'desc': 'Cloud Full privilege on IaaS'}, {'id': 28L, 'name': 'OP_CLOUD_PROVIDER_FOLDER', 'desc': 'Cloud Operator privilege on IaaS'}, {'id': 29L, 'name': 'VIEW_CLOUD_PROVIDER_FOLDER', 'desc': 'Cloud View privilege on IaaS'}, {'id': 30L, 'name': 'FULL_CLOUD_PROVIDER', 'desc': 'Full privilege on IaaS'}, {'id': 31L, 'name': 'OP_CLOUD_PROVIDER', 'desc': 'Operator privilege on IaaS'}, {'id': 32L, 'name': 'VIEW_CLOUD_PROVIDER', 'desc': 'View privilege on IaaS'}, {'id': 33L, 'name': 'FULL_CLOUD_VDC', 'desc': 'Cloud full privilege on vdc'}, {'id': 34L, 'name': 'OP_CLOUD_VDC', 'desc': 'Cloud operator privilege on vdc'}, {'id': 35L, 'name': 'VIEW_CLOUD_VDC', 'desc': 'Cloud view privilege on vdc'}, {'id': 36L, 'name': 'CLOUD_VM_FULL_OPS', 'desc': 'Cloud operator privilege on vm operations'}, {'id': 37L, 'name': 'CLOUD_VM_OP_OPS', 'desc': 'Cloud operator privilege on vm operations'}, {'id': 38L, 'name': 'CLOUD_VM_VIEW_OPS', 'desc': 'Cloud operator privilege on vm operations'}, {'id': 39L, 'name': 'FULL_CLOUD_TEMPLATE_LIBRARY', 'desc': 'Cloud full privilege on Cloud Template Provider'}, {'id': 40L, 'name': 'OP_CLOUD_TEMPLATE_LIBRARY', 'desc': 'Cloud operator privilege on Cloud Template Provider'}, {'id': 41L, 'name': 'VIEW_CLOUD_TEMPLATE_LIBRARY', 'desc': 'Cloud view privilege on Cloud Template Provider'}, {'id': 42L, 'name': 'FULL_CLOUD_TEMPLATE_GROUP', 'desc': 'Cloud full privilege on Cloud Template Group'}, {'id': 43L, 'name': 'OP_CLOUD_TEMPLATE_GROUP', 'desc': 'Cloud operator privilege on Cloud Template Group'}, {'id': 44L, 'name': 'VIEW_CLOUD_TEMPLATE_GROUP', 'desc': 'Cloud view privilege on Cloud Template Group'}, {'id': 45L, 'name': 'FULL_CLOUD_TEMPLATES', 'desc': 'full privilege on Cloud Templates'}, {'id': 46L, 'name': 'OP_CLOUD_TEMPLATES', 'desc': 'operator privilege on Cloud Templates'}, {'id': 47L, 'name': 'VIEW_CLOUD_TEMPLATES', 'desc': 'view privilege on Cloud Templates'}, {'id': 48L, 'name': 'CLOUD_TEMPLATES_FULL_OPS', 'desc': 'Cloud full privilege on Cloud Templates'}, {'id': 49L, 'name': 'CLOUD_TEMPLATES_OP_OPS', 'desc': 'Cloud operator privilege on Cloud Templates'}, {'id': 50L, 'name': 'CLOUD_TEMPLATES_VIEW_OPS', 'desc': 'Cloud view privilege on Cloud Templates'}, {'id': 51L, 'name': 'FULL_VDC_VM_FOLDER', 'desc': 'Full Privilege on Virtual Machines Folder'}, {'id': 52L, 'name': 'OP_VDC_VM_FOLDER', 'desc': 'Operator Privilege on Virtual Machines Folder'}, {'id': 53L, 'name': 'VIEW_VDC_VM_FOLDER', 'desc': 'View Privilege on Virtual Machines Folder'}, {'id': 54L, 'name': 'FULL_CLOUD_VDC_VM_FOLDER', 'desc': 'Cloud full privilege on Virtual Machines Folder'}, {'id': 55L, 'name': 'OP_CLOUD_VDC_VM_FOLDER', 'desc': 'Cloud operator privilege on Virtual Machines Folder'}, {'id': 56L, 'name': 'VIEW_CLOUD_VDC_VM_FOLDER', 'desc': 'Cloud view privilege on Virtual Machines Folder'}, {'id': 57L, 'name': 'FULL_CSEP', 'desc': 'Full Privilege on CSEP'}, {'id': 58L, 'name': 'OP_CSEP', 'desc': 'Operator Privilege on CSEP'}]
    operations_group_dict = {}
    for opgrp in operations_group:
        og=model.OperationGroup()
        og.name=_(opgrp['name'])
        og.description=_(opgrp['desc'])
        og.created_by=_("")
        og.modified_by=_("")
        og.created_date=datetime.now()
        og.modified_date=datetime.now()
        model.DBSession.add(og)
        operations_group_dict[opgrp['name']]=og
        
        
    EC2 = constants.EC2
    CMS = constants.CMS
    EUC = constants.EUC
    OST = constants.OPENSTACK
    ALLCP = [EC2,CMS,EUC,OST]
    EC2CP = [EC2,EUC,OST]
    CMSCP = [CMS]
    cp_types = [
                {'display': u'AmazonEC2', 'name': EC2, 'desc': u'Amazon EC2 Cloud Provider'} ,
                {'display': u'stackoneCloud', 'name': CMS, 'desc': u'stackone-Cloud Cloud Provider'} ,
                {'display': u'Eucalyptus', 'name': EUC, 'desc': u'Eucalyptus Cloud Provider'} ,
                {'display': u'OpenStack', 'name': OST, 'desc': u'OpenStack Cloud Provider'} 
                ]
    cp_types_dict = {}
    # for cp_type in cp_types:
    #     cpt = CPType(cp_type['name'],cp_type['display'],cp_type['desc'])
    #     model.DBSession.add(cpt)
    #     cp_types_dict[cp_type['name']] = cpt
    operations_map = [{'id': 1L, 'op': 'ADD_SERVER_POOL', 'text': '新建服务器池', 'display_id': 'add_server_pool', 'entType': 'DATA_CENTER', 'separator': False, 'display': True, 'seq': 5L, 'groups': ['FULL_DATA_CENTER'], 'icon': 'add.png'},
                    {'id': 2L, 'op': 'ADD_SERVER', 'text': '添加服务器', 'display_id': 'add_node', 'entType': 'SERVER_POOL', 'separator': False, 'display': True, 'seq': 10L, 'groups': ['FULL_SERVER_POOL'], 'icon': 'add.png'}, 
                    {'id': 3L, 'op': 'CONNECT_ALL', 'text': '连接所有', 'display_id': 'connect_all', 'entType': 'SERVER_POOL', 'opr': True, 'separator': True, 'display': True, 'seq': 15L, 'groups': ['FULL_SERVER_POOL', 'OP_SERVER_POOL'], 'icon': 'small_connect.png'}, 
                    {'id': 4L, 'op': 'PROVISION_GROUP_VM', 'text': '新建VM', 'display_id': 'provision_vm', 'entType': 'SERVER_POOL', 'opr': True, 'separator': False, 'display': True, 'seq': 20L, 'groups': ['FULL_SERVER_POOL', 'OP_SERVER_POOL'], 'icon': 'provision_vm.png'}, 
                    {'id': 5L, 'op': 'VIEW_GROUP_PROVISIONING_SETTINGS', 'text': '添加设置', 'icon': 'settings.png', 'display_id': 'group_provision_settings', 'entType': 'SERVER_POOL', 'opr': True, 'separator': False, 'display': False, 'seq': 25L, 'groups': ['FULL_SERVER_POOL', 'OP_SERVER_POOL']}, 
                    {'id': 6L, 'op': 'STORAGE_POOL', 'text': '管理存储', 'display_id': 'storage_pool', 'entType': 'DATA_CENTER,SERVER_POOL', 'opr': True, 'separator': False, 'display': True, 'seq': 35L, 'groups': ['FULL_DATA_CENTER', 'OP_DATA_CENTER', 'FULL_SERVER_POOL', 'OP_SERVER_POOL'], 'icon': 'storage_pool.png'}, 
                    {'id': 101L, 'op': 'DWM_POLICY', 'text': '配置动态负载均衡', 'display_id': 'dwm_policy', 'entType': 'SERVER_POOL', 'separator': False, 'display': False, 'seq': 33L, 'groups': ['FULL_SERVER_POOL', 'OP_SERVER_POOL'], 'icon': 'dwm.png'}, 
                    {'id': 7L, 'op': 'REMOVE_SERVER_POOL', 'text': '移除', 'display_id': 'remove_server_pool', 'entType': 'SERVER_POOL', 'separator': False, 'display': True, 'seq': 999L, 'groups': ['FULL_SERVER_POOL'], 'icon': 'delete.png'}, 
                    {'id': 8L, 'op': 'EDIT_GROUP_PROVISIONING_SETTINGS', 'display_id': 'save_group_vars', 'entType': 'SERVER_POOL', 'opr': True, 'groups': ['FULL_SERVER_POOL', 'OP_SERVER_POOL'], 'icon': '.png'}, 
                    {'id': 9L, 'op': 'ADD_STORAGE_DEF', 'display_id': 'add_storage_def', 'entType': 'DATA_CENTER,SERVER_POOL,MANAGED_NODE', 'opr': True, 'groups': ['FULL_DATA_CENTER', 'OP_DATA_CENTER', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 10L, 'op': 'UPDATE_STORAGE_DEF', 'display_id': 'edit_storage_def', 'entType': 'DATA_CENTER,SERVER_POOL,MANAGED_NODE', 'opr': True, 'groups': ['FULL_DATA_CENTER', 'OP_DATA_CENTER', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 11L, 'op': 'UPDATE_STORAGE_DEF', 'display_id': 'rename_storage_def', 'entType': 'DATA_CENTER,SERVER_POOL,MANAGED_NODE', 'opr': True, 'groups': ['FULL_DATA_CENTER', 'OP_DATA_CENTER', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 12L, 'op': 'REMOVE_STORAGE_DEF', 'display_id': 'remove_storage_def', 'entType': 'DATA_CENTER,SERVER_POOL,MANAGED_NODE', 'opr': True, 'groups': ['FULL_DATA_CENTER', 'OP_DATA_CENTER', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 13L, 'op': 'UPDATE_STORAGE_DEF', 'display_id': 'test_storage_def', 'entType': 'DATA_CENTER,SERVER_POOL,MANAGED_NODE', 'opr': True, 'groups': ['FULL_DATA_CENTER', 'OP_DATA_CENTER', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 14L, 'op': 'EDIT_SERVER', 'text': '编辑主机', 'display_id': 'edit_node', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': False, 'display': True, 'seq': 40L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'file_edit.png'}, 
                    {'id': 327L, 'op': 'OPEN SSH', 'text': '打开SSH终端', 'display_id': 'ssh_node', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': False, 'display': False, 'seq': 41L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'file_edit.png'}, 
                    {'id': 15L, 'op': 'CONNECT_SERVER', 'text': '连接主机', 'display_id': 'connect_node', 'entType': 'MANAGED_NODE', 'text': '连接主机', 'opr': True, 'separator': False, 'display': True, 'seq': 45L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'small_connect.png'}, 
                    {'id': 100L, 'op': 'MIGRATE_SERVER', 'text': '迁移主机', 'display_id': 'migrate_server', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': True, 'display': True, 'seq': 47L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'small_migrate_vm.png'}, 
                    {'id': 16L, 'op': 'PROVISION_VM', 'text': '新建VM', 'display_id': 'provision_vm', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': False, 'display': True, 'seq': 50L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'provision_vm.png'}, 
                    {'id': 17L, 'op': 'RESTORE_FROM_BACKUP', 'text': '还原备份', 'display_id': 'restore_from_backup', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': False, 'display': False, 'seq': 55L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'small_restore.png'}, 
                    {'id': 112L, 'op': 'RESTORE_HIBERNATED', 'text': '恢复休眠', 'display_id': 'restore_hibernated', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': False, 'display': True, 'seq': 56L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'small_restore.png'}, 
                    {'id': 18L, 'op': 'IMPORT_VM_CONFIG_FILE', 'text': '导入VM配置文件', 'display_id': 'import_vm_config', 'entType': 'MANAGED_NODE', 'separator': True, 'display': True, 'seq': 60L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'folder.png'}, 
                    {'id': 19L, 'op': 'START_ALL', 'text': '开启所有VM', 'display_id': 'start_all', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': False, 'display': True, 'seq': 65L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'small_start.png'}, 
                    {'id': 20L, 'op': 'SHUTDOWN_ALL', 'text': '关闭所有VM', 'display_id': 'shutdown_all', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': False, 'display': True, 'seq': 70L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'small_shutdown.png'}, 
                    {'id': 21L, 'op': 'KILL_ALL', 'text': '强制关闭所有VM', 'display_id': 'kill_all', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': False, 'display': True, 'seq': 75L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'small_kill.png'}, 
                    {'id': 22L, 'op': 'MIGRATE_ALL', 'text': '迁移所有VM', 'display_id': 'migrate_all', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': True, 'display': True, 'seq': 80L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'small_migrate_vm.png'}, 
                    {'id': 23L, 'op': 'MANAGE_VIRTUAL_NETWORKS', 'text': '管理虚拟网络', 'display_id': 'manage_virtual_networks', 'entType': 'DATA_CENTER,SERVER_POOL,MANAGED_NODE', 'opr': True, 'separator': True, 'display': True, 'seq': 89L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_DATA_CENTER', 'OP_DATA_CENTER'], 'icon': 'manage_virtual_networks.png'}, 
                    {'id': 111L, 'op': 'MANAGE_VLAN_ID_POOL', 'text': '管理VLAN Id池', 'display_id': 'manage_vlan_id_pool', 'entType': 'DATA_CENTER', 'opr': True, 'separator': True, 'display': True, 'seq': 90L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_DATA_CENTER', 'OP_DATA_CENTER'], 'icon': 'manage_vlan_id_pool.png'}, 
                    {'id': 111L, 'op': 'MANAGE_PUBLIC_IP_POOL', 'text': '管理公共IP池', 'display_id': 'manage_public_ip_pool', 'entType': 'DATA_CENTER', 'opr': True, 'separator': False, 'display': True, 'seq': 91L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_DATA_CENTER', 'OP_DATA_CENTER'], 'icon': 'manage_public_ip_pool.png'}, 
                    {'id': 107L, 'op': 'SERVER_MAINTENANACE', 'text': '主机维护模式', 'display_id': 'server_maintenance', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': False, 'display': True, 'seq': 998L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'general.gif'}, 
                    {'id': 24L, 'op': 'REMOVE_SERVER', 'text': '移除', 'display_id': 'remove_node', 'entType': 'MANAGED_NODE', 'separator': False, 'display': True, 'seq': 999L, 'groups': ['FULL_MANAGED_NODE'], 'icon': 'delete.png'}, 
                    {'id': 101L, 'op': 'POWER_MANAGEMENT', 'text': '配置电源管理', 'display_id': 'power_management', 'entType': 'MANAGED_NODE', 'separator': False, 'display': True, 'seq': 88L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'power_mgmt.png'}, 
                    {'id': 25L, 'op': 'TRANSFER_SERVER', 'display_id': 'transfer_node', 'entType': 'MANAGED_NODE', 'opr': True, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 26L, 'op': 'ADD_VM', 'display_id': '', 'entType': 'MANAGED_NODE', 'opr': True, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 27L, 'op': 'VIEW_NODE_INFO', 'display_id': 'get_node_info', 'entType': 'MANAGED_NODE', 'opr': True, 'view': True, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE', 'VIEW_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 28L, 'op': 'VIEW_NODE_PROPERTIES', 'display_id': 'get_node_properties', 'entType': 'MANAGED_NODE', 'opr': True, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 29L, 'op': 'VIEW_TARGET_IMAGES', 'display_id': 'get_target_images', 'entType': 'MANAGED_NODE', 'opr': True, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 30L, 'op': 'VIEW_TARGET_IMAGE_GROUPS', 'display_id': 'get_target_image_groups', 'entType': 'MANAGED_NODE', 'opr': True, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 31L, 'op': 'VIEW_DIRECTORY_CONTENTS', 'display_id': 'get_dir_contents', 'entType': 'MANAGED_NODE', 'opr': True, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 32L, 'op': 'MAKE_DIRECTORY', 'display_id': 'make_dir', 'entType': 'MANAGED_NODE', 'opr': True, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 33L, 'op': 'MIGRATE_TARGET_NODES', 'display_id': 'get_target_nodes', 'entType': 'MANAGED_NODE', 'opr': True, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': '.png'}, 
                    {'id': 9L, 'op': 'ADD_NETWORK_DEF', 'display_id': 'add_network_def', 'entType': 'DATA_CENTER,SERVER_POOL,MANAGED_NODE,CLOUD_PROVIDER,VDC,CMS_SERVICE_POINT', 'opr': True, 'groups': ['FULL_DATA_CENTER', 'OP_DATA_CENTER', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_MANAGED_NODE', 'OP_MANAGED_NODE', 'FULL_CLOUD_PROVIDER', 'OP_CLOUD_PROVIDER', 'FULL_VDC', 'OP_VDC', 'FULL_CSEP', 'OP_CSEP'], 'icon': '.png'}, 
                    {'id': 10L, 'op': 'UPDATE_NETWORK_DEF', 'display_id': 'edit_network_def', 'entType': 'DATA_CENTER,SERVER_POOL,MANAGED_NODE,CMS_SERVICE_POINT', 'opr': True, 'groups': ['FULL_DATA_CENTER', 'OP_DATA_CENTER', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_MANAGED_NODE', 'OP_MANAGED_NODE', 'FULL_CSEP', 'OP_CSEP'], 'icon': '.png'}, 
                    {'id': 12L, 'op': 'REMOVE_NETWORK_DEF', 'display_id': 'remove_network_def', 'entType': 'DATA_CENTER,SERVER_POOL,MANAGED_NODE,CMS_SERVICE_POINT', 'opr': True, 'groups': ['FULL_DATA_CENTER', 'OP_DATA_CENTER', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_MANAGED_NODE', 'OP_MANAGED_NODE', 'FULL_CSEP', 'OP_CSEP'], 'icon': '.png'}, 
                    {'id': 34L, 'op': 'CHANGE_VM_SETTINGS', 'text': '编辑设置', 'display_id': 'change_vm_settings', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 95L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'file_edit.png'}, 
                    {'id': 35L, 'op': 'EDIT_VM_CONFIG_FILE', 'text': '编辑虚拟机配置文件', 'display_id': 'edit_vm_config_file', 'entType': 'DOMAIN', 'separator': True, 'opr': True, 'display': False, 'seq': 100L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'file_edit.png'}, 
                    {'id': 34L, 'op': 'VIEW_CONSOLE', 'text': '弹出控制台', 'display_id': 'view_console', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 102L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'view_console.png'}, 
                    {'id': 36L, 'op': 'MIGRATE_VM', 'text': '迁移VM', 'display_id': 'migrate', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 105L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'small_migrate_vm.png'}, 
                    {'id': 37L, 'op': 'START', 'text': '开启', 'display_id': 'start', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 110L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'small_start.png'}, 
                    {'id': 109L, 'op': 'START_VIEW_CONSOLE', 'text': '开启并进入控制台', 'display_id': 'start_view_console', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 113L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'provision_vm.png'}, 
                    {'id': 38L, 'op': 'PAUSE', 'text': '暂停', 'display_id': 'pause', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 115L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'small_pause.png'}, 
                    {'id': 39L, 'op': 'UNPAUSE', 'text': '恢复', 'display_id': 'unpause', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 125L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'small_pause.png'}, 
                    {'id': 40L, 'op': 'REBOOT', 'text': '重启', 'display_id': 'reboot', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 120L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'small_reboot.png'}, 
                    {'id': 41L, 'op': 'SHUTDOWN', 'text': '关闭', 'display_id': 'shutdown', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 125L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'small_shutdown.png'}, 
                    {'id': 42L, 'op': 'KILL', 'text': '强制关闭', 'display_id': 'kill', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 130L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'small_kill.png'}, 
                    {'id': 111L, 'op': 'CREATE_IMAGE_FROM_VM', 'text': '转换模板', 'display_id': 'create_image_from_vm', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 126L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'add_appliance.png'}, 
                    {'id': 43L, 'op': 'HIBERNATE_VM', 'text': '休眠', 'display_id': 'hibernate', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 135L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'small_snapshot.png'}, 
                    {'id': 44L, 'op': 'SET_BOOT_DEVICE', 'text': '设置启动顺序', 'display_id': 'set_boot_device', 'entType': 'DOMAIN', 'opr': True, 'separator': True, 'display': True, 'seq': 140L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'file_edit.png'}, 
                    {'id': 45L, 'op': 'REMOVE_VM_CONFIG', 'text': '移除VM配置文件', 'display_id': 'remove_vm_config', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 146L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'vm_delete.png'}, 
                    {'id': 46L, 'op': 'REMOVE_VM', 'display_id': 'delete', 'text': '移除', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 150L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'delete.png'}, 
                    {'id': 47L, 'op': 'VIEW_VM_CONFIG_FILE', 'display_id': 'get_vm_config_file', 'entType': 'DOMAIN', 'opr': True, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': '.png'}, 
                    {'id': 48L, 'op': 'VIEW_VM_INFO', 'display_id': 'get_vm_info', 'entType': 'DOMAIN', 'opr': True, 'view': True, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN', 'VIEW_DOMAIN'], 'icon': '.png'}, 
                    {'id': 49L, 'op': 'ADD_IMAGE_GROUP', 'text': '新建模板组', 'display_id': 'add_image_group', 'entType': 'IMAGE_STORE', 'separator': False, 'display': True, 'seq': 155L, 'groups': ['FULL_IMAGE_STORE'], 'icon': 'add.png'}, 
                    {'id': 50L, 'op': 'VIEW_IMAGE_STORE_INFO', 'display_id': 'get_image_store_info', 'entType': 'IMAGE_STORE', 'opr': True, 'view': True, 'groups': ['FULL_IMAGE_STORE', 'OP_IMAGE_STORE', 'VIEW_IMAGE_STORE'], 'icon': '.png'}, 
                    {'id': 51L, 'op': 'RENAME_IMAGE_GROUP', 'text': '重命名模板组', 'display_id': 'rename_image_group', 'entType': 'IMAGE_GROUP', 'opr': True, 'separator': False, 'display': True, 'seq': 160L, 'groups': ['FULL_IMAGE_GROUP', 'OP_IMAGE_GROUP'], 'icon': 'rename.png'}, 
                    {'id': 52L, 'op': 'REMOVE_IMAGE_GROUP', 'text': '移除模板组', 'display_id': 'remove_image_group', 'entType': 'IMAGE_GROUP', 'separator': False, 'display': True, 'seq': 165L, 'groups': ['FULL_IMAGE_GROUP'], 'icon': 'delete.png'}, 
                    {'id': 53L, 'op': 'IMPORT_APPLIANCE', 'text': '创建模板 ', 'display_id': 'import_appliance', 'entType': 'IMAGE_GROUP,IMAGE_STORE', 'separator': False, 'display': False, 'seq': 170L, 'groups': ['FULL_IMAGE_GROUP', 'FULL_IMAGE_STORE'], 'icon': 'add_appliance.png'}, 
                    {'id': 54L, 'op': 'VIEW_IMAGE_GROUP_INFO', 'display_id': 'get_image_group_info', 'entType': 'IMAGE_GROUP', 'opr': True, 'view': True, 'seq': 175L, 'groups': ['FULL_IMAGE_GROUP', 'OP_IMAGE_GROUP', 'VIEW_IMAGE_GROUP'], 'icon': '.png'}, 
                    {'id': 55L, 'op': 'CREATE_IMAGE', 'display_id': '', 'text': '创建模板', 'entType': 'IMAGE_GROUP', 'opr': True, 'groups': ['FULL_IMAGE_GROUP', 'OP_IMAGE_GROUP'], 'icon': '.png'}, 
                    {'id': 56L, 'op': 'PROVISION_IMAGE', 'display_id': 'provision_image', 'text': '部署VM', 'entType': 'IMAGE', 'opr': True, 'separator': True, 'display': True, 'seq': 180L, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': 'provision_vm.png'}, 
                    {'id': 57L, 'op': 'EDIT_IMAGE_SETTINGS', 'display_id': 'edit_image_settings', 'text': '编辑设置', 'entType': 'IMAGE', 'opr': True, 'separator': False, 'display': True, 'seq': 185L, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': 'file_edit.png'}, 
                    {'id': 58L, 'op': 'EDIT_IMAGE_SCRIPT', 'text': '编辑模板脚本', 'display_id': 'edit_image_script', 'entType': 'IMAGE', 'opr': True, 'separator': False, 'display': False, 'seq': 190L, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': 'file_edit.png'}, 
                    {'id': 59L, 'op': 'EDIT_IMAGE_DESCRIPTION', 'text': '编辑模板说明', 'display_id': 'edit_image_desc', 'entType': 'IMAGE', 'opr': True, 'separator': True, 'display': False, 'seq': 195L, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': 'file_edit.png'}, 
                    {'id': 60L, 'op': 'CREATE_LIKE', 'text': '克隆模板', 'display_id': 'clone_image', 'entType': 'IMAGE', 'separator': False, 'display': True, 'seq': 200L, 'groups': ['FULL_IMAGE'], 'icon': 'clone.png'}, 
                    {'id': 61L, 'op': 'RENAME_IMAGE', 'text': '重命名模板', 'display_id': 'rename_image', 'entType': 'IMAGE', 'opr': True, 'separator': False, 'display': True, 'seq': 205L, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': 'rename.png'}, 
                    {'id': 62L, 'op': 'REMOVE_IMAGE', 'text': '移除模板', 'display_id': 'remove_image', 'entType': 'IMAGE', 'separator': False, 'display': True, 'seq': 210L, 'groups': ['FULL_IMAGE'], 'icon': 'delete.png'}, 
                    {'id': 63L, 'op': 'TRANSFER_IMAGE', 'display_id': 'transfer_image', 'entType': 'IMAGE', 'opr': True, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': '.png'}, 
                    {'id': 64L, 'op': 'EDIT_IMAGE_DESCRIPTION', 'display_id': 'get_image_info', 'entType': 'IMAGE', 'opr': True, 'view': True, 'groups': ['FULL_IMAGE', 'OP_IMAGE', 'VIEW_IMAGE'], 'icon': '.png'}, 
                    {'id': 65L, 'op': 'IMAGE_TARGET_NODES', 'display_id': 'get_target_nodes', 'entType': 'IMAGE', 'opr': True, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': '.png'}, 
                    {'id': 66L, 'op': 'EDIT_IMAGE_SCRIPT', 'display_id': 'get_image_script', 'entType': 'IMAGE', 'opr': True, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': '.png'}, 
                    {'id': 67L, 'op': 'VIEW_APPLIANCE_INFO', 'display_id': 'get_appliance_info', 'entType': 'DOMAIN', 'opr': True, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': '.png'}, 
                    {'id': 68L, 'op': 'SAVE_APPLIANCE_INFO', 'display_id': 'save_appliance_info', 'entType': 'DOMAIN', 'opr': True, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': '.png'}, 
                    {'id': 69L, 'op': 'VIEW_APPLIANCE_MENU', 'display_id': '', 'entType': 'APPLIANCE', 'opr': True, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': '.png'}, 
                    {'id': 70L, 'op': 'VIEW_APPLIANCE_LIST', 'display_id': '', 'entType': 'APPLIANCE', 'opr': True, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': '.png'}, 
                    {'id': 71L, 'op': 'VIEW_APPLIANCE_ARCHS', 'display_id': '', 'entType': 'APPLIANCE', 'opr': True, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': '.png'}, 
                    {'id': 72L, 'op': 'VIEW_APPLIANCE_PACKAGES', 'display_id': '', 'entType': 'APPLIANCE', 'opr': True, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': '.png'}, 
                    {'id': 73L, 'op': 'VIEW_APPLIANCE_PROVIDERS', 'display_id': '', 'entType': 'APPLIANCE', 'opr': True, 'groups': ['FULL_IMAGE', 'OP_IMAGE'], 'icon': '.png'}, 
                    {'id': 74L, 'op': 'CONFIGURE_HIGH_AVAILABILITY', 'text': '配置高可用', 'icon': 'high-availability-icon.png', 'display_id': 'configure_high_availability', 'entType': 'SERVER_POOL', 'opr': True, 'separator': False, 'display': False, 'seq': 32L, 'groups': ['FULL_SERVER_POOL', 'OP_SERVER_POOL']}, 
                    {'id': 75L, 'op': 'CONFIGURE_HIGH_AVAILABILITY', 'text': '电源管理', 'icon': 'high-availability-icon.png', 'display_id': 'configure_high_availability', 'entType': 'DATA_CENTER', 'opr': True, 'separator': False, 'display': False, 'seq': 25L, 'groups': ['FULL_DATA_CENTER', 'OP_DATA_CENTER']}, 
                    {'id': 76L, 'op': 'BACKUP_POLICY', 'text': '配置备份', 'display_id': 'backup_vm_settings', 'entType': 'SERVER_POOL', 'opr': True, 'separator': False, 'display': False, 'seq': 34L, 'groups': ['FULL_SERVER_POOL', 'OP_SERVER_POOL'], 'icon': 'storage_pool.png'}, 
                    {'id': 77L, 'op': 'ADD_BACKUP_POLICY', 'display_id': 'add_backup_policy', 'entType': 'SERVER_POOL', 'opr': True, 'groups': ['FULL_SERVER_POOL', 'OP_SERVER_POOL'], 'icon': '.png'}, 
                    {'id': 78L, 'op': 'UPDATE_BACKUP_POLICY', 'display_id': 'edit_backup_policy', 'entType': 'SERVER_POOL', 'opr': True, 'groups': ['FULL_SERVER_POOL', 'OP_SERVER_POOL'], 'icon': '.png'}, 
                    {'id': 79L, 'op': 'REMOVE_BACKUP_POLICY', 'display_id': 'remove_backup_policy', 'entType': 'SERVER_POOL', 'opr': True, 'groups': ['FULL_SERVER_POOL', 'OP_SERVER_POOL'], 'icon': '.png'}, 
                    {'id': 80L, 'op': 'BACKUP_NOW', 'text': ' 备份', 'display_id': 'backup_now', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': False, 'seq': 142L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'back-up-icon.png'}, 
                    {'id': 81L, 'op': 'EXEC_BACKUP_POLICY', 'display_id': 'exec_backup_policy', 'entType': 'SERVER_POOL,DOMAIN', 'opr': True, 'groups': ['FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'storage_pool.png'}, 
                    {'id': 82L, 'op': 'RESTORE_BACKUP', 'text': '还原备份', 'display_id': 'restore_backup', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': False, 'seq': 144L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'restore-icon.png'}, 
                    {'id': 84L, 'op': 'PURGE_BACKUP', 'text': '清除备份', 'display_id': 'purge_backup', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': False, 'seq': 145L, 'groups': ['FULL_DATA_CENTER', 'OP_DATA_CENTER', 'FULL_SERVER_POOL', 'OP_SERVER_POOL'], 'icon': 'delete.png'}, 
                    {'id': 85L, 'op': 'EDIT_VDC', 'text': '编辑虚拟数据中心', 'display_id': 'edit_vdc', 'entType': 'VDC', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 212L, 'groups': ['FULL_VDC', 'OP_VDC'], 'icon': 'file_edit.png'}, 
                    {'id': 86L, 'op': 'DELETE_VDC', 'text': '移除虚拟数据中心', 'display_id': 'delete_vdc', 'entType': 'VDC', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 213L, 'groups': ['FULL_VDC', 'OP_VDC'], 'icon': 'delete.png'},
                     
                    {'id': 87L, 'op': 'CLOUD_PROVISION_VM', 'text': '新建VM', 'display_id': 'provision_vm', 'entType': 'VDC_VM_FOLDER', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 214L, 'groups': ['FULL_VDC_VM_FOLDER', 'OP_VDC_VM_FOLDER', 'FULL_CLOUD_VDC_VM_FOLDER', 'OP_CLOUD_VDC_VM_FOLDER'], 'icon': 'provision_vm.png'},
#                    {'id': 115, 'op': 'CLOUD_STARTALL', 'text': '开启所有', 'display_id': 'start_all', 'entType': 'VDC_VM_FOLDER', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 225L, 'groups': ['FULL_VDC_VM_FOLDER', 'OP_VDC_VM_FOLDER', 'FULL_CLOUD_VDC_VM_FOLDER', 'OP_CLOUD_VDC_VM_FOLDER'], 'icon': 'small_start.png'},
#                    {'id': 115, 'op': 'CLOUD_STOPALL', 'text': '关闭所有', 'display_id': 'stop_all', 'entType': 'VDC_VM_FOLDER', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 226L, 'groups': ['FULL_VDC_VM_FOLDER', 'OP_VDC_VM_FOLDER', 'FULL_CLOUD_VDC_VM_FOLDER', 'OP_CLOUD_VDC_VM_FOLDER'], 'icon': 'small_shutdown.png'},
                    
                    
                    {'id': 88L, 'op': 'CLOUD_CONNECT', 'text': '连接', 'display_id': 'connect', 'entType': 'CLOUD_VM', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 215L, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS', 'CLOUD_VM_VIEW_OPS'], 'icon': 'small_connect.png'},
                    {'id': 89L, 'op': 'CLOUD_START_VM', 'text': '开启', 'display_id': 'start', 'entType': 'CLOUD_VM', 'CPTYPE': [EC2, CMS, OST], 'separator': False, 'display': True, 'seq': 216L, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS', 'CLOUD_VM_VIEW_OPS'], 'icon': 'small_start.png'},
                    {'id': 90L, 'op': 'CLOUD_STOP_VM', 'text': '关闭', 'display_id': 'stop', 'entType': 'CLOUD_VM', 'CPTYPE': [EC2, CMS, OST], 'separator': False, 'display': True, 'seq': 217L, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS', 'CLOUD_VM_VIEW_OPS'], 'icon': 'small_shutdown.png'},
                    {'id': 91L, 'op': 'CLOUD_DELETE_VM', 'text': '移除', 'display_id': 'terminate', 'entType': 'CLOUD_VM', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 218L, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS'], 'icon': 'delete.png'}, 
                    {'id': 92L, 'op': 'CLOUD_EDIT_VM', 'text': '编辑', 'display_id': 'edit_vm', 'entType': 'CLOUD_VM', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 219L, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS'], 'icon': 'file_edit.png'}, 
                    {'id': 93L, 'op': 'CLOUD_REBOOT_VM', 'text': '重启', 'display_id': 'reboot', 'entType': 'CLOUD_VM', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 220L, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS', 'CLOUD_VM_VIEW_OPS'], 'icon': 'small_reboot.png'}, 
                    {'id': 95L, 'op': 'ADD_CLOUD_PROVIDER', 'text': '添加IaaS', 'display_id': 'add_cloud_provider', 'entType': 'CLOUD_PROVIDER_FOLDER', 'opr': True, 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 224L, 'groups': ['FULL_CLOUD_PROVIDER_FOLDER'], 'icon': 'add.png'}, 
                    {'id': 96L, 'op': 'PROVISION_VDC', 'text': '新建虚拟数据中心', 'display_id': 'provision_vdc', 'entType': 'VDC_FOLDER', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 225L, 'groups': ['FULL_VDC_STORE', 'OP_VDC_STORE'], 'icon': 'provision_vm.png'}, 
                    {'id': 97L, 'op': 'STORAGE_POOL', 'text': '管理公共IP', 'display_id': 'cloud_public_ip', 'entType': 'VDC', 'opr': True, 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 200L, 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'icon': 'Publicip.png'}, 
                    {'id': 98L, 'op': 'STORAGE_POOL', 'text': '管理密钥对', 'display_id': 'cloud_key_pair', 'entType': 'VDC', 'opr': True, 'CPTYPE': EC2CP, 'separator': False, 'display': True, 'seq': 201L, 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'icon': 'KeyPairs.png'}, 
                    {'id': 99L, 'op': 'STORAGE_POOL', 'text': '管理安全组', 'display_id': 'cloud_security_group', 'entType': 'VDC', 'opr': True, 'CPTYPE': EC2CP, 'separator': False, 'display': True, 'seq': 202L, 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'icon': 'Securitygroups.png'}, 
                    {'id': 100L, 'op': 'STORAGE_POOL', 'text': '管理存储', 'display_id': 'cloud_storage', 'entType': 'VDC', 'opr': True, 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 203L, 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'icon': 'StorageManagement.png'}, 
                    {'id': 101L, 'op': 'EDIT_CLOUD_PROVIDER', 'text': '编辑IaaS', 'display_id': 'edit_cloud_provider', 'entType': 'CLOUD_PROVIDER', 'CPTYPE': ALLCP, 'opr': True, 'separator': False, 'display': True, 'seq': 155L, 'groups': ['FULL_CLOUD_PROVIDER', 'OP_CLOUD_PROVIDER'], 'icon': 'file_edit.png'}, 
                    {'id': 102L, 'op': 'CREATE_TEMPLATE', 'text': '克隆模板', 'display_id': 'create_template', 'entType': 'CLOUD_TEMPLATE', 'opr': True, 'CPTYPE': CMSCP, 'separator': False, 'display': True, 'seq': 146L, 'groups': ['CLOUD_TEMPLATES_FULL_OPS', 'CLOUD_TEMPLATES_OP_OPS', 'FULL_CLOUD_TEMPLATES', 'OP_CLOUD_TEMPLATES'], 'icon': 'provision_vm.png'}, 
                    {'id': 105L, 'op': 'DELETE_CLOUD_PROVIDER', 'text': '移除IaaS', 'display_id': 'delete_cloud_provider', 'entType': 'CLOUD_PROVIDER', 'CPTYPE': ALLCP, 'opr': True, 'separator': False, 'display': True, 'seq': 156L, 'groups': ['FULL_CLOUD_PROVIDER', 'OP_CLOUD_PROVIDER'], 'icon': 'delete.png'}, 
                    {'id': 106L, 'op': 'CREATE_TEMPLATE', 'text': '创建模板', 'display_id': 'create_template', 'entType': 'CLOUD_VM', 'opr': True, 'CPTYPE': EC2CP, 'separator': False, 'display': True, 'seq': 221L, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS'], 'icon': 'provision_vm.png'}, 
                    {'id': 107L, 'op': 'ANNOTATE', 'text': '注释', 'display_id': 'annotate', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 222L, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'rename.png'}, 
                    {'id': 108L, 'op': 'ANNOTATE', 'text': '注释', 'display_id': 'annotate', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': False, 'display': True, 'seq': 223L, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'rename.png'}, 
                    {'id': 109L, 'op': 'STORAGE_POOL', 'text': '管理快照', 'display_id': 'cloud_snapshot', 'entType': 'VDC', 'opr': True, 'separator': False, 'display': True, 'seq': 203L, 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'icon': 'StorageManagement.png'}, 
                    {'id': 110L, 'op': 'MANAGE_NETWORK', 'text': '管理网络', 'display_id': 'cloud_network', 'entType': 'VDC,CMS_SERVICE_POINT', 'opr': True, 'CPTYPE': CMSCP, 'separator': False, 'display': True, 'seq': 204L, 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC', 'FULL_CSEP', 'OP_CSEP'], 'icon': 'manage_virtual_networks.png'}]
    i = 0
    for opmap in operations_map:
        i += 1
        o = model.Operation()
        o.name = _(opmap['op'])
        o.icon = _(opmap['icon'])
        o.description = _(opmap['op'])
        o.created_by = _('')
        o.modified_by = _('')
        o.created_date = datetime.now()
        o.modified_date = datetime.now()
        
        if opmap.has_key('text'):
            o.display_name = _(opmap['text'])
        if opmap.has_key('display_id'):
            o.display_id = _(opmap['display_id'])
        for entType in opmap['entType'].split(','):
            o.entityType.append(entity_types[entType])
        if opmap.has_key('display'):
            o.display = opmap['display']
        if opmap.has_key('seq'):
            o.display_seq = opmap['seq']
        if opmap.has_key('separator'):
            o.has_separator = opmap['separator']
        grps = opmap['groups']
        for grp in grps:
            og = operations_group_dict[grp]
            o.opsGroup.append(og)
        # cpts = opmap.get('CPTYPE',None)
        # if cpts:
        #     for cp in cpts:
        #         og = cp_types_dict[cp]
        #         o.cpTypes.append(og)
        # model.DBSession.add(o)
    op_platform_type(None)
    privs = [{'id': 1L, 'name': 'FULL', 'groups': ['FULL_DATA_CENTER', 'FULL_IMAGE_STORE', 'FULL_SERVER_POOL', 'FULL_MANAGED_NODE', 'FULL_IMAGE_GROUP', 'FULL_DOMAIN', 'FULL_IMAGE', 'FULL_VDC', 'FULL_CLOUD_PROVIDER_FOLDER', 'FULL_VDC_STORE', 'VM_FULL_OPS', 'FULL_CLOUD_PROVIDER', 'FULL_CLOUD_TEMPLATE_LIBRARY', 'FULL_CLOUD_TEMPLATE_GROUP', 'FULL_CLOUD_TEMPLATES', 'FULL_VDC_VM_FOLDER', 'FULL_CSEP'], 'type': constants.StackOne}, {'id': 2L, 'name': 'OPERATOR', 'groups': ['OP_DATA_CENTER', 'OP_SERVER_POOL', 'OP_MANAGED_NODE', 'OP_DOMAIN', 'OP_IMAGE_STORE', 'OP_IMAGE_GROUP', 'OP_IMAGE', 'OP_VDC', 'OP_VDC_STORE', 'VM_OP_OPS', 'OP_CLOUD_PROVIDER', 'OP_CLOUD_PROVIDER_FOLDER', 'OP_CLOUD_TEMPLATE_LIBRARY', 'OP_CLOUD_TEMPLATE_GROUP', 'OP_CLOUD_TEMPLATES', 'OP_VDC_VM_FOLDER', 'OP_CSEP'], 'type': constants.StackOne}, {'id': 3L, 'name': 'VIEW', 'groups': ['VIEW_DATA_CENTER', 'VIEW_IMAGE_STORE', 'VIEW_SERVER_POOL', 'VIEW_MANAGED_NODE', 'VIEW_DOMAIN', 'VIEW_IMAGE_GROUP', 'VIEW_IMAGE', 'VIEW_VDC_STORE', 'VIEW_VDC_VM_FOLDER', 'VIEW_CLOUD_PROVIDER', 'CLOUD_TEMPLATES_VIEW_OPS', 'VIEW_VDC', 'VIEW_CLOUD_PROVIDER_FOLDER', 'VIEW_CLOUD_TEMPLATE_LIBRARY', 'VIEW_CLOUD_TEMPLATE_GROUP', 'VIEW_CLOUD_TEMPLATES'], 'type': constants.StackOne}, {'id': 4L, 'name': 'FULL_CLOUD', 'groups': ['FULL_CLOUD_VDC', 'CLOUD_VM_FULL_OPS', 'CLOUD_TEMPLATES_FULL_OPS', 'FULL_CLOUD_VDC_VM_FOLDER'], 'type': constants.CLOUD}, {'id': 5L, 'name': 'OPERATOR_CLOUD', 'groups': ['OP_CLOUD_VDC', 'CLOUD_VM_OP_OPS', 'CLOUD_TEMPLATES_OP_OPS', 'OP_CLOUD_VDC_VM_FOLDER'], 'type': constants.CLOUD}, {'id': 6L, 'name': 'VIEW_CLOUD', 'groups': ['VIEW_CLOUD_VDC', 'CLOUD_VM_VIEW_OPS', 'CLOUD_TEMPLATES_VIEW_OPS', 'VIEW_CLOUD_VDC_VM_FOLDER'], 'type': constants.CLOUD}]
    privileges = []
    privileges_dict = {}
    for priv in privs:
        pri = model.Privilege()
        pri.name = _(priv['name'])
        grps = priv['groups']
        pri.created_by = _('')
        pri.modified_by = _('')
        pri.created_date = datetime.now()
        pri.modified_date = datetime.now()
        pri.type = _(priv['type'])
        privileges_dict[priv['name']] = pri
        privileges.append(pri)
        for grp in grps:
            og = operations_group_dict[grp]
            pri.opGroups.append(og)
        model.DBSession.add(pri)
    return (groups, entity_types, privileges, privileges_dict, cp_types_dict)

def initialise_lookup_data():
    app_catalog = model.ApplianceCatalog(u'stackone')
    app_catalog.url = u'http://192.168.0.16/app_catalog.conf'
    if model.DBSession.query(model.ApplianceCatalog).filter(model.ApplianceCatalog.name == app_catalog.name).first() is None:
        model.DBSession.add(app_catalog)
    categories_dict = {}
    nodeinfo_categories = [
                            {'name':'general','display_name':'General'},
                            {'name':'disk','display_name':'Disk'},
                            {'name':'network','display_name':'Network'}
                          
                          ]
    for xx in nodeinfo_categories:
        category = model.Category(_(xx['name']))
        category.display_name = _(xx['display_name'])
        categories_dict[category.name] = category
        if model.DBSession.query(model.Category).filter(model.Category.name == category.name).first() is None:
            model.DBSession.add(category)
    
    nodeinfo_components = [{'type': 'cpu_info', 'display_name': 'CPU Info', 'category': 'general'}, {'type': 'os_info', 'display_name': 'OS Info', 'category': 'general'}, {'type': 'memory_info', 'display_name': 'Memory Info', 'category': 'general'}, {'type': 'platform_info', 'display_name': 'Platform Info', 'category': 'general'}, {'type': 'disk_info', 'display_name': 'Disk Info', 'category': 'disk'}, {'type': 'network_info', 'display_name': 'Interface Name', 'category': 'network'}, {'type': 'nic_info', 'display_name': 'NIC Info', 'category': 'network'}, {'type': 'bridge_info', 'display_name': 'Bridge Info', 'category': 'network'}, {'type': 'default_bridge', 'display_name': 'Default Bridge', 'category': 'network'}, {'type': 'virt_nw_info', 'display_name': 'Virtual Network Info', 'category': 'network'}, {'type': 'storage_info', 'display_name': 'Storage Info', 'category': 'disk'}]
    for xx in nodeinfo_components:
        comp=model.Component(_(xx['type']))
        comp.display_name=_(xx['display_name'])
        comp.category=categories_dict[_(xx['category'])]
        if model.DBSession.query(model.Component).filter(model.Component.type == comp.type).first() is None:
            model.DBSession.add(comp)

def _(name):
    return to_unicode(name)
def op_platform_type(update_from_version):
    from stackone.model.PlatformType import PlatformType
    VMW = constants.PLT_VMW
    KVM = constants.PLT_KVM
    XEN = constants.PLT_XEN
    VCENTER = constants.VCENTER
    platform_types = [{'name': VMW, 'desc': u'VMW', 'display': u'VMW', 'ops': ['REMOVE_SERVER', 'EDIT_SERVER', 'OPEN SSH', 'CONNECT_SERVER', 'PROVISION_VM', 'MIGRATE_SERVER', 'IMPORT_VM_CONFIG_FILE', 'START_ALL', 'SHUTDOWN_ALL', 'KILL_ALL', 'ADD_VM', 'VIEW_NODE_INFO', 'VIEW_NODE_PROPERTIES', 'VIEW_TARGET_IMAGES', 'VIEW_TARGET_IMAGE_GROUPS', 'ANNOTATE', 'PROVISION_IMAGE', 'EDIT_IMAGE_SETTINGS', 'EDIT_IMAGE_DESCRIPTION', 'CREATE_LIKE', 'RENAME_IMAGE', 'REMOVE_IMAGE', 'TRANSFER_IMAGE', 'IMAGE_TARGET_NODES', 'EDIT_VM_CONFIG_FILE', 'VIEW_VM_CONFIG_FILE', 'CONNECT_ALL', 'ADD_SERVER', 'REMOVE_SERVER_POOL', 'EDIT_GROUP_PROVISIONING_SETTINGS', 'VIEW_GROUP_PROVISIONING_SETTINGS', 'ADD_SERVER_POOL', 'CREATE_IMAGE', 'RENAME_IMAGE_GROUP', 'REMOVE_IMAGE_GROUP', 'ADD_IMAGE_GROUP', 'VIEW_IMAGE_STORE_INFO', 'VIEW_IMAGE_GROUP_INFO', 'CHANGE_VM_SETTINGS', 'VIEW_CONSOLE', 'START', 'START_VIEW_CONSOLE', 'REBOOT', 'SHUTDOWN', 'KILL', 'REMOVE_VM_CONFIG', 'REMOVE_VM', 'VIEW_VM_CONFIG_FILE', 'VIEW_VM_INFO', 'PAUSE', 'UNPAUSE']}, 
                      {'name': KVM, 'desc': u'KVM', 'display': u'KVM'}, 
                      {'name': XEN, 'desc': u'XEN', 'display': u'XEN'}, 
                      {'name': VCENTER, 'desc': u'VCENTER', 'display': u'VCENTER', 'ops': ['REMOVE_SERVER', 'EDIT_SERVER', 'OPEN SSH', 'CONNECT_SERVER', 'PROVISION_VM', 'START_ALL', 'SHUTDOWN_ALL', 'KILL_ALL', 'ADD_VM', 'VIEW_NODE_INFO', 'VIEW_NODE_PROPERTIES', 'VIEW_TARGET_IMAGES', 'VIEW_TARGET_IMAGE_GROUPS', 'ANNOTATE', 'PROVISION_IMAGE', 'EDIT_IMAGE_SETTINGS', 'EDIT_IMAGE_DESCRIPTION', 'CREATE_LIKE', 'RENAME_IMAGE', 'REMOVE_IMAGE', 'TRANSFER_IMAGE', 'IMAGE_TARGET_NODES', 'CHANGE_VM_SETTINGS', 'VIEW_CONSOLE', 'START', 'START_VIEW_CONSOLE', 'REBOOT', 'SHUTDOWN', 'KILL', 'REMOVE_VM', 'VIEW_VM_INFO', 'SUSPEND', 'RESUME', 'CREATE_IMAGE_FROM_VM', 'CONNECT_ALL', 'REMOVE_SERVER_POOL', 'EDIT_GROUP_PROVISIONING_SETTINGS', 'VIEW_GROUP_PROVISIONING_SETTINGS', 'PROVISION_GROUP_VM', 'RENAME_IMAGE_GROUP', 'REMOVE_IMAGE_GROUP', 'VIEW_IMAGE_GROUP_INFO', 'ADD_IMAGE_GROUP', 'VIEW_IMAGE_STORE_INFO', 'CREATE_IMAGE', 'VIEW_CONSOLE', 'START', 'START_VIEW_CONSOLE', 'REBOOT', 'SHUTDOWN', 'KILL', 'REMOVE_VM', 'VIEW_VM_INFO', 'PAUSE', 'UNPAUSE']}]
    platform_types_dict = {}
    for platform_type in platform_types:
        pft = PlatformType(platform_type['name'], platform_type['display'], platform_type['desc'])
        model.DBSession.add(pft)
        platform_types_dict[platform_type['name']] = pft
        platform_types_dict[platform_type['name'] + '_OPS'] = platform_type.get('ops')
    all_ops = model.DBSession.query(model.Operation).all()
    all_platforms = [KVM, XEN]
    for op in all_ops:
        for plt in all_platforms:
            po = platform_types_dict[plt]
            op.platformType.append(po)
        model.DBSession.add(op)
    v_platforms = [VMW, VCENTER]
    for plt in v_platforms:
        po = platform_types_dict[plt]
        ops_name = platform_types_dict[plt + '_OPS']
        ops = model.DBSession.query(model.Operation).filter(model.Operation.name.in_(ops_name)).all()
        for op in ops:
            op.platformType.append(po)
            model.DBSession.add(op)



