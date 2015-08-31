from stackone.core.ha.ha_register import HAEvent
from stackone.model.ManagedNode import ManagedNode
from stackone.model.Groups import ServerGroup
from stackone.core.utils.constants import *
import stackone.core.utils.utils
from stackone.core.utils.NodeProxy import Node
from pprint import pprint
from datetime import datetime
import time
import re
import string
from stackone.core.utils.utils import uuidToString, getHexID, dynamic_map, vm_config_write, instantiate_configs, merge_pool_settings, validateVMSettings, randomUUID, copyToRemote, mktempfile, getDateTime, get_config_text, p_timing_start, p_timing_end, p_task_timing_start, p_task_timing_end
from stackone.core.utils.utils import to_unicode, to_str, create_node
utils = stackone.core.utils.utils
constants = stackone.core.utils.constants
from stackone.model.Entity import *
from stackone.model.DBHelper import DBHelper
import os
import socket
import tempfile
import traceback
import stat
#from stackone.core.platforms.xen.XenNode import XenNode
from stackone.core.platforms.kvm.KVMNode import KVMNode
from stackone.model.Sites import Site
from stackone.model.ImageStore import ImageStore
#from stackone.model.VDCStores import VDCStore
from stackone.model.VM import VM, VMDisks, VMStorageLinks, VMStorageStat, VMDiskManager, OutsideVM
from stackone.model.ImageStore import Image
from stackone.model import DBSession
from stackone.model.Authorization import AuthorizationService
from stackone.model.Metrics import MetricsService, MetricVMRaw, MetricVMCurr, MetricServerRaw, MetricServerCurr, DataCenterRaw, DataCenterCurr
from stackone.core.utils.phelper import AuthenticationException
from stackone.config.ConfigSettings import ClientConfiguration
from stackone.model.storage import StorageDef, StorageManager
from stackone.model.network import NwDef, NwManager
from stackone.model.SyncDefinition import SyncDef
from stackone.model.SPRelations import SPDefLink, DCDefLink, ServerDefLink, StorageDisks, CSEPDefLink
from stackone.model.notification import Notification
from stackone.model.EmailManager import EmailManager
from stackone.model.Credential import Credential
from stackone.model.availability import StateTransition, AvailState, VMStateHistory, AvailHistory
from stackone.model.services import Task, TaskUtil
from stackone.model.PrivilegeOps import PrivilegeOps
from stackone.model.LicenseManager import check_vm_license, check_sbs_makeup, check_platform_expire_date
from sqlalchemy.orm import eagerload
import logging
import tg
import time
import transaction
from stackone.model.LockManager import LockManager
from stackone.model.IPManager import IPManager
from stackone.model.IP import IPS
##from stackone.cloud.DbModel.platforms.cms.CSEP import CSEPZoneServerPool
##from stackone.cloud.DbModel.platforms.cms.CSEP import CSEPContext
##from stackone.cloud.DbModel.platforms.cms.CSEP import CSEP
##from stackone.cloud.DbModel.CloudProvider import *
##from stackone.cloud.DbModel.VDC import VDC
LOGGER = logging.getLogger('stackone.model')
STRG_LOGGER = logging.getLogger('STORAGE_TIMING')
MTR_LOGGER = logging.getLogger('METRICS_TIMING')
class GridManager():
    def __init__(self, client_config, registry, creds_helper):
        self.client_config = client_config
        self.registry = registry
        self.group_list = {}
        self.node_list = {}
        self.storage_manager = StorageManager()
        self.network_manager = NwManager()
        self.sync_manager = SyncDef()

    def getDataCenters(self):
        dcs = DBHelper().get_all(Site)
        return dcs
    #pass
    def getImageStores(self, auth=None, parent=None):
        if parent:
            ents = auth.get_entities(to_unicode(constants.IMAGE_STORE), parent=parent)
            ids = [ent.entity_id for ent in ents]
            iss = DBHelper().filterby(ImageStore,[],[ImageStore.id.in_(ids)])
        else:
            iss = DBHelper().get_all(ImageStore)
        return iss


    def getCloudProviders(self):
        cps = DBHelper().get_all(CloudProviderNode)
        return cps

    def getVDCStores(self):
        iss = DBHelper().get_all(VDCStore)
        return iss

    def getFactory(self, platform):
        factory = self.registry.get_node_factory(platform)
        if factory:
            return factory
        raise Exception('No factory for %s platform.' % platform)
    #pass
    def getPlatform(self, platform):
        pltfrm = self.registry.get_platform_object(platform)
        if pltfrm:
            return pltfrm
        raise Exception('No Platform object for %s platform.' % platform)
    #pass
    def get_provisioning_helper(self, platform, op_context=None):
        from stackone.viewModel import Basic
        plat = self.registry.get_platform_object(platform)
        pr_helper = plat.get_provisioning_helper(op_context)
        if not pr_helper:
            if op_context == 'DELETE_VM':
                return self
            pr_helper = Basic.getImageStore()
        return pr_helper

    def _create_default_groups(self):
        auth = AuthorizationService()
        dc_id = getHexID(constants.DC, [constants.DATA_CENTER])
        dc = DBHelper().filterby(Entity, [], [Entity.entity_id == dc_id])[0L]
        for name in ['Desktops', 'QA Lab', 'Servers']:
            grp = ServerGroup(name)
            auth.add_entity(grp.name, grp.id, to_unicode(constants.SERVER_POOL), dc)
            DBHelper().add(grp)

    def _find_groups(self, node_name, group_list_map=None):
        grp = []
        if group_list_map is None:
            group_list_map = {}
            for g in self.group_list:
                group_list_map[g] = {'node_list': self.group_list[g].getNodeNames()}
        for group_name in group_list_map.keys():
            g = group_list_map[group_name]
            node_list = g['node_list']
            if node_name in node_list:
                grp.append(group_name)
                continue
        return grp

    def discoverNodes(self, ip_list):
        pass
    #pass
    def getGroupList(self, auth, site_id=None, parent=None):
        if site_id:
            group_list = []
            groups = DBSession.query(EntityRelation).filter_by(src_id=site_id)
            for eachgroup in groups:
                group = DBSession.query(ServerGroup).filter_by(id=eachgroup.dest_id).first()
                if group:
                    group_list.append(group)
                    continue
            return group_list
        ents = auth.get_entities(to_unicode(constants.SERVER_POOL), parent=parent)
        ids = [ent.entity_id for ent in ents]
        grplist= DBHelper().filterby(ServerGroup,[],[ServerGroup.id.in_(ids)])
        return grplist

    #pass
    def get_sp_list(self, site_id, def_id, auth, pool_tag=constants.STORAGE, pool_id=None):
        from stackone.model.VLANManager import VLANIDPoolSPRelation
        objSPList = {}
        if site_id:
            vmw_sp_ids = ServerGroup.get_spl_pltfrms_sp()
            group_list = []
            groups = DBSession.query(EntityRelation).filter_by(src_id=site_id).filter(~EntityRelation.dest_id.in_(vmw_sp_ids))
            for eachgroup in groups:
                associated = False
                one_group = {}
                group = DBSession.query(ServerGroup).filter_by(id=eachgroup.dest_id).first()
                if group:
                    ent = auth.get_entity(group.id)
                    if auth.has_privilege("ADD_STORAGE_DEF", ent) and auth.has_privilege("REMOVE_STORAGE_DEF", ent) and pool_tag == constants.STORAGE:
                        group_defn = DBSession.query(SPDefLink).filter_by(group_id=group.id, def_id=def_id).first()
                        if group_defn:
                            associated = True
                        one_group['id'] = group.id
                        one_group['associated'] = associated
                        one_group['serverpool'] = group.name
                        group_list.append(one_group)
                    elif pool_tag == constants.VLAN_ID_POOL:
                        sp_rel = DBSession.query(VLANIDPoolSPRelation).filter_by(sp_id=group.id, vlan_id_pool_id=pool_id).first()
                        if sp_rel:
                            associated = True
                        one_group['id'] = group.id
                        one_group['associated'] = associated
                        one_group['serverpool'] = group.name
                        group_list.append(one_group)
                    else:
                        LOGGER.info('User has no privilege on ' + to_str(group.name) + ' for ATTACH and DETACH storage')
            objSPList['rows'] = group_list
        return objSPList


    def getGroupNames(self, auth):
        grpnames = auth.get_entity_names(to_unicode(constants.SERVER_POOL))
        return grpnames

    def getGroup(self, auth, groupId):
        ent = auth.get_entity(groupId)
        if ent is not None:
            grp = DBHelper().find_by_id(ServerGroup, groupId)
            return grp
        return None

    def get_dom(self, auth, domId):
        ent = auth.get_entity(domId)
        if ent is not None:
            return DBHelper().find_by_id(VM, domId)
        return None

    def get_doms(self, auth, nodeId):
        managed_node = self.getNode(auth, nodeId)
        if managed_node is None:
            raise Exception('Can not find the Server.')
        doms = []
        node = auth.get_entity(nodeId)
        dom_names = auth.get_entity_names(to_unicode(constants.DOMAIN), parent=node)
        for domname in dom_names:
            single_dom = managed_node.get_dom(domname)
            if single_dom:
                doms.append(single_dom)
                continue
        return doms

    def get_node_doms(self, auth, nodeId):
        managed_node = self.getNode(auth, nodeId)
        if managed_node is None:
            raise Exception('Can not find the Server.')
        doms = []
        node = auth.get_entity(nodeId)
        dom_ids = auth.get_entity_ids(to_unicode(constants.DOMAIN), parent=node)
        doms = DBSession.query(VM).filter(VM.id.in_(dom_ids)).all()
        return doms

    def get_running_doms(self, auth, nodeId):
        domlist = self.get_doms(auth, nodeId)
        runningdoms = []
        for dom in domlist:
            if dom.is_resident():
                runningdoms.append(dom)
                continue
        return runningdoms

    def get_dom_names(self, auth, nodeId):
        ent = auth.get_entity(nodeId)
        if ent is not None:
            dom_names = auth.get_entity_names(to_unicode(constants.DOMAIN), parent=ent)
            return dom_names
        return []

    def getNodeNames(self, auth, groupId=None):
        if groupId is None:
            return []
        ent = auth.get_entity(groupId)
        nodes = auth.get_entity_names(to_unicode(constants.MANAGED_NODE), parent=ent)
        return nodes
        return None
