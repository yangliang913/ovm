from stackone.model import DeclarativeBase, DBSession
import stackone.core.utils.constants as constants
from stackone.core.utils.utils import to_unicode, to_str, getHexID
from sqlalchemy.sql.expression import or_, not_
from stackone.model.IP import IPPool, PublicIPPool, PrivateIPPool, IPS
from stackone.model.network import NetworkVMRelation, NwManager
from stackone.model.network import NwManager
from stackone.model.SPRelations import CSEPDefLink
import logging
import tg
LOGGER = logging.getLogger('stackone.model')
class IPManager():
    def reserve_address(self, pool_id, entity_id):
        pool = IPPool.get_pool_by_id(pool_id)
        ip_db = pool.reserve_address(entity_id)
        return ip_db

    def release_address(self, pool_id, entity_id, ip_id=None):
        pool = IPPool.get_pool_by_id(pool_id)
        ip_db = pool.release_address(entity_id, ip_id)
        return ip_db

    def manage_public_ip(self, vm_id, public_ip_id, public_ip, csep_id, add_flag):
        LOGGER.info('Calling network service...')
        if vm_id:
            nw_vm_rel = DBSession.query(NetworkVMRelation).filter_by(vm_id=vm_id).first()
        elif public_ip:
            nw_vm_rel = DBSession.query(NetworkVMRelation).filter_by(public_ip_id=public_ip_id).first()
        if nw_vm_rel:
            LOGGER.info('Got network VM relation')
            nw_def_id = nw_vm_rel.nw_def_id
            private_ip_id = nw_vm_rel.private_ip_id
            nw_defn = NwManager().get_defn(nw_def_id)
            public_interface = ''
            if nw_defn:
                bridge_name = nw_defn.bridge_info.get('name')
            private_ip = ''
            ip_rec = self.get_ip_by_id(private_ip_id)
            if ip_rec:
                private_ip = self.remove_cidr_format_from_ip(ip_rec.ip)
            dom_id = None
            nw_service_host = NwManager().get_nw_service_host(csep_id)
            if nw_service_host:
                LOGGER.info('Got network service host')
                public_interface = self.get_public_interface(csep_id)
                ctx = {}
                ctx['public_ip'] = public_ip
                ctx['private_ip'] = private_ip
                ctx['public_interface'] = public_interface
                ctx['bridge_name'] = bridge_name
                ctx['add_flag'] = add_flag
                ctx['csep_id'] = csep_id
                LOGGER.info('context=' + to_str(ctx))
                NwManager().manage_public_ip(nw_service_host, ctx)

#    def get_public_interface(self, csep_id=None):
#        #from stackone.cloud.DbModel.platforms.cms.CSEP import NetworkService
#        LOGGER.info('Getting public interface...')
#        interface = None
#        if csep_id:
#            nw_service = DBSession.query(NetworkService).filter(NetworkService.csep_id == csep_id).first()
#            if nw_service:
#                interface = nw_service.interface
#            public_interface = tg.config.get('cms_public_interface')
#        LOGGER.info('Public interface is ' + to_str(interface))
#        return interface

    def associate_address(self, pool_id, ip_id, vm_id, csep_id=None):
        LOGGER.info('Associating address...')
        pool = IPPool.get_pool_by_id(pool_id)
        ip_db = pool.associate_address(ip_id, vm_id)
        if pool.type == constants.PUBLIC_IP_POOL:
            public_ip = self.remove_cidr_format_from_ip(ip_db.ip)
            add_flag = 'TRUE'
            public_ip_id = None
            self.manage_public_ip(vm_id, public_ip_id, public_ip, csep_id, add_flag)
        return ip_db
    #pass
    def disassociate_address(self, pool_id, ip_id, csep_id=None):
        LOGGER.info('Disassociating address...')
        pool = IPPool.get_pool_by_id(pool_id)
        ip_db = self.get_ip_by_id(ip_id)
        if pool.type == constants.PUBLIC_IP_POOL:
            public_ip_id = ip_db.id
            public_ip = self.remove_cidr_format_from_ip(ip_db.ip)
            add_flag = 'FALSE'
            vm_id = None
            nw_vm_rel = DBSession.query(NetworkVMRelation).filter_by(public_ip_id = ip_id).first()
            if nw_vm_rel:
                rec_list = DBSession.query(CSEPDefLink).filter_by(def_id = nw_vm_rel.nw_def_id)
                for rec in rec_list:
                    csep_id = rec.csep_id
                    self.manage_public_ip(vm_id,public_ip_id,public_ip,csep_id,add_flag)
        ip_db = pool.disassociate_address(ip_id)
        return ip_db

    def get_all_reserved_addresses(self, pool_id, entity_id=None):
        qry = DBSession.query(IPS).filter(IPS.pool_id == pool_id).filter(IPS.allocated == True)
        if entity_id:
            qry = qry.filter(IPS.reserved_by == entity_id)
        ips_db = qry.all()
        return ips_db

    def get_all_associated_addresses(self, pool_id, entity_id):
        ips_db = DBSession.query(IPS).filter(IPS.pool_id == pool_id).filter(IPS.reserved_by == entity_id).filter(IPS.allocated == True).filter(IPS.vm_id != None).all()
        return ips_db

    def get_all_unassociated_addresses(self, pool_id, entity_id):
        ips_db = DBSession.query(IPS).filter(IPS.pool_id == pool_id).filter(IPS.reserved_by == entity_id).filter(IPS.allocated == True).filter(IPS.vm_id == None).all()
        return ips_db

    def get_all_available_ips(self, pool_id):
        ips_db = DBSession.query(IPS).filter(IPS.pool_id == pool_id).filter(or_(IPS.reserved_by == None, IPS.reserved_by == '')).filter(IPS.allocated == False).all()
        return ips_db

    def get_all_addresses(self, pool_id):
        pool = IPPool.get_pool_by_id(pool_id)
        return pool.get_all_ips()

    def create_private_pool(self, name, cidr, range, nw_def_id, desc=None):
        pool = PrivateIPPool(name, cidr, range, nw_def_id, desc)
        DBSession.add(pool)
        return pool

    def create_public_pool(self, name, cidr=None, iplist=None, desc=None):
        pool = PublicIPPool(name, cidr, iplist, desc)
        DBSession.add(pool)
        return pool

    def delete_pool(self, pool_ids):
        if not isinstance(pool_ids, list):
            pool_ids = [pool_ids]
        pools = DBSession.query(IPPool).filter(IPPool.id.in_(pool_ids)).all()
        DBSession.query(IPS).filter(IPS.pool_id.in_(pool_ids)).delete()
        for pool in pools:
            DBSession.delete(pool)

    def delete_ip(self, exclude_ips, pool_id, cidr=None):
        if not isinstance(exclude_ips, list):
            exclude_ips = [exclude_ips]
        del_ips = DBSession.query(IPS).filter(~IPS.ip.in_(exclude_ips)).filter(IPS.pool_id == pool_id).all()
        for ip in del_ips:
            if not self.can_remove_ip(ip.id):
                LOGGER.info('Can not delete reserved IP:%s' % ip.ip)
                raise Exception('Can not delete reserved IP:%s' % ip.ip)
        for ip in del_ips:
            DBSession.delete(ip)

    def can_remove_pool(self, pool_id):
        if len(self.get_all_reserved_addresses(pool_id)) or self.get_csep_pool_rel(pool_id):
            return False
        return True

