from sqlalchemy import func, outerjoin, join
import simplejson as json
from stackone.model.VM import vifEntry
from stackone.core.utils.utils import dynamic_map, randomMAC, get_ips_from_range, get_ips_from_cidr
from stackone.core.utils.utils import to_unicode, to_str, print_traceback, getHexID, is_cidr, get_cms_network_service_node
from stackone.core.utils.IPy import *
from stackone.viewModel.NodeService import NodeService
from stackone.viewModel.ImageService import ImageService
import Basic
from stackone.model import DBSession
from stackone.model.network import NwDef, NwManager
from stackone.model.Groups import ServerGroup
from stackone.model.SPRelations import ServerDefLink, SPDefLink, DCDefLink, CSEPDefLink
from stackone.model.ManagedNode import ManagedNode
from stackone.model.IPManager import IPManager
from stackone.model.SyncDefinition import SyncDef
from stackone.model.Sites import Site
from stackone.viewModel.VLANService import VLANService
import stackone.core.utils.utils
from stackone.core.utils.constants import *
constants = stackone.core.utils.constants
from stackone.model.DBHelper import DBHelper
from stackone.model.VM import VM
from stackone.model.VLANManager import VLANIDPool
import netaddr
import logging
import tg

LOGGER = logging.getLogger('stackone.viewModel')
nw_type_map = {NwDef.PUBLIC_NW: 'Public', NwDef.HOST_PRIVATE_NW: 'Host Private ', NwDef.VLAN_NW: 'VLAN', NwDef.NETWORK: 'Network'}
available_nws = [{'name': 'Default', 'value': '$DEFAULT_BRIDGE'}, {'name': 'xenbr0', 'value': 'xenbr0'}, {'name': 'xenbr1', 'value': 'xenbr1'}, {'name': 'xenbr2', 'value': 'xenbr2'}, {'name': 'br0', 'value': 'br0'}, {'name': 'br1', 'value': 'br1'}, {'name': 'br2', 'value': 'br2'}, {'name': 'eth0', 'value': 'eth0'}, {'name': 'eth1', 'value': 'eth1'}, {'name': 'eth2', 'value': 'eth2'}]

