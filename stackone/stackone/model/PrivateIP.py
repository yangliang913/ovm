from sqlalchemy import func, outerjoin, join
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String, Boolean, PickleType, Float, DateTime
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.orm import relation, backref
from stackone.model import DeclarativeBase
from stackone.model.Groups import ServerGroup
from stackone.model.network import NwDef
from stackone.model.IP import IPPool
import logging
LOGGER = logging.getLogger('stackone.model')
class PrivateIPPoolSPRelation(DeclarativeBase):
    __tablename__ = 'private_ip_pool_sp_relation'
    id = Column(Unicode(50), primary_key=True)
    private_ip_pool_id = Column(Unicode(50), ForeignKey('ip_pool.id', ondelete='CASCADE'))
    sp_id = Column(Unicode(50), ForeignKey('server_groups.id', ondelete='CASCADE'))
    fk_ip_pipsr = relation('IPPool', backref='private_ip_pool_sp_relation')
    fk_sg_pipsr = relation('ServerGroup', backref='private_ip_pool_sp_relation')
    def __init__(self):
        pass



class DHCPServer(DeclarativeBase):
    __tablename__ = 'nw_service_node'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50))
    description = Column(Unicode(50))
    ip_address = Column(Unicode(50))
    user_name = Column(Unicode(50))
    password = Column(Unicode(50))
    server_id = Column(Unicode(50))
    def __init__(self):
        pass



class NetworkServiceHostNetworkRelation(DeclarativeBase):
    __tablename__ = 'nw_service_host_nw_relations'
    id = Column(Unicode(50), primary_key=True)
    nw_service_host_id = Column(Unicode(50))
    nw_def_id = Column(Unicode(50), ForeignKey('network_definitions.id', ondelete='CASCADE'))
    pid = Column(Unicode(50))
    dns_status = Column(Unicode(50))
    pid_file = Column(Unicode(50))
    conf_file = Column(Unicode(50))
    sync_state = Column(Unicode(50))
    sync_error = Column(Unicode(500))
    fk_nwdef_nwrel_ = relation('NwDef', backref='network_service_host_relation')
    def __init__(self):
        pass



class PrivateIPManager():
    def __init__(self):
        pass



