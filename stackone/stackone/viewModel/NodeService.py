import stat
import time
import os
import calendar
from datetime import datetime, timedelta
from stackone.core.utils import utils
from stackone.core.utils.utils import *
from stackone.core.utils.utils import constants, is_host_remote, convert_to_CMS_TZ
from stackone.core.utils.utils import populate_node_filter, dynamic_map, get_platform_name
from stackone.core.utils.utils import to_unicode, to_str, print_traceback, p_timing_start, p_timing_end
from stackone.model.Groups import ServerGroup
from stackone.viewModel.NodeInfoVO import NodeInfoVO
from stackone.core.utils.phelper import AuthenticationException
import Basic
import simplejson as json
from stackone.model.VM import vifEntry
from stackone.model.VM import ImageDiskEntry
from stackone.model.VM import VM
from stackone.model.ManagedNode import ManagedNode
from stackone.core.ha.ha_fence import *
from stackone.model import DBSession
from stackone.model.Entity import Entity, EntityAttribute, EntityType
from stackone.model.UpdateManager import UIUpdateManager
from stackone.model.Backup import BackupManager
from stackone.model.storage import StorageManager, StorageDef
from stackone.model.network import NwManager
from stackone.model.services import Task
from stackone.model.SPRelations import StorageDisks, SPDefLink
from stackone.model.IPManager import IPManager
from stackone.model import DBSession
from stackone.model.LicenseManager import check_platform_expire_date
from stackone.core.utils.NodeProxy import *
from stackone.core.platforms.vmw.ESXiProxy import *
from stackone.model.Sites import Site
from stackone.model.ImageStore import ImageStore, ImageGroup
import logging
import tg
import transaction
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from sqlalchemy.orm import eagerload
LOGGER = logging.getLogger('stackone.viewModel')
class NodeService():
    def __init__(self):
        self.manager = Basic.getGridManager()

    def get_dom(self, auth, domId, nodeId=None):
        if nodeId is not None:
            node = self.get_managed_node(auth, nodeId)
            return node.get_dom(domId)
        return self.manager.get_dom(auth, domId)

    def get_managed_node(self, auth, nodeId):
        managed_node = self.manager.getNode(auth, nodeId)
        return managed_node

    def get_nodes(self, auth, groupId):
        return self.manager.getNodeList(auth, groupId)

    def get_managed_nodes(self, auth, groupId, site_id=None):
        result = []
        try:
            if site_id == 'data_center':
                site = self.manager.getSiteByGroupId(groupId)
                if site:
                    site_id = site.id
            if groupId:
                node_list = self.get_nodes(auth, groupId)
                for node in node_list:
                    tmp = {}
                    tmp['hostname'] = node.hostname
                    tmp['platform'] = node.platform
                    tmp['group'] = groupId
                    tmp['id'] = node.id
                    result.append(tmp)
            elif site_id:
                group_list = self.manager.getGroupList(auth, site_id)
                if group_list:
                    for group in group_list:
                        if group:
                            node_list = self.get_nodes(auth, group.id)
                            for node in node_list:
                                tmp = {}
                                tmp['hostname'] = node.hostname
                                tmp['platform'] = node.platform
                                tmp['group'] = groupId
                                tmp['id'] = node.id
                                result.append(tmp)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return "{success: false,msg:' " + to_str(ex).replace("'", '') + "'}"
        return dict(success=True, rows=result)
        
    def get_group(self, auth, groupId):
        return self.manager.getGroup(auth, groupId)

    def get_groups(self, auth):
        return self.manager.getGroupList(auth)

    def get_nav_nodes(self, auth):
        result = []
        if not stackone.model.LicenseManager.is_cms_allowed():
            return result
        dcs = self.manager.getDataCenters()
        if not dcs:
            raise Exception('No DataCenter Found.')
        for dc in dcs:
            dc_ent = auth.get_entity(dc.id)
            if dc_ent:
                plt = dc.get_platform()
                childnode = NodeService().get_childnodestatus(auth, dc.id)
                d = dict(NODE_NAME=dc.name, NODE_ID=dc.id, NODE_TYPE=constants.DATA_CENTER,ICONSTATE = plt+'_'+constants.DATA_CENTER, NODE_CHILDREN=childnode, SORT_TEXT='1')
                result.append(d)
            iss = self.manager.getImageStores(auth,dc_ent)
            
            for store in iss:
                if auth.get_entity(store.id):
                    childnode = NodeService().get_childnodestatus(auth, store.id)
                    i = dict(NODE_NAME=store.name, NODE_ID=store.id, NODE_TYPE=constants.IMAGE_STORE, NODE_CHILDREN=childnode, SORT_TEXT='2')
                    result.append(i)
        return result

    def get_cloudnav_nodes(self, auth):
        if stackone.model.LicenseManager.is_cloud_license_violated():
            return []
        cps = auth.get_entities(constants.CLOUD_PROVIDER_FOLDER)
        vdcs = auth.get_entities(constants.VDC_FOLDER)
        result = []
        for cp in cps:
            childnode = NodeService().get_childnodestatus(auth, cp.entity_id)
            c = dict(NODE_NAME=cp.name, NODE_ID=cp.entity_id, NODE_TYPE=constants.CLOUD_PROVIDER_FOLDER, NODE_CHILDREN=childnode, CP_TYPE='ALL', SORT_TEXT='3')
            result.append(c)
        for vdcstore in vdcs:
            childnode = NodeService().get_childnodestatus(auth, vdcstore.entity_id)
            vdc = dict(NODE_NAME=vdcstore.name, NODE_ID=vdcstore.entity_id, NODE_TYPE=constants.VDC_FOLDER, NODE_CHILDREN=childnode, CP_TYPE='ALL', SORT_TEXT='4')
            result.append(vdc)
        if len(result) == 0:
            vdcs = auth.get_entities(constants.VDC)
            if vdcs:
                for vdc in vdcs:
                    cp_type = VDCManager().get_vdc_provider_type(vdc.entity_id)
                    if stackone.model.LicenseManager.is_cloud_plugin_enabled(cp_type):
                        result.append(dict(NODE_TYPE=constants.VDC, NODE_ID=vdc.entity_id, NODE_NAME=vdc.name, NODE_CHILDREN=True, CP_TYPE=cp_type))
                return sorted(result, key=(lambda x: x['NODE_NAME']))
        return result
    
    def get_entitychildren(self, auth, entity_id):
        try:
            entity = auth.get_entity(entity_id)
            if entity is not None:
                children = []
                for child in auth.get_child_entities(entity):
                    children.append(dict(name=child.name, type=child.type.name, id=child.entity_id))
                return {'success': True, 'children': children}
            return {'success': False, 'msg': 'The Entity is not found'}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    def get_platforms(self):
        try:
            #add 0901
            from stackone.model.LicenseManager import check_server_platform
            result = []
            registry = Basic.getPlatformRegistry()
            for plat,info in registry.get_platforms().iteritems():
                ok,msg = check_server_platform(None, plat)
                if ok and info['name']!='Xen':
                    result.append(dict(name = info['name'], value = plat))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
        return result

    def get_provider_types(self, _dc=None):
        try:
            result = []
            for ttype, txt in constants.cp_types.items():
                if stackone.model.LicenseManager.is_cloud_plugin_enabled(ttype):
                    d = {'name': txt, 'value': ttype}
                    result.append(d)
            return sorted(result, key=(lambda x: x['name']))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
        return result


    def get_cp(self, _dc=None):
        try:
            result = []
            cps = DBSession.query(CloudProvider).all()
            for cp in cps:
                d = {'name': cp.name, 'value': cp.provider_type, 'cp_id': cp.id}
                result.append(d)
            return sorted(result, key=(lambda x: x['name']))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
        return result

    def get_platform(self, auth, nodeId, type):
        platform = ''
        image = None
        managed_node = None
        if type == constants.MANAGED_NODE:
            managed_node = self.get_managed_node(auth, nodeId)
            if managed_node is None:
                raise Exception('Can not find the specified Node.')
            platform = managed_node.get_platform()
        elif type == constants.IMAGE:
            image_store = Basic.getImageStore()
            image = image_store.get_image(auth, nodeId)
            if image is None:
                raise Exception('Can not find the Image.')
            platform = image.type
        elif type == constants.DOMAIN:
            vm = self.get_dom(auth, nodeId)
            if vm is None:
                raise Exception('Can not find the vm.')
            platform = vm.get_platform()
        elif type == constants.SERVER_POOL:
            sp = ServerGroup.get_server_pool(nodeId)
            if sp is None:
                raise Exception('Can not find the ServerPool.')
            platform = sp.get_platform()
        elif type == constants.DATA_CENTER:
            dc = Site.get_datacenter(nodeId)
            if dc is None:
                raise Exception('Can not find the DataCenter.')
            platform = dc.get_platform()
        elif type == constants.IMAGE_STORE:
            image_store = ImageStore.get_image_store(nodeId)
            if image_store is None:
                raise Exception('Can not find the ImageStore.')
            platform = image_store.get_platform()
        elif type == constants.IMAGE_GROUP:
            image_group = ImageGroup.get_image_group(nodeId)
            if image_group is None:
                raise Exception('Can not find the ImageGroup.')
            platform = image_group.get_platform()
        elif type in [constants.CLOUD_PROVIDER_FOLDER, constants.CLOUD_PROVIDER, constants.VDC_FOLDER, constants.VDC, constants.VDC_VM_FOLDER, constants.TMP_LIB, constants.CLOUD_TMPGRP, constants.CLOUD_TEMP]:
            platform = constants.GENERIC
        return platform
 #   def get_platform(self, auth, nodeId, type):
 #       platform = ''
 #       image = None
 #       managed_node = None
 #       if type == constants.MANAGED_NODE:
 #           managed_node = self.get_managed_node(auth, nodeId)
 #           if managed_node is None:
 #               raise Exception('Can not find the specified Node.')
 #           platform = managed_node.get_platform()
 #       elif type == constants.IMAGE:
 #           image_store = Basic.getImageStore()
 #           image = image_store.get_image(auth, nodeId)
 #           if image is None:
 #               raise Exception('Can not find the Image.')
 #           platform = image.get_platform()
 #       return platform

    def get_vnc_info(self, auth, nodeId, domId, address):
        result = self.manager.get_vnc_info_use_vnc_applet(auth, nodeId, domId, address)
        return result

    def get_ssh_info(self, auth, nodeId, address, client_platform):
        result = self.manager.get_ssh_info(auth, nodeId, address, client_platform)
        return result

    def delete(self, auth, domId, nodeId):
        self.manager.remove_vm(auth, domId, nodeId)
    
    def server_action(self, auth, nodeId, action):
        managed_node = self.get_managed_node(auth, nodeId)
        if managed_node is not None:
            if not managed_node.is_authenticated():
                try:
                    managed_node.connect()
                except Exception as e:
                    return "{success:false,msg: '" + to_str(e).replace("'", '') + "'}"
            try:
                self.manager.do_node_action(auth, nodeId, action)
            except Exception as e:
                return "{success: false,msg:'" + to_str(e).replace("'", '') + "'}"
            return "{success: true,msg:'Operation Completed Successfully.'}"
        else:
            return "{success:false,msg: 'Can not find the Managed Node'}"
        
    def get_node_info(self, auth, nodeId):
        try:
            result = []
            managed_node = self.get_managed_node(auth, nodeId)
            result.extend(self.getDictInfo(managed_node.get_platform_info(), managed_node.get_platform_info_display_names(), 'Platform Info'))
            result.extend(self.getDictInfo(managed_node.get_os_info(), managed_node.get_os_info_display_names(), 'OS Info'))
            result.extend(self.getDictInfo(managed_node.get_cpu_info(), managed_node.get_cpu_info_display_names(), 'CPU Info'))
            result.extend(self.getDictInfo(managed_node.get_memory_info(), managed_node.get_memory_info_display_names(), 'Memory Info'))
            result.extend(self.getListInfo(managed_node.get_disk_info(), managed_node.get_disk_info_display_names(), 'Disk Info'))
            result.extend(self.getListInfo(managed_node.get_network_info(), managed_node.get_network_info_display_names(), 'Network Info'))
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            print_traceback()
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")
        return dict(success='true', rows=result)

    def refresh_node_info(self, auth, nodeId):
        try:
            result = []
            managed_node = self.get_managed_node(auth, nodeId)
            managed_node.refresh_environ()

        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            print_traceback()
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")
        return dict(success='true', rows=result)
    
    def entity_context(self, auth, node_id):
        try:
            entity_det = auth.get_entity(node_id)
            state = VM.SHUTDOWN
            if entity_det.type.name == constants.DOMAIN:
                vm = DBSession.query(VM).filter(VM.id==entity_det.entity_id).options(eagerload("current_state")).first()
                state = vm.current_state.avail_state
            entity={"node_id":node_id,"node_text":entity_det.name,"node_type":entity_det.type.name,"state":state}
            parent=self.get_parent_id(auth,node_id)
            g_parent=self.get_parent_id(auth, parent.get("node_id"))

        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            print_traceback()
            raise ex
        return dict(entity=entity, parent=parent, g_parent=g_parent)

    def get_parent_id(self, auth, node_id):
        try:
            entity = auth.get_entity(node_id)
            (parent_id, parent_name, parent_type) = ('', '', '')
            if entity.parents:
                parent_id = entity.parents[0].entity_id
                parent_name = entity.parents[0].name
                parent_type = entity.parents[0].type.name
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            print_traceback()
            raise ex
        return dict(node_id=parent_id, node_text=parent_name, node_type=parent_type)

    def get_childnodestatus(self, auth, node_id):
        try:
            childnode = False
            entity = auth.get_entity(node_id)
            if entity is not None:
                children = auth.get_child_entities(entity)
                if children:
                    childnode = True
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            print_traceback()
            raise ex
        return childnode

    def get_updated_entities(self, user_name, group_names):
        try:
            updatemgr = UIUpdateManager()
            updated_entities = updatemgr.get_updated_entities(user_name, group_names)
            return updated_entities
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            print_traceback()
            raise ex

    def get_vm_info(self, auth, domId):
        try:
            result = []
            vm = self.get_dom(auth, domId)
            platform = vm.get_platform()
            registry = Basic.getPlatformRegistry()
            web_helper = registry.get_web_helper(platform)
            vm_info_helper = web_helper.get_vm_info_helper()
            result = vm_info_helper.get_vm_info(vm)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")
        return dict(success='true', rows=result)
    
    def get_vm_config_file(self, auth, domId, nodeId):
        text = ''
        managed_node = self.get_managed_node(auth, nodeId)
        if not managed_node.is_authenticated():
            managed_node.connect()
        dom = self.get_dom(auth, domId)
        vmconfig = dom.vm_config
        text = to_str(vmconfig)
        return text

    def save_vm_config_file(self, auth, domId, nodeId, content):
        try:
            self.manager.save_dom_config_file(auth, domId, nodeId, content)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")
        return "{success: true,msg: 'Success'}"
        
    def remove_vm_config_file(self, auth, domId, nodeId):
        try:
            self.manager.remove_dom_config_file(auth, domId, nodeId)
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex

    def migrate_vm(self, auth, dom_name, domId, source_nodeId, dest_nodeId, live, force, all):
        try:
            managed_node = self.get_managed_node(auth, source_nodeId)
            dest_node = self.get_managed_node(auth, dest_nodeId)
            vm_list = []
            dom_list = []
            if all == 'true':
                for vm in self.manager.get_node_doms(auth, source_nodeId):
                    if managed_node.is_up():
                        vm = managed_node.get_dom(vm.id)
                    vm_list.append(vm)
                    dom_list.append(vm.id)
            else:
                dom = self.manager.get_dom(auth, domId)
                if managed_node.is_up():
                    dom = managed_node.get_dom(dom.id)
                vm_list = [dom]
                dom_list.append(dom.id)
            isLive = False
            isForce = False
            e = []
            w = []
            if live == 'true':
                isLive = True
            if force == 'true':
                isForce = True
            if dest_node.is_up():
                dest_node.connect()
            if not isForce:
                e, w = managed_node.migration_checks(vm_list, dest_node, isLive)
            result = []
            if not isForce and len(e) > 0 or len(w) > 0:
                for err in e:
                    (cat, msg) = err
                    result.append(dict(type='error', category=cat, message=msg))
                for warn in w:
                    (cat, msg) = warn
                    result.append(dict(type='warning', category=cat, message=msg))
                return dict(success=True, rows=result)
            result = {}
            result['dom_list'] = dom_list
            result['submit'] = True
            return result
        except Exception as e:
            print_traceback()
            LOGGER.error(to_str(e))
            return dict(success=False, msg=to_str(e).replace("'", ''))
        return dict(success=True, msg='Migrate task submitted.')

    def get_node_properties(self, auth, nodeId):
        managed_node = self.get_managed_node(auth, nodeId)
        #add 0901
        ret,msg = check_platform_expire_date(managed_node.get_platform())
        if ret == False:
            raise Exception(msg)
        pltfrm = self.manager.getPlatform(managed_node.type)
        auto_disc = pltfrm.is_auto_discover()
        return NodeInfoVO(managed_node,auto_disc)

    def connect_node(self, auth, nodeId, username, password):
        result = dict(success=True, msg='Success')
        managed_node = self.get_managed_node(auth, nodeId)
        credentials = managed_node.get_credentials()
        old_pwd = credentials['password']
        old_usr = credentials['username']
        if username != '' and username != None:
            credentials['username'] = username
            if password == None:
                password = ''
            credentials['password'] = password
            managed_node.set_node_credentials(managed_node.credential.cred_type, **credentials)
        try:
            #add 0901
            ret,msg = check_platform_expire_date(managed_node.get_platform())
            if ret == False:
                raise Exception(msg)
            if not managed_node.is_authenticated():
                managed_node.connect()
            managed_node.refresh_environ()
        except AuthenticationException as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            result = dict(success=False, msg=to_str(ex).replace("'", ''), error='Not Authenticated')
        except Exception as ex:
            print_traceback()
            result = dict(success=False, msg=to_str(ex).replace("'", ''))
        if result['success'] == False:
            credentials['username'] = old_usr
            credentials['password'] = old_pwd
            managed_node.set_node_credentials(managed_node.credential.cred_type, **credentials)
        return result

    def disconnect_node(self, auth, nodeId):
        managed_node = self.get_managed_node(auth, nodeId)
        if managed_node is None:
            pass
        else:
            managed_node.disconnect()
        return None
    def get_data_store(self, auth, host_id):
        result = []
        if host_id:
            node = DBSession.query(ManagedNode).filter(ManagedNode.id == host_id).first()
            if node:
                datastore = node.node_proxy.get_datastores()
                for data in datastore:
                    result.append({'id':data.name,'name':data.name})
        return result
        
    ####pass
    def add_node(self, auth, groupId, platform, hostname, ssh_port, username, password, protocol, xen_port, xen_migration_port, use_keys, address=None, is_standby='False', external_manager_id=None, external_id=None):
        factory = self.manager.getFactory(platform)
        if address is None:
            address = hostname
        if use_keys == 'true':
            usekeys = True
        else:
            usekeys = False
        isRemote = is_host_remote(hostname)
        msg = 'Server Added'
        try:
            node = factory.create_node(platform = platform, hostname = hostname, username = username, password = password, is_remote = isRemote,  ssh_port = int(ssh_port),  use_keys = usekeys, address = address,  protocol =protocol, tcp_port = int(xen_port), migration_port = int(xen_migration_port), external_manager_id = external_manager_id)
            node.connect()
            if usekeys:
                local_node = Basic.getManagedNode()
                if node.is_script_execution_supported():
                    setup_ssh_keys(node, local_node)
            node.set_standby(eval(is_standby))
            self.manager.addNode(auth, node, groupId,external_id,external_manager_id)
            pltfrm = self.manager.getPlatform(platform)
            auto_disc = pltfrm.is_auto_discover()
            if auto_disc:
                try:
                    from stackone.viewModel.TaskCreator import TaskCreator
                    tid = TaskCreator().import_vm_action(auth, node.id, 'import_vms', paths = '', external_manager_id = external_manager_id)
                    msg += '<br>Import Virtual Machine Task Submitted'
                except Exception as ex:
                    traceback.print_exc()
            nodeobj = NodeInfoVO(node, auto_disc)
            node_id = node.id
        except Exception as ex:
            err = to_str(ex).replace("'", ' ')
            LOGGER.error(':' + err)
            print_traceback()
            return dict( success = False,  msg = err)
        return dict( success = True,  msg = msg, node_id = node_id,  nodeobj = nodeobj.toJson())
        
    def edit_node(self, auth, node_id, platform, hostname, ssh_port, username, password, protocol, xen_port, xen_migration_port, use_keys, address=None, is_standby='False'):
        factory = self.manager.getFactory(platform)
        if address is None:
            address = hostname
        if use_keys == 'true' or use_keys == True:
            usekeys = True
        else:
            usekeys = False
        isRemote = is_host_remote(hostname)
        try:
            node = self.manager.getNode(auth, node_id)
            node = factory.update_node(node, platform = platform, hostname = hostname, username = username, password = password, is_remote = isRemote, ssh_port=int(ssh_port), use_keys = usekeys, address= address, protocol = protocol, tcp_port=int(xen_port), migration_port=int(xen_migration_port))
            node.connect()
            if usekeys:
                local_node = Basic.getManagedNode()
                if node.is_script_execution_supported():
                    setup_ssh_keys(node, local_node)
            node.set_standby(eval(is_standby))
            self.manager.editNode(auth, node)
        except Exception as ex:
            print_traceback()
            err = to_str(ex).replace("'", ' ')
            LOGGER.error(':' + err)
            return dict(success=False, msg=err)
        return dict(success=True, msg='Server Updated')

    def change_server_password(self, auth, nodeids, newpassword):
        rej_nodes = []
        for nodeid in nodeids:
            node = self.get_managed_node(auth, nodeid)
            credential = self.manager.changeNodePwd(auth, node, newpassword)
            if credential != True:
                rej_nodes.append(node.hostname)
        msg = 'Password changed successfully.'
        if len(rej_nodes) > 0:
            msg += ' Password failed for following Servers :' + to_str(rej_nodes)
        return msg

    def remove_node(self, auth, nodeId, force):
        try:
            node = self.manager.getNode(auth, nodeId)
            if node is None:
                raise Exception('Can not find the server.')
            if not force:
                domlist = node.get_all_dom_names()[0]
                runningdoms = []
                try:
                    runningdoms = self.manager.get_running_doms(auth, nodeId)
                except Exception as e:
                    print 'Error getting running vm info from ' + node.hostname + '\n' + to_str(e)
                    LOGGER.error('Error getting running vm info from ' + node.hostname + '\n' + to_str(e))
                if len(runningdoms) > 0:
                    raise Exception('Can not delete the server.Running Virtual Machines exist under the Server.')
                else:
                    node_up = node.is_up()
                    return dict(success=True, vms=len(domlist), node_up=node_up)
            node = DBSession.query(Entity).filter(Entity.entity_id == nodeId).first()
            grp = node.parents[0]
            from stackone.viewModel.TaskCreator import TaskCreator
            tid = TaskCreator().remove_node(auth, nodeId, node.name, grp.entity_id, grp.name, force)
            return dict(success=True, msg='Remove Server Task Submitted.', taskid=str(tid))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
    def get_node_status(self, auth, node_id=None, dom_id=None):
        is_part_of_vdc = False
        if dom_id is not None:
            dom_ent = DBSession.query(Entity).filter(Entity.entity_id == dom_id).first()
            node_id = dom_ent.parents[0].entity_id
            ent = auth.get_entity(dom_id)
            if not auth.is_csep_user():
                if ent.csep_context_id:
                    #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEPContext
                    csep_context = CSEPContext.get_csep_context_by_id(ent.csep_context_id)
                    if not csep_context:
                        msg = 'Could not find csep context for csep_context_id:%s' %ent.csep_context_id
                        LOGGER.info(msg)
                    else:
                        vdc = VDC.get_vdc_by_id(csep_context.vdc_id)
                        if vdc:
                            is_part_of_vdc = True
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
        if node is None:
            raise Exception('Can not find the Server.')
        return {'is_up':node.is_up(),'part_of_vdc':is_part_of_vdc}

    def transfer_node(self, auth, node_id, source_group_id, dest_group_id, forcefully):
        try:
            self.manager.transferNode(auth, source_group_id, dest_group_id, node_id, forcefully)
        except Exception as ex:
            print_traceback()
            error_desc = to_str(ex).replace("'", '')
            LOGGER.error(error_desc)
            return "{success: false, msg: '" + error_desc + "'}"
        return "{success: true, msg: 'Success'}"
        
    def edit_vm_information(self, auth, nodeid, domid, memory, cpu):
        dom = self.get_dom(auth, domid, nodeid)
        result = self.manager.cli_edit_vm(auth, dom, memory, cpu)
        return result

    def import_vm_config(self, auth, nodeId, directory, filenames):
        try:
            file_list = []
            file_list = filenames.split(',')
            self.manager.import_dom_config(auth, nodeId, directory, file_list)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def get_alloc_node(self, auth, groupId, imageId):
        try:
            group = self.manager.getGroup(auth, groupId)
            image = None
            if imageId is not None:
                image_store = Basic.getImageStore()
                image = image_store.get_image(auth, imageId)
            policy_ctx = dynamic_map()
            policy_ctx.image = image
            node = group.getAllocationCandidate(auth, policy_ctx)
            if node is None:
                raise Exception('Did not find any suitable server in ' + group.name + '. Some of the reasons can be : 1.Not connected to server.' + '2.Server is not capable of provisioning the image. ' + '3.No server has enough free memory.')
            print dict(success='true', node=dict(name=node.hostname, nodeid=node.hostname, id=node.id))
            return dict(success='true', node=dict(name=node.hostname, nodeid=node.hostname, id=node.id))
        except Exception as ex:
            print_traceback()
            err = to_str(ex).replace("'", ' ')
            LOGGER.error(err)
            return ("{success: false,msg: 'Error:", err, "'}")

    def get_target_nodes(self, auth, node_id=None, image_id=None):
        platform = None
        image = None
        managed_node = None
        if node_id:
            managed_node = self.get_managed_node(auth, node_id)
            if managed_node is None:
                raise Exception('Can not find the specified Node.')
            platform = managed_node.get_platform()
        else:
            if image_id:
                image_store = Basic.getImageStore()
                image = image_store.get_image(auth, image_id)
        grps = self.get_groups(auth)
        result = []
        for grp in grps:
            list = []
            nodes = self.get_nodes(auth, grp.id)
            for node in nodes:
                if node.id != node_id:
                    try:
                        node.connect()
                    except Exception as e:
                        pass
                    if node.is_authenticated():
                        if populate_node_filter(node, platform, image):
                            list.append(dict(name=node.hostname, id=node.id, platform=node.platform, type=constants.MANAGED_NODE, children=[]))
            result.append(dict(name=grp.name, id=grp.id, type=constants.SERVER_POOL, children=list))
        return result

    def get_migrate_target_sps(self, auth, node_id=None, sp_id=None):
        grps = self.get_groups(auth)
        result = []
        for grp in grps:
            if grp.id != sp_id:
                result.append(dict(name=grp.name, id=grp.id, type=constants.SERVER_POOL))
        return result

    def get_target_doms(self, auth):
        platform = None
        image = None
        grps = self.get_groups(auth)
        result = []
        for grp in grps:
            list = []
            nodes = self.get_nodes(auth, grp.id)
            for node in nodes:
                vm_list = []
                doms = self.manager.get_doms(auth, node.id)
                for dom in doms:
                    vm_list.append(dict(name=dom.name, id=dom.id, platform=None, type=constants.DOMAIN, children=[]))
                try:
                    node.connect()
                except Exception as e:
                    pass
                if node.is_authenticated():
                    if populate_node_filter(node, platform, image):
                        list.append(dict(name=node.hostname, id=node.id, platform=node.platform, type=constants.MANAGED_NODE, children=vm_list))
            result.append(dict(name=grp.name, id=grp.id, type=constants.SERVER_POOL, children=list))
        return result

    def get_boot_device(self, auth, domId):
        try:
            dom = self.get_dom(auth, domId)
            vm_config = dom.get_config()
            if not vm_config:
                return "{success: false,msg: 'No configuration file associated with this VM.'}"
            boot_image = vm_config['boot']
            if boot_image is None:
                boot_image = ''
            return "{success: true,msg: 'Success',boot:'" + boot_image + "'}"
        except Exception as ex:
            print_traceback()
            err = to_str(ex).replace("'", ' ')
            LOGGER.error(err)
            return ("{success: false,msg: 'Error:", err, "'}")
        
    def set_boot_device(self, auth, domId, boot):
        try:
            dom = self.get_dom(auth, domId)
            self.manager.set_dom_device(auth, dom, boot)
            msg = 'Success'
            running = 'false'
            if dom.is_resident():
                msg = 'The VM is running. <br/>The new Boot Location will take effect when VM is restarted.'
                running = 'true'
            return "{success: true,msg: '" + msg + "',running:'" + running + "'}"
        except Exception as ex:
            print_traceback()
            err = to_str(ex).replace("'", ' ')
            LOGGER.error(err)
            return ("{success: false,msg: 'Error:", err, "'}")
 
    def add_group(self, auth, name, site_id):
        group = ServerGroup(name)
        self.manager.addGroup(auth, group, site_id)
        return group

    def get_group_vars(self, auth, group_id):
        result = []
        try:
            group_vars = self.manager.getGroupVars(auth, group_id)
            id = 0
            for key in group_vars:
                result.append(dict(id=id, variable=key, value=group_vars[key]))
                id = id + 1
        except Exception as ex:
            print_traceback()
            return dict(success='false', msg=to_str(ex).replace("'", ''))
        return dict(success='true', rows=result)
        
    def save_group_vars(self, auth, group_id, group_vars):
        try:
            groupvars = {}
            for k, v in group_vars.iteritems():
                v = group_vars[k]
                if v and v[0] == '*':
                    continue
                else:
                    groupvars[k] = v
            self.manager.setGroupVars(auth, group_id, groupvars)
        except Exception as ex:
            print_traceback()
            return dict(success='false', msg=to_str(ex).replace("'", ''))
        return dict(success='true', msg='Success')

    def remove_group(self, auth, group_id):
        for node in self.manager.getNodeList(auth, group_id):
            runningdoms = self.manager.get_running_doms(auth, node.id)
            if len(runningdoms) > 0:
                raise Exception('Can not delete the Server Pool.                    Running Virtual Machines exist under the Server Pool.')
        self.manager.removeGroup(auth, group_id, True)

    def mig_down_vms(self, auth, group_id, status):
        try:
            entity = DBSession.query(Entity).filter(Entity.entity_id == group_id).first()
            entity_attr = DBSession.query(EntityAttribute).filter(EntityAttribute.entity_id == group_id).filter(EntityAttribute.name == 'dwm_ps_migrate_down_vms').first()
            if not entity_attr:
                ea = EntityAttribute('dwm_ps_migrate_down_vms', status)
                entity.attributes.append(ea)
            else:
                entity_attr.value = status
                DBSession.add(entity_attr)
        except Exception as ex:
            import traceback
            traceback.print_exc()

    def get_dir_contents(self, auth, nodeId=None, directory=None):
        managed_node = None
        if nodeId is None:
            managed_node = Basic.local_node
        else:
            managed_node = self.get_managed_node(auth, nodeId)
        if managed_node is None:
            raise Exception('Cannot find the Managed Node.')
        else:
            if not managed_node.is_authenticated():
                managed_node.connect()
        return self.list_dir_contents(managed_node, directory, None, True)

    def list_dir_contents(self, managed_node, directory=None, running_vms=None, show_parent=False):
        if not directory:
            dirs = managed_node.get_config_dir()
        else:
            dirs = directory
        dir_entries = managed_node.node_proxy.get_dir_entries(dirs)
        result = []
        counter = 1
        for entry in dir_entries:
            mod_date = time.strftime('%a %b %d %Y %H:%M:%S', time.localtime(entry['mtime']))
            counter = counter + 1
            status_icon = ''
            if running_vms is not None and not entry['isdir']:
                vm_status,vm_config_exists = self.get_vm_status(managed_node, entry['path'], running_vms, entry['size'])
                if vm_status and vm_config_exists:
                    status_icon = "<img width='13' height='13' src='../icons/small_started_state.png'/>"
                else:
                    if not vm_status and vm_config_exists:
                        status_icon = "<img width='13' height='13' src='../icons/small_shutdown.png'/>"
            result.append(dict(id=counter, name=entry['filename'], path=entry['path'], size=entry['size'], date=mod_date, isdir=entry['isdir'], status_icon=status_icon))
        if show_parent == True:
            parent = os.path.abspath(os.path.join(directory, '..'))
            result.append(dict(id=counter + 1, name='..', path=parent, size='', isdir=True))
        return result

    def list_vm_configs(self, auth, nodeId, directory=None):
        result = []
        managed_node = self.get_managed_node(auth, nodeId)
        running_vms = managed_node.get_running_vms()
        if directory is None or directory == '':
            dirct = tg.config.get(constants.CONFIG_DIRECTORIES)
            directories = dirct.split(';')
            for dirs in directories:
                try:
                    result.extend(self.list_dir_contents(managed_node, dirs, running_vms, False))
                except Exception as e:
                    LOGGER.error(to_str(e).replace("'", ''))
            return result
        result = self.list_dir_contents(managed_node, directory, running_vms, True)
        return result

    def get_vm_status(self, managed_node, file, running_vms, file_size):
        status = False
        vm_config_exists = False
        try:
            if file_size < 2048:
                config = managed_node.new_config(file)
                vm_config_exists = True
                if running_vms.has_key(config['name']):
                    status = True
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
        return (status, vm_config_exists)

    def make_dir(self, auth, nodeId, directory, dir):
        try:
            managed_node = self.get_managed_node(auth, nodeId)
            if managed_node is None:
                raise Exception('Cannot find the Managed Node.')
            else:
                if not managed_node.is_authenticated():
                    managed_node.connect()
            utils.mkdir2(managed_node, os.path.join(directory, dir))
        except Exception as ex:
            print_traceback()
            strerror = to_str(ex).replace("'", ' ')
            return ("{success: false,msg: '", strerror, "'}")
        return ("{success: true,msg: 'Successfully created.',newdir:'", os.path.join(directory, dir), "'}")
        
    def getListInfo(self, value_list, display_dict, type1):
        ret_list = []
        if value_list is None:
            return []
        display_list = ['', '', '']
        i = 0
        for name in display_dict:
            display_list[i] = display_dict[name]
            i = i + 1
        ret_list.append(dict(label=display_list[0], value=display_list[1], extra=display_list[2], type=type1))
        for i in range(len(value_list)):
            value_dict = value_list[i]
            column_value = ['', '', '']
            j = 0
            for name in value_dict:
                value = value_dict[name]
                if type(value) == int:
                    value = to_str(value)
                column_value[j] = value.rstrip().lstrip()
                j = j + 1
            ret_list.append(dict(id=type1 + to_str(i), label=column_value[0L], value=column_value[1L], extra=column_value[2L], type=type1))
        return ret_list

    def getDictInfo(self, value_dict, display_dict, type):
        ret_list = []
        mod_dict = self.decorateDictInfo(value_dict, display_dict)
        i = 0
        for key in mod_dict:
            ret_list.append(dict(id=type + to_str(i), label=key, value=mod_dict[key], type=type, extra=''))
            i = i + 1
        return ret_list

    def decorateDictInfo(self, value_dict, display_dict):
        mod_dict = {}
        if value_dict is not None:
            for name in display_dict:
                value = value_dict.get(name)
                if  value:
                    if type(value) == int:
                        value = to_str(value)
                        value = value.rstrip().lstrip()
                mod_dict[display_dict[name]] = value
        return mod_dict
      
    def node_provision_vm(self, auth, group_id, node_id, image_id, vmname, memory, vcpu, cloud, csep_context, vm_disks=None, network={}, csep_id=None, vdc_name=None):
        nw_name = None
        try:
            if not vm_disks:
                vm_disks = []
            mode = 'PROVISION_VM'
            image_store = Basic.getImageStore()
            managed_node = self.get_managed_node(auth, node_id)
            eGroup = self.get_group(auth, group_id)
            storage_manager = StorageManager()
            image = image_store.get_image(auth, image_id)
            context = util_provision_vm(auth, image_store, image, image_id, eGroup, managed_node, storage_manager, vmname, memory, vcpu)
            context.csep_context = csep_context
            image_config = context.image_config
            vm_config = context.vm_config
            disks = []
            disk_entries = []
            template_cfg = []
            d_list_to_create = []
            for disk in vm_config.getDisks(image_config):
                (filename, storage_id, storage_name, storage_type,storage_disk_id,is_new_disk) = self.process_filename(mode, disk.filename, group_id, csep_id, vdc_name)
                disk.filename = filename
                disk_dict = {}
                disk_dict['name'] = filename
                disk_dict['type'] = disk.type
                disk_dict['size'] = disk.size
                disk_dict['fs_type'] = disk.fs_type
                disk_dict['storage_id'] = storage_id
                if is_new_disk:
                    if storage_type in StorageManager().STORAGE_FOR_CREATION:
                        d_list_to_create.append(disk_dict)
                disk_entry = disk
                temp_disk = {}
                temp_disk['DISK_TYPE'] = to_str(disk.type)
                temp_disk['FILE_NAME'] = to_str(disk.filename)
                temp_disk['DEVICE'] = to_str(disk.device)
                temp_disk['READ_WRITE'] = to_str(disk.mode)
                temp_disk['FILE_SYSTEM'] = to_str(disk.fs_type)
                temp_disk['FILE/DIRECTORY'] = ''
                temp_disk['SKIP_BACKUP'] = True
                template_cfg.append(temp_disk)
                disk_entries.append(disk_entry)
            LOGGER.info('Disks to be created are ' + to_str(d_list_to_create))
            for disk_entry in disk_entries:
                if image_config is not None:
                    image_config = self.update_device_entries(image_config, disk_entry)
                disks.append(repr(disk_entry))
            context.vm_config['disk'] = disks
            vifs = vm_config['vif']
            pre_defined_nw_ids = network.get('pre_defined_nw_ids', [])
            private_nw_ids = network.get('private_nw_ids', [])
            private_nw_ids_for_vm = network.get('private_nw_id_for_vm', [])
            nw_ids = []
            nw_ids.extend(pre_defined_nw_ids)
            nw_ids.extend(private_nw_ids_for_vm)
            use_template_nw = vm_config.get(constants.prop_use_template_nw)
            if use_template_nw == True or use_template_nw == 'true':
                use_template_nw = 1
            if use_template_nw != 1 and len(nw_ids)> 0:
                vifs = []
            for nw_id in nw_ids:
                nwdef = NwManager.get_network_by_id(nw_id)
                mac = nwdef.ipv4_info.get('mac')
                mac = '$AUTOGEN_MAC'
                bridge = nwdef.bridge_info.get('name')
                if bridge == 'Default':
                    bridge = '$DEFAULT_BRIDGE'
                vif_entry = vifEntry('mac=%s,bridge=%s,nw_id=%s' % (mac, bridge, nw_id))
                vifs.append(repr(vif_entry))
            context.vm_config['vif'] = vifs
            imagename = image.name
            result = self.manager.provision(auth, context, mode, imagename, group_id, cloud=cloud, vm_disks=vm_disks)
            config = None
            removed_disk_list = None
            vm_id = result
            action = None
            self.manager.manage_vm_disks(auth, vm_id, node_id, config, mode, removed_disk_list, action, d_list_to_create)
            NwManager().remove_network_VM_relation(vm_id)
            network_list = self.get_network_list(vm_id)
            for each_network in network_list:
                bridge_name = each_network.get('bridge')
                mac_address = each_network.get('mac')
                nw_name = None
                (nw_def_id, bridge) = NwManager().get_network(nw_name, bridge_name)
                # as bridge
                if nw_def_id:
                    LOGGER.info('Got the network')
                    pool_id = None
                    pool = IPManager().get_pool(nw_def_id)
                    if pool:
                        LOGGER.info('Got the pool')
                        pool_id = pool.id
                        ips_object = IPManager().reserve_address(pool_id, vm_id)
                        if ips_object:
                            LOGGER.info('Reserved Private IP address')
                            ip_id = ips_object.id
                            IPManager().associate_address(pool_id, ip_id, vm_id, csep_id)
                            LOGGER.info('Private IP is attached to VM')
                            NwManager().add_network_VM_relation(nw_def_id, vm_id, mac_address, ip_id)
            ip_mac_list = NwManager().get_ip_mac_list(vm_id)
            NwManager().update_dns_host_mapping(ip_mac_list, ip_mac_list_old=None)
            NwManager().restart_nw_service_for_VM(ip_mac_list)
            return result
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
    #######tianfeng
    def vm_config_settings(self, auth, image_id, config, mode, node_id, group_id, dom_id, vm_name, is_restore=False, del_vm_id=None, task_id=None):
        start = p_timing_start(LOGGER, 'vm_config_settings ')
        vm_config = None
        hex_id = getHexID()
        try:
            #5336
            if is_restore == False:
                config = json.loads(config)
            (vm_config, image_config) = (None, None)
            ctx = dynamic_map()
            image_store = Basic.getImageStore()
            image = image_store.get_image(auth, image_id)
            managed_node = None
            ctx.platform = None
            if node_id is not None:
                #243
                node_id = node_id
                managed_node = self.get_managed_node(auth,node_id)
                ctx.managed_node = managed_node
                if managed_node is None:
                    raise Exception('Cannot find the Managed Node.')
                ctx.platform = managed_node.get_platform()
            
            if image is not None:
                ctx.image_name = image.name
                ctx.image_id = image.id
                ctx.image = image
                vm_config, image_config = image.get_configs(ctx.platform)
            vm_info = None
            dom = None
            filename_list = []
            if dom_id is not None:
                dom_id = dom_id
                ctx.dom_id = dom_id
                vm = self.manager.get_dom(auth,dom_id)
                dom = managed_node.get_dom(vm.name)
                vm_config = dom.get_config()
                vm_info = dom.get_info()
                for disk in vm_config.getDisks():
                    filename_list.append(disk.filename)
            else:
                if mode == 'PROVISION_VM':
                    dom_id = vm_name
            general = config.get('general_object')
            boot_params = config.get('boot_params_object')
            misc_dic = config.get('misc_object')
            provision_dic = config.get('provision_object')
            network_dic = config.get('network_object')
            high_avail_dic = config.get('high_avail_object')
            scheduling_dic = config.get('scheduling_object')
            storage_status = config.get('storage_status_object')
            backup_status = config.get('backup_object')
            backup_config_list = backup_status.get('backup_stat')
            disk_status = storage_status.get('disk_stat')
            initial_disks = vm_config['disk']
            if image_config is not None and initial_disks is not None:
                for disk in initial_disks:
                    image_config = self.remove_device_entries(image_config, disk)
            disks = []
            disk_entries = []
            template_cfg = []
            d_list_to_create = []
            for disk in disk_status:
                #1470
                filename, storage_id, storage_name, storage_type, storage_disk_id, is_new_disk = self.process_filename(mode, disk.get('filename'), group_id)
                disk['filename'] = filename
                disk['storage_id'] = storage_id
                disk['storage_name'] = storage_name
                disk['storage_disk_id'] = storage_disk_id
                disk_dict = {}
                disk_dict['name'] = filename
                disk_dict['type'] = disk.get('type')
                disk_dict['size'] = disk.get('size')
                disk_dict['fs_type'] = disk.get('fs_type')
                disk_dict['storage_id'] = storage_id
                if is_new_disk:
                    if storage_type in StorageManager().STORAGE_FOR_CREATION:
                        d_list_to_create.append(disk_dict)
                disk_entry = ImageDiskEntry((disk.get('type'), disk.get('filename'), disk.get('device'), disk.get('mode')), image_config)
                disk_entry.option = disk.get('option')
                disk_entry.image_src = disk.get('image_src')
                disk_entry.image_src_type = disk.get('image_src_type')
                disk_entry.image_src_format = disk.get('image_src_format')
                disk_entry.disk_create = disk.get('disk_create')
                disk_entry.disk_type = disk.get('disk_type')
                d_size = disk.get('size')
                if d_size:
                    disk_entry.size = int(d_size)
                else:
                    disk_entry.size = d_size
                temp_disk = {}
                temp_disk['DISK_TYPE'] = to_str(disk.get('type'))
                temp_disk['FILE_NAME'] = to_str(disk.get('filename'))
                temp_disk['DEVICE'] = to_str(disk.get('device'))
                temp_disk['READ_WRITE'] = to_str(disk.get('mode'))
                temp_disk['FILE_SYSTEM'] = to_str(disk.get('fs_type'))
                temp_disk['FILE/DIRECTORY'] = to_str(disk.get('backup_content'))
                if disk.get('skip_backup'):
                    temp_disk['SKIP_BACKUP'] = disk.get('skip_backup')
                else:
                    temp_disk['SKIP_BACKUP'] = False
                template_cfg.append(temp_disk)
                disk_entries.append(disk_entry)
            LOGGER.info('Disks to be created are ' + to_str(d_list_to_create))
            for disk_entry in disk_entries:
                if image_config is not None:
                    image_config = self.update_device_entries(image_config, disk_entry)
                disks.append(repr(disk_entry))
            vm_config['disk'] = disks
            final_disks = disks
            s_stat = vm_config.get_storage_stats()
            for disk in disk_status:
                is_remote = disk.get('shared')
                s_stat.set_remote(disk.get('filename'), is_remote)
                storage_disk_id = unicode(disk.get('storage_disk_id'))
                s_stat.set_storage_disk_id(str(disk.get('filename')), storage_disk_id)
            net_list = network_dic.get('network')
            vifs = []
            nw_name = None
            mac_address = None
            bridge_name = None
            for net_data in net_list:
                nw_name = net_data.get('name')
                mac = net_data.get('mac')
                if mac == 'Autogenerated':
                    mac = '$AUTOGEN_MAC'
                mac_address = mac
                bridge = net_data.get('bridge')
                if bridge == 'Default':
                    bridge = '$DEFAULT_BRIDGE'
                bridge_name = bridge
                nw_id = net_data.get('nw_id')
                vif_entry = vifEntry('mac=%s,bridge=%s,nw_id=%s' % (mac, bridge, nw_id))
                vifs.append(repr(vif_entry))
            vm_config['vif'] = vifs
            for key in misc_dic:
                misc_dic[key] = process_value(misc_dic.get(key))
            for key in provision_dic:
                provision_dic[key] = process_value(provision_dic.get(key))
            err_msgs = validateVMSettings(mode, managed_node, image_store, dom_id, general.get('memory'), general.get('vcpus'))
            if len(err_msgs) > 0:
                raise Exception(err_msgs)
            if mode in ('EDIT_VM_CONFIG', 'PROVISION_VM', 'EDIT_IMAGE') and vm_config:
                for key in boot_params.keys():
                    vm_config[key] = to_str(boot_params.get(key))
                    if boot_params.get('boot_check') == True:
                        vm_config['bootloader'] = boot_params.get('boot_loader')
                        vm_config['kernel'] = ''
                        vm_config['ramdisk'] = ''
                    else:
                        vm_config['bootloader'] = ''
            if mode in ('EDIT_VM_CONFIG', 'PROVISION_VM', 'EDIT_IMAGE') and vm_config:
                for key in general.keys():
                    value = general.get(key)
                    if key in ('memory', 'vcpus'):
                        value = int(general.get(key))
                    if key  == 'filename':
                        if mode not in ('EDIT_IMAGE',):
                            vm_config.set_filename(value)
                            vm_config['config_filename'] = value
                    else:
                        vm_config[key] = value
            elif mode in ('EDIT_VM_INFO',) and vm_info is not None:
                for key in general.keys():
                    value = general.get(key)
                    if key in ('memory', 'vcpus'):
                        value = int(general.get(key))
                    if key == 'filename':
                        vm_config.set_filename(value)
                        vm_config['config_filename'] = value
                    else:
                        vm_info[key] = value
                vm_config['os_flavor'] = general.get('os_flavor')
                vm_config['os_name'] = general.get('os_name')
                vm_config['os_version'] = general.get('os_version')
                vm_config['allow_backup'] = general.get('allow_backup')
                vm_config['template_cfg'] = template_cfg
            ########################
            if mode in ('EDIT_VM_CONFIG', 'PROVISION_VM', 'EDIT_IMAGE') and vm_config:
                vm_config = self.update_config_props(vm_config, misc_dic, self.get_exclude_list())
            if mode in ('EDIT_VM_CONFIG', 'PROVISION_VM', 'EDIT_IMAGE') and vm_config:
                vm_config['quiescent_script_options'] = backup_status.get('quiescent_script_stat')
                vm_config['template_cfg'] = template_cfg
                username = backup_status.get('username')
                password = backup_status.get('password')
                ip_address = backup_status.get('ip_address')
                ssh_port = backup_status.get('ssh_port')
                use_ssh_key = backup_status.get('use_ssh_key')
                if use_ssh_key == True:
                    vm_config['use_ssh_key'] = True
                else:
                    vm_config['use_ssh_key'] = False
                vm_config['ip_address'] = ip_address
                vm_config['username'] = username
                vm_config['password'] = password
                vm_config['ssh_port'] = ssh_port
                backup_retain_days = backup_status.get('backup_retain_days')
                vm_config['backup_retain_days'] = backup_retain_days
            if mode in ('EDIT_IMAGE', 'PROVISION_VM') and image_config:
                image_config = self.update_config_props(image_config, provision_dic)
            print 'after instantiate'
            if mode in ('PROVISION_VM',):
                group = self.manager.getGroup(auth, group_id)
                storage_manager = Basic.getStorageManager()
                ctx.image_store = image_store
                ctx.image_id = image_id
                ctx.managed_node = managed_node
                ctx.vm = None
                ctx.server_pool = group
                ctx.platform = managed_node.get_platform()
                ctx.storage_manager = storage_manager
                if ctx.server_pool is not None:
                    grp_settings = ctx.server_pool.getGroupVars()
                    merge_pool_settings(vm_config, image_config, grp_settings, True)
                vm_config['name'] = vm_name
                vm_config['image_name'] = ctx.image_name
                vm_config['quiescent_script_options'] = backup_status.get('quiescent_script_stat')
                vm_config['template_cfg'] = template_cfg
                ctx.vm_config = vm_config
                ctx.image_config = image_config
            vm_id = None
            ip_mac_list_old = None
            if mode in ('PROVISION_VM', 'EDIT_VM_INFO', 'EDIT_VM_CONFIG'):
                vm_config['auto_start_vm'] = general.get('auto_start_vm')
                
            if mode == 'PROVISION_VM':
                vm_disks = self.manager.get_vm_disks_from_UI(dom_id, config)
                ctx.preferred_nodeid = general.get('preferred_nodeid')
                ctx.ha_priority = high_avail_dic.get('vm_priority')
                vm_id = self.manager.provision(auth, ctx, mode, ctx.image_name, group_id, vm_disks, is_restore, del_vm_id, scheduling_dic, task_id, hex_id)
                for backupconfig in backup_config_list:
                    backup_id = backupconfig.get('backup_id')
                    allow_backup_str = backupconfig.get('allow_backup')
                    backup_all_str = backupconfig.get('backup_all')
                    backupmanger = BackupManager()
                    if backup_all_str == 'true':
                        backupmanger.add_SPbackup_VM_list(vm_id, backup_id, True)
                    elif allow_backup_str == 'true':
                        backupmanger.add_SPbackup_VM_list(vm_id, backup_id, True)
            
            elif mode == 'EDIT_VM_INFO': 
                vm_id = dom_id
                vm_config.set_id(vm_id)
                vm_config['name'] = vm_name
                ctx.image_store = image_store
                ctx.image_id = image_id
                ctx.vm_config = vm_config
                ctx.image_config = image_config
                ctx.managed_node = managed_node
                ctx.node_id = node_id
                ctx.d_list_to_create = d_list_to_create
                d_list_to_remove = self.get_disk_list_to_remove(filename_list, disk_status)
                ctx.d_list_to_remove = d_list_to_remove
                ctx.template_version = general.get('template_version')
                ctx.ha_priority = high_avail_dic.get('vm_priority')
                ctx.preferred_nodeid = general.get('preferred_nodeid')
                vm_disks = self.manager.get_vm_disks_from_UI(dom_id, config)
                self.manager.edit_vm_info(auth, vm_config, vm_info, dom, ctx, mode, initial_disks, final_disks, group_id, vm_disks, scheduling_dic, constants.CORE, hex_id)
                ip_mac_list_old = NwManager().get_ip_mac_list(vm_id)
            
            elif mode == 'EDIT_VM_CONFIG':
                vm_id = dom_id
                vm_config.set_id(vm_id)
                vm_config['vmname'] = vm_name
                vm_config['name'] = vm_name
                ctx.image_id = image_id
                ctx.image_store = image_store
                ctx.vm_config = vm_config
                ctx.image_config = image_config
                ctx.managed_node = managed_node
                ctx.node_id = node_id
                ctx.template_version = general.get('template_version')
                ctx.ha_priority = high_avail_dic.get('vm_priority')
                ctx.preferred_nodeid = general.get('preferred_nodeid')
                vm_disks = self.manager.get_vm_disks_from_UI(dom_id, config)
                ctx.d_list_to_create = d_list_to_create
                d_list_to_remove = self.get_disk_list_to_remove(filename_list, disk_status)
                ctx.d_list_to_remove = d_list_to_remove
                self.manager.edit_vm_config(auth, vm_config, dom, ctx, mode, group_id, vm_disks, scheduling_dic, hex_id)
                for backupconfig in backup_config_list:
                    backup_id = backupconfig.get('backup_id')
                    allow_backup_str = backupconfig.get('allow_backup')
                    backup_all_str = backupconfig.get('backup_all')
                    backupmanger = BackupManager()
                    SPbackup_VM_list_obj = backupmanger.get_SPbackup_VM_list(dom.id, backup_id)
                    if not SPbackup_VM_list_obj:
                        if backup_all_str == 'true':
                            backupmanger.add_SPbackup_VM_list(dom.id, backup_id, True)
                        elif allow_backup_str == 'true':
                            backupmanger.add_SPbackup_VM_list(dom.id, backup_id, True)
                    elif allow_backup_str == 'false':
                        backupmanger.delete_SPbackup_VM_list(dom.id, backup_id)
                ip_mac_list_old = NwManager().get_ip_mac_list(vm_id)
                ##########archer hot add Nic   hot add Disk  20130625
                self.hot_add_nicAndDisk(auth, dom, managed_node, misc_dic)
            elif mode == 'EDIT_IMAGE':
                ctx.update_template = general.get('update_version')
                ctx.new_version = general.get('new_version')
                ctx.os_flavor = general.get('os_flavor')
                ctx.os_name = general.get('os_name')
                ctx.os_version = general.get('os_version')
                ctx.allow_backup = general.get('allow_backup')
                ctx.quiescent_script_options = backup_status.get('quiescent_script_stat')
                ctx.template_cfg = template_cfg
                self.manager.edit_image(auth, vm_config, image_config, ctx)
            
            if mode not in ('EDIT_IMAGE',):
                removed_disk_list = self.removed_disk_list(filename_list, disk_status)
                self.manager.manage_vm_disks(auth, vm_id, node_id, config, mode, removed_disk_list)
                storage_list_for_recompute = []
                for disk in disk_status:
                    storage_id = disk.get('storage_id')
                    if storage_id and storage_id != 'null':
                        defn = StorageManager().get_defn(storage_id)
                        if defn:
                            if not self.check_duplicate_in_list(storage_list_for_recompute, 'STORAGE_DEF', defn.name):
                                storage_list_for_recompute.append(defn)
                            else:
                                LOGGER.info(to_str(defn.name) + ' storage is already marked for Recompute.')
                for filename in filename_list:
                    storage_id = None
                    s_disk = DBSession.query(StorageDisks).filter_by(unique_path=filename).first()
                    if s_disk:
                        storage_id = s_disk.storage_id
                    if storage_id and storage_id!= 'null':
                        defn = StorageManager().get_defn(storage_id)
                        if defn:
                            if not self.check_duplicate_in_list(storage_list_for_recompute, 'STORAGE_DEF', defn.name):
                                storage_list_for_recompute.append(defn)
                            else:
                                LOGGER.info(to_str(defn.name) + ' storage is already marked for Recompute.')
                if storage_list_for_recompute:
                    for each_storage_defn in storage_list_for_recompute:
                        StorageManager().Recompute(each_storage_defn)
                self.manager.unreserve_disks(vm_config, hex_id)
                NwManager().remove_network_VM_relation(vm_id)
                network_list = self.get_network_list(vm_id)
                print network_list,'############network_list#########'
                for each_network in network_list:
                    print each_network,'########each_network#########'
                    bridge_name = each_network.get('bridge')
                    mac_address = each_network.get('mac')
                    nw_def_id, bridge = NwManager().get_network(nw_name, bridge_name)
                    print '#########nw_def_id, bridge######',nw_def_id, bridge
                    if nw_def_id:
                        LOGGER.info('Got the network')
                        pool_id = None
                        pool = IPManager().get_pool(nw_def_id)
                        print '###########pool########',pool
                        if pool:
                            LOGGER.info('Got the pool')
                            pool_id = pool.id
                            ips_object = IPManager().reserve_address(pool_id, vm_id)
                            print ips_object,'##########ips_object#########'
                            if ips_object:
                                LOGGER.info('Reserved Private IP address')
                                ip_id = ips_object.id
                                IPManager().associate_address(pool_id, ip_id, vm_id)
                                LOGGER.info('Private IP is attached to VM')
                                NwManager().add_network_VM_relation(nw_def_id, vm_id, mac_address, ip_id)
                ip_mac_list = NwManager().get_ip_mac_list(vm_id)
                NwManager().update_dns_host_mapping(ip_mac_list, ip_mac_list_old)
                NwManager().restart_nw_service_for_VM(ip_mac_list)
        except Exception as ex:
            self.manager.unreserve_disks(vm_config, hex_id)
            print_traceback()
            err = to_str(ex).replace("'", ' ')
            LOGGER.error(err)
            raise ex
        p_timing_end(LOGGER, start)

    def get_network_list(self, vm_id):
        LOGGER.info('Getting network list...')
        network_list = []
        dom = DBSession.query(VM).filter_by(id=vm_id).first()
        if dom:
            vm_config = dom.get_config()
            vif = vm_config.get('vif')
            for keypair_str in vif:
                network_dic = {}
                keypair_list = keypair_str.split(',')
                for each_keypair in keypair_list:
                    key_value = each_keypair.split('=')
                    if to_str(key_value[0]).strip() == 'mac':
                        mac = key_value[1]
                        network_dic['mac'] = mac
                        continue
                    if to_str(key_value[0]).strip() == 'bridge':
                        bridge = key_value[1]
                        network_dic['bridge'] = bridge
                        continue
                network_list.append(network_dic)
        LOGGER.info('Network list is ' + to_str(network_list))
        return network_list

    def removed_disk_list(self, old_disk_list, new_disk_list):
        LOGGER.info('Getting removed disk list...')
        removed_file_list = []
        for filename in old_disk_list:
            disk_removed = True
            for disk in new_disk_list:
                if filename == disk.get('filename'):
                    disk_removed = False
            if disk_removed:
                removed_file_list.append(filename)
        LOGGER.info('Removed disk list is ' + to_str(removed_file_list))
        return removed_file_list

    def get_disk_list_to_remove(self, disk_list_from_config, disk_list_from_UI):
        d_list_to_remove = []
        for disk_from_config in disk_list_from_config:
            marked_for_deletion = True
            for each_disk in disk_list_from_UI:
                disk_from_UI = each_disk.get('filename')
                if disk_from_config == disk_from_UI:
                    marked_for_deletion = False
            if marked_for_deletion:
                sd = DBSession.query(StorageDisks).filter_by(unique_path=disk_from_config).first()
                if sd:
                    storage_type = sd.storage_type
                    storage_id = sd.storage_id
                    if storage_type in StorageManager.FILE_BASED_STORAGE:
                        d_list_to_remove.append(dict(name=disk_from_config, type='file', storage_id=storage_id))
                    if storage_type == constants.LVM:
                        d_list_to_remove.append(dict(name=disk_from_config, type='lvm', storage_id=storage_id))
        LOGGER.info('Disks to be removed are ' + to_str(d_list_to_remove))
        return d_list_to_remove

    def process_filename(self, mode, filename, group_id, csep_id=None, vdc_name=None):
        is_new_disk = False
        storage_id = ''
        storage_name = ''
        storage_disk_id = ''
        disk_path = ''
        storage_type = ''
        if mode == 'PROVISION_VM' or mode == 'EDIT_VM_CONFIG' or mode == 'EDIT_VM_INFO':
            if filename[0:9] == '$STORAGE_':
                is_new_disk = True
                filename_param = filename.split('/')
                storage_name = filename_param[0].replace('$STORAGE_', '')
