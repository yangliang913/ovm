from sqlalchemy import func, outerjoin, join
from datetime import datetime
from stackone.core.utils.utils import copyToRemote, getHexID, mkdir2, get_config_text
from stackone.core.utils.utils import to_unicode, to_str, p_timing_start, p_timing_end
import stackone.core.utils.utils
from stackone.core.utils.constants import *
constants = stackone.core.utils.constants
import os
import tg
import transaction
import pprint
from tg import session
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String, Boolean, PickleType, Float, DateTime
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.orm import relation, backref
from stackone.model import DeclarativeBase, DBSession
from stackone.model.ManagedNode import ManagedNode
from stackone.model.Groups import ServerGroup
from stackone.model.SPRelations import ServerDefLink, SPDefLink, DCDefLink, StorageDisks, Storage_Stats, Upgrade_Data
from stackone.model.VM import VMDisks, VMStorageLinks, VM
from stackone.model.Entity import Entity, EntityRelation
from stackone.model.Sites import Site
from stackone.core.utils.utils import dynamic_map
from stackone.model.Authorization import AuthorizationService
from stackone.model.SyncDefinition import SyncDef
import logging
LOGGER = logging.getLogger('stackone.model')
STRG_LOGGER = logging.getLogger('STORAGE_TIMING')

class StorageDef(DeclarativeBase):
    __tablename__ = 'storage_definitions'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(100), nullable=False)
    type = Column(Unicode(50), nullable=False)
    description = Column(Unicode(250))
    connection_props = Column(PickleType)
    creds_required = Column(Boolean)
    creds = Column(PickleType)
    is_deleted = Column(Boolean)
    scope = Column(String(2))
    def __init__(self, id, name, type, description, connection_props, scope, creds_required=False, is_deleted=False, status=None):
        self.id = id
        if self.id is None:
            self.id = getHexID()
        self.name = name
        self.type = type
        self.description = description
        self.connection_props = connection_props
        self.creds_required = creds_required
        self.creds = {}
        self.total_size = 0
        self.is_deleted = is_deleted
        self.status = status
        self.scope = scope


    def sanitized_creds(self):
        if self.creds and self.creds.get('password'):
            new_creds = self.creds.copy()
            new_creds['password'] = None
            return new_creds
        return self.creds


    def __repr__(self):
        return to_str(dict(id = self.id,type = self.type,name = self.name,connection_props = self.connection_props,creds_required = self.creds_required,creds = self.creds_required))
    
    def get_connection_props(self):
        return self.connection_props

    def set_connection_props(self, cp):
        self.connetion_props = cp

    def get_creds(self):
        return self.creds

    def set_creds(self, creds):
        self.creds = creds

    def get_stats(self):
        ss = None
        dc_def = DBSession.query(DCDefLink).filter_by(def_id=self.id).first()
        if dc_def:
            ss = DBSession.query(Storage_Stats).filter_by(entity_id=dc_def.site_id, storage_id=self.id).first()
        return ss

    def set_status(self, status):
        self.status = status



