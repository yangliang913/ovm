from stackone.core.utils.firewall import IptablesManager
from stackone.model.ManagedNode import ManagedNode
#from stackone.cloud.DbModel.platforms.cms.CSEP import CSEP, NetworkService
from stackone.model.PrivateIP import NetworkServiceHostNetworkRelation
from stackone.model.network import NwDef, NwManager, NetworkVMRelation
from stackone.model.SPRelations import CSEPDefLink
from stackone.model.IP import IPPool, PublicIPPool, PrivateIPPool, IPS
from stackone.model.IPManager import IPManager
#from stackone.cloud.DbModel.platforms.cms.CSEP import CSEPIPPool
from stackone.core.utils.utils import to_unicode, to_str, get_cms_network_service_node, print_traceback
from stackone.model import DBSession
import stackone.core.utils.constants as constants
from stackone.model.Sites import Site
import logging
import tg
LOGGER = logging.getLogger('stackone.model')
class FirewallManager():
    manager = None
    def __init__(self):
        self.fw_map = {}
    @classmethod
    def get_manager(cls):
        if not cls.manager:
            cls.manager = FirewallManager()
        return cls.manager
    def get_firewall(self, entity_id):
        LOGGER.info('Getting firewall for CSEP/ Data Center...')
        try:
            fw = self.fw_map.get(entity_id)
            if not fw:
                fw = self.add_firewall_for_entity(entity_id)
            return fw
        except Exception as ex:
            LOGGER.error('Firewall does not exist')

    def add_firewall_for_entity(self, entity_id):
        LOGGER.info('Add firewall for CSEP/ Data Center...')
        if entity_id:
            csep = DBSession.query(CSEP).filter_by(id=entity_id).first()
            if csep:
                LOGGER.info('Got CSEP')
                nw_service_host = csep.get_nw_service_host()
                if nw_service_host:
                    fw = IptablesManager(csep.name)
                    self.fw_map[entity_id] = fw
                    LOGGER.info('Firewall is added to CSEP')
                    self.set_nw_service_host(fw, nw_service_host)
                    LOGGER.info('Network service host is added to firewall')
                return fw
            dc = DBSession.query(Site).filter_by(id=entity_id).first()
            if dc:
                LOGGER.info('Got DC')
                nw_service_host = get_cms_network_service_node()
                if nw_service_host:
                    fw = IptablesManager(dc.name)
                    self.fw_map[entity_id] = fw
                    LOGGER.info('Firewall is added to DC')
                    self.set_nw_service_host(fw, nw_service_host)
                    LOGGER.info('Network service host is added to firewall')
                return fw

    def init_firewall_for_all_csep(self):
        LOGGER.info('Applying firewall rules for all csep and Data Center...')
        print 'Applying firewall rules for all CSEP and Data Center...'
        sites = DBSession.query(Site)
        if sites[0]:
            LOGGER.info('Got the site. Site name is ' + to_str(sites[0].name))
            site_id = sites[0].id
            site_name = sites[0].name
            nw_service_host = get_cms_network_service_node()
            if nw_service_host:
                fw = IptablesManager(site_name)
                self.fw_map[site_id] = fw
                self.set_nw_service_host(fw, nw_service_host)
                self.dump(fw)
        csep_list = DBSession.query(CSEP)
        for each_csep in csep_list:
            csep_id = each_csep.id
            LOGGER.info('Got the CSEP. CSEP name is ' + to_str(each_csep.name))
            nw_service_host = each_csep.get_nw_service_host()
            fw = None
            if nw_service_host:
                fw = IptablesManager(each_csep.name)
                self.fw_map[csep_id] = fw
                self.set_nw_service_host(fw, nw_service_host)
            nw_def_list = DBSession.query(CSEPDefLink).filter_by(csep_id=csep_id)
            for each_def in nw_def_list:
                nw_def_id = each_def.def_id
                self.set_firewall_for_network(csep_id, nw_def_id)
            ip_list = self.get_associated_public_ips(csep_id)
            for ip in ip_list:
                public_ip = IPManager().remove_cidr_format_from_ip(ip.ip)
                nw_vm_rel = DBSession.query(NetworkVMRelation).filter_by(public_ip_id=ip.id).first()
                if nw_vm_rel:
                    ip_rec = IPS.get_ip_by_id(nw_vm_rel.private_ip_id)
                    if ip_rec:
                        private_ip = IPManager().remove_cidr_format_from_ip(ip_rec.ip)
                        self.set_firewall_for_public_ip_mapping(csep_id, public_ip, private_ip)
            if fw:
                self.dump(fw)


    def get_associated_public_ips(self, csep_id):
        ip_list = DBSession.query(IPS).join((IPPool, IPPool.id == IPS.pool_id)).join((CSEPIPPool, CSEPIPPool.ip_pool_id == IPPool.id)).filter(CSEPIPPool.csep_id == csep_id).filter(IPPool.type == constants.PUBLIC_IP_POOL).filter(IPS.vm_id != None)
        return ip_list

    def set_firewall_for_network(self, csep_id, nw_def_id, site_id=None):
        LOGGER.info('Applying firewall rules for network...')
        bridge_name = ''
        cidr = ''
        public_interface = ''
        nat_info = None
        fw = None
        try:
            if csep_id:
                fw = self.get_firewall(csep_id)
            if site_id:
                fw = self.get_firewall(site_id)
            if fw:
                556
                LOGGER.info('Got the firewall')
                nw_def = NwManager().get_defn(nw_def_id)
                if nw_def.is_deleted:
                    LOGGER.info('Skipping Deleted NW Def : %s:%s' %(nw_def_id,nw_def.name))
                    return None
                if nw_def:
                    bridge_name = nw_def.bridge_info.get('name')
                    nat_info = nw_def.nat_info
                LOGGER.info('NW NAME ' + nw_def.name + ':' + nw_def_id)
                LOGGER.info('NAT listinfo is ' + to_str(nat_info))
                nated = False
                if nat_info:
                    337
                    nat_interface = nat_info.get('interface')
                    LOGGER.info('NAT interface is ' + to_str(nat_interface))
                    if nat_interface:
                        nated = True
                if nated:
                    552
                    LOGGER.info('NAT forwarded network')
                    cidr = self.get_cidr(nw_def_id)
                    if not cidr:
                        411
                        LOGGER.info('CIDR Empty for ' + nw_def.name + ':'+nw_def_id)
                    public_interface = self.get_public_interface(csep_id)
                    LOGGER.info('bridge name= ' + to_str(bridge_name) + ', cidr= ' + to_str(cidr) + ', public interface= ' + to_str(public_interface))
                    fw.ensure_network_nating(bridge_name, cidr, public_interface)
                    LOGGER.info('Ensured network nating')
                    LOGGER.info('Isolated network')
                    fw.ensure_network_isolation(bridge_name)
                    LOGGER.info('Ensured network isolation')
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))

    def remove_firewall_for_network(self, csep_id, nw_def_id, site_id=None):
        LOGGER.info('Removing firewall rules for network...')
        bridge_name = ''
        cidr = ''
        public_interface = ''
        nat_info = None
        fw = None
        try:
            if csep_id:
                fw = self.get_firewall(csep_id)
            if site_id:
                fw = self.get_firewall(site_id)
            if fw:
                LOGGER.info('Got the firewall for csep')
                nw_def = NwManager().get_defn(nw_def_id)
                if nw_def:
                    bridge_name = nw_def.bridge_info.get('name')
                    nat_info = nw_def.nat_info
                LOGGER.info('NAT info is ' + to_str(nat_info))
                nated = False
                if nat_info:
                    nat_interface = nat_info.get('interface')
                    LOGGER.info('NAT interface is ' + to_str(nat_interface))
                    if nat_interface:
                        nated = True
                if nated:
                    LOGGER.info('NAT forwarded network')
                    cidr = self.get_cidr(nw_def_id)
                    public_interface = self.get_public_interface(csep_id)
                    LOGGER.info('bridge name= ' + to_str(bridge_name) + ', cidr= ' + to_str(cidr) + ', public interface= ' + to_str(public_interface))
                    fw.remove_network_nating(bridge_name, cidr, public_interface)
                    LOGGER.info('Removed network nating')
                    LOGGER.info('Isolated network')
                    fw.remove_network_isolation(bridge_name)
                    LOGGER.info('Removed network isolation')
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))

    def set_firewall_for_public_ip_mapping(self, csep_id, public_ip, private_ip):
        LOGGER.info('Applying firewall rules for public ip mapping...')
        fw = None
        try:
            fw = self.get_firewall(csep_id)
            if fw:
                LOGGER.info('Got the firewall for csep')
                LOGGER.info('Mapping, public ip=' + to_str(public_ip) + ', private ip=' + to_str(private_ip))
                fw.ensure_floating_forward(public_ip, private_ip)
                LOGGER.info('Ensured floating forward')
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))

    def set_nw_service_host(self, fw, nw_service_host):
        if nw_service_host:
            if not nw_service_host.is_up():
                LOGGER.error('Network service node is down')
                return None
            if nw_service_host.maintenance:
                LOGGER.error('Network service node is in maintenance')
                return None
            LOGGER.info('Got network service node. Host name is ' + to_str(nw_service_host.hostname))
            fw.set_nw_service_host(nw_service_host)
            fw.init_host()

    def get_public_interface(self, csep_id=None):
        public_interface = None
        if csep_id:
            csep = DBSession.query(CSEP).filter_by(id=csep_id).first()
            nw_service = csep.network_service[0L]
            if nw_service:
                public_interface = nw_service.interface
                print public_interface,'######################3public_interface##########3'
        else:
            public_interface = tg.config.get('cms_public_interface')
        return public_interface

    def get_cidr(self, nw_def_id):
        cidr = None
        ip_pool = IPManager().get_pool(nw_def_id)
        if ip_pool:
            cidr = ip_pool.cidr
        return cidr

    def dump(self, fw):
        fw_data = {}
        nw_service_host = fw.nw_service_host
        if nw_service_host:
            print 'Network Service Host is ',
            print nw_service_host.hostname
            fw_data['nw_svc_host_name'] = nw_service_host.hostname
        else:
            fw_data['nw_svc_host_name'] = ''
        print 'Chain name is ',
        print constants.FW_CHAIN_NAME
        fw_data['chain_name'] = constants.FW_CHAIN_NAME
        table_data_list = []
        for tables in [fw.ipv4, fw.ipv6]:
            table_data = {}
            tables['filter'].dump()
            rule_data = []
            for r in tables['filter'].rules:
                rule_data.append(str(r))
            table_data['rule_data'] = rule_data
            table_data['chains'] = str(tables['filter'].chains)
            table_data['unwrapped_chains'] = str(tables['filter'].unwrapped_chains)
            table_data_list.append(table_data)
        fw_data['table_data'] = table_data_list
        return fw_data

    def get_fw_info(self):
        fw_main_data = []
        LOGGER.info('Getting firewall rules info for all csep and Data Center...')
        print 'Getting firewall rules info for all csep and Data Center...'
        sites = DBSession.query(Site)
        if sites[0]:
            LOGGER.info('Got the site. Site name is ' + to_str(sites[0L].name))
            site_id = sites[0L].id
            site_name = sites[0L].name
            nw_service_host = get_cms_network_service_node()
            if nw_service_host:
                fw = self.get_firewall(site_id)
                fw.set_chain_name(site_name)
                fw_data = self.dump(fw)
                fw_main_data.append(fw_data)
        csep_list = DBSession.query(CSEP)
        for each_csep in csep_list:
            LOGGER.info('Got the CSEP. CSEP name is ' + to_str(each_csep.name))
            nw_service_host = each_csep.get_nw_service_host()
            if nw_service_host:
                fw = self.get_firewall(each_csep.id)
                fw.set_chain_name(each_csep.name)
                fw_data = self.dump(fw)
                fw_main_data.append(fw_data)
        return fw_main_data



