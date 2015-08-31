from stackone.viewModel.HAService import HAService
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
LOGGER = logging.getLogger('stackone.controllers')
from stackone.model.Authorization import AuthorizationService
from pylons.controllers.util import forward
from pylons.controllers import XMLRPCController


class HAController(ControllerBase):
    ha_service = HAService()

    def enable_ha_cli(self, group_id, enable):
        result = None
        self.authenticate()
        result = self.ha_service.enable_ha_cli(session['auth'], group_id, enable)
        return result

    def get_advanced_params(self, node_id, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.get_advanced_params(session['auth'], node_id)
        return result

    def get_cluster_adapters(self, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.get_cluster_adapters()
        return result

    def get_dc_fence_resources(self, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.get_dc_fence_resources()
        return result

    def get_ha_details(self, node_type, node_id, _dc=None):
        try:
            self.authenticate()
            result = self.ha_service.get_ha_details(node_type, node_id)
            return dict(success=True, ha_data=result)
        except Exception as e:
            print_traceback()
            return dict(success=False, msg='Error:' + to_str(e).replace("'", ' '))
        

    def get_preferred_servers(self, grp_id, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.get_preferred_servers(session['auth'], grp_id)
        return result

    def get_servers(self, node_id, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.get_servers(session['auth'], node_id)
        return result

    def get_sp_fencing_data(self, node_id, node_type, _dc=None):
        try:
            result = None
            self.authenticate()
            result = self.ha_service.get_sp_fencing_data(session['auth'], node_id, node_type)
            return dict(success=True, fencing_data=result)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        

    def get_sp_fencing_devices(self, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.get_sp_fencing_devices()
        return result

    def get_sp_fencingdevice_params(self, fence_id, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.get_sp_fencingdevice_params(fence_id)
        return result

    def get_standby_servers(self, grp_id, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.get_servers_cli(session['auth'], grp_id)
        return result

    def get_vm_priority(self, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.get_vm_priority()
        return result

    def ha_fence_resource_type_meta(self, fence_id, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.ha_fence_resource_type_meta(fence_id)
        return result

    def ha_fence_resource_types(self, category, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.ha_fence_resource_types(category)
        return result

    def ha_fence_resource_types_classification(self, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.ha_fence_resource_types_classification()
        return result

    def ha_vm_priority(self, node_id):
        try:
            self.authenticate()
            info = self.ha_service.ha_vm_priority(session['auth'], node_id)
            return dict(success=True, info=info)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
            

    def process_ha(self, node_id, node_type, ha_data):
        try:
            result = None
            self.authenticate()
            result = self.ha_service.process_ha(session['auth'], node_id, node_type, ha_data)
            return dict(success=True, ha=result)
        except Exception as e:
            print_traceback()
            return dict(success=False, msg='Error:' + to_str(e).replace("'", ' '))

    def remove_fencing_device(self, res_id, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.remove_fencing_device(res_id)
        return result

    def save_dc_params(self, fencing_name, fencing_id, params, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.save_dc_params(fencing_name, fencing_id, params)
        return result

    def save_fencing_details_fordwm(self, node_id, fence_det, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.save_fencing_details_fordwm(node_id, fence_det)
        return result

    def update_dc_params(self, res_id, fencing_name, fencing_id, params, _dc=None):
        result = None
        self.authenticate()
        result = self.ha_service.update_dc_params(res_id, fencing_name, fencing_id, params)
        return result
        
