import pylons
import simplejson as json
from stackone.lib.base import BaseController
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
from stackone.controllers.XMLRPC.StorageXMLRPCController import StorageXMLRPCController
LOGGER = logging.getLogger('stackone.controllers')
from stackone.model.Authorization import AuthorizationService
from pylons.controllers.util import forward
from pylons.controllers import XMLRPCController
from stackone.controllers.BackupController import BackupController
#from stackone.controllers.DecoratedController import DecoratedController
class BackupAjaxController(BaseController):
    backup_controller = stackone.controllers.BackupController.BackupController()
    @expose(template='json')
    def Add_vm_to_backuplist(self, vm_id, backup_id_list):
        result = self.backup_controller.Add_vm_to_backuplist(vm_id, backup_id_list)
        return result
        
    @expose(template='json')
    def BackedUpVMlist(self,sp_id,_dc=None):
        result = self.backup_controller.BackedUpVMlist(sp_id)
        return result

    @expose(template='json')
    def StoreBackup_ConfigRecord(self, group_id, config):
        result = self.backup_controller.StoreBackup_ConfigRecord(group_id, config)
        return result

    #def __init__(self, *args, **kwargs):
      #  if hasattr(self, 'allow_only') and self.allow_only is not None:
      #      predicate = self.allow_only
      #      self = allow_only(predicate)(self)
     #   else:
     #       hasattr(self, 'allow_only')
        #super(DecoratedController, self).__init__(*args, **kwargs)
        
    @expose(template='json')
    def backupVMNow(self, vm_id, config_id):
        result = self.backup_controller.backupVMNow(vm_id, config_id)
        return result

    @expose(template='json')
    def backup_policy_count(self, vm_id):
        result = self.backup_controller.backup_policy_count(vm_id)
        return result

    @expose(template='json')
    def backup_report(self,backup_id, num_runs,_dc=None):
        result = self.backup_controller.backup_report(backup_id, num_runs)
        return result

    @expose(template='json')
    def delete_backuprecord(self,backupsetup_id, group_id,_dc=None):
        result = self.backup_controller.delete_backuprecord(backupsetup_id, group_id)
        return result

    @expose(template='json')
    def get_backupConfig_of_sp(self, group_id,vm_id=None, _dc=None):
        result = self.backup_controller.get_backupConfig_of_sp(group_id, vm_id)
        return result

    @expose(template='json')
    def get_backupsetup_details(self, backupsetup_id):
        result = self.backup_controller.get_backupsetup_details(backupsetup_id)
        return result

    @expose(template='json')
    def get_backupsetupinfo(self,node_id, node_type,_dc=None):
        result = self.backup_controller.get_backupsetupinfo(node_id, node_type)
        return result

    @expose(template='json')
    def get_calendar(self, config_id):
        result = self.backup_controller.get_calendar(config_id)
        return result

    @expose(template='json')
    def get_copy_options(self, group_id,_dc=None):
        display_list = []
        result = []
        key = 'Key1'
        value = 'Value1'
        return dict(success='true', rows=result)

    @expose(template='json')
    def get_datetime_from_list(self, week_days_list, month_days_list, hour_list, min_list):
        result = self.backup_controller.get_datetime_from_list(week_days_list, month_days_list, hour_list, min_list)
        return result

    @expose(template='json')
    def get_file_backup_options(self, group_id,backupsetup_id=None, _dc=None):
        result = self.backup_controller.get_file_backup_options(group_id, backupsetup_id)
        return result

    @expose(template='json')
    def get_individual_sp_backup_task_history(self,backup_id,_dc=None):
        result = self.backup_controller.get_individual_sp_backup_task_history(backup_id)
        return result

    @expose(template='json')
    def get_int_list(self, objList):
        result = self.backup_controller.get_int_list(objList)
        return result

    @expose(template='json')
    def get_server_info(self,group_id,_dc=None):
        result = self.backup_controller.get_server_info(group_id)
        return result

    @expose(template='json')
    def get_sp_backup_task_result(self,node_id,_dc=None):
        result = self.backup_controller.get_sp_backup_task_result(node_id)
        return result

    @expose(template='json')
    def get_sp_vm_backup_history(self,node_id, node_type, search_text=None, _dc=None):
        result = self.backup_controller.get_sp_vm_backup_history(node_id, node_type, search_text)
        return result

    @expose(template='json')
    def get_transferMethod_options(self, group_id,backupsetup_id=None, _dc=None):
        result = self.backup_controller.get_transferMethod_options(group_id, backupsetup_id)
        return result

    @expose(template='json')
    def get_vm_backup_task_result(self,node_id, _dc=None):
        result = self.backup_controller.get_vm_backup_task_result(node_id)
        return result

    @expose(template='json')
    def get_vm_backupsetupinfo(self,sp_id, vm_id,_dc=None):
        result = self.backup_controller.get_vm_backupsetupinfo(sp_id, vm_id)
        return result

    @expose(template='json')
    def get_vms_backupInfo_from_list(self,group_id, backup_id,_dc=None):
        result = self.backup_controller.get_vms_backupInfo_from_list(group_id, backup_id)
        return result

    @expose(template='json')
    def get_vms_backupInfo_from_pool(self,group_id,_dc=None):
        result = self.backup_controller.get_vms_backupInfo_from_pool(group_id)
        return result

    @expose(template='json')
    def non_backupVM(self,node_id, node_type,_dc=None):
        result = self.backup_controller.non_backupVM(node_id, node_type)
        return result

    @expose(template='json')
    def ping_server(self, server, username, password, ssh_port, usekey):
        result = self.backup_controller.ping_server(server, username, password, ssh_port, usekey)
        return result

    @expose(template='json')
    def purge_single_backup(self,result_id, node_id=None):
        self.backup_controller.purge_single_backup(result_id, node_id)

    #@expose(template='json')
    #def routes_placeholder(self, url='/', start_response=None, **kwargs):
     ###   """


    @expose(template='json')
    def sp_backup_failure(self,node_id, node_type,_dc=None):
        result = self.backup_controller.sp_backup_failure(node_id, node_type)
        return result

    @expose(template='json')
    def sp_backup_summary(self,node_id, node_type,_dc=None):
        result = self.backup_controller.sp_backup_summary(node_id, node_type)
        return result

    @expose(template='json')
    def submit_sp_backup_task(self, group_id, config_id):
        result = self.backup_controller.submit_sp_backup_task(group_id, config_id)
        return result

    @expose(template='json')
    def updateSPTaskRecord(self, group_id, config, backupsetup_id):
        result = self.backup_controller.updateSPTaskRecord(group_id, config, backupsetup_id)
        return result

    @expose(template='json')
    def update_sp_backup_task_calendar(self, group_id, policy_config):
        result = self.backup_controller.update_sp_backup_task_calendar(group_id, policy_config)
        return result

    @expose(template='json')
    def vm_backup_summary(self,node_id,_dc=None):
        result = self.backup_controller.vm_backup_summary(node_id)
        return result

    @expose()
    def xmlrpc(self):
        return forward(BackupXMLRPCController())

