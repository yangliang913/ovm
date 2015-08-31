import pylons
import simplejson as json
from stackone.controllers.ControllerBase import ControllerBase
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.NetworkService import NetworkService
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
from stackone.model.Authorization import AuthorizationService
LOGGER = logging.getLogger('stackone.controllers')
from stackone.controllers.NetworkController import NetworkController
from stackone.controllers.XMLRPC.NetworkXMLRPCController import NetworkXMLRPCController
from pylons.controllers.util import forward
from pylons.controllers import XMLRPCController

class NetworkAjaxController(ControllerBase):
    network_controller = NetworkController()

    @expose(template='json')
    def add_nw_defn(self, nw_name, nw_desc, nw_type, nw_bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id=None, op_level=None, group_id=None, node_id=None, nw_gateway=None, nw_ip_address=None, nw_use_vlan=None, nw_vlan_id=None, nw_isbonded=None, nw_slaves=None, interface=None, vlan_id_pool_id=None):
        result = None
        result = self.network_controller.add_nw_defn(nw_name, nw_desc, nw_type, nw_bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id, group_id, node_id, op_level, nw_gateway, nw_ip_address, nw_use_vlan, nw_vlan_id, nw_isbonded, nw_slaves, interface, vlan_id_pool_id)
        return result

    @expose(template='json')
    def add_vlan_id_pool(self, site_id, name, desc, range, interface, sp_ids, cidr, num_hosts, **kw):
        result = None
        result = self.network_controller.add_vlan_id_pool(site_id, name, desc, range, interface, sp_ids, cidr, num_hosts)
        return result
        
    @expose()
    def associate_defns(self, def_ids, def_type, site_id=None, op_level=None, group_id=None):
        result = None
        result = self.network_controller.associate_defns(def_ids, def_type, site_id, op_level, group_id)
        return result
        
    @expose()
    def associate_nw_defns(self, def_ids, def_type, site_id=None, op_level=None, group_id=None, node_id=None):
        result = None
        result = self.network_controller.associate_nw_defns(def_ids, def_type, site_id, op_level, group_id, node_id)
        return result
        
    @expose(template='json')
    def create_public_ip_pool(self, pool_infos, _dc=None):
        result = None
        result = self.network_controller.create_public_ip_pool(pool_infos)
        return result

    @expose(template='json')
    def edit_nw_defn(self, nw_id, nw_name, nw_desc):
        result = None
        result = self.network_controller.edit_nw_defn(nw_id, nw_name, nw_desc)
        return result

    @expose(template='json')
    def edit_vlan_id_pool(self, site_id, vlan_id_pool_id, desc, range, sp_ids, name, **kw):
        result = None
        result = self.network_controller.edit_vlan_id_pool(site_id, vlan_id_pool_id, desc, range, sp_ids, name)
        return result
    
    @expose(template='json')
    def get_all_public_ip_pool(self, _dc=None):
        result = None
        result = self.network_controller.get_all_public_ip_pool()
        return result
    # sam 1025
    @expose(template='json')
    def get_available_nws(self, mode, op_level=None, node_id=None, image_id=None, _dc=None):
        result = self.network_controller.get_available_nws(mode, op_level, node_id,image_id)
        return result
        
    @expose(template='json')
    def get_bond_details(self, nw_id=None, _dc=None):
        result = None
        result = self.network_controller.get_bond_details(nw_id)
        return result
        
    @expose(template='json')
    def get_bridge_prefix(self, _dc=None):
        result = None
        result = self.network_controller.get_bridge_prefix()
        return result
        
    @expose(template='json')
    def get_default_cidr(self, _dc=None):
        result = None
        result = self.network_controller.get_default_cidr()
        return result
    
    @expose(template='json')
    def get_default_interfaces(self, _dc=None):
        result = None
        result = self.network_controller.get_default_interfaces()
        return result
        
    @expose(template='json')
    def get_edit_network_details(self, nw_id):
        result = None
        result = self.network_controller.get_edit_network_details(nw_id)
        return result
        
    @expose(template='json')
    def get_interface(self, node_id, _dc=None):
        result = None
        result = self.network_controller.get_interface(node_id)
        return result
     # sam 1025   
    @expose(template='json')
    def get_network_models(self, image_id, _dc=None):
        result = None
        result = self.network_controller.get_network_models(image_id)
        return result
        
    @expose(template='json')
    def get_new_nw(self, image_id, mode, node_id=None):
        result = None
        result = self.network_controller.get_new_nw(image_id, mode, node_id)
        return result
        
    @expose(template='json')
    def get_new_private_bridge_name(self, node_id=None, group_id=None, site_id=None, op_level=None, _dc=None):
        result = None
        result = self.network_controller.get_new_private_bridge_name(node_id, group_id, site_id, op_level)
        return result
        
    @expose(template='json')
    def get_num_hosts(self, _dc=None):
        result = None
        result = self.network_controller.get_num_hosts()
        return result
        
    @expose(template='json')
    def get_nw_address_space_map(self, _dc=None):
        result = None
        result = self.network_controller.get_nw_address_space_map()
        return result

    @expose(template='json')
    def get_nw_dc_defns(self, site_id=None, op_level=None, group_id=None, node_id=None, _dc=None):
        result = None
        result = self.network_controller.get_nw_dc_defns(site_id, op_level, group_id, node_id)
        return result

    @expose(template='json')
    def get_nw_defns(self, site_id=None, op_level=None, group_id=None, node_id=None, _dc=None):
        result = None
        result = self.network_controller.get_nw_defns(site_id, op_level, group_id, node_id)
        return result

    @expose(template='json')
    def get_nw_det(self, bridge, mac, model, nw_id=None):
        result = None
        result = self.network_controller.get_nw_det(bridge, mac, model, nw_id)
        return result
        
    @expose(template='json')
    def get_nw_nat_fwding_map(self, node_id, _dc=None):
        result = None
        result = self.network_controller.get_nw_nat_fwding_map(node_id)
        return result

    @expose(template='json')
    def get_nws(self, image_id=None, op_level=None, node_id=None, dom_id=None, _dc=None):
        result = None
        result = self.network_controller.get_nws(image_id=image_id, dom_id=dom_id, node_id=node_id, op_level=op_level)
        return result
        
    @expose(template='json')
    def get_public_ips(self, cidr=None, ip_list=None, _dc=None):
        result = None
        result = self.network_controller.get_public_ips(cidr, ip_list)
        return result
        
    @expose(template='json')
    def get_server_nw_def_list(self, def_id, defType, site_id=None, group_id=None, _dc=None):
        result = None
        result = self.network_controller.get_server_nw_def_list(def_id, defType, site_id, group_id)
        return result
        
    @expose(template='json')
    def get_sp_list(self, site_id, def_id=None, pool_tag=None, pool_id=None, _dc=None):
        result = None
        result = self.network_controller.get_sp_list(site_id, def_id, pool_tag, pool_id)
        return result
        
    @expose(template='json')
    def get_vlan_id_pool_details(self, vlan_id_pool_id, _dc=None):
        result = None
        result = self.network_controller.get_vlan_id_pool_details(vlan_id_pool_id)
        return result
        
    @expose(template='json')
    def get_vlan_id_pools(self, _dc=None):
        result = None
        result = self.network_controller.get_vlan_id_pools()
        return result
        
    @expose(template='json')
    def nw_address_changed(self, ip_value, _dc=None):
        result = None
        result = self.network_controller.nw_address_changed(ip_value)
        return result
        
    @expose(template='json')
    def remove_nw_defn(self, def_id, site_id=None, op_level=None, group_id=None, node_id=None, _dc=None):
        result = None
        result = self.network_controller.remove_nw_defn(def_id, site_id, group_id, node_id, op_level)
        return result
        
    @expose(template='json')
    def remove_vlan_id_pool(self, site_id, vlan_id_pool_id, _dc=None):
        result = None
        result = self.network_controller.remove_vlan_id_pool(site_id, vlan_id_pool_id)
        return result
        
    @expose()
    def xmlrpc(self):
        return forward(NetworkXMLRPCController())
        