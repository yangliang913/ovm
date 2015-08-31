from sqlalchemy.orm import relation
from sqlalchemy import ForeignKey, Column, PickleType, DateTime
from sqlalchemy.schema import Index
from stackone.model.VM import VM, VMDisks, VMStorageLinks, VMDiskManager
from sqlalchemy.types import Integer, Unicode, Boolean, String, Text
from stackone.core.utils.utils import to_unicode, to_str, constants, getHexID
from stackone.model import DeclarativeBase, DBSession
from stackone.model.DBHelper import DBHelper
from stackone.model.Credential import Credential
from stackone.model.Entity import Entity, EntityRelation
from stackone.model.storage import StorageManager
from datetime import datetime, timedelta
from stackone.viewModel import Basic
import logging
import traceback
import calendar
import transaction
import os
import tg
from stackone.model.Backup import BackupManager, SPBackupConfig, SPbackup_VM_list, VMBackupResult, VMBackupDetailResult, SPBackupSetting, Server
LOGGER = logging.getLogger('stackone.model')
class VMRestoreResult(DeclarativeBase):
    __tablename__ = 'vm_restore_results'
    id = Column(Unicode(50), primary_key=True)
    backup_id = Column(Unicode(50))
    vm_id = Column(Unicode(50))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(Unicode(50))
    result = Column(Unicode(500))
    backup_result_id = Column(Unicode(50), ForeignKey('vm_backup_results.id'))
    rel_vrr_bkrid = relation('VMBackupResult', backref='VMRestoreResult')
    def __init__(self):
        pass



Index('vrr_bkid_vid_st', VMRestoreResult.backup_id, VMRestoreResult.vm_id, VMRestoreResult.status)
class VMRestoreDetailResult(DeclarativeBase):
    __tablename__ = 'vm_restore_detail_results'
    id = Column(Unicode(50), primary_key=True)
    result_id = Column(Unicode(50), ForeignKey('vm_restore_results.id'))
    phase = Column(Unicode(100))
    status = Column(Unicode(50))
    details = Column(Unicode(500))
    dt_time = Column(DateTime)
    rel_restore_result_detResult = relation('VMRestoreResult', backref='VMRestoreDetailResult')
    def __init__(self):
        pass



