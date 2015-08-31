import pylons
import simplejson as json
from stackone.lib.base import BaseController
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.DashboardService import DashboardService
from stackone.viewModel.ChartService import ChartService
from stackone.core.utils.utils import to_unicode, to_str, print_traceback, performance_debug
import stackone.core.utils.constants
constants = stackone.core.utils.constants
DEBUG_CAT = constants.DEBUG_CATEGORIES
import logging
import tg
import os
from stackone.model.GenericCache import GenericCache
LOGGER = logging.getLogger('stackone.controllers')
from stackone.controllers.ControllerBase import ControllerBase
class DashboardController(ControllerBase):
    __doc__ = '\n\n    '
    dashboard_service = DashboardService()
    chart_service = ChartService()
    def dashboardservice(self, type, node_id, username=None, password=None, **kw):
        try:
            result = None
            self.authenticate()
            if stackone.model.LicenseManager.is_violated():
                return {'success':True,'msg':stackone.model.LicenseManager.LICENSE_VIOLATED_MSG,'mode':'VIOLATION'}

            dashboardInfo = self.dashboard_service.execute(session['auth'], type, node_id, username, password)
            result = json.dumps(dict(success=True, nodes=dashboardInfo.toJson()))
            return result

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))



    def data_center_info(self, node_id, type, op):
        self.authenticate()

        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)
            self.authenticate()
            info = self.dashboard_service.data_center_info(session['auth'], node_id, type, op)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def server_pool_info(self, node_id, type, op):
        self.authenticate()

        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.server_pool_info(session['auth'], node_id, type, op)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def server_info(self, node_id, type, op):
        self.authenticate()

        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.server_info(session['auth'], node_id, type, op)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def vm_info(self, node_id, type):
        self.authenticate()
        
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.vm_info(session['auth'], node_id, type)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def vm_availability(self, node_id, _dc=None):
        self.authenticate()

        try:
            self.authenticate()
            info = self.dashboard_service.vm_availability(session['auth'], node_id)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def vm_storage(self, node_id, _dc=None):
        self.authenticate()

        try:
            self.authenticate()
            info = self.dashboard_service.vm_storage(session['auth'], node_id)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def dashboard_vm_info(self, node_id, type, canned=None, _dc=None):
        self.authenticate()

        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.dashboard_vm_info(session['auth'], node_id, type, canned)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def dashboard_server_info(self, node_id, type, canned=None, _dc=None):
        self.authenticate()

        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)
            self.authenticate()
            info = self.dashboard_service.dashboard_server_info(session['auth'], node_id, type, canned)
            return info

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def dashboard_serverpool_info(self, node_id, type, _dc=None):
        self.authenticate()

        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.dashboard_serverpool_info(session['auth'], node_id, type)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def metrics(self):
        try:
            self.authenticate()
            info = self.chart_service.metrics(session['auth'])
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def get_chart_data(self, node_id, node_type, metric, period, offset, frmdate=None, todate=None, chart_type=None, avg_fdate=None, avg_tdate=None):
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)
            self.authenticate()
            info = self.chart_service.get_chart_data(session['auth'], node_id, node_type, metric, period, offset, frmdate, todate, chart_type, avg_fdate, avg_tdate)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def get_vm_metrics(self, node_id, metric, rolluptype, fromdate=None, todate=None):
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            node_type = constants.DOMAIN
            info = self.chart_service.get_metric_detail(node_id, node_type, metric, rolluptype, fromdate, todate)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def get_server_metrics(self, node_id, metric, rolluptype, fromdate=None, todate=None):
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            node_type = constants.MANAGED_NODE
            info = self.chart_service.get_metric_detail(node_id, node_type, metric, rolluptype, fromdate, todate)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def server_usage(self, node_id, metric, _dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.server_usage(session['auth'], node_id, metric)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def topNvms(self, node_id, metric, node_type, _dc=None):
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.topNvms(session['auth'], node_id, metric, node_type)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def topNservers(self, node_id, metric, node_type, _dc=None):
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.topNservers(session['auth'], node_id, metric, node_type)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def os_distribution_chart(self, node_id, metric, node_type, _dc=None):
        
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.os_distribution_chart(session['auth'], node_id, metric, node_type)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def get_updated_tasks(self, user_name, _dc=None):
        try:
            result = None
            self.authenticate()
            result = self.dashboard_service.get_updated_tasks(user_name)
            return dict(success='true', tasks=result)

        except Exception as ex:
            return ("{success:false,msg:'", to_str(ex).replace("'", ''), "'}")

        return None


    def server_metric_info(self, node_id):
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.server_metric_info(session['auth'], node_id)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def vm_metric_info(self, dom_id):
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.vm_metric_info(session['auth'], dom_id)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def datacenter_summary_info(self, site_id):
        try:
            self.authenticate()
            info = self.dashboard_service.datacenter_summary_info(session['auth'], site_id)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def serverpool_summary_info(self, groupid):
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.serverpool_summary_info(session['auth'], groupid)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def server_summary_info(self, node_id):
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.server_summary_info(session['auth'], node_id)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def vm_summary_info(self, dom_id):
        try:
            if stackone.model.LicenseManager.is_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)

            self.authenticate()
            info = self.dashboard_service.vm_summary_info(session['auth'], dom_id)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def failed_vms(self, vm_ids):
        try:
            self.authenticate()
            vm_info = self.dashboard_service.failed_vms(session['auth'], vm_ids)
            return dict(success=True, vm_info=vm_info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def get_cache_details(self):
        try:
            self.authenticate()
            gc = GenericCache()
            cache_info = gc.get_cache_details()
            return dict(success=True, cache_info=cache_info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def get_custom_search_list(self, node_level, lists_level):
        try:
            self.authenticate()
            info = self.dashboard_service.get_custom_search_list(session['auth'], node_level, lists_level)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def get_custom_search(self, name, lists_level):
        try:
            self.authenticate()
            info = self.dashboard_service.get_custom_search(session['auth'], name, lists_level)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def get_canned_custom_list(self, node_level, lists_level, _dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.get_canned_custom_list(session['auth'], node_level, lists_level)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def get_filter_forsearch(self, _dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.get_filter_forsearch(session['auth'])
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def get_property_forsearch(self, node_id, node_type, listlevel, _dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.get_property_forsearch(session['auth'], node_id, node_type, listlevel)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def save_custom_search(self, name, desc, condition, node_id, level, lists_level, max_count=200L, _dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.save_custom_search(session['auth'], name, desc, condition, node_id, level, lists_level, max_count)
            if info == True:
                return dict(success=True, info=info)

            return dict(success=False, msg=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def delete_custom_search(self, name, _dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.delete_custom_search(session['auth'], name)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def edit_save_custom_search(self, name, desc, condition, max_count=200L, _dc=None):
        try:
            self.authenticate()
            info = self.dashboard_service.edit_save_custom_search(session['auth'], name, desc, condition, max_count)
            return dict(success=True, info=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def test_newcustom_search(self, name, value, node_id, type, listlevel):
        try:
            self.authenticate()
            info = self.dashboard_service.test_newcustom_search(session['auth'], name, value, node_id, type, listlevel)
            return dict(success=True, msg=info)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
    
    
    def get_ui_helper(self, node_id, node_type, ui_type):
        try:
            self.authenticate()
            result = self.dashboard_service.get_ui_helper(session['auth'],node_id,node_type,ui_type)
            print 'get_ui_helper, result:%s' % result
            return dict(success=True,result=result)
        except Exception as ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", ' '))
        




