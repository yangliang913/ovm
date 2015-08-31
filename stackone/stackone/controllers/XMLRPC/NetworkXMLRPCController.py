from stackone.model import *
from stackone.model.Authorization import AuthorizationService
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from stackone.controllers.NetworkController import NetworkController
from tg import session
from stackone.controllers.XMLRPC.stackoneXMLRPC import stackoneXMLRPC
class NetworkXMLRPCController(stackoneXMLRPC):
    network_controller = NetworkController()
    def get_new_nw(self, image_id, mode, node_id=None):
        result = None
        result = self.network_controller.get_new_nw(image_id, mode, node_id)
        return result

    def get_nw_det(self, bridge, mac):
        result = None
        result = self.network_controller.get_nw_det(bridge, mac)
        return result

    def get_nws(self, image_id=None, op_level=None, node_id=None, dom_id=None, _dc=None):
        result = self.network_controller.get_nws(image_id, dom_id, node_id, op_level)
        return result

    def get_available_nws(self, mode, op_level=None, node_id=None, _dc=None):
        result = self.network_controller.get_available_nws(mode, op_level, node_id)
        return result

    def get_nw_address_space_map(self, _dc=None):
        result = self.network_controller.get_nw_address_space_map()
        return result

    def get_nw_nat_fwding_map(self, node_id, _dc=None):
        result = self.network_controller.get_nw_nat_fwding_map(node_id)
        return result

    def get_nw_defns(self, site_id=None, op_level=None, group_id=None, node_id=None, _dc=None):
        result = self.network_controller.get_nw_defns(site_id, op_level, group_id, node_id)
        return result

    def get_nw_dc_defns(self, site_id=None, op_level=None, group_id=None, node_id=None, _dc=None):
        result = self.network_controller.get_nw_dc_defns(site_id, op_level, group_id, node_id)
        return result

    def nw_address_changed(self, ip_value, _dc=None):
        result = self.network_controller.nw_address_changed(ip_value)
        return result

    def get_new_private_bridge_name(self, node_id=None, group_id=None, site_id=None, op_level=None, _dc=None):
        result = self.network_controller.get_new_private_bridge_name(node_id, group_id, site_id, op_level)
        return result

    def add_nw_defn(self, nw_name, nw_desc, bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id=None, op_level=None, group_id=None, node_id=None):
        result = self.network_controller.add_nw_defn(nw_name, nw_desc, bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id, group_id, node_id, op_level)
        return result

    def get_edit_network_details(self, nw_id):
        result = self.network_controller.get_edit_network_details(nw_id)
        return result

    def edit_nw_defn(self, nw_id, nw_name, nw_desc):
        result = NetworkControllerImpl().edit_nw_defn(nw_id, nw_name, nw_desc)
        return result

    def network_remove_nw_defn(self, def_id, site_id=None, op_level=None, group_id=None, node_id=None, _dc=None):
        result = self.network_controller.remove_nw_defn(def_id, site_id, group_id, node_id, op_level)
        return result

    def associate_nw_defns(self, def_ids, def_type, site_id=None, op_level=None, group_id=None, node_id=None):
        self.network_controller.associate_nw_defns(def_ids, def_type, site_id, op_level, group_id, node_id)

    def get_server_nw_def_list(self, def_id, defType, site_id=None, group_id=None, _dc=None):
        result = None
        result = self.network_controller.get_server_nw_def_list(def_id, defType, site_id, group_id)
        return result

    def reserve_address(self, pool_id, entity_id):
        result = self.network_controller.reserve_address(pool_id, entity_id)
        return result

    def release_address(self, pool_id, entity_id, ip_id=None):
        result = self.network_controller.release_address(pool_id, entity_id, ip_id)
        return result

    def associate_address(self, pool_id, ip_id, vm_id, csep_id):
        result = self.network_controller.associate_address(pool_id, ip_id, vm_id, csep_id)
        return result

    def disassociate_address(self, pool_id, ip_id, csep_id):
        result = self.network_controller.disassociate_address(pool_id, ip_id, csep_id)
        return result

    def get_all_reserved_addresses(self, pool_id, entity_id=None):
        result = self.network_controller.get_all_reserved_addresses(pool_id, entity_id)
        return result

    def get_all_associated_addresses(self, pool_id, entity_id):
        result = self.network_service.get_all_associated_addresses(pool_id, entity_id)
        return result

    def get_all_unassociated_addresses(self, pool_id, entity_id):
        result = self.network_controller.get_all_unassociated_addresses(pool_id, entity_id)
        return result

    def get_all_addresses(self, pool_id):
        result = self.network_controller.get_all_addresses(pool_id)
        return result

    def get_all_ip_pools(self):
        result = self.network_controller.get_all_ip_pools()
        return result



