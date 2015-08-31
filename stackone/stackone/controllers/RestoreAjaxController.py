import pylons
import simplejson as json
from stackone.controllers.ControllerBase import ControllerBase
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model import *
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
LOGGER = logging.getLogger('stackone.controllers')
from pylons.controllers import XMLRPCController
from stackone.controllers.XMLRPC.RestoreXMLRPCController import RestoreXMLRPCController
from stackone.controllers.RestoreController import RestoreController
from pylons.controllers.util import forward
class RestoreAjaxController(ControllerBase):
    restore_controller = RestoreController()
    @expose()
    def xmlrpc(self):
        return forward(RestoreXMLRPCController())
        
    @expose(template='json')
    def restore(self,server_id,vm_id,config_id,backup_result_id,ref_disk):
        result=self.restore_controller.restore(server_id,vm_id,config_id,backup_result_id,ref_disk)
        return result
        
    @expose(template='json')
    def get_backupresult_info(self,sp_id,vm_id,_dc=None):
        result=self.restore_controller.get_backupresult_info(sp_id,vm_id,_dc=None)
        return result
        
    @expose(template='json')
    def restore_count(self,vm_id):
        result=self.restore_controller.restore_count(vm_id)
        return result
        
    @expose(template='json')
    def get_sp_vm_restore_history(self,node_id,node_type,search_text=None, _dc=None):
        result=self.restore_controller.get_sp_vm_restore_history(node_id,node_type,search_text)
        return result
        
    @expose(template='json')
    def get_vm_restore_task_result(self,node_id,_dc = None):
        result=self.restore_controller.get_vm_restore_task_result(node_id)
        return result

