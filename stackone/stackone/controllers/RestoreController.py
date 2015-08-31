import pylons
import simplejson as json
from stackone.lib.base import BaseController
from stackone.model import DBSession, metadata
from stackone.controllers.error import ErrorController
from stackone.model.CustomPredicates import has_role
from stackone.controllers.ApplianceController import ApplianceController
from stackone.controllers.DashboardController import DashboardController
from stackone.controllers.ModelController import ModelController
from stackone.controllers.NodeController import NodeController
from stackone.controllers.NetworkController import NetworkController
from stackone.controllers.StorageController import StorageController
from stackone.controllers.TemplateController import TemplateController
from stackone import model
from stackone.model import *
from stackone.model.DBHelper import DBHelper
from stackone.model.Authorization import AuthorizationService
from stackone.model.UpdateManager import UIUpdateManager
from stackone.controllers.secure import SecureController
from tg import expose, flash, require, url, request, redirect, response, session, config
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates
from xml.dom import minidom
from stackone.viewModel.TaskInfo import TaskInfo
from stackone.viewModel.Server import Server
from stackone.viewModel.Message import Message
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
LOGGER = logging.getLogger('stackone.controllers')
from stackone.model.services import TaskCalendar
from stackone.viewModel.RestoreService import RestoreService
from stackone.viewModel.BackupService import BackupService
from stackone.controllers.ControllerBase import ControllerBase
class RestoreController(ControllerBase):
    tc = TaskCreator()
    backup_service = BackupService()
    restore_service = RestoreService()
    def __init__(self):
        pass

    def restore(self, server_id, vm_id, config_id, backup_result_id, ref_disk=None, _dc=None):
        try:
            self.authenticate()
            backup_config_id = None
            self.tc.restore_vm_task(session['auth'],server_id,vm_id,backup_result_id,config_id,ref_disk)
        except Exception,ex:
            print_traceback()
            return "{success: false,msg:'" + to_str(ex).replace("'",'').replace('\n','')+ "'}"
        return "{success:true, msg:'Task submitted'}"
    def restore_frombackup(self, vm_id, config_name, datetime, ref_disk=None, _dc=None):
        result1 = ''
        try:
            self.authenticate()
            backup = self.backup_service.get_backup(config_name)
            if backup:
                backup_result = self.backup_service.get_recent_backupresult(backup,id,vm_id,datetime)
                if backup_result:
                    result = self.tc.restore_vm_task(session['auth'],backup_result.server_id,vm_id,backup_result.id,backup.id,ref_disk)
                    return dict({'success':True,'msg':to_str(result)})
                return dict({'success':False,'msg':'There are no successful backup taken using the policy '+config_name})
            return dict({'success':False,'msg':'TThe backup policy'+config_name +  ' does not exists'})        
        except Exception,ex:
            print_traceback()
            return "{success: false,msg:'" + to_str(ex).replace("'",'').replace('\n','')+ "'}"
        return dict({'success':True,'rows':result})
    def get_backupresult_info(self, sp_id, vm_id, _dc=None):
        result = []
        try:
            self.authenticate()
            restore_manager = RestoreService().getRestoreManager()
            result = restore_manager.get_backupresult_info(sp_id,vm_id)
            
        except Exception,ex:
            print_traceback()
            return dict({'success':False,'msg':to_str(ex).replace("'",'')})
        return {'success':True,'rows':result}
    def restore_count(self, vm_id):
        self.authenticate()
        result = []
        try:
            restore_manager = RestoreService().getRestoreManager()
            result = restore_manager.restore_count(session['auth'],vm_id)
        except Exception,ex:
            err_desc = to_str(ex).replace("'",'')
            err_desc = err_desc.strip()
            LOGGER.error(err_desc)
            return "{success: false,msg: '" + err_desc + "'}"
        return {'success':True,'policy_count':result['policy_count'],'restore_count':result['restore_count'],'last_restore_id':result['last_restore_id'],'last_backup_id':result['last_backup_id'],'msg':'OK'}
    def get_vm_backups(self, vm_id, _dc=None):
        self.authenticate()
        result = []
        try:
            ent = session['auth'].get_entity(vm_id)
            parentent = ent.parents[0]
            grnd_parent = parentent.parents[0]
            sp_id = grnd_parent.entity_id
            restore_manager = RestoreService().getRestoreManager()
            
            result = restore_manager.get_vm_backups(sp_id,vm_id)
        except Exception,e:
            print_traceback()
            return dict({'success':False,'msg':to_str(e).replace("'",'')})
        return {'success':True,'rows':result}
        
    def get_sp_vm_restore_history(self, node_id, node_type, search_text, _dc=None):
        try:
            self.authenticate()
            result = None
            result = self.restore_service.get_sp_vm_restore_history(session['auth'],node_id,node_type,search_text)
        except Exception,ex:
            print_traceback()
            return dict({'success':False,'msg':to_str(ex).replace("'",'')})
        return result
    def get_vm_restore_task_result(self, node_id, _dc=None):
        try:
            self.authenticate()
            result = None
            result = self.restore_service.get_vm_restore_task_result(session['auth'],node_id)
        except Exception,ex:
            print_traceback()
            return dict({'success':False,'msg':to_str(ex).replace("'",'')})
        return result    


