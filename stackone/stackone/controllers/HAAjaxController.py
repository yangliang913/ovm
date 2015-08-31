from tg import expose
from stackone.controllers.ControllerBase import ControllerBase
from stackone.controllers.HAController import HAController 
import pylons
import simplejson as json
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


class HAAjaxController(ControllerBase):
    ha_controller = HAController()

    @expose(template='json')
    def get_advanced_params(self, node_id, _dc=None):
        result = None
        result = self.ha_controller.get_advanced_params(node_id)
        return result

    @expose(template='json')
    def get_cluster_adapters(self, _dc=None):
        result = None
        result = self.ha_controller.get_cluster_adapters()
        return result
        
    @expose(template='json')
    def get_dc_fence_resources(self, _dc=None):
        result = None
        result = self.ha_controller.get_dc_fence_resources()
        return result
        
    @expose(template='json')
    def get_ha_details(self, node_type, node_id, _dc=None):
        result = None
        result = self.ha_controller.get_ha_details(node_type, node_id)
        return result
        
    @expose(template='json')
    def get_preferred_servers(self, grp_id, _dc=None):
        result = None
        result = self.ha_controller.get_preferred_servers(grp_id)
        return result

    @expose(template='json')
    def get_servers(self, node_id, _dc=None):
        result = None
        result = self.ha_controller.get_servers(node_id)
        return result

    @expose(template='json')
    def get_sp_fencing_data(self, node_id, node_type, _dc=None):
        result = None
        result = self.ha_controller.get_sp_fencing_data(node_id, node_type)
        return result

    @expose(template='json')
    def get_sp_fencing_devices(self, _dc=None):
        result = None
        result = self.ha_controller.get_sp_fencing_devices()
        return result

    @expose(template='json')
    def get_sp_fencingdevice_params(self, fence_id, _dc=None):
        result = None
        result = self.ha_controller.get_sp_fencingdevice_params(fence_id)
        return result

    @expose(template='json')
    def get_vm_priority(self, _dc=None):
        result = None
        result = self.ha_controller.get_vm_priority()
        return result

    @expose(template='json')
    def ha_fence_resource_type_meta(self, fence_id, _dc=None):
        result = None
        result = self.ha_controller.ha_fence_resource_type_meta(fence_id)
        return result

    @expose(template='json')
    def ha_fence_resource_types(self, category, _dc=None):
        result = None
        result = self.ha_controller.ha_fence_resource_types(category)
        return result

    @expose(template='json')
    def ha_fence_resource_types_classification(self, _dc=None):
        result = None
        result = self.ha_controller.ha_fence_resource_types_classification()
        return result

    @expose(template='json')
    def process_ha(self, node_id, node_type, ha_data, _dc=None):
        result = None
        result = self.ha_controller.process_ha(node_id, node_type, ha_data)
        return result

    @expose(template='json')
    def remove_fencing_device(self, res_id, _dc=None):
        result = None
        result = self.ha_controller.remove_fencing_device(res_id)
        return result

    @expose(template='json')
    def save_dc_params(self, fencing_name, fencing_id, params, _dc=None):
        result = None
        result = self.ha_controller.save_dc_params(fencing_name, fencing_id, params)
        return result


    @expose(template='json')
    def save_fencing_details_fordwm(self, node_id, fence_det, _dc=None):
        result = None
        result = self.ha_controller.save_fencing_details_fordwm(node_id, fence_det)
        return result

    @expose(template='json')
    def update_dc_params(self, res_id, fencing_name, fencing_id, params, _dc=None):
        result = None
        result = self.ha_controller.update_dc_params(res_id, fencing_name, fencing_id, params)
        return result

    @expose(template='json')
    def xmlrpc(self):
        return forward(HAXMLRPCController())

