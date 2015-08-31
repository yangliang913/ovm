from tg import session
import transaction
from stackone.model.Groups import ServerGroup
from stackone.model.ManagedNode import ManagedNode
from stackone.core.utils import constants
from stackone.core.utils.phelper import AuthenticationException
import Basic
from stackone.model.storage import StorageDef, StorageManager
from stackone.model import DBSession
from stackone.model.VM import VM, VMDisks, VMStorageLinks
from stackone.model.SPRelations import ServerDefLink, SPDefLink,DCDefLink, StorageDisks, Storage_Stats
from stackone.model.storage import StorageDef
from stackone.model.SyncDefinition import SyncDef
from stackone.model.Sites import Site
import stackone.core.utils.utils
from stackone.core.utils.utils import to_unicode,to_str,print_traceback
from stackone.core.utils.constants import *
constants = stackone.core.utils.constants

import logging,traceback
LOGGER = logging.getLogger("stackone.viewModel")
class StorageService():
    def __init__(self):
        self.storage_manager = Basic.getStorageManager()
        self.manager = Basic.getGridManager()
        self.sync_manager = SyncDef()

    def get_storage_types(self):
        try:
            storage_type_list = []
            storage_dic={'Network File Storage (NFS)':constants.NFS,'Internet SCSI (iSCSI)':constants.iSCSI,'ATA Over Ethernet (AOE)':constants.AOE,'Clustered LVM (CLVM)':constants.LVM,'Common Internet File System (CIFS)':constants.CIFS,'Global File System (GFS2)':constants.GFS,'Oracle Cluster File System (OCFS2)':constants.OCFS,'Fibre Channel (FC)':constants.FC}
            for storage_values in storage_dic.keys():
                storage_dic_temp={}
                storage_dic_temp['name']=storage_values
                storage_dic_temp['value']=storage_dic[storage_values]
                storage_type_list.append(storage_dic_temp)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")
        return dict(success='true', rows=storage_type_list)


    def get_vm_id_list(self, auth, node_entities, vm_id_list):
        for eachnode in node_entities:
            vms = auth.get_entities(constants.DOMAIN, parent=eachnode)
            for eachvm in vms:
                vm_id_list.append(eachvm.entity_id)
        return vm_id_list


    def get_vm_local_usage(self, vm_name):
        local_usage = 0.0
        if vm_name:
            vm = DBSession.query(VM).filter_by(name=vm_name).first()
            if vm:
                vm_id = vm.id
                vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
                if vm_disks:
                    for each_vm_disk in vm_disks:
                        vm_storage_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=each_vm_disk.id).first()
                        if not vm_storage_link:
                            local_usage += each_vm_disk.disk_size
        return local_usage


    def get_storage_usage(self, auth, site_id, group_id, scope, defn):
        usage = 0
        vm_id_list = []
        if scope==constants.SCOPE_DC:
            site_entity = auth.get_entity(site_id)
            groups = auth.get_entities(constants.SERVER_POOL, parent=site_entity)
            for eachgroup in groups:
                nodes = auth.get_entities(constants.MANAGED_NODE, parent=eachgroup)
                vm_id_list = self.get_vm_id_list(auth, nodes, vm_id_list)
        if scope == constants.SCOPE_SP:
            group_entity = auth.get_entity(group_id)
            nodes = auth.get_entities(constants.MANAGED_NODE, parent=group_entity)
            vm_id_list = self.get_vm_id_list(auth, nodes, vm_id_list)

        storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=defn.id)
        if storage_disks:
            for each_disk in storage_disks:
                vm_storage_link = DBSession.query(VMStorageLinks).filter_by(storage_disk_id=each_disk.id).first()
                if vm_storage_link:
                    vm_id = None
                    vm_disk = DBSession.query(VMDisks).filter_by(id=vm_storage_link.vm_disk_id).first()
                    if vm_disk:
                        vm_id = vm_disk.vm_id
                    for each_vm_id in vm_id_list:
                        if each_vm_id == vm_id:
                            usage += vm_disk.disk_size
        return usage

