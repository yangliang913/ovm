import pylons
import simplejson as json
from stackone.controllers.ControllerBase import ControllerBase
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
import stackone.core.utils.constants
#from stackone.controllers.XMLRPC.BackupXMLRPCController import BackupXMLRPCController
constants = stackone.core.utils.constants
import logging
import tg
import os
from datetime import datetime
LOGGER = logging.getLogger('stackone.controllers')
from stackone.model.Authorization import AuthorizationService
from pylons.controllers.util import forward
from pylons.controllers import XMLRPCController
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.model.Backup import BackupManager
from stackone.viewModel.BackupService import BackupService

class BackupController(ControllerBase):
    tc = TaskCreator()
    backup_manager = BackupManager()
    backup_service = BackupService()
        
    def Add_vm_to_backuplist(self, vm_id, backup_id_list):
        
        result=None
        self.authenticate()
        try:
            self.backup_manager.Add_vm_to_backuplist(session['auth'],vm_id,backup_id_list)
        except Exception, ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'msg':True}

    def BackedUpVMlist(self,sp_id,_dc=None):
        
        try:
            self.authenticate()
            info=self.backup_manager.BackedUpVMlist(session['auth'],sp_id)
            return dict(success=True,info=info)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))

    def StoreBackup_ConfigRecord(self, group_id, config):
        
        result = None
        self.authenticate()
        config = json.loads(config)
        try:
            schedule = config.get('schedule_object')
            schedule_type = schedule['scheduleType']
            config_id = self.backup_manager.StoreBackup_ConfigRecord(session['auth'],group_id,config)
            if config_id and schedule_type!= 'Manual':
                task_id=self.submit_sp_backup_task(group_id,config_id)
                self.backup_service.update_task_id(config_id,task_id)
            else:
                LOGGER.info('Schedule type is Manual so we are not submitting backup policy task...')

        except Exception ,ex:
            print_traceback()
            return  {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'msg':True}
    #lbz
    def backupVMNow(self, vm_id, config_id, cli=False):
        
        self.authenticate()
        try:
            if cli == True:
                backup = self.backup_service.get_backup(config_id)
                if backup:
                    backup.num_runs += 1#lbz
                    result=self.tc.backup_vm_task(session['auth'],vm_id,backup.id)
                    return {'success':True,'msg':result}
                return {'success':False,'msg':'The backup '+config_id+' does not exists'}
            else:
                config_obj=self.backup_manager.get_sp_backup_config(config_id)
                if config_obj:
                    config_obj.num_runs += 1#lbz
                self.tc.backup_vm_task(session['auth'],vm_id,config_id)
                return "{success: true,msg: 'Task submitted.'}"
        except Exception ,ex:
            err_desc = to_str(ex).replace("'",'')
            err_desc = err_desc.strip()
            LOGGER.error(err_desc)
            return "{success: false,msg: '"+err_desc+"'}"
                
    def backup_policy_count(self, vm_id):
        
        self.authenticate()
        result = {}
        try:
            result = self.backup_manager.backup_policy_count(session['auth'],vm_id)
        except Exception ,ex:
            err_desc = to_str(ex).replace("'",'')
            err_desc = err_desc.strip()
            LOGGER.error(err_desc)
            return "{success: false,msg: '"+err_desc+"'}"
        return {'success':True, 'policy_count':result['policy_count'],'first_backup_id':result['first_backup_id'],'msg':'OK'}

    def backup_report(self,backup_id,num_runs,_dc=None):
        
        try:
            self.authenticate()
            info = self.backup_manager.backup_report(session['auth'],backup_id,num_runs)
            return dict(success=True,info = info)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))

            
            
    def delete_backuprecord(self, backupsetup_id, group_id, _dc=None):
        
        try:
            self.authenticate()
            self.backup_manager.delete_backuprecord(session['auth'],backupsetup_id,group_id)
            return {'success':True, 'msg':'Backup Record Deleted.'}
        except Exception ,ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}

            
            
            
    def get_backupConfig_of_sp(self, group_id, vm_id=None, _dc=None):
        
        try:
            self.authenticate()
            result = None
            result = self.backup_manager.get_backupConfig_of_sp(session['auth'],group_id,vm_id)
        except Exception ,ex:
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return result
        
    def get_backupsetup_details(self, backupsetup_id, cli=False):
        
        try:
            result = None
            self.authenticate()
            if cli == True:
                backup = self.backup_service.get_backup(backupsetup_id)
                if backup:
                    result = self.backup_manager.get_backupsetup_details_cli(backup.id)
                return {'success':False,'msg':'The backup settings with name '+backupsetup_id+' does not exists'}
            else:
                result = self.backup_manager.get_backupsetup_details(backupsetup_id)
        except Exception ,ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'","")}
        return {'success':True,'backupsetup_details':result}


    def get_individual_sp_backup_task_history(self, backup_id, cli=False, _dc=None):
        
        try:
            self.authenticate()
            result = None
            if cli == True:
                backup = self.backup_service.get_backup(backup_id)
                if backup:
                    result = self.backup_service.get_individual_sp_backup_task_history(session['auth'],backup.id)
                return {'success':False,'msg':'The backup settings with name '+backup_id+' does not exists'}
            else:
                result = self.backup_service.get_individual_sp_backup_task_history(session['auth'],backup_id)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return result
                
    def get_backupsetupinfo(self, node_id, node_type, _dc=None):
        try:
            self.authenticate()
            result = []
            result = self.backup_service.get_backupsetupinfo(session['auth'],node_id,node_type)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

    def get_calendar(self, config_id):
        
        cal = None
        backup_occurance = None
        days_list = []
        hour_list = []
        min_list = []
        config = self.backup_manager.get_sp_backup_config(config_id)
        
        if config:
            backup_schedule = self.backup_manager.get_sp_backup_schedule(config.sp_backup_schedule_id)
            
            if backup_schedule:
                backup_occurance = backup_schedule.backup_occurance
                minutes = backup_schedule.backup_time_min
                hours = backup_schedule.backup_time_hr
                week_days_list = self.get_int_list(backup_schedule.backup_weekday_list)
                month_days_list = self.get_int_list(backup_schedule.backup_monthday_list)
                offset = datetime.now() - datetime.now()
                min_datetime = datetime.min + timedelta(days=1)
                min_list = []
                min_list.append(int(minutes))
                hour_list = []
                hour_list.append(int(hours))
                if backup_occurance == 'Hourly':
                        
                    min_datetime = datetime.min + timedelta(days=1, hours=0, minutes=int(minutes))
                    utc_datetime = min_datetime - offset
                    min_list = []
                    min_list.append(utc_datetime.minute)
                else:    
                    min_datetime = datetime.min + timedelta(days=1, hours=int(hours), minutes=int(minutes))
                    utc_datetime = min_datetime - offset
                    min_list = []
                    min_list.append(utc_datetime.minute)
                    hour_list = []
                    hour_list.append(utc_datetime.hour)
                    if backup_occurance == 'Weekly':
                        min_datetime = datetime.min + timedelta(days=1L, hours=int(hours), minutes=int(minutes))
                        utc_datetime = min_datetime - offset
                        min_list = []
                        min_list.append(utc_datetime.minute)
                        hour_list = []
                        hour_list.append(utc_datetime.hour)
                        if utc_datetime.day == min_datetime.day:
                            pass
                        else:
                            if utc_datetime.day < min_datetime.day:
                                for index in range(len(week_days_list)):
                                    week_days_list[index] = (week_days_list[index] - 1) % 7
                            else:
                                if utc_datetime.day > min_datetime.day:
                                    for index in range(len(week_days_list)):
                                        week_days_list[index] = (week_days_list[index] + 1) % 7
                        days_list = week_days_list
                    else:
                        min_datetime = datetime.min + timedelta(days=1L, hours=int(hours), minutes=int(minutes))
                        utc_datetime = min_datetime - offset
                        min_list = []
                        min_list.append(utc_datetime.minute)
                        hour_list = []
                        hour_list.append(utc_datetime.hour)
                        if utc_datetime.day == min_datetime.day:
                            pass
                        else:
                            if utc_datetime.day < min_datetime.day:
                                for index in range(len(month_days_list)):
                                    month_days_list[index] = (month_days_list[index] - 1) % 31
                            else:
                                if utc_datetime.day > min_datetime.day:
                                    for index in range(len(month_days_list)):
                                        month_days_list[index] = (month_days_list[index] + 1) % 31
                        days_list = month_days_list
        return (config, backup_occurance, days_list, hour_list, min_list)

    def get_copy_options(self, group_id,_dc=None):
        
        display_list = []
        result = []
        key = 'Key1'
        value = 'Value1'
        return dict(success='true', rows=result)

    def get_datetime_from_list(self, week_days_list, month_days_list, hour_list, min_list):
        
        datetimeobjList = []
        month_list = []
        hr_list = []
        if month_days_list:
            for day in month_days_list:
                day = int(day)
                month_list.append(day)
        if hour_list:
            for hour in hour_list:
                if min_list:
                    for eachmin in min_list:
                        if month_list:
                            for day in month_list:
                                dateobj = datetime(day, hour, eachmin)
                                datetimeobjList.append(dateobj)
        else:
            if min_list:
                for eachmin in min_list:
                    now = datetime.now()
                    dateobj = datetime(now.year, now.month, now.day, now.hour, eachmin)
                    datetimeobjList.append(dateobj)
        return datetimeobjList
        
    def get_file_backup_options(self, group_id, backupsetup_id=None, _dc=None):
        
        result = []
        if backupsetup_id:
            result = self.backup_manager.get_file_backup_options(group_id, backupsetup_id)
        return dict(success='true', rows=result)
               
            

    def get_int_list(self, objList):
        
        objNewList = []
        for eachitem in objList:
            if eachitem:
                int_item = int(eachitem)
                objNewList.append(int_item)
        return objNewList


        
        
    def get_server_info(self, group_id,_dc=None):
        
        try:
            self.authenticate()
            result = None
            result = self.backup_manager.get_server_info(session['auth'],group_id)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return result
        
    def get_sp_backup_task_result(self, node_id, _dc=None):
        
        try:
            self.authenticate()
            result = None
            result = self.backup_service.get_sp_backup_task_result(session['auth'],node_id)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return result
            
    def get_sp_vm_backup_history(self, node_id, node_type, search_text, _dc=None):
        
        try:
            self.authenticate()
            result = None
            result = self.backup_service.get_sp_vm_backup_history(session['auth'],node_id,node_type,search_text)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return result

    def get_transferMethod_options(self, group_id, backupsetup_id=None, _dc=None):
        
        result = []
        if backupsetup_id:
            result = self.backup_manager.get_transferMethod_options(group_id, backupsetup_id)
        else:
            result.append(dict(attribute='snapshot_create_script', value=''))
            result.append(dict(attribute='snapshot_delete_script', value=''))
            result.append(dict(attribute='transfer_script', value=''))
            result.append(dict(attribute='mount_script', value=''))
            result.append(dict(attribute='options', value=''))
        return dict(success='true', rows=result)

    def get_vm_backup_task_result(self, node_id, _dc=None):
        
        try:
            self.authenticate()
            result = None
            result = self.backup_service.get_vm_backup_task_result(session['auth'],node_id)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return result

    def get_vm_backupsetupinfo(self, sp_id, vm_id,_dc=None):
        
        try:
            self.authenticate()
            result = []
            result = self.backup_service.get_vm_backupsetupinfo(sp_id,vm_id)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)

    def get_vm_backupsetupinfo_cli(self, vm_id, _dc=None):
        
        try:
            self.authenticate()
            ent = session['auth'].get_entity(vm_id)
            parentent = ent.parents[0]
            grnd_parent = parentent.parents[0]
            sp_id = grnd_parent.entity_id
            result = self.backup_service.get_vm_backupsetupinfo_cli(sp_id,vm_id)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)
        
    def get_vms_backupInfo_from_list(self, group_id, backup_id, _dc=None):
        
        try:
            self.authenticate()
            result = None
            result = self.backup_manager.get_vms_backupInfo_from_list(session['auth'],group_id,backup_id)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return result

    def get_vms_backupInfo_from_pool(self, group_id,_dc=None):
        
        try:
            self.authenticate()
            result = None
            result = self.backup_manager.get_vms_backupInfo_from_pool(session['auth'],group_id)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return result

    def list_backups(self, vm_id, policyname, number, details, _dc=None):
        
        try:
            self.authenticate()
            result = None
            result = self.backup_service.list_backups(session['auth'],vm_id,policyname,number,details)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)
        
    def non_backupVM(self, node_id, node_type,_dc=None):
        
        try:
            self.authenticate()
            info = self.backup_manager.non_backupVM(session['auth'],node_id,node_type)
            return dict(success=True,info=info)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))

    def ping_server(self, server, username, password, ssh_port, usekey):
        
        try:
            self.authenticate()
            result = None
            servvice_obj = BackupService()
            result = servvice_obj.ping_server(session['auth'],server,username,password,ssh_port,usekey)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,ping_result=result)

    def purge_single_backup(self, result_id, node_id):
        
        try:
            self.tc.purge_single_backup_task(session['auth'],result_id,node_id)
        except Exception ,ex:
            err_desc = to_str(ex).replace("'","")
            LOGGER.error(err_desc)
            return "{success:false, msg:'"+err_desc+"'}"
        return "{success:true, msg:'Task submitted.'}"


    #def redirect_to(self, url):
    #    try:
     #       protocol = tg.config.get(constants.SERVER_PROTOCOL, 'http')
      #      host = pylons.request.headers['Host']
       ##except Exception as e:
         #   raise e

    def sp_backup_failure(self, node_id, node_type, _dc=None):
        
        try:
            self.authenticate()
            info = self.backup_service.sp_backup_failure(session['auth'],node_id,node_type)
            return dict(success=True,info=info)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))


    def sp_backup_summary(self, node_id, node_type,_dc=None):
        
        try:
            self.authenticate()
            info = self.backup_manager.sp_backup_summary(session['auth'],node_id,node_type)
            return dict(success=True,info=info)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))


    def submit_sp_backup_task(self, group_id, config_id):
        
        config,backup_occurance, days_list,hour_list,min_list= self.get_calendar(config_id)
        task_id = self.tc.sp_backup_task(session['auth'], group_id, config, backup_occurance, days_list, hour_list, min_list)
        return task_id

        
        
    def updateSPTaskRecord(self, group_id, config, backupsetup_id):
        
        result = None
        self.authenticate()
        config = json.loads(config)
        try:
            self.backup_manager.updateSPTaskRecord(session['auth'],group_id,config,backupsetup_id)
            general = config.get('general_object')
            policy_name = general['taskname']
            schedule = config.get('schedule_object')
            schedule_type = schedule['scheduleType']
            policy_config = self.backup_service.get_sp_backup_config(None,group_id,policy_name)
            if schedule_type == 'Manual':
                self.backup_service.delete_backup_policy_task(policy_config.id,group_id)
            else:
                self.update_sp_backup_task_calendar(group_id,policy_config)
            
        except Exception ,ex:
            print_traceback()
            return {'success': False, 'msg': False}
        return {'success': True, 'msg': True}

    def update_sp_backup_task_calendar(self, group_id, policy_config):
        
        if policy_config:
            config,backup_occurance,days_list, hour_list,min_list= self.get_calendar(policy_config.id)
            self.tc.update_sp_backup_task_calendar(session['auth'], group_id, policy_config, backup_occurance, days_list, hour_list, min_list)

    def vm_backup_summary(self, node_id, _dc=None):
        
        try:
            self.authenticate()
            info = self.backup_manager.vm_backup_summary(session['auth'],node_id)
            return dict(success=True,info=info)
        except Exception ,ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))



