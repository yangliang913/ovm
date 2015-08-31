from stackone.model import *
from stackone.model.Authorization import AuthorizationService
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from tg import session
from stackone.controllers.DashboardController import DashboardController
from stackone.controllers.XMLRPC.stackoneXMLRPC import stackoneXMLRPC
class DashboardXMLRPCController(stackoneXMLRPC):
    dashboard_controller = DashboardController()
    def dashboardservice(self, type, node_id, username=None, password=None, **result):
        result = None
        dashboardInfo = self.dashboard_controller.dashboardservice(type, node_id)
        result = json.dumps(dict(success=True, nodes=dashboardInfo.toJson()))
        return result

    def data_center_info(self, node_id, type):
        info = self.dashboard_controller.data_center_info(node_id, type)
        return info

    def server_pool_info(self, node_id, type):
        info = self.dashboard_controller.server_pool_info(node_id, type)
        return info

    def server_info(self, node_id, type):
        info = self.dashboard_controller.server_info(node_id, type)
        return info

    def vm_info(self, node_id, type):
        info = self.dashboard_controller.vm_info(node_id, type)
        return info

    def vm_availability(self, node_id, _dc=None):
        info = self.dashboard_controller.vm_availability(node_id)
        return info

    def vm_storage(self, node_id, _dc=None):
        info = self.dashboard_controller.vm_storage(node_id)
        return info

    def dashboard_vm_info(self, node_id, type, _dc=None):
        info = self.dashboard_controller.dashboard_vm_info(node_id, type)
        return info

    def dashboard_server_info(self, node_id, type, _dc=None):
        info = self.dashboard_controller.dashboard_server_info(node_id, type)
        return info

    def dashboard_serverpool_info(self, node_id, type, _dc=None):
        info = self.dashboard_controller.dashboard_serverpool_info(node_id, type)
        return info

    def metrics(self):
        info = self.dashboard_controller.metrics()
        return info

    def get_chart_data(self, node_id, type, metric, period, offset, frmdate=None, todate=None, chart_type=None, avg_fdate=None, avg_tdate=None):
        info = self.dashboard_controller.get_chart_data(node_id, type, metric, period, offset, frmdate, todate, chart_type, avg_fdate, avg_tdate)
        return info

    def get_vm_metrics(self, dom_id, metric, rolluptype, fromdate=None, todate=None):
        info = self.dashboard_controller.get_vm_metrics(dom_id, metric, rolluptype, fromdate, todate)
        return info

    def get_server_metrics(self, node_id, metric, rolluptype, fromdate=None, todate=None):
        info = self.dashboard_controller.get_server_metrics(node_id, metric, rolluptype, fromdate, todate)
        return info

    def server_usage(self, node_id, metric, _dc=None):
        info = self.dashboard_controller.server_usage(node_id, metric)
        return info

    def topNvms(self, node_id, metric, node_type, _dc=None):
        info = self.dashboard_controller.topNvms(node_id, metric, node_type)
        return info

    def topNservers(self, node_id, metric, node_type, _dc=None):
        info = self.dashboard_controller.topNservers(node_id, metric, node_type)
        return info

    def os_distribution_chart(self, node_id, metric, node_type, _dc=None):
        info = self.dashboard_controller.os_distribution_chart(node_id, metric, node_type)
        return info

    def get_updated_tasks(self, user_name, _dc=None):
        result = None
        result = self.dashboard_controller.get_updated_tasks(user_name)
        return result

    def server_metric_info(self, node_id):
        result = None
        result = self.dashboard_controller.server_metric_info(node_id)
        return result

    def vm_metric_info(self, node_id):
        result = None
        result = self.dashboard_controller.vm_metric_info(node_id)
        return result

    def datacenter_summary_info(self, site_id):
        result = None
        result = self.dashboard_controller.datacenter_summary_info(site_id)
        return result

    def serverpool_summary_info(self, groupid):
        result = None
        result = self.dashboard_controller.serverpool_summary_info(groupid)
        return result

    def server_summary_info(self, node_id):
        result = None
        result = self.dashboard_controller.server_summary_info(node_id)
        return result

    def vm_summary_info(self, domid):
        result = None
        result = self.dashboard_controller.vm_summary_info(domid)
        return result

    def get_cache_details(self):
        result = None
        result = self.dashboard_controller.get_cache_details()
        return result



