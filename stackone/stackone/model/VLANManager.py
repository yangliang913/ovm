from stackone.core.utils.utils import to_unicode, to_str, getHexID
import stackone.core.utils.utils
from stackone.core.utils.constants import *
constants = stackone.core.utils.constants
import os
import tg
import pprint
import traceback
import transaction
from sqlalchemy import func, outerjoin, join
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String, Boolean, PickleType, Float, DateTime
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.orm import relation, backref
from stackone.model.Groups import ServerGroup
from stackone.model.network import NwDef
from stackone.model import DeclarativeBase, DBSession
from stackone.model.Entity import EntityRelation
from stackone.model.LockManager import LockManager
import netaddr
import math
import pprint
import re
import logging
LOGGER = logging.getLogger('stackone.model')
class VLANIDPool(DeclarativeBase):
    __tablename__ = 'vlan_id_pools'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50))
    description = Column(Unicode(50))
    range = Column(Unicode(50))
    interface = Column(Unicode(50))
    used = Column(Integer, default = 0)
    total = Column(Integer)
    cidr = Column(Unicode(50))
    num_hosts = Column(Integer)
    def __init__(self):
        pass



class VLANIDPoolSPRelation(DeclarativeBase):
    __tablename__ = 'vlan_id_pool_sp_relation'
    id = Column(Unicode(50), primary_key=True)
    vlan_id_pool_id = Column(Unicode(50), ForeignKey('vlan_id_pools.id', ondelete='CASCADE'))
    sp_id = Column(Unicode(50), ForeignKey('server_groups.id'))
    fk_vip_vipspr = relation('VLANIDPool', backref='vlan_id_pool_sp_relation')
    fk_sg_vipspr = relation('ServerGroup', backref='vlan_id_pool_sp_relation')
    def __init__(self):
        pass



class VLANID(DeclarativeBase):
    __tablename__ = 'vlan_ids'
    id = Column(Unicode(50), primary_key=True)
    vlan_id = Column(Integer)
    vlan_id_pool_id = Column(Unicode(50), ForeignKey('vlan_id_pools.id', ondelete='CASCADE'))
    used_by = Column(Unicode(50))
    fk_vip_vi = relation('VLANIDPool', backref='vlan_ids')
    def __init__(self):
        pass



