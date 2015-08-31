import socket
from datetime import datetime
from stackone.core.utils.utils import copyToRemote, getHexID, mkdir2
from stackone.core.utils.utils import dynamic_map, get_cms_network_service_node
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.utils
from stackone.core.utils.constants import *
constants = stackone.core.utils.constants
import os
import tg
import pprint
import traceback
import transaction
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String, Boolean, PickleType, Float, DateTime
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.orm import relation, backref
from stackone.model.SPRelations import ServerDefLink, SPDefLink, DCDefLink, CSEPDefLink
from stackone.model.ManagedNode import ManagedNode
from stackone.model.Groups import ServerGroup
from stackone.model.Entity import Entity, EntityRelation
from stackone.model.Sites import Site
from stackone.model import DeclarativeBase, DBSession
from stackone.model.Authorization import AuthorizationService
from stackone.model.VM import VM
import logging
LOGGER = logging.getLogger('stackone.model')
class NwDef(DeclarativeBase):
    PUBLIC_NW = to_unicode('PUBLIC_NW')
    HOST_PRIVATE_NW = to_unicode('HOST_PRIVATE_NW')
    VLAN_NW = to_unicode('VLAN_NW')
    NETWORK = to_unicode('NETWORK')
    __tablename__ = 'network_definitions'
    id = Column(Unicode(50), primary_key=True)
    type = Column(Unicode(50))
    name = Column(Unicode(50))
    description = Column(Unicode(100))
    is_deleted = Column(Boolean)
    csep_context_id = Column(Unicode(50))
    bridge_info = Column(PickleType)
    vlan_info = Column(PickleType)
    bond_info = Column(PickleType)
    ipv4_info = Column(PickleType)
    dhcp_info = Column(PickleType)
    nat_info = Column(PickleType)
    scope = Column(String(2))
    def __init__(self, id, type, name, description, is_deleted, csep_context_id, scope, bridge_info=dynamic_map(), vlan_info=dynamic_map(), bond_info=dynamic_map(), ipv4_info=dynamic_map(), dhcp_info=dynamic_map(), nat_info=dynamic_map(), status=None):
        self.id = id
        if self.id is None:
            self.id = getHexID()

        self.type = type
        self.name = name
        self.description = description
        self.csep_context_id = csep_context_id
        self.is_deleted = is_deleted
        self.bridge_info = bridge_info
        self.vlan_info = vlan_info
        self.bond_info = bond_info
        self.ipv4_info = ipv4_info
        self.dhcp_info = dhcp_info
        self.nat_info = nat_info
        self.status = status
        self.scope = scope


    def set_deleted(self, value=True):
        self.is_deleted = value

    def get_deleted(self):
        return self.is_deleted

    def is_nated(self):
        if self.nat_info and self.nat_info.get('interface'):
            return True
        return False


    def get_definition(self):
        desc = ''
        if self.type == self.HOST_PRIVATE_NW:
            desc += self.ipv4_info.get('ip_network')
        elif self.type==self.PUBLIC_NW:
            if self.bridge_info and self.bridge_info.get('phy_list'):
                if self.ipv4_info and self.ipv4_info.get('ip_network'):
                    desc = '%s (%s) connected to %s' % (self.bridge_info.get('name'), self.ipv4_info.get('ip_network'), self.bridge_info.get('phy_list'))
                else:
                    desc = '%s connected to %s' % (self.bridge_info.get('name'), self.bridge_info.get('phy_list'))
            else:
                if self.ipv4_info and self.ipv4_info.get('ip_network'):
                    desc = '%s (%s)' % (self.bridge_info.get('name'), self.ipv4_info.get('ip_network'))
                else:
                    desc = '%s' % (self.bridge_info.get('name'))
        elif self.type==self.VLAN_NW:
            if self.bridge_info and self.bridge_info.get('phy_list'):
                if self.ipv4_info and self.ipv4_info.get('ip_network'):
                    desc = '%s (%s) connected to %s' % (self.bridge_info.get('name'), self.ipv4_info.get('ip_network'), self.bridge_info.get('phy_list'))
                else:
                    desc = '%s connected to %s' % (self.bridge_info.get('name'), self.bridge_info.get('phy_list'))
            else:
                if self.ipv4_info and self.ipv4_info.get('ip_network'):
                    desc = '%s (%s)' % (self.bridge_info.get('name'), self.ipv4_info.get('ip_network'))
                else:
                    desc = '%s' % (self.bridge_info.get('name'))
        return desc

        

    def get_vlan_id(self):
        if self.type == self.VLAN_NW:
            return self.vlan_info.get('vlan_id')
            
            
    def get_vlan_ip_range(self):
        if self.type == self.VLAN_NW:
            return self.ipv4_info.get('ip_network')


    #get_network_by_id = classmethod()
    @classmethod
    def get_network_by_id(cls, nw_id):
        return DBSession.query(cls).filter(cls.id == nw_id).first()
    
    def __repr__(self):
        return to_str({'id':self.id,'type':self.type,'name':self.name,'description':self.description,'csep_context_id':self.csep_context_id,'bridge_info':self.bridge_info,'vlan_info':self.vlan_info,'bond_info':self.bond_info,'bond_info':self.ipv4_info,'dhcp_info':self.dhcp_info,'nat_info':self.nat_info,'is_deleted':self.is_deleted})



Index('nwdef_type', NwDef.type)
class NetworkVMRelation(DeclarativeBase):
    __tablename__ = 'network_vm_relations'
    id = Column(Unicode(50), primary_key=True)
    nw_def_id = Column(Unicode(50), ForeignKey('network_definitions.id', ondelete='CASCADE'))
    vm_id = Column(Unicode(50), ForeignKey('vms.id', ondelete='CASCADE'))
    mac_address = Column(Unicode(50))
    private_ip_id = Column(Unicode(50))
    public_ip_id = Column(Unicode(50))
    sync_state = Column(Unicode(50))
    sync_error = Column(Unicode(1000))
    fk_nw_nwvmr = relation('NwDef', backref='network_vm_relations')
    fk_vm_nwvmr = relation('VM', backref='network_vm_relations')
    def __init__(self):
        pass


