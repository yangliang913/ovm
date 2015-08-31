from stackone.model import *
from stackone.model.Authorization import AuthorizationService
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from tg import session
from stackone.controllers.ApplianceController import ApplianceController
from stackone.controllers.XMLRPC.stackoneXMLRPC import stackoneXMLRPC
class ApplianceXMLRPCController(stackoneXMLRPC):
    appliance_controller = ApplianceController()
    def get_appliance_providers(self, **result):
        result = self.appliance_controller.get_appliance_providers()
        return result

    def get_appliance_packages(self, **result):
        result = self.appliance_controller.get_appliance_packages()
        return result

    def get_appliance_archs(self, **result):
        result = self.appliance_controller.get_appliance_archs()
        return result

    def get_appliance_list(self, **result):
        result = self.appliance_controller.get_appliance_list()
        return result

    def refresh_appliances_catalog(self, **result):
        result = self.appliance_controller.refresh_appliances_catalog()
        return result

    def importappliance(self, href, type, arch, pae, hvm, provider_id, platform, image_name, group_id, date=None, time=None, **result):
        result = self.appliance_controller.import_appliance_cli(href, type, arch, pae, hvm, None, provider_id, platform, None, None, image_name, group_id, 'true', date, time)
        return result

    def get_appliance_menu_items(self, dom_id, node_id):
        result = self.appliance_controller.get_appliance_menu_items(dom_id, node_id)
        return result

    def get_appliance_info(self, dom_id, node_id, action=None):
        result = self.appliance_controller.get_appliance_info(dom_id, node_id, action)
        return result

    def save_appliance_info(self, dom_id, node_id, action=None, **result):
        result = self.appliance_controller.save_appliance_info(dom_id, node_id, action, kw)
        return result