class PoolManager():
    def __init__(self):
        pass

    def mark_used(self, pool_tag, context):
        if pool_tag == constants.VLAN_ID_POOL:
            LOGGER.info('Marking VLAN ID as used...')
            pool_id = context.get('pool_id')
            nw_def_id = context.get('nw_def_id')
            vlan_id = context.get('vlan_id')
            vlan_id_rec = DBSession.query(VLANID).filter_by(vlan_id_pool_id=pool_id, vlan_id=vlan_id).first()
            if vlan_id_rec:
                vlan_id_rec.used_by = nw_def_id

    def get_next_id(self, pool_tag, context):
        available_id = None
        interface = None
        if pool_tag == constants.VLAN_ID_POOL:
            LOGGER.info('Get next vlan id from pool...')
            pool_id = context.get('pool_id')
            nw_def_id = context.get('nw_def_id')
            null_value = None
            LOGGER.info('Getting CMS Lock...')
            LockManager().get_lock(constants.VLAN_ID_POOL, pool_id, constants.NEXT_VLAN_ID, constants.Table_vlan_id_pools)
            interface = VLANManager().get_interface(pool_id)
            rs = DBSession.query(func.min(VLANID.vlan_id).label('vlan_id')).join((VLANIDPool, VLANIDPool.id == VLANID.vlan_id_pool_id)).filter(VLANID.used_by == null_value).filter(VLANIDPool.id == pool_id).first()
            is_tuple = isinstance(rs, tuple)
            if is_tuple and rs[0]:
                available_id = rs.vlan_id
                LOGGER.info('Available vlan id is ' + to_str(available_id))
                context['vlan_id'] = available_id
                self.mark_used(pool_tag, context)
                vlan = DBSession.query(VLANIDPool).filter(VLANIDPool.id == pool_id).first()
                if vlan:
                    vlan.used = int(vlan.used) + 1
            LOGGER.info('Releasing CMS Lock...')
            LockManager().release_lock()
        return (available_id, interface)

    def get_unused_id(self, pool_tag, context):
        unused_id = None
        interface = None
        if pool_tag == constants.VLAN_ID_POOL:
            LOGGER.info('Get unused (free) vlan id from pool...')
            available_id,interface = PoolManager().get_next_id(pool_tag, context)
            msg = 'available_id :%s, interface :%s' % (available_id, interface)
            print msg
            LOGGER.info(msg)
            if not available_id:
                pool_id = context.get('pool_id')
                LOGGER.info('Getting CMS Lock...')
                LockManager().get_lock(constants.VLAN_ID_POOL, pool_id, constants.NEXT_VLAN_ID, constants.Table_vlan_id_pools)
                rs = DBSession.query(func.max(VLANID.vlan_id).label('vlan_id')).join((VLANIDPool, VLANIDPool.id == VLANID.vlan_id_pool_id)).filter(VLANIDPool.id == pool_id).first()
                is_tuple = isinstance(rs, tuple)
                if is_tuple and rs[0]:
                    max_id = rs.vlan_id
                    msg = 'Max vlan id is ' + to_str(max_id)
                    print msg
                    LOGGER.info(msg)
                    if max_id:
                        unused_id = int(max_id) + 1
                else:
                    unused_id = 1
                raise Exception('VLAN ID Pool limit is reached. So need to take VLAN ID from out of range. The next VLAN ID is ' + to_str(unused_id) + ' which can be used.')
                LOGGER.info('Releasing CMS Lock...')
                LockManager().release_lock()
            else:
                unused_id = available_id
            nw_list = DBSession.query(NwDef).filter_by(type=NwDef.VLAN_NW)
            for nw_rec in nw_list:
                vlan_info = nw_rec.vlan_info
                bridge_info = nw_rec.bridge_info
                nat_info = nw_rec.nat_info
                ex_vlan_id = vlan_info.get('vlan_id')
                if not ex_vlan_id or ex_vlan_id == 'None':
                    bridgename = bridge_info.get('name')
                    if bridgename.find('.') >= 0:
                        ex_vlan_id = bridge_info.get('name').split('.')[1]
                    else:
                        ex_vlan_id = 0
                ex_interface = nat_info.get('interface')
                if int(unused_id) == int(ex_vlan_id) and to_str(interface).strip() == to_str(ex_interface).strip():
                    context['vlan_id'] = available_id
                    pool_id = context.get('pool_id')
                    LOGGER.info('Getting CMS Lock...')
                    LockManager().get_lock(constants.VLAN_ID_POOL, pool_id, constants.NEXT_VLAN_ID, constants.Table_vlan_id_pools)
                    self.mark_used(pool_tag, context)
                    vlan = DBSession.query(VLANIDPool).filter(VLANIDPool.id == pool_id).first()
                    if vlan:
                        vlan.used = int(vlan.used) + 1
                    LOGGER.info('VLAN ID ' + to_str(unused_id) + ' and interface ' + interface + ' are used in vitual network ' + to_str(nw_rec.name))
                    LOGGER.info('Releasing CMS Lock...')
                    LockManager().release_lock()
        return (unused_id, interface)

    def release_id(self, pool_tag, context):
        if pool_tag == constants.VLAN_ID_POOL:
            LOGGER.info('Release vlan id here...')
            pool_id = context.get('pool_id')
            vlan_id = context.get('vlan_id')
            nw_def_id = context.get('nw_def_id')
            if nw_def_id:
                rec = DBSession.query(VLANID).filter_by(used_by=nw_def_id).first()
            else:
                rec = DBSession.query(VLANID).join((VLANIDPool, VLANIDPool.id == VLANID.vlan_id_pool_id)).filter(VLANIDPool.id == pool_id).filter(VLANID.vlan_id == vlan_id).first()
            if rec:
                rec.used_by = None
            vlan = DBSession.query(VLANIDPool).filter(VLANIDPool.id == pool_id).first()
            if vlan:
                vlan.used = int(vlan.used) - 1



