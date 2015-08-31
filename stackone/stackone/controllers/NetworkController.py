import pylons
import simplejson as json
from stackone.lib.base import BaseController
from stackone.core.utils.utils import getHexID
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.core.utils.utils import wait_for_task_completion
from stackone.model import *
from stackone.viewModel import Basic
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.viewModel.NetworkService import NetworkService
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
from stackone.viewModel.VLANService import VLANService
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
LOGGER = logging.getLogger('stackone.controllers')
from stackone.controllers.ControllerBase import ControllerBase

class NetworkController(ControllerBase):
    manager = Basic.getGridManager()
    network_service = NetworkService()
    tc = TaskCreator()
 
    def add_nw_defn(self, nw_name, nw_desc, nw_type, nw_bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id=None, group_id=None, node_id=None, op_level=None, nw_gateway=None, nw_ip_address=None, nw_use_vlan=None, nw_vlan_id=None, nw_isbonded=None, nw_slaves=None, interface=None, vlan_id_pool_id=None, sp_ids=None, csep_context_id=None, csep_id=None, nw_id=None, cp_id=None):
        try:
            self.authenticate()
            task_id = self.tc.add_nw_defn_task(session['auth'], nw_name, nw_desc, nw_type, nw_bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id, group_id, node_id, op_level, nw_gateway, nw_ip_address, nw_use_vlan, nw_vlan_id, nw_isbonded, nw_slaves, interface, vlan_id_pool_id, sp_ids, csep_context_id, csep_id, nw_id, cp_id)
        except Exception as ex:
            print_traceback()
            return "{success: false,msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"
        return "{'success': 'true','msg': 'Task submitted.','task_id':" + str(task_id) + '}'
        
    def add_vlan_id_pool(self, site_id, name, desc, range, interface, sp_ids, cidr, num_hosts):
        try:
            self.authenticate()
            result = self.network_service.add_vlan_id_pool(session['auth'], site_id, name, desc, range, interface, sp_ids, cidr, num_hosts)
            return result
        except Exception as ex:
            print_traceback()
            return "{success: false, msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"
        
    def associate_address(self, pool_id, ip_id, vm_id, csep_id):
        result = None
        result = self.network_service.associate_address(session['auth'], pool_id, ip_id, vm_id, csep_id)
        return result
        
    def associate_defns(self, def_ids, def_type, site_id=None, op_level=None, group_id=None):
        try:
            self.authenticate()
            self.tc.associate_defns_task(session['auth'], site_id, group_id, def_type, def_ids, op_level)
            return "{success: true,msg: 'Task submitted.'}"
        except Exception as ex:
            print_traceback()
            return "{success: false,msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"
    
    def associate_nw_defns(self, def_ids, def_type, site_id=None, op_level=None, group_id=None, node_id=None):
        try:
            self.authenticate()
            self.network_service.associate_nw_defns(site_id, group_id, node_id, def_type, def_ids, session['auth'], op_level)
            return "{success: true,msg: 'Task submitted.'}"
        except Exception as ex:
            print_traceback()
            return "{success: false,msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"
    
    def create_network(self, nw_name, nw_desc, nw_type, nw_bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id, group_id, node_id, op_level, nw_gateway, nw_ip_address, nw_use_vlan, nw_vlan_id, nw_isbonded, nw_slaves, interface, vlan_id_pool_id, sp_id, csep_context_id, csep_id, cp_id):
        nw_id = getHexID()
        t = self.add_nw_defn(nw_name, nw_desc, nw_type, nw_bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id, group_id, node_id, op_level, nw_gateway, nw_ip_address, nw_use_vlan, nw_vlan_id, nw_isbonded, nw_slaves, interface, vlan_id_pool_id, sp_id, csep_context_id, csep_id, nw_id, cp_id)
        t = eval(t)
        finish,status = wait_for_task_completion(t.get('task_id'), 5000)
        if finish == True and status == Task.SUCCEEDED:
            nw_def = DBSession.query(NwDef).filter(NwDef.id == nw_id).first()
            vlan_info = nw_def.vlan_info
            result = {'nw_id': nw_id, 'nw_vlan_id': vlan_info.get('vlan_id')}
            return result
            
    def create_private_pool(self, name, cidr, desc=None):
        result = None
        result = self.network_service.create_private_pool(session['auth'], name, cidr, desc)
        return result
        
    def create_public_ip_pool(self, pool_infos):
        try:
            result = self.network_service.create_public_ip_pool(session['auth'], pool_infos)
            return dict(success=True, rows=result)
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
    def create_public_pool(self, name, cidr, desc=None):
        result = None
        result = self.network_service.create_public_pool(session['auth'], name, cidr, desc)
        return result
        
    def delete_pool(self, pool_id):
        result = None
        result = self.network_service.delete_pool(session['auth'], pool_id, entity_id)
        return result
        
    def disassociate_address(self, pool_id, ip_id, csep_id):
        result = None
        result = self.network_service.disassociate_address(session['auth'], pool_id, ip_id, csep_id)
        return result
        
    def edit_nw_defn(self, nw_id, nw_name, nw_desc):
        try:
            self.authenticate()
            result = self.network_service.edit_nw_defn(nw_id, nw_name, nw_desc)
            return result
        except Exception as ex:
            print_traceback()
            return "{success: false, msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"
        
    def edit_vlan_id_pool(self, site_id, vlan_id_pool_id, desc, range, sp_ids, name):
        try:
            self.authenticate()
            result = self.network_service.edit_vlan_id_pool(session['auth'], site_id, vlan_id_pool_id, desc, range, sp_ids, name)
            return result
        except Exception as ex:
            print_traceback()
            return "{success: false, msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"
            
    def get_all_addresses(self, pool_id):
        result = None
        result = self.network_service.get_all_addresses(session['auth'], pool_id)
        return result
        
    def get_all_associated_addresses(self, pool_id, entity_id):
        result = None
        result = self.network_service.get_all_associated_addresses(session['auth'], pool_id, entity_id)
        return result
        
    def get_all_ip_pools(self):
        result = None
        result = self.network_service.get_all_ip_pools(session['auth'])
        return result
        
    def get_all_public_ip_pool(self):
        try:
            result = self.network_service.get_all_public_ip_pool(session['auth'])
            return dict(success=True, rows=result)
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
    
    def get_all_reserved_addresses(self, pool_id, entity_id=None):
        result = None
        result = self.network_service.get_all_reserved_addresses(session['auth'], pool_id, entity_id)
        return result

    def get_all_unassociated_addresses(self, pool_id, entity_id):
        result = None
        result = self.network_service.get_all_unassociated_addresses(session['auth'], pool_id, entity_id)
        return result
     # sam 1025   
    def get_available_nws(self, mode, op_level=None, node_id=None, image_id=None, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_available_nws(session['auth'], mode, node_id,image_id, op_level)
            return {'success': True, 'rows': result}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
    def get_bond_details(self, nw_id=None):
        try:
            result = None
            self.authenticate()
            result = self.network_service.get_bond_details(nw_id)
            return result
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
    def get_bridge_prefix(self):
        try:
            self.authenticate()
            result = self.network_service.get_bridge_prefix()
            return {'success': True, 'rows': result}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
    def get_default_cidr(self, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_default_cidr()
            return {'success': True, 'rows': result}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
            
    def get_default_interfaces(self, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_default_interfaces()
            return {'success': True, 'rows': result}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
    
    def get_edit_network_details(self, nw_id):
        try:
            self.authenticate()
            result = self.network_service.get_edit_network_details(nw_id)
            return dict(success=True, network=result)
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
    def get_interface(self, node_id, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_interface(session['auth'], node_id)
            return {'success': True, 'rows': result}
        except Exception as ex:
            print ex
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
    # sam 1025
    def get_network_models(self, image_id):
        self.authenticate()
        try:
            info = self.network_service.get_network_models(session['auth'],image_id)
            return {'success': True, 'rows': info}
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex))
            
    def get_new_nw(self, image_id, mode, node_id=None):
        try:
            result = None
            self.authenticate()
            result = self.network_service.get_new_nw(session['auth'], image_id, mode, node_id)
            return {'success': True, 'rows': result}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

        
    def get_new_private_bridge_name(self, node_id=None, group_id=None, site_id=None, op_level=None, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_new_private_bridge_name(session['auth'], node_id, group_id, site_id, op_level)
            return dict(success=True, bridge=result)
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def get_num_hosts(self, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_num_hosts()
            return {'success': True, 'rows': result}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
    def get_nw_address_space_map(self, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_nw_address_space_map()
            return {'success': True, 'nw_address_space': result}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
    def get_nw_dc_defns(self, site_id=None, op_level=None, group_id=None, node_id=None, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_nw_dc_defns(session['auth'], site_id, group_id, node_id)
            return {'success': True, 'rows': result}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
    
    def get_nw_defns(self, site_id=None, op_level=None, group_id=None, node_id=None, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_nw_defns(session['auth'], site_id, group_id, node_id, op_level)
            return {'success': True, 'rows': result}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
    def get_nw_det(self, bridge, mac, model, nw_id):
        try:
            self.authenticate()
            result = self.network_service.get_nw_det(bridge, mac, model, nw_id)
            return {'success': True, 'nw_det': result}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
    
    def get_nw_nat_fwding_map(self, node_id, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_nw_nat_fwding_map(session['auth'], node_id)
            return {'success': True, 'nw_nat': result}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
    def get_nws(self, image_id=None, op_level=None, node_id=None, dom_id=None, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_nws(session['auth'], image_id, dom_id, node_id, op_level)
            return {'success': True, 'rows': result}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
    
    def get_public_ips(self, cird, ip_list):
        try:
            result = self.network_service.get_public_ips(session['auth'], cird, ip_list)
            return dict(success=True, rows=result)
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
                
    def get_server_nw_def_list(self, def_id, defType, site_id=None, group_id=None, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.get_server_def_list(site_id, group_id, def_id)
            return result
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
            
    def get_sp_list(self, site_id, def_id=None, pool_tag=None, pool_id=None, _dc=None):
        try:
            result = self.manager.get_sp_list(site_id, def_id, session['auth'], pool_tag, pool_id)
            return result
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
    def get_vlan_id_pool_details(self, vlan_id_pool_id):
        try:
            self.authenticate()
            result = VLANService().get_vlan_id_pool_details(vlan_id_pool_id)
            return {'success': True, 'rows': result}
        except Exception as ex:
            print_traceback()
            return "{success: false, msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"
            
    def get_vlan_id_pools(self):
        try:
            self.authenticate()
            result = VLANService().get_vlan_id_pools()
            return {'success': True, 'rows': result}
        except Exception as ex:
            print_traceback()
            return "{success: false, msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"

        
    def nw_address_changed(self, ip_value, _dc=None):
        try:
            self.authenticate()
            result = self.network_service.nw_address_changed(ip_value)
            return dict(success=True, range=result)
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
    
    def release_address(self, pool_id, entity_id, ip_id=None):
        result = None
        result = self.network_service.release_address(session['auth'], pool_id, entity_id, ip_id)
        return result
        
    def remove_network(self, def_id, site_id=None, group_id=None, node_id=None, op_level=None, csep_id=None, cp_id=None):
        t = self.remove_nw_defn(def_id, site_id, group_id, node_id, op_level, csep_id, cp_id)
        t = eval(t)
        finish,status = wait_for_task_completion(t.get('task_id'), 5000)
        if finish == True and status == Task.SUCCEEDED:
            return "{'success': 'true','msg': 'Task submitted.'}"
        else:
            raise Exception('Could not remove the network')

        
    def remove_nw_defn(self, def_id, site_id=None, group_id=None, node_id=None, op_level=None, csep_id=None, cp_id=None):
        try:
            self.authenticate()
            task_id = self.tc.remove_nw_defn_task(session['auth'], def_id, site_id, group_id, node_id, op_level, csep_id, cp_id)
            return "{'success': 'true','msg': 'Task submitted.','task_id':" + str(task_id) + '}'
        except Exception as ex:
            print_traceback()
            return "{success: false,msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"
    
    def remove_vlan_id_pool(self, site_id, vlan_id_pool_id):
        try:
            self.authenticate()
            self.tc.remove_vlan_id_pool_task(session['auth'], site_id, vlan_id_pool_id)
            return "{success: true, msg: 'Task submitted.'}"
        except Exception as ex:
            print_traceback()
            return "{success: false, msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"
            
    def reserve_address(self, pool_id, entity_id):
        result = None
        result = self.network_service.reserve_address(session['auth'], pool_id, entity_id)
        return result        