####### jiankong
    def getNodeList(self, auth, groupId=None):
        if groupId is None:
            return []
        else:
            ent = auth.get_entity(groupId)
            nodelist = []
            if ent is not None:
                child_ents = auth.get_entities(to_unicode(constants.MANAGED_NODE), parent=ent)
                ids = [child_ent.entity_id for child_ent in child_ents]
                nodelist= DBHelper().filterby(ManagedNode,[],[ManagedNode.id.in_(ids)],[ManagedNode.hostname.asc()])
            return nodelist
        return []


    def getNode(self, auth, nodeId):
        ent = auth.get_entity(nodeId)
        if ent is not None:
            return DBHelper().find_by_id(ManagedNode, nodeId)
        return None
    #pass
    def addNode(self, auth, node, groupId=None, external_id=None, external_manager_id=None):
        if groupId is None:
            raise Exception('Invalid Group.')
        else:
            ent = auth.get_entity(groupId)
            if not auth.has_privilege('ADD_SERVER', ent):
                raise Exception(constants.NO_PRIVILEGE)
            if ent is not None:
                try:
                    nodes = DBHelper().filterby(ManagedNode, [], [ManagedNode.hostname == node.hostname])
                    if len(nodes) > 0:
                        raise Exception('Server %s already exists.' % node.hostname)
                    node_ent = auth.add_entity(node.hostname, node.id, to_unicode(constants.MANAGED_NODE), ent)
                    external_id = node.get_external_id()
                    if external_id:
                        EntityAttribute.add_entity_attribute(node_ent, constants.EXTERNAL_ID, external_id)
                    if external_manager_id:
                        EntityAttribute.add_entity_attribute(node_ent, constants.EXTERNAL_MANAGER_ID, external_manager_id)
                    node.isHVM = node.is_HVM()
                    DBHelper().add(node)
                    ah = AvailHistory(node.id, ManagedNode.UP, AvailState.MONITORING, datetime.now(), u'Newly created Node')
                    DBSession.add(ah)
                    node._init_environ()
                    if stackone.model.LicenseManager.is_violated():
                        raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)
                    soc_count = node.get_socket_info()
                    ret,msg = check_sbs_makeup(soc_count)
                    if ret == False:
                        raise Exception(msg)
                    node.socket = soc_count
                    try:
                        self.updateMetrics(auth, None, node.id)
                    except Exception as e:
                        traceback.print_exc()
                    try:
                        from stackone.viewModel.TaskCreator import TaskCreator
                        tc = TaskCreator()
                        if not external_id:
                            tc.sync_server_task(auth, node.id)
                    except Exception as e:
                        traceback.print_exc()
                except Exception as e:
                    traceback.print_exc()
                    DBSession.rollback()
                    transaction.begin()
                    raise e
            return None


    def removeNode(self, auth, nodeId, force=False):
        from stackone.model.Backup import BackupManager
        ent = auth.get_entity(nodeId)
        if not auth.has_privilege('REMOVE_SERVER', ent):
            raise Exception(constants.NO_PRIVILEGE)
        if not PrivilegeOps.check_child_privileges(auth, 'REMOVE_SERVER', ent):
            raise Exception(constants.NO_CHILD_PRIVILEGE % ('Virtual Machines', 'Server'))
        groupId = ent.parents[0L].entity_id
        site = self.getSiteByGroupId(groupId)
        site_id = None
        if site:
            site_id = site.id
        self.sync_manager.on_remove_node(nodeId, groupId, site_id, auth, self.storage_manager)
        self.sync_manager.on_remove_node(nodeId, groupId, site_id, auth, self.network_manager)
        BackupManager().delete_vms_from_bkp_policy(auth, nodeId, groupId)
        domlist = PrivilegeOps.get_vm_ids(ent)
        for domid in domlist:
            self.remove_dom_config_file(auth, domid, nodeId)
        auth.remove_entity_by_id(nodeId)
        MetricsService().DeleteCurrentMetrics(constants.SERVER_CURR, nodeId)
        node = DBHelper().find_by_id(ManagedNode, nodeId)
        node.remove_environ()
        OutsideVM.onRemoveNode(node.id)
        DBHelper().delete(node)
        return None

    def changeNodePwd(self, auth, node, pwd):
        ent = auth.get_entity(node.id)
        if not auth.has_privilege('EDIT_SERVER', ent):
            raise Exception(constants.NO_PRIVILEGE)
        try:
            credentials = node.get_credentials()
            old_pwd = credentials['password']
            credentials['password'] = pwd
            node.set_node_credentials(node.credential.cred_type, **credentials)
            node.connect()
        except AuthenticationException as ex:
            credentials['password'] = old_pwd
            node.set_node_credentials(node.credential.cred_type, **credentials)
            return False
        except Exception as e:
            credentials['password'] = old_pwd
            node.set_node_credentials(node.credential.cred_type, **credentials)
            ex = to_str(node.hostname) + ':' + to_str(ex)
            raise Exception(ex)
        return True

    #pass
    def editNode(self, auth, node):
        ent = auth.get_entity(node.id)
        if not auth.has_privilege('EDIT_SERVER', ent):
            raise Exception(constants.NO_PRIVILEGE)
        managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == node.id).first()
        ret,msg = check_platform_expire_date(managed_node.get_platform())
        if ret == False:
            raise Exception(msg)
        DBHelper().add(node)
        node.refresh_environ()

    def transferNode(self, auth, source_group_id, dest_group_id, node_id, forcefully):
        from stackone.model.Backup import BackupManager
        vm_list = []
        ent = auth.get_entity(node_id)
        grp = auth.get_entity(dest_group_id)
        if not auth.has_privilege('ADD_SERVER', grp) or not auth.has_privilege('TRANSFER_SERVER', ent):
            raise Exception(constants.NO_PRIVILEGE)
        if ent is not None:
            sync_manager = SyncDef()
            if forcefully == 'false':
                sync_manager.validate_transfer_node(node_id, source_group_id, auth)
            site = self.getSiteByGroupId(source_group_id)
            site_id = None
            if site:
                site_id = site.id
            BackupManager().delete_vms_from_bkp_policy(auth, node_id, source_group_id)
            grp = DBSession.query(Entity).filter(Entity.entity_id == dest_group_id).first()
            ent = DBSession.query(Entity).filter(Entity.entity_id == node_id).first()
            auth.update_entity(ent, parent=grp)
            self.sync_manager.on_transfer_node(node_id, source_group_id, dest_group_id, site_id, auth, self.storage_manager)
            self.sync_manager.on_transfer_node(node_id, source_group_id, dest_group_id, site_id, auth, self.network_manager)
            vm_list = self.get_vms_from_pool(auth, source_group_id)
            if vm_list:
                for eachvm in vm_list:
                    self.remove_vm_storage_links_only(eachvm.id)
                    error = self.matching_on_AddEditDelete_vm(auth, 'TRANSFER_SERVER', eachvm.id)
                    if error:
                        LOGGER.error(to_str(error))
                        continue
        return None

    def getNodeMetrics(self, auth, node):
        metrics = node.get_metrics()
        return metrics

    def refreshNodeMetrics(self, auth, node):
        try:
            node.connect()
        except AuthenticationException as ex:
            raise Exception('Server not authenticated.')
        except Exception as ex:
            raise ex
        try:
            self.collectMetrics(auth, node)
        except Exception as ex:
            raise ex

    def collectMetrics(self, auth, managed_node):
        metrics = self.getNodeMetrics(auth, managed_node)
        ms = MetricsService()
        ent = auth.get_entity(managed_node.id)
        child_ents = auth.get_entities(to_unicode(constants.DOMAIN), parent=ent)
        for child_ent in child_ents:
            if child_ent.name not in metrics.keys():
                continue
        return None    

    def getCurrentMetrics(self, auth, managed_node):
        ms = MetricsService()
        vmmetrics = {}
        ent = auth.get_entity(managed_node.id)
        child_ents = auth.get_entities(to_unicode(constants.DOMAIN), parent=ent)
        for vm in child_ents:
            metrics = ms.getVMMetricsData('VM_METRIC_CURR', vm)
            if metrics:
                vmmetrics[vm.name] = metrics
                continue
        return vmmetrics
    #pass
    def do_node_action(self, auth, nodeId, action, requester=None):
        if stackone.model.LicenseManager.is_violated():
            raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)
        ent = auth.get_entity(nodeId)
        managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == nodeId).first()
        ret,msg = check_platform_expire_date(managed_node.get_platform())
        if ret == False:
            raise Exception(msg)
        ent = auth.get_entity(nodeId)
        if not auth.has_privilege(action.upper(), ent):
            raise Exception(constants.NO_PRIVILEGE)
        err_doms = []
        for e in ent.children:
            try:
                if TaskUtil.is_cancel_requested() == True:
                    err_str = 'Error in Virtual Machines:- ' + to_str(err_doms)
                    return dict(status=constants.TASK_CANCELED, msg=constants.TASK_CANCEL_MSG, results=err_str)
                if action == 'start_all':
                    action = 'start'
                else:
                    if action == 'shutdown_all':
                        action = 'shutdown'
                    else:
                        if action == 'kill_all':
                            action = 'kill'
                self.do_dom_action(auth, e.entity_id, ent.entity_id, action)
                continue
            except Exception as ex:
                traceback.print_exc()
                err_doms.append(e.name + '-' + to_str(ex))
        if err_doms:
            err_str = 'Error in Virtual Machines:- ' + to_str(err_doms).replace("'", '')
            raise Exception(err_str)


    def restore_dom(self, auth, nodeId, file):
        ent = auth.get_entity(nodeId)
        if not auth.has_privilege('RESTORE_FROM_BACKUP', ent):
            raise Exception(constants.NO_PRIVILEGE)
        managed_node = DBHelper().find_by_id(ManagedNode, nodeId)
        managed_node.restore_dom(file)

    def cloneNode(self, source_node, dest):
        pass

    def migrateDomains(self, auth, source_node, vm_list, dest, live, force=False, all=False, requester=constants.CORE):
        ex_list = []
        ent = auth.get_entity(dest.id)
        if not auth.has_privilege('ADD_VM', ent):
            raise Exception(constants.NO_PRIVILEGE)
        ret,msg = check_platform_expire_date(dest.get_platform())
        if ret == False:
            raise Exception(msg)
        ret,msg = check_platform_expire_date(source_node.get_platform())
        if ret == False:
            raise Exception(msg)
        try:
            try:
                for vm in vm_list:
                    if TaskUtil.is_cancel_requested() == True:
                        err_str = to_str(ex_list)
                        return dict(status=constants.TASK_CANCELED, msg=constants.TASK_CANCEL_MSG, results=err_str)
                    try:
                        ent=auth.get_entity(vm.id)
                        if ent is not None and  not auth.has_privilege('MIGRATE_VM',ent):
                            raise Exception(constants.NO_PRIVILEGE)
                        source_node = DBSession.query(ManagedNode).filter(ManagedNode.id == source_node.id).one()
                        LOGGER.info('process the migration of vm:' + vm.name)
                        self.migrateDomain(auth, vm.name, source_node, dest, live, force=True, requester=requester)
                        LOGGER.info('migration over vm:' + vm.name)
                    except Exception as ex1:
                        traceback.print_exc()
                        ex_list.append('Error migrating ' + vm.name + ' : ' + to_str(ex1))
                        continue
            except Exception as ex:
                traceback.print_exc()
                raise ex
        finally:
            if len(ex_list) > 0L:
                msg = 'Errors in migrate all operations \n'
                for m in ex_list:
                    msg = msg + m + '\n'
                raise Exception(msg)


    def migrateNode(self, auth, source_node, dest, live, force=False, requester=constants.CORE):
        ent1 = auth.get_entity(source_node.id)
        ent2 = auth.get_entity(dest.id)
        if not auth.has_privilege('MIGRATE_ALL', ent1) or not auth.has_privilege('ADD_VM', ent2):
            raise Exception(constants.NO_PRIVILEGE)
        vm_list = []
        for vm in self.get_node_doms(auth, source_node.id):
            vm_list.append(vm)
        self.migrateDomains(auth, source_node, vm_list, dest, live, force, requester=requester)

    def cloneDomain(self, source_dom_name, source_node, dest_node=None):
        pass
    def migrateDomain(self, auth, source_dom_name, source_node, dest_node, live, force=False, requester=constants.CORE):
        tid = str(TaskUtil.get_task_context())
        if stackone.model.LicenseManager.is_violated():
            raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

        dom = DBHelper().find_by_name(VM, source_dom_name)
        destid = dest_node.id
        srcid = source_node.id
        LOGGER.info(tid + ' : migrate :' + source_dom_name + ' : requester : ' + requester)
        ret,msg = check_platform_expire_date(dest_node.get_platform())
        if ret == False:
            raise Exception(msg)
        ret,msg = check_platform_expire_date(source_node.get_platform())
        if ret == False:
            raise Exception(msg)
        if requester in [constants.HA,constants.Maintenance]:
            LOGGER.info(tid + ' : process the migration checks.')
            err_list,warn_list = source_node.migration_checks([dom], dest_node, live)
            if len(err_list)>0:
                result = []
                for err in err_list:
                    cat,msg = err
                    result.append(dict(type='error', category=cat, message=msg))
                for warn in warn_list:
                    cat,msg = warn
                    result.append(dict(type='warning', category=cat, message=msg))
                raise Exception('Migration check results:', to_str(result))

        if requester in [constants.Maintenance]:
            requester = constants.CORE
        try:
            LOGGER.info(tid + ' : check if migration allowed ')
            source_node,dom,fail_state,success_state = self.change_dom_transient_state(auth, dom, 'migrate', source_node.id, requester)
            LOGGER.info(tid + ' : check if it is live migration ')
            if dom.is_running() and source_node.is_up():
                if dest_node.is_up():
                    dom.status = constants.MIGRATING
                    DBSession.add(dom)
                    transaction.commit()
                    dest_node = DBSession.query(ManagedNode).filter(ManagedNode.id == destid).one()
                    source_node = DBSession.query(ManagedNode).filter(ManagedNode.id == srcid).one()
                    LOGGER.info(tid + ' : issue live migrate command ')
                    source_node.migrate_dom(source_dom_name, dest_node, live)
                else:
                    StateTransition.is_allowed(dom.id, None, requester)
                    raise Exception('Running VM %s cannot be migrated to a down node' % (dom.name))

        except socket.timeout:
            print 'ignoring timeout on migration '
            LOGGER.info(tid + ' : ignoring timeout on migration ')
        except Exception as e:
            LOGGER.error(tid + ' : ' + str(e) + ' : ' + str(datetime.now()))
            StateTransition.is_allowed(dom.id, None, requester)
            traceback.print_exc()
            dom = DBSession.query(VM).filter(VM.id == dom.id).first()
            dom.status = None
            DBSession.add(dom)
            transaction.commit()
            raise e

        wait_time_over = False
        disappeared = False
        LOGGER.info(tid + ' : check whether to Wait for migration to complete. ')
        if dom.is_running() and source_node.is_up():
            wait_time = dom.get_wait_time('migrate')
            LOGGER.info(tid + ' : start Wait for migration to complete. wait_time:' + str(wait_time))
            disappeared,wait_time_over = self.wait_for_migration(wait_time, source_node, source_dom_name, dest_node)
        else:
            LOGGER.info(tid + ' : no need to Wait for migration ')
            LOGGER.info(tid + ' : vm running : ' + str(dom.is_running()) + ' : node up: ' + str(source_node.is_up()))
        if wait_time_over ==True:
            LOGGER.info(tid + ' : wait_time is over ')
            StateTransition.is_allowed(dom.id, fail_state, requester)
            msg = 'VM did not appear in destination node .'
            if disappeared == False:
                msg = 'VM still running in source node after ' + str(wait_time) + 'seconds.'
            dom = DBSession.query(VM).filter(VM.id == dom.id).first()
            dom.status = None
            DBSession.add(dom)
            transaction.commit()
            raise Exception(msg)
        LOGGER.info(tid + ' : migration complete ')
        dom = DBSession.query(VM).filter(VM.id == dom.id).first()
        if source_node.is_up() or dest_node.is_up():
            LOGGER.info(tid + ' : process the vm config file')
            self.process_config_file(dom, source_node, dest_node)
        srvr = auth.get_entity(dest_node.id)
        LOGGER.info(tid + ' : update the server-vm entity relation')
        auth.update_entity_by_id(dom.id, parent=srvr)
        dom.status = None
        DBSession.add(dom)
        transaction.commit()
        if requester != constants.HA:
            LOGGER.debug(tid + ' : Removing VM state history, requester:%s' % requester)
            VMStateHistory.remove_vm_states(source_node.id, dom.id, all=True)

        StateTransition.is_allowed(dom.id, success_state, requester)

    def wait_for_migration(self, wait_time, source_node, dom_name, dest_node):
        i=0
        wait_time_over=False
        disappeared=False
        while i <= wait_time:
            time.sleep(1)
            try:
                if disappeared==False and \
                    (source_node.get_running_vms().has_key(dom_name) or \
                    source_node.get_running_vms().has_key("migrating-"+dom_name)):
                    if i==wait_time:
                        wait_time_over=True
                else:
                    disappeared=True
                    i=0
                    while i < 5:
                        time.sleep(1)
                        metrics=dest_node.get_running_vms()
                        i+=1
                        if metrics.has_key(dom_name):
                            return (disappeared, wait_time_over)
                    return (True, True)
            except Exception, e:
                LOGGER.error("Error "+e)
                traceback.print_exc()
            i+=1
        return (disappeared, wait_time_over)

    def move_config_file(self, dom_name, source_node, dest_node):
        dom = source_node.get_dom(dom_name)
        if dom and dom.get_config():
            config = dom.get_config()
            target_filename = config['config_filename']
            isLink = False
            mode = source_node.node_proxy.lstat(target_filename).st_mode
            if stat.S_ISLNK(mode) is True:
                isLink = True
                print 'CONFIG NAME  = ',
                print config.filename
                target = source_node.node_proxy.readlink(config.filename)
                print 'ORIG TARGET  = ',
                print target
                target = os.path.join(os.path.dirname(config.filename), target)
                print 'TARGET  = ',
                print target
                target_filename = os.path.abspath(target)
                print 'TARGET FILENAME = ',
                print target_filename
            if target_filename is not None:
                if dest_node.node_proxy.file_exists(target_filename):
                    t_handle,t_name = tempfile.mkstemp(prefix=dom_name)
                    try:
                        source_node.node_proxy.get(target_filename, t_name)
                        utils.mkdir2(dest_node, os.path.dirname(target_filename))
                        dest_node.node_proxy.put(t_name, target_filename)
                        source_node.node_proxy.remove(target_filename)
                    finally:
                        os.close(t_handle)
                        os.remove(t_name)
                if isLink:
                    dest_node.node_proxy.symlink(target_filename, config.filename)
                    source_node.node_proxy.remove(config.filename)
            dest_node.add_dom_config(config.filename)
            source_node.remove_dom_config(config.filename)
        return None

    def process_config_file(self, dom, source_node, dest_node):
        if dom and dom.get_config():
            config = dom.get_config()
            if source_node.is_up():
                target_filename = config["config_filename"]
                if source_node.node_proxy.file_exists(target_filename):
                    source_node.node_proxy.remove(target_filename)
            if dest_node.is_up():
                config.set_managed_node(dest_node)
                config.set_filename(config["config_filename"])
                if not dest_node.node_proxy.file_exists(config.filename):
                    config.write()


    def getGroupVars(self, auth, groupId):
        ent=auth.get_entity(groupId)
        if not auth.has_privilege('VIEW_GROUP_PROVISIONING_SETTINGS',ent):
            raise Exception(constants.NO_PRIVILEGE)
        group=DBHelper().find_by_id(ServerGroup,groupId)
        group_vars = group.getGroupVars()

        if not group_vars : # is None:
            # put some dummy ones for users to understand
            group_vars = {}
            group_vars["CLASS_A_STORAGE"] = "#/mnt/nfs_share/class_a"
            group_vars["CLASS_B_STORAGE"] = "#/mnt/nfs_share/class_b"
            group_vars["VM_DISKS_DIR"] = "#/mnt/shared/vm_disk"
            group_vars["VM_CONF_DIR"] = "#/mnt/shared/vm_configs"
            group_vars["DEFAULT_BRIDGE"] = "#br0"
        return group_vars

    def setGroupVars(self, auth, groupId, groupvars):
        ent=auth.get_entity(groupId)
        if not auth.has_privilege('EDIT_GROUP_PROVISIONING_SETTINGS',ent):
            raise Exception(constants.NO_PRIVILEGE)
        group=self.getGroup(auth,groupId)
        group.setGroupVars(groupvars)
        DBHelper().add(group)


    def addGroup(self, auth, grp, siteId):
        ent=auth.get_entity(siteId)
        if not auth.has_privilege('ADD_SERVER_POOL',ent):
            raise Exception(constants.NO_PRIVILEGE)
        try:
            grps=DBHelper().filterby(ServerGroup,[],[ServerGroup.name==grp.name])
            if len(grps)>0:
                raise Exception("Group %s already exists." % grp.name)
            auth.add_entity(grp.name,grp.id,to_unicode(constants.SERVER_POOL),ent)
            DBHelper().add(grp)
            
            self.sync_manager.on_add_group(grp.id)
            #self.sync_manager.on_add_group(grp.id)
        except Exception, e:
            traceback.print_exc()
            raise e

    #pass
    def removeGroup(self, auth, groupId, deep=False):
        ent = auth.get_entity(groupId)
        if not auth.has_privilege('REMOVE_SERVER_POOL', ent):
            raise Exception(constants.NO_PRIVILEGE)

        if not PrivilegeOps.check_child_privileges(auth, 'REMOVE_SERVER_POOL', ent):
            raise Exception(constants.NO_CHILD_PRIVILEGE % ('Servers', 'Server Pool'))
        running_ha_evts = DBSession.query(HAEvent).filter(HAEvent.status == HAEvent.STARTED).filter(HAEvent.sp_id == groupId).all()
        if running_ha_evts:
            raise Exception('Can not delete the Server Pool.                    High Availability Task is going on.')


        z_sp = DBSession.query(CSEPZoneServerPool).filter(CSEPZoneServerPool.sp_id == groupId).first()
        if z_sp is not None:
            raise Exception('Can not delete the Server Pool. \n   Server Pool is being used by IaaS.')

        site = self.getSiteByGroupId(groupId)
        site_id = None
        if site:
            site_id = site.id

        self.sync_manager.on_remove_group(site_id, groupId, auth, self.storage_manager)
        self.sync_manager.on_remove_group(site_id, groupId, auth, self.network_manager)
        from stackone.viewModel.DWMService import DWMService
        DWMService.delete_dwm_details(groupId)

        if deep:
            nodelist = PrivilegeOps.get_server_ids(ent)
            for nodeid in nodelist:
                self.removeNode(auth, nodeid)

        ent = DBSession.query(Entity).filter(Entity.entity_id == groupId).first()
        auth.remove_entity(ent)
        grp = DBHelper().find_by_id(ServerGroup, groupId)
        DBHelper().delete(grp)


    def shutdown(self):
        groups = self.getGroupList()
        for group in groups.itervalues():
            nodes = self.getNodeList(group.name)
            for n in nodes.itervalues():
                try:
                    n.disconnect()
                except Exception as ex:
                    print ex
        ungrouped_nodes = self.getNodeList()
        for n in ungrouped_nodes.itervalues():
            try:
                n.disconnect()
            except Exception as ex:
                print ex

    def import_dom_configs(self, auth, nodeId, paths, external_manager_id):
        print 'paths: ',
        print paths,
        print 'nodeId: ',
        print nodeId
        if stackone.model.LicenseManager.is_violated():
            raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)
        managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == nodeId).first()
        ret,msg = check_platform_expire_date(managed_node.get_platform())
        if ret == False:
            raise Exception(msg)
        managed_node = self.getNode(auth, nodeId)
        if managed_node is None:
            raise Exception('Can not find the Server with nodeId %s', nodeId)
        msgs = []
        err_doms = []
        try:
            tid = TaskUtil.get_task_context()
            paths = paths.split(',')
            paths = managed_node.process_paths(paths)
            for path in paths:
                print 'XXXX processing ',
                print path
                if TaskUtil.is_cancel_requested() == True:
                    err_str = self.get_msg_str(msgs).replace("'", '')
                    return dict(status=constants.TASK_CANCELED, msg=constants.TASK_CANCEL_MSG, results=err_str)
                else:
                    try:
                        msgs.append('========================================')
                        msgs.append('\nImport VM processing ' + path + '\n')
                        msg = self._import_dom_config(auth, nodeId, path, task_id=tid, external_manager_id=external_manager_id)
                        msgs.append(msg + '\n')
                        continue
                    except Exception as ex:
                        traceback.print_exc()
                        LOGGER.error(to_str(ex))
                        err_doms.append(to_str(ex))
                        msgs.append(to_str(ex) + '\n')
                        continue
        except Exception as ex:
            raise ex
        if len(err_doms) > 0L:
            err_str = 'Error in importing virtual machines:- \n'
            err_str += '--------------------------------------------------\n'
            err_str += self.get_msg_str(msgs).replace("'", '')
            raise Exception(err_str)
        msg = 'Importing Virtual Machines \n'
        msg += '----------------------------------------\n'
        msg += self.get_msg_str(msgs).replace("'", '')
        return msg

    #pass
    def get_msg_str(self, msgs):
        message = ''
        for msg in msgs:
            message += msg
        return message

    def _import_dom_config(self, auth, nodeId, path, task_id=None, external_manager_id=None):
        ent = auth.get_entity(nodeId)
        if not auth.has_privilege('IMPORT_VM_CONFIG_FILE', ent):
            raise Exception(constants.NO_PRIVILEGE)
        managed_node = self.getNode(auth, nodeId)
        if managed_node is None:
            raise Exception('Can not find the Server.')
        ret,msg = check_platform_expire_date(managed_node.get_platform())
        if ret == False:
            raise Exception(msg)
        ret,msg = check_vm_license(new=1L, platform=managed_node.get_platform())
        if ret == False:
            raise Exception(msg)
        allowed,info = StateTransition.is_allowed(nodeId, ManagedNode.IMPORT, constants.CORE)
        if allowed == False:
            raise Exception(constants.NO_OP + '\n' + str(info['msg']))
        try:
            ent = auth.get_entity(nodeId)
            managed_node = self.getNode(auth, nodeId)
            print '0000 : Paths = ',
            print path
            dom = managed_node.get_dom_from_config(path)
            print '1111 : Doms = ',
            print dom
            msg = ''
            for dom in [dom]:
                #1619
                print '\n Trying to Import VM  ..... ',
                print dom.name,
                print '\n'
                msg += 'Trying to Import VM ' + dom.name + '\n'
                print 'YYYY processing ',
                print dom.name
                d_config = dom.get_config()
                if d_config and d_config.get('boot') is None:
                    d_config['boot'] = 'c'
                if re.sub(managed_node.get_vm_invalid_chars_exp(), '', dom.name) != dom.name:
                    raise Exception('VM name can not contain special chars %s' % managed_node.get_vm_invalid_chars())
                if dom.name == '':
                    raise Exception('VM name can not be blank.')
                config_from_file = dom.get_config()
                grp = self.getGroup(auth, ent.parents[0L].entity_id)
                template_map = {}
                if grp is not None:
                    grp_settings = grp.getGroupVars()
                    merge_pool_settings(config_from_file, {}, grp_settings, True)
                    for key in grp_settings:
                        template_map[key] = grp_settings[key]
                if template_map.get('VM_CONF_DIR') is None:
                    template_map['VM_CONF_DIR'] = tg.config.get('VM_CONF_DIR')
                config_from_file.instantiate_config(template_map)
                config_from_file.set_filename(config_from_file['config_filename'])
                dom.vm_config = get_config_text(dom.get_config())
                miss_options = []
                for opt in constants.reqd_config_options:
                    val = config_from_file.get(opt)
                    if val is None:
                        miss_options.append(opt)
                        continue
                if len(miss_options) > 0L:
                    raise Exception('Following option(s) are missing in the config file:-' + str(miss_options))
                doms = DBHelper().filterby(VM, [], [VM.name == dom.name])
                if len(doms) > 0L:
                    StateTransition.is_allowed(nodeId, ManagedNode.IMPORT_OVER, constants.CORE)
                    msg += 'VM ' + dom.name + ' already exists. \n'
                    return msg
                group_id = ent.parents[0L].entity_id
                vm_disks = self.get_vm_disks_from_UI(dom.id, config_from_file)
                error = self.pre_matching_on_AddEditDelete_vm(auth, 'IMPORT_VM_CONFIG_FILE', dom.id, vm_disks)
                if error:
                    raise Exception(error)
                dom_ent = auth.add_entity(dom.name, dom.id, to_unicode(constants.DOMAIN), ent)
                external_id = d_config.get(constants.EXTERNAL_ID)
                print 'external_id: ',
                print external_id
                if external_id:
                    EntityAttribute.add_entity_attribute(dom_ent, constants.EXTERNAL_ID, external_id)
                if external_manager_id:
                    EntityAttribute.add_entity_attribute(dom_ent, constants.EXTERNAL_MANAGER_ID, external_manager_id)
                dom.created_taskid = task_id
                dom.preferred_nodeid = nodeId
                dom.ha_priority = 0
                DBHelper().add(dom)
                managed_node.refresh()
                metrics = managed_node.get_metrics()
                dom_metrics = metrics.get(dom.name)
                if dom_metrics is not None:
                    state = dom_metrics.get('STATE')
                    dom.current_state.avail_state = state
                else:
                    dom.current_state.avail_state = VM.SHUTDOWN
                if dom.is_running():
                    dom.current_state.monit_state = AvailState.MONITORING
                if dom:
                    self.update_vm_disks(auth, dom.id, nodeId, config_from_file)
                DBSession.query(OutsideVM).filter(OutsideVM.node_id == nodeId).filter(OutsideVM.name == dom.name).delete()
                print 'ZZZZZ processing ',
                print dom.name
                transaction.commit()
                config_from_file.set_managed_node(managed_node)
                config_from_file.write()
                StateTransition.is_allowed(nodeId, ManagedNode.IMPORT_OVER, constants.CORE)
                self.updateMetrics(auth, None, nodeId)
            managed_node = self.getNode(auth, nodeId)
            managed_node.refresh_vm_avail()
            msg += 'VM ' + dom.name + ' imported successfully. \n'
            return msg
        except Exception as ex:
            StateTransition.is_allowed(nodeId, ManagedNode.IMPORT_OVER, constants.CORE)
            traceback.print_exc()
            err = to_str(ex).replace("'", ' ')
            raise Exception('Error adding file, ' + path + '. ' + err)
        return None

    #tianfeng
    def remove_vm(self, auth, domId, nodeId, force=False, requester=constants.CORE):
        ent = auth.get_entity(domId)
        if not auth.has_privilege('REMOVE_VM', ent):
            raise Exception(constants.NO_PRIVILEGE)
        nodeId = ent.parents[0L].entity_id
        dom = self.get_dom(auth, domId)
        if not dom:
            raise Exception('Can not find the specified VM.')
        if dom.is_running():
            try:
                self.do_dom_action(auth, domId, nodeId, constants.KILL)
            except Exception as e:
                traceback.print_exc()
                raise e
        try:
            allowed,info = StateTransition.is_allowed(ent.entity_id, VM.REMOVE, requester)
            if allowed == False:
                raise Exception(constants.NO_OP + '\n' + str(info['msg']))
            dom = DBSession.query(VM).filter(VM.id == domId).options(eagerload('current_state')).first()
            managed_node = self.getNode(auth, nodeId)
            dom.get_config().set_filename(dom.get_config()['config_filename'])
            try:
                connected = True
                try:
                    managed_node.connect()
                except Exception as e:
                    connected = False
                    traceback.print_exc()
            finally:
                if connected == True or force == False:
                    pr_helper = self.get_provisioning_helper(managed_node.get_platform(),'DELETE_VM')
                    pr_helper.cleanupQCDomain(managed_node,dom,auth)
                if connected == False and force == True:
                    msg = "Can not connect to server "+managed_node.hostname+\
                                   to_str(e)+" Skipping vm disk deletion."
                    LOGGER.error(msg)
                    print msg
            dom_tasks = []
            tasks = DBSession.query(Task).filter(Task.task_id.in_([dom.start_taskid, dom.shutdown_taskid, dom.delete_taskid])).all()
            for task in tasks:
                if len(task.result) == 0L:
                    dom_tasks.append(task.task_id)
                    continue
            storage_id_list = self.storage_manager.get_storage_id_list(domId)
            self.remove_all_vm_storage_links(dom.id)
            StorageManager().remove_storage_disks(dom.id)
            ip_mac_list = NwManager().get_ip_mac_list(dom.id)
            if ip_mac_list:
                ip_mac_list_old = None
                NwManager().update_dns_host_mapping(ip_mac_list, ip_mac_list_old, op=constants.REMOVE_MAPPING)
                NwManager().restart_nw_service_for_VM(ip_mac_list)
            self.disassociate_address(dom.id)
            NwManager().remove_network_VM_relation(domId)
            DBSession.delete(dom)
            auth.remove_entity_by_id(domId)
            MetricsService().DeleteCurrentMetrics(constants.VM_CURR, domId)
            self.matching_on_AddEditDelete_vm(auth, 'REMOVE_VM', dom.id)
            transaction.commit()
            self.updateMetrics(auth, domId, nodeId)
            from stackone.viewModel.TaskCreator import TaskCreator
            TaskCreator().delete_task(dom_tasks)
            VMStateHistory.remove_vm_states(nodeId, domId, all=True)
            self.storage_manager.Recompute_on_remove_vm(storage_id_list)
        except Exception as e:
            traceback.print_exc()
            StateTransition.is_allowed(dom.id, VM.REMOVE_FAILED, requester)
            raise e
        return None


    def disassociate_address(self, vm_id):
        pool_id = None
        ip_id = None
        ip_db = DBSession.query(IPS).filter_by(vm_id=vm_id)

        for each_rec in ip_db:
            ip_id = each_rec.id
            pool_id = each_rec.pool_id
            rec = IPManager().disassociate_address(pool_id, ip_id)

    def remove_dom_config_file(self, auth, domId, nodeId, requester=constants.CORE):
        ent = auth.get_entity(domId)
        if not auth.has_privilege('REMOVE_VM_CONFIG', ent):
            raise Exception(constants.NO_PRIVILEGE)

        dom = self.get_dom(auth, domId)
        if not dom:
            raise Exception('Can not find the specified VM.')

        allowed,info = StateTransition.is_allowed(ent.entity_id, VM.REMOVE, requester)
        if allowed == False:
            raise Exception(constants.NO_OP + '\n' + str(info['msg']))
        
        dom_config = dom.get_config()
        try:
            storage_id_list = self.storage_manager.get_storage_id_list(domId)
            self.remove_all_vm_storage_links(dom.id)
            dom_tasks = []
            tasks = DBSession.query(Task).filter(Task.task_id.in_([dom.start_taskid, dom.shutdown_taskid, dom.delete_taskid])).all()
    
            for task in tasks:
                if len(task.result) == 0:
                    dom_tasks.append(task.task_id)
    
            DBHelper().delete(dom)
            auth.remove_entity_by_id(domId)
            transaction.commit()
            self.updateMetrics(auth, domId, nodeId)
            from stackone.viewModel.TaskCreator import TaskCreator
            TaskCreator().delete_task(dom_tasks)
            VMStateHistory.remove_vm_states(nodeId, domId, all=True)
            self.storage_manager.Recompute_on_remove_vm(storage_id_list)
    
        except Exception as e:
            traceback.print_exc()
            StateTransition.is_allowed(dom.id, VM.REMOVE_FAILED, requester)
            raise e


    def save_dom_config_file(self, auth, domId, nodeId, content):
        if stackone.model.LicenseManager.is_violated():
            raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

        ent = auth.get_entity(domId)
        if not auth.has_privilege('EDIT_VM_CONFIG_FILE', ent):
            raise Exception(constants.NO_PRIVILEGE)

        r = self.check_vm_config_datas(content)
        if not r.get('success'):
            raise Exception(r.get('msg'))

        dom = self.get_dom(auth, domId)
        filename = dom.get_config()['config_filename']
        managed_node = self.getNode(auth, nodeId)
        dom.vm_config = content
        DBHelper().add(dom)
        file1 = managed_node.node_proxy.open(filename, 'w')
        file1.write(content)
        file1.close()

    def check_vm_config_datas(self, content):
        l = content.strip().split('\n')
        invalid_datas = [x for x in l if len(x.split("=", 1))==1]
        if invalid_datas:
            msg = 'Invalid entry in config : %s ' %(','.join(invalid_datas))
            return dict(success = False, msg = msg)
        ll = [x.split("=", 1) for x in l if len(x.split("=", 1))==2]
        dic = dict(ll)
        msg = ''
        for key, value in dic.items():
            try:
                eval(value)
            except Exception , ex:
                msg = 'Invalid value for attribute : %s ' %key
                return dict(success = False, msg = msg)
        return dict(success = True, msg = msg)

    #pass
    def save_dom(self, auth, domId, nodeId, file, directory):
        managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == nodeId).first()
        ret,msg = check_platform_expire_date(managed_node.get_platform())
        if ret == False:
            raise Exception(msg)
        ent = auth.get_entity(domId)
        if not auth.has_privilege('HIBERNATE_VM', ent):
            raise Exception(constants.NO_PRIVILEGE)
        managed_node = self.getNode(auth, nodeId)
        dom = managed_node.get_dom(domId)
        if directory and not managed_node.node_proxy.file_exists(directory):
            utils.mkdir2(managed_node, directory)
        if dom.is_resident():
            dom._save(file)

    def reserve_disks(self, vm_config, hex_id):
        try:
            transaction.begin()
            for file in vm_config.getDisks():
                #get disk name
                unique_path = file.filename
                #check the storage disk should not be reserved.
                storage_disk = DBSession.query(StorageDisks).filter_by(unique_path=unique_path).first()
                if storage_disk:
                    #if storage disk is not reserved, not allocated and not in read only mode then reserve it.
                    if not storage_disk.transient_reservation and not storage_disk.storage_allocated and file.mode != 'r':
                        storage_disk.transient_reservation = hex_id
                        LOGGER.info("Storage disk " + to_str(unique_path) + " is reserved.")
                    else:
                        #We can use read only disk even if it is reserved.
                        #do not raise exception for read only disk.
                        if not storage_disk.storage_allocated and file.mode != 'r':
                            #if storage disk is reserved then throw exception
                            raise Exception("Storage disk " + to_str(unique_path) + " is already being used by other Virtual Machine.")
            
            transaction.commit()
        except Exception, ex:
            LOGGER.error(str(ex))
            transaction.abort()
            raise Exception(str(ex))

    def unreserve_disks(self, vm_config, hex_id=None):
        LOGGER.info('Unreserving storage disks...')
        if not vm_config:
            LOGGER.info("vm config not present. So can not unreserve disks.")
            return
        
        #loop through all the attached to VM.
        for file in vm_config.getDisks():
            #get disk name
            unique_path = file.filename
                
            #check whether the storage disk is reserved.
            storage_disk = None
            if hex_id:
                storage_disk = DBSession.query(StorageDisks)\
                .filter_by(unique_path=unique_path, transient_reservation=hex_id).first()
            
            if storage_disk:
                #unreserve storage disk
                storage_disk.transient_reservation = None
                LOGGER.info("Storage disk " + to_str(unique_path) + " is unreserved.")

    def unreserve_disks_on_cms_start(self):
        LOGGER.info("Unreserving storage disks on CMS start...")
        #get all the storage disks
        storage_disk_list = DBSession.query(StorageDisks).filter(StorageDisks.transient_reservation != None)
        for storage_disk in storage_disk_list:
            #unreserve storage disk.
            storage_disk.transient_reservation = None
            LOGGER.info("Storage disk " + to_str(storage_disk.unique_path) + " is unreserved.")
        transaction.commit()
    #pass
    def edit_vm_config(self, auth, vm_config, dom, context, mode=None, group_id=None, vm_disks=None, scheduling_dic=None, hex_id=None):
        start = p_timing_start(LOGGER, 'edit_vm_config')
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)
    
            ent = auth.get_entity(dom.id)
            if not auth.has_privilege('CHANGE_VM_SETTINGS', ent):
                raise Exception(constants.NO_PRIVILEGE)
            self.reserve_disks(vm_config, hex_id)
            node_id = context.node_id
            managed_node = None
            if node_id is not None:
                managed_node = self.getNode(auth, node_id)
                context.managed_node = managed_node
                context.setup_config = None
                if managed_node is None:
                    raise Exception('Cannot find the Managed Node.')
            ret,msg = check_platform_expire_date(managed_node.get_platform())
            if ret == False:
                raise Exception(msg)

            vm_config.set_managed_node(context.managed_node)
            vm_config.update_storage_stats()
            dom.setDownMem(vm_config['memory'])
            dom.setDownVCPUs(vm_config['vcpus'])
            error = self.pre_matching_on_AddEditDelete_vm(auth, 'EDIT_VM_CONFIG', dom.id, vm_disks)
            if error:
                raise Exception(error)

            self.create_disk(auth, context)
            self.remove_disk(auth, context)
            ent.name = vm_config['vmname']
            dom.name = vm_config['vmname']
            vm_config['name'] = vm_config['vmname']
            dom.vm_config = get_config_text(vm_config)
            dom.template_version = context.template_version
            dom.os_flavor = vm_config['os_flavor']
            dom.os_name = vm_config['os_name']
            dom.os_version = vm_config['os_version']
            dom.allow_backup = vm_config['allow_backup']
            dom.ha_priority = context.ha_priority
            dom.preferred_nodeid = context.preferred_nodeid
            creds = DBSession.query(Credential).filter_by(entity_id=dom.id).first()
            if creds:
                cred_details = {}
                cred_details['username'] = vm_config['username']
                cred_details['password'] = vm_config['password']
                cred_details['ip_address'] = vm_config['ip_address']
                cred_details['ssh_port'] = vm_config['ssh_port']
                cred_details['use_ssh_key'] = vm_config['use_ssh_key']
                creds.cred_details = cred_details

            task_data = self.submit_vm_tasks(auth, dom, context, scheduling_dic, mode)
            dom.start_taskid = task_data.get('start_taskid')
            dom.reboot_taskid = task_data.get('restart_taskid')
            dom.shutdown_taskid = task_data.get('shutdown_taskid')
            dom.delete_taskid = task_data.get('delete_taskid')
            dom.email_id = task_data.get('email_id')
            dom.minutes_before = task_data.get('minutes_before')
            dom.rep_interval = task_data.get('rep_interval')
            DBHelper().add(dom)
            DBHelper().add(ent)
            if not vm_config.filename:
                filename = dom.get_config()['config_filename']
                if filename:
                    vm_config.set_filename(filename)
            vm_config.write()
            p_timing_end(LOGGER, start)

        except Exception as ex:
            traceback.print_exc()
            raise Exception(str(ex))


    def create_disk(self, auth, context):
        store = context.image_store
        image_id = context.image_id
        v_config = context.vm_config
        i_config = context.image_config
        d_list_to_create = context.d_list_to_create
        managed_node = context.managed_node
        d_list_to_remove = context.d_list_to_remove
        image_store_location = managed_node.config.get(constants.prop_image_store)
        if image_store_location is None:
            image_store_location = store.DEFAULT_STORE_LOCATION

        if d_list_to_create:
            for each_disk in d_list_to_create:
                context = {}
                context['create_flag'] = True
                context['disk_name'] = each_disk.get('name')
                context['disk_type'] = each_disk.get('type')
                context['disk_size'] = each_disk.get('size')
                context['fs_type'] = each_disk.get('fs_type')
                context['image_store_location'] = image_store_location
                context['storage_id'] = each_disk.get('storage_id')
                context['storage_allocated'] = True
                context['added_manually'] = False
                exit_code,output,storage_disk_id,storage_id = StorageManager().execute_create_disk_script(context, managed_node)
                if exit_code > 0:
                    raise Exception(to_str(output))


    def remove_disk(self, auth, context):
        store = context.image_store
        image_id = context.image_id
        v_config = context.vm_config
        i_config = context.image_config
        d_list_to_create = context.d_list_to_create
        managed_node = context.managed_node
        d_list_to_remove = context.d_list_to_remove
        image_store_location = managed_node.config.get(constants.prop_image_store)
        if image_store_location is None:
            image_store_location = store.DEFAULT_STORE_LOCATION

        if d_list_to_remove:
            for each_disk in d_list_to_remove:
                context = {}
                context['delete_flag'] = True
                context['disk_name'] = each_disk.get('name')
                context['disk_type'] = each_disk.get('type')
                context['image_store_location'] = image_store_location
                context['storage_id'] = each_disk.get('storage_id')
                exit_code,output,storage_disk_id = StorageManager().execute_remove_disk_script(context, managed_node)
                if exit_code > 0:
                    raise Exception(to_str(output))

    #pass
    def edit_image(self, auth, vm_config, image_config, context):
        from stackone.viewModel import Basic
        ent = auth.get_entity(context.image.id)
        original_imageid = context.image.id
        if not auth.has_privilege('EDIT_IMAGE_SETTINGS', ent):
            raise Exception(constants.NO_PRIVILEGE)
        if context.update_template:
            prev_image = context.image
            prev_image.id = getHexID()
            DBHelper().add(prev_image)
            DBSession.flush()
            image_store = Basic.getImageStore()
            edit_image = image_store.create_image_instance(name=context.image.name, platform=context.image.platform, id=original_imageid, location=context.image.location)
            edit_image.prev_version_imgid = original_imageid
            edit_image.version = context.new_version
        else:
            edit_image = context.image
        edit_image.vm_config = get_config_text(vm_config)
        edit_image.image_config = get_config_text(image_config)
        edit_image.os_flavor = context.os_flavor
        edit_image.os_name = context.os_name
        edit_image.os_version = context.os_version
        edit_image.allow_backup = context.allow_backup
        DBHelper().add(edit_image)
        image_config.write()
        vm_config.write()

    def cli_edit_vm(self, auth, dom, memory, cpu):
        ent = auth.get_entity(dom.id)
        if not auth.has_privilege('CHANGE_VM_SETTINGS', ent):
            raise Exception(constants.NO_PRIVILEGE)
        vmconfig = dom.get_config()
        msg = ' Virtual machine settings changed sucessfully.'
        err_msgs = []

        if memory != '':
            try:
                memory = int(memory)
            except:
                err_msgs.append('Specify a proper integer value for the Memory.')
            vmconfig['memory'] = memory
        if cpu != '':
            try:
                cpu = int(cpu)
            except:
                err_msgs.append('Specify a proper integer value for the VirtualCPUs.')
            vmconfig['vcpus'] = cpu

        if len(err_msgs) > 0:
            raise Exception(err_msgs)

        dom.vm_config = get_config_text(vmconfig)
        if dom.is_resident():
            msg += ' Changes will be affected on restart.'
        return msg
    #pass
    def edit_vm_info(self, auth, vm_config, vm_info, dom, context, mode, initial_disks, final_disks, group_id=None, vm_disks=None, scheduling_dic=None, requester=constants.CORE, hex_id=None):
        if stackone.model.LicenseManager.is_violated():
            raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

        ent = auth.get_entity(dom.id)
        if not auth.has_privilege('CHANGE_VM_SETTINGS', ent):
            raise Exception(constants.NO_PRIVILEGE)

        allowed,info = StateTransition.is_allowed(ent.entity_id, VM.EDIT, requester)
        if allowed == False:
            raise Exception(constants.NO_OP + '\n' + str(info['msg']))

        self.reserve_disks(vm_config, hex_id)

        try:
            node_id = context.node_id
            managed_node = None
            if node_id is not None:
                managed_node = self.getNode(auth,node_id)
                context.managed_node = managed_node
                context.setup_config = None
                if managed_node is None:
                    raise Exception('Cannot find the Managed Node.')

            ret,msg = check_platform_expire_date(managed_node.get_platform())
            if ret == False:
                raise Exception(msg)
            
            vm_config.set_managed_node(context.managed_node)
            mem = vm_info['memory']
            vcpus = vm_info['vcpus']
            dom.setMem(mem)
            dom.setVCPUs(vcpus)
            error = self.pre_matching_on_AddEditDelete_vm(auth, 'EDIT_VM_INFO', dom.id, vm_disks)
            if error:
                raise Exception(error)
            self.create_disk(auth, context)
            self.remove_disk(auth, context)
            detach_disk_list=[val for val in initial_disks \
                          if val not in final_disks]
            attach_disk_list=[val for val in final_disks \
                          if val not in initial_disks]
            if detach_disk_list:
                dom.detachDisks(detach_disk_list)
            if attach_disk_list:
                dom.attachDisks(attach_disk_list)
            dom = DBSession.query(VM).filter(VM.id == dom.id).first()
            dom.template_version = context.template_version
            dom.os_flavor=vm_config["os_flavor"]
            dom.os_name=vm_config["os_name"]
            dom.os_version=vm_config["os_version"]
            dom.allow_backup = vm_config["allow_backup"]
            dom.ha_priority = context.ha_priority
            dom.preferred_nodeid = context.preferred_nodeid
            creds = DBSession.query(Credential).filter_by(entity_id = dom.id).first()
            if creds:
                cred_details = {}
                cred_details['username'] = vm_config['username']
                cred_details['password'] = vm_config['password']
                cred_details['ip_address'] = vm_config['ip_address']
                cred_details['ssh_port'] = vm_config['ssh_port']
                cred_details['use_ssh_key'] = vm_config['use_ssh_key']
                creds.cred_details = cred_details
            task_data = self.submit_vm_tasks(auth,dom,context,scheduling_dic,mode)
            dom.start_taskid = task_data.get('start_taskid')
            dom.reboot_taskid = task_data.get('restart_taskid')
            dom.shutdown_taskid = task_data.get('shutdown_taskid')
            dom.delete_taskid = task_data.get('delete_taskid')
            dom.email_id = task_data.get('email_id')
            dom.minutes_before = task_data.get('minutes_before')
            dom.rep_interval = task_data.get('rep_interval')
            vm_config.update_storage_stats()
            dom.vm_config = get_config_text(vm_config)
            if not vm_config.filename:
                filename = dom.get_config('config_filename')
                if filename:
                    vm_config.set_filename(filename)
            DBSession.add(dom)
            transaction.commit()
            vm_config.write()
            StateTransition.is_allowed(dom.id, VM.EDIT_SUCCEEDED, requester)

        except Exception as e:
            traceback.print_exc()
            StateTransition.is_allowed(dom.id, VM.EDIT_FAILED, requester)
            raise e
    #tianfeng
    def increaseProvisionCount(self, node_id):
        self.changeProvisionCount(node_id, 1L)
    #pass
    def decreaseProvisionCount(self, node_id):
        self.changeProvisionCount(node_id, -1)
    ###pass
    def changeProvisionCount(self, node_id, count):
        try:
            transaction.begin()
            avail_state = DBSession.query(AvailState).filter(AvailState.entity_id == node_id).first()
            if avail_state:
                avail_state.used_count = avail_state.used_count + count
                DBSession().add(avail_state)
            transaction.commit()
        except Exception as e:
            traceback.print_exc()
            raise e
    #pass
    def provision(self, auth, context, mode, img_name, group_id=None, vm_disks=[], is_restore=False, del_vm_id=None, scheduling_dic=None, task_id=None, hex_id=None, cloud=None):
        if stackone.model.LicenseManager.is_violated():
            raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)
        ret,msg = check_vm_license(new=1L, platform=context.managed_node.get_platform())
        if ret == False:
            raise Exception(msg)
        ret,msg = check_platform_expire_date(context.managed_node.get_platform())
        if ret == False:
            raise Exception(msg)
        v_config = context.vm_config
        print 'XXXXXXXXXXXXXXXX',
        print v_config.__class__
        i_config = context.image_config
        image_id = context.image_id
        managed_node = context.managed_node
        node_id = managed_node.id
        self.reserve_disks(v_config, hex_id)

        try:
            ent = auth.get_entity(managed_node.id)
            if not auth.has_privilege('PROVISION_VM', ent):
                raise Exception(constants.NO_PRIVILEGE)
            self.increaseProvisionCount(node_id)
            managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
            context.managed_node = managed_node
            ent = auth.get_entity(managed_node.id)
            vmname = context.vm_config['name']
            doms = DBHelper().filterby(VM, [], [VM.name == vmname])
            if len(doms) > 0:
                raise Exception('VM %s already exists.' % vmname)
    
            if is_restore == True:
                id = del_vm_id
            else:
                id = getHexID()
    
            v_config['uuid'] = id
            store,managed_node,vm_config_file,vm_config = vm_config_write(auth, context, image_id, v_config, i_config, img_name)
            vm = managed_node.new_vm_from_config(vm_config)
            vm.id = id
            vm.image_id = image_id
            vm.template_version = context.image.version
            vm.os_flavor = v_config['os_flavor']
            vm.os_name = v_config['os_name']
            vm.os_version = v_config['os_version']
            vm.allow_backup = v_config['allow_backup']
            vm.created_user = auth.user_name
            vm.created_date = datetime.now()
            vm.preferred_nodeid = context.preferred_nodeid
            vm.ha_priority = context.ha_priority
            vm.credential = Credential(id, u'', username=v_config['username'], password=v_config['password'], ip_address=v_config['ip_address'], ssh_port=v_config['ssh_port'], use_ssh_key=v_config['use_ssh_key'])
            vm.backup_retain_days = v_config['backup_retain_days']
            if context.csep_context:
                cloud_id = context.csep_context.pop('new_vm_id', None)
                vm.cloud_vm_id = cloud_id
                vm.current_state.cloud_entity_id = cloud_id
            error = self.pre_matching_on_AddEditDelete_vm(auth, 'PROVISION_VM', id, vm_disks)
            if error:
                raise Exception(error)
            pr_helper = self.get_provisioning_helper(managed_node.platform)
            out,exit_code,log_filename,external_id = pr_helper.execute_provisioning_script(auth, managed_node, image_id, v_config, i_config)
            #out,exit_code,log_filename,external_id = store.execute_provisioning_script(auth, managed_node, image_id, v_config, i_config)
            if exit_code == 0:
                try:
                    csep_context = context.csep_context
                    vm_ent = auth.add_entity(vmname, id, to_unicode(constants.DOMAIN), ent, csep_context=csep_context)
                    vm_config.update_storage_stats()
                    vm_config.update_storage_disks()
                    vm.vm_config = get_config_text(vm_config)
                    DBHelper().add(vm)
                    managed_node.refresh_vm_avail()
                    transaction.commit()
                    vm_config.write()
                    #StateTransition.is_allowed(node_id, ManagedNode.PROVISION_OVER, constants.CORE)
                    self.decreaseProvisionCount(node_id)
                    self.updateMetrics(auth, id, node_id)
                    vm = DBSession.query(VM).filter(VM.id == id).one()
                    if vm is not None:
                        task_data = self.submit_vm_tasks(auth, vm, context, scheduling_dic, mode)
                        vm.start_taskid = task_data.get('start_taskid')
                        vm.reboot_taskid = task_data.get('restart_taskid')
                        vm.shutdown_taskid = task_data.get('shutdown_taskid')
                        vm.delete_taskid = task_data.get('delete_taskid')
                        vm.created_taskid = task_id
                        vm.email_id = task_data.get('email_id')
                        vm.minutes_before = task_data.get('minutes_before')
                        vm.rep_interval = task_data.get('rep_interval')
                        if cloud:
                            vm.csep_id = cloud['servicepoint_id']
                            vm.serverpool_id = cloud['serverpool_id']
                        DBHelper().add(vm)
                        if external_id:
                            EntityAttribute.add_entity_attribute(vm_ent,constants.EXTERNAL_ID,external_id,vm_ent.entity_id)
                            
                    return id
                except Exception as e:
                    traceback.print_exc()
                    raise e
            else:
                print 'out==',out,'exit_code=',exit_code,'log',log_filename
                raise Exception('Script Output\n------------------\n'+out + log_filename)
        except Exception as e:
            #StateTransition.is_allowed(node_id,ManagedNode.PROVISION_OVER,constants.CORE)
            self.decreaseProvisionCount(node_id)
            traceback.print_exc()
            raise e

    #pass
    def cleanupQCDomain(self, managed_node, dom, auth, vbdlocation=''):
        from stackone.viewModel import Basic
        vm_config = None
        image_config = None
        dom_config = None
        if dom:
            dom_config = dom.get_config()
        if dom_config:
            dom_config.delete_config_file()
            image_store = Basic.getImageStore()
            image_id = dom.image_id
            image = image_store.get_image(auth,image_id)
            if image:
                vm_config,image_config = image.get_configs(managed_node.get_platform())
            context = dynamic_map()
            context.image_store = image_store
            context.image_id = image_id
            context.vm_config = vm_config
            context.image_config = image_config
            context.managed_node = managed_node
            d_list_to_remove = []

            for file in dom_config.getDisks():
                if file.mode.find('w') == -1:
                    continue

                vm_disk_types = tg.config.get(constants.vm_disk_types)
                try:
                    vm_disk_types = eval(vm_disk_types)
                except Exception as e:
                    vm_disk_types = ['file', 'tap:aio', 'tap:qcow', 'tap:vmdk']
                    print e
                if file.filename and (file.filename.strip().find('/dev/disk/') == 0 or file.filename.strip().find('/dev/etherd/') == 0):
                    continue
                strg_type = file.type
                filename = file.filename
                sd = DBSession.query(StorageDisks).filter_by(unique_path=filename).first()
                if sd:
                    storage_type = sd.storage_type
                    storage_id = sd.storage_id
                    if storage_type in StorageManager().STORAGE_FOR_CREATION:
                        if storage_type == constants.LVM:
                            strg_type = constants.LVM
                        else:
                            strg_type = 'file'
                        d_list_to_remove.append(dict(name=filename, type=strg_type, storage_id=storage_id))
                else:
                    d_list_to_remove.append(dict(name=filename, type=strg_type))
            context.d_list_to_remove = d_list_to_remove
            self.remove_disk(auth, context)
        else:
            print "Couldn't find the domain . Skipping deletion" 

    def remove_nw_id(self, dom, node):
        LOGGER.info('Removing nw_id from vif in vm config...')
        vif = ''
        try:
            vm_config = dom.get_config()
            update_dom = False
            vif = vm_config.get('vif')
            new_vif = []
            loc = []