class VLANManager():
    def __init__(self):
        pass

    def get_unused_id(self, pool_tag, context):
        result = PoolManager().get_unused_id(pool_tag, context)
        return result

    def release_id(self, pool_tag, context):
        PoolManager().release_id(pool_tag, context)

    def get_interface(self, pool_id):
        interface = None
        rec = DBSession.query(VLANIDPool).filter_by(id=pool_id).first()
        if rec:
            interface = rec.interface
        return interface

    def attach_vlan_id_pool(self, sp_ids, vlan_id_pool):
        if sp_ids:
            id_list = sp_ids.split(',')
            for each_id in id_list:
                vlan_id_pool_sp_rel = None
                vlan_id_pool_sp_rel = DBSession.query(VLANIDPoolSPRelation).filter_by(vlan_id_pool_id=vlan_id_pool.id, sp_id = each_id).first()
                if not vlan_id_pool_sp_rel:
                    vlan_id_pool_sp_rel = VLANIDPoolSPRelation()
                    vlan_id_pool_sp_rel.id = getHexID()
                    vlan_id_pool_sp_rel.sp_id = each_id
                    vlan_id_pool.vlan_id_pool_sp_relation.append(vlan_id_pool_sp_rel)
                    LOGGER.info('SP relation is added to VLAN ID Pool')

    def detach_vlan_id_pool(self, site_id, sp_ids, vlan_id_pool_id):
        sp_id_list = []
        if sp_ids:
            sp_id_list = sp_ids.split(',')
        ent_rel_list = DBSession.query(EntityRelation).filter_by( src_id = site_id, relation = 'Children')
        for ent_rel in ent_rel_list:
            group_id = ent_rel.dest_id
            if group_id not in sp_id_list:
                vlan_id_pool_rel = DBSession.query(VLANIDPoolSPRelation).filter_by(vlan_id_pool_id=vlan_id_pool_id, sp_id=group_id).first()
                if vlan_id_pool_rel:
                    DBSession.delete(vlan_id_pool_rel)
                    LOGGER.info('VLAN ID Pool relation with SP is removed')


    def add_vlan_id_pool(self, auth, site_id, name, desc, range, interface, sp_ids, cidr, num_hosts):
        LOGGER.info('Adding VLAN ID Pool..')
        vlan_id_pool = VLANIDPool()
        vlan_id_pool_id = getHexID()
        vlan_id_pool.id = vlan_id_pool_id
        vlan_id_pool.name = name
        vlan_id_pool.description = desc
        vlan_id_pool.range = range
        vlan_id_pool.interface = interface
        vlan_id_pool.cidr = cidr
        vlan_id_pool.num_hosts = num_hosts
        rnge = range.split('-')
        diff = int(rnge[1]) - int(rnge[0])
        vlan_id_pool.total = diff
        network_size = num_hosts
        num_networks = diff + 1
        vlan_start = rnge[0]
        vlan_nw_infos = self.get_vlan_network_info(cidr, num_networks, network_size, vlan_start, interface)
        for info_dict in vlan_nw_infos:
            vlan_nw_info_db = self.create_vlan_network_info_db(info_dict)
            vlan_id_pool.vlan_nws_infos.append(vlan_nw_info_db)
        LOGGER.info('VLAN Network info added.')
        self.attach_vlan_id_pool(sp_ids, vlan_id_pool)
        nums = range.split('-')
        first_num = nums[0]
        last_num = nums[1]
        i = first_num
        while int(i) <= int(last_num):
            vlan_id = VLANID()
            vlan_id.id = getHexID()
            vlan_id.vlan_id = int(i)
            vlan_id.used_by = None
            vlan_id_pool.vlan_ids.append(vlan_id)
            i = int(i) + 1
        LOGGER.info('VLAN IDs are added')
        DBSession.add(vlan_id_pool)
        transaction.commit()
        LOGGER.info('VLAN ID Pool is added.')

    def get_vlan_network_info(self, cidr, num_networks, network_size, vlan_start, interface, **msg):
        num_networks = int(num_networks)
        network_size = int(network_size)
        vlan_start = int(vlan_start)
        msg = '\nnum_networks:%s, network_size:%s, vlan_start:%s, cidr:%s, interface:%s ' % (num_networks, network_size, vlan_start, cidr, interface)
        print msg
        LOGGER.info(msg)
        if num_networks + vlan_start > 4094:
            raise ValueError('The sum between the number of networks and the vlan start cannot be greater than 4094')
        fixed_net = netaddr.IPNetwork(cidr)
        msg = '\nfixed_net:%s, num_networks*network_size:%s' % (len(fixed_net), num_networks * network_size)
        print msg
        LOGGER.info(msg)
        if len(fixed_net) < num_networks * network_size:
            raise ValueError('The network range is not big enough to fit %(num_networks)s. Network size is %(network_size)s' % locals())
        private_ip_bottom_reserve = int(tg.config.get('private_ip_bottom_reserve', 10))
        private_ip_top_reserve = int(tg.config.get('private_ip_top_reserve', 2))
        interface_str = 'x'
        if interface:
            if_str = re.sub('\\D', '', interface)
            if if_str:
                interface_str = if_str
        result = []
        for index in range(num_networks):
            vlan = vlan_start + index
            start = index * network_size
            significant_bits = 32 - int(math.log(network_size, 2))
            cidr = '%s/%s' % (fixed_net[start], significant_bits)
            project_net = netaddr.IPNetwork(cidr)
            net = {}
            net['cidr'] = to_unicode(cidr)
            net['netmask'] = to_unicode(project_net.netmask)
            net['gateway'] = to_unicode(list(project_net)[1])
            net['broadcast'] = to_unicode(project_net.broadcast)
            net['vpn_private_address'] = to_unicode(list(project_net)[2])
            net['dhcp_start'] = to_unicode(list(project_net)[private_ip_bottom_reserve])
            net['dhcp_end'] = to_unicode(list(project_net)[private_ip_top_reserve * -1])
            net['vlan_id'] = vlan
            net['bridge'] = to_unicode('br%s_%s' % (interface_str, vlan))
            result.append(net)
        return result

    def create_vlan_network_info(self, vlan_id_pool, cidr, num_networks, network_size, vlan_start, interface):
        vlan_nw_infos = self.get_vlan_network_info(cidr, num_networks, network_size, vlan_start, interface)
        for info_dict in vlan_nw_infos:
            vlan_nw_info_db = self.create_vlan_network_info_db(info_dict)
            vlan_nw_info_db.vlan_pool_id = vlan_id_pool.id
            DBSession.add(vlan_nw_info_db)
        LOGGER.info('created vlan_network_info for vlan_id_pool:%s' % vlan_id_pool.name)

    def create_vlan_network_info_db(self, info_dict):
        vlan_nw_info_db = VLANNetworkInfo(cidr=info_dict.get('cidr'), dhcp_start=info_dict.get('dhcp_start'), dhcp_end=info_dict.get('dhcp_end'), gateway=info_dict.get('gateway'), netmask=info_dict.get('netmask'), vlan_id=info_dict.get('vlan_id'), vpn_private_address=info_dict.get('vpn_private_address'), broadcast=info_dict.get('broadcast'), bridge=info_dict.get('bridge'))
        return vlan_nw_info_db

    def delete_vlan_network_info(self, vlan_id_pool, vlan_ids):
        if not isinstance(vlan_ids, list):
            vlan_ids = [vlan_ids]
        DBSession.query(VLANNetworkInfo).filter(VLANNetworkInfo.vlan_id.in_(vlan_ids)).filter(VLANNetworkInfo.vlan_pool_id == vlan_id_pool.id).delete()
        LOGGER.info('deleted vlan_network_info for vlan_id_pool:%s' % vlan_id_pool.name)

    def edit_vlan_id_pool(self, auth, site_id, vlan_id_pool_id, desc, range, sp_ids, name):
        LOGGER.info('Editing VLAN ID Pool..')
        vlan_id_pool = DBSession.query(VLANIDPool).filter_by(id=vlan_id_pool_id).first()
        if vlan_id_pool:
            list_to_delete = []
            range_old = vlan_id_pool.range
            vlan_id_pool.name = name
            vlan_id_pool.description = desc
            vlan_id_pool.range = range
            DBSession.add(vlan_id_pool)
            interface = vlan_id_pool.interface
            self.attach_vlan_id_pool(sp_ids, vlan_id_pool)
            self.detach_vlan_id_pool(site_id, sp_ids, vlan_id_pool_id)
            nums_old = range_old.split('-')
            first_num_old = int(nums_old[0])
            last_num_old = int(nums_old[1])
            nums = range.split('-')
            first_num = int(nums[0])
            last_num = int(nums[1])
            if first_num < first_num_old:
                LOGGER.info('Range increased at start...')
                i = 0
                i = first_num
                while int(i) < int(first_num_old):
                    vlan_id = VLANID()
                    vlan_id.id = getHexID()
                    vlan_id.vlan_id = int(i)
                    vlan_id.vlan_id_pool_id = vlan_id_pool_id
                    vlan_id.used_by = None
                    DBSession.add(vlan_id)
                    i = int(i) + 1
                network_size = vlan_id_pool.num_hosts
                num_networks = int(first_num_old) - int(first_num)
                cidr = vlan_id_pool.cidr
                vlan_start = int(first_num)
                self.create_vlan_network_info(vlan_id_pool, cidr, num_networks, network_size, vlan_start, interface)
            else:
                if last_num > last_num_old:
                    LOGGER.info('Range increased at end...')
                    i = 0
                    i = int(last_num_old) + 1
                    while int(i) <= int(last_num):
                        vlan_id = VLANID()
                        vlan_id.id = getHexID()
                        vlan_id.vlan_id = int(i)
                        vlan_id.vlan_id_pool_id = vlan_id_pool_id
                        vlan_id.used_by = None
                        DBSession.add(vlan_id)
                        i = int(i) + 1
                    network_size = vlan_id_pool.num_hosts
                    num_networks = int(last_num) - int(last_num_old)
                    cidr = vlan_id_pool.cidr
                    vlan_start = int(last_num_old)
                    self.create_vlan_network_info(vlan_id_pool, cidr, num_networks, network_size, vlan_start, interface)
            if first_num > first_num_old:
                LOGGER.info('Range decreased at start...')
                i = 0
                i = first_num_old
                while int(i) < int(first_num):
                    list_to_delete.append(i)
                    i = int(i) + 1
            else:
                if last_num < last_num_old:
                    LOGGER.info('Range decreased at end...')
                    i = 0
                    i = int(last_num) + 1
                    while int(i) <= int(last_num_old):
                        list_to_delete.append(i)
                        i = int(i) + 1
            LOGGER.info('VLAN IDs to be deleted are ' + to_str(list_to_delete))
            if list_to_delete:
                DBSession.query(VLANID).filter(VLANID.vlan_id.in_(list_to_delete)).filter(VLANID.vlan_id_pool_id == vlan_id_pool_id).delete()
                self.delete_vlan_network_info(vlan_id_pool, list_to_delete)
                LOGGER.info('Out of range VLAN IDs are deleted')
            LOGGER.info('VLAN IDs are updated')
            transaction.commit()

    def get_vlan_id_pools(self):
        result = []
        rs = DBSession.query(VLANIDPool).join((VLANID, VLANID.vlan_id_pool_id == VLANIDPool.id)).outerjoin((VLANIDPoolSPRelation, VLANIDPoolSPRelation.vlan_id_pool_id == VLANIDPool.id), (ServerGroup, ServerGroup.id == VLANIDPoolSPRelation.sp_id))
        for pool in rs:
            rec_dic = {}
            if pool:
                rec_dic['id'] = pool.id
                rec_dic['name'] = pool.name
                rec_dic['description'] = pool.description
                rec_dic['range'] = pool.range
                rec_dic['interface'] = pool.interface
                rec_dic['cidr'] = pool.cidr
                rec_dic['num_hosts'] = pool.num_hosts
                rec_dic['used_by'] = ''
                sp_list = DBSession.query(ServerGroup).join((VLANIDPoolSPRelation, VLANIDPoolSPRelation.sp_id == ServerGroup.id)).join((VLANIDPool, VLANIDPool.id == VLANIDPoolSPRelation.vlan_id_pool_id)).filter(VLANIDPool.id == pool.id)
                sp_names = ''
                if sp_list:
                    for sp in sp_list:
                        if sp_names:
                            sp_names = sp_names + ', ' + to_str(sp.name)
                        sp_names = sp.name
                    rec_dic['used_by'] = sp_names
            result.append(rec_dic)
        return result

    def get_vlan_id_pool(self, vlan_id_pool_id):
        rec = DBSession.query(VLANIDPool).filter_by(id=vlan_id_pool_id).first()
        return rec

    def get_vlan_id_pool_details(self, vlan_id_pool_id):
        result = []
        rec = DBSession.query(VLANIDPool).filter_by(id=vlan_id_pool_id).first()
        rec_dic = {}
        if rec:
            rec_dic['id'] = rec.id
            rec_dic['name'] = rec.name
            rec_dic['description'] = rec.description
            rec_dic['range'] = rec.range
            rec_dic['interface'] = rec.interface
            rec_dic['used_by'] = ''
        result.append(rec_dic)
        return result

    def remove_vlan_id_pool(self, vlan_id_pool_id):
        LOGGER.info('Removing VLAN ID Pool..')
        DBSession.query(VLANIDPoolSPRelation).filter_by(vlan_id_pool_id=vlan_id_pool_id).delete()
        DBSession.query(VLANID).filter_by(vlan_id_pool_id=vlan_id_pool_id).delete()
        DBSession.query(VLANNetworkInfo).filter_by(vlan_pool_id=vlan_id_pool_id).delete()
        vlan_id_pool = DBSession.query(VLANIDPool).filter_by(id=vlan_id_pool_id).first()
        DBSession.delete(vlan_id_pool)
        transaction.commit()

    def get_common_vlan_id_pools_by_sp(self, auth, sp_ids):
        if not isinstance(sp_ids, list):
            sp_ids = [sp_ids]
        vlan_id_pools_result = []
        count = 1
        for sp_id in sp_ids:
            vlan_id_pools = DBSession.query(VLANIDPool).join((VLANID, VLANID.vlan_id_pool_id == VLANIDPool.id)).outerjoin((VLANIDPoolSPRelation, VLANIDPoolSPRelation.vlan_id_pool_id == VLANIDPool.id), (ServerGroup, ServerGroup.id == VLANIDPoolSPRelation.sp_id)).filter(ServerGroup.id == sp_id).all()
            if count == 1:
                vlan_id_pools_result = vlan_id_pools
            else:
                if len(vlan_id_pools_result):
                    vlan_id_pools_result = list(set(vlan_id_pools_result) & set(vlan_id_pools))
        count += 1
        return vlan_id_pools_result