#pass
    def get_storage_def_list(self, auth, site_id, group_id, scope=None, op=None):
        storage_list = []
        try:
            if site_id == 'data_center':
                site = self.manager.getSiteByGroupId(group_id)
                if site:
                    site_id = site.id
            sds = self.storage_manager.get_sd_ids(site_id, group_id, to_unicode(constants.STORAGE), scope)
            if sds:
                for item in sds:
                    temp_sd_dic = {}
                    s_def = self.storage_manager.get_sd(item.def_id, site_id, group_id, to_unicode(constants.STORAGE))
                    associated = False
                    if s_def:
                        node_defn = DBSession.query(ServerDefLink).filter_by(def_id=s_def.id).first()
                        if node_defn:
                            associated = True
                        usage = ''
                        if scope == constants.SCOPE_DC:
                            ss = DBSession.query(Storage_Stats).filter_by(entity_id=site_id, storage_id=s_def.id).first()
                            if ss:
                                usage = ss.allocation_in_DC
                        elif scope == constants.SCOPE_SP:
                            ss = DBSession.query(Storage_Stats).filter_by(entity_id=group_id, storage_id=s_def.id).first()
                            if ss:
                                usage = ss.allocation_in_SP
                        str_group_list = None
                        group_defns = DBSession.query(SPDefLink).filter_by(def_id=s_def.id)
                        if group_defns:
                            for eachdefn in group_defns:
                                group = DBSession.query(ServerGroup).filter_by(id=eachdefn.group_id).first()
                                if group:
                                    if str_group_list:
                                        str_group_list = str_group_list + ', ' + group.name
                                    else:
                                        str_group_list = group.name
                        total = 0.0
                        ss = s_def.get_stats()
                        if ss:
                            total = ss.total_size
                        
                        definition = self.get_defn(s_def)
                        temp_sd_dic['stats'] = ''
                        temp_sd_dic['name'] = s_def.name
                        temp_sd_dic['connection_props'] = s_def.connection_props
                        temp_sd_dic['type'] = s_def.type
                        temp_sd_dic['id'] = s_def.id
                        temp_sd_dic['creds'] = s_def.creds
                        temp_sd_dic['creds_required'] = s_def.creds_required
                        temp_sd_dic['size'] = total
                        temp_sd_dic['definition'] = definition
                        temp_sd_dic['description'] = s_def.description
                        if op:
                            if op == 'SP' or op == 'DC':
                                temp_sd_dic['status'] = item.status
                            else:
                                temp_sd_dic['status'] = ''
                        else:
                            temp_sd_dic['status'] = s_def.status
                        temp_sd_dic['scope'] = s_def.scope
                        temp_sd_dic['associated'] = associated
                        temp_sd_dic['serverpools'] = str_group_list
                        if not usage:
                            usage = 0
                        temp_sd_dic['usage'] = usage
                        storage_list.append(temp_sd_dic)
                    else:
                        LOGGER.info('Storage definition not found.')
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return dict(success=False, msg=to_str(ex).replace("'", ''), rows=storage_list)
        return dict(success=True, rows=storage_list)



    def get_dc_storage_def_list(self, auth, site_id, group_id):
        storage_list = []
        try:
            if site_id == 'data_center':
                site = self.manager.getSiteByGroupId(group_id)
                if site:
                    site_id = site.id
            defn_list = self.storage_manager.getSiteDefListToAssociate(site_id, group_id, to_unicode(constants.STORAGE))
            if defn_list:
                for s_def in defn_list:
                    temp_sd_dic = {}
                    if s_def:
                        total = 0.0
                        if s_def.get_stats():
                            objStats = s_def.get_stats()
                            if objStats:
                                total = objStats.total_size
                        definition = self.get_defn(s_def)
                        temp_sd_dic['stats'] = ''
                        temp_sd_dic['name'] = s_def.name
                        temp_sd_dic['connection_props'] = s_def.connection_props
                        temp_sd_dic['type'] = s_def.type
                        temp_sd_dic['id'] = s_def.id
                        temp_sd_dic['creds'] = s_def.creds
                        temp_sd_dic['creds_required'] = s_def.creds_required
                        temp_sd_dic['size'] = total
                        temp_sd_dic['definition'] = definition
                        temp_sd_dic['description'] = s_def.description
                        temp_sd_dic['status'] = s_def.status
                        temp_sd_dic['scope'] = s_def.scope
                        storage_list.append(temp_sd_dic)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return dict(success=False, msg=to_str(ex).replace("'", ''), rows=storage_list)
        return dict(success=True, rows=storage_list)


    def get_server_storage_def_list(self, auth, node_id, op):
        storage_list = []
        try:
            defn_list = self.sync_manager.get_server_defns(node_id, to_unicode(constants.STORAGE))
            if defn_list:
                for item in defn_list:
                    temp_sd_dic = {}
                    s_def = self.storage_manager.get_defn(item.def_id)
                    if s_def:
                        total = 0.0
                        if s_def.get_stats():
                            objStats = s_def.get_stats()
                            if objStats:
                                total = objStats.total_size
                        definition = self.get_defn(s_def)
                        temp_sd_dic['stats'] = ''
                        temp_sd_dic['name'] = s_def.name
                        temp_sd_dic['connection_props'] = s_def.connection_props
                        temp_sd_dic['type'] = s_def.type
                        temp_sd_dic['id'] = s_def.id
                        temp_sd_dic['creds'] = s_def.creds
                        temp_sd_dic['creds_required'] = s_def.creds_required
                        temp_sd_dic['size'] = total
                        temp_sd_dic['definition'] = definition
                        temp_sd_dic['description'] = s_def.description
                        if op:
                            if op == 'S':
                                temp_sd_dic['status'] = item.status
                            else:
                                temp_sd_dic['status'] = ''
                        else:
                            temp_sd_dic['status'] = ''
                        temp_sd_dic['scope'] = s_def.scope
                        storage_list.append(temp_sd_dic)
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
        return storage_list

