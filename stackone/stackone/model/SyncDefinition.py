from datetime import datetime
from stackone.core.utils.utils import copyToRemote, get_path, mkdir2, getHexID
from stackone.core.utils.utils import to_unicode, to_str, get_cms_network_service_node
import stackone.core.utils.utils
from stackone.core.utils.constants import *
constants = stackone.core.utils.constants
import os
import transaction
import traceback
import fileinput
from tg import session
from stackone.model import DBSession, Entity
from stackone.model.SPRelations import ServerDefLink, SPDefLink, DCDefLink, Storage_Stats, CSEPDefLink
from stackone.model.Sites import Site
from stackone.model.Groups import ServerGroup
from stackone.model.ManagedNode import ManagedNode
from stackone.model.Metrics import MetricsCurr
from stackone.model.VM import VM, VMStorageLinks
from stackone.model.PrivilegeOps import PrivilegeOps
from stackone.model.IPManager import IPManager
from sqlalchemy.orm import eagerload
import logging
LOGGER = logging.getLogger('stackone.model')
class SyncDef():
    def __init__(self):
        pass

    def is_node_in_sync(self, node, def_type):
        in_sync = True
        def_link = DBSession.query(ServerDefLink).filter_by(server_id=node.id, def_type=def_type, status=constants.OUT_OF_SYNC)
        if def_link:
            if def_link.count() > 0:
                in_sync = False
        return in_sync


    def in_sync(self, auth, entity, state_owner):
        in_sync = False
        ent_type = entity.type.name
        if ent_type==constants.MANAGED_NODE:
            node = DBSession.query(ManagedNode).filter_by(id=entity.id).first()
            in_sync = self.is_node_in_sync(node, state_owner)
        if ent_type==constants.SERVER_POOL:
            node_entities = auth.get_entities(to_unicode(constants.MANAGED_NODE), entity)
            for each_node in node_entities:
                in_sync = self.is_node_in_sync(each_node, state_owner)
                if in_sync:
                    break
        if ent_type==constants.DATA_CENTER:
            sp_entities = auth.get_entities(to_unicode(constants.SERVER_POOL), entity)
            for each_sp in sp_entities:
                if in_sync:
                    break
                sp_entity = auth.get_entity(each_sp.id)
                node_entities = auth.get_entities(to_unicode(constants.MANAGED_NODE), sp_entity)
                for each_node in node_entities:
                    in_sync = self.is_node_in_sync(each_node, state_owner)
                    if in_sync:
                        break
        return in_sync

    def is_syncing(self, entity, state_owner):
        syncing = False
        ent_type = entity.type.name
        if ent_type == constants.MANAGED_NODE:
            def_link = DBSession.query(ServerDefLink).filter_by(server_id=entity.id, def_type=state_owner, transient_state=constants.SYNCING)
        else:
            if ent_type == constants.SERVER_POOL:
                def_link = DBSession.query(SPDefLink).filter_by(group_id=entity.id, def_type=state_owner, transient_state=constants.SYNCING)
            else:
                if ent_type == constants.DATA_CENTER:
                    def_link = DBSession.query(DCDefLink).filter_by(site_id=entity.id, def_type=state_owner, transient_state=constants.SYNCING)
        if def_link:
            if def_link.count() > 0:
                syncing = True
        return syncing

    def set_transient_state(self, defn, transient_state, op, site_id=None, group_id=None, node_id=None):
        scope = defn.scope
        if op==constants.SCOPE_LEVEL:
            if scope == constants.SCOPE_S:
                def_link = DBSession.query(ServerDefLink).filter_by(server_id=node_id, def_id=defn.id).first()
            else:
                if scope == constants.SCOPE_SP:
                    def_link = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_id=defn.id).first()
                else:
                    if scope == constants.SCOPE_DC:
                        def_link = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_id=defn.id).first()
            if def_link:
                if transient_state:
                    def_link.transient_state = to_unicode(transient_state)
                else:
                    def_link.transient_state = None
                LOGGER.info('Transient state of ' + to_str(defn.name) + ' is changed to ' + to_str(transient_state) + ' at definition scope level')
        if op==constants.NODE_LEVEL:
            def_link = DBSession.query(ServerDefLink).filter_by(server_id=node_id, def_id=defn.id).first()
            if def_link:
                if transient_state:
                    def_link.transient_state = to_unicode(transient_state)
                else:
                    def_link.transient_state = None
                LOGGER.info('Transient state of ' + to_str(defn.name) + ' is changed to ' + to_str(transient_state) + ' at node level')

    def change_defn_transient_state(self, auth, node, transient_state, state_owner, state_transaction):
        allowed,info = state_transaction.is_allowed(node.id, transient_state, state_owner)
        if allowed == False:
            raise Exception(constants.NO_OP + '\n' + str(info['msg']))

    def add_defn(self, defn, site, group, node, auth, defType, op, action_op, def_manager, grid_manager, op_level, sp_ids=None, scan_result=None, csep_id=None):
        scope = op_level
        if scope == constants.SCOPE_S:
            entityId = node.id
        elif scope == constants.SCOPE_SP:
            entityId = group.id
        elif scope == constants.SCOPE_DC:
            entityId = site.id
        elif scope == constants.SCOPE_CP:
            entityId = csep_id
        ent = auth.get_entity(entityId)
        if not auth.has_privilege(action_op, ent):
            raise Exception(constants.NO_PRIVILEGE)
        if scope == constants.SCOPE_SP:
            if not PrivilegeOps.check_child_privileges(auth, action_op, ent):
                raise Exception(constants.NO_CHILD_PRIVILEGE % ('Servers', 'Server Pool'))
        DBSession.add(defn)
        nw_id = defn.id
        if site:
            def_manager.SaveScanResult(defn.id, grid_manager, scan_result, site.id)
        def_manager.RemoveScanResult(scan_result)
        errs = []
        details = {}
        status = to_unicode(constants.OUT_OF_SYNC)
        if scope == constants.SCOPE_DC:
            oos_count = 0
            status = to_unicode(constants.IN_SYNC)
            self.add_site_defn(site.id, defn.id, defType, status, oos_count)
            def_manager.manage_defn_to_groups(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager)
        elif scope == constants.SCOPE_SP:
            def_manager.manage_defn_to_groups(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager)
        elif scope == constants.SCOPE_S:
            self.add_node_defn(node.id, defn.id, defType, status, details)
            update_status = True
            #def_manager.add_private_ip_pool(defn)
            self.sync_node_defn(auth, node, group.id, site.id, defn, defType, op, def_manager, update_status, errs)
            
        elif scope == constants.SCOPE_CP:
            oos_count = 0
            status = to_unicode(constants.IN_SYNC)
            self.add_csep_defn(csep_id, defn.id, defType, status, oos_count)
            def_manager.manage_defn_to_groups(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager, csep_id)
            details['defn_id'] = defn.id
            if node:
                details['node_id'] = node.id
        def_manager.on_defn_creation(auth,**details)
        def_manager.Recompute(defn)
        if errs:
            if len(errs) > 0:
                LOGGER.error('Error:' + to_str(errs))
        return (errs, nw_id)

    def add_node_defn(self, node_id, def_id, def_type, status, details):
        row = DBSession.query(ServerDefLink).filter_by(server_id=node_id, def_id=def_id).first()
        if not row:
            node_defn = ServerDefLink()
            node_defn.server_id = to_unicode(node_id)
            node_defn.def_type = to_unicode(def_type)
            node_defn.def_id = def_id
            node_defn.status = to_unicode(status)
            node_defn.details = to_unicode(details)
            node_defn.dt_time = datetime.now()
            DBSession.add(node_defn)

    def add_group_defn(self, group_id, def_id, def_type, status, oos_count):
        row = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_id=def_id).first()
        if not row:
            SPDL = SPDefLink()
            SPDL.group_id = group_id
            SPDL.def_type = def_type
            SPDL.def_id = def_id
            SPDL.status = status
            SPDL.oos_count = oos_count
            SPDL.dt_time = datetime.now()
            DBSession.add(SPDL)
        
    def add_site_defn(self, site_id, def_id, def_type, status, oos_count):
        row = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_id=def_id).first()
        if not row:
            DCDL = DCDefLink()
            DCDL.site_id = site_id
            DCDL.def_type = def_type
            DCDL.def_id = def_id
            DCDL.status = to_unicode(status)
            DCDL.oos_count = oos_count
            DCDL.dt_time = datetime.now()
            DBSession.add(DCDL)

    def add_csep_defn(self, csep_id, def_id, def_type, status, oos_count):
        row = DBSession.query(CSEPDefLink).filter_by(csep_id=csep_id, def_id=def_id).first()
        if not row:
            CPDL = CSEPDefLink()
            CPDL.csep_id = csep_id
            CPDL.def_type = def_type
            CPDL.def_id = def_id
            CPDL.status = to_unicode(status)
            CPDL.oos_count = oos_count
            CPDL.dt_time = datetime.now()
            DBSession.add(CPDL)

    def sync_defn(self, defn, site, group, auth, defType, op, def_manager, update_status=True, errs=None, csep_id=None):
        server_list = []
        group_defn = DBSession.query(SPDefLink).filter_by(group_id=group.id, def_id=defn.id).first()
        if group_defn:
            group_ent = auth.get_entity(group.id)
            if group_ent is not None:
                node_ents = auth.get_entities(to_unicode(constants.MANAGED_NODE), parent=group_ent)
                for node_ent in node_ents:
                    node = DBSession.query(ManagedNode).filter_by(id=node_ent.entity_id).filter(ManagedNode.maintenance == False).first()
                    if node:
                        server_list.append(node)
                        try:
                            processor = None
                            sync_forcefully = False
                            site_id = None
                            if site:
                                site_id = site.id
                            self.sync_node_defn(auth, node, group.id, site_id, defn, defType, op, def_manager, update_status, errs, processor, sync_forcefully, csep_id)
                        except Exception as ex:
                            LOGGER.error(to_str(ex))

        return server_list

    def sync_node(self, defn_list, node, groupId, site_id, auth, defType, op, def_manager, update_status=True, errs=None):
        if not groupId:
            if node and auth:
                entity = auth.get_entity(node.id)
                if entity:
                    groupId = entity.parents[0].entity_id
        if defn_list:
            for defn in defn_list:
                if defn:
                    try:
                        self.sync_node_defn(auth, node, groupId, site_id, defn, defType, op, def_manager, update_status, errs)
                        def_manager.Recompute(defn)
                    except Exception as ex:
                        LOGGER.error('Error: ' + to_str(ex))
                    if errs:
                        if len(errs)>0:
                            LOGGER.error('Error in syncing definition while removing node: ' + to_str(errs))

    def remove_defn(self, defn, site, group, node, auth, defType, op, action_op, def_manager, grid_manager, add_mode=False, group_list=None, op_level=None, csep_id=None):
        warning_msg = None
        scope = op_level
        entityId = None
        server_list = []
        if scope == constants.SCOPE_S:
            entityId = node.id
        elif scope == constants.SCOPE_SP:
            entityId = group.id
        elif scope == constants.SCOPE_DC:
            entityId = site.id
        elif scope == constants.SCOPE_CP:
            entityId = csep_id
        ent = auth.get_entity(entityId)
        if not auth.has_privilege(action_op, ent):
            raise Exception(constants.NO_PRIVILEGE)
        if scope == constants.SCOPE_SP:
            if not PrivilegeOps.check_child_privileges(auth, action_op, ent):
                raise Exception(constants.NO_CHILD_PRIVILEGE % ('Servers', 'Server Pool'))
        if defn:
            returnVal = def_manager.is_storage_allocated(defn.id)
            if returnVal==True:
                allocated = False
                if op_level==constants.SCOPE_SP and defn.scope==constants.SCOPE_DC:
                    vm_disks = grid_manager.get_vm_disks_from_pool(auth, group.id)
                    storage_disks = grid_manager.get_storage_disks_from_storage(defn.id)
                    if storage_disks:
                        for each_storage_disk in storage_disks:
                            if allocated == True:
                                break
                            for each_vm_disk in vm_disks:
                                vm_storage_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=each_vm_disk.id, storage_disk_id=each_storage_disk.id).first()
                                if vm_storage_link:
                                    allocated = True
                                    warning_msg = 'All the links associated with the storage (' + to_str(defn.name) + ') would be removed'
                                    break
                else:
                    warning_msg = 'The storage (' + to_str(defn.name) + ') and all the links associated with it would be removed'
            if op_level == constants.SCOPE_SP and defn.scope == constants.SCOPE_DC:
                defn.is_deleted = False
            else:
                defn.is_deleted = True
            node_defn = DBSession.query(ServerDefLink).filter_by(def_id=defn.id).first()
            if node_defn:
                node = DBSession.query(ManagedNode).filter_by(id=node_defn.server_id).first()
            site_id = None
            group_id = None
            if node:
                if group:
                    group_id = group.id
                else:
                    entity = auth.get_entity(node.id)
                    if entity:
                        group_id = entity.parents[0].entity_id
                if group_id:
                    group = DBSession.query(ServerGroup).filter_by(id=group_id).first()
                if group:
                    if site:
                        site_id = site.id
                    else:
                        entity = auth.get_entity(group.id)
                        if entity:
                            site_id = entity.parents[0].entity_id
                    if site_id:
                        site = DBSession.query(Site).filter_by(id=site_id).first()

                if add_mode==False:
                    if defn.scope==constants.SCOPE_S:
                        self.sync_node_defn(auth, node, group_id, site_id, defn, defType, op, def_manager)
                        server_list.append(node)
                    elif op_level==constants.SCOPE_SP:
                        result = self.sync_defn(defn, site, group, auth, defType, op, def_manager)
                        if result:
                            server_list.extend(result)
                    elif op_level==constants.SCOPE_DC and defn.scope==constants.SCOPE_DC:
                        site_entity = auth.get_entity(site.id)
                        group_entities = auth.get_entities(to_unicode(constants.SERVER_POOL), site_entity)
                        for eachgroup in group_entities:
                            group = DBSession.query(ServerGroup).filter_by(id=eachgroup.entity_id).first()
                            result = self.sync_defn(defn, site, group, auth, defType, op, def_manager)
                            if result:
                                server_list.extend(result)
                    elif op_level==constants.SCOPE_CP and defn.scope==constants.SCOPE_CP:
                        dc_def_links = DBSession.query(SPDefLink).filter_by(def_id=defn.id)
                        for each_link in dc_def_links:
                            group = DBSession.query(ServerGroup).filter_by(id=each_link.group_id).first()
                            update_status = True
                            errs = None
                            result = self.sync_defn(defn, site, group, auth, defType, op, def_manager, update_status, errs, csep_id)
                            if result:
                                server_list.extend(result)
        if op_level == constants.SCOPE_SP and defn.scope == constants.SCOPE_DC:
            defn.is_deleted = False
            self.disassociate_defn(site, group, auth, defn, defType, add_mode, grid_manager)
        else:
            self.delete_defn(defn, auth, defType, def_manager, grid_manager)
        def_manager.Recompute(defn)
        return warning_msg
        

    def isVMRunningInPool(self, auth, group_id):
        returnVal = False
        ent = auth.get_entity(group_id)
        nodes = auth.get_entities(to_unicode(constants.MANAGED_NODE), parent=ent)
        for eachnode in nodes:
            returnVal = self.isVMRunningOnServer(auth, eachnode.entity_id)
            if returnVal == True:
                break
        return returnVal

    def isVMRunningOnServer(self, auth, node_id):
        returnVal = False
        ent = auth.get_entity(node_id)
        vmIds = auth.get_entity_ids(constants.DOMAIN, parent=ent)
        for eachvmid in vmIds:
            vm = DBSession.query(VM).filter_by(id=eachvmid).options(eagerload('current_state')).first()
            if vm:
                if vm.current_state.avail_state==VM.RUNNING:
                    returnVal = True
                    LOGGER.info('VM is running on server.')
                    break
        return returnVal

    def delete_defn(self, defn, auth, defType, def_manager, grid_manager):
        LOGGER.info('Deleting definition...')
        #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEP
        from stackone.model.SyncDefinition import SyncDef
        scope = defn.scope
        logical_delete = False
        if defn.is_deleted==True:
            vm_id = None
            ext_nw_svc_host = None
            csep_id = None

            if defType==constants.NETWORK:
                if defn.scope==constants.SCOPE_CP:
                    csep_defn = DBSession.query(CSEPDefLink).filter_by(def_id=defn.id).first()
                    if csep_defn:
                        csep_id = csep_defn.csep_id
                        csep = DBSession.query(CSEP).filter_by(id=csep_id).first()
                        if csep:
                            ext_nw_svc_host = csep.get_nw_service_host()
                else:
                    ext_nw_svc_host = get_cms_network_service_node()
                if ext_nw_svc_host:
                    if ext_nw_svc_host.is_up() and not ext_nw_svc_host.maintenance:
                        LOGGER.info('Syncing network service host - ' + to_str(ext_nw_svc_host.hostname))
                        group_id = None
                        site_id = None
                        defType = constants.NETWORK
                        op = constants.DETACH
                        update_status = True
                        errs = []
                        processor = None
                        sync_forcefully = None
                        use_auth = False
                        SyncDef().sync_node_defn(auth, ext_nw_svc_host, group_id, site_id, defn, defType, op, def_manager, update_status, errs, processor, sync_forcefully, csep_id, use_auth)
                        def_manager.remove_defn_dependencies(csep_id, defn.id, vm_id)
                    else:
                        LOGGER.info('Network Service Node (' + to_str(ext_nw_svc_host.hostname) + ') is down')
                        logical_delete = True
            if scope==constants.SCOPE_S:
                node_defn = DBSession.query(ServerDefLink).filter_by(def_id=defn.id, def_type=defType, status=constants.OUT_OF_SYNC).first()
                if node_defn:
                    node = grid_manager.getNode(auth, node_defn.server_id)
                    if node:
                        LOGGER.info('Definition ' + defn.name + ' is OUT_OF_SYNC on the server ' + node.hostname)
                else:
                    LOGGER.info('Allowing to delete definition...')
                    DBSession.query(ServerDefLink).filter_by(def_id=defn.id, def_type=defType).delete()
                    grid_manager.remove_vm_links_to_storage(defn.id)
                    def_manager.remove_storage_disk(defn.id)
                    DBSession.delete(defn)
            elif scope==constants.SCOPE_SP:
                rowGroupDef = DBSession.query(SPDefLink).filter_by(def_id=defn.id, def_type=defType).first()
                if rowGroupDef:
                    if rowGroupDef.oos_count>0:
                        LOGGER.info('Definition is OUT_OF_SYNC at server pool level')
                    else:
                        LOGGER.info('Allowing to delete definition...')
                        DBSession.query(SPDefLink).filter_by(def_id=defn.id, def_type=defType).delete()
                        DBSession.query(ServerDefLink).filter_by(def_id=defn.id, def_type=defType).delete()
                        grid_manager.remove_vm_links_to_storage(defn.id)
                        def_manager.remove_storage_disk(defn.id)
                        if logical_delete:
                            DBSession.delete(defn)
            elif scope==constants.SCOPE_DC:
                rowGroupDef = DBSession.query(DCDefLink).filter_by(def_id=defn.id, def_type=defType).first()
                if rowGroupDef:
                    if rowGroupDef.oos_count>0:
                        LOGGER.info('Definition is OUT_OF_SYNC at data center level')
                    else:
                        LOGGER.info('Allowing to delete definition...')
                        DBSession.query(DCDefLink).filter_by(def_id=defn.id, def_type=defType).delete()
                        DBSession.query(SPDefLink).filter_by(def_id=defn.id, def_type=defType).delete()
                        DBSession.query(ServerDefLink).filter_by(def_id=defn.id, def_type=defType).delete()
                        grid_manager.remove_vm_links_to_storage(defn.id)
                        def_manager.remove_storage_disk(defn.id)
                        DBSession.query(Storage_Stats).filter_by(storage_id=defn.id).delete()
                        group_defn = DBSession.query(DCDefLink).filter_by(def_id=defn.id, def_type=defType).first()
                        if not group_defn:
                            node_defn = DBSession.query(ServerDefLink).filter_by(def_id=defn.id, def_type=defType).first()
                            if not logical_delete and not node_defn:
                                DBSession.delete(defn)
                        transaction.commit()
            if scope==constants.SCOPE_CP:
                rowGroupDef = DBSession.query(CSEPDefLink).filter_by(def_id=defn.id, def_type=defType).first()
                if rowGroupDef:
                    if rowGroupDef.oos_count>0:
                        LOGGER.info('Definition is OUT_OF_SYNC at csep level')
                    else:
                        LOGGER.info('Allowing to delete definition...')
                        if not logical_delete:
                            DBSession.query(CSEPDefLink).filter_by(def_id=defn.id, def_type=defType).delete()
                        DBSession.query(SPDefLink).filter_by(def_id=defn.id, def_type=defType).delete()
                        DBSession.query(ServerDefLink).filter_by(def_id=defn.id, def_type=defType).delete()
                        grid_manager.remove_vm_links_to_storage(defn.id)
                        def_manager.remove_storage_disk(defn.id)
                        DBSession.query(Storage_Stats).filter_by(storage_id=defn.id).delete()
                        csep_defn = DBSession.query(CSEPDefLink).filter_by(def_id=defn.id, def_type=defType).first()
                        if not csep_defn:
                            node_defn = DBSession.query(ServerDefLink).filter_by(def_id=defn.id, def_type=defType).first()
                            if not logical_delete and not node_defn:
                                DBSession.delete(defn)
                    transaction.commit()


    def disassociate_defn(self, site, group, auth, defn, defType, add_mode, grid_manager):
        LOGGER.info('Disassociating definition...')
        allows_delete = False
        if add_mode==False:
            dc_defn = DBSession.query(DCDefLink).filter_by(site_id=site.id, def_id=defn.id, def_type=defType).first()
            if dc_defn:
                if dc_defn.oos_count == 0:
                    allows_delete = True

                if dc_defn.oos_count>0:
                    LOGGER.info('Definition is OUT_OF_SYNC at data center level')
        else:
            if add_mode == True:
                allows_delete = True
        if allows_delete==True:
            LOGGER.info('Allowing to delete definition...')
            for node in group.getNodeList(auth).itervalues():
                if node:
                    node_defn = DBSession.query(ServerDefLink).filter_by(server_id=node.id, def_id=defn.id, def_type=defType).first()
                    if node_defn:
                        DBSession.delete(node_defn)
            group_defn = DBSession.query(SPDefLink).filter_by(group_id=group.id, def_id=defn.id, def_type=defType).first()
            if group_defn:
                DBSession.delete(group_defn)
            vm_id_list = []
            for node in group.getNodeList(auth).itervalues():
                if node:
                    for vm in grid_manager.get_node_doms(auth, node.id):
                        if vm:
                            vm_id_list.append(vm.id)
            grid_manager.remove_vm_links_to_storage(defn.id, vm_id_list)
            transaction.commit()


    def props_to_cmd_param(self, props):
        cp = ''
        if props:
            for p,v in props.iteritems():
                if v:
                    if cp:
                        cp += '|'
                    cp += '%s=%s' % (p, v)
            cp = "'%s'" % (cp)
        return cp

    def sync_node_defn(self, auth, node, group_id, site_id, defn, defType, op, def_manager=None, update_status=True, errs=None, processor=None, sync_forcefully=False, csep_id=None, use_auth=True):
        LOGGER.info('update_status= ' + to_str(update_status))
        scope = defn.scope
        dt_time = datetime.now()
        if op in [constants.ATTACH,constants.DETACH]:
            (st_op, nw_op, operation) = (None, None, None)
            if op == constants.ATTACH:
                st_op = 'ADD_STORAGE_DEF'
                nw_op = 'ADD_NETWORK_DEF'
            elif op == constants.DETACH:
                st_op = 'REMOVE_STORAGE_DEF'
                nw_op = 'REMOVE_NETWORK_DEF'

            from stackone.model.storage import StorageManager
            from stackone.model.network import NwManager
            if isinstance(def_manager, StorageManager):
                operation = st_op
            elif isinstance(def_manager, NwManager):
                operation = nw_op
            ent = DBSession.query(Entity).filter(Entity.entity_id == node.id).first()

            if use_auth:
                if not auth.has_privilege(operation, ent):
                    raise Exception(constants.NO_PRIVILEGE)
        if not errs:
            errs = []
        errs = def_manager.CheckOp(op, errs)
        try:
            self.set_transient_state(defn, constants.SYNCING, constants.NODE_LEVEL, site_id, group_id, node.id)
            node = DBSession.query(ManagedNode).filter_by(id=node.id).first()
            if not node.is_up():
                LOGGER.error('Node is down')
                return {'output':'Node is down','exit_code':1}
            if node.maintenance:
                LOGGER.error('Node is in maintenance')
                return {'output':'Node is in maintenance','exit_code':1}

            exit_code, output= def_manager.exec_script(node, group_id, defn, defType, op)
        except Exception as ex:
            exit_code = 222
            output = to_str(ex)
            if not output:
                output = 'Error occurred in Sync operation'
        if exit_code == 1 and output == constants.STORAGE_ALREADY_MOUNTED:
            exit_code = 0
        self.set_transient_state(defn, None, constants.NODE_LEVEL, site_id, group_id, node.id)
        if exit_code:
            status = to_unicode(constants.OUT_OF_SYNC)
        else:
            status = to_unicode(constants.IN_SYNC)
        LOGGER.info('exit_code= ' + to_str(exit_code))
        LOGGER.info('Status= ' + to_str(status))
        LOGGER.info('output=' + to_str(output))
        if not exit_code:
            if not output:
                output = def_manager.getSyncMessage(op)
        details = output
        if not csep_id:
            csep_def_link = DBSession.query(CSEPDefLink).filter_by(def_id=defn.id).first()
            if csep_def_link:
                csep_id = csep_def_link.csep_id
        if update_status == True:
            self.update_node_defn(auth, node.id, group_id, site_id, defn.id, defn.type, status, dt_time, details, scope, defType, csep_id)
        def_manager.nw_svc_specific_sync(auth, node, defn, csep_id, op)
        if op==constants.GET_DISKS:
            result = {}
            result['type'] = defn.type
            result['id'] = defn.id
            result['op'] = op
            result['name'] = defn.name
            if processor:
                if exit_code:
                    errs.append('Error: %s, %s, %s' % (defn.name, node.hostname, output))
                    raise Exception(output)
                processor(op, output, result)
                LOGGER.info('Result of Processor= ' + to_str(result))
                return result
            errs.append('Can not process output. %s' % op)
            raise Exception('Can not process output. %s' % op)
        if exit_code:
            errs.append('Error: %s, %s, %s' % (defn.name, node.hostname, output))
            raise Exception(output)
        else:
            return {'output':output,'exit_code':exit_code}

    def update_node_defn(self, auth, node_id, group_id, site_id, def_id, def_type, status, dt_time, details, scope, defType, csep_id=None):
        LOGGER.info('Updating server definition status...')
        node_defn = DBSession.query(ServerDefLink).filter_by(server_id=node_id, def_id=def_id).first()
        if node_defn:
            if status:
                node_defn.status = status
            node_defn.dt_time = datetime.now()
            if details:
                node_defn.details = details
            transaction.commit()
            LOGGER.info('Server definition status is updated. Status is ' + to_str(status))
        LOGGER.info('Updating server pool definition status...')
        oos_count_g = 0
        g_status = to_unicode(constants.IN_SYNC)
        if group_id:
            group_entity = auth.get_entity(group_id)
            if group_entity is not None:
                group = DBSession.query(ServerGroup).filter_by(id=group_id).first()
                if group:
                    group.credential = None
                    for node in group.getNodeList(auth).itervalues():
                        rowNodeDefn = DBSession.query(ServerDefLink).filter_by(server_id=node.id, def_id=def_id, def_type=to_unicode(defType), status=to_unicode(constants.OUT_OF_SYNC))
                        if rowNodeDefn:
                            oos_count_g += rowNodeDefn.count()
        if oos_count_g > 0:
            g_status = to_unicode(constants.OUT_OF_SYNC)
        else:
            g_status = to_unicode(constants.IN_SYNC)
        group_sd = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_id=def_id, def_type=to_unicode(defType)).first()
        if group_sd:
            group_sd.status = g_status
            group_sd.dt_time = datetime.now()
            group_sd.oos_count = oos_count_g
            transaction.commit()
            LOGGER.info('Server pool level definition status is updated')

        LOGGER.info('Updating data center definition status...')
        oos_count_dc = 0
        dc_status = to_unicode(constants.IN_SYNC)
        rowNodeDefn = DBSession.query(ServerDefLink).filter_by(def_id=def_id, def_type=to_unicode(defType), status=to_unicode(constants.OUT_OF_SYNC))
        if rowNodeDefn:
            oos_count_dc = rowNodeDefn.count()
        if oos_count_dc > 0:
            dc_status = to_unicode(constants.OUT_OF_SYNC)
        else:
            dc_status = to_unicode(constants.IN_SYNC)
        dc_sd = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_id=def_id, def_type=to_unicode(defType)).first()
        if dc_sd:
            dc_sd.status = dc_status
            dc_sd.dt_time = datetime.now()
            dc_sd.oos_count = oos_count_dc
            DBSession.flush()
            transaction.commit()
            LOGGER.info('Data center level definition status is updated')

        if csep_id:
            csep_sd = DBSession.query(CSEPDefLink).filter_by(csep_id=csep_id, def_id=def_id, def_type=to_unicode(defType)).first()
            if csep_sd:
                csep_sd.status = dc_status
                csep_sd.dt_time = datetime.now()
                csep_sd.oos_count = oos_count_dc
                DBSession.flush()
                transaction.commit()
                LOGGER.info('CSEP level definition status is updated')

    def update_defn(self, defn, new_name, new_desc, site, group, auth, defType, op, def_manager, action_op, op_level=None, sp_ids=None, grid_manager=None, csep_id=None):
        if group and auth:
            ent = auth.get_entity(group.id)
            if not auth.has_privilege(action_op, ent):
                raise Exception(constants.NO_PRIVILEGE)
        defn.name = new_name
        defn.description = new_desc
        errs = []
        if op_level == constants.SCOPE_DC:
            def_manager.manage_defn_to_groups(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager)
        else:
            if op_level == constants.SCOPE_CP:
                def_manager.manage_defn_to_groups(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager, csep_id)
        def_manager.Recompute(defn)

    def validate_transfer_node(self, nodeId, sourceGroupId, auth):
        vm_running = False
        def_present = False
        node_defn = DBSession.query(ServerDefLink).filter_by(server_id=nodeId).first()
        if node_defn:
            def_present = True
            LOGGER.info('Storage/ Network are present on server.')
        vm_running = self.isVMRunningOnServer(auth, nodeId)
        if def_present == True and vm_running == True:
            raise Exception('VM_RUNNING')


    def SyncAll(self, site_id, group, defn_list, op, auth, def_manager, transient_state, state_owner, state_transaction):
        error_desc = ''
        for eachdefn in defn_list:
            self.set_transient_state(eachdefn, constants.SYNCING, constants.SCOPE_LEVEL, site_id, group.id, None)
            grp_ent = DBSession.query(Entity).filter(Entity.entity_id == group.id).first()
            for node in PrivilegeOps.get_servers(grp_ent):
                try:
                    self.change_defn_transient_state(auth, node, transient_state, state_owner, state_transaction)
                    node_defn = DBSession.query(ServerDefLink).filter_by(def_id=eachdefn.id, server_id=node.id).first()
                    if node_defn:
                        defType = node_defn.def_type
                        self.sync_node_defn(auth, node, group.id, site_id, eachdefn, defType, op, def_manager)
                except Exception as ex:
                    error_desc += to_str(ex) + '\n'
                    LOGGER.error('SP Sync operation is failed for server (' + node.hostname + ') and definition (' + eachdefn.name + '). Error description: ' + to_str(ex))
                    state_transaction.set_none_state(node.id, state_owner)
                state_transaction.set_none_state(node.id, state_owner)
            self.set_transient_state(eachdefn, None, constants.SCOPE_LEVEL, site_id, group.id, None)
        if error_desc:
            raise Exception(error_desc)

    def SyncServer(self, site_id, group_id, defn_list, node, op, auth, def_manager, transient_state, state_owner, state_transaction, sync_forcefully):
        for eachdefn in defn_list:
            try:
                self.change_defn_transient_state(auth, node, transient_state, state_owner, state_transaction)
                node_defn = DBSession.query(ServerDefLink).filter_by(def_id=eachdefn.id).first()
                if node_defn:
                    defType = node_defn.def_type
                csep_id = None
                csep_node_defn = DBSession.query(CSEPDefLink).filter_by(def_id=eachdefn.id).first()
                if csep_node_defn:
                    csep_id = csep_node_defn.csep_id
                self.sync_node_defn(auth, node, group_id, site_id, eachdefn, defType, op, def_manager, True, None, None, sync_forcefully, csep_id)
                def_manager.Recompute(eachdefn)
            except Exception as ex:
                LOGGER.error('Server Sync operation is failed for server (' + node.hostname + ') and definition (' + eachdefn.name + '). Error description: ' + to_str(ex))
                traceback.print_exc()
                state_transaction.set_none_state(node.id, state_owner)
                raise Exception(to_str(ex))
            state_transaction.set_none_state(node.id, state_owner)

    def get_node_defns(self, def_id, defType):
        defns = []
        node_defns = DBSession.query(ServerDefLink).filter_by(def_id=def_id, def_type=to_unicode(defType))
        if node_defns:
            for eachdefn in node_defns:
                defns.append(eachdefn)
        return defns

    def get_server_defns(self, server_id, defType):
        defns = []
        defns = DBSession.query(ServerDefLink).filter_by(server_id=server_id, def_type=defType)
        return defns

    def on_add_node(self, nodeId, groupId, site_id, auth, def_manager):
        op = constants.ATTACH
        if not(nodeId or groupId):
            return None
        defn_list = []
        errs = []
        sync_manager = SyncDef()
        defType = def_manager.getType()
        sp_defns = DBSession.query(SPDefLink).filter_by(group_id=to_unicode(groupId))
        if sp_defns:
            for eachdefn in sp_defns:
                defn = def_manager.get_defn(eachdefn.def_id)
                if defn:
                    defn_list.append(defn)
                    status = to_unicode(constants.OUT_OF_SYNC)
                    details = None
                    sync_manager.add_node_defn(nodeId, defn.id, defType, status, details)
        node = DBSession.query(ManagedNode).filter_by(id=nodeId).first()
        if node:
            update_status = True
            try:
                sync_manager.sync_node(defn_list, node, groupId, site_id, auth, defType, op, def_manager, update_status, errs)
            except Exception as ex:
                if errs:
                    if len(errs)>0:
                        LOGGER.error('Error in syncing definition while adding node: ' + to_str(errs))

    def on_remove_node(self, nodeId, groupId, site_id, auth, def_manager, isTransfer=False, csep_id=None):
        op = constants.DETACH
        if not groupId:
            return None
        errs = []
        sync_manager = SyncDef()
        defType = def_manager.getType()
        node = DBSession.query(ManagedNode).filter_by(id=nodeId).first()
        if node:
            defn_list = []
            node_defns = DBSession.query(ServerDefLink).filter_by(server_id=nodeId, def_type=defType)
            if node_defns:
                for eachdefn in node_defns:
                    defn = def_manager.get_defn(eachdefn.def_id)
                    if defn:
                        defn_list.append(defn)
                        continue
            try:
                update_status = True
                sync_manager.sync_node(defn_list, node, groupId, site_id, auth, defType, op, def_manager, update_status, errs)
            except Exception as ex:
                LOGGER.error('Error: ' + to_str(ex))
                if errs:
                    if len(errs)>0:
                        LOGGER.error('Error in syncing definition while removing node: ' + to_str(errs))
            if node_defns:
                for eachdefn in node_defns:
                    defn = def_manager.get_defn(eachdefn.def_id)
                    if defn:
                        if defn.scope!=constants.SCOPE_S:
                            if eachdefn.status == constants.OUT_OF_SYNC:
                                LOGGER.error('WARNING: The definition status is OUT_OF_SYNC. Still the definition linking with the server is getting deleted. server_id=' + node.id + ', def_id=' + eachdefn.def_id + ', def_type=' + eachdefn.def_type + ', details=' + to_str(eachdefn.details))
                            DBSession.delete(eachdefn)
                        if defn.scope == constants.SCOPE_S and isTransfer == False:
                            DBSession.delete(defn)
                        self.update_node_defn(auth, nodeId, groupId, site_id, defn.id, defn.type, '', datetime.now(), '', defn.scope, defType, csep_id)

    def on_add_group(self, groupId):
        return None

    def on_remove_group(self, site_id, groupId, auth, def_manager):
        op = constants.DETACH
        sync_manager = SyncDef()
        defType = def_manager.getType()
        site = DBSession.query(Site).filter_by(id=site_id).first()
        group = DBSession.query(ServerGroup).filter_by(id=groupId).first()
        defn_list = []
        sp_defns = DBSession.query(SPDefLink).filter_by(group_id=groupId)

        if sp_defns:
            for eachdefn in sp_defns:
                defn = def_manager.get_defn(eachdefn.def_id)
                if defn:
                    defn_list.append(defn)
        for each_defn in defn_list:
            group_defn = DBSession.query(SPDefLink).filter_by(def_id=each_defn.id, def_type=defType).first()
            if group_defn:
                DBSession.delete(group_defn)
            if each_defn.scope == constants.SCOPE_SP:
                DBSession.delete(each_defn)
    def on_transfer_node(self, nodeId, sourceGroupId, destGroupId, site_id, auth, def_manager):
        self.on_remove_node(nodeId, sourceGroupId, site_id, auth, def_manager, True)
        self.on_add_node(nodeId, destGroupId, site_id, auth, def_manager)



