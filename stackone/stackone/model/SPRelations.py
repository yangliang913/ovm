from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, String, Boolean, PickleType, Float, DateTime
from sqlalchemy.orm import relation, backref
from sqlalchemy.schema import Index, Sequence
from stackone.model import DeclarativeBase, metadata, DBSession
from stackone.model.Groups import ServerGroup
from stackone.model.Sites import Site
from stackone.model.ManagedNode import ManagedNode
from sqlalchemy.schema import UniqueConstraint, Index
from stackone.core.utils.utils import uuidToString, randomUUID, dynamic_map
class Upgrade_Data(DeclarativeBase):
    __tablename__ = 'upgrade_data'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50))
    version = Column(Unicode(50))
    description = Column(Unicode(100))
    upgraded = Column(Boolean)
    def __init__(self):
        pass



class Storage_Stats(DeclarativeBase):
    __tablename__ = 'storage_stats'
    id = Column(Unicode(50), primary_key=True)
    entity_id = Column(Unicode(50))
    storage_id = Column(Unicode(50), ForeignKey('storage_definitions.id'))
    total_size = Column(Float)
    used_size = Column(Float)
    available_size = Column(Float)
    allocation_in_DC = Column(Float)
    allocation_in_SP = Column(Float)
    storage_used_in_SP = Column(Float)
    storage_avail_in_SP = Column(Float)
    allocation_at_S_for_DC = Column(Float)
    allocation_at_S_for_SP = Column(Float)
    local_storage_at_VM = Column(Float)
    shared_storage_at_VM = Column(Float)
    storage_allocation_at_DC = Column(Float)
    locked = Column(Boolean)
    fk_sd_ss = relation('StorageDef', backref='Storage_Stats')
    def __init__(self):
        pass



Index('idx_ss_entid_sid', Storage_Stats.entity_id, Storage_Stats.storage_id)
class ServerDefLink(DeclarativeBase):
    __tablename__ = 'serverdeflinks'
    __table_args__ = (UniqueConstraint('server_id', 'def_id', name='ucServerDefLink'), {})
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    server_id = Column(Unicode(50), ForeignKey('managed_nodes.id'))
    def_type = Column(Unicode(50))
    def_id = Column(Unicode(50))
    status = Column(Unicode(50))
    details = Column(Unicode(1500))
    dt_time = Column(DateTime)
    transient_state = Column(Unicode(50))
    mng_node = relation('ManagedNode', backref='ServerDefLink')
    def __init__(self):
        pass



Index('sdef_sid_dtype_did', ServerDefLink.server_id, ServerDefLink.def_type, ServerDefLink.def_id)
class SPDefLink(DeclarativeBase):
    __tablename__ = 'spdeflinks'
    __table_args__ = (UniqueConstraint('group_id', 'def_id', name='ucSPDefLink'), {})
    id = Column(Integer, Sequence('spdef_id_seq'), primary_key=True)
    group_id = Column(Unicode(50), ForeignKey('server_groups.id'))
    def_type = Column(Unicode(50))
    def_id = Column(Unicode(50))
    status = Column(Unicode(50))
    oos_count = Column(Integer)
    dt_time = Column(DateTime)
    transient_state = Column(Unicode(50))
    svr_grp = relation('ServerGroup', backref='SPDefLink')
    def __init__(self):
        pass



Index('spdef_gid_dtype_did', SPDefLink.group_id, SPDefLink.def_type, SPDefLink.def_id)
class DCDefLink(DeclarativeBase):
    __tablename__ = 'dcdeflinks'
    __table_args__ = (UniqueConstraint('site_id', 'def_id', name='ucDCDefLink'), {})
    id = Column(Integer, Sequence('dcdef_id_seq'), primary_key=True)
    site_id = Column(Unicode(50), ForeignKey('sites.id'))
    def_type = Column(Unicode(50))
    def_id = Column(Unicode(50))
    status = Column(Unicode(50))
    oos_count = Column(Integer)
    dt_time = Column(DateTime)
    transient_state = Column(Unicode(50))
    site_grp = relation('Site', backref='DCDefLink')
    def __init__(self):
        pass



Index('dcdef_sid_dtype_did', DCDefLink.site_id, DCDefLink.def_type, DCDefLink.def_id)
class CSEPDefLink(DeclarativeBase):
    __tablename__ = 'csepdeflinks'
    __table_args__ = (UniqueConstraint('csep_id', 'def_id', name='ucCSEPDefLink'), {})
    id = Column(Integer, Sequence('dcdef_id_seq'), primary_key=True)
    csep_id = Column(Unicode(50))
    def_type = Column(Unicode(50))
    def_id = Column(Unicode(50))
    status = Column(Unicode(50))
    oos_count = Column(Integer)
    dt_time = Column(DateTime)
    transient_state = Column(Unicode(50))
    def __init__(self):
        pass



Index('csepdef_cid_dtype_did', CSEPDefLink.csep_id, CSEPDefLink.def_type, CSEPDefLink.def_id)
class StorageDisks(DeclarativeBase):
    __tablename__ = 'storage_disks'
    id = Column(Unicode(50), primary_key=True)
    storage_id = Column(Unicode(50), ForeignKey('storage_definitions.id'))
    storage_type = Column(Unicode(50))
    disk_name = Column(Unicode(100))
    mount_point = Column(Unicode(50))
    file_system = Column(Unicode(50))
    actual_size = Column(Float)
    size = Column('disk_size', Float)
    unique_path = Column(Unicode(255))
    current_portal = Column(Unicode(50))
    target = Column(Unicode(50))
    state = Column(Unicode(50))
    lun = Column(Integer)
    storage_allocated = Column(Boolean)
    added_manually = Column(Boolean)
    transient_reservation = Column(Unicode(50))
    fk_StorageDisks_StorageDef = relation('StorageDef', backref='StorageDisks')
    def __init__(self):
        pass



Index('sdisk_upath', StorageDisks.unique_path)