class RestoreManager():
    def __init__(self):
        self.manager = Basic.getGridManager()
        self.storage_manager = StorageManager()
        self.backup_manager = BackupManager()

    def add_vm_restore_result(self, backup_id, vm_id, start_time, end_time, status, result, bkp_result_id=None):
        bkp_result = VMRestoreResult()
        bkp_result.id = getHexID()
        bkp_result.backup_id = backup_id
        bkp_result.vm_id = vm_id
        bkp_result.start_time = start_time
        bkp_result.end_time = end_time
        bkp_result.status = status
        bkp_result.result = result
        bkp_result.backup_result_id = bkp_result_id
        DBSession.add(bkp_result)
        transaction.commit()
        return bkp_result.id

    def update_vm_restore_result(self, result_id, end_time, status, result):
        bkp_result = DBSession.query(VMRestoreResult).filter_by(id=result_id).first()
        if bkp_result:
            if end_time:
                bkp_result.end_time = end_time
            bkp_result.status = status
            bkp_result.result = result
            transaction.commit()

    def get_comment_prefix(self, seq):
        s_seq = None
        if not seq:
            seq = 0
        seq = int(seq) + 1
        s_seq = to_str(seq)
        if len(s_seq) == 1:
            s_seq = '0' + s_seq
        return (seq, s_seq)

    def add_restore_detail_result(self, result_id, phase, status, details, cms_start=False, seq=0, restore_service=None):
        s_seq = seq
        if details:
            seq,s_seq = self.get_comment_prefix(seq)
            bkp_result = VMRestoreDetailResult()
            bkp_result.id = getHexID()
            bkp_result.result_id = result_id
            bkp_result.phase = phase
            bkp_result.status = status
            bkp_result.details = s_seq + '-' + details
            bkp_result.dt_time = datetime.now()
            DBSession.add(bkp_result)
            if not cms_start:
                transaction.commit()
            if restore_service:
                restore_service.seq = seq
        return bkp_result.id

    def get_backupresult_info(self, sp_id, vm_id):
        result = []
        config_list = DBSession.query(SPBackupConfig).filter_by(sp_id=sp_id).all()
        LOGGER.info('##########config_list###########')
        LOGGER.info(config_list)
        for configobj in config_list:
            vm_backup_result_list = DBSession.query(VMBackupResult).filter_by(backup_id=configobj.id, status='Success', vm_id=vm_id).order_by(VMBackupResult.start_time).all()
            LOGGER.info('##########vm_backup_result_list###########')
            LOGGER.info(vm_backup_result_list)
            if vm_backup_result_list:
                last_index = len(vm_backup_result_list) - 1
                last_backup = str(vm_backup_result_list[last_index].start_time)
                location = ''
                if configobj.rel_setting_conf.is_remote:
                    location = str(configobj.rel_setting_conf.backup_server_details['server']) + ':'
                location = 'managednode:'
                location += configobj.rel_setting_conf.backup_destination
                result.append(dict(backupsetup_id=configobj.id, taskname=configobj.name, location=location, last_backup=last_backup, backup_result_id=vm_backup_result_list[last_index].id))
        return result

    def get_vm_backups(self, sp_id, vm_id):
        result = []
        config_list = DBSession.query(SPBackupConfig).filter_by(sp_id=sp_id).all()
        for configobj in config_list:
            vm_backup_result = DBSession.query(VMBackupResult).filter_by(backup_id=configobj.id, status='Success', vm_id=vm_id).order_by(VMBackupResult.start_time.desc()).first()
            if vm_backup_result:
                last_backup = str(vm_backup_result.start_time)
                location = ''
                if configobj.rel_setting_conf.is_remote:
                    location = str(configobj.rel_setting_conf.backup_server_details['server']) + ':'
                location = 'managednode:'
                location += configobj.rel_setting_conf.backup_destination
                configobj.rel_setting_conf.backup_type('Backup Type')
        return result

    def update_vms(self, node, vm_info):
        try:
            dom = DBSession.query(VM).filter_by(name=vm_info.get('name')).first()
            if dom:
                dom.vm_config = vm_info.get('vm_config')
                transaction.commit()
                LOGGER.info('vms table is updated')
        except Exception as ex:
            LOGGER.error('Error: ' + to_str(ex).replace("'", ''))

    def restore_count(self, auth, vm_id):
        info_dict = {}
        info_dict['policy_count'] = 0
        info_dict['restore_count'] = 0
        info_dict['last_restore_id'] = ''
        info_dict['last_backup_id'] = ''
        sp_backup_VM_list = BackupManager().get_SPbackup_VM_list_by_vmid(vm_id)
        if sp_backup_VM_list:
            info_dict['policy_count'] = len(sp_backup_VM_list)
            vm_backup_result_list = DBSession.query(VMBackupResult).filter_by(vm_id=vm_id, status='Success').order_by(VMBackupResult.start_time).all()
            if vm_backup_result_list:
                last_index = len(vm_backup_result_list) - 1
                vm_backup_result_obj = vm_backup_result_list[last_index]
                info_dict['restore_count'] = len(vm_backup_result_list)
                info_dict['last_restore_id'] = vm_backup_result_obj.id
                info_dict['last_backup_id'] = vm_backup_result_obj.backup_id
        return info_dict

    def is_restoring(self, vm_entity_id):
        return_val = False
        vm_backup_result = DBSession.query(VMRestoreResult).filter_by(vm_id=vm_entity_id, status='Running').first()
        if vm_backup_result:
            return_val = True
        return return_val

    def update_restore_status(self, rec):
        sStatus = 'Failed'
        details = 'Restore failed : CMS restarted.'
        rec.status = sStatus
        msg = rec.result
        if msg:
            rec.result = msg + '. ' + details
        rec.result = details
        self.add_restore_detail_result(rec.id, None, sStatus, details, cms_start=True)
        DBSession.add(rec)
        transaction.commit()

    def delete_restore_detail_results(self, result_id, dt_time=None):
        if dt_time:
            DBSession.query(VMRestoreDetailResult).filter(VMRestoreDetailResult.result_id == result_id).filter(VMRestoreDetailResult.dt_time <= dt_time).delete()
        DBSession.query(VMRestoreDetailResult).filter(VMRestoreDetailResult.result_id == result_id).delete()
        LOGGER.info('Restore result details are deleted.')
        transaction.commit()

    def delete_restore_results(self, backup_id, dt_time):
        try:
            DBSession.query(VMRestoreResult).filter(VMRestoreResult.backup_id == backup_id).filter(VMRestoreResult.start_time <= dt_time).delete()
            transaction.commit()
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))

    def delete_restore_single_result(self, result_id):
        try:
            DBSession.query(VMRestoreResult).filter(VMRestoreResult.id == result_id).delete()
            LOGGER.info('VM restore single result is deleted.')
            transaction.commit()
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))

    def get_sp_vm_restore_history(self, auth, node_id, node_type, search_text):
        task_backup_info = {}
        tasklist_info = []
        sp_id_list = []
        vm_id = None
        search_limit = tg.config.get('RESTORE_SEARCH_LIMIT')
        if search_text:
            search_text = to_str(search_text).strip()
            vm = DBSession.query(VM).filter_by(name=search_text).first()
            if vm:
                vm_id = vm.id
        if node_type == constants.DATA_CENTER:
            
            dc_ent = auth.get_entity(node_id)
            sp_ents = auth.get_entities(to_unicode(constants.SERVER_POOL), parent=dc_ent)
            sp_id_list = [sp_ent.entity_id for sp_ent in sp_ents]
        if node_type == constants.SERVER_POOL:
            sp_id_list.append(node_id)

        rec_count = 0
        if sp_id_list:
            for sp_id in sp_id_list:
                sp_bkp_conf_list = DBSession.query(SPBackupConfig).filter_by(sp_id=sp_id).all()
                if sp_bkp_conf_list:
                    for sp_bkp_conf in sp_bkp_conf_list:
                        if search_text:
                            restore_result_obj_list = DBSession.query(VMRestoreResult, VMBackupResult).join((VMBackupResult, VMRestoreResult.backup_result_id == VMBackupResult.id)).filter(VMRestoreResult.backup_id == sp_bkp_conf.id).order_by(VMRestoreResult.start_time).all()
                        restore_result_obj_list = DBSession.query(VMRestoreResult, VMBackupResult).join((VMBackupResult, VMRestoreResult.backup_result_id == VMBackupResult.id)).filter(VMRestoreResult.backup_id == sp_bkp_conf.id).order_by(VMRestoreResult.start_time).all()
                        if restore_result_obj_list:
                            for result_obj in restore_result_obj_list:
                                restore_result_obj = result_obj[0]
                                backup_result_obj = result_obj[1]
                                vm_id = restore_result_obj.vm_id
                                task_info = {}
                                task_info['taskid'] = sp_bkp_conf.id
                                task_info['name'] = sp_bkp_conf.name
                                task_info['vm_id'] = restore_result_obj.vm_id
                                ent = auth.get_entity(restore_result_obj.vm_id)
                                if ent:
                                    task_info['vm'] = ent.name
                                    task_info['server'] = ent.parents[0].name
                                task_info['vm'] = restore_result_obj.vm_name
                                task_info['server'] = restore_result_obj.server_name
                                location = ''
                                exec_context = backup_result_obj.execution_context
                                location = exec_context['SERVER'] + ':' + exec_context['BACKUP_DESTINATION']
                                task_info['location'] = location
                                task_info['starttime'] = restore_result_obj.start_time
                                task_info['endtime'] = restore_result_obj.end_time
                                task_info['backup_size'] = 0
                                task_info['status'] = restore_result_obj.status
                                task_info['errmsg'] = restore_result_obj.result
                                task_info['restore'] = restore_result_obj.id
                                bkp_settings = DBSession.query(SPBackupSetting).filter_by(id=sp_bkp_conf.sp_backup_setting_id).first()
                                task_info['backup_type'] = bkp_settings.backup_type
                                task_info['backup_content'] = bkp_settings.backup_content
                                selective_content = self.backup_manager.get_backup_content(vm_id, bkp_settings.backup_content)
                                selective_content = False
                                if selective_content:
                                    task_info['selective_content'] = True
                                else:
                                    task_info['selective_content'] = False
                                lvm_present = self.backup_manager.has_lvm(vm_id, bkp_settings.backup_type)
                                task_info['lvm_present'] = lvm_present
                                vm_exists = self.backup_manager.vm_exists(vm_id)
                                task_info['vm_exists'] = vm_exists
                                task_info['result_id'] = restore_result_obj.id
                                tasklist_info.append(task_info)
                                rec_count += 1
                                if search_limit:
                                    if int(rec_count) >= int(search_limit):
                                        task_backup_info['rows'] = tasklist_info
                                        return task_backup_info
        task_backup_info['rows'] = tasklist_info
        return task_backup_info


    def get_vm_restore_task_result(self, auth, vm_id):
        task_backup_info = {}
        tasklist_info = []
        msg = " Number of VM's backed up= 2 \n Number of VM backup suceeded = 2\n Number of VM backup failed = 0"
        vmrestore_result_obj_list = DBSession.query(VMRestoreResult, VMBackupResult).join((VMBackupResult, VMRestoreResult.backup_result_id == VMBackupResult.id)).filter(VMRestoreResult.vm_id == vm_id).order_by(VMRestoreResult.start_time).all()
        if vmrestore_result_obj_list:
            for vm_result_obj in vmrestore_result_obj_list:
                vmrestore_result_obj = vm_result_obj[0]
                vmbackup_result_obj = vm_result_obj[1]
                sp_bkp_conf = DBSession.query(SPBackupConfig).filter_by(id=vmrestore_result_obj.backup_id).first()
                if sp_bkp_conf:
                    detailResult_obj_list = DBSession.query(VMRestoreDetailResult).filter_by(result_id=vmrestore_result_obj.id).order_by(VMRestoreDetailResult.details).all()
                    msg2 = ''
                    if detailResult_obj_list:
                        for detailResult_obj in detailResult_obj_list:
                            if detailResult_obj:
                                msg2 += detailResult_obj.details + '\n'
                    task_info = {}
                    task_info['taskid'] = vmrestore_result_obj.id
                    task_info['status'] = vmrestore_result_obj.status
                    task_info['name'] = sp_bkp_conf.name
                    location = ''
                    exec_context = vmbackup_result_obj.execution_context
                    location = exec_context['SERVER'] + ':' + exec_context['BACKUP_DESTINATION']
                    task_info['location'] = location
                    task_info['backup_size'] = 0
                    task_info['starttime'] = vmrestore_result_obj.start_time
                    task_info['endtime'] = vmrestore_result_obj.end_time
                    task_info['errmsg'] = msg2
                    task_info['restore'] = vmrestore_result_obj.id
                    tasklist_info.append(task_info)
        task_backup_info['rows'] = tasklist_info
        return task_backup_info



