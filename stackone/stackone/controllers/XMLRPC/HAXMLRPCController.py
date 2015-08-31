import pylons
from stackone.model import *
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
constants = stackone.core.utils.constants
LOGGER = logging.getLogger('stackone.controllers')
from stackone.controllers.HAController import HAController
from stackone.controllers.XMLRPC.stackoneXMLRPC import stackoneXMLRPC
class HAXMLRPCController(stackoneXMLRPC):
    ha_controller = HAController()
    def get_vm_priority(self, _dc=None):
        result = None
        result = self.ha_controller.get_vm_priority()
        return result

    def ha_vm_priority(self, node_id):
        info = self.ha_controller.ha_vm_priority(node_id)
        return info

    def get_preferred_servers(self, grp_id, _dc=None):
        result = None
        result = self.ha_controller.get_preferred_servers_cli(grp_id)
        return result

    def get_standby_servers(self, grp_id, _dc=None):
        result = None
        result = self.ha_controller.get_standby_servers(grp_id)
        return result

    def get_sp_fencing_data(self, node_id, node_type, _dc=None):
        result = None
        result = self.ha_controller.get_sp_fencing_data(node_id, node_type)
        return result

    def get_sp_fencing_devices(self, _dc=None):
        result = None
        result = self.ha_controller.get_sp_fencing_devices()
        return result

    def get_sp_fencingdevice_params(self, fence_id, _dc=None):
        result = None
        result = self.ha_controller.get_sp_fencingdevice_params(fence_id)
        return result

    def get_cluster_adapters(self, _dc=None):
        result = None
        result = self.ha_controller.get_cluster_adapters()
        return result

    def ha_fence_resource_types(self, _dc=None):
        result = None
        result = self.ha_controller.ha_fence_resource_types()
        return result

    def process_ha(self, node_id, node_type, ha_data, _dc=None):
        result = None
        result = self.ha_controller.process_ha(node_id, node_type, ha_data)
        return result

    def get_ha_details(self, node_type, node_id, _dc=None):
        result = None
        result = self.ha_controller.get_ha_details(node_type, node_id)
        return result

    def get_advanced_params(self, node_id, _dc=None):
        result = None
        result = self.ha_controller.get_advanced_params(node_id)
        return result

    def ha_fence_resource_type_meta(self, fence_id, _dc=None):
        result = None
        result = self.ha_controller.ha_fence_resource_type_meta(fence_id)
        return result

    def get_dc_fence_resources(self, _dc=None):
        result = None
        result = self.ha_controller.get_dc_fence_resources()
        return result

    def save_dc_params(self, fencing_name, fencing_id, params, _dc=None):
        result = None
        result = self.ha_controller.save_dc_params(fencing_name, fencing_id, params)
        return result

    def update_dc_params(self, res_id, fencing_name, fencing_id, params, _dc=None):
        result = None
        result = self.ha_controller.update_dc_params(res_id, fencing_name, fencing_id, params)
        return result

    def remove_fencing_device(self, res_id, _dc=None):
        result = None
        result = self.ha_controller.remove_fencing_device(res_id)
        return result

    def enable_ha(self, groupid, enable):
        result = self.ha_controller.enable_ha_cli(groupid, enable)
        return result



