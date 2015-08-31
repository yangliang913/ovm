from datetime import datetime
from stackone.core.utils.utils import to_unicode, to_str, getHexID, remove_cidr_format_from_ip, get_ips_from_cidr
import stackone.core.utils.constants as constants
from sqlalchemy.sql.expression import or_, not_
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String, Boolean, PickleType, Float, DateTime
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.orm import relation, backref
from stackone.model import DeclarativeBase, DBSession
from stackone.model.LockManager import LockManager
from stackone.model.VM import VM
from stackone.model.network import NetworkVMRelation
import os
import tg
import pprint
import traceback
import logging
LOGGER = logging.getLogger('stackone.model')
import netaddr as netapi

class IPPool(DeclarativeBase):
    __doc__ = '\n\n    '
    __tablename__ = 'ip_pool'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50))
    cidr = Column(Unicode(50))
    description = Column(Unicode(250))
    used = Column(Integer, default=0)
    total = Column(Integer, default=0)
    type = Column(Unicode(50), default=u'NONE')
    __mapper_args__ = {'polymorphic_on': type}
    def __init__(self, name, cidr=None, iplist=None, description=None):
        self.id = getHexID()
        self.name = name
        self.cidr = cidr
        self.iplist = iplist
        self.ip_networks = []
        self.description = description
        self._validate_network()
        self._validate_range_with_network()
        self._populate_ips_table()
        self.total = len(self.ips)
        self.used = 0
        LOGGER.debug('name:%s, cidr:%s, iplist:%s, total:%s' % (self.name, self.cidr, self.iplist, self.total))

    def get_cidr_format(self, ip):
        cidr_format = tg.config.get('cidr_format')
        idx = to_str(ip).find('/')
        if idx > 0:
            cidr_format = ip[idx:len(ip)]
        return cidr_format

    def _populate_ips_table(self):
        for ip in self.iplist:
            ips_obj = IPS()
            ips_obj.pool_id = self.id
            ips_obj.ip = ip
            self.ips.append(ips_obj)
        LOGGER.debug('IPPool:%s successfully created' % self.name)

    def _validate_network(self):
        pass

    def _validate_range_with_network(self):
        pass

    def _get_all_pool(self):
        pass

    @classmethod
    def get_pool_by_name(cls, pool_name):
        return DBSession.query(cls).filter(cls.name == pool_name).first()
    
    @classmethod    
    def get_pool_by_id(cls, pool_id):
        return DBSession.query(cls).filter(cls.id == pool_id).first()
    
    def get_all_ips(self):
        return self.ips

    def get_ip(self, ip):
        ip_db = DBSession.query(IPS).filter(IPS.pool_id == self.id).filter(IPS.ip == ip).first()
        return ip_db
    #@property
    def reserve_address(self, entity_id):
        try:
            LOGGER.info('Getting CMS Lock...')
            LockManager().get_lock(constants.IPS, self.id, constants.RESERVE_ADDRESS_OP, constants.Table_ip_pool)
            ip_db = DBSession.query(IPS).filter(IPS.pool_id == self.id).filter(or_(IPS.reserved_by == None, IPS.reserved_by == '')).filter(IPS.allocated == False).first()
            if not ip_db:
                LOGGER.error('All IPs are Reserved')
                raise Exception('All IPs are Reserved')
            else:
                ip_db.reserved_by = entity_id
                ip_db.allocated = True
                used = 0
                if self.used != None:
                    used = int(self.used)
                self.used = used + 1
                DBSession.add(ip_db)
                return ip_db
        finally:
            LOGGER.info('Releasing CMS Lock...')
            LockManager().release_lock()
        return None

    def release_address(self, entity_id, ip_id=None):
        try:
            LOGGER.info('Getting CMS Lock...')
            LockManager().get_lock(constants.IPS, self.id, constants.RESERVE_ADDRESS_OP, constants.Table_ip_pool)
            qry = DBSession.query(IPS).filter(IPS.pool_id == self.id).filter(IPS.reserved_by == entity_id)
            if ip_id:
                qry = qry.filter(IPS.id == ip_id)
            ips_db = qry.all()
            for ip_db in ips_db:
                ip_db.reserved_by = None
                ip_db.vm_id = None
                ip_db.allocated = False
                self.used = int(self.used) - 1
                DBSession.add(ip_db)
        finally:
            LOGGER.info('Releasing CMS Lock...')
            LockManager().release_lock()
        return None

    def associate_address(self, ip_id, vm_id):
        try:
            LOGGER.info('Getting CMS Lock...')
            LockManager().get_lock(constants.IPS, self.id, constants.ASSOCIATE_ADDRESS_OP, constants.Table_ip_pool)
            ip_db = DBSession.query(IPS).filter(IPS.pool_id == self.id).filter(IPS.id == ip_id).filter(IPS.allocated == True).first()
            ip_db.vm_id = vm_id
            vm = DBSession.query(VM).filter(VM.id == vm_id).first()
            if vm:
                private_networks_vm_rel = vm.network_vm_relations
                if len(private_networks_vm_rel):
                    private_networks_vm_rel[0].public_ip_id = ip_id
                    DBSession.add(private_networks_vm_rel[0])
            
            DBSession.add(ip_db)
            return ip_db
        finally:
            LOGGER.info('Releasing CMS Lock...')
            LockManager().release_lock()
            LOGGER.info('IP:%s attached to VM_Id:%s' % (ip_db.ip, vm_id))

    def disassociate_address(self, ip_id):
        ip_db = None
        try:
            LOGGER.info('Getting CMS Lock...')
            LockManager().get_lock(constants.IPS, self.id, constants.ASSOCIATE_ADDRESS_OP, constants.Table_ip_pool)
            ip_db = DBSession.query(IPS).filter(IPS.pool_id == self.id).filter(IPS.id == ip_id).first()
            private_networks_vm_rel = DBSession.query(NetworkVMRelation).filter(NetworkVMRelation.public_ip_id == ip_id).filter(NetworkVMRelation.vm_id == ip_db.vm_id).first()
            if private_networks_vm_rel:
                private_networks_vm_rel.public_ip_id = None
                DBSession.add(private_networks_vm_rel)
                
            ip_db.vm_id = None
            DBSession.add(ip_db)
            return ip_db
        finally:
            LOGGER.info('Releasing CMS Lock...')
            LockManager().release_lock()
            LOGGER.info('IP:%s disassociated' % ip_db.ip)
        return None

    def app_new_ip(self, addresses, cidr=None):
        if not isinstance(addresses, list):
            addresses = [addresses]

        ips = [ip_db.ip for ip_db in self.ips]
        addresses = [address for address in addresses if address not in ips]
        self.iplist = addresses
        self._validate_network()
        for address in addresses:
            ip_db = self.get_ip(address)
            if not ip_db:
                ips_obj = IPS()
                ips_obj.pool_id = self.id
                ips_obj.ip = address
                self.ips.append(ips_obj)
                LOGGER.info('Added IP:%s to Pool:%s' % (address, self.name))
                continue
                
            ip_db.ip = address
            DBSession.add(ip_db)
            LOGGER.info('Updated IP:%s in the Pool:%s' % (address, self.name))


    def _validate_address(self, addresses):
        pass

    def __str__(self):
        return '(%s, Name:%s, ID:%s, CIDR:%s)' % (self.__class__, self.name, self.id, self.cidr)



