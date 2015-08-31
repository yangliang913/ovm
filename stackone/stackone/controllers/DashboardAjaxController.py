import pylons
import simplejson as json
from stackone.lib.base import BaseController
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.DashboardService import DashboardService
from stackone.viewModel.ChartService import ChartService
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
LOGGER = logging.getLogger('stackone.controllers')
from stackone.model.Authorization import AuthorizationService
from pylons.controllers.util import forward
from pylons.controllers import XMLRPCController
from stackone.controllers.DashboardController import DashboardController
from stackone.controllers.XMLRPC.DashboardXMLRPCController import DashboardXMLRPCController
from stackone.controllers.ControllerBase import ControllerBase
class DashboardAjaxController(ControllerBase):
    __doc__ = '\n\n    '
    dashboard_controller= DashboardController()
    @expose()
    def xmlrpc(self):
        return forward(DashboardXMLRPCController())
        
    @expose(template='json')
    def dashboardservice(self, type, node_id, username=None, password=None, **kw):
        dashboardInfo = None
        dashboardInfo = self.dashboard_controller.dashboardservice(type,node_id,username,password)
        return dashboardInfo

    @expose(template='json')
    def data_center_info(self, node_id, type, op=None):
        info = self.dashboard_controller.data_center_info(node_id,type,op)
        return info

    @expose(template='json')
    def server_pool_info(self, node_id, type, op=None):
        info = self.dashboard_controller.server_pool_info(node_id,type,op)
        return info

    @expose(template='json')
    def server_info(self, node_id, type, op=None):
        result = None
        result = self.dashboard_controller.server_info(node_id,type,op)
        return result

    @expose(template='json')
    def vm_info(self, node_id, type):
        info = self.dashboard_controller.vm_info(node_id,type)
        return info

    @expose(template='json')
    def vm_availability(self, node_id, _dc=None):
        info = self.dashboard_controller.vm_availability(node_id)
        return info

    @expose(template='json')
    def vm_storage(self, node_id, _dc=None):
        info = self.dashboard_controller.vm_storage(node_id)
        return info

    @expose(template='json')
    def dashboard_vm_info(self, node_id, type, canne=None, _dc=None):
        result = self.dashboard_controller.dashboard_vm_info(node_id,type,canne)
        return result

    @expose(template='json')
    def dashboard_server_info(self, node_id, type, canned=None, _dc=None):
        info = self.dashboard_controller.dashboard_server_info(node_id,type,canned)
        return dict(success=True,info=info)

    @expose(template='json')
    def dashboard_serverpool_info(self, node_id, type, _dc=None):
        result = self.dashboard_controller.dashboard_serverpool_info(node_id,type)
        return result

    @expose(template='json')
    def metrics(self):
        result = self.dashboard_controller.metrics()
        return result

    @expose(template='json')
    def get_chart_data(self, node_id, node_type, metric, period, offset, frmdate=None, todate=None, chart_type=None, avg_fdate=None, avg_tdate=None):
        result = self.dashboard_controller.get_chart_data(node_id,node_type,metric,period,offset,frmdate,todate,chart_type,avg_fdate,avg_tdate)
        return result

    @expose(template='json')
    def server_usage(self, node_id, metric, _dc=None):
        result = self.dashboard_controller.server_usage(node_id,metric)
        return result

    @expose(template='json')
    def topNvms(self, node_id, metric, node_type, _dc=None):
        result = self.dashboard_controller.topNvms(node_id,metric,node_type)
        return result

    @expose(template='json')
    def topNservers(self, node_id, metric, node_type, _dc=None):
        result = self.dashboard_controller.topNservers(node_id,metric,node_type)
        return result

    @expose(template='json')
    def os_distribution_chart(self, node_id, metric, node_type, _dc=None):
        result = self.dashboard_controller.os_distribution_chart(node_id,metric,node_type)
        return result

    @expose(template='json')
    def get_updated_tasks(self, user_name, _dc=None):
        result = None
        result = self.dashboard_controller.get_updated_tasks(user_name)
        return result

    @expose(template='json')
    def failed_vms(self, vm_ids, _dc=None):
        result = None
        result = self.dashboard_controller.failed_vms(vm_ids)
        return result

    @expose(template='json')
    def get_custom_search_list(self, node_level, lists_level, _dc=None):
        result = None
        result = self.dashboard_controller.get_custom_search_list(node_level,lists_level)
        return result

    @expose(template='json')
    def get_custom_search(self, name, lists_level, _dc=None):
        result = None
        result = self.dashboard_controller.get_custom_search(name,lists_level)
        return result

    @expose(template='json')
    def get_canned_custom_list(self, node_level, lists_level, _dc=None):
        result = None
        result = self.dashboard_controller.get_canned_custom_list(node_level,lists_level)
        return result

    @expose(template='json')
    def get_filter_forsearch(self, _dc=None):
        result = None
        result = self.dashboard_controller.get_filter_forsearch()
        return result

    @expose(template='json')
    def get_property_forsearch(self, node_id, node_type, listlevel, _dc=None):
        result = None
        result = self.dashboard_controller.get_property_forsearch(node_id,node_type,listlevel)
        return result

    @expose(template='json')
    def save_custom_search(self, name, desc, condition, node_id, level, lists_level, max_count=200, _dc=None):
        result = None
        result = self.dashboard_controller.save_custom_search(name,desc,condition,node_id,level,lists_level,max_count)
        return result

    @expose(template='json')
    def delete_custom_search(self,name, _dc=None):
        result = None
        result = self.dashboard_controller.delete_custom_search(name)
        return result

    @expose(template='json')
    def edit_save_custom_search(self, name, desc, condition, max_count=200, _dc=None):
        result = None
        result = self.dashboard_controller.edit_save_custom_search(name,desc,condition,max_count)
        return result

    @expose(template='json')
    def test_newcustom_search(self, name, value, node_id, type, listlevel, _dc=None):
        result = None
        result = self.dashboard_controller.test_newcustom_search(name,value,node_id,type,listlevel)
        return result
    @expose(template='json')
    def get_ui_helper(self, node_id, node_type, ui_type, _dc=None):
        result = self.dashboard_controller.get_ui_helper(node_id,node_type,ui_type)
        return result
    