###############$$$$$$$$$$$
    def add_storage_def_cli(self, auth, site_id, group_id, node_id, type, opts, op_level=None, sp_ids=None, added_manually=False):
        storagename = opts['name']
        storage = DBSession.query(StorageDef).filter(StorageDef.name == storagename).first()
        if storage:
            return {'success':False,'msg':'The storage with storagename '+ storagename+' already exists.'}
        result = self.add_storage_def(auth, site_id, group_id, node_id, type, opts, op_level, sp_ids, added_manually)
        if result == "{success: true,msg: 'Storage Added.'}":
            return {'success':True,'msg':'The storage with storagename '+storagename+' added successfully.'}
        return {'success':False,'msg':result}

        
    def add_storage_def(self, auth, site_id, group_id, node_id, type, opts, op_level=None, sp_ids=None, added_manually=False, scan_result=None):
        new_sd = self.get_valid_sd(type, opts, op_level, added_manually)
        site = self.manager.getSite(site_id)
        group = self.manager.getGroup(auth, group_id)
        node = None
        group_list = self.manager.getGroupList(auth, site_id)
        try:
            sdlist = self.storage_manager.get_sds(site_id, group_id)
            for sd in sdlist:
                if new_sd.name == sd.name:
                    raise Exception('Storage share with same name already exists.')
            errs = []
            errs = self.update_storage_def(auth, new_sd, None, None, None, site, group, op_level, True, sp_ids, errs, scan_result)
            if errs:
                if len(errs) > 0:
                    add_mode = True
                    self.sync_manager.remove_defn(new_sd, site, group, node, auth, to_unicode(constants.STORAGE), constants.DETACH, 'REMOVE_STORAGE_DEF', self.storage_manager, self.manager, add_mode, group_list, op_level)
                    return {'success':False,'msg':to_str(errs).replace("'",'')}
        except Exception as ex:
            print_traceback()
            err_desc = to_str(ex).replace("'", '')
            err_desc = err_desc.strip()
            LOGGER.error(err_desc)
            try:
                add_mode = True
                defn_temp = self.storage_manager.get_sd(new_sd.id, None, None, None)
                if defn_temp:
                    self.sync_manager.remove_defn(defn_temp, site, group, node, auth, to_unicode(constants.STORAGE), constants.DETACH, 'REMOVE_STORAGE_DEF', self.storage_manager, self.manager, add_mode, group_list, op_level)
            except Exception as ex1:
                print_traceback()
                LOGGER.error(to_str(ex1).replace("'", ''))
                raise Exception(to_str(ex1))
            if err_desc:
                raise Exception(err_desc)
            return "{success: false,msg: '" + err_desc + "'}"
        return "{success: true,msg: 'Storage Added.'}"


    def edit_storage_def(self, auth, storage_id, site_id, groupId, type, op_level, sp_ids, opts):
        try:
            site = self.manager.getSite(site_id)
            group = self.manager.getGroup(auth, groupId)
            new_name = opts.get('name')
            new_desc = opts.get('description')
            self.update_storage_def(auth, None, new_name, new_desc, storage_id, site, group, op_level, False, sp_ids)
            self.SaveScanResult(storage_id, site_id)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", '').strip(), "'}")
        return "{success: true,msg: 'Storage Updated.'}"


    def get_valid_sd(self, type, options, scope, added_manually=False):
        creds_req = False
        creds = {}
        conn_options = {}
        if type == constants.iSCSI:
            creds_req = True
            creds['username'] = options.get('username')
            creds['password'] = options.get('password')
            conn_options['server'] = options.get('portal')
            conn_options['target'] = options.get('target')
            conn_options['options'] = options.get('options')
            conn_options['username'] = options.get('username')
            conn_options['password'] = options.get('password')
        if type == constants.NFS:
            conn_options['server'] = options.get('server')
            conn_options['share'] = options.get('share')
            conn_options['mount_point'] = options.get('mount_point')
            conn_options['mount_options'] = options.get('mount_options')
        if type == constants.AOE:
            conn_options['interface'] = options.get('interface')
        if type == constants.LVM:
            conn_options['volume_group'] = options.get('volume_group')
        if type == constants.CIFS:
            conn_options['server'] = options.get('server')
            conn_options['windows_share'] = options.get('windows_share')
            conn_options['mount_point'] = options.get('mount_point')
            conn_options['windows_username'] = options.get('windows_username')
            conn_options['windows_password'] = options.get('windows_password')
            conn_options['domain'] = options.get('domain')
        if type == constants.GFS:
            conn_options['device'] = options.get('device')
            conn_options['mount_point'] = options.get('mount_point')
        if type == constants.OCFS:
            conn_options['device'] = options.get('device')
            conn_options['mount_point'] = options.get('mount_point')
        if type == constants.FC:
            conn_options['host_adapter'] = options.get('host_adapter')
            conn_options['bus_channel'] = options.get('bus_channel')
            conn_options['target'] = options.get('target')
            conn_options['lun'] = options.get('lun')
        conn_options['added_manually'] = added_manually
        new_sd = StorageDef(None, to_unicode(options.get('name')), type, to_unicode(options.get('description')), conn_options, scope, creds_req)
        if creds_req == True:
            new_sd.set_creds(creds)
        if options['total_cap']!='null':
            options['total_cap'] = str(options.get('total_cap')).strip()
            if options['total_cap']:
                total_cap = str(options.get('total_cap'))
                if not total_cap:
                    total_cap=0
        return new_sd


    def associate_defns(self, site_id, group_id, def_type, def_ids, auth, op_level=None):
        error_desc = ''
        site = self.manager.getSite(site_id)
        group = self.manager.getGroup(auth, group_id)
        group_list = self.manager.getGroupList(auth, site_id)
        def_id_list = def_ids.split(',')
        for def_id in def_id_list:
            new_sd = DBSession.query(StorageDef).filter_by(id=def_id).first()
            node = None
            sp_ids = group_id
            try:
                self.sync_manager.add_defn(new_sd, site, group, node, auth, to_unicode(constants.STORAGE), constants.ATTACH, 'ADD_STORAGE_DEF', self.storage_manager, self.manager, op_level, sp_ids)
            except Exception as ex:
                error_desc = to_str(ex)
                print_traceback()
                LOGGER.error(to_str(ex).replace("'", ''))
                add_mode = True
                try:
                    self.sync_manager.remove_defn(new_sd, site, group, node, auth, to_unicode(constants.STORAGE), constants.DETACH, 'REMOVE_STORAGE_DEF', self.storage_manager, self.manager, add_mode, group_list, op_level)
                except Exception as ex1:
                    print_traceback()
                    LOGGER.error(to_str(ex1).replace("'", ''))
                    raise Exception(to_str(ex1))
                if error_desc:
                    raise Exception(error_desc)
        return {'success':True,'msg':'Storage Added'}


    def update_storage_def(self, auth, new_sd, new_name, new_desc, storage_id, site, group, op_level, new=True, sp_ids=None, errs=None, scan_result=None):
        if new==True:
            if group:
                group_defns = DBSession.query(SPDefLink).filter_by(group_id=group.id)
            elif site:
                group_defns = DBSession.query(DCDefLink).filter_by(site_id=site.id)
            for group_defn in group_defns:
                rowSDef = DBSession.query(StorageDef).filter_by(id=group_defn.def_id, name=new_name).first()
                if rowSDef:
                    raise Exception('Storage definition with the same name already exists')
            node = None
            self.sync_manager.add_defn(new_sd, site, group, node, auth, to_unicode(constants.STORAGE), constants.ATTACH, 'ADD_STORAGE_DEF', self.storage_manager, self.manager, op_level, sp_ids, scan_result)
        else:
            if group:
                group_defns = DBSession.query(SPDefLink).filter_by(group_id=group.id)
            elif site:
                group_defns = DBSession.query(DCDefLink).filter_by(site_id=site.id)
            for group_defn in group_defns:
                rowSDef = DBSession.query(StorageDef).filter_by(id=group_defn.def_id, name=new_name).first()
                if rowSDef and rowSDef.id != storage_id:
                    raise Exception('Storage definition with the same name already exists')
            defn = DBSession.query(StorageDef).filter_by(id=storage_id).first()
            self.sync_manager.update_defn(defn, new_name, new_desc, site, group, auth, to_unicode(constants.STORAGE), constants.ATTACH, self.storage_manager, 'UPDATE_STORAGE_DEF', op_level, sp_ids, self.manager)


    def storage_definition(self, storage):
        storagedef = DBSession.query(StorageDef).filter(StorageDef.name == storage).first()
        return storagedef

    def remove_storage_def_cli(self, auth, storage, site_id, op_level, groupId=None):
        storagedef = self.storage_definition(storage)
        if storagedef:
            storage_id = storagedef.id
            result = self.remove_storage_def(auth, storage_id, site_id, groupId, op_level)
            return result
        return {'success':False,'msg':'The storage'+storage+'does not exists'}


    def is_storage_allocated(self, storage_id):
        returnVal = False
        msg = 'NOT_IN_USE'
        try:
            returnVal = self.storage_manager.is_storage_allocated(storage_id)
            if returnVal:
                msg = 'IN_USE'
            return "{success: true,msg: '" + msg + "'}"
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            return "{success: false,msg: '" + to_str(ex) + "'}"


    def remove_storage_def(self, auth, storage_id, site_id, groupId, op_level=None):
        try:
            site = self.manager.getSite(site_id)
            group = self.manager.getGroup(auth, groupId)
            group_list = self.manager.getGroupList(auth, site_id)
            sd_to_remove = self.storage_manager.get_sd(storage_id, site_id, groupId, to_unicode(constants.STORAGE))
            node = None
            add_mode = False
            warning_msg = self.sync_manager.remove_defn(sd_to_remove, site, group, node, auth, to_unicode(constants.STORAGE), constants.DETACH, 'REMOVE_STORAGE_DEF', self.storage_manager, self.manager, add_mode, group_list, op_level)
            if warning_msg:
                return "{success: true,msg: '" + warning_msg + "'}"
            return "{success: true,msg: 'Storage Removed'}"
        except Exception as ex:
            print_traceback()
            err_desc = to_str(ex).replace("'", '')
            err_desc = err_desc.strip()
            LOGGER.error(to_str(err_desc))
            return "{success: false,msg: '" + err_desc + "'}"


    def rename_storage_def(self, auth, new_name, storage_id, groupId):
        pass

    def get_vm_linked_with_storage(self, storage_disk_id):
        vm = None
        if storage_disk_id:
            vm_storage_link = DBSession.query(VMStorageLinks).filter_by(storage_disk_id=storage_disk_id).first()
            if vm_storage_link:
                vm_disk = DBSession.query(VMDisks).filter_by(id=vm_storage_link.vm_disk_id).first()
                if vm_disk:
                    vm = DBSession.query(VM).filter_by(id=vm_disk.vm_id).first()
        return vm


    def edit_test_output(self, details):
        objStat = {}
        objSummary = {}
        objDetailsList = []
        objStorageDetails = {}
        if details:
            objSummary = details.get('SUMMARY')
            objStorageDetails = details.get('STORAGE_DETAILS')
            details_list = details.get('DETAILS')
            for objDetails in details_list:
                storage_disk_id = None
                storage_allocated = False
                vm_name = None
                disk_name = None
                if objDetails.get('uuid'):
                    unique_path = str(objDetails.get('uuid')).strip()
                    storage_disk = DBSession.query(StorageDisks).filter_by(unique_path=to_unicode(unique_path)).first()
                    storage_allocated = 'No'
                    if storage_disk:
                        if storage_disk.storage_allocated == True:
                            storage_allocated = 'Yes'
                            storage_disk_id = storage_disk.id
                    uuid_param = to_str(unique_path).split('/')
                    disk_name = uuid_param[len(uuid_param) - 1]
                objDetails['STORAGE_ALLOCATED'] = storage_allocated
                objDetails['DISKS'] = disk_name
                if storage_disk_id:
                    vm = self.get_vm_linked_with_storage(storage_disk_id)
                    if vm:
                        vm_name = vm.name
                objDetails['VM_NAME'] = vm_name
                objDetailsList.append(objDetails)
        objStat['STORAGE_DETAILS'] = objStorageDetails
        objStat['DETAILS'] = objDetailsList
        objStat['SUMMARY'] = objSummary
        return objStat



    def get_storage_for_test(self, storage_id):
        objStat = {}
        objSummary = {}
        objDetailsList = []
        objDetails = {}
        objStorageDetails = {}
        disk_name = None
        storage_type = None
        total_size = 0
        available_size = 0
        if storage_id:
            defn = self.storage_manager.get_defn(storage_id)
            if defn:
                stats = defn.get_stats()
                if stats:
                    total_size = stats.total_size
                    objStorageDetails = []
                    storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=defn.id)
                    for each_storage_disk in storage_disks:
                        if objDetails:
                            objDetailsList.append(objDetails)
                            objDetails = {}
                        objDetails['STORAGE_DISK_ID'] = None
                        objDetails['STORAGE_ALLOCATED'] = False
                        objDetails['USED'] = each_storage_disk.size
                        objDetails['SIZE'] = each_storage_disk.actual_size
                        objDetails['CurrentPortal'] = None
                        objDetails['Target'] = None
                        objDetails['uuid'] = each_storage_disk.unique_path
                        objDetails['State'] = None
                        objDetails['Lun'] = None
                        objDetails['VM_NAME'] = None
                    objStat['name'] = defn.name
                    objStat['success'] = True
                    objStat['type'] = defn.type
                    objStat['id'] = defn.id
                    objStat['op'] = constants.GET_DISKS
        if objStorageDetails:
            objStat['STORAGE_DETAILS'] = objStorageDetails
        if objDetails:
            objDetailsList.append(objDetails)
            objStat['DETAILS'] = objDetailsList
        if objSummary:
            objStat['SUMMARY'] = objSummary
        return objStat

