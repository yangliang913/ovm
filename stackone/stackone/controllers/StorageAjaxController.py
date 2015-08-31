import pylons
import simplejson as json
from stackone.controllers.ControllerBase import ControllerBase
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.StorageService import StorageService
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
from stackone.viewModel import Basic
from stackone.controllers.StorageController import StorageController
class StorageAjaxController(ControllerBase):
    storage_controller = StorageController()
    @expose()
    def xmlrpc(self):
        return forward(StorageXMLRPCController())
        
    def __init__(self):
        self.manager = Basic.getGridManager()
        
    @expose(template='json')
    def get_storage_def_list(self, site_id=None, op_level=None, group_id=None, _dc=None):
        result = None
        result=self.storage_controller.get_storage_def_list(site_id,op_level,group_id,_dc)
        return result
              
    @expose(template='json')
    def get_dc_storage_def_list(self, site_id=None, group_id=None, _dc=None):
        result = None
        result = self.storage_controller.get_dc_storage_def_list(site_id,group_id)
        return result
        
    @expose(template='json')
    def get_storage_types(self, **kw):
        result = None
        result = self.storage_controller.get_storage_types()
        return result
        
    @expose(template='json')
    def add_storage_def(self, type, site_id=None, op_level=None, group_id=None, node_id=None, sp_ids=None, added_manually=False, **kw):
        result = None
        result = self.storage_controller.add_storage_def(type,site_id,op_level,group_id,node_id,sp_ids,added_manually,kw)
        return result
        
    @expose(template='json')
    def edit_storage_def(self, storage_id, type, site_id=None, group_id=None, op_level=None, sp_ids=None, **kw):
        result = None
        result = self.storage_controller.edit_storage_def(storage_id,type,site_id,group_id,op_level,sp_ids,kw)
        return result
        
    @expose(template='json')
    def is_storage_allocated(self,storage_id):
        result = None
        result = self.storage_controller.is_storage_allocated(storage_id)
        return result
        
    @expose(template='json')
    def remove_storage_def(self, storage_id, site_id=None, op_level=None, group_id=None):
        result = None
        result = self.storage_controller.remove_storage_def(storage_id,site_id,op_level,group_id)
        return result
        
    @expose(template='json')
    def rename_storage_def(self, storage_id, new_name, group_id=None):
        result = None
        result = self.storage_controller.rename_storage_def(storage_id,new_name,group_id)
        return result
        
    @expose(template='json')
    def storage_def_test(self, type, storage_id, mode, site_id=None, op_level=None, group_id=None, node_id=None, show_available='true', vm_config_action=None, disk_option=None, **kw):
        result = None
        result = self.storage_controller.storage_def_test(type,storage_id,mode,site_id,op_level,group_id,node_id,show_available,vm_config_action,disk_option,kw)
        return result
        
    @expose()
    def associate_defns(self, def_ids, def_type, site_id=None, op_level=None, group_id=None):
        result = None
        result = self.storage_controller.associate_defns(def_ids,def_type,site_id,op_level,group_id)
        return result
        
    @expose(template='json')
    def get_sp_list(self, site_id, def_id=None, _dc=None):
        result = None
        result = self.storage_controller.get_sp_list(site_id,def_id)
        return result
        
    @expose(template='json')
    def get_server_storage_def_list(self, def_id, defType, site_id=None, group_id=None, _dc=None):
        result = None
        result = self.storage_controller.get_server_storage_def_list(def_id,defType,site_id,group_id)
        return result
        
    @expose()
    def RemoveScanResult(self):
        result = None
        result = self.storage_controller.RemoveScanResult()
        return result
        
    @expose()
    def SaveScanResult(self,storage_id):
        result = None
        result = self.storage_controller.SaveScanResult(storage_id)
        return result
        
    @expose(template='json')
    def get_sp_list(self, site_id, def_id=None, _dc=None):
        result = None
        result = self.storage_controller.get_sp_list(site_id,def_id)
        return result
        
    @expose()
    def add_storage_disk(self, add_manually, group_id, storage_id, actual_size, allocated_size, unique_path, current_portal=None, target=None, state=None, lun=None, storage_allocated=False):
        result = None
        result = self.storage_controller.add_storage_disk(add_manually,group_id,storage_id,actual_size,allocated_size,unique_path,current_portal,target,state,lun,storage_allocated)
        return result
        
    @expose()
    def remove_storage_disk(self,storage_disk_id):
        result = None
        result = self.storage_controller.remove_storage_disk(storage_disk_id)
        return result
        
    @expose()
    def mark_storage_disk(self,storage_disk_id,used):
        result = None
        result = self.storage_controller.mark_storage_disk(storage_disk_id,used)
        return result