class PublicIPPool(IPPool):
    __doc__ = '\n        \n    '
    __mapper_args__ = {'polymorphic_identity': constants.PUBLIC_IP_POOL}
    def __init__(self, name, cidr=None, iplist=None, description=None):
        IPPool.__init__(self, name, cidr, iplist, description)

    def _get_all_pool(self):
        return DBSession.query(PublicIPPool).all()

    def check_ips(self):
        pool_ids = [p.id for p in self._get_all_pool()]
        return DBSession.query(IPS).filter(IPS.pool_id.in_(pool_ids)).filter(IPS.ip.in_(self.iplist)).all()


    def _validate_network(self):
        if self.iplist:
            if len(self.check_ips()):
                excep_msg = 'Address already in use'
                LOGGER.error(excep_msg)
                raise Exception(excep_msg)
        
    @classmethod
    def _get_pool(cls, pool_id):
        pool_obj = None
        if pool_id:
            pool_obj = DBSession.query(cls).filter(cls.id == pool_id).first()
        
        return pool_obj


class PrivateIPPool(IPPool):
    __doc__ = '\n\n    '
    range = Column(Unicode(50))
    nw_def_id = Column(Unicode(50))
    __mapper_args__ = {'polymorphic_identity': constants.PRIVATE_IP_POOL}
    def __init__(self, name, cidr, range, nw_def_id, description=None):
        self.range = range
        self.nw_def_id = nw_def_id
        iplist = None
        IPPool.__init__(self, name, cidr, iplist, description)
        return None

    def _validate_range_with_network(self):
        ip_networks = []
        if self.range:
            start, end = self.range.split('-')
            ip_addresses = list(netapi.iter_iprange(start, end))
            ip_networks.extend(netapi.cidr_merge(ip_addresses))
        else:
            ip_addresses = get_ips_from_cidr(self.cidr)
            ip_networks.extend(netapi.cidr_merge(ip_addresses))
        address_lst = []
        net = netapi.IPNetwork(self.cidr)
        for network in ip_networks:
            for address in network:
                address_lst.append(str(address))
                if address not in net:
                    excep_msg = 'given dhcp range:%s not a subset of network:%s' % (self.range, net)
                    LOGGER.error(excep_msg)
                    raise Exception(excep_msg)
                    
        self.iplist = address_lst

    def _get_all_pool(self):
        return DBSession.query(PrivateIPPool).all()

    @classmethod
    def _get_pool(cls, nw_def_id):
        pool_obj = None
        if nw_def_id:
            pool_obj = DBSession.query(cls).filter(cls.nw_def_id == nw_def_id).first()
        return pool_obj


class IPS(DeclarativeBase):
    __doc__ = '\n\n    '
    __tablename__ = 'ips'
    id = Column(Unicode(50), primary_key=True)
    pool_id = Column(Unicode(50), ForeignKey('ip_pool.id', ondelete='CASCADE'))
    ip = Column(Unicode(50))
    allocated = Column(Boolean, default=False)
    vm_id = Column(Unicode(50))
    reserved_by = Column(Unicode(50))
    vdc_context = Column(Unicode(50))
    pool = relation('IPPool', backref='ips')
    def __init__(self):
        self.id = getHexID()

    def get_pool(self):
        return self.pool

    def is_reserved(self):
        return self.allocated

    @classmethod
    def get_ip_by_id(cls, ip_id):
        return DBSession.query(cls).filter(cls.id == ip_id).first()
        
    def __str__(self):
        return '(%s, pool_id:%s, ID:%s, IP:%s, Allocated:%s, vm_id:%s, Reserved_by:%s)' % (self.__class__, self.pool_id, self.id, self.ip, self.allocated, self.vm_id, self.reserved_by)



