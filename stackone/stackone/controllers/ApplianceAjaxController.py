import pylons
import simplejson as json
from stackone.viewModel.Userinfo import Userinfo
from stackone.model.Authorization import AuthorizationService
from stackone.controllers.ControllerBase import ControllerBase
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.ApplianceService import ApplianceService
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
LOGGER = logging.getLogger('stackone.controllers')
from pylons.controllers.util import forward
from pylons.controllers import XMLRPCController
from stackone.controllers.ApplianceController import ApplianceController
from stackone.controllers.XMLRPC.ApplianceXMLRPCController import ApplianceXMLRPCController
class ApplianceAjaxController(ControllerBase):
    __doc__ = '\n\n    '
    appliance_controller = ApplianceController()
    
    @expose()
    def xmlrpc(self):
        return forward(ApplianceXMLRPCController())
        
    @expose(template='json')
    def get_appliance_providers(self,**kw):
        result = None
        result = self.appliance_controller.get_appliance_providers()
        return result
       
    @expose(template='json')
    def get_appliance_packages(self,**kw):
        result = None
        result = self.appliance_controller.get_appliance_packages()
        return result
        
    @expose(template='json')
    def get_appliance_archs(self,**kw):
        result = None
        result = self.appliance_controller.get_appliance_archs()
        return result
        
    @expose(template='json')
    def get_appliance_list(self,**kw):
        result = None
        result = self.appliance_controller.get_appliance_list()
        return result
        
    @expose(template='json')
    def refresh_appliances_catalog(self):
        try:
            result = None
            result = self.appliance_controller.refresh_appliances_catalog()
        except Exception , ex:
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return dict(success=True,rows=result)
        
    @expose(template='json')
    def import_appliance(self, href, type, arch, pae, hvm, size, provider_id, platform, description, link, image_name, group_id, is_manual, date=None, time=None, **kw):
        result = None
        result = self.appliance_controller.import_appliance(href,type,arch,pae,hvm,size,provider_id,platform,description,link,image_name,group_id,is_manual,date,time)
        return result
        
    @expose(template='json')
    def get_appliance_menu_items(self,dom_id,node_id):
        result = None
        result = self.appliance_controller.get_appliance_menu_items(dom_id,node_id)
        return result
        
    @expose(template='json')
    def get_appliance_info(self,dom_id,node_id,action):
        result = None
        result = self.appliance_controller.get_appliance_info(dom_id,node_id,action)
        return result
        
    @expose(template='json')
    def save_appliance_info(self,dom_id,node_id,action,**kw):
        result = None
        result = self.appliance_controller.save_appliance_info(dom_id,node_id,action,**kw)
        return result