class NetworkService:
    #PASSED
    def __init__(self):
        self.nw_manager = Basic.getNetworkManager()
        self.managed_node = Basic.getManagedNode()
        self.sync_manager = SyncDef()
        self.manager = Basic.getGridManager()
        self.ip_manager = IPManager()
    
    #PASSED
    def add_nw_defn(self, auth, nw_name, nw_desc, nw_type, nw_bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id, group_id, node_id, op_level=None, nw_gateway=None, nw_ip_address=None, nw_use_vlan=None, nw_vlan_id=None, nw_isbonded=None, nw_slaves=None, interface=None, vlan_id_pool_id=None, sp_ids=None, csep_context_id=None, csep_id=None, nw_id=None):
        group = None
        managed_node = None
        vlan_id_pool_rec = None
        new_nw_def = None
        site = None
        if not nw_id:
            nw_id = getHexID()
        scope = op_level
        if site_id == 'data_center':
            site = self.manager.getSiteByGroupId(group_id)
            if site:
                site_id = site.id
        else:
            site = self.manager.getSite(site_id)
            
        group_list = self.manager.getGroupList(auth, site_id)
        try:
            if vlan_id_pool_id:
                vlan_id_pool_rec = VLANService().get_vlan_id_pool(vlan_id_pool_id)
                context = {}
                pool_tag = constants.VLAN_ID_POOL
                context['pool_id'] = vlan_id_pool_id
                context['nw_def_id'] = nw_id
                nw_vlan_id, interface = VLANService().get_unused_id(pool_tag, context)
                vlan_nw_info_db = VLANService().get_vlan_network_info_by_vlan_id(nw_vlan_id, vlan_id_pool_id)
                nw_address_space = vlan_nw_info_db.cidr
                nw_dhcp_range = to_str(vlan_nw_info_db.dhcp_start) + '-' + to_str(vlan_nw_info_db.dhcp_end)
                nw_gateway = vlan_nw_info_db.gateway
                nw_bridge = vlan_nw_info_db.bridge
            
            errors = self.validate_new_nw_def(auth, 'ADD', nw_type, nw_name, nw_desc, nw_bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id, group_id, node_id, scope)
            if errors:
                if len(errors) > 0:
                    LOGGER.error(to_str(errors))
                    raise Exception(errors)
            
            if nw_type == NwDef.PUBLIC_NW:
                bridge_info = dynamic_map()
                bridge_info.name = nw_bridge
                bridge_info.phy_list = nw_phy_if
                new_nw_def = NwDef(nw_id, nw_type, nw_name, nw_desc, False, scope, bridge_info=bridge_info)
            
            if nw_type == NwDef.VLAN_NW:
                bridge_info = dynamic_map()
                bridge_info.name = nw_bridge
                ipv4_info = dynamic_map()
                ipv4_info.ip_network = nw_address_space
                ipv4_info.gateway = nw_gateway
                ipv4_info.ip_address = nw_ip_address
                vlan_info = dynamic_map()
                vlan_info.use_vlan = nw_use_vlan
                vlan_info.vlan_id = nw_vlan_id
                vlan_info.interface = interface
                if vlan_id_pool_rec:
                    vlan_info.vlan_id_pool_id = vlan_id_pool_rec.id
                    vlan_info.vlan_id_pool_name = vlan_id_pool_rec.name
                else:
                    vlan_info.vlan_id_pool_id = ''
                    vlan_info.vlan_id_pool_name = ''
                
                if nw_address_space:
                    if nw_dhcp_range:
                        ip = IP(nw_address_space, make_net=True)
                        bridge_info.ip_address = ip[1].strNormal()
                        bridge_info.netmask = ip.netmask().strNormal()
                    else:
                        bridge_info.ip_address = ''
                        bridge_info.netmask = ''
                
                dhcp_info = dynamic_map()
                if nw_dhcp_range:
                    r = nw_dhcp_range.split('-')
                    if len(r) == 2:
                        dhcp_info.dhcp_start = r[0].strip()
                        dhcp_info.dhcp_end = r[1].strip()
                else:
                    dhcp_info.dhcp_start = ''
                    dhcp_info.dhcp_end = ''
                
                nat_info = dynamic_map()
                nat_info.interface = nw_nat_fwding
                bond_info = dynamic_map()
                bond_info.is_bonded = nw_isbonded
                bond_info.slave_list = []
                if nw_slaves:
                    slave_list = nw_slaves.split(',')
                    if slave_list:
                        bond_info.slave_list = slave_list
                
                new_nw_def = NwDef(nw_id, nw_type, nw_name, nw_desc, False, csep_context_id, scope, bridge_info=bridge_info, vlan_info=vlan_info, bond_info=bond_info, ipv4_info=ipv4_info, dhcp_info=dhcp_info, nat_info=nat_info)
                new_nw_def.bridge_info = self.get_dic(new_nw_def.bridge_info)
                new_nw_def.vlan_info = self.get_dic(new_nw_def.vlan_info)
                new_nw_def.bond_info = self.get_dic(new_nw_def.bond_info)
                new_nw_def.ipv4_info = self.get_dic(new_nw_def.ipv4_info)
                new_nw_def.dhcp_info = self.get_dic(new_nw_def.dhcp_info)
                new_nw_def.nat_info = self.get_dic(new_nw_def.nat_info)
                if group_id:
                    group = DBSession.query(ServerGroup).filter_by(id=group_id).first()
                
                managed_node = NodeService().get_managed_node(auth, node_id)
                errs = []
                alldefns = []
                if scope == constants.SCOPE_S:
                    alldefns = DBSession.query(ServerDefLink).filter_by(server_id=managed_node.id, def_type=to_unicode(constants.NETWORK))
                elif scope == constants.SCOPE_SP:
                    alldefns = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_type=to_unicode(constants.NETWORK))
                elif scope == constants.SCOPE_DC:
                    alldefns = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type=to_unicode(constants.NETWORK))
                
                for node_defn in alldefns:
                    rowNF = DBSession.query(NwDef).filter_by(id=node_defn.def_id, name=new_nw_def.name).first()
                    if rowNF:
                        raise Exception('Network definition with the same name already exists')
                
                scan_result = None
                if sp_ids:
                    sp_ids = sp_ids
                else:
                    if group:
                        sp_ids = group.id
                
                errs, nw_id = self.sync_manager.add_defn(new_nw_def, site, group, managed_node, auth, to_unicode(constants.NETWORK), constants.ATTACH, 'ADD_NETWORK_DEF', self.nw_manager, self.manager, scope, sp_ids, scan_result, csep_id)
                if errs:
                    if len(errs) > 0:
                        add_mode = True
                        self.sync_manager.remove_defn(new_nw_def, site, group, managed_node, auth, to_unicode(constants.NETWORK), constants.DETACH, 'REMOVE_NETWORK_DEF', self.nw_manager, self.manager, add_mode, group_list, scope, csep_id)
                        return {'success': False, 'msg': to_str(errs).replace("'", '')}
                
            else:
                bridge_info = dynamic_map()
                bridge_info.name = nw_bridge
                ipv4_info = dynamic_map()
                ipv4_info.ip_network = nw_address_space
                ip = IP(nw_address_space)
                bridge_info.ip_address = ip[1].strNormal()
                bridge_info.netmask = ip.netmask().strNormal()
                dhcp_info = dynamic_map()
                r = nw_dhcp_range.split('-')
                if len(r) == 2:
                    dhcp_info.dhcp_start = r[0].strip()
                    dhcp_info.dhcp_end = r[1].strip()
                
                nat_info = dynamic_map()
                nat_info.interface = nw_nat_fwding
                new_nw_def = NwDef(nw_id, nw_type, nw_name, nw_desc, False, csep_context_id, scope, bridge_info=bridge_info, ipv4_info=ipv4_info, dhcp_info=dhcp_info, nat_info=nat_info)
                new_nw_def.bridge_info = self.get_dic(new_nw_def.bridge_info)
                new_nw_def.vlan_info = self.get_dic(new_nw_def.vlan_info)
                new_nw_def.bond_info = self.get_dic(new_nw_def.bond_info)
                new_nw_def.ipv4_info = self.get_dic(new_nw_def.ipv4_info)
                new_nw_def.dhcp_info = self.get_dic(new_nw_def.dhcp_info)
                new_nw_def.nat_info = self.get_dic(new_nw_def.nat_info)
                group = None
                if group_id:
                    group = DBSession.query(ServerGroup).filter_by(id=group_id).first()
                
                managed_node = NodeService().get_managed_node(auth, node_id)
                errs = []
                if scope == constants.SCOPE_S:
                    alldefns = DBSession.query(ServerDefLink).filter_by(server_id=managed_node.id, def_type=to_unicode(constants.NETWORK))
                elif scope == constants.SCOPE_SP:
                    alldefns = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_type=to_unicode(constants.NETWORK))
                elif scope == constants.SCOPE_DC:
                    alldefns = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type=to_unicode(constants.NETWORK))
                
                for node_defn in alldefns:
                    rowNF = DBSession.query(NwDef).filter_by(id=node_defn.def_id, name=new_nw_def.name).first()
                    if rowNF:
                        raise Exception('Network definition with the same name already exists')
                    rowNF = DBSession.query(NwDef).filter_by(id=node_defn.def_id).first()
                    if rowNF:
                        if new_nw_def.ipv4_info.get('ip_network') == rowNF.ipv4_info.get('ip_network'):
                            raise Exception('Network definition with the same address space already exists')
                        continue
                (errs, nw_id) = self.sync_manager.add_defn(new_nw_def, site, group, managed_node, auth, to_unicode(constants.NETWORK), constants.ATTACH, 'ADD_NETWORK_DEF', self.nw_manager, self.manager, scope)
                if scope == constants.SCOPE_DC or scope == constants.SCOPE_SP:
                    oos_count = 0
                    status = to_unicode(constants.IN_SYNC)
                    details = None
                    self.sync_manager.add_node_defn(managed_node.id, new_nw_def.id, to_unicode(constants.NETWORK), status, details)
                    op = constants.ATTACH
                    update_status = True
                    errs = []
                    self.nw_manager.sync_node_defn(auth, managed_node, group_id, site_id, new_nw_def, to_unicode(constants.NETWORK), op, self.nw_manager, update_status, errs)
                
                if errs:
                    if len(errs) > 0:
                        add_mode = True
                        self.sync_manager.remove_defn(new_nw_def, site, group, managed_node, auth, to_unicode(constants.NETWORK), constants.DETACH, 'REMOVE_NETWORK_DEF', self.nw_manager, self.manager, add_mode, group_list, scope, csep_id)
                        return {'success': False, 'msg': to_str(errs).replace("'", '')}
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            add_mode = True
            try:
                if vlan_id_pool_id:
                    pool_tag = constants.VLAN_ID_POOL
                    context = {}
                    context['vlan_id'] = nw_vlan_id
                    context['pool_id'] = vlan_id_pool_id
                    VLANService().release_id(pool_tag, context)
                
                if new_nw_def:
                    self.sync_manager.remove_defn(new_nw_def, site, group, managed_node, auth, to_unicode(constants.NETWORK), constants.DETACH, 'REMOVE_NETWORK_DEF', self.nw_manager, self.manager, add_mode, group_list, scope, csep_id)
            except Exception as ex1:
                print_traceback()
                LOGGER.error(to_str(ex1).replace("'", ''))
            raise Exception(ex)
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'msg': 'Network Added', 'nw_id': nw_id, 'nw_vlan_id': nw_vlan_id}
        

    #PASSED
    def add_vlan_id_pool(self, auth, site_id, name, desc, range, interface, sp_ids, cidr, num_hosts):
        from stackone.viewModel.TaskCreator import TaskCreator
        fixed_net = netaddr.IPNetwork(cidr)
        nums = range.split('-')
        first_num = int(nums[0])
        last_num = int(nums[1])
        num_networks = int(last_num) - int(first_num)
        network_size = int(num_hosts)
        if len(fixed_net) < num_networks * network_size:
            raise ValueError('The %s is not big enough to fit %s networks with %s hosts each. (%s < %s)' % (cidr, num_networks, network_size, len(fixed_net), num_networks * network_size))
        tc = TaskCreator()
        tc.add_vlan_id_pool_task(auth, site_id, name, desc, range, interface, sp_ids, cidr, num_hosts)
        return "{success: true, msg: 'Task submitted.'}"  
    #PASSED
    def associate_address(self, auth, pool_id, ip_id, vm_id, csep_id=None):
        LOGGER.info('Associating address...')
        try:
            ip_db = self.ip_manager.associate_address(pool_id, ip_id, vm_id, csep_id)
            return self.ip_manager.remove_cidr_format_from_ip(ip_db.ip)
        except Exception as ex:
            print_traceback()
            return False
            
    #PASSED
    def associate_defns(self, site_id, group_id, def_type, def_ids, auth, op_level=None):
        site = self.manager.getSite(site_id)
        group = self.manager.getGroup(auth, group_id)
        group_list = self.manager.getGroupList(auth, site_id)
        def_id_list = def_ids.split(',')
        
        for def_id in def_id_list:
            defn = DBSession.query(NwDef).filter_by(id=def_id).first()
            node = None
            sp_ids = group_id
            try:
                self.sync_manager.add_defn(defn, site, group, node, auth, to_unicode(constants.NETWORK), constants.ATTACH, 'ADD_NETWORK_DEF', self.nw_manager, self.manager, op_level, sp_ids)
            except Exception as ex:
                print_traceback()
                LOGGER.error(to_str(ex).replace("'", ''))
                add_mode = True
                self.sync_manager.remove_defn(defn, site, group, node, auth, to_unicode(constants.NETWORK), constants.DETACH, 'REMOVE_NETWORK_DEF', self.nw_manager, self.manager, add_mode, group_list, op_level)
                raise Exception(ex)
                
        return {'success': True, 'msg': 'Network Added'}
        
        
    #PASSED
    def associate_nw_defns(self, site_id, group_id, node_id, def_type, def_ids, auth, op_level=None):
        site = self.manager.getSite(site_id)
        group = self.manager.getGroup(auth, group_id)
        def_id_list = def_ids.split(',')
        for def_id in def_id_list:
            defn = self.nw_manager.get_defn(def_id)
            node = DBSession.query(ManagedNode).filter_by(id=node_id).first()
            try:
                self.sync_manager.add_defn(defn, site, group, node, auth, to_unicode(constants.NETWORK), constants.ATTACH, 'ADD_NETWORK_DEF', self.nw_manager, self.manager, op_level, None)
            except Exception as ex:
                print_traceback()
                LOGGER.error(to_str(ex).replace("'", ''))
                add_mode = True
                group_list = self.manager.getGroupList(auth, site_id)
                self.sync_manager.remove_defn(defn, site, group, node, auth, to_unicode(constants.NETWORK), constants.DETACH, 'REMOVE_NETWORK_DEF', self.nw_manager, self.manager, add_mode, group_list, op_level)
                return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'msg': 'Network Added'}
        
        
    #PASSED
    def create_private_pool(self, auth, name, cidr, desc=None):
        try:
            result = self.ip_manager.create_private_pool(name, cidr, desc)
            return result
        except Exception as ex:
            print_traceback()
            return False
            
    #PASSED
    def create_public_ip_pool(self, auth, pool_infos):
        from pprint import pprint
        pool_infos = json.loads(pool_infos)
        pool_info = pool_infos.get('pool_info')
        remove_pools = pool_infos.get('remove_public_ip_pools')
        if remove_pools:
            remove_pools = [x for x in remove_pools if x]
            for pool_id in remove_pools:
                if not self.ip_manager.can_remove_pool(pool_id):
                    raise Exception('Can not delete pool:%s, reserved ips exist' % pool_id)
            self.ip_manager.delete_pool(remove_pools)
            return None
            
        if pool_info:
            name = pool_info.get('name')
            cidr = pool_info.get('cidr')
            cidr_radio = pool_info.get('cidr_radio')
            iplist = pool_info.get('iplist')
            iplist_radio = pool_info.get('iplist_radio')
            pool_id = pool_info.get('pool_id')
            iplist = self.get_public_ips(auth, cidr, iplist)
            if not pool_id:
                pool = self.ip_manager.create_public_pool(name, cidr, iplist=iplist)
            else:
                pool = self.ip_manager.get_pool_by_id(pool_id)
                if len(iplist):
                    self.ip_manager.delete_ip(iplist, pool_id, cidr)
                    self.ip_manager.add_new_ip(pool_id, iplist, cidr)
                    pool.name = name
                    pool.cidr = cidr
                    pool.total = len(pool.ips)
                    DBSession.add(pool)
            ips = []
            for ip in pool.ips:
                ips.append({'id': ip.id, 'ip': ip.ip, 'is_selected': True, 'can_remove': self.ip_manager.can_remove_ip(ip.id)})
            return {'id': pool.id, 'name': pool.name, 'cidr': pool.cidr, 'iplist': ips, 'total_ips': len(pool.ips), 'available_ips': len(self.ip_manager.get_all_available_ips(pool.id))}
            
        
        
    #PASSED
    def create_public_pool(self, auth, name, cidr, desc=None):
        try:
            result = self.ip_manager.create_public_pool(name, cidr, desc)
            return result
        except Exception as ex:
            print_traceback()
            return False
            
    #PASSED
    def delete_pool(self, auth, pool_id):
        try:
            result = self.ip_manager.delete_pool(pool_id)
            return result
        except Exception as ex:
            print_traceback()
            return False

            
    #PASSED
    def disassociate_address(self, auth, pool_id, ip_id, csep_id=None):
        LOGGER.info('Disassociating address...')
        try:
            ip_db = self.ip_manager.disassociate_address(pool_id, ip_id, csep_id)
            return self.ip_manager.remove_cidr_format_from_ip(ip_db.ip)
        except Exception as ex:
            print_traceback()
            return False
            
    ##########$$$$$$$$$$$$$$$$$PASSED
    def edit_nw_defn(self, nw_id, nw_name, nw_desc, csep_id=None):
        nw_name = nw_name
        nw_desc = nw_desc
        try:
            errmsgs = []
            common_desc = {'Network name': nw_name, 'Network description': nw_desc}
            for key in common_desc:
                v = common_desc.get(key)
                if not v:
                    errmsgs.append('%s is required.' % (key))
            
            if errmsgs:
                if len(errmsgs) > 0:
                    return {'success': False, 'msg': to_str(errmsgs).replace("'", '')}
            
            row = DBSession.query(SPDefLink).filter_by(def_id=nw_id).first()
            if row:
                scope = constants.SCOPE_SP
            else:
                scope = constants.SCOPE_S
            
            alldefns = None
            if scope == constants.SCOPE_S:
                node_defn = DBSession.query(ServerDefLink).filter_by(def_id=nw_id).first()
                if node_defn:
                    alldefns = DBSession.query(ServerDefLink).filter_by(server_id=node_defn.server_id, def_type=to_unicode(constants.NETWORK))
            else:
                if scope == constants.SCOPE_SP:
                    group_defn = DBSession.query(SPDefLink).filter_by(def_id=nw_id).first()
                    if group_defn:
                        alldefns = DBSession.query(SPDefLink).filter_by(group_id=group_defn.group_id, def_type=to_unicode(constants.NETWORK))
                else:
                    if scope == constants.SCOPE_DC:
                        group_defn = DBSession.query(DCDefLink).filter_by(def_id=nw_id).first()
                        if group_defn:
                            alldefns = DBSession.query(DCDefLink).filter_by(site_id=group_defn.site_id, def_type=to_unicode(constants.NETWORK))
                    else:
                        if scope == constants.SCOPE_CP:
                            csep_defn = DBSession.query(CPDefLink).filter_by(def_id=nw_id).first()
                            if csep_defn:
                                alldefns = DBSession.query(CPDefLink).filter_by(csep_id=csep_id, def_type=to_unicode(constants.NETWORK))
            
            if alldefns:
                for eachdefn in alldefns:
                    defnTemp = DBSession.query(NwDef).filter_by(id=eachdefn.def_id, name=nw_name).first()
                    if defnTemp and defnTemp.id != nw_id:
                        raise Exception('Network definition with the same name already exists')
            
            defn = DBSession.query(NwDef).filter_by(id=nw_id).first()
            group = None
            auth = None
            op_level = None
            sp_ids = None
            grid_manager = None
            self.sync_manager.update_defn(defn, nw_name, nw_desc, None, group, auth, constants.NETWORK, constants.ATTACH, self.nw_manager, 'UPDATE_NETWORK_DEF', op_level, sp_ids, grid_manager, csep_id)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'msg': ''}
        
    #PASSED
    def edit_vlan_id_pool(self, auth, site_id, vlan_id_pool_id, desc, range, sp_ids, name):
        from stackone.viewModel.TaskCreator import TaskCreator
        tc = TaskCreator()
        nums = range.split('-')
        first_num = int(nums[0])
        last_num = int(nums[1])
        num_networks = int(last_num) - int(first_num)
        vlan_id_pool = DBSession.query(VLANIDPool).filter_by(id=vlan_id_pool_id).first()
        cidr = vlan_id_pool.cidr
        fixed_net = netaddr.IPNetwork(cidr)
        network_size = int(vlan_id_pool.num_hosts)
        if len(fixed_net) < num_networks * network_size:
            raise ValueError('The %s is not big enough to fit %s networks with %s hosts each. (%s < %s)' % (cidr, num_networks, network_size, len(fixed_net), num_networks * network_size))
            
        tc.edit_vlan_id_pool_task(auth, site_id, vlan_id_pool_id, desc, range, sp_ids, name)
        return "{success: true, msg: 'Task submitted.'}"
        
    #PASSED
    def find_nw(self, vif, op_level=None):
        bridge_name = vif.get_bridge()
        site_id = None
        group_id = None
        for defn in self.nw_manager.get_defns(to_unicode(constants.NETWORK), site_id, group_id, self.managed_node.id, op_level):
            if defn.bridge_info and defn.bridge_info['name'] == bridge_name:
                return defn
                
    #PASSED
    def get_all_addresses(self, auth, pool_id):
        try:
            result = self.ip_manager.get_all_addresses(pool_id)
            return result
        except Exception as ex:
            print_traceback()
            return False
            
    #PASSED
    def get_all_associated_addresses(self, auth, pool_id, entity_id):
        try:
            result = self.ip_manager.get_all_associated_addresses(pool_id, entity_id)
            return result
        except Exception as ex:
            print_traceback()
            return False
            
    #PASSED
    def get_all_ip_pools(self, auth):
        result = []
        return result
        
    #PASSED
    def get_all_known_bridges(self, auth, node_id, group_id, site_id, op_level=None):
        bridge_names = []
        managed_node = NodeService().get_managed_node(auth, node_id)
        if managed_node is not None:
            bridges = managed_node.get_bridge_info()
            if bridges:
                bridge_names = bridge_names + bridges.keys()

        if self.nw_manager:
            defns = self.nw_manager.get_defns(to_unicode(constants.NETWORK), site_id, group_id, node_id, op_level)
            if defns is not None:
                for defn in defns:
                    if defn.bridge_info and  defn.bridge_info['name']:
                        n = defn.bridge_info['name']
                        if n not in bridge_names:
                            bridge_names.append(n)
        
        return bridge_names
    
    #PASSED
    def get_all_public_ip_pool(self, auth):
        result = []
        pools = self.ip_manager.get_all_public_ip_pools()
        for pool in pools:
            ips_lst = []
            ips = pool.get_all_ips()
            for ip in ips:
                ips_lst.append({'id': ip.id, 'ip': ip.ip, 'is_selected': True, 'can_remove': self.ip_manager.can_remove_ip(ip.id)})
            total_ips = len(pool.ips)
            result.append({'id': pool.id, 'name': pool.name, 'total_ips': total_ips, 'available_ips': len(self.ip_manager.get_all_available_ips(pool.id)), 'cidr': pool.cidr, 'iplist': '000', 'ip_info': ips_lst, 'can_remove': self.ip_manager.can_remove_pool(pool.id)})
            
        return result
    
    #PASSED
    def get_all_reserved_addresses(self, auth, pool_id, entity_id=None):
        try:
            result = self.ip_manager.get_all_reserved_addresses(pool_id, entity_id)
            return result
        except Exception as ex:
            print_traceback()
            return False

            
    #PASSED
    def get_all_unassociated_addresses(self, auth, pool_id, entity_id):
        try:
            result = self.ip_manager.get_all_unassociated_addresses(pool_id, entity_id)
            return result
        except Exception as ex:
            print_traceback()
            return False
            
    #PASSED
    def get_available_nws(self, auth, mode, node_id,image_id, op_level=None):
        result = []
        image = ImageService().get_image(auth,image_id)
        # changed by Alex
        if not image and mode in ('edit_image_settings', 'provision_vm', 'provision_image'):
            msg = 'Could not find Template with ID:%s' %image_id
            raise Exception(msg)
        
        
        if mode in ('edit_image_settings',):
            result.extend([nw for nw in image.get_default_available_networks()])
            nw_defns = self.nw_manager.get_dc_level_nw_defns()
            for nw_def in nw_defns:
                result.append({'name': nw_def.bridge_info.get('name'), 'value': nw_def.bridge_info.get('name'), 'nw_id': nw_def.id})
        else:
            nw_map = {}
            managed_node = NodeService().get_managed_node(auth, node_id)
            if not managed_node:
                msg = 'Could not find Server with ID:%s' %node_id
                raise Exception(msg)
            if mode in ('provision_vm', 'provision_image'):
                nw_map['Default'] = '$DEFAULT_BRIDGE'
                default_nw  = image.get_default_network()
                if default_nw:
                    result.append(default_nw)
            bridges = managed_node.get_bridge_info()
            virtual_networks = managed_node.get_virtual_networks_info()
            
            
            site_id = None
            group_id = None
            op_level = None
            for nw in self.nw_manager.get_defns(to_unicode(constants.NETWORK), site_id, group_id, node_id, op_level):
                bridge = None
                network = None
                if nw.ipv4_info and nw.ipv4_info.get('ip_network'):
                    network = nw.ipv4_info.get('ip_network')
                    
                if nw.bridge_info and nw.bridge_info.get('name'):
                    bridge = nw.bridge_info.get('name')
                    
                if bridge and network:
                    desc = '%s (%s, %s)' % (nw.name, bridge, network)
                else:
                    if bridge:
                        desc = '%s (%s)' % (nw.name, bridge)
                    else:
                        if network:
                            desc = '%s (%s)' % (nw.name, network)
                            
                if nw.bridge_info and nw.bridge_info.get('name'):
                    nw_map[desc] = nw.bridge_info.get('name')
                    result.append(dict(value=nw.bridge_info.get('name'), name=desc, nw_id=nw.id))

            if bridges is not None:
                for n in bridges.itervalues():
                    name = n['name']
                    if name not in nw_map.itervalues():
                        desc = name + ' network'
                        if n.get('network'):
                            desc = '%s (%s,%s)' % (desc, name, n['network'])
                        
                        nw_map[desc] = name
                        result.append(dict(value=name, name=desc, nw_id=''))
            for nw in virtual_networks:
                if nw.get('type') in ('Virtual Machine',) and nw.get('name') not in ('VM Network',):
                    vlu = '%s:%s' %(nw.get('switch'),nw.get('name'))
                    result.append(dict(value = vlu,name = nw.get('name'),nw_id = ''))
        return result
        
    #PASSED
    def get_bond_details(self, nw_id=None):
        slavelist_info = []
        try:
            print 'Inside Network get_bond_details'
            print nw_id
            if nw_id:
                nw = self.nw_manager.get_defn(nw_id)
                if nw.bond_info:
                    print nw.bond_info
                    if nw.bond_info['is_bonded'] == 'true':
                        print "nw.bond_info['slave_list']",
                        print nw.bond_info['slave_list']
                        for slave in nw.bond_info['slave_list']:
                            slave_info = {}
                            slave_info['phy_nw_name'] = slave
                            slave_info['is_slave'] = True
                            slavelist_info.append(slave_info)
            else:            
                slave_info = {}
                slave_info['phy_nw_name'] = 'eth0'
                slave_info['is_slave'] = True
                slavelist_info.append(slave_info)
                slave_info = {}
                slave_info['phy_nw_name'] = 'eth1'
                slave_info['is_slave'] = False
                slavelist_info.append(slave_info)
                slave_info = {}
                slave_info['phy_nw_name'] = 'eth2'
                slave_info['is_slave'] = False
                slavelist_info.append(slave_info)
                slave_info = {}
                slave_info['phy_nw_name'] = 'eth3'
                slave_info['is_slave'] = False
                slavelist_info.append(slave_info)
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")
        
        return dict(success='true', rows=slavelist_info)

        
    #PASSED
    def get_bridge_prefix(self):
        result = []
        bridge_prefix = tg.config.get('bridge_prefix')
        result.append(dict(name=bridge_prefix))
        return result

    #PASSED
    def get_default_cidr(self):
        result = []
        try:
            default_cidr = {'10.0.0.0/8': '10.0.0.0/8', '192.168.0.0/16': '192.168.0.0/16', '172.16.0.0/16 ': '172.16.0.0/16'}
            for key in default_cidr.keys():
                result.append(dict(name=key, value=default_cidr.get(key)))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
            
        return result
        
    #PASSED
    def get_default_interfaces(self):
        result = []
        try:
            default_interfaces = {'eth0': 'eth0', 'eth1': 'eth1', 'eth2': 'eth2', 'eth3': 'eth3', 'eth4': 'eth4', 'bond0': 'bond0', 'bond1': 'bond1', 'bond2': 'bond2', 'bond3': 'bond3', 'bond4': 'bond4'}
            for key in default_interfaces.keys():
                result.append(dict(name=key, value=default_interfaces.get(key)))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
            
        return result
        
    #PASSED
    def get_dic(self, objDic):
        objDic_new = {}
        objArrayKeys = []
        objArrayKeys = objDic.keys()
        
        for key in objArrayKeys:
            objDic_new[key] = objDic[key]
        
        if objDic_new:
            returnVal = objDic_new
        else:
            returnVal = None
            
        return returnVal
        
    #PASSED
    def get_edit_network_details(self, nw_id):
        try:
            network_value = {}
            nw = self.nw_manager.get_defn(nw_id)
            dhcp_range_value = None
            if nw.dhcp_info and nw.dhcp_info['dhcp_start'] and nw.dhcp_info['dhcp_end']:
                dhcp_range_value = nw.dhcp_info['dhcp_start'] + ' - ' + nw.dhcp_info['dhcp_end']
            
            if nw.vlan_info:
                network_value['vlan_id_pool_id'] = nw.vlan_info.get('vlan_id_pool_id')
                network_value['vlan_id_pool_name'] = nw.vlan_info.get('vlan_id_pool_name')
                network_value['vlan_id'] = nw.vlan_info.get('vlan_id')
            
            network_value['nw_id'] = nw_id
            network_value['nw_type'] = nw.type
            network_value['name'] = nw.name
            network_value['description'] = nw.description
            network_value['bridge_info_name'] = nw.bridge_info['name']
            network_value['bridge_info_phy_list'] = None
            network_value['nw_bridge_info_name'] = nw.bridge_info['name']
            network_value['nw_ipv4_info_ip_network'] = nw.ipv4_info['ip_network']
            if nw.type == NwDef.VLAN_NW:
                network_value['gateway'] = nw.ipv4_info['gateway']
                network_value['ip_address'] = nw.ipv4_info['ip_address']
            else:
                network_value['gateway'] = ''
                network_value['ip_address'] = ''
                
            network_value['dhcp_range_value'] = dhcp_range_value
            network_value['nw_nat_info_interface'] = nw.nat_info['interface']
            network_value['interface'] = nw.nat_info['interface']
            if nw.nat_info and nw.nat_info['interface']:
                network_value['nw_nat_forward'] = True
            else:
                network_value['nw_nat_forward'] = False
            
            if nw.vlan_info:
                network_value['use_vlan'] = nw.vlan_info['use_vlan']
                network_value['vlan_id'] = nw.vlan_info['vlan_id']
            else:
                network_value['use_vlan'] = False
                network_value['vlan_id'] = ''
            
            if nw.bond_info:
                network_value['is_bonded'] = nw.bond_info['is_bonded']
                network_value['slave_list'] = nw.bond_info['slave_list']
            else:
                network_value['is_bonded'] = False
                network_value['slave_list'] = []
                
        except Exception as ex:
            print_traceback()
            raise ex
        
        return network_value
        
            
    #PASSED
    def get_interface(self, auth, node_id):
        result = []
        try:
            nw_nat_fwding_map = {}
            managed_node = NodeService().get_managed_node(auth, node_id)
            if managed_node is not None:
                nics = managed_node.get_nic_info()
                if nics:
                    for nic in nics.itervalues():
                        nic_name = nic['name']
                        nw_nat_fwding_map[nic_name] = nic_name
            
            for key in nw_nat_fwding_map.keys():
                result.append(dict(name=key, value=nw_nat_fwding_map.get(key)))
                
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
            
        return result
        
    #PASSED
    def get_ips_tobe_remove_and_add(self, ips_info):
        remove_ip_ips = []
        add_ips = []
        for ip_info in ips_info:
            if not ip_info.get('is_selected') and ip_info.get('id'):
                ip_info.get('id')
                remove_ip_ips.append(ip_info.get('id'))
        
            if ip_info.get('is_selected') and not ip_info.get('id'):
                add_ips.append(ip_info.get('ip'))
            
        return (add_ips, remove_ip_ips)
        
    #PASSED
    def get_linked_entity_list(self, auth, defn):
        #from stackone.cloud.DbModel.VDC import VDC
        str_group_list = None
        if defn.scope == constants.SCOPE_DC:
            site_defns = DBSession.query(DCDefLink).filter_by(def_id=defn.id)
            if site_defns:
                for eachdefn in site_defns:
                    site = DBSession.query(Site).filter_by(id=eachdefn.site_id).first()
                    if str_group_list:
                        str_group_list = str_group_list + ', ' + site.name
                    else:
                        str_group_list = site.name
                        
        elif defn.scope == constants.SCOPE_SP:
            group_defns = DBSession.query(SPDefLink).filter_by(def_id=defn.id)
            if group_defns:
                for eachdefn in group_defns:
                    group = DBSession.query(ServerGroup).filter_by(id=eachdefn.group_id).first()
                    if str_group_list:
                        str_group_list = str_group_list + ', ' + group.name
                    else:
                        str_group_list = group.name
                
        elif defn.scope == constants.SCOPE_S: 
            node_defns = DBSession.query(ServerDefLink).filter_by(def_id=defn.id)
            if node_defns:
                for eachdefn in node_defns:
                    node = DBSession.query(ManagedNode).filter_by(id=eachdefn.server_id).first()
                    if str_group_list:
                        str_group_list = str_group_list + ', ' + node.hostname
                    else:
                        str_group_list = node.hostname
                        
        elif defn.scope == constants.SCOPE_CP:
            csep_defns = DBSession.query(CSEPDefLink).filter_by(def_id=defn.id)
            if csep_defns:
                vdc_name = ''
                csep_context = DBSession.query(CSEPContext).filter_by(id=defn.csep_context_id).first()
                if csep_context:
                    vdc_acc = DBSession.query(VDC).filter_by(id=csep_context.vdc_id).first()
                    if vdc_acc:
                        vdc_name = vdc_acc.name
                
                for eachdefn in csep_defns:
                    csep = DBSession.query(CSEP).filter_by(id=eachdefn.csep_id).first()
                    csep_name = ''
                    if csep:
                        csep_name = csep.name
                
                    if str_group_list:
                        str_group_list = str_group_list + ', ' + csep_name + '-' + vdc_name
                    else:
                        str_group_list = csep_name + '-' + vdc_name
                        
        return str_group_list
        
    #PASSED
    def get_network_models(self,auth,image_id):
        image = ImageService().get_image(auth,image_id)
        if image:
            return image.get_network_models()
        else:
            # changed by Alex
            infolist = []
            infolist.append(dict(name='i82551', value='i82551'))
            infolist.append(dict(name='i8255715', value='i8255715'))
            infolist.append(dict(name='i82559er', value='i82559er'))
            infolist.append(dict(name='ne2k-pci', value='ne2k-pci'))
            infolist.append(dict(name='ne2k-isa', value='ne2k-isa'))
            infolist.append(dict(name='pcnet', value='pcnet'))
            infolist.append(dict(name='rtl8139', value='rtl8139'))
            infolist.append(dict(name='rmc91c111', value='rmc91c111'))
            infolist.append(dict(name='lance', value='lance'))
            infolist.append(dict(name='mef-fec', value='mef-fec'))
            infolist.append(dict(name='virtio', value='virtio'))
            return infolist
                
    #PASSED
    def get_new_bridge_name(self, auth, template, node_id, group_id, site_id, op_level=None):
        new_name = ''
        bridge_names = self.get_all_known_bridges(auth, node_id, group_id, site_id, op_level)
        
        for i in range(0, 1000):
            name = template % i
            if name in bridge_names:
                continue
            new_name = name
            break
        
        return new_name
        
    #PASSED
    def get_new_nw(self, auth, image_id, mode, node_id, op_level=None):
        result = []
        if mode in ('edit_image_settings', 'provision_vm', 'provision_image'):
            (vif_entry, nw_entry) = self.get_new_nw_entry()
        else:
            managed_node = NodeService().get_managed_node(auth, node_id)
            mac = randomMAC()
            if managed_node is not None:
                bridge = managed_node.get_default_bridge()
            if not bridge:
                bridge = 'xenbr0'
            if managed_node.platform == 'kvm':
                bridge = 'br0'
            vif_entry = vifEntry('mac=%s,bridge=%s' % (mac, bridge))
            nw_entry = None
        result.append(self.get_nw_entry(vif_entry, op_level))
        return result
        
    #PASSED
    def get_new_nw_entry(self, image_conf=None):
        return (vifEntry('mac=$AUTOGEN_MAC,bridge=$DEFAULT_BRIDGE'), None)

    #PASSED
    def get_new_private_bridge_name(self, auth, node_id, group_id, site_id, op_level=None):
        result = {}
        try:
            bridge = self.get_new_bridge_name(auth, 'pbr%d', node_id, group_id, site_id, op_level)
            result['bridge'] = bridge
            return result
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
        
    #PASSED
    def get_num_hosts(self):
        result = []
        try:
            default_num_host = {256: 256, 512: 512, 1024: 1024}
            for key in default_num_host.keys():
                result.append(dict(name=key, value=default_num_host.get(key)))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
        
        return result

        
    #PASSED
    def get_number_from_interface(self, interface):
        number = None
        if interface:
            number = interface[len(interface)-1:len(interface)]
        return number
        
    #PASSED
    def get_nw_address_space_map(self):
        result = []
        try:
            nw_address_space = {'10.1.0.0/24': '10.1.0.0/24', '10.2.0.0/24': '10.2.0.0/24', '10.3.0.0/24': '10.3.0.0/24', '10.4.0.0/24': '10.4.0.0/24'}
            for key in nw_address_space.keys():
                result.append(dict(name=key, value=nw_address_space.get(key)))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
            
        return result
        
    #PASSED
    def get_nw_dc_defns(self, auth, site_id, group_id, node_id):
        result = []
        defns = self.nw_manager.getSiteDefListToAssociate(site_id, group_id, to_unicode(constants.NETWORK))
        for defn in defns:
            result.append(dict(id=defn.id, name=defn.name, type=nw_type_map[defn.type], description=defn.description, definition=defn.get_definition(), status=defn.status, scope=defn.scope))
        return result
        
    #PASSED
    def get_nw_defns(self, auth, site_id, group_id, node_id, op_level=None):
        group_list = []
        if op_level == constants.SCOPE_DC:
            group_list = self.manager.getGroupList(auth, site_id)
        elif op_level == constants.SCOPE_SP:
            group = DBSession.query(ServerGroup).filter_by(id=group_id).first()
            group_list.append(group)
        
        defns = self.nw_manager.get_defns(to_unicode(constants.NETWORK), site_id, group_id, node_id, op_level, auth, group_list)
        bridge_list = []
        result = []
        for defn in defns:
            linked_entity_list = None
            server_name = None
            associated = False
            if defn.type != NwDef.VLAN_NW:
                node_defn = DBSession.query(ServerDefLink).filter_by(def_id=defn.id).first()
                if node_defn:
                    node = DBSession.query(ManagedNode).filter_by(id=node_defn.server_id).first()
                    if node:
                        server_name = node.hostname
                    associated = True
            linked_entity_list = self.get_linked_entity_list(auth, defn)
            def_status = ''
            def_status = defn.status
            if op_level == constants.SCOPE_DC:
                def_status = constants.IN_SYNC
            
            if nw_type_map[defn.type] == constants.VLAN:
                server_name = 'N/A'
            
            result.append(dict(id=defn.id, name=defn.name, type=nw_type_map[defn.type], description=defn.description, definition=defn.get_definition(), status=def_status, scope=defn.scope, associated=associated, server=server_name, displayscope=linked_entity_list))
            
            if defn.bridge_info:
                if defn.bridge_info['name']:
                    bridge_list.append(defn.bridge_info['name'])
        
        return result
        
    #PASSED
    def get_nw_det(self, bridge, mac, model, nw_id=None, op_level=None):
        result = []
        vif_entry = vifEntry('mac=%s,bridge=%s,model=%s,nw_id=%s' % (mac, bridge, model, nw_id))
        result.append(self.get_nw_entry(vif_entry, op_level))
        return result
        
    #PASSED
    def get_nw_details(self, vif, nw):
        nw_bridge_name = vif.get_bridge()
        nw_mac = vif.get_mac()
        if nw_mac == '$AUTOGEN_MAC':
            nw_mac = 'Autogenerated'
        if nw_bridge_name == '$DEFAULT_BRIDGE':
            nw_bridge_name = 'Default'
        nw_name = None
        nw_type = None
        nw_desc = None
        if not nw:
            if nw_bridge_name is not None:
                nw_name = nw_bridge_name + ' Network'
                nw_type = NwDef.PUBLIC_NW
                nw_desc = nw_bridge_name
        else:
            nw_name = nw.name
            nw_type = nw.type
            nw_desc = '%s (%s)' % (nw.get_definition(), vif.get_bridge())
        
        return (nw_type, nw_name, nw_desc, nw_mac, vif.get_bridge(), vif.get_item('model'), vif.get_item('nw_id'))
    
    #PASSED
    def get_nw_entry(self, vif_entry, op_level=None):
        nw = self.find_nw(vif_entry, op_level)
        (nw_type, nw_name, nw_desc, nw_mac, bridge_name, model, nw_id) = self.get_nw_details(vif_entry, nw)
        return dict(type=nw_type, name=nw_name, description=nw_desc, mac=nw_mac, bridge=bridge_name, model=model, nw_id=nw_id)

    #PASSED
    def get_nw_nat_fwding_map(self, auth, node_id):
        result = []
        try:
            nw_nat_fwding_map = {'Any interface': 'ANY'}
            managed_node = NodeService().get_managed_node(auth, node_id)
            if managed_node is not None:
                nics = managed_node.get_nic_info()
                for nic in nics.itervalues():
                    nic_name = nic['name']
                    nw_nat_fwding_map[nic_name] = nic_name
            for key in nw_nat_fwding_map.keys():
                result.append(dict(name=key, value=nw_nat_fwding_map.get(key)))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
            
        return result

        
    #PASSED
    def get_nw_svc_host_details(self, def_id):
        nw_svc_host = None
        sync_status = None
        details = ''
        defn = NwManager().get_defn(def_id)
        if defn:
            scope = defn.scope
            if scope:
                if scope == constants.SCOPE_DC or scope == constants.SCOPE_SP:
                    LOGGER.info('This is CMS side definition')
                    nw_svc_host = get_cms_network_service_node()
                    dc_def_link = DBSession.query(DCDefLink).filter_by(def_id=def_id).first()
                if scope == constants.SCOPE_CP:
                    LOGGER.info('This is CMS Cloud side definition')
                    csep_def_link = DBSession.query(CSEPDefLink).filter_by(def_id=def_id).first()
                    if csep_def_link:
                        csep = DBSession.query(CSEP).filter_by(id=csep_def_link.csep_id).first()
                        
                        if csep:
                            nw_svc_host = csep.get_nw_service_host()
                            
            if nw_svc_host:
                node_def_link = DBSession.query(ServerDefLink).filter_by(server_id=nw_svc_host.id, def_id=def_id, dt_time=DBSession.query(func.max(ServerDefLink.dt_time).label('dt_time')).filter_by(server_id=nw_svc_host.id, def_id=def_id).first()).first()
                if node_def_link:
                    details = node_def_link.details
                    sync_status = node_def_link.status
        
        return (nw_svc_host, sync_status, details)
        
    #########PASSED
    def get_nws(self, auth, image_id=None, dom_id=None, node_id=None, op_level=None):
        vm_config = None
        managed_node = None
        if node_id is not None:
            managed_node = NodeService().get_managed_node(auth,node_id)
            if managed_node is not None:
                self.managed_node = managed_node
        if dom_id is not None:
            dom = DBHelper().find_by_name(VM, dom_id)
            vm_config = dom.get_config()
        elif image_id is not None:
            image = ImageService().get_image(auth, image_id)
            platform = None
            if managed_node is not None:
                platform = managed_node.get_platform()
            vm_config,img_conf = image.get_configs(platform)
        if not vm_config:
            return None
        vifs = vm_config.getNetworks()
        result = []
        for vif in vifs:
            result.append(self.get_nw_entry(vif,op_level))

        return result
    
    #PASSED
    def get_public_ips(self, auth, cidr=None, ip_list=None):
        addresses = []
        if cidr:
            cnt = len(cidr.split('-'))
            if cnt == 1:
                addresses = get_ips_from_cidr(cidr)
            elif cnt == 2:
                start,end = cidr.split('-')
                start_ip = self.ip_manager.remove_cidr_format_from_ip(start)
                end_ip = self.ip_manager.remove_cidr_format_from_ip(end)
                range = '%s-%s' % (start_ip, end_ip)
                addresses = get_ips_from_range(range)
        else:
            if ip_list:
                new_ip_list = to_unicode(ip_list).split(',')
                for ip in new_ip_list:
                    if ip:
                        addresses.append(ip)
                        
        return addresses
        
    #PASSED
    def get_server_def_list(self, site_id, group_id, def_id):
        try:
            server_def_list = []
            node_defns = self.sync_manager.get_node_defns(def_id, to_unicode(constants.NETWORK))
            if node_defns:
                for eachdefn in node_defns:
                    temp_dic = {}
                    if eachdefn:
                        node = DBSession.query(ManagedNode).filter_by(id=eachdefn.server_id).first()
                        temp_dic['id'] = eachdefn.server_id
                        temp_dic['nw_svc_host'] = ''
                        if node:
                            temp_dic['name'] = node.hostname
                        else:
                            temp_dic['name'] = None
                        
                        temp_dic['status'] = eachdefn.status
                        if eachdefn.details:
                            temp_dic['details'] = eachdefn.details
                        else:
                            temp_dic['details'] = None
                        
                        server_def_list.append(temp_dic)
                        
            (nw_svc_host, sync_status, details) = self.get_nw_svc_host_details(def_id)
            if nw_svc_host:
                record_exist = False
                for item in server_def_list:
                    if item.get('name') == nw_svc_host.hostname:
                        record_exist = True
                        item['nw_svc_host'] = '*'
                
                if not record_exist:
                    temp_dic = {}
                    temp_dic['id'] = nw_svc_host.id
                    temp_dic['nw_svc_host'] = '*'
                    if nw_svc_host:
                        temp_dic['name'] = nw_svc_host.hostname
                    else:
                        temp_dic['name'] = None
                    
                    temp_dic['status'] = sync_status
                    if eachdefn.details:
                        temp_dic['details'] = details
                    else:
                        temp_dic['details'] = None
                    
                    server_def_list.append(temp_dic)
                
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")
        
        return dict(success='true', rows=server_def_list)
        
        
    #PASSED
    def get_status(self, def_id, pool_id, node_id):
        status = 'N/A'
        if pool_id is None:
            nstatus_info = self.nw_manager.get_node_status(def_id, node_id)
            if nstatus_info:
                status = nstatus_info.status
        else:
            gstatus_info = self.nw_manager.get_group_status(def_id, pool_id)
            if gstatus_info:
                status = gstatus_info.status
                
        return status
        
    #PASSED
    def get_vif_entry(self, auth, mode, node_id):
        if mode in ('EDIT_IMAGE', 'PROVISION_VM'):
            vif_entry = self.get_new_nw_entry(None)
        else:
            managed_node = NodeService().get_managed_node(auth, node_id)
            mac = randomMAC()
            if managed_node is not None:
                bridge = managed_node.get_default_bridge()
            if not bridge:
                bridge = 'xenbr0'
            if managed_node.platform == 'kvm':
                bridge = 'br0'
            vif_entry = vifEntry('mac=%s,bridge=%s' % (mac, bridge))
        return vif_entry
        
    #PASSED
    def manage_nw_to_groups(self, csep_id, sp_ids):
        from tg import session
        def_list = DBSession.query(CSEPDefLink).filter_by(csep_id=csep_id)
        for each_defn in def_list:
            defn = DBSession.query(NwDef).filter_by(id=each_defn.def_id).first()
            if defn:
                site = None
                group = None
                defType = constants.NETWORK
                op = constants.ATTACH
                def_manager = self.nw_manager
                auth = session['auth']
                errs = []
                grid_manager = self.manager
                self.nw_manager.manage_defn_to_groups(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager, csep_id)
                
        
    #PASSED
    def nw_address_changed(self, ip_value):
        result = {}
        try:
            if ip_value:
                x = IP(ip_value)
                start = x[len(x) / 2]
                end = x[-1]
                range = '%s-%s' % (start.strNormal(), end.strNormal())
                result['range'] = range
            else:
                result['range'] = ''
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
            
        return result
        
    #PASSED
    def release_address(self, auth, pool_id, entity_id, ip_id=None):
        try:
            result = self.ip_manager.release_address(pool_id, entity_id, ip_id)
            return result
        except Exception as ex:
            print_traceback()
            return False
            
    #PASSED
    def remove_nw_defn(self, auth, def_id, site_id, group_id, node_id, op_level=None, csep_id=None):
        try:
            nw_def = self.nw_manager.get_defn(def_id)
            site = self.manager.getSite(site_id)
            group = None
            if group_id:
                group = DBSession.query(ServerGroup).filter_by(id=group_id).first()
            managed_node = NodeService().get_managed_node(auth, node_id)
            group_list = self.manager.getGroupList(auth, site_id)
            add_mode = False
            self.sync_manager.remove_defn(nw_def, site, group, managed_node, auth, to_unicode(constants.NETWORK), constants.DETACH, 'REMOVE_NETWORK_DEF', self.nw_manager, self.manager, add_mode, group_list, op_level, csep_id)
            pool_tag = constants.VLAN_ID_POOL
            context = {}
            context['nw_def_id'] = def_id
            VLANService().release_id(pool_tag, context)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'msg': 'Network Removed'}
        
    #PASSED
    def reserve_address(self, auth, pool_id, entity_id):
        try:
            ip_db = self.ip_manager.reserve_address(pool_id, entity_id)
            return {'ip': self.ip_manager.remove_cidr_format_from_ip(ip_db.ip), 'external_id': ip_db.id}
        except Exception as ex:
            print_traceback()
            return False
        
    #PASSED
    def sync_defn(self, auth, server_ids, def_id, site_id, group_id):
        server_id_list = server_ids.split(',')
        for server_id in server_id_list:
            node = DBSession.query(ManagedNode).filter_by(id=server_id).first()
            defn = DBSession.query(NwDef).filter_by(id=def_id).first()
            defType = constants.NETWORK
            self.sync_manager.sync_node_defn(auth, node, group_id, site_id, defn, defType, constants.ATTACH, self.nw_manager)
        return dict(success='true')
        
    #PASSED
    def validate_new_nw_def(self, auth, mode, nw_type, nw_name, nw_desc, bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id, group_id, node_id, op_level):
        errmsgs = []
        priv_nw_desc = {'Network bridge device': bridge, 'Address space': nw_address_space, 'DHCP address range': nw_dhcp_range, 'NAT Forwarding': nw_nat_fwding, 'Network name': nw_name, 'Network description': nw_desc, 'nat_radio': nat_radio}
        if nw_type == NwDef.VLAN_NW:
            priv_nw_desc = {'Network bridge device': bridge, 'Address space': nw_address_space, 'Network name': nw_name, 'Network description': nw_desc}
        
        if mode == 'ADD':
            for key in priv_nw_desc.keys():
                v = priv_nw_desc.get(key)
                if nat_radio == 'false':
                    if key == 'NAT Forwarding':
                        continue
            
                if key == 'Address space':
                    continue
                
                if key == 'DHCP address range':
                    continue
                
                if not v:
                    errmsgs.append('%s is required.' % (key))
                
            if nw_type == NwDef.HOST_PRIVATE_NW:
                if nw_dhcp_range:
                    r = nw_dhcp_range.split('-')
                    if len(r) != 2:
                        errmsgs.append('DHCP should be in start-end format. e.g. 192.168.1.128 - 192.168.1.254')
                    
            if bridge in self.get_all_known_bridges(auth, node_id, group_id, site_id, op_level):
                errmsgs.append('Bridge (%s) already exist, please choose different name.' % bridge)
            
        else:
            common_desc = {'Network name': nw_name, 'Network description': nw_desc}
            for key in common_desc:
                v = common_desc.get(key)
                if not v:
                    errmsgs.append('%s is required.' % (key))
            
        return errmsgs
        
 
