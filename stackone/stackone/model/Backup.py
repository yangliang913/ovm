from sqlalchemy.orm import relation
from sqlalchemy import ForeignKey, Column, PickleType, DateTime
from sqlalchemy.schema import Index
from stackone.model.VM import VM, VMDisks
from sqlalchemy.types import Integer, Unicode, Boolean, String, Text
from stackone.core.utils.utils import to_unicode, to_str, constants, getHexID
from stackone.model import DeclarativeBase, DBSession
from stackone.model.ManagedNode import ManagedNode
from stackone.model.DBHelper import DBHelper
from stackone.model.Credential import Credential
from stackone.model.Groups import ServerGroup
from datetime import datetime, timedelta
import time
import calendar
import transaction
import tg
from stackone.viewModel import Basic
from stackone.model.Entity import Entity, EntityType
import logging
import traceback
import calendar
LOGGER = logging.getLogger('stackone.model')
class SPBackupSetting(DeclarativeBase):
    __tablename__ = 'sp_backup_settings'
    id = Column(Unicode(50), primary_key=True)
    backup_type = Column(Unicode(50))
    backup_content = Column(Unicode(50))
    backup_destination = Column(Unicode(50))
    backup_server_details = Column(PickleType)
    server_id = Column(Unicode(50), ForeignKey('servers.id'))
    is_remote = Column(Boolean)
    advance_options = Column(PickleType)
    backup_window = Column(Integer)
    transferMethod = Column(Unicode(50))
    full_backup = Column(Boolean)
    use_tar = Column(Boolean)
    compression_type = Column(Unicode(50))
    includeAll_VM = Column(Boolean)
    transferMethod_options = Column(PickleType)
    def __init__(self):
        pass



class SPBackupSchedule(DeclarativeBase):
    __tablename__ = 'sp_backup_schedules'
    id = Column(Unicode(50), primary_key=True)
    backup_occurance = Column(Unicode(50))
    backup_time_hr = Column(Unicode(50))
    backup_time_min = Column(Unicode(50))
    backup_weekday = Column(Unicode(50))
    backup_weekday_list = Column(PickleType)
    backup_day = Column(Integer)
    backup_monthday_list = Column(PickleType)
    backup_purge_days = Column(Integer)
    next_schedule = Column(DateTime)
    def __init__(self):
        pass



class SPBackupConfig(DeclarativeBase):
    __tablename__ = 'sp_backup_configs'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(100), nullable=False)
    sp_id = Column(Unicode(50), ForeignKey('server_groups.id'))
    num_runs = Column(Integer)
    sp_backup_setting_id = Column(Unicode(50), ForeignKey('sp_backup_settings.id'))
    sp_backup_schedule_id = Column(Unicode(50), ForeignKey('sp_backup_schedules.id'))
    task_id = Column(Integer, ForeignKey('tasks.task_id'))
    rel_setting_conf = relation('SPBackupSetting', backref='SPBackupConfig')
    rel_sch_conf = relation('SPBackupSchedule', backref='SPBackupConfig')
    rel_sg_conf = relation('ServerGroup', backref='SPBackupConfig')
    rel_tsk_conf = relation('Task', backref='SPBackupConfig')
    def __init__(self):
        pass



class SPbackup_VM_list(DeclarativeBase):
    __tablename__ = 'spbackup_vm_list'
    id = Column(Unicode(50), primary_key=True)
    vm_id = Column(Unicode(50))
    backup_id = Column(Unicode(50), ForeignKey('sp_backup_configs.id'))
    allow_backup = Column(Boolean)
    rel_vm_config_list = relation('SPBackupConfig', backref='SPbackup_VM_list')
    def __init__(self):
        pass



class Server(DeclarativeBase):
    __tablename__ = 'servers'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50))
    ssh_port = Column(Integer)
    use_key = Column(Boolean)
    credential = relation(Credential, primaryjoin=id == Credential.entity_id, foreign_keys=[Credential.entity_id], uselist=False, cascade='all, delete, delete-orphan')
    def __init__(self):
        pass



class VMBackupResult(DeclarativeBase):
    __tablename__ = 'vm_backup_results'
    id = Column(Unicode(50), primary_key=True)
    backup_id = Column(Unicode(50))
    vm_id = Column(Unicode(50))
    backup_destination = Column(Unicode(100))
    start_time = Column(DateTime)
    end_time = Column(DateTime)
    status = Column(Unicode(50))
    result = Column(Unicode(500))
    run_number = Column(Integer)
    backup_size = Column(Unicode(50))
    zip_location = Column(Unicode(100))
    zip_name = Column(Unicode(50))
    zip_structure = Column(Unicode(100))
    local_vm_path = Column(Unicode(100))
    vm_name = Column(Unicode(255))
    server_id = Column(Unicode(50))
    server_name = Column(Unicode(255))
    execution_context = Column(PickleType)
    def __init__(self):
        pass



Index('vbr_bkid_rn_vid_st', VMBackupResult.backup_id, VMBackupResult.run_number, VMBackupResult.vm_id, VMBackupResult.status)
class VMBackupDetailResult(DeclarativeBase):
    __tablename__ = 'vm_backup_detail_results'
    id = Column(Unicode(50), primary_key=True)
    result_id = Column(Unicode(50), ForeignKey('vm_backup_results.id'))
    phase = Column(Unicode(100))
    status = Column(Unicode(50))
    details = Column(Unicode(500))
    dt_time = Column(DateTime)
    rel_result_detResult = relation('VMBackupResult', backref='VMBackupDetailResult')
    def __init__(self):
        pass