#                disk_name = filename_param[1]
                disk_name = filename_param[1]
                s_def = DBSession.query(StorageDef).filter_by(name=storage_name).first()
                if s_def:
                    storage_id = s_def.id
                    storage_name = s_def.name
                    storage_type = s_def.type
                    if storage_type in StorageManager().FILE_BASED_STORAGE:
                        disk_path = s_def.connection_props.get('mount_point')
                    if storage_type == constants.LVM:
                        disk_path = s_def.connection_props.get('volume_group')
                    sp_strg_link = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_id=storage_id).first()
                    if not sp_strg_link:
                        raise Exception('Storage ' + to_str(s_def.name) + ' is not attached with the server pool')
                    if storage_type in StorageManager().STORAGE_FOR_CREATION:
                        if disk_name == '$DISK_NAME.disk.xm':
                            unique_name = getHexID()
                            if storage_type == constants.LVM:
                                disk_name = unique_name
                            else:
                                disk_name = disk_name.replace('$DISK_NAME', unique_name)
                            if csep_id and vdc_name:
                                disk_name = to_str(vdc_name) + '_' + to_str(disk_name)
                            if vdc_name:
                                filename = os.path.join(disk_path, vdc_name, disk_name)
                            else:
                                filename = os.path.join(disk_path, disk_name)
                            LOGGER.info('Attach prefix to the disk name. The prefix is VDC name. The disk name is ' + to_str(filename))
                        filename = os.path.join(disk_path, disk_name)
                    if storage_type in StorageManager().BLOCK_STORAGE:
                        filename = StorageManager().get_disk_from_pool(storage_id)
        return (filename, storage_id, storage_name, storage_type, storage_disk_id, is_new_disk)

    def check_duplicate_in_list(self, item_list, list_type, item):
        return_val = False
        for each_item in item_list:
            if list_type == 'STORAGE_DEF':
                each_item = each_item.name
            if each_item == item:
                return_val = True
                return return_val
        return return_val

    def update_config_props(self, config, model, excluded=[]):
        print 'Model====  ',model
        delete_props = []
        if config is None:
            return None
        for prop in config:
            if prop not in excluded:
                found = False
                for key in model.keys():
                    if key == prop:
                        found = True
                        break
                if not found:
                    delete_props.append(prop)
        for prop in delete_props:
            del config.options[prop]
        for key in model.keys():
            value = model.get(key)
            value = to_str(value)
            key = key.strip()
            value = value.strip()
            value = guess_value(value)
            if key is not None and key is not '':
                config[key] = value
        return config

    def get_exclude_list(self):
        return ['name', 'memory', 'kernel', 'ramdisk', 'root',  'extra', 'vcpus', 'on_shutdown', 'auto_start_vm', 'config_filename', 'os_flavor', 'os_name', 'os_version', 'allow_backup', 'on_reboot', 'on_crash', 'bootloader', 'disk', 'STORAGE_STATS', 'template_cfg', 'quiescent_script_options']

    def get_vm_config(self, auth, domId, nodeId):
        result = {}
        try:
            #1439
            if domId is not None and nodeId is not None:
                node = self.get_managed_node(auth, nodeId)
                dom = DBSession.query(VM).filter(VM.name == domId).first()
                if dom:
                    if dom.is_running() and node.is_up():
                        dom = node.get_dom(domId)
                else:
                    return None
            else:
                return None
            vm_config = dom.get_config()
            if vm_config is not None:
                for key in vm_config.keys():
                    result[key] = vm_config.get(key)
                node_ent = DBSession.query(Entity).filter(Entity.entity_id == node.id).first()
                ha = 0
                if node_ent.ha and node_ent.ha.registered == True:
                    ha = 1
                result['ha_enabled'] = ha
                result['os_flavor'] = dom.os_flavor
                result['os_version'] = dom.os_version
                result['allow_backup'] = dom.allow_backup
                result['os_name'] = dom.os_name
                result['filename'] = ''
                result['backup_retain_days'] = dom.backup_retain_days
                ha_priorities = constants.HA_PRIORITIES
                ha_priority = None
                for vp in ha_priorities:
                    if ha_priorities[vp] == dom.ha_priority:
                        ha_priority = vp
                        break
                result['ha_priority'] = ha_priority
                result['preferred_nodeid'] = dom.preferred_nodeid
                result['template_version'] = to_str(dom.template_version)
                result['inmem_memory'] = vm_config.get('memory')
                result['inmem_vcpus'] = vm_config.get('vcpus')
                result['inmem_bootloader'] = vm_config.get('bootloader')
                tasks = DBSession.query(Task).filter(Task.task_id.in_([dom.start_taskid, dom.reboot_taskid, dom.shutdown_taskid, dom.delete_taskid])).all()
                for task in tasks:
                    if task.name == constants.START and len(task.result) == 0L:
                        result['start_time'] = convert_to_CMS_TZ(task.interval[0L].next_execution)
                        continue
                    if task.name == constants.REBOOT and len(task.result) == 0L:
                        result['restart_time'] = convert_to_CMS_TZ(task.interval[0L].next_execution)
                        continue
                    if task.name == constants.SHUTDOWN and len(task.result) == 0L:
                        result['retire_time'] = convert_to_CMS_TZ(task.interval[0L].next_execution)
                        result['on_retire'] = 'Shutdown'
                        continue
                    if task.name == 'Remove VM' and len(task.result) == 0L:
                        result['retire_time'] = convert_to_CMS_TZ(task.interval[0L].next_execution)
                        result['on_retire'] = 'Delete'
                        continue
                result['email_id'] = auth.email_address
                if dom.shutdown_taskid or dom.delete_taskid:
                    #1168
                    if dom.email_id is not None:
                        result['email_id'] = dom.email_id
                    if dom.minutes_before is not None:
                        dd = timedelta(minutes=dom.minutes_before)
                        result['days_before'] = dd.days
                        result['hours_before'] = dd.seconds / 3600L
                    if dom.rep_interval is not None:
                        dd = timedelta(minutes=dom.rep_interval)
                        hours, seconds = divmod(dd.seconds, 3600L)
                        result['rep_hours'] = hours
                        result['rep_min'] = seconds / 60
                result['username'] = vm_config.get('username')
                result['password'] = vm_config.get('password')
                result['ip_address'] = vm_config.get('ip_address')
                result['ssh_port'] = vm_config.get('ssh_port')
                result['use_ssh_key'] = vm_config.get('use_ssh_key')
                try:
                    if dom['memory'] is not None:
                        result['inmem_memory'] = dom['memory']
                    if dom['vcpus'] is not None:
                        result['inmem_vcpus'] = dom['vcpus']
                    if dom['bootloader'] is not None:
                        result['inmem_bootloader'] = dom['bootloader']
                except Exception as e:
                    print 'Exception: ',
                    print e
                t_vers = get_template_versions(dom.image_id)
                version_list = []
                for ver in t_vers:
                    version_list.append(ver[0])
                result['template_versions'] = version_list
                result['filename'] = vm_config['config_filename']
        except Exception as ex:
            import traceback
            traceback.print_exc()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
        return result

    def get_shutdown_event_map(self):
        try:
            result = []
            result.append(dict(id='destroy', value='Destroy'))
            result.append(dict(id='preserve', value='Preserve'))
            result.append(dict(id='rename-restart', value='Rename-Restart'))
            result.append(dict(id='restart', value='Restart'))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")
        return dict(success='true', shutdown_event_map=result)

    def remove_device_entries(self, image_config, device):
        if not device:
            return None
        if device:
            print '## Device change detected from ',
            print device,
            print device
            old_create_var = device + '_disk_create'
            old_image_src_var = device + '_image_src'
            old_image_src_type_var = device + '_image_src_type'
            old_image_src_format_var = device + '_image_src_format'
            old_size_var = device + '_disk_size'
            old_disk_fs_type_var = device + '_disk_fs_type'
            old_disk_type_var = device + '_disk_type'
            for var, value in ((old_create_var, ''), (old_size_var, 0), (old_disk_fs_type_var, ''), (old_disk_type_var, ''), (old_image_src_var, ''), (old_image_src_type_var, ''), (old_image_src_format_var, '')):
                print 'delting ',
                print var
                del image_config[var]
        return image_config

    def update_device_entries(self, image_config, disk_entry, old_device=None):
        if not disk_entry:
            return None
        device = disk_entry.device
        pos = device.find(':cdrom')
        if pos > -1:
            device = device[0:pos]
        create_var = device + '_disk_create'
        image_src_var = device + '_image_src'
        image_src_type_var = device + '_image_src_type'
        image_src_format_var = device + '_image_src_format'
        size_var = device + '_disk_size'
        disk_fs_type_var = device + '_disk_fs_type'
        disk_type_var = device + '_disk_type'
        create_value = None
        if disk_entry.option == disk_entry.CREATE_DISK:
            create_value = 'yes'
        if disk_entry.option == disk_entry.USE_REF_DISK:
            if disk_entry.type == 'phy' and disk_entry.disk_type == '':
                create_value = ''
            else:
                create_value = 'yes'
        if not create_value or create_value != 'yes':
            disk_entry.size = 0
            if disk_entry.option != disk_entry.USE_REF_DISK:
                disk_entry.image_src = ''
                disk_entry.image_src_type = ''
                disk_entry.image_src_format = ''
        for var, value in ((create_var, create_value), (size_var, disk_entry.size), (disk_fs_type_var, disk_entry.fs_type), (disk_type_var, disk_entry.disk_type), (image_src_var, disk_entry.image_src), (image_src_type_var, disk_entry.image_src_type), (image_src_format_var, disk_entry.image_src_format)):
            if value and value != 'None':
                print '*** updating ',
                print var,
                print value
                image_config[var] = value
            else:
                del image_config[var]
        return image_config

    def get_quiescent_script_options(self, auth, dom_id, node_id):
        result = []
        try:
            vm_config = self.get_vm_config(auth, dom_id, node_id)
            quiescent_script_options = vm_config['quiescent_script_options']
            if quiescent_script_options:
                for eachkey in quiescent_script_options:
                    result.append(dict(attribute=eachkey, value=quiescent_script_options[eachkey]))
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
        return result

    def get_tasks(self, auth, node_id, node_type, display_type=None):
        result = None
        try:
            pending_list = []
            completed_list = []
            ent = auth.get_entity(node_id)
            if ent is None:
                return None
            lim = tg.config.get(constants.TaskPaneLimit)
            ago = datetime.now() + timedelta(days=-long(lim))
            limit = 200

            try:
                limit = int(tg.config.get(constants.task_panel_row_limit, '200'))
            except Exception as e:
                print 'Exception: ',
                print e

            if node_type == constants.DOMAIN:
                dom = DBSession().query(VM).filter(VM.id == node_id).one()
                #tasks = DBSession.query(Task).filter(Task.entity_id != None).filter(or_(Task.entity_id == node_id, Task.task_id == dom.delete_taskid, Task.task_id == dom.created_taskid)).filter(Task.submitted_on >= ago).order_by(Task.task_id.desc()).limit(limit).all()
                tasks1 = DBSession.query(Task).options(eagerload('result')).options(eagerload('interval')).filter(Task.entity_id == node_id).filter(Task.submitted_on >= ago).order_by(Task.submitted_on.desc()).limit(limit).all()
                tids = []
                if dom.delete_taskid:
                    tids.append(dom.delete_taskid)
                if dom.created_taskid:
                    tids.append(dom.created_taskid)
                tasks2 = []
                if tids:
                    tasks2 = DBSession.query(Task).options(eagerload('result')).options(eagerload('interval')).filter(Task.task_id.in_(tids)).filter(Task.submitted_on >= ago).order_by(Task.submitted_on.desc()).limit(limit).all()
                tasks = tasks1 + tasks2
                
            if node_type == constants.CLOUD_VM:
                #cloud_vm = DBSession().query(CloudVM).filter(CloudVM.id == node_id).one()
                tasks = DBSession().query(Task).filter(Task.entity_id != None).filter(Task.entity_id == node_id).all()
            elif node_type == constants.MANAGED_NODE:
                dom_ids = []
                for dom in ent.children:
                    dom_ids.append(dom.entity_id)
                dom_ids.append(node_id)
                tasks = DBSession.query(Task).options(eagerload('result')).options(eagerload('interval')).filter(Task.entity_id.in_(dom_ids)).filter(Task.submitted_on >= ago).order_by(Task.submitted_on.desc()).limit(limit).all()
                #tasks = DBSession.query(Task).filter(Task.entity_id != None).filter(or_(Task.entity_id == node_id, Task.entity_id.in_(dom_ids))).filter(Task.submitted_on >= ago).order_by(Task.task_id.desc()).limit(limit).all()
            elif node_type == constants.SERVER_POOL:
                server_ids = []
                dom_ids = []
                for server in ent.children:
                    server_ids.append(server.entity_id)
                    for dom in server.children:
                        dom_ids.append(dom.entity_id)
                server_ids.extend(dom_ids)  
                tasks = DBSession.query(Task).options(eagerload('result')).options(eagerload('interval')).filter(Task.entity_id.in_(server_ids)).filter(Task.submitted_on >= ago).order_by(Task.submitted_on.desc()).limit(limit).all() 
                #tasks = DBSession.query(Task).filter(Task.entity_id != None).filter(or_(Task.entity_id.in_(server_ids), Task.entity_id.in_(dom_ids))).filter(Task.submitted_on >= ago).order_by(Task.task_id.desc()).limit(limit).all()
            status = Task.TASK_STATUS
            for task in tasks:
                if len(task.result) == 0 and len(task.interval) > 0:
                    execution_time = task.interval[0].next_execution
                    pending_list.append(dict(task_id=task.task_id, taskname=task.name, username=task.user_name, entity_name=task.entity_name, start_time=convert_to_CMS_TZ(execution_time), end_time='', status=status[0L], edit_icon="<img title='Edit Task' alt='Edit Task' width='13' height='13' src='../icons/file_edit.png'/>", delete_icon="<img title='Delete Task' alt='Delete Task' width='13' height='13' src='../icons/delete.png'/>", error_msg='', cancellable=task.is_cancellable()))
                else:
                    start_time = task.result[0].timestamp
                    end_time = ''
                    if task.is_finished():
                        end_time = task.result[0].endtime
                        end_time = convert_to_CMS_TZ(end_time)
                    err = task.result[0].results
                    if task.result[0].status == Task.SUCCEEDED:
                        err = task.name + ' ' + 'Completed Successfully'
                    completed_list.append(dict(task_id=task.task_id, taskname=task.name, username=task.user_name, entity_name=task.entity_name, start_time=convert_to_CMS_TZ(start_time), end_time=end_time, status=status[task.result[0L].status], edit_icon='', delete_icon='', error_msg=err, cancellable=task.is_cancellable()))
            if display_type == 'Pending':
                result = pending_list
            else:
                if display_type == 'Completed':
                    result = completed_list
                else:
                    result = pending_list + completed_list
        except Exception as e:
            raise e
        return result

    def get_task_display(self):
        try:
            result = []
            dic = constants.TASK_TYPES

            for key in dic.keys():
                result.append(dict(id=dic[key], value=key))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', task_display=result)

    def get_vmschedule_status(self, dom_id, action):
        status = False
        try:
            exe_time = None
            dom = DBSession().query(VM).filter(VM.id == dom_id).one()
            tasks = DBSession.query(Task).filter(Task.task_id.in_([eval('dom.' + action + '_taskid')])).all()
            if len(tasks) > 0 and len(tasks[0].interval) > 0:
                status = True
                exe_time = tasks[0].interval[0].next_execution
        except Exception as ex:
            print_traceback()
            print '\n\n========',
            print ex
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', status=status, exe_time=exe_time)

        

    def delete_task(self, task_id):
        try:
            DBSession.query(Task).filter(Task.task_id == task_id).filter(Task.result == None).delete()
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true')

    def edit_task(self, task_id, date, time):
        try:
            task = DBSession.query(Task).filter(Task.task_id == task_id).one()
            task.interval[0].next_execution = getDateTime(date, time)
            DBSession.add(task)

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true')
        
    def schedule_email_notification(self):
        from datetime import datetime, timedelta
        vms = DBSession.query(VM).all()

        try:
            for vm in vms:
                tasks = DBSession.query(Task).filter(Task.task_id.in_([vm.shutdown_taskid, vm.delete_taskid])).all()
                notify = False
                utcnow = datetime.now()
                msg = ''
                for task in tasks:
                    if len(task.interval) > 0 and task.interval[0].next_execution is not None:
                        exe_time = task.interval[0].next_execution
                        diff_date = exe_time - utcnow
                        day_min = diff_date.days * 24 * 60
                        hr_min = diff_date.seconds / 60
                        diff_min = day_min + hr_min
                        if diff_min < vm.minutes_before and not notify:
                            if vm.last_email_notification is not None:
                                rep_diff = utcnow - vm.last_email_notification
                                rep_min = rep_diff.seconds / 60
                                
                                if vm.rep_interval != 0 and rep_min >= vm.rep_interval:
                                    notify = True
                            notify = True

                        if notify:
                            msg += self.create_msg(vm, task)

                if len(msg) > 0:
                    self.do_notification_entry(msg, vm, utcnow)

        except Exception as e:
            print_traceback()
            raise e

        return None

    def create_msg(self, vm, task):
        LOGGER.info('-----create_msg----')
        msg = ''
        try:
            if task.name == 'shutdown':
                msg += 'Shutdown of virtual machine ' + vm.name + ' scheduled at ' + to_str(task.interval[0].next_execution) + ' GMT.<br/>'
            else:
                if task.name == 'Remove VM':
                    msg += 'Deletion of virtual machine ' + vm.name + ' scheduled at ' + to_str(task.interval[0].next_execution) + ' GMT.<br/>'
        except Exception as e:
            traceback.print_exc()
            raise e
        return msg

    def do_notification_entry(self, msg, vm, entry_time):
        LOGGER.info('-----do_notification_entry----')
        print '=====In notification===='
        from stackone.model.notification import Notification
        try:
            dd = timedelta(minutes=vm.rep_interval)
            hours, seconds = divmod(dd.seconds, 3600)
            minutes = seconds / 60
            inrval_msg = ''
            if hours > 0 or minutes > 0:
                inrval_msg += '<br/>Schedule Notification email you will be getting in every '
                if hours > 0:
                    inrval_msg += to_str(hours) + ' hour(s). '
                if minutes > 0:
                    inrval_msg += to_str(minutes) + ' minutes.'
            msg = msg + inrval_msg
            html = '<html><body><br/>' + msg + '</body></html>'
            notification = Notification('', 'schedule email', entry_time, html, '', vm.email_id)
            notification.subject = 'stackone schedule'
            DBSession.add(notification)
            vm.last_email_notification = entry_time
            DBSession.add(vm)
        except Exception as e:
            traceback.print_exc()
            raise e
    
    def get_schedule_values(self, type):
        LOGGER.info('-----get_schedule_values----')
        result = []
        try:
            dic = {}
            if type == 'provision':
                dic = {'Now': 'Now', 'Later': 'Later'}
            else:
                if type == 'start':
                    dic = {'On Provisioning': 'On Provisioning', 'Later': 'Later'}
                else:
                    if type == 'restart':
                        dic = {'Later': 'Later'}
                    else:
                        if type == 'retire':
                            dic = {'Never': 'Never', 'Specific Date': 'Specific Date'}
                        else:
                            if type == 'on_retire':
                                dic = {'Shutdown': 'Shutdown', 'Delete': 'Delete'}

            for key in dic.keys():
                result.append(dict(id=key, value=dic.get(key)))

        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', sch_values=result)

    def get_server_maintenance(self, auth, node_id):
        try:
            from stackone.model.Maintenance import Maintenance
            node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
            do_nothing = False
            shutdown_vms = False
            migrate_to_other_server = False
            migrate_vms_back_from_servers = False
            migrate_to_specific_server = False
            migrate_vms_back_from_specific_server = False
            if node.maintenance_operation == Maintenance.DO_NOTHING:
                do_nothing = True
            if node.maintenance_operation == Maintenance.SHUTDOWN_ALL_VMS:
                shutdown_vms = True
            elif node.maintenance_operation == Maintenance.MIGRATE_VMS_TO_SERVERS:
                migrate_to_other_server = True
                if node.maintenance_migrate_back:
                    migrate_vms_back_from_servers = True
            elif node.maintenance_operation == Maintenance.MIGRATE_VMS_TO_SERVER:
                migrate_to_specific_server = True
                if node.maintenance_migrate_back:
                    migrate_vms_back_from_specific_server = True

            infos = {'maintenance': node.is_maintenance(), 'do_nothing': do_nothing, 'shutdown_vms': shutdown_vms, 'migrate_to_other_server': migrate_to_other_server, 'migrate_to_specific_server': migrate_to_specific_server, 'migrate_vms_back_from_servers': migrate_vms_back_from_servers, 'migrate_vms_back_from_specific_server': migrate_vms_back_from_specific_server, 'server': node.maintenance_mig_node_id}
            return {'success': True, 'info': infos}
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

    def get_servers(self, auth, sp_id, node_id):
        try:
            result = []
            from stackone.model.Maintenance import Maintenance
            node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
            group = self.manager.getGroup(auth, sp_id)
            node_list = Maintenance.getNodeList(auth, group.id)
            node_list.remove(node)

            for mnode in node_list:
                if not mnode.is_maintenance():
                    result.append(dict(node_id=mnode.id, name=mnode.hostname, platform=get_platform_name(mnode.type), cpu=mnode.get_cpu_info().get(constants.key_cpu_count, 0L), memory=mnode.get_memory_info().get(constants.key_memory_total, 0L), is_standby=mnode.is_standby()))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', servers=result)

    def do_server_maintenance(self, auth, node_id, info):
        try:
            node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
            ret,msg = check_platform_expire_date(node.get_platform())
            if ret == False:
                raise Exception(msg)
            
            from stackone.model.Maintenance import Maintenance
            mainte = Maintenance()
            check_result = mainte.initial_check(node_id, info['maintenance'])
            if check_result['success']:
                mainte.initialize(auth, node_id)
                #node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
                result = mainte.set_server_maintenance(info)
                if result['success']:
                    from TaskCreator import TaskCreator
                    tc = TaskCreator()
                    task_id = tc.server_maintenance(auth, node_id, node.hostname, info['maintenance'])
                    return {'success': True, 'task_id': to_str(task_id)}
            else:
                LOGGER.info(check_result['msg'])
                return check_result
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return result
        
    def process_annotation(self, auth, node_id, text, user=None):
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
        if node:
            ret,msg = check_platform_expire_date(node.get_platform())
            if ret == False:
                raise Exception(msg)
        ent = auth.get_entity(node_id)
        msg = "Annotated by : '" + auth.user_name + "'\nAnnotation:\n\n" + text + '\n'
        if user is not None:
            result = self.get_annotation(auth, node_id)
            annotate = result.get('annotate')
            msg += "\nPreviously Annotated by : '" + annotate.get('user') + "'\nPrevious Annotation :\n\n" + annotate.get('text')
        attribs = filter((lambda atr: atr.name in ('user', 'text')), ent.attributes)
        for attr in attribs:
            DBSession.delete(attr)
        ent.attributes.append(EntityAttribute(u'user', auth.user_name))
        ent.attributes.append(EntityAttribute(u'text', text))
        DBSession.add(ent)
        notify_annotation(ent, msg)
        transaction.commit()
        return msg

    def get_annotation(self, auth, node_id):
        ent = auth.get_entity(node_id)
        attribs = filter((lambda atr: atr.name in ('user', 'text')), ent.attributes)
        dic = {}
        for attr in attribs:
            dic.update({attr.name:attr.value})
        return dict(success=True, annotate=dic)

    def clear_annotation(self, auth, node_id):
        LOGGER.info('-----clear_annotation----')
        ent = auth.get_entity(node_id)
        result = self.get_annotation(auth, node_id)
        annotate = result.get('annotate')
        attribs = filter((lambda atr: atr.name in ('user', 'text')), ent.attributes)
        for attr in attribs:
            DBSession.delete(attr)
        msg = "Annotation cleared. \n\nPreviously Annotated by : '" + annotate.get('user') + "'\nPrevious Annotation :\n\n" + annotate.get('text')
        notify_annotation(ent, msg)
        transaction.commit()
        return msg

    def is_in_maintenance_mode(self,auth, node_id):
        LOGGER.info('-----is_in_maintenance_mode----')
        try:
            result = {}
            node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
            if node:
                return {'success': True, 'is_maintenance': node.is_maintenance(), 'msg': ''}

            return {'success': False, 'is_maintenance': '', 'msg': 'Node is None'}
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")
        return result
    #Vcenter
    def get_vcenter_nodes(self, auth, vm_id):
        try:
            vm_ent = auth.get_entity(vm_id)
            result = []
            serverpool = []
            if vm_ent:
                vcenter_id = vm_ent.get_external_manager_id().value
                if vcenter_id:
                    dc_ent_ids = DBSession.query(EntityAttribute.entity_id).filter(EntityAttribute.name == constants.EXTERNAL_MANAGER_ID).join((Entity,EntityAttribute.entity_id == Entity.entity_id)).filter(EntityAttribute.value == vcenter_id).filter(Entity.type_id == EntityType.DATA_CENTER).all()
                    for dc_ent_id in dc_ent_ids:
                        dc_ent = auth.get_entity(dc_ent_id[0])
                        if dc_ent:
                            datacenter = dict(name = to_str(dc_ent.name),children = [])
                            server_pools = auth.get_entities(constants.SERVER_POOL,dc_ent)
                            for server_pool in server_pools:
                                serverpool = dict(name = to_str(server_pool.name),children = [])
                                datacenter['children'].append(serverpool)
                                nodes = auth.get_entities(constants.MANAGED_NODE,server_pool)
                                for node in nodes:
                                    managenodes = dict(name = to_str(node.name),children = [],id = to_str(node.entity_id))
                                    serverpool['children'].append(managenodes)
                        result.append(datacenter)
                    return {'nodes':result}
        except Exception,ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",''))
            return ("{success: false,msg: '",to_str(ex).replace("'",''),"'}")


    def fbuffer(self,f, chunk_size=10000):
        while True:
            chunk = f.read(chunk_size)
            if not chunk: break
            yield chunk
    def upload_iso(self,auth,file):
        try:
            if file.filename:
                filen = os.path.basename(file.filename)
                #f = open(os.path.join(dir_path, fname), 'wb', 10000)
                #open('/home/stackone/' + filen, 'wb').write(file.file.read())
                dir_path = r'/home/stackone/'
                f = open(os.path.join(dir_path, filen), 'wb', 10000)
                # Read the file in chunks
                for chunk in self.fbuffer(file.file):
                    f.write(chunk)
                f.close()
                message = 'The file "' + filen + '" was uploaded to '+dir_path+'successfully'
                return {'success':'true','message':message}
            else:
                message = 'No file was uploaded'
                return {'success':'false','message':message}

        except Exception,ex:
            return  {'success':'false','message':ex}
        
    #########hot add NIC  Disk  archer  2013--6-25    
    def hot_add_nicAndDisk(self,auth,dom,managed_node,misc_dic):
        from stackone.core.utils.utils import device_exist
        dom = managed_node.get_dom(dom.name)
        if dom.is_running():
            for k,v in misc_dic.items():
                device_k = '*'.join([managed_node.id,dom.name,k])
                if k.startswith('nic_model') or k.startswith('storage_disk'):
                    if not device_exist(device_k):
                        if k.startswith('nic_model'):
                            val = v.split(',')
                            if val[1] != 'action=delete':
                                if val[0] in ['model=e1000','model=rtl8139','model=virtio','model=ne2k_pci']:
                                    self.manager.hot_add_nic(auth,dom,val[0],device_k)
                        elif k.startswith('storage_disk'):
                            file_path,disk_type,disk_size,action = v.split(',')
                            if disk_type in ['scsi','virtio']:
                                if not os.path.exists(file_path):
                                    self.manager.hot_create_disk(auth, managed_node,file_path,disk_size)
                                    self.manager.hot_add_disk(auth, dom, file_path,disk_type,device_k)
                    else:
                        if v.find('action=delete') > -1 or v.find('action = delete') > -1:
                            if k.startswith('storage_disk'):
                                filepath = v.split(',')[0]
                            else:
                                filepath = None
                            self.manager.hot_delete_Device(auth,managed_node,dom,device_k,filepath)
        
    def hot_add_usb(self,auth, dom_id,node_id,usb_info):
        vm = self.manager.get_dom(auth,dom_id)
        managed_node = self.get_managed_node(auth,node_id)
        dom = managed_node.get_dom(vm.name)
        result = self.manager.hot_add_usb(auth, managed_node,dom,usb_info)
        return result
    def hot_del_usb(self,auth, dom_id,node_id,usb_info):
        vm = self.manager.get_dom(auth,dom_id)
        managed_node = self.get_managed_node(auth,node_id)
        dom = managed_node.get_dom(vm.name)
        result = self.manager.hot_del_usb(auth, managed_node,dom,usb_info)
        return result
    def get_usb_pci(self,auth, node_id):
        managed_node = self.get_managed_node(auth,node_id)
        result = self.manager.get_usb_pci(auth, managed_node)
        return result    