#    def get_csep_pool_rel(self, pool_id):
#        #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEPIPPool
#        return DBSession.query(CSEPIPPool).filter_by(ip_pool_id=pool_id).first()

    def can_remove_ip(self, ip_id):
        ip_db = self.get_ip_by_id(ip_id)
        if ip_db.is_reserved():
            return False
        return True

    def get_pool(self, nw_def_id):
        pool_rec = PrivateIPPool._get_pool(nw_def_id)
        return pool_rec

    def get_public_pool(self, pool_id):
        pool_rec = PublicIPPool._get_pool(pool_id)
        return pool_rec

    def get_all_public_ip_pools(self):
        return DBSession.query(PublicIPPool).all()

    def get_all_private_ip_pools(self):
        return DBSession.query(PrivateIPPool).all()

    def get_pool_by_id(self, pool_id):
        return IPPool.get_pool_by_id(pool_id)

    def get_ip_by_id(self, ip_id):
        return IPS.get_ip_by_id(ip_id)

    def add_new_ip(self, pool_id, addresses, cidr=None):
        pool = IPPool.get_pool_by_id(pool_id)
        return pool.app_new_ip(addresses, cidr)

    def get_cidr_format(self, ip):
        cidr_format = tg.config.get('cidr_format')
        idx = to_str(ip).find('/')
        if idx > 0:
            cidr_format = ip[idx:len(ip)]
        return cidr_format

    def put_ips_in_cidr_format(self, ip_list, cidr_format):
        result = []
        for address in ip_list:
            address = to_str(address) + to_str(cidr_format)
            result.append(address)
        return result

    def remove_cidr_format(self, ip_list):
        new_ip_list = []
        for ip in ip_list:
            idx = to_str(ip).find('/')
            if idx > 0:
                ip = ip[0L:idx]
        new_ip_list.append(ip)
        return new_ip_list

    def remove_cidr_format_from_ip(self, ip):
        idx = to_str(ip).find('/')
        if idx > 0:
            ip = ip[0:idx]
        return ip



def ip_manager_testing():
    print '========private_ip_manager_testing============'
    ip_manager = IPManager()
    pool = DBSession.query(IPPool).first()
    res_ip = ip_manager.reserve_address(pool.id, u'555')
    print '-------pool reserved for entity 555----------',
    print pool.name
    res_ips = ip_manager.get_all_reserved_addresses(pool.id, u'555')
    print '-------get_all_reserved_addresses----------',
    print res_ips
    ip_manager.associate_address(pool.id, res_ip.id, u'999')
    print '-----associate_address to vm 999------------'
    asso_ips = ip_manager.get_all_associated_addresses(pool.id, u'555')
    print '------get_all_associated_addresses------',
    print asso_ips
    unass_ips = ip_manager.get_all_unassociated_addresses(pool.id, u'555')
    print '-----get_all_unassociated_addresses-----------',
    print unass_ips
    ip_manager.disassociate_address(pool.id, asso_ips[0L].id)
    print '------disassociate_address----------',
    print asso_ips[0].id