#            for vif_item in vif:
#                vif_item_param_list = vif_item.split(',')
#                new_item = ''
#                for item in vif_item_param_list:
#                    if item.find('nw_id=')<0:
#                        if not new_item:
#                            new_item = to_str(item)
#                        else:
#                            new_item += ', ' + to_str(item)
#                new_vif.append(new_item)  
            for vif_item in vif:
                vif_item_param_list = vif_item.split(',')
                for ite in vif_item_param_list:
                    if ite.find('nw_id=')<0:
                        loc.append(ite)    
                new_vif.append(','.join(loc))
                loc = []
            LOGGER.debug('new_vif=' + to_str(new_vif))
            vm_config['vif'] = new_vif
            update_dom = True
            if update_dom == True:
                dom.vm_config = get_config_text(vm_config)
                DBSession.add(dom)
                vm_config.set_managed_node(node)
                vm_config.set_filename(vm_config['config_filename'])
                vm_config.write()
                LOGGER.info('nw_id is removed from vif in vm config')
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
        return new_vif


    def add_nw_id(self, dom, node, vif):
        LOGGER.info('Adding nw_id to vif in vm config...')
        try:
            LOGGER.debug('vif=' + to_str(vif))
            vm_config = dom.get_config()
            update_dom = False
            vm_config['vif'] = vif
            update_dom = True
            if update_dom == True:
                dom.vm_config = get_config_text(vm_config)
                DBSession.add(dom)
                vm_config.set_managed_node(node)
                vm_config.set_filename(vm_config['config_filename'])
                vm_config.write()
                LOGGER.info('nw_id is added to vif in vm config')
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
    #tianfeng
    def do_dom_action(self, auth, domId, nodeId, action, requester=constants.CORE):
        if stackone.model.LicenseManager.is_violated():
            raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)
        ent = auth.get_entity(domId)
        if not auth.has_privilege(action.upper(), ent):
            raise Exception(constants.NO_PRIVILEGE)
        managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == nodeId).first()
        ret,msg = check_platform_expire_date(managed_node.get_platform())
        if ret == False:
            raise Exception(msg)

        try:
            ret_msg = None
            nodeId = ent.parents[0].entity_id
            node = self.getNode(auth, nodeId)
            dom = node.get_dom(ent.name)
            (fail_state, success_state) = (None, None)
            result = False
            vif_val = ''
            if action == 'start':
                if not dom.is_resident():
                    node,dom,fail_state,success_state = self.change_dom_transient_state(auth, dom, action, nodeId, requester)
                    try:
                        msg,vm_exists = self.check_vm_on_nodes(auth, dom, node)
                        ip_mac_list = NwManager().get_ip_mac_list(dom.id)
                        ip_mac_list_old = None
                        NwManager().update_dns_host_mapping(ip_mac_list, ip_mac_list_old)
                        NwManager().restart_nw_service_for_VM(ip_mac_list)
                        vif_val = self.remove_nw_id(dom, node)
                        node = self.getNode(auth, nodeId)
                        dom = node.get_dom(ent.name)
                        if not vm_exists:
                            dom._start()
                        else:
                            StateTransition.is_allowed(domId, success_state, requester)
                            return msg
                    except Exception as e:
                        traceback.print_exc()
                        StateTransition.is_allowed(domId, fail_state, requester)
                        raise e
                else:
                    LOGGER.info('Virtual Machine ' + ent.name + ' is already running.')
            elif dom.is_resident():
                node,dom,fail_state,success_state = self.change_dom_transient_state(auth, dom, action, nodeId, requester)
                try:
                    if action == 'pause':
                        result = dom._pause()
                    if action == 'unpause':
                        if dom.get_state() == VM.PAUSED:
                            result = dom._unpause()
                        else:
                            raise Exception('Virtual Machine ' + ent.name + ' is not in Paused state.')
                    if action == 'reboot':
                        dom._reboot()
                    if action == 'shutdown':
                        dom._shutdown()
                    if action == 'kill':
                        dom._destroy()
                except Exception as e:
                    StateTransition.is_allowed(domId, fail_state, requester)
                    traceback.print_exc()
                    raise e
            elif action in [constants.KILL, constants.SHUTDOWN]:
                LOGGER.info('Virtual MachineLOGGER ' + ent.name + ' is not running.')
            else:
                raise Exception('Virtual Machine ' + ent.name + ' is not running')
    
            try:
                dom.check_action_status(action, result)
    
            except Exception as e:
                traceback.print_exc()
                StateTransition.is_allowed(domId, fail_state, requester)
                raise e
            if action == 'start':
                metrics = node.get_metrics()
                data_dict = metrics.get(dom.name)
                if data_dict is not None:
                    time.sleep(5)
                metrics = node.get_metrics()
                data_dict = metrics.get(dom.name)
                if data_dict is None:
                    StateTransition.is_allowed(domId, fail_state, requester)
                    is_hvm = dom.is_hvm()
                    err = 'VM went down after 5 seconds.'
                    if is_hvm == False:
                        if node.node_proxy.file_exists(constants.XEN_LOG_PATH):
                            f = None
                            try:
                                f = node.node_proxy.open(constants.XEN_LOG_PATH, 'r')
                                err_log = self.tail(f, 10)
        
                                for e in err_log:
                                    err += e
                            finally:
                                if f is not None:
                                    f.close()
                    raise Exception(err)
                try:
                    vm_config = dom.get_config()
                    update_dom = False
                    if dom.is_hvm():
                        boot = vm_config.get('boot')
                        n_boot = vm_config.get('next_boot_device')
                        if n_boot is not None:
                            if boot != n_boot:
                                vm_config['boot'] = n_boot
                                ret_msg = 'value of config option boot changed to ' + n_boot
                                update_dom = True
                    else:
                        boot = vm_config.get('bootloader')
                        n_boot = vm_config.get('next_bootloader')
                        if n_boot is not None:
                            if boot != n_boot:
                                vm_config['bootloader'] = n_boot
                                vm_config['save_ramdisk'] = vm_config['ramdisk']
                                vm_config['ramdisk'] = ''
                                vm_config['save_kernel'] = vm_config['kernel']
                                vm_config['kernel'] = ''
                                ret_msg = 'value of config option bootloader changed to ' + n_boot
                                update_dom = True
                    if vif_val:
                        self.add_nw_id(dom, node, vif_val)
                    if update_dom == True:
                        dom.vm_config = get_config_text(vm_config)
                        DBSession.add(dom)
                        vm_config.set_managed_node(node)
                        vm_config.set_filename(vm_config['config_filename'])
                        vm_config.write()
                        LOGGER.info(to_str(ret_msg))
    
                except Exception as e:
                    traceback.print_exc()
                    print 'Exception: ',
                    print e
    
                dom.start_monitoring()
            elif action == 'shutdown' or action == 'kill':
                dom.stop_monitoring()
            transaction.commit()
            StateTransition.is_allowed(domId, success_state, requester)
            self.updateMetrics(auth, domId, nodeId)
            node = self.getNode(auth, nodeId)
            node.refresh_vm_avail()
        except Exception as e:
            traceback.print_exc()
            raise e
    #pass
    def change_dom_transient_state(self, auth, dom, action, nodeId, requester, tid=None):
        domId = dom.id
        fail_state = None
        success_state = None
        ent = auth.get_entity(dom.id)
        LOGGER.info(str(tid)+ ' : domname : '+ dom.name+' : '+action)
        if action == 'start':
            allowed,info = StateTransition.is_allowed(ent.entity_id, VM.START, requester, [nodeId])
            if allowed == False:
                raise Exception(constants.NO_OP + '\n' + str(info['msg']))
            fail_state = VM.START_FAILED
            success_state = VM.START_SUCCEEDED
        elif action == 'pause':
            allowed,info = StateTransition.is_allowed(ent.entity_id, VM.PAUSE, requester, [nodeId])
            if allowed == False:
                raise Exception(constants.NO_OP + '\n' + str(info['msg']))
            fail_state = VM.PAUSE_FAILED
            success_state = VM.PAUSE_SUCCEEDED
        elif action == 'unpause':
            allowed,info = StateTransition.is_allowed(ent.entity_id, VM.RESUME, requester, [nodeId])
            if allowed == False:
                raise Exception(constants.NO_OP + '\n' + str(info['msg']))
            fail_state = VM.RESUME_FAILED
            success_state = VM.RESUME_SUCCEEDED
        elif action == 'reboot':
            allowed,info = StateTransition.is_allowed(ent.entity_id, VM.REBOOT, requester, [nodeId])
            if allowed == False:
                raise Exception(constants.NO_OP + '\n' + str(info['msg']))
            fail_state = VM.REBOOT_FAILED
            success_state = VM.REBOOT_SUCCEEDED
        elif action == 'shutdown':
            allowed,info = StateTransition.is_allowed(ent.entity_id, VM.STOP, requester, [nodeId])
            if allowed == False:
                raise Exception(constants.NO_OP + '\n' + str(info['msg']))
            fail_state = VM.STOP_FAILED
            success_state = VM.STOP_SUCCEEDED
        elif action == 'kill':
            allowed,info = StateTransition.is_allowed(ent.entity_id, VM.KILL, requester, [nodeId])
            if allowed == False:
                raise Exception(constants.NO_OP + '\n' + str(info['msg']))
            fail_state = VM.KILL_FAILED
            success_state = VM.KILL_SUCCEEDED
        elif action == 'migrate':
            allowed,info = StateTransition.is_allowed(ent.entity_id, VM.MIGRATE, requester, [nodeId])
            if allowed == False:
                raise Exception(constants.NO_OP + '\n' + str(info['msg']))
            fail_state = VM.MIGRATE_FAILED
            success_state = VM.MIGRATE_SUCCEEDED
        LOGGER.info(str(tid) + ' : call refresh node')
        node,dom = self.refresh_node(nodeId, domId,tid)
        LOGGER.info(str(tid)+ ' : refresh node over')
        return (node, dom, fail_state, success_state)
    #pass
    def refresh_node(self, nodeId, domId, tid=None):
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == nodeId).first()
        dom = DBSession.query(VM).filter(VM.id == domId).first()
        try:
            LOGGER.info(str(tid) + ' : refreshing dom object')
            if node.is_up():
                LOGGER.info(str(tid) + ' : refreshing dom object . going to the node')
                dom = node.get_dom(dom.name)
            else:
                LOGGER.info(str(tid) + ' : refreshing dom object . not going to the node. node is down')
        except Exception as e:
            print 'refresh_node Exception: ',
            print e
            LOGGER.error(str(tid) + ' : refreshing dom object error : ' + str(e))
        dom.node = node
        return (node, dom)

    def tail(self, f, n):
        pos, lines = n+1, []
        while len(lines) <= n:
            try:
                try:
                    f.seek(-pos, 2)
                except IOError:
                    f.seek(0)
                    break
            finally:
                    lines = list(f)
            pos *= 2
        return lines[-n:]

    def set_dom_device(self, auth, dom, boot):
        ent = auth.get_entity(dom.id)
        if not auth.has_privilege('SET_BOOT_DEVICE', ent):
            raise Exception(constants.NO_PRIVILEGE)
        vm_config = dom.get_config()
        if not vm_config:
            raise Exception('No configuration file associated with this VM.')
        if boot is not None:
            vm_config['boot'] = boot
            dom.vm_config = get_config_text(vm_config)
            DBHelper().add(dom)
            nodeid = ent.parents[0].entity_id
            mgd_node = DBSession.query(ManagedNode).filter(ManagedNode.id == nodeid).first()
            vm_config.set_managed_node(mgd_node)
            vm_config.set_filename(dom.get_config()['config_filename'])
            vm_config.write()


    def save_appliance_info(self, auth, dom, config):
        ent = auth.get_entity(dom.id)
        if not auth.has_privilege('SAVE_APPLIANCE_INFO', ent):
            raise Exception(constants.NO_PRIVILEGE)
        dom.vm_config = get_config_text(config)
        DBHelper().add(dom)
        nodeid = ent.parents[0].entity_id
        mgd_node = DBSession.query(ManagedNode).filter(ManagedNode.id == nodeid).first()
        config.set_managed_node(mgd_node)
        config.set_filename(dom.get_config()['config_filename'])
        config.write()
    #pass
    def migrate_vm(self, auth, dom_list, source_node_id, dest_node_id, isLive, isForce, migrate_all, requester=constants.CORE):
        managed_node = self.getNode(auth, source_node_id)
        dest_node = self.getNode(auth, dest_node_id)
        if dest_node.is_up():
            dest_node.connect()
        vm_list = []
        for domid in dom_list:
            doms = DBHelper().filterby(VM, [], [VM.id == domid])
            if len(doms) > 0:
                vm_list.append(doms[0])
        if migrate_all:
            self.migrateNode(auth, managed_node, dest_node, True, isForce, requester=requester)
        else:
            self.migrateDomains(auth, managed_node, vm_list, dest_node, True, isForce, requester=requester)
            LOGGER.info('start update metrics')
        try:
            LOGGER.info('start update metrics dest_node')
            self.updateMetrics(auth, None, dest_node.id)
            LOGGER.info('start update metrics src_node')
            self.updateMetrics(auth, None, managed_node.id)
        except Exception as e:
            traceback.print_exc()
            LOGGER.error(to_str(e))
        LOGGER.info('update metrics over')

    def resume_migrate_vm(self, auth, dom_list, source_node_id, dest_node_id, isLive, isForce, migrate_all, requester=constants.CORE, recover=False):
        managed_node = self.getNode(auth, source_node_id)
        dest_node = self.getNode(auth, dest_node_id)
        if dest_node.is_up():
            dest_node.connect()
        src_ent = DBSession.query(Entity).filter(Entity.entity_id == managed_node.id).first()
        dest_ent = DBSession.query(Entity).filter(Entity.entity_id == dest_node.id).first()
        running_vms = dest_node.get_running_vms()
        if migrate_all:
            (fail_ents, vm_ents) = (auth.get_entities(to_unicode(constants.DOMAIN), parent=src_ent), auth.get_entities(to_unicode(constants.DOMAIN), parent=src_ent))
            succ_ents = []
            for vm_ent in vm_ents:
                migration_status = False
                #migration_status = False
                if recover == True:
                    migration_status = running_vms.has_key(vm_ent.name)
                else:
                    migration_status = self.get_migration_status(running_vms, managed_node, vm_ent, dest_node)
                if migration_status == True:
                    succ_ents.append(vm_ent)
                    fail_ents.remove(vm_ent)
                    auth.update_entity_by_id(vm_ent.entity_id, parent=dest_ent)
            transaction.commit()
            if len(fail_ents)>0:
                names = [e.name for e in fail_ents]
                raise Exception('Failed to migrate following Virtual Machines: ' + to_str(names))
        else:
            fail_ents, vm_ents = (DBSession.query(Entity).filter(Entity.entity_id.in_(dom_list)).all(), DBSession.query(Entity).filter(Entity.entity_id.in_(dom_list)).all())
            pend_ents = []
            for vm_ent in vm_ents:
                if vm_ent.parents[0].entity_id == source_node_id:
                    migration_status = False
                    if recover == True:
                        migration_status = running_vms.has_key(vm_ent.name)
                    else:
                        migration_status = self.get_migration_status(running_vms, managed_node, vm_ent, dest_node)
                    if migration_status == True:
                        fail_ents.remove(vm_ent)
                        auth.update_entity_by_id(vm_ent.entity_id, parent=dest_ent)  
                    else:  
                        pend_ents.append(vm_ent.entity_id)   
                else: 
                    fail_ents.remove(vm_ent)
            transaction.commit()
            if len(fail_ents)>0:
                names = [e.name for e in fail_ents]
                raise Exception('Failed to migrate following Virtual Machines: ' + to_str(names))

        try:
            self.updateMetrics(auth, None, dest_node.id)
            self.updateMetrics(auth, None, managed_node.id)

        except Exception as e:
            traceback.print_exc()
            LOGGER.error(to_str(e))


    def get_migration_status(self, dest_running_vms, managed_node, vm_ent, dest_node):
        if dest_running_vms.has_key(vm_ent.name):
            dom = DBSession.query(VM).filter(VM.id == vm_ent.entity_id).first()
            wait_time = dom.get_wait_time(constants.MIGRATE)
            (disappeared, wait_time_over) = (False, False)
            if managed_node.is_up():
                src_running_vms = managed_node.get_running_vms()
                if src_running_vms.has_key(dom.name) or src_running_vms.has_key('migrating-' + dom.name):
                    disappeared,wait_time_over = self.wait_for_migration(wait_time, managed_node, dom.name, dest_node)
            if wait_time_over != True:
                return True
        return False
    #pass
    def get_ssh_info(self, auth, nodeId, address, client_platform):
        managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == nodeId).first()
        ret,msg = check_platform_expire_date(managed_node.get_platform())
        if ret == False:
            raise Exception(msg)
        result = {}
        hostname = str(managed_node.hostname)
        credentials = DBSession.query(Credential).filter(Credential.entity_id == nodeId).first()
        uname = str(credentials.cred_details['username'])
        port = str(credentials.cred_details['ssh_port'])
        client_config = ClientConfiguration()
        sshhost = client_config.get(constants.prop_ssh_forward_host)
        sshport = client_config.get(constants.prop_ssh_forward_port)
        sshuser = client_config.get(constants.prop_ssh_forward_user)
        sshpwd = client_config.get(constants.prop_ssh_forward_password)
        sshkey = client_config.get(constants.prop_ssh_forward_key)
        ssh_file_loc = client_config.get(constants.ssh_file)
        ssh_tunnel_setup = client_config.get(constants.prop_ssh_tunnel_setup)
        ssh_log_level = client_config.get(constants.prop_ssh_log_level)
        msg = 'ManagedNode Infos## hostname:%s, uname:%s, port:%s' % (hostname, uname, port)
        print msg
        LOGGER.info(msg)
        msg = 'IntermediateServer Infos## sshhost:%s, sshport:%s, sshuser:%s, sshpwd:%s, sshkey:%s, ssh_file_loc:%s, ssh_tunnel_setup:%s, ssh_log_level:%s' % (sshhost, sshport, sshuser, sshpwd, sshkey, ssh_file_loc, ssh_tunnel_setup, ssh_log_level)
        print msg
        LOGGER.info(msg)
        if sshhost == '' or sshhost != constants.LOCALHOST and (sshuser == '' or sshpwd == '') or sshport == '':
            msg = 'For non localhost intermediate server, please specify username, password and port in development.ini'
            print msg
            LOGGER.error(msg)
            raise Exception('SSH forwarding is not configured. ')
        ports = sshport.split(':')
        if len(ports) > 2L or len(ports) == 0L or sshport == None:
            raise Exception('SSH Port numbers are not configured properly. For Example,6900:7000')
        forward_port = None
        ssh_node = create_node(sshhost, sshuser, sshpwd)
        if ssh_node is None:
            raise Exception('Can not connect to SSH Host, ' + sshhost + '.')
        forward_port = str(ssh_node.get_unused_port(int(ports[0L]), int(ports[1L])))

        try:
            forward_port = str(ssh_node.get_unused_port(int(ports[0L]), int(ports[1])))
        except Exception as e:
            LOGGER.error(to_str(e))
            traceback.print_exc()
            raise e
        temp_file_name = forward_port + '_' + port + '_'
        temp_file = mktempfile(ssh_node, temp_file_name, '.log')
        log_level = '-d ' * int(ssh_log_level)
        cmd = 'socat ' + log_level + 'TCP-LISTEN:' + str(forward_port) + " EXEC:'/usr/bin/ssh -i " + str(ssh_file_loc) + ' -p ' + str(port) + ' ' + str(uname) + '@' + str(hostname) + ' socat - TCP\\:127.0.0.1\\:' + to_str(port) + " '> " + temp_file + ' 2>&1 &'
        print '-----cmd------',
        print cmd
        if ssh_tunnel_setup:
            result['forwarding'] = 'Enabled'
            msg = 'SSH forwarding enabled through Server:%s' % sshhost
            print msg
            LOGGER.info(msg)
            output,exit_code = ssh_node.node_proxy.exec_cmd(cmd, timeout=None)
            if exit_code == 1:
                raise Exception('Error forwarding the port to SSH Host. ' + output)
            if not sshuser:
                sshuser = 'root'
            applet_cmd = self.formAppletCommandForSSH(client_platform, forward_port, sshuser, sshhost, address)
        else:
            result['forwarding'] = 'Disabled'
            msg = 'SSH forwarding disabled'
            print msg
            LOGGER.info(msg)
            applet_cmd = self.formAppletCommandForSSH(client_platform, port, uname, hostname, None)
        print 'applet cmd==',
        print applet_cmd
        result['command'] = applet_cmd
        result['hostname'] = sshhost
        result['port'] = sshport
        result['server'] = hostname
        return result


    def formAppletCommandForSSH(self, osname, forwardport, username, host, address):
        applet_cmd = None
        port_variable = None
        value_map = {}
        (command, template_str) = (None, None)
        if osname == constants.WINDOWS:
            command = tg.config.get(constants.PUTTY_CMD)
            port_variable = str(forwardport) + ' '
            value_map[constants.PORT] = port_variable
        elif osname == constants.LINUX:
            command = tg.config.get(constants.SSH_CMD)
            port_variable = str(forwardport) + ' '
            value_map[constants.PORT] = port_variable

        if host == 'localhost' and address:
            host = address
        template_str = string.Template(command)
        value_map[constants.USER] = str(username)
        value_map[constants.APPLET_IP] = str(host)
        applet_cmd = to_str(template_str.safe_substitute(value_map))
        return applet_cmd
    #pass
    def get_vnc_info_use_vnc_applet(self, auth, nodeId, domId, address):
        managed_node = self.getNode(auth, nodeId)
        dom = self.get_dom(auth, domId)
        if not managed_node:
            raise Exception('Could not find server with ID:%s' % nodeId)
        if not dom:
            raise Exception('Could not find VM with ID:%s' % domId)
        return managed_node.get_vnc_info(dom, address)
    #pass
    def get_vnc_info_use_local_viewer(self, auth, nodeId, dom_id, cmd):
        import pylons
        import string
        import types
        managed_node = self.getNode(auth, nodeId)
        dom = self.get_dom(auth, dom_id)
        if not managed_node:
            raise Exception('Could not find server with ID:%s' % nodeId)
        if not dom:
            raise Exception('Could not find VM with ID:%s' % dom_id)
        command = tg.config.get(cmd)
        print '--command--',
        print command,
        print cmd
        info = {}
        host = pylons.request.headers['Host']
        if host.find(':') != -1L:
            address = host.split(':')
        else:
            address = host
        info = managed_node.get_vnc_info(dom, address)
        value_map = managed_node.get_console_local_viewer_param_dict(cmd, info)
        if command is not None:
            if type(command) in [types.StringType, types.UnicodeType]:
                template_str = string.Template(command)
                command = to_str(template_str.safe_substitute(value_map))
        print '---Gridmanager---get_vnc_info_use_local_viewer---applet_cmd---',
        print command
        return (command, info)
    #pass
    def collectVMMetrics(self, auth, node_id, metrics=None):
        managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).one()
        if metrics is None:
            try:
                if managed_node.is_up():
                    metrics = self.getNodeMetrics(auth, managed_node)
                else:
                    metrics = {}
            except Exception as e:
                metrics = {}
                traceback.print_exc()
                LOGGER.error(to_str(e))
        ent = auth.get_entity(managed_node.id)
        child_ents = auth.get_entities(to_unicode(constants.DOMAIN), parent=ent)
        keys = metrics.keys()
        for child_ent in child_ents:
            dom = DBSession.query(VM).filter(VM.id == child_ent.entity_id).one()
            allowed,info = StateTransition.is_allowed(child_ent.entity_id, VM.COLLECT, constants.CORE, change=False)
            if allowed == False:
                LOGGER.error('Not updating current metrics for VM ' + dom.name + '. Operation not allowed.' + '\n' + str(info['msg']))
                continue
            cont,msg = dom.status_check()
            if cont == False:
                LOGGER.error(msg)
                continue
            if msg is not None:
                LOGGER.error(msg)
            if child_ent.name in keys:
                dict_data = metrics[child_ent.name]
                self.insert_data(dict_data, child_ent)
                continue
            dict_data = {'STATE': VM.SHUTDOWN}
            dict_data['CLOUD_VM_ID'] = dom.cloud_vm_id
            managed_node.augment_storage_stats(child_ent.name, dict_data, dom)
            self.insert_data(dict_data, child_ent)


    def insert_data(self, dict_data, child_ent):
        vm_metrics_obj = MetricVMRaw()
        ms = MetricsService()
        try:
            LockManager().get_lock(constants.METRICS, child_ent.entity_id, constants.COLLECT_METRICS, constants.Table_metrics + '/' + constants.Table_metrics_curr)
            ms.insertMetricsData(dict_data, child_ent.entity_id, vm_metrics_obj)
        finally:
            LockManager().release_lock()
    #pass
    def collectServerMetrics(self, auth, m_node, filter=False):
        node_snapshot = {}
        if m_node is not None:
            try:
                if m_node.is_up():
                    node_snapshot = None
                    try:
                        strt = p_task_timing_start(MTR_LOGGER, 'NodeGetMterics', m_node.id)
                        node_snapshot = m_node.get_metrics(filter=filter)
                        p_task_timing_end(MTR_LOGGER, strt)
                    except Exception as ex:
                        print 'error getting info for ',
                        print m_node.hostname,
                        print ex
                        traceback.print_exc()
                    if node_snapshot is None:
                        node_snapshot = {}
                        node_snapshot['NODE_NAME'] = m_node.hostname
                    node_snapshot['NODE_NAME'] = m_node.hostname
                    node_snapshot['NODE_STATUS'] = 'Connected'
                else:
                    node_snapshot = {'NODE_NAME': m_node.hostname, 'NODE_STATUS': 'Not Connected'}
            except Exception as e:
                traceback.print_exc()
                LOGGER.error(e)
            node_snapshot['NODE_PLATFORM'] = m_node.platform
        ms = MetricsService()
        server_metrics_obj = MetricServerRaw()
        try:
            LockManager().get_lock(constants.METRICS, m_node.id, constants.COLLECT_METRICS, constants.Table_metrics + '/' + constants.Table_metrics_curr)
            ms.insertServerMetricsData(node_snapshot, m_node.id, server_metrics_obj)
        finally:
            LockManager().release_lock()
        return node_snapshot
    #pass
    def collectServerPoolMetrics(self, auth, pool_id):
        node_list = self.getNodeList(auth, pool_id)
        connected = 0
        for m_node in node_list:
            if m_node is  None:
                continue
            if m_node is not None:
                try:
                    if m_node.is_up():
                        connected = connected + 1
                except Exception as e:
                    LOGGER.error(e)
        ms = MetricsService()
        try:
            LockManager().get_lock(constants.METRICS, pool_id, constants.COLLECT_METRICS, constants.Table_metrics + '/' + constants.Table_metrics_curr)
            ms.collect_serverpool_metrics(pool_id, connected, auth)
        finally:
            LockManager().release_lock()

    def SyncAll(self, auth, site_id, group_id, def_type, def_manager):
        print '--------SyncAll----site_id, group_id, def_type, def_manager---------',
        print site_id,
        print group_id,
        print def_type,
        print def_manager
        defn_list = []
        sync_manager = SyncDef()
        node_id = None
        operation = None
        if def_type == constants.STORAGE:
            operation = 'STORAGE_POOL'
        else:
            if def_type == constants.NETWORK:
                operation = 'MANAGE_VIRTUAL_NETWORKS'
        if operation:
            ent = auth.get_entity(group_id)
            if not auth.has_privilege(operation, ent):
                raise Exception(constants.NO_PRIVILEGE)
            if not PrivilegeOps.check_child_privileges(auth, operation, ent):
                raise Exception(constants.NO_CHILD_PRIVILEGE % ('Servers', 'Server Pool'))
        if group_id:
            group = DBSession.query(ServerGroup).filter_by(id=group_id).first()
            if def_type == constants.STORAGE:
                defns = DBSession.query(SPDefLink).filter_by(group_id=group_id, status=constants.OUT_OF_SYNC, def_type=def_type)
                if defns:
                    if defns.count == 0:
                        LOGGER.info('No OUT_OF_SYNC record found for the group level definitions in Sync All operation.')
            elif def_type == constants.NETWORK:
                defns = []
                for node in group.getNodeList(auth).itervalues():
                    node_defns = DBSession.query(ServerDefLink).filter_by(server_id=node.id, status=constants.OUT_OF_SYNC, def_type=def_type)
                    if node_defns:
                        for each_node_defn in node_defns:
                            defns.append(each_node_defn)
                if len(node_defns) == 0:
                    LOGGER.info('No OUT_OF_SYNC record found for the definitions in Sync All operation.')
        if defns:
            for eachdefn in defns:
                defn = def_manager.get_defn(eachdefn.def_id)
                if defn:
                    defn_list.append(defn)
        if defn_list:
            op = constants.ATTACH
            if def_type == constants.STORAGE:
                transient_state = constants.STORAGE_SYNCING
                owner = constants.STORAGE
            else:
                if def_type == constants.NETWORK:
                    transient_state = constants.NETWORK_SYNCING
                    owner = constants.NETWORK
            sync_manager.SyncAll(site_id, group, defn_list, op, auth, def_manager, transient_state, owner, StateTransition)


    def SyncServer(self, auth, node_id, def_type, def_manager, sync_forcefully):
        node = None
        defn_list = []
        sync_manager = SyncDef()
        if sync_forcefully:
            node_defns = DBSession.query(ServerDefLink).filter_by(server_id=node_id, def_type=def_type)
        else:
            node_defns = DBSession.query(ServerDefLink).filter_by(server_id=node_id, status=constants.OUT_OF_SYNC, def_type=def_type)

        if node_defns:
            if node_defns.count() == 0 and sync_forcefully == False:
                LOGGER.info('No OUT_OF_SYNC record found for Sync Server operation.')
                return None
            if sync_forcefully:
                LOGGER.info('Sync definitions forcefully.')
    
            node = DBSession.query(ManagedNode).filter_by(id=node_id).first()
            try:
                node.connect()
            except Exception as ex:
                traceback.print_exc()
                raise Exception(to_str(ex))
    
            node_entity = auth.get_entity(node_id)
            group_id = node_entity.parents[0].entity_id
            group_entity = node_entity.parents[0]
            site_id = group_entity.parents[0].entity_id
            if node_defns.count() == 0:
                sync_manager.on_add_node(node_id, group_id, site_id, auth, def_manager)
                return None
            for eachdefn in node_defns:
                defn = def_manager.get_defn(eachdefn.def_id)
                if defn:
                    defn_list.append(defn)
            if def_type == constants.NETWORK:
                csep_list = DBSession.query(CSEP)
                if csep_list:
                    for csep in csep_list:
                        nw_svc_node = self.network_manager.get_nw_service_host(csep.id)
                        if nw_svc_node and node:
                            if nw_svc_node.hostname == node.hostname:
                                node_defns = DBSession.query(CSEPDefLink).filter_by(csep_id=csep.id, def_type=def_type)
                                if node_defns:
                                    for eachdefn in node_defns:
                                        defn = def_manager.get_defn(eachdefn.def_id)
                                        if defn:
                                            if defn.is_deleted == False:
                                                defn_list.append(defn)
    
            if defn_list:
                op = constants.ATTACH
                if def_type == constants.STORAGE:
                    transient_state = constants.STORAGE_SYNCING
                    owner = constants.STORAGE
                else:
                    if def_type == constants.NETWORK:
                        transient_state = constants.NETWORK_SYNCING
                        owner = constants.NETWORK
                sync_manager.SyncServer(site_id, group_id, defn_list, node, op, auth, def_manager, transient_state, owner, StateTransition, sync_forcefully)
    
            if def_type == constants.NETWORK:
                deleted_defn_list = []
                deleted_defn_list = DBSession.query(NwDef).filter_by(is_deleted=True)
                if deleted_defn_list:
                    for defn in deleted_defn_list:
                        LOGGER.info('Deleting definition ' + to_str(defn.name))
                        sync_manager.delete_defn(defn, auth, def_type, def_manager, self)


    def updateMetrics(self, auth, domId=None, nodeId=None, groupId=None):
        if domId is None and nodeId is None and groupId is None:
            self.collect_metrics_for_all_nodes(auth)
            return None

        if groupId is not None:
            node_list = self.getNodeList(auth, groupId)
            for m_node in node_list:
                if m_node is not None :
                    continue
                else:
                    node_id=m_node.id
                    node_snapshot = self.collectServerMetrics(auth, m_node)
                    self.collectVMMetrics(auth, node_id, node_snapshot)
            self.collectServerPoolMetrics(auth, groupId)
            return None

        if nodeId is not None:
            ent=auth.get_entity(nodeId)
            m_node=self.getNode(auth, nodeId)
            if m_node is None :
                return None
            node_snapshot=self.collectServerMetrics(auth, m_node)
            self.collectVMMetrics(auth, nodeId, node_snapshot)
            pool_id=ent.parents[0].entity_id
            self.collectServerPoolMetrics(auth, pool_id)
            return None
        if domId is not None:
            ent=auth.get_entity(domId)
            node=ent.parents[0]
            m_node=self.getNode(auth, node.entity_id)
            if m_node is None :
                return None
            node_snapshot=self.collectServerMetrics(auth, m_node)
            self.collectVMMetrics(auth, node.entity_id, node_snapshot)
            pool_id=node.parents[0].entity_id
            self.collectServerPoolMetrics(auth, pool_id)
            return None

    def getSiteByGroupId(self, group_id):
        site = None
        entity = DBSession.query(EntityRelation).filter_by(dest_id=group_id).first()
        if entity:
            site = DBSession.query(Site).filter_by(id=entity.src_id).first()
        return site

    def getSite(self, site_id):
        site = DBSession.query(Site).filter_by(id=site_id).first()
        return site

    def send_notifications(self, auth):
        notification_count = 500
        try:
            notification_count = int(tg.config.get(constants.NOTIFICATION_COUNT))
        except Exception as e:
            print 'Exception: ',
            print e
        emanager = EmailManager()
        check_email_setup = emanager.get_emailsetupinfo()
        if len(check_email_setup) > 0L:
            notifications = DBSession.query(Notification).filter(Notification.mail_status == False).order_by(Notification.error_time.asc()).limit(notification_count).all()
            for n in notifications:
                sent = False
                email = n.emailId
                if n.subject is None:
                    message = n.task_name + ' Task failed at ' + to_str(n.error_time) + '\n\n' + to_str(n.error_msg)
                    subject = 'stackone - Failed Task: ' + n.task_name
                else:
                    subject = n.subject
                    message = to_str(n.error_msg)
                sent = emanager.send_email(email, message, subject, 'html')
                if sent == True:
                    n.mail_status = True
                    DBHelper().update(n)
                else:
                    LOGGER.error('Error Sending Notification:-' + subject)
                    break
        return None

    def get_vm_disks_from_UI(self, vm_id, config):
        vm_disks = []
        if config:
            storage_status_object = config.get('storage_status_object')
            if storage_status_object:
                disk_stat = storage_status_object.get('disk_stat')
                if disk_stat:
                    for each_disk_stat in disk_stat:
                        disk = {}
                        vm_disk_id = None
                        objVMDisk = DBSession.query(VMDisks).filter_by(vm_id=vm_id, disk_name=each_disk_stat.get('filename')).first()
                        if objVMDisk:
                            vm_disk_id = objVMDisk.id
                        disk['vm_id'] = vm_id
                        disk['id'] = vm_disk_id
                        disk['disk_name'] = each_disk_stat.get('filename')
                        disk['read_write'] = each_disk_stat.get('mode')
                        disk['backup_content'] = each_disk_stat.get('backup_content')
                        vm_disks.append(disk)
        return vm_disks

    #tianfeng
    def manage_vm_disks(self, auth, vm_id, node_id, config, mode, removed_disk_list, action=None, new_disk_list=None):
        vm = DBSession.query(VM).filter_by(id=vm_id).first()
        vm_config = None
        vm_name = None
        if vm:
            vm_name = vm.name
            vm_config = vm.get_config()
            vm_config.set_id(vm_id)
            managed_node = DBSession.query(ManagedNode).filter_by(id=node_id).first()
            vm_config.set_managed_node(managed_node)
            config = vm.get_UI_config(config)
        if config:
            #1196
            storage_status_object = config.get('storage_status_object')
            if not storage_status_object:
                config = vm.get_UI_config()
                if config:
                    storage_status_object = config.get('storage_status_object')
            if storage_status_object:
                disk_stat = storage_status_object.get('disk_stat')
                if disk_stat:
                    self.remove_all_vm_storage_links(vm_id, action)
                    sequence = 0
                    for each_disk_stat in disk_stat:
                        sd = None
                        storage_id = None
                        storage_disk_id = None
                        storage_disk_id = each_disk_stat.get('each_disk_stat')
                        disk_name = each_disk_stat.get('filename')
                        if disk_name and not storage_disk_id:
                            sd = DBSession.query(StorageDisks).filter_by(unique_path=disk_name).first()
                            if sd:
                                storage_id = sd.storage_id
                                storage_disk_id = sd.id                        
                        dev_type = each_disk_stat.get('device')
                        read_write = each_disk_stat.get('mode')
                        is_shared = each_disk_stat.get('shared')
                        backup_content = each_disk_stat.get('backup_content')
                        skip_backup = each_disk_stat.get('skip_backup')
                        disk_entry = each_disk_stat.get('disk_entry')
                        actual_size = 0
                        if disk_name:
                            actual_size,disk_dev_type = VMDiskManager(vm_config).get_disk_size(None, disk_name)
                        actual_size_GB = self.storage_manager.convert_to_GB_from_Bytes(actual_size)
                        disk_size = each_disk_stat.get('size')
                        disk_size_GB = self.storage_manager.convert_to_GB(disk_size)
                        if mode == 'EDIT_VM_CONFIG' or mode == 'EDIT_VM_INFO' or mode == 'PROVISION_VM':
                            if disk_size == 'null' or disk_size == '' or disk_size == None or disk_size == 0:
                                disk_size = self.storage_manager.convert_to_MB(actual_size_GB)
                                disk_size_GB = self.storage_manager.convert_to_GB(disk_size)
                        
                        disk_type = each_disk_stat.get('type')
                        file_system = each_disk_stat.get('fs_type')
                        if not storage_id:
                            storage_id = each_disk_stat.get('storage_id')
                        defn = None
                        storage_type = ''
                        if new_disk_list and not storage_id:
                            for each_new_disk in new_disk_list:
                                if disk_name == each_new_disk.get('name'):
                                    storage_id = each_new_disk.get('storage_id')
    
                        defn = StorageManager().get_defn(storage_id)
                        if defn:
                            storage_type = defn.type
                        if (mode == 'PROVISION_VM' or mode == 'EDIT_VM_CONFIG' or mode == 'EDIT_VM_INFO') and storage_type in StorageManager().STORAGE_FOR_CREATION:
                            storage_allocated = False
                            added_manually = False
                            storage_disk_id = self.storage_manager.add_storage_disk(storage_id, actual_size_GB, disk_size_GB, disk_name, None, None, None, None, storage_allocated, self, added_manually, defn)
                            disk_size_GB = actual_size_GB
                        vm_memory = None
                        vm_disk = self.add_vm_disk(vm_id, disk_name, disk_size_GB, dev_type, read_write, disk_type, is_shared, file_system, backup_content, vm_memory, sequence, skip_backup)
                        sequence = sequence + 1
                        self.add_vm_storage_link(vm_disk.id, storage_disk_id)
                        op = '+'
                        self.storage_manager.calculate_disk_size(storage_disk_id, vm_disk.id, disk_size, op, action)
        error_msg = None
        error_msg = self.matching_on_AddEditDelete_vm(auth, mode, vm_id, removed_disk_list)
        if error_msg:
            raise Exception(error_msg)

    def add_vm_disk(self, vm_id, disk_name, disk_size, dev_type, read_write, disk_type, is_shared, file_system, backup_content, vm_memory=None, sequence=None, skip_backup=False):
        vm_disk = VMDisks()
        vm_disk.id = getHexID()
        vm_disk.vm_id = vm_id
        vm_disk.disk_name = disk_name
        if not disk_size:
            disk_size = 0
        vm_disk.disk_size = float(disk_size)
        vm_disk.dev_type = dev_type
        vm_disk.read_write = read_write
        vm_disk.disk_type = disk_type
        vm_disk.is_shared = is_shared
        vm_disk.file_system = file_system
        vm_disk.backup_content = backup_content
        if vm_memory:
            vm_disk.vm_memory = vm_memory
        else:
            vm_disk.vm_memory = self.get_vm_memory(vm_id)

        vm_disk.sequence = sequence
        vm_disk.skip_backup = skip_backup
        DBSession.add(vm_disk)
        return vm_disk

    def add_vm_storage_link(self, vm_disk_id, storage_disk_id):
        try:
            vm_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=vm_disk_id, storage_disk_id=storage_disk_id).first()
            if not vm_link:
                if storage_disk_id:
                    vm_storage_link = VMStorageLinks()
                    vm_storage_link.id = getHexID()
                    vm_storage_link.vm_disk_id = vm_disk_id
                    vm_storage_link.storage_disk_id = storage_disk_id
                    DBSession.add(vm_storage_link)
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error('Can not add duplicate vm disk and storage disk link.')

    def get_vm_memory(self, vm_id):
        vm_memory = 0
        vm = DBSession.query(VM).filter_by(id=vm_id).first()
        if vm:
            vm_config = vm.vm_config
            if vm_config:
                vm_config_param_list = str(vm_config).split('=')
                for each_param in vm_config_param_list:
                    if each_param[0].strip() == 'memory':
                        vm_memory = each_param[1].strip()
        return vm_memory

    def remove_storage_disk_links(self, storage_disk_id, action=None):
        link_list = DBSession.query(VMStorageLinks).filter_by(storage_disk_id=storage_disk_id)
        for vm_storage_link in link_list:
            self.remove_storage_disk_link(vm_storage_link, action)

    def remove_storage_disk_link(self, vm_storage_link, action=None):
        storage_disk_id = vm_storage_link.storage_disk_id
        vm_disk_id = vm_storage_link.vm_disk_id
        DBSession.delete(vm_storage_link)
        vm_disk = DBSession.query(VMDisks).filter_by(id=vm_disk_id).first()
        if vm_disk:
            disk_size = vm_disk.disk_size
        op = '-'
        self.storage_manager.calculate_disk_size(storage_disk_id, vm_disk_id, disk_size, op, action)

    def remove_vm_storage_link(self, vm_disk_id, action=None):
        vm_storage_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=vm_disk_id).first()
        if vm_storage_link:
            self.remove_storage_disk_link(vm_storage_link, action)

    def remove_vm_storage_links_only(self, vm_id, action=None):
        vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
        if vm_disks:
            for vm_disk in vm_disks:
                self.remove_vm_storage_link(vm_disk.id, action)

    def remove_all_vm_storage_links(self, vm_id, action=None):
        vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
        if vm_disks:
            for vm_disk in vm_disks:
                self.remove_vm_storage_link(vm_disk.id, action)
                self.remove_vm_disk(vm_disk.id)

    def remove_vm_links_to_storage(self, storage_id, vm_id_list=None, action=None):
        storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=storage_id)
        if storage_disks:
            for eachdisk in storage_disks:
                vm_storage_links = []
                if vm_id_list:
                    for vm_id in vm_id_list:
                        v_s_link = DBSession.query(VMStorageLinks).join((VMDisks, VMDisks.id == VMStorageLinks.vm_disk_id)).join((VM, VM.id == VMDisks.vm_id)).filter(VM.id == vm_id).filter(VMStorageLinks.storage_disk_id == eachdisk.id).first()
                        vm_storage_links.append(v_s_link)
                else:
                    vm_storage_links = DBSession.query(VMStorageLinks).filter_by(storage_disk_id=eachdisk.id)

                if vm_storage_links:
                    for eachlink in vm_storage_links:
                        if eachlink:
                            self.remove_vm_storage_link(eachlink.vm_disk_id, action)
                            self.remove_vm_disk(eachlink.vm_disk_id)

    def remove_vm_disk(self, vm_disk_id):
        vm_disk = DBSession.query(VMDisks).filter_by(id=vm_disk_id).first()
        if vm_disk:
            DBSession.delete(vm_disk)

    def update_vm_disks(self, auth, vm_id, node_id, config):
        if config:
            self.remove_all_vm_storage_links(vm_id)
            self.add_vm_disks_from_config(config)
        self.matching_vm_disks(auth, vm_id)
    #pass
    def add_vm_disks_from_config(self, config):
        from stackone.viewModel.VMService import VMService
        if config:
            filename = None
            disk_size = 0
            device = None
            mode = None
            type = None
            is_shared = False
            file_system = None
            backup_content = None
            i = 0
            disk_manager = config.get_disk_manager()
            
            vm = DBSession.query(VM).filter_by(name=config.name).first()
            if vm:
                vm_id = vm.id
                for de in config.getDisks():
                    type = de.type
                    filename = de.filename
                    device = de.device
                    mode = de.mode
                    disk_size,device_temp = disk_manager.get_disk_size(de,filename,vm.name)
                    #disk_size,device_temp = VMDiskManager(config).get_disk_size(None, filename)
                    backup_content = VMService().get_backup_content(config, filename)
                    disk_size_temp = self.storage_manager.convert_to_GB_from_Bytes(disk_size)
                    vm_disk = self.add_vm_disk(vm_id, filename, disk_size_temp, device, mode, type, is_shared, file_system, backup_content, sequence=i)
                    i += 1

    def pre_matching_on_AddEditDelete_vm(self, auth, mode, vm_id, vm_disks=None):
        LOGGER.info('Running pre-matching logic for VM disks...')
        start = p_timing_start(STRG_LOGGER, 'pre_matching_on_AddEditDelete_vm', log_level='DEBUG')
        error_msg = ''
        if mode == 'PROVISION_VM' or mode == 'IMPORT_VM_CONFIG_FILE' or mode == 'TRANSFER_SERVER' or mode == 'EDIT_VM_CONFIG' or mode == 'EDIT_VM_INFO' or  mode == 'REMOVE_VM':
            if not vm_disks:
                return error_msg 
            for each_vm_disk in vm_disks:
                disk_name = each_vm_disk.get('disk_name')
                read_write = each_vm_disk.get('read_write')
                LOGGER.info('Disk name is ' + to_str(disk_name))
                if read_write == 'w':
                    result = DBSession.query(VMDisks).join((StorageDisks, StorageDisks.unique_path == VMDisks.disk_name))\
                    .join((VMStorageLinks, VMStorageLinks.storage_disk_id == StorageDisks.id))\
                    .join((VM, VM.id == VMDisks.vm_id)).filter(StorageDisks.storage_allocated == True)\
                    .filter(VMDisks.read_write != 'r').filter(VMDisks.disk_name == disk_name).filter(VM.id != vm_id).first()
                    if result:
                        rs = DBSession.query(VM.name, VMDisks.disk_name).join((VMDisks, VMDisks.vm_id == VM.id)).filter(VMDisks.id == result.id).first()
                        error_msg = 'Invalid disk entry. Storage disk ' + to_str(rs.disk_name) + ' is allocated to virtual machine ' + to_str(rs.name) + ' in read-write mode.'
                        LOGGER.error(to_str(error_msg))

        p_timing_end(STRG_LOGGER, start)
        return error_msg

    def matching_on_AddEditDelete_vm(self, auth, mode, vm_id, removed_disk_list=None):
        start = p_timing_start(STRG_LOGGER, 'matching_on_AddEditDelete_vm ', log_level='DEBUG')
        error_msg = None
        if mode == 'PROVISION_VM' or mode == 'TRANSFER_SERVER' or mode == 'EDIT_VM_CONFIG' or mode == 'EDIT_VM_INFO' or mode == 'REMOVE_VM':
            error_msg = self.matching_vm_disks(auth, vm_id, removed_disk_list)
        p_timing_end(STRG_LOGGER, start)
        return error_msg

    def get_vms_from_pool(self, auth, group_id):
        vm_list = []
        if group_id:
            group_entity = auth.get_entity(group_id)
            node_entities = auth.get_entities(to_unicode(constants.MANAGED_NODE), group_entity)
            if node_entities:
                for eachnode in node_entities:
                    vm_entities = auth.get_entities(to_unicode(constants.DOMAIN), eachnode)
                    for eachvm in vm_entities:
                        vm = DBSession.query(VM).filter_by(id=eachvm.entity_id).first()
                        if vm:
                            vm_list.append(vm)
        return vm_list

    def get_vm_disks_from_pool(self, auth, group_id):
        vm_disk_list = []
        if group_id:
            group_entity = auth.get_entity(group_id)
            node_entities = auth.get_entities(to_unicode(constants.MANAGED_NODE), group_entity)
            if node_entities:
                for eachnode in node_entities:
                    vm_entities = auth.get_entities(to_unicode(constants.DOMAIN), eachnode)
                    for eachvm in vm_entities:
                        vm_disks = DBSession.query(VMDisks).filter_by(vm_id=eachvm.entity_id)
                        if vm_disks:
                            for eachdisk in vm_disks:
                                vm_disk_list.append(eachdisk)

        return vm_disk_list
    def get_storage_disks_from_pool(self, group_id):
        start = p_timing_start(STRG_LOGGER, 'pre_matching (get_storage_disks_from_pool) ', log_level='DEBUG')
        storage_disk_list = []
        if group_id:
            storage_disks = DBSession.query(StorageDisks.id, StorageDisks.storage_id, StorageDisks.storage_type, StorageDisks.disk_name, StorageDisks.mount_point, StorageDisks.file_system, StorageDisks.actual_size, StorageDisks.size.label('disk_size'), StorageDisks.unique_path, StorageDisks.current_portal, StorageDisks.target, StorageDisks.state, StorageDisks.lun, StorageDisks.storage_allocated, StorageDisks.added_manually, StorageDisks.transient_reservation).join((StorageDef, StorageDef.id == StorageDisks.storage_id)).join((SPDefLink, SPDefLink.def_id == StorageDef.id)).filter(SPDefLink.group_id == group_id)
            if storage_disks:
                return storage_disks
        p_timing_end(STRG_LOGGER, start)
        return storage_disk_list

    def get_storage_disks_from_storage(self, storage_id):
        storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=storage_id)
        return storage_disks

    def matching_vm_disks(self, auth, vm_id, removed_disk_list=None):
        start = p_timing_start(STRG_LOGGER, 'matching_vm_disks ')
        error_msg = ''
        if vm_id:
            vm_disks = DBSession.query(VMDisks).filter_by(vm_id = vm_id)
            if vm_disks:
                LOGGER.info('Matching for the VM which is being processed...')
                for each_vm_disk in vm_disks:
                    disk_name = each_vm_disk.disk_name
                    LOGGER.info('Disk name - ' + to_str(disk_name))
                    s_disk = DBSession.query(StorageDisks).filter(StorageDisks.unique_path == disk_name).first()
                    if s_disk:
                        isMatched,msg = self.matching_logic(each_vm_disk, s_disk)
            if removed_disk_list:
                LOGGER.info('Matching for removed disks...Lets see if other VM can use this disk...')
                for removed_disk in removed_disk_list:
                    disk_name = removed_disk
                    LOGGER.info('Removed disk name - ' + to_str(disk_name))
                    rs = DBSession.query(VMDisks, StorageDisks).join((StorageDisks, StorageDisks.unique_path == VMDisks.disk_name)).join((VM, VM.id == VMDisks.vm_id)).filter(VMDisks.disk_name == disk_name).filter(VM.id != vm_id).first()
                    if rs:
                        v_disk = rs[0]
                        s_disk = rs[1]
                        isMatched,msg = self.matching_logic(v_disk, s_disk)
        p_timing_end(STRG_LOGGER, start)
        return error_msg

    def matching_disk_on_discover_storage(self, vm_disks, storage_disk_id):
        if vm_disks:
            storage_disk = DBSession.query(StorageDisks).filter_by(id=storage_disk_id).first()
            if storage_disk:
                for each_vm_disk in vm_disks:
                    self.matching_logic(each_vm_disk, storage_disk)

    def matching_logic(self, vm_disk, storage_disk):
        start = p_timing_start(STRG_LOGGER, 'matching_logic ')
        isMatched = False
        msg = None
        if str(vm_disk.disk_name).strip() == str(storage_disk.unique_path).strip():
            LOGGER.info('Matching disk (' + str(vm_disk.disk_name) + ') is found')
            if storage_disk.storage_allocated == False:
                LOGGER.info('Storage (' + str(vm_disk.disk_name) + ') is not allocated')
                self.add_vm_storage_link(vm_disk.id, storage_disk.id)
                LOGGER.info('vm storage link is updated')
                vm_disk.is_shared = True
                vm_disk.read_write = 'w'
                isMatched = True
                op = '+'
                self.storage_manager.calculate_disk_size(storage_disk.id, vm_disk.id, vm_disk.disk_size, op)
            else:
                if vm_disk.read_write == 'r':
                    LOGGER.info('Storage (' + to_str(vm_disk.disk_name) + ') is allocated. Adding vm disk link in readonly mode.')
                    self.add_vm_storage_link(vm_disk.id, storage_disk.id)
                    vm_disk.is_shared = True
                    isMatched = True
                    op = '+'
                    self.storage_manager.calculate_disk_size(storage_disk.id, vm_disk.id, vm_disk.disk_size, op)
                else:
                    isMatched = True
                    vm_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=vm_disk.id, storage_disk_id=storage_disk.id).first()
                    if vm_link:
                        LOGGER.info('vm disk and storage disk link already exists so we are not throwing exception or logging error.')
                    else:
                        LOGGER.error('Matching disk (' + str(vm_disk.disk_name) + ') is found. The disk is already allocated and in read-write mode. So it is invalid disk entry.')
                        msg = 'Invalid disk entry.'

        p_timing_end(STRG_LOGGER, start)
        return (isMatched, msg)

    def submit_vm_tasks(self, auth, dom, context, scheduling_dic, mode):
        try:
            from stackone.viewModel.TaskCreator import TaskCreator
            tc = TaskCreator()
            if not scheduling_dic:
                scheduling_dic = {}
            start_taskid = None
            task_data = {}
            if mode == 'EDIT_VM_CONFIG' or mode == 'EDIT_VM_INFO':
                tasks = DBSession.query(Task).filter(Task.task_id.in_([dom.start_taskid, dom.reboot_taskid, dom.shutdown_taskid, dom.delete_taskid])).all()
                for task in tasks:
                    if len(task.result) == 0:
                        tc.delete_task([task.task_id])
            if mode != 'EDIT_VM_INFO':
                if scheduling_dic.get('start_on') == 'Later':
                    date = scheduling_dic.get('start_date')
                    time = scheduling_dic.get('start_time')
                    result = tc.vm_action(auth, dom.id, context.managed_node.id, constants.START, date, time)
                    start_taskid = result
                else:
                    if scheduling_dic.get('start_on') == 'On Provisioning' and mode == 'PROVISION_VM':
                        result = tc.vm_action(auth, dom.id, context.managed_node.id, constants.START, None, None)
                        start_taskid = result
                    else:
                        start_taskid = None
    
            task_data['start_taskid'] = start_taskid
            shutdown_taskid = None
            delete_taskid = None
            if scheduling_dic.get('retire') == 'Specific Date':
                date = scheduling_dic.get('retire_date')
                time = scheduling_dic.get('retire_time')
                if scheduling_dic.get('on_retire') == 'Shutdown':
                    result = tc.vm_action(auth, dom.id, context.managed_node.id, constants.SHUTDOWN, date, time)
                    shutdown_taskid = result
                    delete_taskid = None
                else:
                    if scheduling_dic.get('on_retire') == 'Delete':
                        result = tc.vm_remove_action(auth, dom.id, context.managed_node.id, force=False, dateval=date, timeval=time)
                        delete_taskid = result
                        shutdown_taskid = None
            else:
                shutdown_taskid = None
                delete_taskid = None
    
            task_data['shutdown_taskid'] = shutdown_taskid
            task_data['delete_taskid'] = delete_taskid
            restart_taskid = None
            if scheduling_dic.get('restart_on') == 'Later':
                date = scheduling_dic.get('restart_date')
                time = scheduling_dic.get('restart_time')
                result = tc.vm_action(auth, dom.id, context.managed_node.id, constants.REBOOT, date, time)
                restart_taskid = result
    
            task_data['restart_taskid'] = restart_taskid
            email_id = None
            minutes_before = None
            rep_interval = None
            if scheduling_dic.get('retire') == 'Specific Date':
                email_id = scheduling_dic.get('email_id')
                day_min = scheduling_dic.get('email_days_before', 0) * 24 * 60
                hr_min = scheduling_dic.get('email_hours_before', 0) * 60
                minutes_before = day_min + hr_min
                hr_min = scheduling_dic.get('email_rep_hours', 0) * 60
                min = scheduling_dic.get('email_rep_min', 0)
                rep_interval = hr_min + min
            else:
                email_id = None
                minutes_before = None
                rep_interval = None
    
            task_data['email_id'] = email_id
            task_data['minutes_before'] = minutes_before
            task_data['rep_interval'] = rep_interval
    
        except Exception as ex:
            traceback.print_exc()

        return task_data

    def check_vm_on_nodes(self, auth, dom, node):
        vm_exists = False
        msg = ''
        o_vm = DBSession.query(OutsideVM).filter(OutsideVM.name == dom.name).first()
        if o_vm is not None:
            vm_node = DBHelper().find_by_id(ManagedNode, o_vm.node_id)
            if vm_node is not None and vm_node.is_up():
                if dom.name in vm_node.get_running_vms().keys():
                    entity = auth.get_entity(dom.id)
                    parent_ent = DBSession.query(Entity).filter(Entity.entity_id == vm_node.id).first()
                    auth.update_entity(entity, parent=parent_ent)
                    self.updateMetrics(auth, dom.id, vm_node.id)
                    vm_node = DBHelper().find_by_id(ManagedNode, o_vm.node_id)
                    vm_node.refresh_vm_avail()
                    DBSession.query(OutsideVM).filter(OutsideVM.node_id == vm_node.id).filter(OutsideVM.name == dom.name).delete()
                    transaction.commit()

                    from stackone.model.UpdateManager import UIUpdateManager
                    UIUpdateManager().set_updated_entities(node.id)
                    msg = 'VM found running on the node ' + vm_node.hostname + '. Marking VM as started'
                    LOGGER.info(msg)
                    vm_exists = True
        return (msg, vm_exists)
    ############# hotaddNic  20130624
    def hot_add_nic(self,auth,dom,v,device_k):
        from stackone.core.utils.utils import get_slot_number,device_tag
        kvm =dom.node.get_vmm()
        cmd = 'pci_add auto nic '+v
        (output,prompt) = kvm.send_command(dom.pid,cmd)
        if prompt == True:
            slot =  get_slot_number(output).strip()
            device_tag(device_k+'*'+slot)
        

    def hot_create_disk(self,auth,managed_node,file_path,disk_size):
        cmd = 'qemu-img create -f qcow2  %s  %s' %(file_path,disk_size)
        #if not os.path.exists(file_path):
        output,exit_code = managed_node.node_proxy.exec_cmd(cmd)
        LOGGER.info('Exit Code= ' + to_str(exit_code))
        LOGGER.info('Output of script= ' + to_str(output))
        return (exit_code, output)
        
    def hot_add_disk(self,auth,dom,file_path,disk_type,device_k):
        from stackone.core.utils.utils import get_slot_number,device_tag
        cmd  = 'pci_add auto storage file=%s,if=%s' %(file_path,disk_type)
        kvm =dom.node.get_vmm()
        try:
            (output,prompt) = kvm.send_command(dom.pid,cmd)
            if prompt == True:
                slot =  get_slot_number(output).strip()
                device_tag(device_k+'*'+slot)
        except Exception,e:
            raise Exception('hot add faild '+e)
    
    def hot_delete_Device(self,auth,managed_node,dom,device_k,filepath):
        from stackone.core.utils.utils import get_device_solt
        solt = get_device_solt(device_k)
        cmd  = 'pci_del pci_addr=%s' %solt
        try:
            kvm =dom.node.get_vmm()
            (output,prompt) = kvm.send_command(dom.pid,cmd)
        except Exception,e:
            raise Exception('hot delete faild ' + e)
        if filepath:
            cmd = 'rm -f %s' %filepath
            output,exit_code = managed_node.node_proxy.exec_cmd(cmd)
            LOGGER.info('Exit Code= ' + to_str(exit_code))
            LOGGER.info('Output of script= ' + to_str(output))
            return (exit_code, output)
    def get_virtual_size(self,source_node,disk_name):
        from stackone.core.utils.utils import get_virtual_size
        cmd = 'qemu-img info %s' %disk_name
        output,exit_code = source_node.node_proxy.exec_cmd(cmd)
        LOGGER.info('Exit Code= ' + to_str(exit_code))
        LOGGER.info('Output of script= ' + to_str(output))
        disk_size = get_virtual_size(output)
        return disk_size
        
    def start_add_nic_storage(self,auth,dom,managed_node,config):
        dir_path = '/home/stackone/nic_disk'
        if not os.path.exists(dir_path):
            os.mkdir(dir_path)
        files = os.listdir(dir_path) 
        for k in config.keys():
            v = config.get(k)
            if k.startswith('nic_model') or k.startswith('storage_disk'):
                find_file = '*'.join([managed_node.id,dom.name,k])
                for f in files:
                    file_tag = '*'.join(f.split('*')[:-1])
                    if file_tag == find_file:
                        os.remove(os.path.join(dir_path,f))
                        break
                #dom = managed_node.get_dom(dom.name)
                if k.startswith('nic_model'):
                    v = v.split(',')[0]
                    self.hot_add_nic(auth,dom, v, find_file)
                elif k.startswith('storage_disk'):
                    file_path,disk_type,disk_size,action = v.split(',')
                    self.hot_add_disk(auth,dom, file_path, disk_type, find_file)
    #  archer 20131129  hot add USB
    def get_usb_pci(self,auth,managed_node):
        cmd = 'lsusb'
        #if not os.path.exists(file_path):
        output,exit_code = managed_node.node_proxy.exec_cmd(cmd)
        LOGGER.info('Exit Code= ' + to_str(exit_code))
        LOGGER.info('Output of script= ' + to_str(output))
        if exit_code == 0:
            output = [ms for ms in output.split('\n') if len(ms)>0]
        return {'success_code':exit_code, 'message':output}
    #host:bus.addr
    def hot_add_usb(self,auth,managed_node,dom,usb_info):
        from stackone.core.utils.utils import get_bus_addr
        print '##########hot_add_usb#######',usb_info
        (bus,addr) = get_bus_addr(usb_info)
        print '########(bus,addr)###############',(bus,addr)
        try:
            bus = int(bus)
            addr = int(addr)
            if bus != -1 and addr != -1:
                cmd  = 'usb_add  host:%s.%s' %(bus,addr)
                kvm =dom.node.get_vmm()
                try:
                    #(output,prompt) = kvm.send_command(dom.pid,cmd)
                    #if prompt and output == cmd:
                    #return True
                    if self.sed_command_true(kvm, dom.pid, cmd)[0]:
                        return  {'success':'true','message':'usb add successfully'}
                except Exception,e:
                    raise Exception('hot add faild '+str(e))
                    return {'success':'false','message':e}
            else:
                return {'success':'false','message':'can not find usb to add'}
        except Exception,e:
            raise Exception('hot add usb faild '+str(e))
    def get_usb_device(self,auth,managed_node,dom,usb_info):
        cmd  = 'info  usb'
        kvm =dom.node.get_vmm()
        try:
            #(output,prompt) = kvm.send_command(dom.pid,cmd)
            #if prompt and output == cmd:
            #return output
            print '########get_usb_device#########'
            flag,output =  self.sed_command_true(kvm, dom.pid, cmd)
            print '##########flag ,output###############',flag,output
            if flag:
                return output 
        except Exception,e:
            raise Exception('hot add faild '+str(e))
    def hot_del_usb(self,auth,managed_node,dom,usb_info):
        from stackone.core.utils.utils import get_device
        usb_info = self.get_usb_device(auth, managed_node, dom, usb_info)
        device = get_device(usb_info)
        if device != -1:
            cmd  = 'usb_del  %s' %device
            print cmd 
            kvm =dom.node.get_vmm()
            try:
                #(output,prompt) = kvm.send_command(dom.pid,cmd)
                #print output,prompt,'################output,prompt###########'
                #if prompt and output == cmd:
                #return True
                if self.sed_command_true(kvm, dom.pid, cmd)[0]:
                    return  {'success':'true','message':'usb del successfully'}
            except Exception,e:
                raise Exception('hot del faild '+str(e))
                return {'success':False,'message':e}
        else:
            return {'success':'false','message':'can not find usb to del'}
    def sed_command_true(self,kvm,pid,cmd):
        (output,prompt) = kvm.send_command(pid,cmd)
        return True,output
        