#############################################pas
    def get_storage_disks_for_test(self, storage_id, show_available, vm_config_action, disk_option):
        objStat = {}
        objSummary = {}
        objDetailsList = []
        objDetails = {}
        objStorageDetails = []
        disk_name = None
        storage_type = None
        total_size = 0
        available_size = 0
        vm_name = None
        storage_disks = None
        if vm_config_action  == 'provision_vm' or vm_config_action == 'provision_image' or vm_config_action == 'edit_image':
            if disk_option == 'CREATE_DISK':
                objStat = self.get_storage_for_test(storage_id)
                return objStat

        if show_available == 'true':
            storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=storage_id, storage_allocated=False)
        else:
            storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=storage_id)

        if storage_id:
            defn = self.storage_manager.get_defn(storage_id)
            if defn:
                stats = defn.get_stats()
                if stats:
                    total_size = stats.total_size
                    objSummary['TOTAL'] = total_size
                    storage_detail = {}
                    storage_detail['AVAILABLE'] = stats.available_size
                    storage_detail['USED'] = stats.used_size
                    storage_detail['SIZE'] = stats.total_size
                    storage_detail['MOUNT'] = ''
                    storage_detail['FILESYSTEM'] = ''
                    storage_detail['VOLUME_GROUP'] = ''
                    storage_detail['uuid'] = ''
                    objStorageDetails.append(storage_detail)
        if storage_disks:
            for each_storage_disk in storage_disks:
                if objDetails:
                    objDetailsList.append(objDetails)
                    objDetails = {}
                disk_name = each_storage_disk.disk_name
                storage_type = each_storage_disk.storage_type
                storage_id = each_storage_disk.storage_id
                objDetails['STORAGE_DISK_ID'] = each_storage_disk.id
                if each_storage_disk.storage_allocated == True:
                    objDetails['STORAGE_ALLOCATED'] = 'Yes'
                else:
                    objDetails['STORAGE_ALLOCATED'] = 'No'

                objDetails['USED'] = each_storage_disk.size
                objDetails['SIZE'] = each_storage_disk.actual_size
                objDetails['CurrentPortal'] = each_storage_disk.current_portal
                objDetails['Target'] = each_storage_disk.target
                objDetails['uuid'] = each_storage_disk.unique_path
                objDetails['State'] = each_storage_disk.state
                objDetails['Lun'] = each_storage_disk.lun
                vm_name = None
                vm = self.get_vm_linked_with_storage(each_storage_disk.id)
                if vm:
                    vm_name = vm.name

                objDetails['VM_NAME'] = vm_name
                disk_name = None
                unique_path = each_storage_disk.unique_path
                if unique_path:
                    uuid_param = to_str(unique_path).split('/')
                    disk_name = uuid_param[len(uuid_param) - 1]

                objDetails['DISKS'] = disk_name
                logical_volume = None
                disk_param = []
                disk_param = to_str(each_storage_disk.unique_path).split('/')
                if disk_param:
                    logical_volume = disk_param[len(disk_param) - 1]

                objDetails['LOGICAL_VOLUME'] = logical_volume

            objStat['name'] = defn.name
            objStat['success'] = True
            objStat['type'] = storage_type
            objStat['id'] = storage_id
            objStat['op'] = constants.GET_DISKS

        if objStorageDetails:
            objStat['STORAGE_DETAILS'] = objStorageDetails

        if objDetails:
            objDetailsList.append(objDetails)
            objStat['DETAILS'] = objDetailsList

        if objSummary:
            objStat['SUMMARY'] = objSummary

        return objStat


    def storage_def_test_cli(self, auth, storage_name, nodeId, groupId, site_id, type, mode, opts, scope, show_available='true', vm_config_action=None, disk_option=None):
        storagedef = DBSession.query(StorageDef).filter(StorageDef.name == storage_name).first()
        if storagedef:
            storage_id = storagedef.id
            result = self.storage_def_test(auth, storage_id, nodeId, groupId, site_id, type, mode, opts, scope, show_available, vm_config_action, disk_option)
            return result

        return dict(success=False, msg='The storage ' + storage_name + ' does not exists')