class VLANNetworkInfo(DeclarativeBase):
    #__doc__ = '\n    '
    __tablename__ = 'vlan_network_info'
    id = Column(Unicode(50), primary_key=True)
    cidr = Column(Unicode(50))
    dhcp_start = Column(Unicode(50))
    dhcp_end = Column(Unicode(50))
    gateway = Column(Unicode(50))
    netmask = Column(Unicode(50))
    vlan_id = Column(Integer)
    vpn_private_address = Column(Unicode(50))
    broadcast = Column(Unicode(50))
    bridge = Column(Unicode(50))
    vlan_pool_id = Column(Unicode(50), ForeignKey('vlan_id_pools.id', ondelete='CASCADE'))
    vlan_pool = relation('VLANIDPool', backref='vlan_nws_infos')
    def __init__(self, cidr=None, dhcp_start=None, dhcp_end=None, gateway=None, netmask=None, vlan_id=None, vpn_private_address=None, broadcast=None, bridge=None):
        self.id = getHexID()
        self.cidr = cidr
        self.dhcp_start = dhcp_start
        self.dhcp_end = dhcp_end
        self.gateway = gateway
        self.netmask = netmask
        self.vlan_id = vlan_id
        self.vpn_private_address = vpn_private_address
        self.broadcast = broadcast
        self.bridge = bridge
    @classmethod
    def get_vlan_network_info_by_vlan_id(cls, vlan_id, pool_id):
        return DBSession.query(cls).filter(cls.vlan_pool_id == pool_id).filter(cls.vlan_id == vlan_id).first()
        
    def __str__(self):
        return '(%s, ID:%s, cidr:%s, vlan:%s)' % (self.__class__, self.id, self.cidr, self.vlan_id)