class BackupManager():
    def __init__(self):
        self.manager = Basic.getGridManager()

    def last_day_of_month(self, year, month):
        pass
    #################error
    def get_external_id(self):
        return DBSession.query(EntityAttribute).filter(EntityAttribute.entity_id == self.entity_id).filter(EntityAttribute.name == 'external_id').first()
        
    def validate_date(self, year, month, day):
        try:
            valid_datetime = datetime(year,month,day)
            return valid_datetime.day
        except ValueError,e:
            lastday = calendar.monthrange(year,month)[1]
            return lastday
    def add_SPbackup_VM_list(self, vm_id, backup_id, allow_backup=True):
        obj_table = SPbackup_VM_list()
        obj_table.id = getHexID()
        obj_table.vm_id = vm_id
        obj_table.backup_id = backup_id
        obj_table.allow_backup = allow_backup
        DBSession.add(obj_table)
        return obj_table.id

    def get_SPbackup_VM_list(self, vm_id, backup_id):
        return_val = None
        return_val = DBSession.query(SPbackup_VM_list).filter_by(vm_id=vm_id, backup_id=backup_id).first()
        return return_val

    def delete_SPbackup_VM_list(self, vm_id, backup_id):
        SPbackup_VM_list_obj = self.get_SPbackup_VM_list(vm_id, backup_id)
        if SPbackup_VM_list_obj:
            DBSession.delete(SPbackup_VM_list_obj)

    def get_SPbackup_VM_list_by_vmid(self, vm_id):
        return_val = None
        return_val = DBSession.query(SPbackup_VM_list).filter_by(vm_id=vm_id).all()
        return return_val

    def get_SPbackup_VM_list_by_backupid(self, backup_id):
        return_val = None
        return_val = DBSession.query(SPbackup_VM_list).filter_by(backup_id=backup_id).all()
        return return_val

    def update_SPbackup_VM_list(self, vm_id, backup_id, allow_backup):
        bkp_result = DBSession.query(SPbackup_VM_list).filter_by(backup_id=backup_id, vm_id=vm_id).first()
        bkp_result.allow_backup = allow_backup

    def add_sp_backup_schedule(self, backup_occurance, backup_time_hr, backup_time_min, backup_weekday_list, backup_weekday, backup_monthday_list, backup_day, backup_purge_days):
        obj_table = SPBackupSchedule()
        obj_table.id = getHexID()
        obj_table.backup_occurance = backup_occurance
        obj_table.backup_time_hr = backup_time_hr
        obj_table.backup_time_min = backup_time_min
        obj_table.backup_weekday = backup_weekday
        obj_table.backup_weekday_list = backup_weekday_list
        obj_table.backup_monthday_list = backup_monthday_list
        obj_table.backup_day = backup_day
        obj_table.backup_purge_days = backup_purge_days
        obj_table.next_schedule = datetime.now()
        curr_time = datetime.now()
        next_time = datetime.now()
        int_backup_hour = int(backup_time_hr)
        int_backup_min = int(backup_time_min)
        DBSession.add(obj_table)
        return obj_table.id

    def add_sp_backup_setting(self, backup_type, backup_content, backup_destination, backup_server_details, is_remote, backup_window, transferMethod, full_backup, includeAll_VM, transferMethod_options, use_tar, compression_type=None):
        name = backup_server_details.get('server')
        username = backup_server_details.get('username')
        password = backup_server_details.get('password')
        ssh_port = backup_server_details.get('ssh_port')
        use_key = backup_server_details.get('use_key')
        cred_type = None
        server_id = self.add_server(name, username, password, ssh_port, use_key, cred_type)
        obj_table = SPBackupSetting()
        obj_table.id = getHexID()
        obj_table.backup_type = backup_type
        obj_table.backup_content = backup_content
        obj_table.backup_destination = backup_destination
        obj_table.backup_server_details = backup_server_details
        obj_table.server_id = server_id
        obj_table.is_remote = is_remote
        obj_table.backup_window = backup_window
        obj_table.transferMethod = transferMethod
        obj_table.full_backup = full_backup
        obj_table.use_tar = use_tar
        obj_table.compression_type = compression_type
        obj_table.includeAll_VM = includeAll_VM
        obj_table.transferMethod_options = transferMethod_options
        DBSession.add(obj_table)
        return obj_table.id

    def add_sp_backup_config(self, name, group_id, setting_id, schedule_id):
        obj_table = SPBackupConfig()
        obj_table.id = getHexID()
        obj_table.name = name
        obj_table.sp_id = group_id
        obj_table.sp_backup_setting_id = setting_id
        obj_table.sp_backup_schedule_id = schedule_id
        obj_table.num_runs = 0
        DBSession.add(obj_table)
        return obj_table.id

    def delete_sp_backup_config(self, conf_id):
        sp_bkp_conf = DBSession.query(SPBackupConfig).filter_by(id=conf_id).first()
        if sp_bkp_conf:
            DBSession.delete(sp_bkp_conf)

    def update_vm_backup_result(self, result_id, end_time, status, result, backup_destination=None, backup_size=None, zip_location=None, zip_name=None, zip_structure=None, local_vm_path=None, execution_context=None):
        bkp_result = DBSession.query(VMBackupResult).filter_by(id=result_id).first()
        if bkp_result:
            if end_time:
                bkp_result.end_time = end_time
            if status:
                bkp_result.status = status
            if result:
                bkp_result.result = result
            if backup_destination:
                bkp_result.backup_destination = backup_destination
            if backup_size:
                bkp_result.backup_size = backup_size
            if zip_location:
                bkp_result.zip_location = zip_location
            if zip_name:
                bkp_result.zip_name = zip_name
            if zip_structure:
                bkp_result.zip_structure = zip_structure
            if local_vm_path:
                bkp_result.local_vm_path = local_vm_path
            if execution_context:
                bkp_result.execution_context = execution_context
            transaction.commit()

    def add_vm_backup_result(self, backup_id, vm_id, backup_destination, start_time, end_time, status, result, run_number, zip_location, zip_name, backup_size='0', vm_name=None, server_id=None, server_name=None, execution_context=None):
        bkp_result = VMBackupResult()
        bkp_result.id = getHexID()
        bkp_result.backup_id = backup_id
        bkp_result.vm_id = vm_id
        bkp_result.backup_destination = backup_destination
        bkp_result.start_time = start_time
        bkp_result.end_time = end_time
        bkp_result.status = status
        bkp_result.result = result
        bkp_result.run_number = run_number
        bkp_result.backup_size = backup_size
        bkp_result.zip_location = zip_location
        bkp_result.zip_name = zip_name
        bkp_result.vm_name = vm_name
        bkp_result.server_id = server_id
        bkp_result.server_name = server_name
        bkp_result.execution_context = execution_context
        DBSession.add(bkp_result)
        transaction.commit()
        return bkp_result.id

    def get_comment_prefix(self, seq):
        s_seq = None
        if not seq:
            seq = 0
        seq = int(seq) + 1
        s_seq = to_str(seq)
        if len(s_seq) == 1:
            s_seq = '0' + s_seq
        return (seq, s_seq)

    def add_backup_detail_result(self, result_id, phase, status, details, seq, cms_start=False):
        s_seq = seq
        if details:
            seq,s_seq = self.get_comment_prefix(seq)
            bkp_result = VMBackupDetailResult()
            bkp_result.id = getHexID()
            bkp_result.result_id = result_id
            bkp_result.phase = phase
            bkp_result.status = status
            bkp_result.details = to_str(s_seq) + '-' + details
            bkp_result.dt_time = datetime.now()
            DBSession.add(bkp_result)
            if not cms_start:
                transaction.commit()
        return seq

    def get_sp_backup_config(self, config_id, group_id=None, policy_name=None):
        return_val = None
        if config_id:
            return_val = DBSession.query(SPBackupConfig).filter_by(id=config_id).first()
        elif group_id and policy_name:
            return_val = DBSession.query(SPBackupConfig).filter_by(sp_id=group_id, name=policy_name).first()
        return return_val

    def get_sp_backup_setting(self, setting_id):
        return_val = None
        return_val = DBSession.query(SPBackupSetting).filter_by(id=setting_id).first()
        return return_val

    def get_sp_backup_schedule(self, schedule_id):
        return_val = None
        return_val = DBSession.query(SPBackupSchedule).filter_by(id=schedule_id).first()
        return return_val

    def get_server(self, server_id):
        return_val = None
        return_val = DBSession.query(Server).filter_by(id=server_id).first()
        return return_val

    def StoreBackup_ConfigRecord(self, auth, group_id, config):
        ent = auth.get_entity(group_id)
        if not auth.has_privilege('ADD_BACKUP_POLICY', ent):
            raise Exception(constants.NO_PRIVILEGE)
        general = config.get('general_object')
        schedule = config.get('schedule_object')
        storage = config.get('storage_object')
        excludeVM = config.get('excludeVM_object')
        policy_name = general['taskname']
        rec = DBSession.query(SPBackupConfig).filter_by(sp_id=group_id, name=policy_name).first()
        if rec:
            raise Exception('Backup Policy with the name ' + to_str(policy_name) + ' already exists in the server pool. So backup policy can not be created.')
        backup_occurance = schedule['scheduleType']
        backup_time_hr = schedule['Hour']
        backup_time_min = schedule['Minute']
        backup_weekday = schedule['Week']
        backup_day = schedule['Month']
        backup_purge_days = schedule['Purge']
        backup_weekday_string = schedule['weekday_stat']
        backup_weekday_list = backup_weekday_string.split(',')
        backup_monthday_string = schedule['monthday_stat']
        backup_monthday_list = backup_monthday_string.split(',')
        schedule_id = self.add_sp_backup_schedule(backup_occurance, backup_time_hr, backup_time_min, backup_weekday_list, backup_weekday, backup_monthday_list, backup_day, backup_purge_days)
        is_remote = storage['RemoteServer']
        server_details = {}
        if is_remote:
            server_details = dict(server = storage['RemoteServerName'], username = storage['User_Name'], password = storage['password'], ssh_port = storage['ssh_port'], use_key = storage['use_key'] )
        backup_type = general['coldBackup']
        backup_content = general['copyRaw']
        backup_destination = storage['Location']
        backup_server_details = server_details
        transferMethod = general['transferMethod']
        full_backup = general['full_backup']
        backup_window = 30
        includeAll_VM = excludeVM['includeAll_VM']
        use_tar = general['use_tar']
        compression_type = general['compression_type']
        transferMethod_options = general['transferMethod_options']
        setting_id = self.add_sp_backup_setting(backup_type, backup_content, backup_destination, backup_server_details, is_remote, backup_window, transferMethod, full_backup, includeAll_VM, transferMethod_options, use_tar, compression_type)
        name = general['taskname']
        config_id = self.add_sp_backup_config(name, group_id, setting_id, schedule_id)
        vm_stat = excludeVM.get('vm_stat')
        for vm_info in vm_stat:
            vm_id = vm_info.get('id')
            if vm_info.get('allow_backup') == 'true':
                self.add_SPbackup_VM_list(vm_id=vm_id, backup_id=config_id, allow_backup=True)
            else:
                self.delete_SPbackup_VM_list(vm_id=vm_id, backup_id=config_id)
        return config_id

    def get_vms_backupInfo_from_pool(self, auth, group_id):
        vmlist = self.manager.get_vms_from_pool(auth, group_id)
        vm_backup_info = {}
        vmlist_info = []
        for vm in vmlist:
            template_info = ''
            os_name = ''
            template_info = vm.get_template_info()
            template = template_info['template_name']
            os_info = vm.get_os_info()
            os_name = os_info['name'] + ' ' + to_str(os_info['version'])
            vm_info = {}
            vm_info['id'] = vm.id
            vm_info['allow_backup'] = True
            vm_info['vm'] = vm.name
            vm_info['template'] = template
            vm_info['os_name'] = os_name
            vmlist_info.append(vm_info)
        vm_backup_info['rows'] = vmlist_info
        return vm_backup_info

    def get_vms_backupInfo_from_list(self, auth, group_id, backup_id):
        vmlist = self.manager.get_vms_from_pool(auth, group_id)
        vm_backup_info = {}
        vmlist_info = []
        for vm in vmlist:
            template_info = ''
            os_name = ''
            template_info = vm.get_template_info()
            template = template_info['template_name']
            os_info = vm.get_os_info()
            os_name = os_info['name'] + ' ' + to_str(os_info['version'])
            vm_info = {}
            vm_info['id'] = vm.id
            SPbackup_VM_list_obj = self.get_SPbackup_VM_list(vm.id, backup_id)
            if SPbackup_VM_list_obj:
                vm_info['allow_backup'] = True
            else:
                vm_info['allow_backup'] = False
            vm_info['vm'] = vm.name
            vm_info['template'] = template
            vm_info['os_name'] = os_name
            vmlist_info.append(vm_info)
        vm_backup_info['rows'] = vmlist_info
        return vm_backup_info

    def get_server_info(self, auth, group_id):
        server_list = self.manager.getNodeList(auth, group_id)
        server_backup_info = {}
        serverlist_info = []
        for server in server_list:
            server_info = {}
            server_info['id'] = server.id
            server_info['server_name'] = server.hostname
            serverlist_info.append(server_info)
        server_backup_info['rows'] = serverlist_info
        return server_backup_info

    def get_backupsetupinfo(self, auth, node_id, node_type):
        result = []
        sp_id_list = []
        if node_type == constants.DATA_CENTER:
            dc_ent = auth.get_entity(node_id)
            sp_ents = auth.get_entities(to_unicode(constants.SERVER_POOL), parent=dc_ent)
            sp_id_list = [sp_ent.entity_id for sp_ent in sp_ents]
        elif node_type == constants.SERVER_POOL:
            sp_id_list.append(node_id)

        if sp_id_list:
            for sp_id in sp_id_list:
                config_list = DBSession.query(SPBackupConfig).filter_by(sp_id=sp_id).all()
                for configobj in config_list:
                    server_pool_name = configobj.rel_sg_conf.name
                    backuptype_str = ''
                    if configobj.rel_setting_conf.backup_type == constants.COLD:
                        backuptype_str = 'Cold Backup'
                    else:
                        backuptype_str = 'Hot Backup'
                    frequency = configobj.rel_sch_conf.backup_occurance
                    next_schedule = ''
                    if configobj.rel_sch_conf.backup_occurance == 'Daily':
                        next_schedule = 'Daily: at ' + configobj.rel_sch_conf.backup_time_hr + 'hr ' + configobj.rel_sch_conf.backup_time_min + 'min'
                    if configobj.rel_sch_conf.backup_occurance == 'Hourly':
                        next_schedule = 'Hourly: at ' + configobj.rel_sch_conf.backup_time_min + 'min'
                    if configobj.rel_sch_conf.backup_occurance == 'Weekly':
                        next_schedule = 'Weekly: on '
                        weekday = {'0':'Mon','1':'Tue','2':'Wed','3':'Thr','4':'Fri','5':'Sat','6':'Sun'}
                        for day in configobj.rel_sch_conf.backup_weekday_list:
                            if day:
                                next_schedule += weekday[day] + ', '
                        next_schedule += ' at ' + configobj.rel_sch_conf.backup_time_hr + 'hr ' + configobj.rel_sch_conf.backup_time_min + 'min'
                    if configobj.rel_sch_conf.backup_occurance == 'Monthly':
                        next_schedule = 'Monthly: on '
                        for day in configobj.rel_sch_conf.backup_monthday_list:
                            if day:
                                next_schedule += day + ', '
                        next_schedule += 'day(s) at ' + configobj.rel_sch_conf.backup_time_hr + 'hr ' + configobj.rel_sch_conf.backup_time_min + 'min'
                    location = ''
                    retention = ''
                    if configobj.rel_setting_conf.is_remote:
                        serverobj = DBHelper().find_by_id(Server, configobj.rel_setting_conf.server_id)
                        location = str(serverobj.name) + ':'
                    else:
                        location = 'Managed Server:'
                    location += configobj.rel_setting_conf.backup_destination
                    retention = configobj.rel_sch_conf.backup_purge_days
                    failures = 0
                    start_time = ''
                    status = ''
                    vm_backup_result_list = DBSession.query(VMBackupResult).filter_by(backup_id=configobj.id, run_number=configobj.num_runs).order_by(VMBackupResult.start_time).all()
            
                    if vm_backup_result_list:
                        start_time = vm_backup_result_list[0].start_time
                        for vm_backup_result in vm_backup_result_list:
                            if vm_backup_result.status == 'Failed':
                                status = 'Failed'
                                failures += 1
                            elif vm_backup_result.status == 'Success':
                                if status != 'Failed':
                                    status = 'Success'
                        last_index = len(vm_backup_result_list) - 1
                        last_backup_status = str(vm_backup_result_list[last_index].status)
                        last_backup_detail = vm_backup_result_list[last_index].result
                    result.append(dict(backupsetup_id=configobj.id, taskname=configobj.name, backup_type=backuptype_str, frequency=frequency, failures=failures, start_time=start_time, status=status, num_runs=configobj.num_runs, retention=retention, location=location, next_schedule=next_schedule, serverpool=server_pool_name))
        return result


    def get_vm_backupsetupinfo(self, sp_id, vm_id, cli=False):
        result = []
        sp_backup_VM_list = self.get_SPbackup_VM_list_by_vmid(vm_id)

        if sp_backup_VM_list:
            for sp_backup_VM_obj in sp_backup_VM_list:
                configobj = self.get_sp_backup_config(sp_backup_VM_obj.backup_id)
                if configobj:
                    backuptype_str = ''
                    if configobj.rel_setting_conf.backup_type == constants.COLD:
                        backuptype_str = 'Cold Backup'
                    else:
                        backuptype_str = 'Hot Backup'
                    frequency = configobj.rel_sch_conf.backup_occurance
                    next_schedule = self.get_backup_schedule(configobj)
                    location = ''
                    retention = ''
                    if configobj.rel_setting_conf.is_remote:
                        serverobj = DBHelper().find_by_id(Server, configobj.rel_setting_conf.server_id)
                        location = str(serverobj.name) + ':'
                    else:
                        location = 'Managed Server:'
                    location += configobj.rel_setting_conf.backup_destination
                    retention = configobj.rel_sch_conf.backup_purge_days
                    failures = 0
                    start_time = ''
                    status = ''
                    last_backup_status = ''
                    last_backup_detail = ''
                    detail_msg = ''
                    vm_backup_result_list = DBSession.query(VMBackupResult).filter_by(backup_id=configobj.id, vm_id=vm_id).order_by(VMBackupResult.start_time).all()
                    if vm_backup_result_list:
                        last_index = len(vm_backup_result_list) - 1
                        last_backup_status = str(vm_backup_result_list[last_index].status)
                        last_backup_detail = vm_backup_result_list[last_index].result
                        start_time = vm_backup_result_list[last_index].start_time
                        status = str(vm_backup_result_list[last_index].status)
                        if vm_backup_result_list[last_index].status == 'Failed':
                            failures += 1
                        detailResult_obj_list = DBSession.query(VMBackupDetailResult).filter_by(result_id=vm_backup_result_list[last_index].id).order_by(VMBackupDetailResult.details).all()
                        if detailResult_obj_list:
                            for detailResult_obj in detailResult_obj_list:
                                if detailResult_obj:
                                    detail_msg += detailResult_obj.details + '\n'
                    if cli == True:
                        Location = ''
                        serverobj = DBHelper().find_by_id(Server, configobj.rel_setting_conf.server_id)
                        if configobj.rel_setting_conf.is_remote:
                            Location = 'Server:' + str(serverobj.name) + '& Location:'
                        else:
                            Location = 'server:localhost & Location:'
                        Location += configobj.rel_setting_conf.backup_destination
                        failures('Failures')
                        result.append({'Policy Name':configobj.name,'Backup Type':backuptype_str,'Location':Location,'Next Schedule':next_schedule,'Last Backup Status':last_backup_status,'Last Backup Detail':last_backup_detail,'Frequency':frequency,'Backup Start Time':start_time,'Number of Backups':configobj.num_runs,'Failures':failures})
                    result.append(dict(backupsetup_id=configobj.id, taskname=configobj.name, backup_type=backuptype_str, retention=retention, location=location, num_runs=configobj.num_runs, next_schedule=next_schedule, last_backup_status=last_backup_status, last_backup_detail=last_backup_detail, frequency=frequency, start_time=start_time, status=status, failures=failures, detail_msg=detail_msg))
        return result


    def delete_backup_policy_task(self, policy_id, group_id):
        LOGGER.info('Deleting backup policy task...')
        from stackone.model.services import TaskCalendar, TaskResult, TaskInterval, Task
        configobj = DBHelper().find_by_id(SPBackupConfig, policy_id)
        task_id = configobj.task_id
        if task_id:
            DBSession.query(TaskResult).filter_by(task_id=task_id).delete()
            DBSession.query(TaskCalendar).filter_by(task_id=task_id).delete()
            configobj.task_id = None
            DBSession.query(Task).filter_by(task_id=task_id).delete()
            LOGGER.info('Backup policy task is deleted')

    def delete_backuprecord(self, auth, backupsetup_id, group_id):
        from stackone.model.services import TaskCalendar, TaskResult, TaskInterval, Task
        ent = auth.get_entity(group_id)
        if not auth.has_privilege('REMOVE_BACKUP_POLICY', ent):
            raise Exception(constants.NO_PRIVILEGE)
        configobj = DBHelper().find_by_id(SPBackupConfig, backupsetup_id)
        task_id = configobj.task_id
        DBSession.query(TaskResult).filter_by(task_id=task_id).delete()
        DBSession.query(TaskCalendar).filter_by(task_id=task_id).delete()
        settingobj = configobj.rel_setting_conf
        scheduleobj = configobj.rel_sch_conf
        DBHelper().delete(scheduleobj)
        DBHelper().delete(configobj)
        DBSession.query(Task).filter_by(task_id=task_id).delete()

    def get_num_runs(self, backupsetup_id):
        result = 0
        config_obj = self.get_sp_backup_config(backupsetup_id)
        if config_obj:
            result = config_obj.num_runs
        return result

    def get_transferMethod_options(self, group_id, backupsetup_id):
        result = []
        config_obj = DBHelper().find_by_id(SPBackupConfig, backupsetup_id)
        if config_obj:
            transferMethod_options = config_obj.rel_setting_conf.transferMethod_options
            if transferMethod_options:
                for eachkey in transferMethod_options:
                    result.append(dict(attribute=eachkey, value=transferMethod_options[eachkey]))
        return result

    def get_backupsetup_details_cli(self, backupsetup_id):
        result = []
        config_obj = DBHelper().find_by_id(SPBackupConfig, backupsetup_id)
        settingobj = config_obj.rel_setting_conf
        scheduleobj = config_obj.rel_sch_conf
        serverobj = DBHelper().find_by_id(Server, settingobj.server_id)
        if config_obj.rel_setting_conf.is_remote:
            serverobj = DBHelper().find_by_id(Server, config_obj.rel_setting_conf.server_id)
            location = str(serverobj.name) + ':'
        else:
            location = 'localhost:'
        location += config_obj.rel_setting_conf.backup_destination
        vmnames = []
        backups_vmlists = DBSession.query(SPbackup_VM_list).filter(SPbackup_VM_list.backup_id == config_obj.id).all()
        for backupvm in backups_vmlists:
            vm = DBSession.query(VM).filter_by(id=backupvm.vm_id).first()
            vmnames.append(vm.name)
        next_schedule = self.get_backup_schedule(config_obj)
        category = ''
        if settingobj.full_backup == True:
            category = 'Full Backup'
        else:
            category = 'Disk Backup'
        result.append({'Policyname':config_obj.name,'Backup Type':settingobj.backup_type,'Category':category,'Schedule':next_schedule,'Backup Destination':location,'Virtual Machines':vmnames})
        return result

    def get_backup_schedule(self, config_obj):
        next_schedule = ''
        if config_obj.rel_sch_conf.backup_occurance == 'Daily':
            next_schedule = 'Daily: at ' + config_obj.rel_sch_conf.backup_time_hr + 'hr ' + config_obj.rel_sch_conf.backup_time_min + 'min'
        if config_obj.rel_sch_conf.backup_occurance == 'Hourly':
            next_schedule = 'Hourly: at ' + config_obj.rel_sch_conf.backup_time_min + 'min'
        if config_obj.rel_sch_conf.backup_occurance == 'Weekly':
            next_schedule = 'Weekly: on '
            weekday = {'0':'Mon','1':'Tue','2':'Wed','3':'Thr','4':'Fri','5':'Sat','6':'Sun'}
            for day in config_obj.rel_sch_conf.backup_weekday_list:
                if day:
                    next_schedule += weekday[day] + ', '
            next_schedule += ' at ' + config_obj.rel_sch_conf.backup_time_hr + 'hr ' + config_obj.rel_sch_conf.backup_time_min + 'min'
        if config_obj.rel_sch_conf.backup_occurance == 'Monthly':
            next_schedule = 'Monthly: on '
            for day in config_obj.rel_sch_conf.backup_monthday_list:
                if day:
                    next_schedule += day + ', '
            next_schedule += 'day(s) at ' + config_obj.rel_sch_conf.backup_time_hr + 'hr ' + config_obj.rel_sch_conf.backup_time_min + 'min'
        return next_schedule

    def get_backupsetup_details(self, backupsetup_id):
        result = []
        config_obj = DBHelper().find_by_id(SPBackupConfig, backupsetup_id)
        settingobj = config_obj.rel_setting_conf
        scheduleobj = config_obj.rel_sch_conf
        weekday_dict = {}
        serverobj = DBHelper().find_by_id(Server, settingobj.server_id)
        server_details = {}
        if serverobj:
            server_details = {'server':serverobj.name,'username':serverobj.credential.cred_details['username'],'password':serverobj.credential.cred_details['password'],'ssh_port':serverobj.ssh_port,'use_key':serverobj.use_key}
        result.append(dict(backupsetup_id=config_obj.id, taskname=config_obj.name, backup_occurance=scheduleobj.backup_occurance, backup_time_hr=scheduleobj.backup_time_hr, backup_time_min=scheduleobj.backup_time_min, backup_weekday=scheduleobj.backup_weekday, backup_weekday_list=scheduleobj.backup_weekday_list, backup_monthday_list=scheduleobj.backup_monthday_list, backup_day=scheduleobj.backup_day, backup_purge_days=scheduleobj.backup_purge_days, backup_type=settingobj.backup_type, backup_content=settingobj.backup_content, transferMethod=settingobj.transferMethod, full_backup=settingobj.full_backup, backup_destination=settingobj.backup_destination, backup_server_details=server_details, is_remote=settingobj.is_remote, advance_options=settingobj.advance_options, backup_window=settingobj.backup_window, includeAll_VM=settingobj.includeAll_VM, use_tar=settingobj.use_tar, compression_type=settingobj.compression_type))
        return result

    def updateSPTaskRecord(self, auth, group_id, config, backupsetup_id):
        ent = auth.get_entity(group_id)
        if not auth.has_privilege('UPDATE_BACKUP_POLICY', ent):
            raise Exception(constants.NO_PRIVILEGE)
        config_obj = DBHelper().find_by_id(SPBackupConfig, backupsetup_id)
        settingobj = config_obj.rel_setting_conf
        scheduleobj = config_obj.rel_sch_conf

        if config_obj:
            general = config.get('general_object')
            schedule = config.get('schedule_object')
            storage = config.get('storage_object')
            excludeVM = config.get('excludeVM_object')
            vm_stat = excludeVM.get('vm_stat')
            settingobj.includeAll_VM = excludeVM.get('includeAll_VM')
    
            if excludeVM.get('includeAll_VM'):
                for vm_info in vm_stat:
                    vm_id = vm_info.get('id')
                    if self.get_SPbackup_VM_list(vm_id=vm_id, backup_id=backupsetup_id) == None:
                        self.add_SPbackup_VM_list(vm_id=vm_id, backup_id=backupsetup_id, allow_backup=True)
            else:
                for vm_info in vm_stat:
                    vm_id = vm_info.get('id')
                    if vm_info.get('allow_backup') == 'true':
                        SPbackup_VM_obj = self.get_SPbackup_VM_list(vm_id=vm_id, backup_id=backupsetup_id)
                        if not SPbackup_VM_obj:
                            self.add_SPbackup_VM_list(vm_id=vm_id, backup_id=backupsetup_id, allow_backup=True)
                    else:
                        self.delete_SPbackup_VM_list(vm_id=vm_id, backup_id=backupsetup_id)
            scheduleobj.backup_occurance = schedule.get('scheduleType')
            scheduleobj.backup_time_hr = schedule.get('Hour')
            scheduleobj.backup_time_min = schedule.get('Minute')
            scheduleobj.backup_weekday = schedule.get('Week')
            scheduleobj.backup_day = schedule.get('Month')
            scheduleobj.backup_purge_days = schedule.get('Purge')
            backup_weekday_string = schedule.get('weekday_stat')
            scheduleobj.backup_weekday_list = backup_weekday_string.split(',')
            backup_monthday_string = schedule.get('monthday_stat')
            scheduleobj.backup_monthday_list = backup_monthday_string.split(',')
            settingobj.is_remote = storage['RemoteServer']
            server_details = {}
            if settingobj.is_remote:
                server_details = {'server':storage['RemoteServerName'],'username':storage['User_Name'],'password':storage['password'],'ssh_port':storage['ssh_port'],'use_key':storage['use_key']}
                name = server_details.get('server')
                username = server_details.get('username')
                password = server_details.get('password')
                ssh_port = server_details.get('ssh_port')
                use_key = server_details.get('use_key')
                cred_type = None
                self.update_server(settingobj.server_id, name, username, password, ssh_port, use_key, cred_type)
            settingobj.backup_type = general['coldBackup']
            settingobj.backup_content = general['copyRaw']
            settingobj.backup_destination = storage['Location']
            settingobj.backup_server_details = server_details
            settingobj.transferMethod = general['transferMethod']
            settingobj.full_backup = general['full_backup']
            settingobj.backup_window = 30
            settingobj.use_tar = general['use_tar']
            settingobj.compression_type = general['compression_type']
            settingobj.transferMethod_options = general['transferMethod_options']
            config_obj.name = general['taskname']
            config_obj.sp_id = group_id


    def get_sp_vm_backup_history(self, auth, node_id, node_type, search_text):
        task_backup_info = {}
        tasklist_info = []
        sp_id_list = []
        vm_id = None
        search_limit = tg.config.get('BACKUP_SEARCH_LIMIT')
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
                            backup_result_obj_list = DBSession.query(VMBackupResult).filter_by(backup_id=sp_bkp_conf.id, vm_id=vm_id).order_by(VMBackupResult.start_time).all()
                        else:
                            backup_result_obj_list = DBSession.query(VMBackupResult).filter_by(backup_id=sp_bkp_conf.id).order_by(VMBackupResult.start_time).all()
                        if backup_result_obj_list:
                            for backup_result_obj in backup_result_obj_list:
                                vm_id = backup_result_obj.vm_id
                                task_info = {}
                                task_info['taskid'] = sp_bkp_conf.id
                                task_info['name'] = sp_bkp_conf.name
                                task_info['vm_id'] = backup_result_obj.vm_id
                                ent = auth.get_entity(backup_result_obj.vm_id)
                                if ent:
                                    task_info['vm'] = ent.name
                                    task_info['server'] = ent.parents[0].name
                                else:
                                    task_info['vm'] = backup_result_obj.vm_name
                                    task_info['server'] = backup_result_obj.server_name
                                location = ''
                                exec_context = backup_result_obj.execution_context
                                location = exec_context['SERVER'] + ':' + exec_context['BACKUP_DESTINATION']
                                task_info['location'] = location
                                task_info['starttime'] = backup_result_obj.start_time
                                task_info['endtime'] = backup_result_obj.end_time
                                task_info['backup_size'] = backup_result_obj.backup_size
                                task_info['status'] = backup_result_obj.status
                                task_info['errmsg'] = backup_result_obj.result
                                task_info['restore'] = backup_result_obj.id
                                bkp_settings = DBSession.query(SPBackupSetting).filter_by(id=sp_bkp_conf.sp_backup_setting_id).first()
                                task_info['backup_type'] = bkp_settings.backup_type
                                task_info['backup_content'] = bkp_settings.backup_content
                                selective_content = self.get_backup_content(vm_id, bkp_settings.backup_content)
                                if selective_content:
                                    task_info['selective_content'] = True
                                else:
                                    task_info['selective_content'] = False
                                lvm_present = self.has_lvm(vm_id, bkp_settings.backup_type)
                                task_info['lvm_present'] = lvm_present
                                vm_exists = self.vm_exists(vm_id)
                                task_info['vm_exists'] = vm_exists
                                task_info['result_id'] = backup_result_obj.id
                                tasklist_info.append(task_info)
                                rec_count += 1
                                if search_limit:
                                    if int(rec_count) >= int(search_limit):
                                        task_backup_info['rows'] = tasklist_info
                                        return task_backup_info
        task_backup_info['rows'] = tasklist_info
        return task_backup_info


    def get_sp_backup_task_result(self, auth, group_id):
        task_backup_info = {}
        tasklist_info = []
        sp_bkp_conf_list = DBSession.query(SPBackupConfig).filter_by(sp_id=group_id).all()

        if sp_bkp_conf_list:
            for sp_bkp_conf in sp_bkp_conf_list:
                location = ''
                if sp_bkp_conf.rel_setting_conf.is_remote:
                    serverobj = DBHelper().find_by_id(Server, sp_bkp_conf.rel_setting_conf.server_id)
                    location = str(serverobj.name) + ':'
                else:
                    location = 'Managed Server:'
                location += sp_bkp_conf.rel_setting_conf.backup_destination
                for run_number in range(1, sp_bkp_conf.num_runs + 1):
                    backup_result_obj_list = DBSession.query(VMBackupResult).filter_by(backup_id=sp_bkp_conf.id, run_number=run_number).order_by(VMBackupResult.start_time).all()
        
                    if backup_result_obj_list:
                        task_info = {}
                        task_info['taskid'] = sp_bkp_conf.id
                        task_info['location'] = location
                        start_time = datetime.max
                        end_time = datetime.min
                        count_success = 0
                        count_failure = 0
                        failedvmlist = ''
                        SucessfulvmList = ''
                        msg = ''
                        vm_message = ''
                        for backup_result in backup_result_obj_list:
                            905
                            if backup_result:
                                prev_start_time = start_time
                                start_time = backup_result.start_time
                                prev_end_time = end_time
                                end_time = backup_result.end_time
                                if end_time:
                                    if prev_end_time:
                                        if prev_end_time>end_time:
                                            end_time = prev_end_time
                                if prev_start_time < start_time:
                                    start_time = prev_start_time
                                task_info['node_id'] = backup_result.vm_id
                                dom = self.manager.get_dom(auth, backup_result.vm_id)
                        
                                if dom:
                                    if backup_result.status == 'Success':
                                        count_success += 1
                                        SucessfulvmList = SucessfulvmList + to_str(dom.name) + '\n'
                                    if backup_result.status == 'Failed':
                                        count_failure += 1
                                        failedvmlist = failedvmlist + to_str(dom.name) + '\n'
                                    if backup_result.end_time:
                                        delta = backup_result.end_time - backup_result.start_time
                                    else:
                                        delta = backup_result.start_time - backup_result.start_time
                                    if backup_result.status == 'Success':
                                        vm_message += to_str(dom.name) + ' backup process started at ' + str(backup_result.start_time) + ' and finished at ' + str(backup_result.end_time) + ' \n' + 'With current status { ' + backup_result.result + ' }\n \n'
                                    if backup_result.status == 'Running':
                                        vm_message += to_str(dom.name) + ' backup process started at ' + str(backup_result.start_time) + ' and is still running\n With current status { ' + backup_result.result + ' }\n \n'
                                    if backup_result.status == 'Failed':
                                        vm_message += to_str(dom.name) + ' backup process started at ' + str(backup_result.start_time) + ' and stop at ' + str(backup_result.end_time) + ' \nWith current status { ' + backup_result.result + ' }\n \n'
                            
                            msg += vm_message
                        if count_failure > 0:
                            task_info['status'] = 'Failed'
                        else:
                            if count_success > 0:
                                task_info['status'] = 'Success'
                            else:
                                task_info['status'] = 'Running'
                        task_info['backup_size'] = backup_result.backup_size
                        task_info['name'] = sp_bkp_conf.name
                        task_info['starttime'] = start_time
                        task_info['endtime'] = end_time
                        task_info['errmsg'] = msg
                        tasklist_info.append(task_info)
        task_backup_info['rows'] = tasklist_info
        return task_backup_info


    def get_vm_backup_task_result(self, auth, vm_id):
        task_backup_info = {}
        tasklist_info = []
        msg = " Number of VM's backed up= 2 \n Number of VM backup suceeded = 2\n Number of VM backup failed = 0"
        vmbackup_result_obj_list = DBSession.query(VMBackupResult).filter_by(vm_id=vm_id).order_by(VMBackupResult.start_time).all()
        if vmbackup_result_obj_list:
            for vmbackup_result_obj in vmbackup_result_obj_list:
                sp_bkp_conf = DBSession.query(SPBackupConfig).filter_by(id=vmbackup_result_obj.backup_id).first()
                if sp_bkp_conf:
                    detailResult_obj_list = DBSession.query(VMBackupDetailResult).filter_by(result_id=vmbackup_result_obj.id).order_by(VMBackupDetailResult.details).all()
                    msg2 = ''
                    if detailResult_obj_list:
                        for detailResult_obj in detailResult_obj_list:
                            if detailResult_obj:
                                msg2 += detailResult_obj.details + '\n'
                    task_info = {}
                    task_info['taskid'] = vmbackup_result_obj.id
                    task_info['result_id'] = vmbackup_result_obj.id
                    task_info['vm_id'] = vm_id
                    task_info['status'] = vmbackup_result_obj.status
                    task_info['name'] = sp_bkp_conf.name
                    vm_entity = auth.get_entity(vm_id)
                    if vm_entity:
                        m_node_name = vm_entity.parents[0].name + ':'
                    else:
                        m_node_name = ''
                    location = ''
                    exec_context = vmbackup_result_obj.execution_context
                    location = exec_context['SERVER'] + ':' + exec_context['BACKUP_DESTINATION']
                    task_info['location'] = location
                    task_info['backup_size'] = vmbackup_result_obj.backup_size
                    task_info['starttime'] = vmbackup_result_obj.start_time
                    task_info['endtime'] = vmbackup_result_obj.end_time
                    task_info['errmsg'] = msg2
                    task_info['restore'] = vmbackup_result_obj.id
                    tasklist_info.append(task_info)
        task_backup_info['rows'] = tasklist_info
        return task_backup_info

    def get_backupConfig_of_sp(self, auth, group_id, vm_id=None):
        task_backup_info = {}
        tasklist_info = []
        sp_bkp_conf_list = DBSession.query(SPBackupConfig).filter_by(sp_id=group_id).all()
        if sp_bkp_conf_list:
            for sp_bkp_conf in sp_bkp_conf_list:
                if sp_bkp_conf.rel_setting_conf.backup_type == constants.COLD:
                    backup_type = 'Cold Backup'
                else:
                    backup_type = 'Hot Backup'
                frequency = sp_bkp_conf.rel_sch_conf.backup_occurance
                allow_backup = True
                if vm_id:
                    SPbackup_VM_list_obj = self.get_SPbackup_VM_list(vm_id, sp_bkp_conf.id)
                    if SPbackup_VM_list_obj:
                        allow_backup = True
                    else:
                        allow_backup = False
                task_info = {}
                task_info['backup_id'] = sp_bkp_conf.id
                task_info['allow_backup'] = allow_backup
                task_info['backup_type'] = backup_type
                task_info['frequency'] = frequency
                task_info['retention_days'] = sp_bkp_conf.rel_sch_conf.backup_purge_days
                task_info['backup_all'] = sp_bkp_conf.rel_setting_conf.includeAll_VM
                task_info['name'] = sp_bkp_conf.name
                tasklist_info.append(task_info)
        task_backup_info['rows'] = tasklist_info
        return task_backup_info

    def get_vm_backup_result(self, result_id):
        rec = DBSession.query(VMBackupResult).filter_by(id=result_id).first()
        return rec

    def add_server(self, name, username, password, ssh_port, use_key, cred_type):
        try:
            server = Server()
            id = getHexID()
            server.id = id
            server.name = name
            if not ssh_port:
                ssh_port = 22
            server.ssh_port = int(ssh_port)
            server.use_key = use_key
            if not username:
                username = ''
            if not password:
                password = ''
            server.credential = Credential(id, '', username=username, password=password)
            DBSession.add(server)
            DBSession.flush()
        except Exception as ex:
            LOGGER.error('Error: ' + to_str(ex).replace("'", ''))
            raise ex
        return server.id

    def update_server(self, server_id, name, username, password, ssh_port, use_key, cred_type):
        server = DBSession.query(Server).filter_by(id=server_id).first()
        if server:
            server.name = name
            server.credential.cred_details['username'] = username
            server.credential.cred_details['password'] = password
            server.ssh_port = ssh_port
            server.use_key = use_key

    def add_entity_type(self):
        try:
            et = DBSession.query(EntityType).filter_by(name='REMOTE_SERVER').first()
            if not et:
                e = EntityType()
                e.name = 'REMOTE_SERVER'
                e.display_name = 'Remote Server'
                e.created_date = datetime.now
                DBSession.add(e)
        except Exception as e:
            raise e

    def add_entity(self, entity_id):
        try:
            et = DBSession.query(EntityType).filter_by(name='REMOTE_SERVER').first()
            if et:
                e = DBSession.query(Entity).filter_by(name='Remote Server').first()
                if not e:
                    e = Entity()
                    e.name = 'Remote Server'
                    e.created_date = datetime.now
                    e.entity_id = entity_id
                    e.type_id = et.id
                    DBSession.add(e)
        except Exception as e:
            raise e

    def get_zip_location(self, result_id):
        zip_location = ''
        zip_name = ''
        zip_structure = ''
        vm_backup_result = DBSession.query(VMBackupResult).filter_by(id=result_id).first()
        if vm_backup_result:
            zip_location = vm_backup_result.zip_location
            if vm_backup_result.zip_name:
                zip_name = vm_backup_result.zip_name
            else:
                zip_name = ''
            if vm_backup_result.zip_structure:
                zip_structure = vm_backup_result.zip_structure
            else:
                zip_structure = ''
            if vm_backup_result.local_vm_path:
                local_vm_path = vm_backup_result.local_vm_path
            else:
                local_vm_path = ''
        LOGGER.info('zip_location=' + to_str(zip_location))
        LOGGER.info('zip_name=' + to_str(zip_name))
        LOGGER.info('zip_structure=' + to_str(zip_structure))
        LOGGER.info('local_vm_path=' + to_str(local_vm_path))
        return (zip_location, zip_name, zip_structure, local_vm_path)

    def get_individual_sp_backup_task_history(self, auth, backup_id):
        task_backup_info = {}
        tasklist_info = []
        sp_bkp_conf = self.get_sp_backup_config(backup_id)

        #[NODE: 33]
        if sp_bkp_conf:
            location = ''
            if sp_bkp_conf.rel_setting_conf.is_remote:
                serverobj = DBHelper().find_by_id(Server, sp_bkp_conf.rel_setting_conf.server_id)
                location = str(serverobj.name) + ':'
            else:
                location = 'managednode:'
            location += sp_bkp_conf.rel_setting_conf.backup_destination
            for run_number in range(1, sp_bkp_conf.num_runs + 1):
                backup_result_obj_list = DBSession.query(VMBackupResult).filter_by(backup_id=sp_bkp_conf.id, run_number=run_number).order_by(VMBackupResult.start_time).all()
    
                #[NODE: 214]
                if backup_result_obj_list:
                    task_info = {}
                    task_info['taskid'] = sp_bkp_conf.id
                    task_info['location'] = location
                    start_time = datetime.max
                    end_time = datetime.min
                    count_success = 0
                    count_failure = 0
                    failedvmlist = ''
                    SucessfulvmList = ''
                    msg = ''
                    vm_message = ''
                    for backup_result in backup_result_obj_list:
                        #[NODE: 317]
                        if backup_result:
                            prev_start_time = start_time
                            start_time = backup_result.start_time
                            prev_end_time = end_time
                            end_time = backup_result.end_time
                    
                            #[NODE: 354]
                            if end_time:
                    
                            #[NODE: 361]
                                if prev_end_time:
                                    if prev_end_time>end_time:
                                        end_time = prev_end_time
                            if prev_start_time < start_time:
                                start_time = prev_start_time
                            task_info['node_id'] = backup_result.vm_id
                            dom = self.manager.get_dom(auth, backup_result.vm_id)
                            if backup_result.status == 'Success':
                                count_success += 1
                                if dom:
                                    SucessfulvmList = SucessfulvmList + to_str(dom.name) + '\n'
                            if backup_result.status == 'Failed':
                                count_failure += 1
                                if dom:
                                    failedvmlist = failedvmlist + to_str(dom.name) + '\n'
                            if backup_result.end_time:
                                delta = backup_result.end_time - backup_result.start_time
                            else:
                                delta = backup_result.start_time - backup_result.start_time
                            if backup_result.status == 'Success':
                                if dom:
                                    vm_message += to_str(dom.name) + ' backup process started at ' + str(backup_result.start_time) + ' and finished at ' + str(backup_result.end_time) + ' \n' + 'With current status { ' + backup_result.result + ' }\n \n'
                            if backup_result.status == 'Running':
                                if dom:
                                    vm_message += to_str(dom.name) + ' backup process started at ' + str(backup_result.start_time) + ' and is still running\n With current status { ' + backup_result.result + ' }\n \n'
                    
                            if backup_result.status == 'Failed':
                                if dom:
                                    vm_message += to_str(dom.name) + ' backup process started at ' + str(backup_result.start_time) + ' and stop at ' + str(backup_result.end_time) + ' \nWith current status { ' + backup_result.result + ' }\n \n'
                        msg += vm_message
                        if count_failure > 0:
                            task_info['status'] = 'Failed'
                        else:
                            if count_success > 0:
                                task_info['status'] = 'Success'
                            else:
                                task_info['status'] = 'Running'
                        task_info['backup_size'] = backup_result.backup_size
                        task_info['name'] = sp_bkp_conf.name
                        task_info['starttime'] = backup_result.start_time
                        task_info['endtime'] = backup_result.end_time
                        task_info['errmsg'] = msg
                        tasklist_info.append(task_info)

        task_backup_info['rows'] = tasklist_info
        return task_backup_info


    def build_storage_stats(self, vm_id):
        storage_stats = {}
        disk_stats = {}
        vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
        for each_disk in vm_disks:
            disk = {}
            disk['DEV_TYPE'] = each_disk.dev_type
            disk['IS_LOCAL'] = each_disk.is_shared
            disk['DISK_SIZE'] = each_disk.disk_size
            disk['DISK_NAME'] = each_disk.disk_name
            disk['STORAGE_DISK_ID'] = None
            if not each_disk.backup_content:
                disk['BACKUP_CONTENT'] = None
            else:
                disk['BACKUP_CONTENT'] = each_disk.backup_content
        disk['VM_ID'] = each_disk.vm_id
        disk['DISK_ID'] = each_disk.id
        disk['READ_WRITE'] = each_disk.read_write
        disk['DISK_TYPE'] = each_disk.disk_type
        disk['FILE_SYSTEM'] = each_disk.file_system
        disk['VM_MEMORY'] = each_disk.vm_memory
        disk_stats[each_disk.disk_name] = disk
        storage_stats['DISK_STATS'] = disk_stats
        storage_stats['LOCAL_ALLOCATION'] = None
        storage_stats['SHARED_ALLOCATION'] = None
        return storage_stats

    def update_vm_config_file(self, vm_id, config_file):
        import fileinput
        storage_stats = self.build_storage_stats(vm_id)
        for line in fileinput.FileInput(config_file, inplace=1):
            if line.find('STORAGE_STATS =') == 0:
                line = 'STORAGE_STATS = ' + to_str(storage_stats)

    def get_backup_content(self, vm_id, backup_content, file_path=None):
        LOGGER.info('Getting selective contents...')
        selective_content = None
        if backup_content == constants.BKP_CONTENT:
            if file_path:
                vm_disk = DBSession.query(VMDisks).filter_by(vm_id=vm_id, disk_name=file_path).first()
                if vm_disk:
                    selective_content = vm_disk.backup_content
            else:
                vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
                for each_disk in vm_disks:
                    selective_content = each_disk.backup_content
                    if selective_content:
                        break
        LOGGER.info('Selective contents are ' + to_str(selective_content))
        return selective_content


    def has_lvm(self, vm_id, backup_type):
        lvm_present = False
        if backup_type == constants.HOT:
            vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
            for each_disk in vm_disks:
                disk_type = each_disk.disk_type
                if disk_type == 'lvm':
                    lvm_present = True
                    break
        return lvm_present

    def vm_exists(self, vm_id):
        vm_exists = False
        vm = DBSession.query(VM).filter_by(id=vm_id).first()
        if vm:
            vm_exists = True
        return vm_exists

    def total_backupsize_calcu(self, backupsize_list):
        total_backupsize = 0.0
        total_backupsize_str = '0'

        #[NODE: 18]
        if backupsize_list:
            for backupsize in backupsize_list:
                if backupsize:
                    try:
                        total_backupsize += float(backupsize)
                    except Exception as ex:
                        LOGGER.error('Error: ' + to_str(ex))

        total_backupsize_str = to_str(total_backupsize)
        return total_backupsize_str


    def sp_backup_summary(self, auth, node_id, node_type):
        info_list = []
        sp_id_list = []
        backupsize_list = []
        num_backup_policies = 0
        num_backup_failures = 0
        num_not_backup_vm = 0
        total_backupsize = 0
        twodays_back = datetime.now() - timedelta(days=7)

        if node_type == constants.DATA_CENTER:
            dc_ent = auth.get_entity(node_id)
            sp_ents = auth.get_entities(to_unicode(constants.SERVER_POOL), parent=dc_ent)
            sp_id_list = [sp_ent.entity_id for sp_ent in sp_ents]

        #[NODE: 167]
        if node_type == constants.SERVER_POOL:
            sp_id_list.append(node_id)

        #[NODE: 207]
        if sp_id_list:
            for sp_id in sp_id_list:
                config_list = DBSession.query(SPBackupConfig).filter_by(sp_id=sp_id).all()
                if config_list:
                    num_backup_policies += len(config_list)
                    for configobj in config_list:
                        vm_backup_result_list = DBSession.query(VMBackupResult).filter_by(backup_id=configobj.id).all()
                        if vm_backup_result_list:
                            for vm_backup_result_obj in vm_backup_result_list:
                                backupsize_list.append(vm_backup_result_obj.backup_size)
                                if vm_backup_result_obj.start_time > twodays_back:
                                    if vm_backup_result_obj.status == 'Failed':
                                        num_backup_failures += 1
                sp_ent = auth.get_entity(sp_id)
                server_ents = auth.get_entities(to_unicode(constants.MANAGED_NODE), parent=sp_ent)
                for server_ent in server_ents:
                    vm_ents = auth.get_entities(to_unicode(constants.DOMAIN), parent=server_ent)
                    for vm_ent in vm_ents:
                        backedup_vm = self.get_SPbackup_VM_list_by_vmid(vm_ent.entity_id)
                        if not backedup_vm:
                            num_not_backup_vm += 1
                total_backupsize = self.total_backupsize_calcu(backupsize_list)
        info_list.append(dict(name='Backup Policies', value=num_backup_policies))
        info_list.append(dict(name='Backup Failures <br/>(Last 7 days)', value=num_backup_failures))
        info_list.append(dict(name='Virtual Machines without backup policy', value=num_not_backup_vm))
        info_list.append(dict(name='Total Backup Size (GB)', value=total_backupsize))
        return info_list


    def vm_backup_summary(self, auth, vm_id):
        info_list = []
        backupsize_list = []
        num_backup_policies = 0
        num_backup_failures = 0
        total_backupsize = 0
        twodays_back = datetime.now() - timedelta(days=7)
        sp_backup_VM_list = self.get_SPbackup_VM_list_by_vmid(vm_id)
        if sp_backup_VM_list:
            num_backup_policies = len(sp_backup_VM_list)
        vm_backup_result_list = DBSession.query(VMBackupResult).filter_by(vm_id=vm_id).all()

        if vm_backup_result_list:
            for vm_backup_result_obj in vm_backup_result_list:
                backupsize_list.append(vm_backup_result_obj.backup_size)
                if vm_backup_result_obj.start_time > twodays_back:
                    if vm_backup_result_obj.status == 'Failed':
                        num_backup_failures += 1
        total_backupsize = self.total_backupsize_calcu(backupsize_list)
        info_list.append(dict(name='Backup Policies', value=num_backup_policies))
        info_list.append(dict(name='Backup Failures <br/>(Last 7 days)', value=num_backup_failures))
        info_list.append(dict(name='Total Backup Size (GB)', value=total_backupsize))
        return info_list


    def sp_backup_failure(self, auth, node_id, node_type):
        info_list = []
        sp_id_list = []

        if node_type == constants.DATA_CENTER:
            dc_ent = auth.get_entity(node_id)
            sp_ents = auth.get_entities(to_unicode(constants.SERVER_POOL), parent=dc_ent)
            sp_id_list = [sp_ent.entity_id for sp_ent in sp_ents]
        if node_type == constants.SERVER_POOL:
            sp_id_list.append(node_id)

        if sp_id_list:
            for sp_id in sp_id_list:
                sp_ent = auth.get_entity(sp_id)
                server_ents = auth.get_entities(to_unicode(constants.MANAGED_NODE), parent=sp_ent)
                for server_ent in server_ents:
                    vm_ents = auth.get_entities(to_unicode(constants.DOMAIN), parent=server_ent)
                    for vm_ent in vm_ents:
                        config_list = DBSession.query(SPBackupConfig).filter_by(sp_id=sp_id).all()
                        if config_list:
                            for configobj in config_list:
                                info_dict = {}
                                vm_backup_result_list = DBSession.query(VMBackupResult).filter_by(backup_id=configobj.id, vm_id=vm_ent.entity_id).order_by(VMBackupResult.start_time.desc()).all()
                                last_success = ''
                                last_fail = ''
                                num_fail = 0
                                if vm_backup_result_list:
                                    for vm_backup_result_obj in vm_backup_result_list:
                                        if vm_backup_result_obj.status == 'Success':
                                            last_success = vm_backup_result_obj.start_time
                                            break
                                        elif vm_backup_result_obj.status == 'Failed':
                                            num_fail += 1
                                            last_fail = vm_backup_result_obj.start_time
                                    if num_fail != 0 :
                                        info_dict['node_id'] = vm_ent.entity_id
                                        info_dict['last_success'] = last_success
                                        info_dict['num_fail'] = num_fail
                                        info_dict['vm'] = vm_ent.name
                                        info_dict['policy'] = configobj.name
                                        info_list.append(info_dict)
        return info_list


    def backup_report(self, auth, backup_id, num_runs):
        info_list = []
        vm_backup_result_list = DBSession.query(VMBackupResult).filter_by(backup_id=backup_id, run_number=num_runs).all()
        if vm_backup_result_list:
            for vm_backup_result_obj in vm_backup_result_list:
                vm_ent = auth.get_entity(vm_backup_result_obj.vm_id)
                info_dict = {}
                info_dict['node_id'] = vm_ent.entity_id
                info_dict['vm'] = vm_ent.name
                info_dict['status'] = vm_backup_result_obj.status
                info_dict['message'] = vm_backup_result_obj.result
                detail_result = ''
                detailResult_obj_list = DBSession.query(VMBackupDetailResult).filter_by(result_id=vm_backup_result_obj.id).order_by(VMBackupDetailResult.dt_time).all()
                for detailResult_obj in detailResult_obj_list:
                    detail_result += detailResult_obj.details
                    detail_result += '\n'
                info_dict['detail_result'] = detail_result
                info_list.append(info_dict)
        return info_list

    def non_backupVM(self, auth, node_id, node_type):
        info_list = []
        sp_id_list = []
        if node_type == constants.DATA_CENTER:
            dc_ent = auth.get_entity(node_id)
            sp_ents = auth.get_entities(to_unicode(constants.SERVER_POOL), parent=dc_ent)
            sp_id_list = [sp_ent.entity_id for sp_ent in sp_ents]
        if node_type == constants.SERVER_POOL:
            sp_id_list.append(node_id)

        if sp_id_list:
            for sp_id in sp_id_list:
                vmlist = self.manager.get_vms_from_pool(auth, sp_id)
                for vm in vmlist:
                    SPbackup_VM_list_obj = self.get_SPbackup_VM_list_by_vmid(vm.id)
                    if not SPbackup_VM_list_obj:
                        os_name = ''
                        os_info = vm.get_os_info()
                        if os_info:
                            os_name = os_info['name'] + ' ' + to_str(os_info['version'])
                        template_info = vm.get_template_info()
                        template = template_info['template_name']
                        info_dict = {}
                        info_dict['group_id'] = sp_id
                        info_dict['vm_id'] = vm.id
                        info_dict['vm_name'] = vm.name
                        info_dict['template'] = template
                        info_dict['os_name'] = os_name
                        info_list.append(info_dict)
        return info_list


    def Add_vm_to_backuplist(self, auth, vm_id, backup_id_list):
        print backup_id_list
        backup_id_list = backup_id_list.split(',')
        if backup_id_list:
            for backup_id in backup_id_list:
                self.add_SPbackup_VM_list(vm_id=vm_id, backup_id=backup_id, allow_backup=True)

    def BackedUpVMlist(self, auth, group_id):
        info_list = []
        vmlist = self.manager.get_vms_from_pool(auth, group_id)
        for vm in vmlist:
            SPbackup_VM_list_obj = self.get_SPbackup_VM_list_by_vmid(vm.id)
            if SPbackup_VM_list_obj:
                ent = auth.get_entity(vm.id)
                server = ''
                if ent:
                    server = ent.parents[0].name
                os_name = ''
                os_info = vm.get_os_info()
                if os_info:
                    os_name = os_info['name'] + ' ' + to_str(os_info['version'])
                template_info = vm.get_template_info()
                template = template_info['template_name']
                info_dict = {}
                info_dict['group_id'] = group_id
                info_dict['vm_id'] = vm.id
                info_dict['vm_name'] = vm.name
                info_dict['os_name'] = os_name
                info_dict['template'] = template
                info_dict['server'] = server
                info_list.append(info_dict)
        return info_list

    def backup_policy_count(self, auth, vm_id):
        info_dict = {}
        info_dict['policy_count'] = 0
        info_dict['first_backup_id'] = ''
        sp_backup_VM_list = self.get_SPbackup_VM_list_by_vmid(vm_id)
        if sp_backup_VM_list:
            info_dict['policy_count'] = len(sp_backup_VM_list)
            info_dict['first_backup_id'] = sp_backup_VM_list[0].backup_id
        return info_dict

    def is_backing_up(self, vm_entity_id):
        return_val = False
        vm_backup_result = DBSession.query(VMBackupResult).filter_by(vm_id=vm_entity_id, status='Running').first()
        if vm_backup_result:
            return_val = True
        return return_val

    def get_string_aligned(self, text, size=15.0):
        space_count = 0
        if size > len(text):
            space_count = size - len(text)
            text = self.prefix_spaces(text, space_count)
        return text

    def prefix_spaces(self, text, space_count):
        i = 0
        while i <= space_count:
            text = ' ' + text
            i += 1
        return text

    def update_backup_status(self, rec):
        sStatus = 'Failed'
        details = 'Backup failed : CMS restarted.'
        rec.status = sStatus
        msg = rec.result
        if msg:
            rec.result = msg + '. ' + details
        else:
            rec.result = details
        self.add_backup_detail_result(rec.id, None, sStatus, details, 500, cms_start=True)
        DBSession.add(rec)
        transaction.commit()

    def update_task_id(self, config_id, task_id):
        config = self.get_sp_backup_config(config_id)
        if config:
            config.task_id = task_id

    def parse_details(self, output, op):
        disk_details = {}
        if output:
            counter = 0
            for i in output.splitlines():
                partition_name = ''
                d = {}
                if not i:
                    continue
                i = i.strip()
                if i.find(op) != 0:
                    continue
                for j in i.split('|'):
                    nameAndValue = j.lstrip().split('=')
                    d[nameAndValue[0]] = nameAndValue[1]
                    if op == 'PART_DETAILS' and to_str(nameAndValue[0]).strip() == 'PART_NAME':
                        partition_name = nameAndValue[1]
                del d[op]
                counter += 1
                if op == 'PART_DETAILS':
                    disk_details[partition_name] = d
                elif op == 'VG_DETAILS':
                    disk_details['VG' + to_str(counter)] = d
                elif op == 'LV_DETAILS':
                    disk_details['LV' + to_str(counter)] = d
        return disk_details

    def get_managed_node(self, auth, vm_id):
        vm_entity = auth.get_entity(vm_id)
        node_id = vm_entity.parents[0].entity_id
        node = self.manager.getNode(auth, node_id)
        node.connect()
        return (node_id, node)

    def get_remote_node(self, objSettings):
        try:
            server = objSettings['server']
            username = objSettings['user_name']
            password = objSettings['password']
            ssh_port = objSettings['ssh_port']
            if not ssh_port:
                ssh_port = 22
            remote_node = ManagedNode(server, ssh_port=int(ssh_port), username=username, password=password, isRemote=True, helper=None, use_keys=False, address=None)
            remote_node.connect()
        except Exception as ex:
            LOGGER.error(to_str(ex))
            if to_str(ex) == 'timed out':
                err_desc = 'We are getting timed out error while creating remote node. Remote node might be down.' + '\nError Description: ' + to_str(ex)
                LOGGER.info('We are getting timed out error while creating remote node. Remote node might be down.')
                raise Exception(err_desc)
            else:
                raise Exception(ex)
        return remote_node

    def purge_backup(self, auth, group_id, backup_config_id, restore_manager):
        LOGGER.info('Purging backup...')
        backup_config = self.get_sp_backup_config(backup_config_id)
        backup_id = backup_config_id
        purge_interval = backup_config.rel_sch_conf.backup_purge_days
        cutoff_date = datetime.now() + timedelta(days=-int(purge_interval))
        backup_result_list = DBSession.query(VMBackupResult).filter(VMBackupResult.backup_id == backup_id).filter(VMBackupResult.start_time <= cutoff_date).all()
        node = None
        sp_bkp_settings = self.get_sp_backup_setting(backup_config.sp_backup_setting_id)
        if sp_bkp_settings.is_remote == True:
            serverobj = self.get_server(sp_bkp_settings.server_id)
            if serverobj:
                objSettings = {}
                objSettings['server'] = serverobj.name
                objSettings['user_name'] = serverobj.credential.cred_details['username']
                objSettings['password'] = serverobj.credential.cred_details['password']
                objSettings['ssh_port'] = serverobj.ssh_port
                node = self.get_remote_node(objSettings)
        for each_backup_result in backup_result_list:
            result_id = each_backup_result.id
            execution_context = each_backup_result.execution_context
            if not node:
                vm_id = execution_context.get('VM_ID')
                node_id,node = self.get_managed_node(auth, vm.id)
            backup_dest_dir_dic = execution_context.get('BACKUP_DEST_DIR_STRUCTURE')
            backup_date_path = backup_dest_dir_dic.get('backup_date_path')
            path_params_list = backup_date_path.split('/')
            date_folder_name = path_params_list[len(path_params_list) - 1]
            cutoff_date_param_list = to_str(cutoff_date).split(' ')
            cutoff_date_tmp = cutoff_date_param_list[0]
            time_part = cutoff_date_param_list[1]
            time_part_list = time_part.split('.')
            time_part = time_part_list[0]
            date_format_string = '%Y-%m-%d %H:%M:%S'
            date_folder_name = time.strptime(date_folder_name + ' ' + to_str(time_part), date_format_string)
            cutoff_date_tmp = time.strptime(cutoff_date_tmp + to_str(time_part), date_format_string)
            if date_folder_name <= cutoff_date_tmp:
                if backup_date_path != '/':
                    cmd = 'rm -rf ' + to_str(backup_date_path)
                    LOGGER.info('Command=' + to_str(cmd))
                    node.node_proxy.exec_cmd(cmd)
            restore_manager.delete_restore_detail_results(result_id, cutoff_date)
            self.delete_backup_detail_results(result_id, cutoff_date)
        restore_manager.delete_restore_results(backup_id, cutoff_date)
        self.delete_backup_results(backup_id, cutoff_date)

    def delete_backup_detail_results(self, result_id, dt_time=None):
        if dt_time:
            DBSession.query(VMBackupDetailResult).filter(VMBackupDetailResult.result_id == result_id).filter(VMBackupDetailResult.dt_time <= dt_time).delete()
        else:
            DBSession.query(VMBackupDetailResult).filter(VMBackupDetailResult.result_id == result_id).delete()
        LOGGER.info('Backup result details are deleted.')
        transaction.commit()

    def delete_backup_results(self, backup_id, dt_time):
        try:
            DBSession.query(VMBackupResult).filter(VMBackupResult.backup_id == backup_id).filter(VMBackupResult.start_time <= dt_time).delete()
            transaction.commit()
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex).replace("'", ''))

    def delete_backup_single_result(self, result_id):
        try:
            DBSession.query(VMBackupResult).filter(VMBackupResult.id == result_id).delete()
            LOGGER.info('VM backup single result is deleted.')
            transaction.commit()
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex).replace("'", ''))

    def delete_vm_from_bkp_policy(self, vm_id, policy_id):
        rec = DBSession.query(SPbackup_VM_list).filter_by(vm_id=vm_id, backup_id=policy_id).first()
        if rec:
            DBSession.delete(rec)

    def delete_vms_from_bkp_policy(self, auth, node_id, group_id):
        vm_list = self.manager.get_node_doms(auth, node_id)
        policy_list = DBSession.query(SPBackupConfig).filter_by(sp_id=group_id)
        for vm in vm_list:
            for policy in policy_list:
                self.delete_vm_from_bkp_policy(vm.id, policy.id)

    def purge_single_backup(self, auth, result_id, restore_manager):
        LOGGER.info('Purging single backup...')
        each_backup_result = DBSession.query(VMBackupResult).filter(VMBackupResult.id == result_id).first()
        if not each_backup_result:
            err_desc = 'Virtual Machine backup result not found.'
            LOGGER.info(err_desc)
            raise Exception(err_desc)
            return None
        backup_config = self.get_sp_backup_config(each_backup_result.backup_id)
        backup_id = each_backup_result.backup_id
        node = None
        sp_bkp_settings = self.get_sp_backup_setting(backup_config.sp_backup_setting_id)
        if sp_bkp_settings:
            if sp_bkp_settings.is_remote == True:
                serverobj = self.get_server(sp_bkp_settings.server_id)
                if serverobj:
                    objSettings = {}
                    objSettings['server'] = serverobj.name
                    objSettings['user_name'] = serverobj.credential.cred_details['username']
                    objSettings['password'] = serverobj.credential.cred_details['password']
                    objSettings['ssh_port'] = serverobj.ssh_port
                    node = self.get_remote_node(objSettings)

        execution_context = each_backup_result.execution_context
        if not node:
            vm_id = execution_context.get('VM_ID')
            node_id,node = self.get_managed_node(auth, vm_id)
        backup_dest_dir_dic = execution_context.get('BACKUP_DEST_DIR_STRUCTURE')
        backup_date_path = ''
        if backup_dest_dir_dic:
            backup_date_path = backup_dest_dir_dic.get('backup_date_path')
        if backup_date_path and backup_date_path != '/':
            cmd = 'rm -rf ' + to_str(backup_date_path)
            LOGGER.info('Command=' + to_str(cmd))
            node.node_proxy.exec_cmd(cmd)
            LOGGER.info('Physical backup folder is deleted.')
        cutoff_date = None
        restore_manager.delete_restore_detail_results(result_id, cutoff_date)
        cutoff_date = None
        self.delete_backup_detail_results(result_id, cutoff_date)
        restore_manager.delete_restore_single_result(result_id)
        self.delete_backup_single_result(result_id)