###########################pas
    def storage_def_test(self, auth, storage_id, nodeId, groupId, site_id, type, mode, opts, scope, show_available='true', vm_config_action=None, disk_option=None):
        if mode == 'SELECT':
            result = self.get_storage_disks_for_test(storage_id, show_available, vm_config_action, disk_option)
            return result
        try:
            self.storage_manager.RemoveScanResult()
            group = self.manager.getGroup(auth, groupId)
            managed_node = self.manager.getNode(auth, nodeId)
            if not managed_node:
                raise Exception('Managed Server not found.')
            
            try:
                managed_node.connect()
            except AuthenticationException as ex:
                if opts.has_key('username') and opts.has_key('password'):
                    managed_node.set_credentials(opts['username'], opts['password'])
                    try:
                        managed_node.connect()
                    except AuthenticationException as ex:
                        print_traceback()
                        LOGGER.error(to_str(ex).replace("'", ''))
                        return ("{success: false,msg: '", to_str(ex).replace("'", ''), "',error:'Not Authenticated'}")
                else:
                    return ("{success: false,msg: '", to_str(ex).replace("'", ''), "',error:'Not Authenticated'}")
            sd = None
            if mode == 'TEST' or mode == 'EDIT' or mode == 'SELECT':
                sd = self.storage_manager.get_sd(storage_id, site_id, groupId, to_unicode(constants.STORAGE))
            else:
                sd = self.get_valid_sd(type, opts, scope)
            if site_id:
                if site_id == 'data_center':
                    site = self.manager.getSiteByGroupId(group.id)
                else:
                    site = self.manager.getSite(site_id)
            else:
                site = self.manager.getSiteByGroupId(group.id)
            result = self.test_storage_def(auth, managed_node, group, site, sd)
            if result or  mode == 'NEW' or mode == 'EDIT':
                #if not mode == 'NEW' or mode == 'EDIT':
                try:
                    session[constants.SCAN_RESULT] = result
                    session.save()
                except Exception as ex:
                    print_traceback()
                    LOGGER.error('Error while keeping the scan result in session: ' + to_str(ex).replace("'", ''))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        return result



    def test_storage_def(self, auth, managed_node, group, site, sd):
        details = None
        testmsg = None
        try:
            details = self.storage_manager.get_sd_details(auth, sd, managed_node, group, site, to_unicode(constants.STORAGE), self.storage_manager)
            details = self.edit_test_output(details)
        except Exception as ex:
            testmsg = ex
        
        if details == None or len(details) == 0 or testmsg != None:
            if testmsg:
                LOGGER.info(to_str(testmsg).replace("'", ''))
            else:
                testmsg = ''
            return dict(success=False, msg=to_str(testmsg).replace("'", ''))
        details['success'] = 'true'
        return details

    def get_defn(self, sd):
        if not sd:
            return ''
        desc = None
        if sd.type == constants.NFS:
            desc = sd.connection_props['server'] + ', ' + sd.connection_props['share']
        elif sd.type == constants.iSCSI:
            desc = sd.connection_props['server'] + ', ' + sd.connection_props['target']
        elif sd.type == constants.AOE:
            desc = sd.connection_props['interface']
        if not desc:
            return ''
        return desc