class NwManager():
    s_scripts_location = '/var/cache/stackone/nw'
    s_common_scripts_location = '/var/cache/stackone/common'
    def __init__(self):
        self.defs = {}
        self.group_defn_status = []
        self.node_defn_status = []

    def add_network_VM_relation(self, nw_def_id, vm_id, mac_address, private_ip_id=None):
        LOGGER.info('Creating Network VM relation...')
        new_id = None
        if nw_def_id:
            nw_vm_rel = NetworkVMRelation()
            new_id = getHexID()
            nw_vm_rel.id = new_id
            nw_vm_rel.nw_def_id = nw_def_id
            nw_vm_rel.vm_id = vm_id
            nw_vm_rel.mac_address = mac_address
            nw_vm_rel.private_ip_id = private_ip_id
            DBSession.add(nw_vm_rel)
            transaction.commit()
            LOGGER.info('Network VM relation is created')
        return new_id


    def remove_network_VM_relation(self, vm_id, nw_def_id=None):
        LOGGER.info('Removing Network VM relation...')
        if vm_id:
            DBSession.query(NetworkVMRelation).filter_by(vm_id=vm_id).delete()
            LOGGER.info('Network VM relation is removed')
        else:
            if nw_def_id:
                DBSession.query(NetworkVMRelation).filter_by(nw_def_id=nw_def_id).delete()
                LOGGER.info('Network VM relation is removed')


    def restart_nw_service_for_VM(self, nw_def_id_list):
        LOGGER.info('Restarting network service...')

        for each_dic in nw_def_id_list:
            nw_def_id = each_dic.get('nw_def_id')
            self.setup_dns_server(nw_def_id)


    def get_dhcp_host_file(self, conf_file):
        file_name = ''
        if conf_file:
            file_name = conf_file[0:len(conf_file) - len('.conf')] + '_dhcp.conf'
        else:
            file_name = conf_file

        return file_name


    def initialize_dnsmasq_conf(self, nw_def_id, csep_id=None):
        from stackone.model.PrivateIP import NetworkServiceHostNetworkRelation
        LOGGER.info('Initializing dnsmasq conf file...')
        node = None
        nw_def = DBSession.query(NwDef).filter(NwDef.id == nw_def_id).first()
        if nw_def:
            interface = nw_def.bridge_info.get('name')
            netmask = nw_def.bridge_info.get('netmask')
            dhcp_start = nw_def.dhcp_info.get('dhcp_start')
            dhcp_end = nw_def.dhcp_info.get('dhcp_end')
            node = self.get_nw_service_host(csep_id)
            nw_host_rel = None
            if node:
                nw_host_rel = DBSession.query(NetworkServiceHostNetworkRelation).filter_by(nw_def_id=nw_def_id, nw_service_host_id=node.id).first()

            if nw_host_rel:
                try:
                    file_name = nw_host_rel.conf_file
                    LOGGER.info('Conf file name is ' + to_str(file_name))
                    f = node.node_proxy.open(file_name, 'r')
                    lines = f.readlines()
                    f.close()

                except Exception as ex:
                    LOGGER.error(to_str(nw_host_rel.conf_file) + ' file does not exists')
                    return None

                f = node.node_proxy.open(file_name, 'w')
                i = 0
                for line in lines:
                    new_line = ''
                    if line.strip() == '#no-dhcp-interface=':
                        new_line = 'interface=' + interface
                        f.write(line)

                    if line.strip() == '#bind-interfaces':
                        new_line = 'bind-interfaces'

                    if line.strip() == '#dhcp-range=192.168.0.50,192.168.0.150,255.255.255.0,12h':
                        new_line = 'dhcp-range=' + dhcp_start + ',' + dhcp_end + ',' + netmask + ',infinite'
                        f.write(line)

                    line_written = False
                    if new_line:
                        new_line = new_line + '\n'
                        f.write(new_line)
                        line_written = True

                    if not line_written:
                        f.write(line)
                        continue
                f.close()
                LOGGER.info('dnsmasq conf file is initialized')

        
        
    def update_dns_host_mapping(self, ip_mac_list, ip_mac_list_old=None, op=constants.ADD_MAPPING):
        from stackone.model.PrivateIP import NetworkServiceHostNetworkRelation
        LOGGER.info('Updating dnsmasq conf file...')
        for each_pair in ip_mac_list:
            node = None
            nw_def_id = each_pair.get('nw_def_id')
            nw_host_rel = DBSession.query(NetworkServiceHostNetworkRelation).filter_by(nw_def_id=nw_def_id).first()
            if nw_host_rel:
                try:
                    nw_service_host_id = nw_host_rel.nw_service_host_id
                    node = DBSession.query(ManagedNode).filter_by(id=nw_service_host_id).first()
                    if node:
                        LOGGER.info('We have got the network service host')

                    file_name = nw_host_rel.conf_file
                    file_name = self.get_dhcp_host_file(file_name)
                    f = node.node_proxy.open(file_name, 'r')
                    lines = f.readlines()
                    f.close()

                except Exception as ex:
                    LOGGER.error(to_str(nw_host_rel.conf_file) + ' file does not exists')
                    return None

                f = node.node_proxy.open(file_name, 'w')
                if f:
                    LOGGER.info(to_str(file_name) + ' mapping file is open for mapping')

                i = 0
                file_updated = False
                for line in lines:
                    new_line = ''
                    marked_for_delete = False
                    if op==constants.REMOVE_MAPPING:
                        new_line = to_str(each_pair.get('mac_address')) + ',' + to_str(each_pair.get('ip_address')) + ',infinite'
                        if line.strip() == new_line:
                            marked_for_delete = True
                    else:
                        if ip_mac_list_old:
                            LOGGER.info('Removing old mapping...')
                            for each_pair_old in ip_mac_list_old:
                                line_old = to_str(each_pair_old.get('mac_address')) + ',' + to_str(each_pair_old.get('ip_address')) + ',infinite'
                                if line.strip() == line_old:
                                    marked_for_delete = True
                                    break

                        new_line = to_str(each_pair.get('mac_address')) + ',' + to_str(each_pair.get('ip_address')) + ',infinite'
                        if line.strip() == new_line:
                            marked_for_delete = True
                    if not marked_for_delete and line.strip() != '':
                        f.write(line)
                        LOGGER.info('Existing MAC IP mapping is added as ' + to_str(line))
                        continue

                if op != constants.REMOVE_MAPPING:
                    new_line = to_str(each_pair.get('mac_address')) + ',' + to_str(each_pair.get('ip_address')) + ',infinite' + '\n'
                    f.write(new_line)
                    file_updated = True
                    LOGGER.info('New MAC IP mapping is added as ' + to_str(new_line))

                f.close()
                LOGGER.info('dhcp host file is updated')

    def get_ip_mac_list(self, vm_id):
        LOGGER.info('Getting ip and mac list...')
        from stackone.model.IPManager import IPManager
        from stackone.model.IP import IPS
        from stackone.model.VLANManager import VLANNetworkInfo
        from stackone.model.PrivateIP import NetworkServiceHostNetworkRelation
        tmp_list = []
        netmask = ''
        rec_list = DBSession.query(NetworkVMRelation.mac_address, NetworkVMRelation.nw_def_id, IPS.ip).join((IPS, IPS.id == NetworkVMRelation.private_ip_id)).filter(NetworkVMRelation.vm_id == vm_id)
        for rec in rec_list:
            tmp_dic = {}
            ip = IPManager().remove_cidr_format_from_ip(rec.ip)
            mac = rec.mac_address
            nw_def_id = rec.nw_def_id
            interface = ''
            dhcp_start = ''
            dhcp_end = ''
            nw_def = DBSession.query(NwDef).filter(NwDef.id == nw_def_id).first()
            if nw_def:
                interface = nw_def.bridge_info.get('name')
                dhcp_start = nw_def.dhcp_info.get('dhcp_start')
                dhcp_end = nw_def.dhcp_info.get('dhcp_end')

            vlan_nw_info = DBSession.query(VLANNetworkInfo).join((NetworkServiceHostNetworkRelation, NetworkServiceHostNetworkRelation.nw_service_host_id == VLANNetworkInfo.id)).filter(NetworkServiceHostNetworkRelation.nw_def_id == nw_def_id).first()
            if vlan_nw_info:
                netmask = vlan_nw_info.netmask

            tmp_dic['mac_address'] = mac
            tmp_dic['ip_address'] = ip
            tmp_dic['nw_def_id'] = nw_def_id
            tmp_dic['interface'] = interface
            tmp_dic['dhcp_start'] = dhcp_start
            tmp_dic['dhcp_end'] = dhcp_end
            tmp_dic['netmask'] = netmask
            tmp_list.append(tmp_dic)

        LOGGER.info('IP and MAC list is ' + to_str(tmp_list))
        return tmp_list

    def getType(self):
        return to_unicode(constants.NETWORK)

    def get_defn(self, id):
        defn = DBSession.query(NwDef).filter_by(id=id).first()
        return defn

    def get_dc_level_nw_defns(self):
        dc_db = DBSession.query(Entity).filter(Entity.name == constants.DC).first()
        site_id = dc_db.entity_id
        resultset = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type=to_unicode(constants.NETWORK))

        #may be have problem
        nw_def_ids=[row.def_id for row in resultset]
        nw_defns=DBSession.query(NwDef).filter(NwDef.id.in_(nw_def_ids)).all()
        return nw_defns



    def get_defns(self, defType, site_id, group_id, node_id=None, op_level=None, auth=None, group_list=None):
        from stackone.model.SyncDefinition import SyncDef
        sync_manager = SyncDef()
        defs_array = []
        if op_level == constants.SCOPE_DC:
            resultset = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type=defType)
            for row in resultset:
                defn = DBSession.query(NwDef).filter_by(id=row.def_id, is_deleted=False).first()
                if defn:
                    defn.status = row.status
                    defs_array.append(defn)
            resultset = DBSession.query(CSEPDefLink)
            for row in resultset:
                defn = DBSession.query(NwDef).filter_by(id=row.def_id, is_deleted=False).first()
                if defn:
                    defn.status = row.status
                    defs_array.append(defn)
        elif op_level==constants.SCOPE_SP:
            defs_array = self.getDefnsFromGroupList(auth, site_id, group_list, defType, defs_array)

        elif op_level==constants.SCOPE_S:
            resultset = DBSession.query(ServerDefLink).filter_by(server_id=node_id, def_type=defType)
            for row in resultset:
                defn = DBSession.query(NwDef).filter_by(id=row.def_id, type=NwDef.HOST_PRIVATE_NW, is_deleted=False).first()
                if defn:
                    defn.status = row.status
                    defs_array.append(defn)
                defn = DBSession.query(NwDef).filter_by(id=row.def_id, type=NwDef.PUBLIC_NW, is_deleted=False).first()
                if defn:
                    defn.status = row.status
                    defs_array.append(defn)
        elif not op_level:
            resultset = DBSession.query(NwDef).join((ServerDefLink, ServerDefLink.def_id == NwDef.id)).filter(ServerDefLink.server_id == node_id).filter(ServerDefLink.def_type == defType).filter(NwDef.is_deleted == False)
            for defn in resultset:
                if defn:
                    defs_array.append(defn)
        return defs_array


    def get_defined_networks(self, defType, site_id, group_id, node_id=None, op_level=None, auth=None, group_list=None):
        defs_array = []
        if op_level==constants.SCOPE_DC:
            resultset = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type=defType)
            for row in resultset:
                defn = DBSession.query(NwDef).filter_by(id=row.def_id, is_deleted=False).first()
                if defn:
                    defn.status = row.status
                    defs_array.append(defn)
        return defs_array


    def getDefnsFromGroupList(self, auth, site_id, group_list, defType, defs_array):
        if group_list:
            for group in group_list:
                resultset = DBSession.query(SPDefLink).filter_by(group_id=group.id, def_type=defType)
                for row in resultset:
                    defn = self.get_defn(row.def_id)
                    if defn:
                        if defn.is_deleted==False:
                            defn.status = self.get_defn_status(defn, defType, site_id, group.id, None)
                            defs_array.append(defn)
                for node in group.getNodeList(auth).itervalues():
                    resultset = DBSession.query(ServerDefLink).filter_by(server_id=node.id, def_type=defType)
                    for row in resultset:
                        defn = DBSession.query(NwDef).filter_by(id=row.def_id, scope=constants.SCOPE_S, is_deleted=False).first()
                        if defn:
                            defn.status = row.status
                            defs_array.append(defn)
        return defs_array



    def get_defn_status(self, defn, defType, site_id, group_id, node_id):
        status = None
        if defn.scope == constants.SCOPE_DC:
            dc_defn = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_id=defn.id, def_type=defType).first()
            if dc_defn:
                status = dc_defn.status
        elif defn.scope == constants.SCOPE_SP:
            sp_defn = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_id=defn.id, def_type=defType).first()
            if sp_defn:
                status = sp_defn.status
        elif defn.scope == constants.SCOPE_S:
            s_defn = DBSession.query(ServerDefLink).filter_by(server_id=node_id, def_id=defn.id, def_type=defType).first()
            if s_defn:
                status = s_defn.status
        elif defn.scope == constants.SCOPE_CP:
            cp_defn = DBSession.query(CSEPDefLink).filter_by(def_id=defn.id, def_type=defType).first()
            if cp_defn:
                status = cp_defn.status

        return status


    def getSiteDefListToAssociate(self, site_id, group_id, defType):
        sdArray = []
        if site_id:
            dc_rs = DBSession.query(DCDefLink).filter_by(site_id=site_id, def_type=defType)
            for row in dc_rs:
                sp_def = DBSession.query(SPDefLink).filter_by(group_id=group_id, def_id=row.def_id, def_type=defType).first()
                if not sp_def:
                    defn = DBSession.query(NwDef).filter_by(id=row.def_id, scope=constants.SCOPE_DC, is_deleted=False).first()
                    if defn:
                        defn.status = row.status
                        sdArray.append(defn)
        return sdArray


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


    def get_group_status(self, def_id, group_id):
        for g in self.group_defn_status:
            if g.group_id == group_id and g.def_id == def_id:
                return g
        return None

    def props_to_cmd_param(self, props):
        cp = ''
        if props:
            for p,v in props.iteritems():
                if v:
                    if cp:
                        cp += '|'
                    cp += '%s=%s' % (p, v)
            cp = "'%s'" % (cp)

        return cp


    def prepare_scripts(self, dest_node, type, defType):
        s_src_scripts_location = tg.config.get('nw_script')
        s_src_scripts_location = os.path.abspath(s_src_scripts_location)
        s_common_src_scripts_location = tg.config.get('common_script')
        s_common_src_scripts_location = os.path.abspath(s_common_src_scripts_location)
        LOGGER.info('Source script location= ' + to_str(s_src_scripts_location))
        LOGGER.info('Destination script location= ' + to_str(self.s_scripts_location))
        copyToRemote(s_src_scripts_location, dest_node, self.s_scripts_location)
        LOGGER.info('Common source script location= ' + to_str(s_common_src_scripts_location))
        LOGGER.info('Common destination script location= ' + to_str(self.s_common_scripts_location))
        copyToRemote(s_common_src_scripts_location, dest_node, self.s_common_scripts_location)
        
    def exec_script(self, node, group, defn, defType, op=constants.GET_DETAILS, tag=constants.NETWORK, ctx=None):
        if tag == constants.NETWORK:
            script_name = os.path.join(self.s_scripts_location, 'scripts', 'nw.sh')
        elif tag == constants.DNS_SERVICE or tag == constants.MANAGE_PUBLIC_IP:
            script_name = os.path.join(self.s_scripts_location, 'scripts', 'dns_service.sh')

        node_ip_address = socket.gethostbyname(node.hostname)
        type = None
        if defn:
            type = defn.type
        if not type:
            type = None
        self.prepare_scripts(node, type, defType)
        log_dir = node.config.get(prop_log_dir)
        if log_dir is None or log_dir == '':
            log_dir = DEFAULT_LOG_DIR
        log_filename = os.path.join(log_dir, 'nw/scripts', 'nw_sh.log')
        mkdir2(node, os.path.dirname(log_filename))
        new_vlan_info = {}
        print defn.vlan_info,'##########defn.bridge_info######',defn.bridge_info
        if defn:
            vlan_info = defn.vlan_info
            if vlan_info:
                new_vlan_info['vlan_id'] = vlan_info.get('vlan_id')
                new_vlan_info['interface'] = vlan_info.get('interface')
        if tag == constants.NETWORK:
            br_info = self.props_to_cmd_param(defn.bridge_info)
            new_vlan_info = self.props_to_cmd_param(new_vlan_info)
            ipv4_info = self.props_to_cmd_param(defn.ipv4_info)
            bond_info = self.props_to_cmd_param(defn.bond_info)
            dhcp_info = self.props_to_cmd_param(defn.dhcp_info)
            nat_info = self.props_to_cmd_param(defn.nat_info)
        elif tag == constants.DNS_SERVICE:
            ipv4_info = self.props_to_cmd_param(defn.ipv4_info)
            new_vlan_info = self.props_to_cmd_param(new_vlan_info)
            br_info = self.props_to_cmd_param(defn.bridge_info)
            dhcp_info = self.props_to_cmd_param(defn.dhcp_info)
        elif tag == constants.MANAGE_PUBLIC_IP:
            public_ip = ctx.get('public_ip')
            private_ip = ctx.get('private_ip')
            public_interface = ctx.get('public_interface')
            bridge_name = ctx.get('bridge_name')
            add_flag = ctx.get('add_flag')

        script_loc = os.path.join(self.s_scripts_location, 'scripts')
        script_args = ''

        if tag == constants.NETWORK:
            if type:
                script_args = ' -t ' + type
            if br_info:
                script_args += ' -b ' + br_info
    
            if new_vlan_info:
                script_args += ' -v ' + new_vlan_info
    
            if ipv4_info:
                script_args += ' -i ' + ipv4_info
    
            if bond_info:
                script_args += ' -p ' + bond_info
    
            if dhcp_info:
                script_args += ' -d ' + dhcp_info
    
            if nat_info:
                script_args += ' -n ' + nat_info
    
            if op:
                script_args += ' -o ' + op
    
            if script_loc:
                script_args += ' -s ' + script_loc
    
            if log_filename:
                script_args += ' -l ' + log_filename
    
            if node_ip_address:
                script_args += ' -r ' + node_ip_address
        if tag == constants.DNS_SERVICE:
            if ipv4_info:
                script_args = ' -i ' + ipv4_info
    
            if new_vlan_info:
                script_args += ' -v ' + new_vlan_info
    
            if log_filename:
                script_args += ' -l ' + log_filename
    
            if script_loc:
                script_args += ' -s ' + script_loc
    
            if br_info:
                script_args += ' -b ' + br_info
    
            if dhcp_info:
                script_args += ' -d ' + dhcp_info
    
            if tag:
                script_args += ' -c ' + tag
        elif tag == constants.MANAGE_PUBLIC_IP:
            if public_ip:
                script_args = ' -p ' + public_ip
    
            if private_ip:
                script_args += ' -r ' + private_ip
    
            if bridge_name:
                script_args += ' -g ' + bridge_name
    
            if public_interface:
                script_args += ' -t ' + public_interface
    
            if log_filename:
                script_args += ' -l ' + log_filename
    
            if script_loc:
                script_args += ' -s ' + script_loc
    
            if add_flag:
                script_args += ' -f ' + add_flag
    
            if tag:
                script_args += ' -c ' + tag

        cmd = script_name + script_args
        LOGGER.info('Command= ' + to_str(cmd))
        output = 'Success'
        exit_code = 0
        output,exit_code = node.node_proxy.exec_cmd(cmd)
        LOGGER.info('Exit Code= ' + to_str(exit_code))
        LOGGER.info('Output of script= ' + to_str(output))
        if exit_code == 10:
            output = 'Not deleting bridge physically since bridge and server IP addresses are same'
            LOGGER.info(output)
            exit_code = 0

        LOGGER.info('Exit Code= ' + to_str(exit_code))
        LOGGER.info('Output of script= ' + to_str(output))
        return (exit_code, output)




    def CheckOp(self, op, errs):
        if op not in [constants.ATTACH, constants.DETACH]:
            errs.append('Invalid network defn sync op ' + op)
            raise Exception('Invalid network defn sync op ' + op)

        return errs


    def getSyncMessage(self, op):
        messasge = None
        if op == constants.ATTACH:
            messasge = 'Network created successfully.'
        elif op == constants.DETACH:
            messasge = 'Network removed successfully.'
        return messasge


    def associate_defn_to_groups(self, site, sp_ids, defn, defType, op, def_manager, auth, errs):
        return None

    def sync_node_defn(self, auth, node, group_id, site_id, defn, defType, op, def_manager=None, update_status=True, errs=None, processor=None):
        from stackone.model.SyncDefinition import SyncDef
        sync_manager = SyncDef()
        sync_manager.sync_node_defn(auth, node, group_id, site_id, defn, defType, op, def_manager, update_status, errs)

    def remove_storage_disk(self, storage_id):
        return None

    def is_storage_allocated(self, storage_id):
        return False

    def SaveScanResult(self, storage_id, grid_manager, scan_result=None, site_id=None):
        return None

    def RemoveScanResult(self, scan_result=None):
        return None

    def remove_vm_links_to_storage(self, storage_id):
        return None

    def manage_defn_to_group(self, site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager, csep_id=None):
        from stackone.model.SyncDefinition import SyncDef
        try:
            node_list = None
            sync_manager = SyncDef()
            associated = self.is_associated_to_group(group, defn)
            marked_for_association = self.is_present_in_list(group.id, sp_ids)
            if associated==False and marked_for_association==True:
                details = None
                status = constants.OUT_OF_SYNC
                node_list = grid_manager.getNodeList(auth, group.id)
                for managed_node in node_list:
                    sync_manager.add_node_defn(managed_node.id, defn.id, defType, status, details)

                oos_count = len(node_list)
                status = constants.OUT_OF_SYNC
                sync_manager.add_group_defn(group.id, defn.id, defType, status, oos_count)
                update_status = True
                sync_manager.sync_defn(defn, site, group, auth, defType, op, def_manager, update_status, errs, csep_id)
                self.initialize_dnsmasq_conf(defn.id, csep_id)
            if associated == True and marked_for_association == False:
                update_status = True
                op = constants.DETACH
                sync_manager.sync_defn(defn, site, group, auth, defType, op, def_manager, update_status, errs)
                add_mode = False
                sync_manager.disassociate_defn(site, group, auth, defn, defType, add_mode, grid_manager)

            return node_list

        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            raise Exception(ex)

        return None


    def manage_defn_to_groups(self, site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager, csep_id=None):
        #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEP
        from stackone.model.SyncDefinition import SyncDef
        self.add_private_ip_pool(defn)
        result = {}
        server_list = []

        if group:
            result = self.manage_defn_to_group(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager, csep_id)
            if result:
                server_list.extend(result)

        else:
            if sp_ids:
                sp_id_list = sp_ids.split(',')

                for group_id in sp_id_list:
                    group = grid_manager.getGroup(auth, group_id)

                    if group:
                        result = self.manage_defn_to_group(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager, csep_id)

                        if result:
                            server_list.extend(result)

            else:
                if site:
                    site_entity = auth.get_entity(site.id)
                    group_entities = auth.get_entities(to_unicode(constants.SERVER_POOL), site_entity)

                    for eachgroup in group_entities:
                        group = DBSession.query(ServerGroup).filter_by(id=eachgroup.entity_id).first()
                        result = self.manage_defn_to_group(site, group, sp_ids, defn, defType, op, def_manager, auth, errs, grid_manager, csep_id)
                        if result:
                            server_list.extend(result)
                else:
                    LOGGER.error('Error: Site is None')

        ext_nw_svc_host = None
        if defn.scope == constants.SCOPE_CP:
            csep = DBSession.query(CSEP).filter_by(id=csep_id).first()
            if csep:
                ext_nw_svc_host = csep.get_nw_service_host()
        else:
            ext_nw_svc_host = get_cms_network_service_node()

        if ext_nw_svc_host:
            do_sync = True

            for server in server_list:
                if server.id == ext_nw_svc_host.id:
                    LOGGER.info('Network service host is found in the server list. That means it is already got sync with the network. So we are not syncing it again.')
                    do_sync = False
            if do_sync:
                details = ''
                status = to_unicode(constants.OUT_OF_SYNC)
                if op == constants.ATTACH:
                    SyncDef().add_node_defn(ext_nw_svc_host.id, defn.id, defType, status, details)

                LOGGER.info('Syncing for external network service host')
                group_id = None
                site_id = None
                defType = constants.NETWORK
                op = op
                update_status = True
                errs = []
                processor = None
                sync_forcefully = None
                use_auth = False
                SyncDef().sync_node_defn(auth, ext_nw_svc_host, group_id, site_id, defn, defType, op, def_manager, update_status, errs, processor, sync_forcefully, csep_id, use_auth)
        return result


    def is_present_in_list(self, str_id, str_ids):
        returnVal = False
        id_list = None

        if str_ids:
            id_list = str_ids.split(',')

            for eachid in id_list:
                if to_str(eachid) == to_str(str_id):
                    returnVal = True
                    return returnVal
        return returnVal


    def is_associated_to_group(self, group, defn):
        returnVal = False
        group_defn = DBSession.query(SPDefLink).filter_by(group_id=group.id, def_id=defn.id).first()
        if group_defn:
            returnVal = True

        return returnVal


    def Recompute(self, defn):
        return None

    def remove_storage_stats(self, def_id, entity_id):
        return None


    def manage_public_ip(self, nw_service_host, ctx):
        from stackone.model.FirewallManager import FirewallManager
        LOGGER.info('manage_public_ip...')
        exit_code = None
        output = None
        op = None
        group = None
        defn = None
        defType = constants.NETWORK
        tag = constants.MANAGE_PUBLIC_IP
        public_ip = ctx.get('public_ip')
        private_ip = ctx.get('private_ip')
        csep_id = ctx.get('csep_id')
        add_flag = ctx.get('add_flag')
        fw_manager = FirewallManager.get_manager()
        if add_flag == 'TRUE':
            fw_manager.set_firewall_for_public_ip_mapping(csep_id, public_ip, private_ip)
        else:
            fw = fw_manager.get_firewall(csep_id)
            if fw:
                fw.remove_floating_forward(public_ip, private_ip)
        node = None
        if nw_service_host:
            node = nw_service_host
            LOGGER.info('Network service host is ' + to_str(node.hostname))

        if node:
            exit_code,output = self.exec_script(node, group, defn, defType, op, tag, ctx)
            if exit_code <= 0:
                status = constants.SUCCESS
            else:
                if exit_code > 0:
                    status = constants.FAIL
                    LOGGER.error('Network service failed')
        return (exit_code, output)


    def setup_dns_server(self, nw_def_id, node=None):
        from stackone.model.PrivateIP import NetworkServiceHostNetworkRelation
        #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEP, CSEPContext
        #from stackone.cloud.core.model.CloudProviderManager import CloudProviderManager
        LOGGER.info('Setting up dns server...')
        exit_code = None
        output = None
        op = None
        group = None
        user_name = None
        password = None
        tag = constants.DNS_SERVICE
        defType = constants.NETWORK
        need_restart = True
        dns_status = None
        conf_file = None
        pid_file = None
        pid = None
        sync_state = None
        sync_error = None
        bridge_name = None
        defn = DBSession.query(NwDef).filter_by(id=nw_def_id).first()
        if not node:
            csep_context_id = defn.csep_context_id
            if csep_context_id:
                csep_context = DBSession.query(CSEPContext).filter_by(id=csep_context_id).first()
                if csep_context:
                    cp = CloudProviderManager().get_cp(csep_context.cp_id)
                    if cp:
                        csep = DBSession.query(CSEP).filter_by(name=cp.path).first()
                        if csep:
                            node = self.get_nw_service_host(csep.id)
            else:
                node = get_cms_network_service_node()
        if node:
            nw_host_rel = DBSession.query(NetworkServiceHostNetworkRelation).filter_by(nw_def_id=nw_def_id, nw_service_host_id=node.id).first()
            if nw_host_rel:
                pid = nw_host_rel.pid
        if not node:
            LOGGER.debug('Nw service host is None!!')
        else:
            LOGGER.debug('Nw service host is ' + node.hostname)
        if node:
            if pid:
                LOGGER.info('pid present. pid is ' + to_str(pid))
                cmd = 'ls /proc | grep ' + to_str(pid)
                LOGGER.info('cmd= ' + to_str(cmd))
                LOGGER.info('node name is ' + to_str(node.hostname))
                output,exit_code = node.node_proxy.exec_cmd(cmd)
                LOGGER.info('output= ' + to_str(output))
                LOGGER.info('exit_code= ' + to_str(exit_code))
                if not exit_code:
                    cmd = 'kill -HUP ' + to_str(pid)
                    LOGGER.info('cmd= ' + to_str(cmd))
                    node.node_proxy.exec_cmd(cmd)
                    LOGGER.info('Network service sigh up')
                    need_restart = False
            else:
                LOGGER.info('pid absent')

        if node and need_restart:
            LOGGER.info('Need to restart network service')
            LOGGER.info(defn.bridge_info)
            LOGGER.info('@@@@@@@@@@@@@@@@@@@@@@@@@@@@@')
            exit_code,output = self.exec_script(node, group, defn, defType, op=op, tag=tag)
            bridge_info = defn.bridge_info
            bridge_name = bridge_info.get('name')
            conf_file = self.get_dns_conf_file(bridge_name)

            if exit_code<=0:
                dns_status = constants.SUCCESS
                pid = self.get_pid(node, bridge_name)
                pid_file = self.get_dns_pid_file(bridge_name)
                sync_state = constants.IN_SYNC
            elif exit_code>0:
                dns_status = constants.FAIL
                sync_state = constants.OUT_OF_SYNC
                sync_error = output

                if to_str(sync_error).find('dnsmasq: failed to bind listening socket for')>=0:
                    cmd = "ps aux | grep dnsmasq | grep '" + to_str(bridge_name) + "' | grep -v 'PID' | awk '{print($2)}'"
                    LOGGER.info('cmd=' + to_str(cmd))
                    output,exit_code = node.node_proxy.exec_cmd(cmd)
                    LOGGER.info('exit_code=' + to_str(exit_code))
                    LOGGER.info('output=' + to_str(output))
                    if not exit_code:
                        if output:
                            pid = to_str(output)
                    if pid:
                        self.add_nw_service_host_relation(node, defn.id, dns_status, conf_file, pid_file, pid, sync_state, sync_error)

        if node and defn:
            self.add_nw_service_host_relation(node, defn.id, dns_status, conf_file, pid_file, pid, sync_state, sync_error)
        return (exit_code, output)


    def create_network(self, context):
        from stackone.viewModel.NetworkService import NetworkService
        from stackone.model.VLANManager import VLANIDPool
        from stackone.model.SyncDefinition import SyncDef
        from tg import session
        network_service = NetworkService()
        result = None
        auth = session['auth']
        nw_name = context.get('nw_name')
        nw_desc = context.get('nw_desc')
        nw_address_space = context.get('nw_address_space')
        nw_dhcp_range = context.get('nw_dhcp_range')
        nw_nat_fwding = context.get('nw_nat_fwding')
        sp_ids = context.get('sp_id')
        csep_context_id = context.get('csep_context_id')
        vdc_id = context.get('vdc_id')
        csep_id = context.get('csep_id')
        nw_type = 'VLAN_NW'
        nw_bridge = None
        if nw_nat_fwding:
            (result, nat_radio) = ('vlan_id', 'true')
        else:
            nat_radio = 'false'

        site_id = None
        group_id = None
        node_id = None
        op_level = constants.SCOPE_CP
        nw_gateway = None
        nw_ip_address = None
        nw_use_vlan = 'false'
        nw_vlan_id = None
        nw_isbonded = None
        nw_slaves = None
        interface = None
        vlan_id_pool = DBSession.query(VLANIDPool).first()
        vlan_id_pool_id = vlan_id_pool.id
        result = network_service.add_nw_defn(auth, nw_name, nw_desc, nw_type, nw_bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id, group_id, node_id, op_level, nw_gateway, nw_ip_address, nw_use_vlan, nw_vlan_id, nw_isbonded, nw_slaves, interface, vlan_id_pool_id, sp_ids, csep_context_id, csep_id)
        nw_id = result.get('nw_id')
        nw_vlan_id = result.get('nw_vlan_id')
        if nw_id:
            result={'nw_id':nw_id,'name':nw_name,'desc':nw_desc,'dhcp_range':nw_dhcp_range,'address_space':nw_address_space,'nat':nw_nat_fwding,'vlan_id':nw_vlan_id}
        return result


    def remove_network(self, context):
        from stackone.viewModel.NetworkService import NetworkService
        from tg import session
        network_service = NetworkService()
        nw_def_id = context.get('nw_def_id')
        csep_id = context.get('csep_id')
        auth = session['auth']
        site_id = None
        group_id = None
        node_id = None
        op_level = constants.SCOPE_CP
        result = network_service.remove_nw_defn(auth, nw_def_id, site_id, group_id, node_id, op_level, csep_id)
        return result

    def edit_network(self, context):
        from stackone.viewModel.NetworkService import NetworkService
        from tg import session
        network_service = NetworkService()
        nw_def_id = context.get('nw_def_id')
        desc = context.get('desc')
        nw_name = context.get('nw_name')
        result = network_service.edit_nw_defn(nw_def_id, nw_name, desc)
        return result

    def add_nw_service_host_relation(self, node, nw_def_id, dns_status, conf_file, pid_file=None, pid=None, sync_state=None, sync_error=None):
        from stackone.model.PrivateIP import NetworkServiceHostNetworkRelation
        if node:
            nw_host_rel = DBSession.query(NetworkServiceHostNetworkRelation).filter_by(nw_def_id=nw_def_id).first()
            if nw_host_rel:
                nw_host_rel.nw_service_host_id = node.id
                if pid:
                    nw_host_rel.pid = pid
                if dns_status:
                    nw_host_rel.dns_status = dns_status
                if pid_file:
                    nw_host_rel.pid_file = pid_file
                if conf_file:
                    nw_host_rel.conf_file = conf_file
                if sync_state:
                    nw_host_rel.sync_state = sync_state
                if sync_error:
                    nw_host_rel.sync_error = sync_error
                LOGGER.info('Network service host and network relation is updated')
            else:
                nw_host_rel = NetworkServiceHostNetworkRelation()
                nw_host_rel.id = getHexID()
                nw_host_rel.nw_service_host_id = node.id
                nw_host_rel.nw_def_id = nw_def_id
                nw_host_rel.pid = pid
                nw_host_rel.dns_status = dns_status
                nw_host_rel.pid_file = pid_file
                nw_host_rel.conf_file = conf_file
                nw_host_rel.sync_state = sync_state
                nw_host_rel.sync_error = sync_error
                DBSession.add(nw_host_rel)
                LOGGER.info('Network service host and network relation is added')

            transaction.commit()

        return None 


    def get_network(self, nw_name, bridge_name=None):
        LOGGER.info('Getting network...')
        nw_def_id = None

        if nw_name:
            nw = DBSession.query(NwDef).filter_by(name=nw_name).first()

            if nw:
                nw_def_id = nw.id
                bridge_info = nw.bridge_info

                if bridge_info:
                    bridge_name = bridge_info.get('name')


        if bridge_name and not nw_def_id:
            nw_list = DBSession.query(NwDef)

            for nw in nw_list:
                bridge_info = nw.bridge_info

                if bridge_info:

                    if bridge_name==bridge_info.get('name'):
                        nw_def_id = nw.id

        LOGGER.info('Got the network, which is ' + to_str(bridge_name))
        return (nw_def_id, bridge_name)


    def add_private_ip_pool(self, defn):
        from stackone.model.IPManager import IPManager
        name = defn.name
        desc = defn.description
        cidr = defn.ipv4_info.get('ip_network')
        dhcp_start = defn.dhcp_info.get('dhcp_start')
        dhcp_end = defn.dhcp_info.get('dhcp_end')
        if dhcp_start:
            range = dhcp_start + '-' + dhcp_end
        else:
            range = ''

        pool = IPManager().create_private_pool(name, cidr, range, defn.id, desc)
        self.reserve_gateway_ip(pool.id, defn.id)
        return None 


    #get_network_by_id = classmethod()
    @classmethod
    def get_network_by_id(self, nw_id):
        return NwDef.get_network_by_id(nw_id)
    def reserve_gateway_ip(self, pool_id, nw_def_id):
        from stackone.model.IPManager import IPManager
        from stackone.model.IP import IPS
        reserved_by = constants.GATEWAY + '_' + to_str(nw_def_id)
        rec = DBSession.query(IPS).filter_by(reserved_by=reserved_by).first()
        if not rec:
            ips_object = IPManager().reserve_address(pool_id, reserved_by)
            if ips_object:
                ip_id = ips_object.id
                IPManager().associate_address(pool_id, ip_id, constants.GATEWAY)
        return None 


    def remove_private_ip_pool(self, nw_def_id):
        from stackone.model.IPManager import IPManager
        pool_id = None
        pool = IPManager().get_pool(nw_def_id)

        if pool:
            pool_id = pool.id
            rec_list = IPManager().get_all_reserved_addresses(pool_id)

            for rec in rec_list:
                IPManager().release_address(pool_id, rec.reserved_by)

        if pool_id:
            IPManager().delete_pool(pool_id)
        return None


    def remove_defn_dependencies(self, csep_id, defn_id, vm_id):
        from stackone.model.FirewallManager import FirewallManager
        fw = FirewallManager.get_manager()
        fw.remove_firewall_for_network(csep_id, defn_id)
        self.releasePublicIP(defn_id)
        self.remove_private_ip_pool(defn_id)
        self.remove_network_VM_relation(vm_id, defn_id)
        self.nw_service_cleanup(defn_id)
        return None

    def nw_service_cleanup(self, defn_id):
        LOGGER.info('Cleanning up for network service...')
        from stackone.model.PrivateIP import NetworkServiceHostNetworkRelation
        nw_host_rel = DBSession.query(NetworkServiceHostNetworkRelation).filter_by(nw_def_id=defn_id).first()

        if nw_host_rel:
            pid = nw_host_rel.pid
            conf_file = nw_host_rel.conf_file
            pid_file = nw_host_rel.pid_file
            nw_service_host_id = nw_host_rel.nw_service_host_id

            if nw_service_host_id:
                node = DBSession.query(ManagedNode).filter_by(id=nw_service_host_id).first()

                if node:
                    if pid:
                        self.kill_process(node, pid)

                    LOGGER.info('Removing dnsmasq config file')
                    self.remove_file(node, conf_file)
                    LOGGER.info('Removing dhcp host file')
                    dhcp_host_file = self.get_dhcp_host_file(conf_file)
                    self.remove_file(node, dhcp_host_file)
                    if conf_file:
                        lease_file = conf_file[0:len(conf_file) - len('.conf')] + '.leases'
                        LOGGER.info('Removing leases file')
                        self.remove_file(node, lease_file)

                    LOGGER.info('Removing dnsmasq pid file')
                    self.remove_file(node, pid_file)

                DBSession.delete(nw_host_rel)
                LOGGER.info('Network service host and network relation is removed')

        vm_id = None
        NwManager().remove_network_VM_relation(vm_id, defn_id)
        return None


    def kill_process(self, node, pid):
        LOGGER.info('Killing process...')
        cmd = 'kill ' + to_str(pid)
        LOGGER.info('cmd= ' + to_str(cmd))
        node.node_proxy.exec_cmd(cmd)
        LOGGER.info('Process is killed')

    def remove_file(self, node, file_name):
        LOGGER.info('Removing file...')
        cmd = 'rm -f ' + to_str(file_name)
        node.node_proxy.exec_cmd(cmd)
        LOGGER.info('File is removed')

    def get_pid(self, node, bridge_name):
        pid = None
        LOGGER.info('Getting pid...')

        try:
            file_name = self.get_dns_pid_file(bridge_name)
            f = node.node_proxy.open(file_name, 'r')
            lines = f.readlines()
            pid = lines[0]
            f.close()
            LOGGER.info('pid is ' + to_str(pid))
            return pid

        except Exception as ex:
            LOGGER.error(to_str(ex))
            return pid

        return None


    def get_dns_conf_file(self, bridge_name):
        stackone_cache_dir = tg.config.get('stackone_cache_dir')
        conf_file_name = os.path.join(stackone_cache_dir, 'networks', bridge_name + '.conf')
        return conf_file_name

    def get_dns_pid_file(self, bridge_name):
        stackone_cache_dir = tg.config.get('stackone_cache_dir')
        dns_pid_file = os.path.join(stackone_cache_dir, 'networks', bridge_name + '.pid')
        return dns_pid_file

    def get_nw_service_host(self, csep_id=None):
        LOGGER.info('Getting network service host...')
        #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEP
        nw_service_host = None
        if csep_id:
            csep = DBSession.query(CSEP).filter_by(id=csep_id).first()
            if csep:
                nw_service_host = csep.get_nw_service_host()
        else:
            nw_service_host = get_cms_network_service_node()

        return nw_service_host


    def on_defn_creation(self,auth,**details):
        from stackone.model.PrivateIP import NetworkServiceHostNetworkRelation
        defn_id = details.get('defn_id')
        node_id = details.get('node_id')
        exit_code = details.get('exit_code')
        output = details.get('output')
        rec_list = DBSession.query(NetworkVMRelation).filter_by(nw_def_id=defn_id)

        for each_rec in rec_list:
            vm_id = each_rec.vm_id
            ent = auth.get_entity(vm_id)
            entity_id = ent.parents[0].entity_id

            if entity_id==node_id:
                if exit_code>0:
                    rec.sync_state = constants.OUT_OF_SYNC
                    rec.sync_error = output
                else:
                    rec.sync_state = constants.IN_SYNC
                    rec.sync_error = None


    def is_nw_svc_host(self, auth, node, csep_id):
        LOGGER.info('Checking is nw service host...')
        #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEP
        site = None
        csep = None
        is_nw_svc_host = False

        if csep_id:
            LOGGER.info('Looking for network service host at Cloud side...')
            csep = DBSession.query(CSEP).filter_by(id=csep_id).first()

            if csep:
                nw_svc_host = csep.get_nw_service_host()

                if nw_svc_host.id==node.id:
                    is_nw_svc_host = True
                    LOGGER.info('Yes it is nw service host and name is ' + to_str(nw_svc_host.hostname))

        else:
            LOGGER.info('Looking for network service host at CMS side...')
            node_from_config = get_cms_network_service_node()
            print node_from_config,'########node_from_config#########'
            if node_from_config:
                if node_from_config.id==node.id:
                    is_nw_svc_host = True
                    node_entity = auth.get_entity(node.id)
                    if node_entity:
                        site_entity = node_entity.parents[0].parents[0]
                        site = DBSession.query(Site).filter_by(id=site_entity.entity_id).first()
                        LOGGER.info('Site name is ' + to_str(site.name))
                    else:
                        site = DBSession.query(Site).first()
                        LOGGER.info('Site name is ' + to_str(site.name))

                    LOGGER.info('Yes it is nw service host at CMS side and name is ' + to_str(node_from_config.hostname))
        return (is_nw_svc_host, csep, site)

    #pass
    def nw_svc_specific_sync(self, auth, node, defn, csep_id, op):
        LOGGER.info('Doing nw service specific sync...')
        #from stackone.cloud.DbModel.platforms.cms.CSEP import InternalNetworkService
        from stackone.model.PrivateIP import NetworkServiceHostNetworkRelation
        from stackone.model.network import NetworkVMRelation
        from stackone.model.FirewallManager import FirewallManager
        from stackone.model.IPManager import IPManager
        public_interface = None
        node = DBSession.query(ManagedNode).filter_by(id=node.id).first()
        print node,'##########node#########'
        is_nw_svc_host,csep,site = self.is_nw_svc_host(auth, node, csep_id)
        print '############is_nw_svc_host,csep,site##########',is_nw_svc_host,csep,site
        if is_nw_svc_host:
            dhcp_start = None
            dhcp_end = None
            dhcp_info = defn.dhcp_info
            if dhcp_info:
                dhcp_start = dhcp_info.get('dhcp_start')
                dhcp_end = dhcp_info.get('dhcp_end')
            if not dhcp_start and not dhcp_end:
                LOGGER.info('Network definition does not have DHCP so network service host would not get sync with this definition.')
                return None

            nw_svc_host_nw_rel = DBSession.query(NetworkServiceHostNetworkRelation).filter_by(nw_def_id=defn.id, nw_service_host_id=node.id, sync_state=constants.IN_SYNC).first()
            if nw_svc_host_nw_rel and op == constants.ATTACH:
                LOGGER.info('Network definition is already in sync with network service host')
                return None
            LOGGER.info('Doing firewall settings...')
            fw_manager = FirewallManager.get_manager()

            if csep:
                fw = fw_manager.get_firewall(csep.id)
                old_nw_svc_host = csep.get_nw_service_host()
                nw_service_host = fw.nw_service_host
                if not nw_service_host:
                    fw_manager.set_nw_service_host(fw, node)
                    LOGGER.info('New network service host (' + node.hostname + ') is added to firewall')
                else:
                    LOGGER.info('Network service host for the firewall is ' + to_str(nw_service_host.hostname))

                if old_nw_svc_host.hostname != node.hostname:
                    LOGGER.info('Old (' + old_nw_svc_host.hostname + ') and new (' + node.hostname + ') network service hosts are not same. So setting up new network service host in firewall.')
                    fw_manager.set_nw_service_host(fw, node)
                    LOGGER.info('New network service host (' + node.hostname + ') is added to firewall')

                public_interface = IPManager().get_public_interface(csep.id)

            else:
                if site:
                    fw = fw_manager.get_firewall(site.id)
                    old_nw_svc_host = get_cms_network_service_node()
                    nw_service_host = fw.nw_service_host
                    if not nw_service_host:
                        fw_manager.set_nw_service_host(fw, node)
                        LOGGER.info('New network service host (' + node.hostname + ') is added to firewall')
                    else:
                        LOGGER.info('Network service host for the firewall is ' + to_str(nw_service_host.hostname))

                    if old_nw_svc_host.hostname != node.hostname:
                        LOGGER.info('Old (' + old_nw_svc_host.hostname + ') and new (' + node.hostname + ') network service hosts are not same. So setting up new network service host in firewall.')
                        fw_manager.set_nw_service_host(fw, node)
                        LOGGER.info('New network service host (' + node.hostname + ') is added to firewall')

                    public_interface = tg.config.get('cms_public_interface')

            LOGGER.info('Setting up dnsmasq service...')
            exit_code,output = self.setup_dns_server(defn.id, node)
            fw_manager = FirewallManager.get_manager()
            if csep:
                LOGGER.info('Apply firewall settings for network')
                if op == constants.ATTACH:
                    fw_manager.set_firewall_for_network(csep.id, defn.id)
                else:
                    if op == constants.DETACH:
                        fw_manager.remove_firewall_for_network(csep.id, defn.id)
            else:
                if site:
                    LOGGER.info('Apply firewall settings for site')
                    if op == constants.ATTACH:
                        fw_manager.set_firewall_for_network(csep_id, defn.id, site.id)
                    else:
                        if op == constants.DETACH:
                            fw_manager.remove_firewall_for_network(csep_id, defn.id, site.id)

            nw_vm_rel_list = DBSession.query(NetworkVMRelation).filter_by(nw_def_id=defn.id)

            for nw_vm_rel in nw_vm_rel_list:
                LOGGER.info('Going through each network VM relation')
                vm_id = nw_vm_rel.vm_id
                private_ip_id = nw_vm_rel.private_ip_id
                public_ip_id = nw_vm_rel.public_ip_id
                public_ip = ''
                private_ip = ''
                bridge_name = ''
                if op == constants.ATTACH:
                    add_flag = 'TRUE'
                elif op == constants.DETACH:
                    add_flag = 'FALSE'
                    
                if public_ip_id:
                    public_ip = IPManager().get_ip_by_id(public_ip_id)
                    public_ip = IPManager().remove_cidr_format_from_ip(public_ip.ip)
                if private_ip_id:
                    private_ip = IPManager().get_ip_by_id(private_ip_id)
                    private_ip = IPManager().remove_cidr_format_from_ip(private_ip.ip)
                bridge_name = defn.bridge_info.get('name')
                ctx = {}
                ctx['public_ip'] = public_ip
                ctx['private_ip'] = private_ip
                ctx['public_interface'] = public_interface
                ctx['bridge_name'] = bridge_name
                ctx['add_flag'] = add_flag
                ctx['csep_id'] = csep_id
                LOGGER.info('Context to network service is ' + to_str(ctx))
                if public_ip and private_ip:
                    node = DBSession.query(ManagedNode).filter_by(id = node.id).first()
                    self.manage_public_ip(node, ctx)




    def releasePublicIP(self, defn_id):
        from stackone.model.GridManager import GridManager
        from stackone.viewModel import Basic
        manager = Basic.getGridManager()
        nw_vm_rel_list = DBSession.query(NetworkVMRelation).filter_by(nw_def_id=defn_id)

        for nw_vm in nw_vm_rel_list:
            manager.disassociate_address(nw_vm.vm_id)