Index('strgedef_type', StorageDef.type)
class StorageManager():
    s_scripts_location = '/var/cache/stackone/storage'
    FILE_BASED_STORAGE = [constants.NFS, constants.GFS, constants.GFS2, constants.OCFS, constants.OCFS2, constants.CIFS]
    BLOCK_STORAGE = [constants.LVM, constants.iSCSI, constants.AOE, constants.FC]
    STORAGE_FOR_CREATION = []
    STORAGE_FOR_REMOVAL = []
    
    
    def __init__(self):
        self.storage_processors = {constants.NFS : self.nfs_processor,\
                            constants.iSCSI : self.iscsi_processor,\
                            constants.AOE : self.aoe_processor,\
                            constants.LVM : self.lvm_processor,\
                            constants.CIFS : self.cifs_processor,\
                            constants.GFS : self.gfs_processor,\
                            constants.OCFS : self.ocfs_processor,\
                            constants.FC : self.fc_processor}
        self.STORAGE_FOR_CREATION = []
        self.STORAGE_FOR_CREATION = self.get_storage_for_creation_list(self.FILE_BASED_STORAGE)
        self.STORAGE_FOR_REMOVAL = []
        self.STORAGE_FOR_REMOVAL = self.get_storage_for_removal_list(self.FILE_BASED_STORAGE)
    def get_storage_for_creation_list(self, storage_type_list):
        temp_list = []
        temp_list.extend(storage_type_list)
        temp_list.append(constants.LVM)
        return temp_list

    def get_storage_for_removal_list(self, storage_type_list):
        temp_list = []
        temp_list.extend(storage_type_list)
        temp_list.append(constants.LVM)
        return temp_list

    def getType(self):
        return to_unicode(constants.STORAGE)

    def getSiteDefListToAssociate(self, site_id, group_id, defType):
        sdArray = []
        if site_id:
            dc_rs = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type=defType)
            if dc_rs:
                for row in dc_rs:
                    sp_def = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_id=row.def_id, def_type=defType).first()
                    if not sp_def:
                        defn = DBSession.query(StorageDef).filter_by(id=row.def_id, scope=constants.SCOPE_DC).first()
                        if defn:
                            defn.status = row.status
                            sdArray.append(defn)
        return sdArray

    def get_sds(self, site_id, group_id):
        if group_id:
            rs = DBSession.query(SPDefLink).filter_by(group_id=group_id)
        else:
            if site_id:
                rs = DBSession.query(DCDefLink).filter_by(site_id=site_id)
        sdArray = []

        for row in rs:
            row_nw = DBSession.query(StorageDef).filter_by(id=row.def_id).first()
            if row_nw:
                sdArray.append(row_nw)
        return sdArray

    def get_sd_ids(self, site_id, group_id, defType, scope):
        ids_array = []
        sync_manager = SyncDef()
        def_ids = None
        if scope == constants.SCOPE_SP or scope == constants.SCOPE_S:
            def_ids = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_type=to_unicode(defType))
        elif scope == constants.SCOPE_DC:
            def_ids = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type=to_unicode(defType))

        return def_ids
    def get_sd(self, sd_id, site_id, group_id, defType):
        status = None
        rsSD = DBSession.query(StorageDef).filter_by(id=sd_id).first()
        if rsSD:
            if rsSD.scope == constants.SCOPE_SP:
                group_defn = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_type=to_unicode(defType), def_id=sd_id).first()
            elif rsSD.scope == constants.SCOPE_DC:
                group_defn = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type=to_unicode(defType), def_id=sd_id).first()
            if group_defn:
                status = group_defn.status
            rsSD.status = status
        return rsSD

    def get_defn(self, id):
        defn = DBSession.query(StorageDef).filter_by(id=id).first()
        return defn

    def get_sd_details(self, auth, sd, node, group, site, defType, def_manager):
        sync_manager = SyncDef()
        details = None
        groupId = None
        existing_def = None
        if group:
            groupId = group.id
        else:
            entity = auth.get_entity(node.id)
            if entity:
                groupId = entity.parents[0].entity_id

        result_processor = self.storage_processors[sd.type]
        update_status = False
        try:
            errs = []
            op = constants.GET_DISKS
            details = sync_manager.sync_node_defn(auth, node, groupId, site.id, sd, to_unicode(defType), op, def_manager, update_status, errs, processor=result_processor)
        except Exception as ex:
            existing_def = def_manager.isDefnExists(sd, node)
            if existing_def:
                LOGGER.info('Definition already exists. This definition matches with the existing definition ' + existing_def.name + ' on the server ' + node.hostname)

            op = constants.ATTACH
            sync_manager.sync_node_defn(auth, node, groupId, site.id, sd, defType, op, def_manager)
            errs = []
            op = constants.GET_DISKS
            details = sync_manager.sync_node_defn(auth, node, groupId, site.id, sd, defType, op, def_manager, update_status, errs, processor=result_processor)
            if not existing_def:
                op = constants.DETACH
                sync_manager.sync_node_defn(auth, node, groupId, site.id, sd, defType, op, def_manager)
        return details

    def parse_diskdetails(self, output, result):
        disk_details = []
        if output:
            for i in output.splitlines():
                d = {}
                if not i:
                    continue
                i = i.strip()
                if i.find('DISK_DETAILS') != 0:
                    continue
                for j in i.split('|'):
                    nameAndValue = j.lstrip().split('=')
                    d[nameAndValue[0]] = nameAndValue[1]
                del d['DISK_DETAILS']
                disk_details.append(d)
        return disk_details

    def parse_output(self, output, result):
        Lista = []
        if output:
            for i in output.splitlines():
                d = {}
                if not i:
                    continue
    
                i = i.strip()
                if i.find('OUTPUT') != 0:
                    continue
                for j in i.split('|'):
                    nameAndValue = j.lstrip().split('=')
                    d[nameAndValue[0]] = nameAndValue[1]

                del d['OUTPUT']
                Lista.append(d)
        return Lista

    def parse_summary(self, output, result):
        if output:
            for i in output.splitlines():
                d = {}
                if not i:
                    continue
                i = i.strip()
                if i.find('SUMMARY') != 0:
                    continue
                for j in i.split('|'):
                    nameAndValue = j.lstrip().split('=')
                    d[nameAndValue[0]] = nameAndValue[1]
                del d['SUMMARY']
            return d

    def nfs_processor(self, op, output, result):
        print 'nfs processor called with \n',
        print output
        if op == 'GET_DISKS_SUMMARY':
            result['SUMMARY'] = self.parse_summary(output, result)
        else:
            result['STORAGE_DETAILS'] = self.parse_output(output, result)
            result['DETAILS'] = self.parse_diskdetails(output, result)
            result['SUMMARY'] = self.parse_summary(output, result)

    def iscsi_processor(self, op, output, result):
        print 'iscsi processor called with \n',
        print output
        if op == 'GET_DISKS_SUMMARY':
            result['SUMMARY'] = self.parse_summary(output, result)
        else:
            result['STORAGE_DETAILS'] = self.parse_output(output, result)
            result['DETAILS'] = self.parse_output(output, result)
            result['SUMMARY'] = self.parse_summary(output, result)

    def fc_processor(self, op, output, result):
        print 'fc processor called with \n',
        print output
        if op == 'GET_DISKS_SUMMARY':
            result['SUMMARY'] = self.parse_summary(output, result)
        else:
            result['STORAGE_DETAILS'] = self.parse_output(output, result)
            result['DETAILS'] = self.parse_output(output, result)
            result['SUMMARY'] = self.parse_summary(output, result)

    def aoe_processor(self, op, output, result):
        print 'aoe processor called with \n',
        print output
        if op == 'GET_DISKS_SUMMARY':
            result['SUMMARY'] = self.parse_summary(output, result)
        else:
            result['STORAGE_DETAILS'] = self.parse_output(output, result)
            result['DETAILS'] = self.parse_output(output, result)
            result['SUMMARY'] = self.parse_summary(output, result)

    def lvm_processor(self, op, output, result):
        print 'lvm processor called with \n',
        print output
        if op == 'GET_DISKS_SUMMARY':
            result['SUMMARY'] = self.parse_summary(output, result)
        else:
            result['STORAGE_DETAILS'] = self.parse_output(output, result)
            result['DETAILS'] = self.parse_diskdetails(output, result)
            result['SUMMARY'] = self.parse_summary(output, result)

    def cifs_processor(self, op, output, result):
        print 'cifs processor called with \n',
        print output
        if op == 'GET_DISKS_SUMMARY':
            result['SUMMARY'] = self.parse_summary(output, result)
        else:
            result['STORAGE_DETAILS'] = self.parse_output(output, result)
            result['DETAILS'] = self.parse_diskdetails(output, result)
            result['SUMMARY'] = self.parse_summary(output, result)

    def ocfs_processor(self, op, output, result):
        print 'ocfs processor called with \n',
        print output
        if op == 'GET_DISKS_SUMMARY':
            result['SUMMARY'] = self.parse_summary(output, result)
        else:
            result['STORAGE_DETAILS'] = self.parse_output(output, result)
            result['DETAILS'] = self.parse_diskdetails(output, result)
            result['SUMMARY'] = self.parse_summary(output, result)

    def gfs_processor(self, op, output, result):
        print 'gfs processor called with \n',
        print output
        self.nfs_processor(op, output, result)

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

    def prepare_scripts(self, dest_node, type, defType):
        s_src_scripts_location = tg.config.get('storage_script')
        s_src_scripts_location = os.path.abspath(s_src_scripts_location)
        LOGGER.info('Source script location= ' + to_str(s_src_scripts_location))
        LOGGER.info('Destination script location= ' + to_str(self.s_scripts_location))
        copyToRemote(s_src_scripts_location, dest_node, self.s_scripts_location)
        common_function_script_name = os.path.join(s_src_scripts_location, 'storage_functions')
        LOGGER.info('Common source script location= ' + to_str(common_function_script_name))
        dest_location = os.path.join(self.s_scripts_location, 'scripts')
        LOGGER.info('Common destination script location= ' + to_str(dest_location))
        copyToRemote(common_function_script_name, dest_node, dest_location, 'storage_functions')

    def exec_script(self, node, group, defn, defType, op=constants.GET_DETAILS, context=None):
        disk_type = ''
        disk_name = ''
        disk_size = ''
        fs_type = ''
        cms_cloud = ''
        image_store_location = ''
        if context:
            disk_type = context.get('disk_type')
            disk_name = context.get('disk_name')
            disk_size = context.get('disk_size')
            fs_type = context.get('fs_type')
            cms_cloud = context.get('cms_cloud')
            image_store_location = context.get('image_store_location')
        type = ''
        if defn:
            type = defn.type
        else:
            type = constants.NFS

        self.prepare_scripts(node, type, defType)
        script_name = os.path.join(self.s_scripts_location, 'scripts', type, 'storage.sh')
        log_dir = node.config.get(prop_log_dir)
        if log_dir is None or log_dir == '':
            log_dir = DEFAULT_LOG_DIR
        log_filename = os.path.join(log_dir, 'storage/scripts', type, 'storage_sh.log')
        mkdir2(node, os.path.dirname(log_filename))
        mount_point = ''
        if type == constants.NFS and defn:
            mount_point = defn.connection_props.get('mount_point')
            if mount_point.startswith('/') == True:
                mkdir2(node, mount_point)
        elif type == constants.GFS:
            type = constants.GFS2
        elif type == constants.OCFS:
            type = constants.OCFS2
        cp = ''
        creds_str = ''
        password = ''
        if defn:
            cp = self.props_to_cmd_param(defn.connection_props)
            creds_str = self.props_to_cmd_param(defn.creds)
            password = defn.creds.get('password')
        script_loc = os.path.join(self.s_scripts_location, 'scripts')
        file_filter = '*.disk.xm'
        script_args = ''
        if type:
            script_args = ' -t ' + type
        if cp:
            script_args += ' -c ' + cp

        if creds_str:
            script_args += ' -p ' + creds_str
        if op:
            script_args += ' -o ' + op

        if script_loc:
            script_args += ' -s ' + script_loc
        if log_filename:
            script_args += ' -l ' + log_filename

        if file_filter:
            script_args += ' -w ' + file_filter
        if image_store_location:
            script_args += ' -r ' + image_store_location

        if disk_name:
            script_args += ' -d ' + disk_name
        if disk_type:
            script_args += ' -y ' + disk_type

        if disk_size:
            script_args += ' -z ' + to_str(disk_size)
        if fs_type:
            script_args += ' -f ' + fs_type

        cmd = script_name + script_args
        cmd_temp = cmd.replace('password=' + to_str(password), 'password=*****')
        LOGGER.info('Command= ' + to_str(cmd_temp))
        output = 'Success'
        exit_code = 0
        output,exit_code = node.node_proxy.exec_cmd(cmd)
        LOGGER.info('Exit Code= ' + to_str(exit_code))
        LOGGER.info('Output of script= ' + to_str(output))
        return (exit_code, output)

    def iscsi_target_login_check(self, output, exit_code):
        if to_str(output).find('iscsiadm: initiator reported error (15 - already exists)') >= 0:
            info_text = 'Already logged in to ISCSI target...'
            LOGGER.info(info_text)
            output = info_text
            exit_code = 0
        return (exit_code, output)

    def CheckOp(self, op, errs):
        if op not in [constants.GET_DISKS, constants.GET_DISKS_SUMMARY, constants.ATTACH, constants.DETACH]:
            errs.append('Invalid storage defn sync op ' + op)
            raise Exception('Invalid storage defn sync op ' + op)
        return errs

    def isDefnExists(self, defn, node):
        returnVal = None
        con_props_new = defn.connection_props
        server_new = con_props_new.get('server')
        share_new = con_props_new.get('share')
        mount_point_new = con_props_new.get('mount_point')
        target_new = con_props_new.get('target')
        node_defns = DBSession.query(ServerDefLink).filter_by(server_id=node.id)
        for eachdefn in node_defns:
            sd = DBSession.query(StorageDef).filter_by(id=eachdefn.def_id).first()
            if sd:
                con_props = sd.connection_props
                server = con_props.get('server')
                share = con_props.get('share')
                local_server = node.hostname
                mount_point = con_props.get('mount_point')
                target = con_props.get('target')
                if defn.type == constants.NFS and server == server_new and share == share_new and mount_point == mount_point_new:
                    returnVal = sd
                if defn.type == constants.iSCSI and server == server_new and target == target_new:
                    returnVal = sd
        return returnVal


    def getSyncMessage(self, op):
        messasge = None
        if op == constants.ATTACH:
            messasge = 'Mount operation is done successfully.'
        elif op == constants.DETACH:
            messasge = 'Unmount operation is done successfully.'
        return messasge


    def manage_storage_disk(self, storage_id, grid_manager, scan_result, site_id):
        LOGGER.info('Managing storage disks...')
        defn = self.get_defn(storage_id)
        if defn:
            total_size = 0
            used_size = 0
            available_size = 0
            if scan_result:
                objStorage_details = scan_result.get('STORAGE_DETAILS')
                objStorage_details = objStorage_details[0]
                objSummary = scan_result.get('SUMMARY')
                objStats_details = scan_result.get('DETAILS')
                ss_new_rec = False
                ss = DBSession.query(Storage_Stats).filter_by(entity_id=site_id, storage_id=storage_id).first()
                if not ss:
                    ss_new_rec = True
                    ss = Storage_Stats()
                    ss.id = getHexID()
                    ss.entity_id = site_id
                    ss.storage_id = storage_id

                if objSummary:
                    total_size = objSummary.get('TOTAL')
                if objStorage_details:
                    used_size = objStorage_details.get('USED')
                    available_size = objStorage_details.get('AVAILABLE')
                ss.total_size = total_size
                ss.used_size = used_size
                ss.available_size = available_size
                if ss_new_rec:
                    DBSession.add(ss)
                LOGGER.info('Storage stat is updated')
                if objStats_details:
                    for eachdetail in objStats_details:
                        actual_size = eachdetail.get('SIZE')
                        used_size = eachdetail.get('USED')
                        unique_path = eachdetail.get('uuid')
                        current_portal = eachdetail.get('CurrentPortal')
                        target = eachdetail.get('Target')
                        state = eachdetail.get('State')
                        lun = eachdetail.get('Lun')
                        storage_disk = DBSession.query(StorageDisks).filter_by(storage_id=storage_id, unique_path=unique_path).first()
                        if storage_disk:
                            if not used_size:
                                used_size = 0
                            if used_size == 0:
                                used_size = actual_size
                            storage_disk.size = float(used_size)
                            storage_disk.actual_size = float(actual_size)
                            storage_disk.state = state
                            storage_disk.lun = lun
                        else:
                            storage_allocated = False
                            self.add_storage_disk(storage_id, actual_size, used_size, unique_path, current_portal, target, state, lun, storage_allocated, grid_manager)
                        all_disks = DBSession.query(StorageDisks).filter_by(storage_id=storage_id)
                        if all_disks:
                            for each_disk in all_disks:
                                disk_found = False
                                if not str(each_disk.unique_path).strip():
                                    DBSession.delete(each_disk)
                                    continue
                                for each_stat in objStats_details:
                                    if str(each_stat.get('uuid')).strip() == str(each_disk.unique_path).strip():
                                        disk_found = True
                                if disk_found == False and each_disk.added_manually == False:
                                    vm_storage_link = DBSession.query(VMStorageLinks).filter_by(storage_disk_id=each_disk.id).first()
                                    if vm_storage_link:
                                        LOGGER.info('The storage disk (' + each_disk.disk_name + ') is in use so that it can not be deleted.')
                                    else:
                                        DBSession.delete(each_disk)
                self.Recompute(defn)


    def is_storage_allocated(self, storage_id):
        returnVal = False
        if storage_id:
            disk = DBSession.query(StorageDisks).filter_by(storage_id=storage_id, storage_allocated=True).first()
            if disk:
                LOGGER.info('Storage (' + str(disk.disk_name) + ') is in use.')
                returnVal = True
        return returnVal


    def remove_storage_disk(self, storage_id):
        if storage_id:
            disks = DBSession.query(StorageDisks).filter_by(storage_id=storage_id)
            for eachdisk in disks:
                DBSession.delete(eachdisk)


    def remove_storage_disks(self, vm_id):
        LOGGER.info('Removing storage disks...')
        vm_config = None
        vm = DBSession.query(VM).filter_by(id=vm_id).first()
        if vm:
            vm_config = vm.get_config()
            for file in vm_config.getDisks():
                filename = file.filename
                disks = DBSession.query(StorageDisks).filter_by(unique_path=filename)
                for eachdisk in disks:
                    if eachdisk.storage_type in StorageManager().STORAGE_FOR_REMOVAL:
                        DBSession.delete(eachdisk)
                        LOGGER.info('Storage disk ' + to_str(eachdisk.unique_path) + ' is removed.')

    def mark_storage_disk(self, storage_disk_id, used):
        storage_disk = DBSession.query(StorageDisks).filter_by(id=storage_disk_id).first()
        if storage_disk:
            storage_disk.storage_allocated = used

    def remove_storage_disk_manually(self, storage_disk_id):
        storage_disk = DBSession.query(StorageDisks).filter_by(id=storage_disk_id).first()
        if storage_disk:
            DBSession.delete(storage_disk)

    def manage_defn_to_groups(self, site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager, csep_id=None):
        result = {}
        if group:
            result = self.manage_defn_to_group(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager)
        else:
            if site:
                site_entity = auth.get_entity(site.id)
                group_entities = auth.get_entities(to_unicode(constants.SERVER_POOL), site_entity)
                for eachgroup in group_entities:
                    group = DBSession.query(ServerGroup).filter_by(id=eachgroup.entity_id).first()
                    result = self.manage_defn_to_group(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager)
            else:
                LOGGER.error('Error: Site is None')
        return result

    def manage_defn_to_group(self, site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager):
        try:
            sync_manager = SyncDef()
            associated = self.is_associated_to_group(group, defn)
            marked_for_association = self.is_present_in_list(group.id, sp_ids)
            if associated == False and marked_for_association == True:
                details = None
                status = constants.OUT_OF_SYNC
                group_entity = auth.get_entity(group.id)
                node_entities = auth.get_entities(to_unicode(constants.MANAGED_NODE), group_entity)
                for eachnode in node_entities:
                    sync_manager.add_node_defn(eachnode.entity_id, defn.id, defType, status, details)
                oos_count = len(node_entities)
                status = constants.OUT_OF_SYNC
                sync_manager.add_group_defn(group.id, defn.id, defType, status, oos_count)
                update_status = True
                sync_manager.sync_defn(defn, site, group, auth, defType, op, def_manager, update_status, errs)
                vm_disks = grid_manager.get_vm_disks_from_pool(auth, group.id)
                storage_disks = DBSession.query(StorageDisks).filter_by(storage_id=defn.id)
                if storage_disks:
                    for eachdisk in storage_disks:
                        grid_manager.matching_disk_on_discover_storage(vm_disks, eachdisk.id)

            if associated == True and marked_for_association == False:
                update_status = True
                op = constants.DETACH
                sync_manager.sync_defn(defn, site, group, auth, defType, op, def_manager, update_status, errs)
                add_mode = False
                sync_manager.disassociate_defn(site, group, auth, defn, defType, add_mode, grid_manager)
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            raise Exception(ex)
            return dict(success=False, msg=to_str(ex).replace("'", ''))

        return dict(success=True, msg='Storage Associated')

    def is_present_in_list(self, str_id, str_ids):
        returnVal = False
        if str_ids != None:
            id_list = str_ids.split(',')
            for eachid in id_list:
                if to_str(eachid) == to_str(str_id):
                    returnVal = True
                    return returnVal
        return returnVal

    def is_associated_to_group(self, group, defn):
        returnVal = False
        group_defn = DBSession.query(SPDefLink).filter_by(group_id=group.id, def_id=defn.id).first()
        if group_defn:
            returnVal = True
        return returnVal

    def calculate_disk_size(self, storage_disk_id, vm_disk_id, disk_size, op, action=None):
        vm_disk = None
        if not disk_size:
            disk_size = 0
        if vm_disk_id:
            vm_disk = DBSession.query(VMDisks).filter_by(id=vm_disk_id).first()
            if vm_disk:
                vm_disk.size = self.convert_to_GB(disk_size)

        if storage_disk_id:
            storage_disk = DBSession.query(StorageDisks).filter_by(id=storage_disk_id).first()
            if storage_disk:
                storage_allocated = storage_disk.storage_allocated
                if op == '+':
                    if vm_disk:
                        if vm_disk.read_write == 'w':
                            storage_allocated = True
                if op == '-':
                    if vm_disk:
                        if vm_disk.read_write == 'w':
                            storage_allocated = False
                if action == 'DETACH' and not storage_allocated:
                    storage_allocated = True            
                storage_disk.storage_allocated = storage_allocated

    def update_size_in_storage_def(self, storage_id, unique_path, used_size):
        LOGGER.info('Updating storage stats...')
        defn = DBSession.query(StorageDef).filter_by(id=storage_id).first()

        if defn:
            stats = defn.stats
            if stats:
                objStats = {}
                objSummary = {}
                objDetailsList = []
                objDetails = []
                objStorage_details = []
                objStorage_details = stats.get('STORAGE_DETAILS')
                objSummary = stats['SUMMARY']
                if not objSummary:
                    LOGGER.error('Error: SUMMARY object is not found. Can not update size in storage_definitions table.')
                    return None
                if float(objSummary.get('TOTAL')) > 0:
                    total_size = self.convert_to_MB(objSummary.get('TOTAL'))

                if not total_size:
                    total_size = 0
                objDetailsList = stats['DETAILS']
                if not objDetailsList:
                    LOGGER.error('Error: DETAILS object is not found. Can not update size in storage_definitions table.')
                    return None
                if objDetailsList:
                    total_used_size = 0
                    for each_disk in objDetailsList:
                        if each_disk.get('uuid'):
                            if each_disk.get('uuid') == unique_path:
                                if float(used_size) > 0:
                                    each_disk['USED'] = self.convert_to_GB(used_size)
                                else:
                                    each_disk['USED'] = 0
                            if float(each_disk.get('USED')) > 0:
                                total_used_size += self.convert_to_MB(each_disk.get('USED'))
    
                            objDetails.append(each_disk)
                    objStats['name'] = stats.get('name')
                    objStats['type'] = stats.get('type')
                    objStats['id'] = stats.get('id')
                    objStats['op'] = stats.get('op')
                    available_size = total_size - total_used_size
                    objSummary['AVAILABLE'] = self.convert_to_GB(available_size)
                    objStats['SUMMARY'] = objSummary
                    objStats['DETAILS'] = objDetails
                    objStats['STORAGE_DETAILS'] = objStorage_details
                defn.stats = objStats

    def convert_to_MB(self, size_in_GB):
        if not size_in_GB:
            size_in_GB = 0
        size_in_GB = float(size_in_GB)
        if size_in_GB > 0:
            size = size_in_GB * 1024
        else:
            size = 0

        size = round(size, 2)
        return size

    def convert_to_GB(self, size_in_MB):
        if not size_in_MB:
            size_in_MB = 0

        size_in_MB = float(size_in_MB)
        if size_in_MB > 0:
            size = size_in_MB / 1024
        else:
            size = 0
        size = round(size, 2)
        return size

    def convert_to_GB_from_Bytes(self, size_in_Bytes):
        GB_BYTES = 1073741824.0
        if not size_in_Bytes:
            size_in_Bytes = 0

        size_in_Bytes = float(size_in_Bytes)
        if size_in_Bytes > 0:
            size = size_in_Bytes / GB_BYTES
        else:
            size = 0
        size = round(size, 2)
        return size

    def convert_to_Bytes_from_GB(self, size_in_GB):
        size = 0
        GB_BYTES = 1073741824.0
        if not size_in_GB:
            size_in_GB = 0
        size_in_GB = float(size_in_GB)
        if size_in_GB > 0:
            size = size_in_GB * GB_BYTES
        else:
            size = 0
        size = int(size)
        return size

    def get_mount_point(self, storage_id=None, defn=None):
        mount_point = ''
        if storage_id and not defn:
            defn = DBSession.query(StorageDef).filter_by(id=storage_id).first()
        if defn:
            con_props = defn.connection_props
            mount_point = con_props.get('mount_point')
        return mount_point

    def add_storage_disk(self, storage_id, actual_size, size, unique_path, current_portal, target, state, lun, storage_allocated, grid_manager, added_manually=False, defn=None, disk_id=None):
        LOGGER.info('Adding storage disk...')
        storage_disk_id = None
        if storage_id:
            mount_point = None
            file_system = None
            storage_type = None
            disk_name = None
            if not defn:
                defn = self.get_defn(storage_id)
            if defn:
                disk_name = defn.name
                storage_type = defn.type
            storage_disk = DBSession.query(StorageDisks).filter_by(unique_path=unique_path).first()
            if storage_disk:
                LOGGER.info('Storage disk record for ' + to_str(unique_path) + ' already present in database.')
                storage_disk_id = storage_disk.id
            else:
                storage_disk = StorageDisks()
                if disk_id:
                    storage_disk_id = disk_id
                else:
                    storage_disk_id = getHexID()
    
                storage_disk.id = storage_disk_id
                storage_disk.storage_id = storage_id
                storage_disk.storage_type = storage_type
                storage_disk.disk_name = disk_name
                storage_disk.mount_point = mount_point
                storage_disk.file_system = file_system
                if not actual_size:
                    actual_size = 0
                if not size:
                    size = 0
    
                storage_disk.actual_size = float(actual_size)
                storage_disk.size = float(size)
                storage_disk.unique_path = unique_path
                storage_disk.current_portal = current_portal
                storage_disk.target = target
                storage_disk.state = state
                storage_disk.lun = lun
                storage_disk.storage_allocated = storage_allocated
                storage_disk.added_manually = added_manually
                DBSession.add(storage_disk)
                LOGGER.info('Storage disk ' + to_str(unique_path) + ' is added')

        return storage_disk_id

    def RemoveScanResult(self, scan_result=None):
        try:
            if scan_result:
                return "{success:true, msg:''}"
            try:
                scan_result = session.get(constants.SCAN_RESULT)
            except Exception as ex:
                info_msg = to_str(ex).replace("'", '')
                LOGGER.info(info_msg)
            if scan_result:
                session[constants.SCAN_RESULT] = None
                session.save()
            return "{success:true, msg:''}"
        except Exception as ex:
            error_msg = to_str(ex).replace("'", '')
            LOGGER.error(error_msg)
            return "{success:false, msg:'" + error_msg + "'}"

    def GetScanResult(self):
        scan_result = None
        scan_result = session.get(constants.SCAN_RESULT)
        return scan_result

    def SaveScanResult(self, storage_id, grid_manager, scan_result=None, site_id=None):
        try:
            added_manually = False
            if not scan_result:
                try:
                    scan_result = session.get(constants.SCAN_RESULT)
                except Exception as ex:
                    info_msg = to_str(ex).replace("'", '')
                    LOGGER.info(info_msg)
            if scan_result:
                success = False
                success = scan_result.get('success')
                if not success:
                    LOGGER.info('Scan is failed. Can not update sizes.')
                    return None
                defn = self.get_defn(storage_id)
                if defn:
                    added_manually = defn.connection_props.get('added_manually')
                    if not added_manually:
                        self.manage_storage_disk(defn.id, grid_manager, scan_result, site_id)
                        LOGGER.info('Storage stats and storage disks are updated.')
                else:
                    LOGGER.info('Storage stats is not updated since storage is not found.')
                return "{success:true, msg:''}"
        except Exception as ex:
            error_msg = to_str(ex).replace("'", '')
            LOGGER.error(error_msg)
            return "{success:false, msg:'" + error_msg + "'}"


    def check_mounting(self, node, defn):
        file_system = None
        mount_point = None
        server = None
        output = 'Success'
        exit_code = 0
        server = defn.connection_props.get('server')
        file_system = defn.connection_props.get('share')
        mount_point = defn.connection_props.get('mount_point')
        LOGGER.info('file_system= ' + to_str(file_system))
        LOGGER.info('mount_point= ' + to_str(mount_point))
        if not file_system or not mount_point:
            return (exit_code, output)
        cmd = os.path.join(self.s_scripts_location, 'scripts', 'check_mounting.sh')
        LOGGER.info('Command= ' + to_str(cmd))
        output,exit_code = node.node_proxy.exec_cmd(cmd)
        LOGGER.info('Exit Code= ' + to_str(exit_code))
        LOGGER.info('Output of script= ' + to_str(output))

        if not exit_code:
            mount_points = []
            mount_points = output.split(',')
            for each_item in mount_points:
                LOGGER.info('each_item ' + to_str(each_item))
                if each_item.strip():
                    fs_mp = []
                    fs_mp = each_item.strip().split('|')
                    LOGGER.info('fs_mp ' + to_str(fs_mp))
                    file_system_with_server = server + ':' + file_system
                    if file_system ==fs_mp[0] and mount_point == fs_mp[1]:
                        output = constants.STORAGE_ALREADY_MOUNTED
                        exit_code = 1
                    elif file_system_with_server == fs_mp[0] and mount_point == fs_mp[1]:
                        output = constants.STORAGE_ALREADY_MOUNTED
                        exit_code = 1
                    elif mount_point == fs_mp[1]:
                        output = 'Mount Point is busy'
                        exit_code = 1

        return (exit_code, output)


    def Recompute_on_remove_vm(self, storage_id_list):
        for storage_id in storage_id_list:
            defn = self.get_defn(storage_id)
            self.Recompute(defn)


    def get_storage_id_list(self, vm_id):
        storage_id_list = []
        if vm_id:
            disks = DBSession.query(StorageDisks, VMDisks, VMStorageLinks).filter(VMDisks.vm_id == vm_id).filter(VMDisks.id == VMStorageLinks.vm_disk_id).filter(StorageDisks.id == VMStorageLinks.storage_disk_id)
            if disks:
                for disk in disks:
                    storage_disk = disk[0]
                    storage_id = storage_disk.storage_id
                    storage_id_list.append(storage_id)
        return storage_id_list


    def lock_ss_row(self, rec):
        rec.locked = True

    def unlock_ss_row(self, rec):
        rec.locked = False

    def Recompute(self, defn):
        LOGGER.info('Recomputing storage stats...')
        start = p_timing_start(STRG_LOGGER, 'Recompute main ')
        if not defn:
            LOGGER.info('Storage definition not found.')
            return None
        site_id = 0
        dc_def = DBSession.query(DCDefLink).filter_by(def_id=defn.id, def_type=constants.STORAGE).first()
        if dc_def:
            site_id = dc_def.site_id
        else:
            sites = DBSession.query(Site)
            site_id = sites[0].id

        total_storage_size_in_DC = self.get_total_storage(site_id, None, constants.SCOPE_DC)
        total_size,used_size = self.get_storage_sizes(defn, site_id)
        self.update_storage_stats_for_datacenter(defn, site_id, total_size, total_storage_size_in_DC)
        LOGGER.info('DC records is populated.')
        self.update_storage_stats_for_serverpool(defn, site_id, total_size, total_storage_size_in_DC)
        LOGGER.info('Server pool records are populated.')
        self.update_storage_stats_for_server(defn, site_id, total_storage_size_in_DC)
        LOGGER.info('Server and VM records are populated.')
        p_timing_end(STRG_LOGGER, start)


    def get_storage_sizes(self, defn, site_id):
        total_size = 0
        used_size = 0
        ss = DBSession.query(Storage_Stats).filter_by(entity_id=site_id, storage_id=defn.id).first()
        if ss:
            total_size = ss.total_size
            used_size = ss.used_size
        if not total_size:
            total_size = 0
        if not used_size:
            used_size = 0

        return (total_size, used_size)


    def update_storage_stats_for_datacenter(self, defn, site_id, total_size, total_storage_size_in_DC):
        start = p_timing_start(STRG_LOGGER, 'Recompute (update_storage_stats_for_datacenter) ')
        storage_used_in_DC = self.get_storage_used_in_site(site_id, defn)
        if not storage_used_in_DC:
            storage_used_in_DC = 0
        storage_allocation_at_DC = self.get_storage_allocation_at_DC(site_id, total_storage_size_in_DC)
        if not storage_allocation_at_DC:
            storage_allocation_at_DC = 0

        context = {}
        context['QUERY_FOR'] = 'DEF'
        context['entity_id'] = site_id
        context['storage_id'] = defn.id
        if total_size:
            context['allocation_in_DC'] = 100 * float(storage_used_in_DC) / float(total_size)
        else:
            context['allocation_in_DC'] = 0

        self.update_storage_stats(context)
        context = {}
        context['QUERY_FOR'] = 'ENTITY'
        context['entity_id'] = site_id
        context['storage_allocation_at_DC'] = storage_allocation_at_DC
        self.update_storage_stats(context)
        p_timing_end(STRG_LOGGER, start)


    def get_total_storage_size_in_DC(self, site_id):
        total_storage_size_in_DC = 0
        rs = DBSession.query(func.sum(StorageDisks.actual_size).label('disk_size')).join((StorageDef, StorageDef.id == StorageDisks.storage_id)).first()
        total_storage_size_in_DC = rs.total_size
        if not total_storage_size_in_DC:
            total_storage_size_in_DC = 0

        return total_storage_size_in_DC


    def update_storage_stats_for_serverpool(self, defn, site_id, total_size, total_storage_size_in_DC):
        start = p_timing_start(STRG_LOGGER, 'Recompute (update_storage_stats_for_serverpool) ')
        storage_used_in_DC = self.get_storages_used_in_site(site_id)
        storage_available = float(total_storage_size_in_DC) - float(storage_used_in_DC)
        context = {}
        context['QUERY_FOR'] = 'ENTITY'
        context['entity_id'] = site_id
        context['storage_avail_in_SP'] = storage_available
        self.update_storage_stats(context)
        sp_def_list = DBSession.query(ServerGroup)
        if sp_def_list:
            for sp_def in sp_def_list:
                group_id = sp_def.id
                storage_used_in_SP = self.get_storage_used_in_group(group_id, defn)
                if not storage_used_in_SP:
                    storage_used_in_SP = 0

                context = {}
                context['QUERY_FOR'] = 'ENTITY'
                context['entity_id'] = group_id
                context['storage_id'] = defn.id
                if total_size:
                    context['allocation_in_SP'] = 100 * float(storage_used_in_SP) / float(total_size)
                else:
                    context['allocation_in_SP'] = 0

                self.update_storage_stats(context)
                storages_used_in_SP = self.get_storages_used_in_group(group_id)
                if not storages_used_in_SP:
                    storages_used_in_SP = 0

                context = {}
                context['QUERY_FOR'] = 'ENTITY'
                context['entity_id'] = group_id
                context['storage_used_in_SP'] = storages_used_in_SP
                context['storage_avail_in_SP'] = storage_available
                self.update_storage_stats(context)
        p_timing_end(STRG_LOGGER, start)

    def update_storage_stats_for_server(self, defn, site_id, total_storage_size_in_DC):
        start = p_timing_start(STRG_LOGGER, 'Recompute (update_storage_stats_for_server) ')
        from stackone.viewModel import Basic
        grid_manager = Basic.getGridManager()
        node_def_list = DBSession.query(ServerDefLink.server_id.label('node_id'), EntityRelation.src_id.label('group_id')).join((EntityRelation, EntityRelation.dest_id == ServerDefLink.server_id)).filter(ServerDefLink.def_id == defn.id).filter(ServerDefLink.def_type == constants.STORAGE).filter(EntityRelation.relation == 'Children')
        if node_def_list.count() <= 0:
            node_def_list = DBSession.query(ManagedNode.id.label('node_id'), EntityRelation.src_id.label('group_id')).join((EntityRelation, EntityRelation.dest_id == ManagedNode.id)).filter(EntityRelation.relation == 'Children')

        if node_def_list:
            for node_def in node_def_list:
                node_id = node_def.node_id
                group_id = node_def.group_id
                strg_usage_for_S = self.get_storage_usage_for_server(node_id)
                total_strg_size_sp = self.get_total_storage(site_id, group_id, constants.SCOPE_SP)
                context = {}
                context['QUERY_FOR'] = 'ENTITY'
                context['entity_id'] = node_id
                if total_storage_size_in_DC:
                    context['allocation_at_S_for_DC'] = 100 * float(strg_usage_for_S) / float(total_storage_size_in_DC)
                else:
                    context['allocation_at_S_for_DC'] = 0
    
                if total_strg_size_sp:
                    context['allocation_at_S_for_SP'] = 100 * float(strg_usage_for_S) / float(total_strg_size_sp)
                else:
                    context['allocation_at_S_for_SP'] = 0
    
                self.update_storage_stats(context)
                entity_rel_list = DBSession.query(EntityRelation).filter_by(src_id=node_id, relation='Children')
        
                for entity_rel in entity_rel_list:
                    self.update_storage_stats_for_vm(entity_rel.dest_id)

        p_timing_end(STRG_LOGGER, start)


    def update_storage_stats_for_vm(self, vm_id):
        start = p_timing_start(STRG_LOGGER, 'Recompute (update_storage_stats_for_vm) ', log_level='INFO')
        shared_size,local_size = self.get_storage_size(vm_id)
        context = {}
        context['QUERY_FOR'] = 'ENTITY'
        context['entity_id'] = vm_id
        context['local_storage_at_VM'] = local_size
        context['shared_storage_at_VM'] = shared_size
        self.update_storage_stats(context)
        p_timing_end(STRG_LOGGER, start)

    def update_storage_stats(self, context):
        ss = None
        entity_id = context.get('entity_id')
        storage_id = context.get('storage_id')

        if storage_id:
            defn = self.get_defn(storage_id)
            if not defn:
                LOGGER.info('Storage definition does not exist so that Storage table can not be updated with the definition.')
                return None
        if context.get('QUERY_FOR') == 'DEF':
            ss = DBSession.query(Storage_Stats).filter_by(entity_id=entity_id, storage_id=storage_id).first()
        elif context.get('QUERY_FOR') == 'ENTITY':
            if storage_id:
                ss = DBSession.query(Storage_Stats).filter_by(entity_id=entity_id, storage_id=storage_id).first()
            else:
                ss = DBSession.query(Storage_Stats).filter_by(entity_id=entity_id, storage_id=None).first()

        if ss:
            if not ss.locked:
                self.lock_ss_row(ss)
                if context.get('entity_id'):
                    ss.entity_id = context.get('entity_id')
                if context.get('storage_id'):
                    ss.storage_id = context.get('storage_id')
        
                if context.get('total_size'):
                    ss.total_size = context.get('total_size')
                else:
                    if context.get('total_size') == 0:
                        ss.total_size = 0
        
                if context.get('used_size'):
                    ss.used_size = context.get('used_size')
                else:
                    if context.get('used_size') == 0:
                        ss.used_size = 0
        
                if context.get('available_size'):
                    ss.available_size = context.get('available_size')
                else:
                    if context.get('available_size') == 0:
                        ss.available_size = 0
        
                if context.get('allocation_in_DC'):
                    ss.allocation_in_DC = context.get('allocation_in_DC')
                else:
                    if context.get('allocation_in_DC') == 0:
                        ss.allocation_in_DC = 0
        
                if context.get('allocation_in_SP'):
                    ss.allocation_in_SP = context.get('allocation_in_SP')
                else:
                    if context.get('allocation_in_SP') == 0:
                        ss.allocation_in_SP = 0
        
                if context.get('storage_used_in_SP'):
                    ss.storage_used_in_SP = context.get('storage_used_in_SP')
                else:
                    if context.get('storage_used_in_SP') == 0:
                        ss.storage_used_in_SP = 0
        
                if context.get('storage_avail_in_SP'):
                    ss.storage_avail_in_SP = context.get('storage_avail_in_SP')
                else:
                    if context.get('storage_avail_in_SP') == 0:
                        ss.storage_avail_in_SP = 0
        
                if context.get('allocation_at_S_for_DC'):
                    ss.allocation_at_S_for_DC = context.get('allocation_at_S_for_DC')
                else:
                    if context.get('allocation_at_S_for_DC') == 0:
                        ss.allocation_at_S_for_DC = 0
        
                if context.get('allocation_at_S_for_SP'):
                    ss.allocation_at_S_for_SP = context.get('allocation_at_S_for_SP')
                else:
                    if context.get('allocation_at_S_for_SP') == 0:
                        ss.allocation_at_S_for_SP = 0
        
                if context.get('local_storage_at_VM'):
                    ss.local_storage_at_VM = context.get('local_storage_at_VM')
                else:
                    if context.get('local_storage_at_VM') == 0:
                        ss.local_storage_at_VM = 0
        
                if context.get('shared_storage_at_VM'):
                    ss.shared_storage_at_VM = context.get('shared_storage_at_VM')
                else:
                    if context.get('shared_storage_at_VM') == 0:
                        ss.shared_storage_at_VM = 0
        
                if context.get('storage_allocation_at_DC'):
                    ss.storage_allocation_at_DC = context.get('storage_allocation_at_DC')
                else:
                    if context.get('storage_allocation_at_DC') == 0:
                        ss.storage_allocation_at_DC = 0
        
                self.unlock_ss_row(ss)
                LOGGER.info('The record is updated.')
    
            else:
                LOGGER.info('The record is locked. So the record can not be updated.')

        else:
            ss = Storage_Stats()
            ss.id = getHexID()
            ss.entity_id = context.get('entity_id')
            ss.storage_id = context.get('storage_id')
            ss.total_size = context.get('total_size')
            ss.used_size = context.get('used_size')
            ss.available_size = context.get('available_size')
            ss.allocation_in_DC = context.get('allocation_in_DC')
            ss.allocation_in_SP = context.get('allocation_in_SP')
            ss.storage_used_in_SP = context.get('storage_used_in_SP')
            ss.storage_avail_in_SP = context.get('storage_avail_in_SP')
            ss.allocation_at_S_for_DC = context.get('allocation_at_S_for_DC')
            ss.allocation_at_S_for_SP = context.get('allocation_at_S_for_SP')
            ss.local_storage_at_VM = context.get('local_storage_at_VM')
            ss.shared_storage_at_VM = context.get('shared_storage_at_VM')
            ss.storage_allocation_at_DC = context.get('storage_allocation_at_DC')
            DBSession.add(ss)
            LOGGER.info('The record is created.')


    def remove_storage_stats(self, def_id, entity_id):
        ss = None
        if def_id:
            ss = DBSession.query(Storage_Stats).filter_by(storage_id=def_id).first()
        else:
            if entity_id:
                ss = DBSession.query(Storage_Stats).filter_by(entity_id=entity_id).first()
        if ss:
            DBSession.delete(ss)


    def get_storage_used_in_site(self, site_id, defn):
        start = p_timing_start(STRG_LOGGER, 'Recompute (get_storage_used_in_site) ', log_level='INFO')
        total_shared_size = 0
        rs = DBSession.query(func.sum(VMDisks.disk_size).label('disk_size')).join((VMStorageLinks, VMStorageLinks.vm_disk_id == VMDisks.id)).join((StorageDisks, StorageDisks.id == VMStorageLinks.storage_disk_id)).join((DCDefLink, DCDefLink.def_id == StorageDisks.storage_id)).filter(DCDefLink.site_id == site_id).filter(DCDefLink.def_id == defn.id).first()
        total_shared_size = rs.disk_size
        if not total_shared_size:
            total_shared_size = 0
        p_timing_end(STRG_LOGGER, start)
        return total_shared_size


    def get_storages_used_in_site(self, site_id):
        start = p_timing_start(STRG_LOGGER, 'Recompute (get_storages_used_in_site) ', log_level='INFO')
        total_shared_size = 0
        rs = DBSession.query(func.sum(VMDisks.disk_size).label('disk_size')).join((VMStorageLinks, VMStorageLinks.vm_disk_id == VMDisks.id)).join((StorageDisks, StorageDisks.id == VMStorageLinks.storage_disk_id)).join((DCDefLink, DCDefLink.def_id == StorageDisks.storage_id)).filter(DCDefLink.site_id == site_id).first()
        total_shared_size = rs.disk_size
        if not total_shared_size:
            total_shared_size = 0
        p_timing_end(STRG_LOGGER, start)
        return total_shared_size


    def get_storage_used_in_group(self, group_id, defn):
        start = p_timing_start(STRG_LOGGER, 'Recompute (get_storage_used_in_group) ', log_level='INFO')
        total_shared_size = 0
        rs = DBSession.query(func.sum(VMDisks.disk_size).label('disk_size')).join((VMStorageLinks, VMStorageLinks.vm_disk_id == VMDisks.id)).join((StorageDisks, StorageDisks.id == VMStorageLinks.storage_disk_id)).join((SPDefLink, SPDefLink.def_id == StorageDisks.storage_id)).filter(SPDefLink.group_id == group_id).filter(SPDefLink.def_id == defn.id).filter(VMDisks.vm_id.in_(DBSession.query(EntityRelation.dest_id).filter(EntityRelation.relation == 'Children').filter(EntityRelation.src_id.in_(DBSession.query(EntityRelation.dest_id).filter(EntityRelation.relation == 'Children').filter(EntityRelation.src_id == group_id))))).first()
        total_shared_size = rs.disk_size
        if not total_shared_size:
            total_shared_size = 0
        p_timing_end(STRG_LOGGER, start)
        return total_shared_size


    def get_storages_used_in_group(self, group_id):
        start = p_timing_start(STRG_LOGGER, 'Recompute (get_storages_used_in_group) ', log_level='INFO')
        total_shared_size = 0
        rs = DBSession.query(func.sum(VMDisks.disk_size).label('disk_size')).join((VMStorageLinks, VMStorageLinks.vm_disk_id == VMDisks.id)).join((StorageDisks, StorageDisks.id == VMStorageLinks.storage_disk_id)).join((SPDefLink, SPDefLink.def_id == StorageDisks.storage_id)).filter(SPDefLink.group_id == group_id).filter(VMDisks.vm_id.in_(DBSession.query(EntityRelation.dest_id).filter(EntityRelation.relation == 'Children').filter(EntityRelation.src_id.in_(DBSession.query(EntityRelation.dest_id).filter(EntityRelation.relation == 'Children').filter(EntityRelation.src_id == group_id))))).first()
        total_shared_size = rs.disk_size
        if not total_shared_size:
            total_shared_size = 0

        p_timing_end(STRG_LOGGER, start)
        return total_shared_size


    def get_storage_usage_for_server(self, node_id):
        start = p_timing_start(STRG_LOGGER, 'Recompute (get_storage_usage_for_server) ', log_level='INFO')
        usage = 0.0
        rs = DBSession.query(func.sum(VMDisks.disk_size).label('disk_size')).join((VMStorageLinks, VMStorageLinks.vm_disk_id == VMDisks.id)).join((StorageDisks, StorageDisks.id == VMStorageLinks.storage_disk_id)).join((ServerDefLink, ServerDefLink.def_id == StorageDisks.storage_id)).filter(ServerDefLink.server_id == node_id).filter(VMDisks.vm_id.in_(DBSession.query(EntityRelation.dest_id).filter(EntityRelation.src_id == node_id).filter(EntityRelation.relation == 'Children'))).first()
        usage = rs.disk_size
        if not usage:
            usage = 0
        p_timing_end(STRG_LOGGER, start)
        return usage


    def get_storage_size(self, vm_id):
        shared_size = 0.0
        local_size = 0.0
        if vm_id:
            disks = DBSession.query(VMDisks, VMStorageLinks).outerjoin((VMStorageLinks, VMDisks.id == VMStorageLinks.vm_disk_id)).filter(VMDisks.vm_id == vm_id)
            if disks:
                for disk in disks:
                    vm_disk = disk[0]
                    vm_storage_link = disk[1]
                    disk_size = vm_disk.disk_size
                    if disk_size:
                        if vm_storage_link:
                            shared_size += disk_size
                        else:
                            local_size += disk_size
        return (shared_size, local_size)


    def get_storage_allocation_at_DC(self, site_id, total_storage_size_in_DC):
        start = p_timing_start(STRG_LOGGER, 'Recompute (get_storage_allocation_at_DC) ')
        storage_allocation_at_DC = 0
        total_shared_size = 0
        rs = DBSession.query(func.sum(VMDisks.disk_size).label('disk_size')).join((VMStorageLinks, VMStorageLinks.vm_disk_id == VMDisks.id)).join((StorageDisks, StorageDisks.id == VMStorageLinks.storage_disk_id)).join((DCDefLink, DCDefLink.def_id == StorageDisks.storage_id)).filter(DCDefLink.site_id == site_id).first()
        total_shared_size = rs.disk_size
        if not total_shared_size:
            total_shared_size = 0

        if not total_storage_size_in_DC:
            total_storage_size_in_DC = 0

        if total_storage_size_in_DC:
            storage_allocation_at_DC = 100 * float(total_shared_size) / float(total_storage_size_in_DC)
        else:
            storage_allocation_at_DC = 0

        p_timing_end(STRG_LOGGER, start)
        return storage_allocation_at_DC


    def get_total_storage(self, site_id, group_id, scope):
        start = p_timing_start(STRG_LOGGER, 'Recompute (get_total_storage) ')
        total_size = 0
        rs = None
        if scope == constants.SCOPE_DC:
            rs = DBSession.query(func.sum(Storage_Stats.total_size).label('total_size')).join((DCDefLink, DCDefLink.def_id == Storage_Stats.storage_id)).filter(DCDefLink.site_id == site_id).first()
        elif scope == constants.SCOPE_SP:
            rs = DBSession.query(func.sum(Storage_Stats.total_size).label('total_size')).join((SPDefLink, SPDefLink.def_id == Storage_Stats.storage_id)).filter(SPDefLink.group_id == group_id).first()

        if rs:
            total_size = rs.total_size
        if not total_size:
            total_size = 0

        p_timing_end(STRG_LOGGER, start)
        return total_size


    def storage_stats_data_upgrade(self):
        upgraded = False
        upgrade_data = DBSession.query(Upgrade_Data).filter_by(name=to_unicode(constants.STORAGE_STATS), version=to_unicode('2.0-2.0.1')).first()
        if upgrade_data:
            upgraded = upgrade_data.upgraded
        if not upgraded:
            LOGGER.info('Data upgrading for storage stats for version 2.0 to 2.0.1...')
            def_list = DBSession.query(StorageDef)

            for defn in def_list:
                LOGGER.info('Recomputing for definition ' + to_str(defn.name))
                self.Recompute(defn)

            upgrade_data = Upgrade_Data()
            upgrade_data.id = to_unicode(getHexID())
            upgrade_data.name = to_unicode(constants.STORAGE_STATS)
            upgrade_data.version = to_unicode('2.0-2.0.1')
            upgrade_data.description = to_unicode('Recomputing storage stats')
            upgrade_data.upgraded = True
            DBSession.add(upgrade_data)
            transaction.commit()
            LOGGER.info('Database for storage stats is upgraded for version 2.0 to 2.0.1.')
        else:
            LOGGER.info('Database for storage stats is already upgraded for version 2.0 to 2.0.1.')


    def get_storage_def_id(self, group_ids):
        def_link = DBSession.query(SPDefLink).filter(SPDefLink.def_type == constants.STORAGE).filter(SPDefLink.group_id.in_(group_ids)).first()
        if def_link:
            return def_link.def_id


    def get_storage_and_node(self, zone=None):
        LOGGER.info('Getting managed node and storage...')
        managed_node = ''
        def_id = ''
        create_flag = False
        delete_flag = False
        def_links = DBSession.query(ServerDefLink).join((ManagedNode, ServerDefLink.server_id == ManagedNode.id)).filter(ManagedNode.maintenance == False)
        for def_link in def_links:
            node = DBSession.query(ManagedNode).filter_by(id=def_link.server_id).first()
            if node and node.is_up():
                if def_link:
                    def_id = def_link.def_id
                    managed_node = node
                    defn = DBSession.query(StorageDef).filter(StorageDef.id == def_id).first()
                    if defn:
                        storage_type = defn.type
                        if storage_type in self.STORAGE_FOR_CREATION:
                            create_flag = True
                        if storage_type in self.STORAGE_FOR_REMOVAL:
                            delete_flag = True
                        break

        return (managed_node, def_id, create_flag, delete_flag)


    def get_common_dir(self):
        LOGGER.info('Getting common directory...')
        image_store_location = tg.config.get('image_store')
        common_dir = tg.config.get('common_dir')
        return os.path.join(image_store_location, common_dir)

    def get_image_store_location(self):
        LOGGER.info('Getting image store location...')
        location = ''
        location = tg.config.get('default_store_location')
        return location

    def execute_create_disk_script(self, context, managed_node=None):
        hex_id = context.get('hex_id')
        create_flag = context.get('create_flag')
        storage_id = context.get('storage_id')
        zone = context.get('zone')
        disk_name = context.get('disk_name')
        unique_path = context.get('disk_name')
        disk_size = context.get('disk_size')
        mode = context.get('mode')
        storage_allocated = context.get('storage_allocated')
        added_manually = context.get('added_manually')
        cms_cloud = context.get('cms_cloud')
        vdc_name = context.get('vdc_name')
        image_store_location = self.get_image_store_location()
        context['image_store_location'] = image_store_location
        common_src = self.get_common_dir()
        if not managed_node or not storage_id:
            managed_node,storage_id,create_flag,delete_flag = self.get_storage_and_node()
        
        preferred_strg_id = context.get('preferred_strg_id')
        if preferred_strg_id:
            storage_id = preferred_strg_id

        LOGGER.info('common_src is ' + to_str(common_src))
        LOGGER.info('managed_node is ' + str(managed_node))
        LOGGER.info('image_store_location is ' + to_str(image_store_location))
        group = None
        storage_type = None
        defn = self.get_defn(storage_id)
        if defn:
            storage_type = defn.type
        defType = constants.STORAGE
        op = constants.CREATE_DISK
        if storage_type in self.STORAGE_FOR_CREATION:
            create_flag = True
        elif storage_type in self.BLOCK_STORAGE:
            create_flag = False

        exit_code = 0
        output = ''
        storage_disk_id = ''
        
        if create_flag:
            LOGGER.info('Create disk flag is True')
            copyToRemote(common_src, managed_node, image_store_location)
            if storage_type in self.STORAGE_FOR_CREATION:
                disk_name = context.get('disk_name')
                if storage_type != constants.LVM:
                    if disk_name.find('.disk.xm')<0:
                        disk_name = to_str(vdc_name) + '_' + to_str(disk_name) + '.disk.xm'
                        unique_path = disk_name
                        context['disk_name'] = disk_name

            if cms_cloud:
                mp = ''
                cp = self.props_to_cmd_param(defn.connection_props)
                if cp:
                    cp_params = cp.split('|')
                    for prm in cp_params:
                        if prm.find('mount_point') >= 0:
                            mp = prm.split('=')[1]

                if mp and disk_name:
                    unique_path = os.path.join(mp, vdc_name, disk_name)
                    context['disk_name'] = unique_path

                disk_size = int(self.convert_to_MB(disk_size))
                context['disk_size'] = disk_size
            exit_code,output = self.exec_script(managed_node, group, defn, defType, op, context)
            LOGGER.info('Disk created successfully.')
            if cms_cloud and storage_type in self.STORAGE_FOR_CREATION:
                grid_manager = None
                storage_disk_id = self.add_storage_disk(storage_id, disk_size, disk_size, unique_path, None, None, None, None, storage_allocated, grid_manager, added_manually, defn)
                if storage_disk_id and hex_id:
                    self.reserve_disk(storage_disk_id, hex_id)
        else:
            LOGGER.info('Create disk flag is False')
            filename,storage_disk_id = self.get_disk_from_pool(storage_id)
            if storage_disk_id and cms_cloud and mode == constants.CREATE_DISK:
                used = True
                self.mark_storage_disk(storage_disk_id, used)
                if storage_disk_id and hex_id:
                    self.reserve_disk(storage_disk_id, hex_id)
        return (exit_code, output, storage_disk_id, storage_id)


    def reserve_disk(self, storage_disk_id, hex_id):
        LOGGER.info('Reserving disk...')
        disk = DBSession.query(StorageDisks).filter_by(id=storage_disk_id).first()
        if disk:
            disk.transient_reservation = hex_id


    def unreserve_disk(self, storage_disk_id):
        LOGGER.info('Unreserving disk...')
        disk = DBSession.query(StorageDisks).filter_by(id=storage_disk_id).first()
        if disk:
            disk.transient_reservation = None



    def get_reserve_disk(self, hex_id):
        LOGGER.info('Getting reserve disk...')
        disk = DBSession.query(StorageDisks).filter_by(transient_reservation=hex_id).first()
        return disk

    def get_disk_from_pool(self, storage_id):
        LOGGER.info('Get disk from pool...')
        filename = ''
        storage_disk_id = ''
        sd = DBSession.query(StorageDisks).filter_by(storage_id=storage_id, storage_allocated=False).first()
        if sd:
            storage_disk_id = sd.id
            filename = sd.unique_path
        else:
            raise Exception('Could not find free storage disk for block storage')

        return (filename, storage_disk_id)


    def execute_remove_disk_script(self, context, managed_node=None):
        hex_id = context.get('hex_id')
        delete_flag = context.get('delete_flag')
        storage_id = context.get('storage_id')
        cms_cloud = context.get('cms_cloud')
        disk_name = context.get('disk_name')
        unique_path = context.get('disk_name')
        mode = context.get('mode')
        image_store_location = self.get_image_store_location()
        context['image_store_location'] = image_store_location
        common_src = self.get_common_dir()
        if not managed_node:
            managed_node,storage_id,create_flag,delete_flag = self.get_storage_and_node()
        LOGGER.info('common_src is ' + to_str(common_src))
        LOGGER.info('managed_node is ' + str(managed_node))
        LOGGER.info('image_store_location is ' + to_str(image_store_location))
        exit_code = 0
        output = ''
        storage_disk_id = ''
        if delete_flag:
            LOGGER.info('Delete disk flag is True')
            copyToRemote(common_src, managed_node, image_store_location)

        storage_id = context.get('storage_id')
        group = None
        storage_type = None
        defn = self.get_defn(storage_id)
        if defn:
            storage_type = defn.type

        defType = constants.STORAGE
        op = constants.REMOVE_DISK
        if cms_cloud:
            storage_disk_id = context.get('storage_disk_id')
            sd = DBSession.query(StorageDisks).filter(StorageDisks.id == storage_disk_id).first()
            if sd:
                unique_path = sd.unique_path
                context['disk_name'] = unique_path
        exit_code,output = self.exec_script(managed_node, group, defn, defType, op, context)
        if storage_disk_id and cms_cloud and mode == constants.REMOVE_DISK:
            used = False
            self.mark_storage_disk(storage_disk_id, used)
        s_disk = None
        if storage_type in self.STORAGE_FOR_REMOVAL and not cms_cloud:
            if storage_disk_id:
                s_disk = DBSession.query(StorageDisks).filter(StorageDisks.id == storage_disk_id).first()
            else:
                s_disk = DBSession.query(StorageDisks).filter_by(unique_path=unique_path).first()

        if s_disk:
            storage_disk_id = s_disk.id
            self.remove_storage_disk_manually(storage_disk_id)

        return (exit_code, output, storage_disk_id)


    def attach_disks(self, context, disk_list):
        LOGGER.info('Attaching disks to VM...')
        from stackone.viewModel import Basic
        grid_manager = Basic.getGridManager()
        if context:
            instance_id = context.get('instance_id')
            volume_id = context.get('volume_id')
            dom = DBSession.query(VM).filter(VM.id == instance_id).first()
        if dom:
            action = 'ATTACH'
            self.update_vm_config(dom, disk_list, action)
            vm_config = dom.get_config()
            managed_node = self.get_parent_node(dom.id)
            if dom.get_state() == VM.RUNNING:
                dom = managed_node.get_dom(dom.name)
                dom.attachDisks(disk_list)

            mode = None
            removed_disk_list = None
            grid_manager.manage_vm_disks(session['auth'], dom.id, managed_node.id, vm_config, mode, removed_disk_list, action)
            s_disk = DBSession.query(StorageDisks).filter_by(id=volume_id).first()
            if s_disk:
                storage_id = s_disk.storage_id
                defn = self.get_defn(storage_id)
                self.Recompute(defn)


    def detach_disks(self, context, disk_list):
        LOGGER.info('Detaching disks to VM...')
        from stackone.viewModel import Basic
        grid_manager = Basic.getGridManager()
        if context:
            instance_id = context.get('instance_id')
            volume_id = context.get('volume_id')
            dom = DBSession.query(VM).filter(VM.id == instance_id).first()

        if dom:
            action = 'DETACH'
            self.update_vm_config(dom, disk_list, action)
            vm_config = dom.get_config()
            managed_node = self.get_parent_node(dom.id)
            if dom.get_state() == VM.RUNNING:
                dom = managed_node.get_dom(dom.name)
                dom.detachDisks(disk_list)
            mode = None
            removed_disk_list = None
            grid_manager.manage_vm_disks(session['auth'], dom.id, managed_node.id, vm_config, mode, removed_disk_list)
            s_disk = DBSession.query(StorageDisks).filter_by(id=volume_id).first()
            if s_disk:
                storage_id = s_disk.storage_id
                defn = self.get_defn(storage_id)
                self.Recompute(defn)


    def get_parent_node(self, dom_id):
        LOGGER.info('Getting parent node for VM...')
        node = None
        entity = DBSession.query(Entity).filter_by(entity_id=dom_id).first()
        if entity:
            node_id = entity.parents[0].entity_id
            node = DBSession.query(ManagedNode).filter_by(id=node_id).first()
        return node

    def update_vm_config(self, dom, disk_list, action):
        LOGGER.info('Updating VM config...')
        if dom:
            vm_config = dom.get_config()
            if vm_config:
                dom_disks = []
                for each_disk in vm_config.getDisks():
                    dom_disks.append(str(each_disk))
                for each_disk in disk_list:
                    each_disk = str(each_disk)
                    if action == 'ATTACH':
                        dom_disks.append(to_str(each_disk))

                    elif action == 'DETACH':
                        try:
                            for dsk in dom_disks:
                                if to_str(dsk).find(to_str(each_disk)) >= 0:
                                    dom_disks.remove(to_str(dsk))
                        except Exception as ex:
                            LOGGER.error(to_str(ex))
                if dom.name:
                    filename = dom.get_config()['config_filename']
                    if filename:
                        vm_config.set_filename(filename)

                vm_config['disk'] = dom_disks
                dom.vm_config = get_config_text(vm_config)
                DBSession.add(dom)
                try:
                    node = self.get_parent_node(dom.id)
                    if node and filename:
                        f = node.node_proxy.open(filename, 'w')
                        lines = get_config_text(vm_config)
                        f.write(lines)
                        f.close()
                        LOGGER.info('vm_config is updated.')
                except Exception as ex:
                    LOGGER.error(to_str(ex))
        

    def remove_defn_dependencies(self, csep_id, defn_id, vm_id):
        pass

    def on_defn_creation(self, auth, **kwargs):
        pass

    def nw_svc_specific_sync(self, auth, node, defn, csep_id, op):
        pass

    def delete_storage_vdc_folders(self, vdc_name):
        def_list = DBSession.query(StorageDef)
        for defn in def_list:
            connection_props = defn.connection_props
            mount_point = ''
            if connection_props:
                if defn.type in self.STORAGE_FOR_CREATION:
                    def_link = DBSession.query(ServerDefLink).filter_by(def_id=defn.id).first()
                    if def_link:
                        node = DBSession.query(ManagedNode).filter_by(id=def_link.server_id).first()
                        if node:
                            mount_point = connection_props.get('mount_point')
                            storage_vdc_folder = os.path.join(mount_point, vdc_name)
                            if node.node_proxy.file_exists(storage_vdc_folder):
                                cmd = 'rm -rf ' + to_str(storage_vdc_folder)
                                node.node_proxy.exec_cmd(cmd)