###################
    def get_server_def_list(self, auth, site_id, group_id, def_id):
        try:
            server_def_list = []
            node_defns = self.sync_manager.get_node_defns(def_id, to_unicode(constants.STORAGE))
            if node_defns:
                for eachdefn in node_defns:
                    temp_dic = {}
                    if eachdefn:
                        node = DBSession.query(ManagedNode).filter_by(id=eachdefn.server_id).first()
                        node_entity = auth.get_entity(node.id)
                        if group_id:
                            if group_id == node_entity.parents[0].entity_id:
                                temp_dic['id'] = eachdefn.server_id
                                if node:
                                    temp_dic['name'] = node.hostname
                                    temp_dic['serverpool'] = node_entity.parents[0].name
                                else:
                                    temp_dic['name'] = None
                                    temp_dic['serverpool'] = None
                                temp_dic['status'] = eachdefn.status
                                if eachdefn.details:
                                    temp_dic['details'] = eachdefn.details
                                else:
                                    temp_dic['details'] = None
                                server_def_list.append(temp_dic)
                        else:
                            temp_dic['id'] = eachdefn.server_id
                            if node:
                                temp_dic['name'] = node.hostname
                                temp_dic['serverpool'] = node_entity.parents[0].name
                            else:
                                temp_dic['name'] = None
                                temp_dic['serverpool'] = None
                            temp_dic['status'] = eachdefn.status
                            if eachdefn.details:
                                temp_dic['details'] = eachdefn.details
                            else:
                                temp_dic['details'] = None
                            server_def_list.append(temp_dic)
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")
        return dict(success='true', rows=server_def_list)


    def sync_defn(self, auth, server_ids, def_id, site_id, group_id):
        server_id_list = server_ids.split(',')
        for server_id in server_id_list:
            node = DBSession.query(ManagedNode).filter_by(id=server_id).first()
            defn = DBSession.query(StorageDef).filter_by(id=def_id).first()
            self.sync_manager.sync_node_defn(auth, node, group_id, site_id, defn, constants.STORAGE, constants.ATTACH, self.storage_manager)
        return dict(success='true')


    def get_total_storage(self, auth, site_id, group_id, scope=None):
        try:
            result = self.get_storage_def_list(auth, site_id, group_id, scope)
            total_storage = 0.0
            stge_res = result.get('rows')
            for val in stge_res:
                if val.get('size'):
                    total_storage = total_storage + float(val.get('size'))
            return total_storage
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex


    def update_disks_size(self, auth):
        from stackone.model.availability import AvailState
        sites = DBSession.query(Site)
        if sites:
            for eachsite in sites:
                site_entity = auth.get_entity(eachsite.id)
                group_entities = auth.get_entities(to_unicode(constants.SERVER_POOL), site_entity)
                for eachgroup in group_entities:
                    group = DBSession.query(ServerGroup).filter_by(id=eachgroup.entity_id).first()
                    if group:
                        group_entity = auth.get_entity(group.id)
                        node_entities = auth.get_entities(to_unicode(constants.MANAGED_NODE), group_entity)
                        for eachnode in node_entities:
                            node = DBSession.query(ManagedNode).filter_by(id=eachnode.entity_id).first()
                            is_node_up = True
                            objAvailState = DBSession.query(AvailState).filter_by(entity_id=node.id).first()
                            if objAvailState:
                                avail_state = objAvailState.avail_state
                                if avail_state == node.DOWN:
                                    is_node_up = False
                            if is_node_up:
                                server_def_link = DBSession.query(ServerDefLink).filter_by(server_id=node.id)
                                if server_def_link:
                                    for each_link in server_def_link:
                                        defn = DBSession.query(StorageDef).filter_by(id=each_link.def_id).first()
                                        if defn:
                                            if defn.type == constants.NFS or defn.type == constants.OCFS or defn.type == constants.CIFS or defn.type == constants.GFS:
                                                scan_result = self.test_storage_def(auth, node, group, eachsite, defn)
                                                self.update_size(defn, scan_result)


    def update_size(self, defn, scan_result):
        LOGGER.info('Updating sizes...')
        if not scan_result:
            LOGGER.info('Scan result is empty. Not updating sizes.')
            return None
        success = scan_result.get('success')
        if not success:
            LOGGER.info('Scan is failed. Not updating sizes.')
            return None
        objDetailsList = scan_result['DETAILS']
        if not objDetailsList:
            LOGGER.error('DETAILS object is not found in scan result. Can not update size in storage_definitions table.')
            return None
        for each_disk in objDetailsList:
            unique_path = each_disk.get('uuid')
            if unique_path:
                used_size = each_disk.get('USED')
                if not used_size:
                    used_size = 0
                if float(used_size) < 0:
                    used_size = 0
                storage_disk = DBSession.query(StorageDisks).filter_by(storage_id=defn.id, unique_path=to_unicode(unique_path)).first()
                if storage_disk:
                    storage_disk.disk_size = used_size
                    LOGGER.info('Storage disk is updated')
                    transaction.commit()


    def RemoveScanResult(self):
        result = self.storage_manager.RemoveScanResult()
        return result

    def SaveScanResult(self, storage_id, site_id):
        scan_result = None
        result = self.storage_manager.SaveScanResult(storage_id, self.manager, scan_result, site_id)
        return result

    def add_storage_disk_manually(self, add_manually, auth, group_id, storage_id, actual_size, allocated_size, unique_path, current_portal, target, state, lun, storage_allocated):
        try:
            storage_disk_id = self.storage_manager.add_storage_disk(storage_id, actual_size, allocated_size, unique_path, current_portal, target, state, lun, storage_allocated, self.manager, add_manually)
            vm_disk_list = self.manager.get_vm_disks_from_pool(auth, group_id)
            self.manager.matching_disk_on_discover_storage(vm_disk_list, storage_disk_id)
            return "{success:true, msg:''}"
        except Exception as ex:
            error_msg = to_str(ex).replace("'", '')
            LOGGER.error(error_msg)
            return "{success:false, msg:'" + error_msg + "'}"


    def remove_storage_disk_cli(self, storage_disk_name):
        storagedisk = DBSession.query(StorageDisks).filter(StorageDisks.unique_path == storage_disk_name).first()
        if storagedisk:
            storage_disk_id = storagedisk.id
            result = self.remove_storage_disk_manually(storage_disk_id)
            if result == "{success:true, msg:''}":
                return dict(success=True, msg='The storage disk ' + storage_disk_name + ' removed successfully\n')
            return dict(success=False, msg=result)
        return dict(success=False, msg='The storage disk ' + storage_disk_name + ' does not exists')


    def remove_storage_disk_manually(self, storage_disk_id):
        try:
            self.manager.remove_storage_disk_links(storage_disk_id)
            self.storage_manager.remove_storage_disk_manually(storage_disk_id)
            return "{success:true, msg:''}"
        except Exception as ex:
            error_msg = to_str(ex).replace("'", '')
            LOGGER.error(error_msg)
            return "{success:false, msg:'" + error_msg + "'}"


    def mark_storage_disk(self, storage_disk_id, used):
        try:
            self.storage_manager.mark_storage_disk(storage_disk_id, used)
            return "{success:true, msg:''}"
        except Exception as ex:
            error_msg = to_str(ex).replace("'", '')
            LOGGER.error(error_msg)
            return "{success:false, msg:'" + error_msg + "'}"


    def mark_storage_disk_cli(self, storage, used):
        storagedisk = DBSession.query(StorageDisks).filter(StorageDisks.unique_path == storage).first()
        if storagedisk:
            storage_disk_id = storagedisk.id
            result = self.mark_storage_disk(storage_disk_id, used)
            if result == "{success:true, msg:''}":
                return dict(success=True, msg='The storage disk ' + storage + ' allocated successfully')
            return dict(success=False, msg=result)
        return dict(success=False, msg='The storage disk ' + storage + ' does not exists')


    def create_disk(self, context, managed_node=None):
        self.storage_manager.execute_create_disk_script(context, managed_node)

    def remove_disk(self, context, managed_node=None):
        self.storage_manager.execute_remove_disk_script(context, managed_node)

