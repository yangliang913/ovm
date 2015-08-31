from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, Boolean, DateTime
from datetime import datetime
from sqlalchemy.orm import relation, backref
from sqlalchemy.schema import Index, Sequence
from stackone.model import DeclarativeBase, metadata, DBSession
class HAFenceResourceType(DeclarativeBase):
    __tablename__ = 'ha_fence_resource_types'
    id = Column(Integer, Sequence('ha_fence_id_seq'), primary_key=True)
    name = Column(Unicode(50))
    display_name = Column(Unicode(255))
    fence_method = Column(Unicode(50))
    script_location = Column(Unicode(255))
    meta_source = Column(Unicode(255))
    classification = Column(Unicode(255))
    description = Column(Unicode(255))
    resources = relation('HAFenceResource', backref='type')
    meta = relation('HAFenceResourceTypeMeta', backref='resource_type')
    def __init__(self, name, display_name, fence_method, script_location, src, classification=None, description=None):
        self.name = name
        self.display_name = display_name
        self.fence_method = fence_method
        self.script_location = script_location
        self.meta_source = src
        self.classification = classification
        self.description = description



class HAFenceResourceTypeMeta(DeclarativeBase):
    __tablename__ = 'ha_fence_resource_type_meta'
    id = Column(Integer, Sequence('ha_meta_id_seq'), primary_key=True)
    fence_id = Column(Integer, ForeignKey(HAFenceResourceType.id, ondelete='CASCADE'))
    sequence = Column(Integer)
    field = Column(Unicode(50))
    type = Column(Unicode(50))
    display_name = Column(Unicode(255))
    is_resource = Column(Boolean, default=False)
    is_instance = Column(Boolean, default=False)
    is_environ = Column(Boolean, default=False)
    field_type = Column(Unicode(50))
    field_datatype = Column(Unicode(50))
    field_values = Column(Text)
    def __init__(self, field, display_name, field_type, field_datatype, type=None, sequence=None, values=None):
        self.field = field
        self.display_name = display_name
        self.field_type = field_type
        self.field_datatype = field_datatype
        self.type = type
        self.sequence = sequence
        self.field_values = values



class HAFenceResource(DeclarativeBase):
    __tablename__ = 'ha_fence_resources'
    id = Column(Integer, Sequence('ha_fe_re_id_seq'), primary_key=True)
    name = Column(Unicode(50))
    fence_id = Column(Integer, ForeignKey('ha_fence_resource_types.id', ondelete='CASCADE'))
    entity_resources = relation('HAEntityResource', backref='resource')
    params = relation('HAFenceResourceParam', backref='resource', cascade='all, delete, delete-orphan')
    def __init__(self, name, fence_id):
        self.name = name
        self.fence_id = fence_id



class HAFenceResourceParam(DeclarativeBase):
    __tablename__ = 'ha_fence_resource_params'
    id = Column(Integer, Sequence('ha__param_id_seq'), primary_key=True)
    resource_id = Column(Integer, ForeignKey(HAFenceResource.id, ondelete='CASCADE'))
    name = Column(Unicode(255))
    value = Column(Unicode(255))
    type = Column(Unicode(50))
    field = Column(Unicode(50))
    field_datatype = Column(Unicode(50))
    sequence = Column(Integer)
    def __init__(self, name, value=None, type=None, field=None, field_datatype=None, sequence=None):
        self.name = name
        self.value = value
        self.type = type
        self.field = field
        self.field_datatype = field_datatype
        self.sequence = sequence



class HAEntityResource(DeclarativeBase):
    __tablename__ = 'ha_entity_resources'
    id = Column(Integer, Sequence('ha_ent_resource_id_seq'), primary_key=True)
    entity_id = Column(Unicode(50))
    order = Column(Integer)
    resource_id = Column(Integer, ForeignKey('ha_fence_resources.id', ondelete='CASCADE'))
    params = relation('HAEntityResourceParam', backref='entity_resource', cascade='all, delete, delete-orphan')
    def __init__(self, entity_id, resource_id, order):
        self.entity_id = entity_id
        self.resource_id = resource_id
        self.order = order



class HAEntityResourceParam(DeclarativeBase):
    __tablename__ = 'ha_entity_resource_params'
    id = Column(Integer, Sequence('ha_ent_resource_id_seq'), primary_key=True)
    entity_resource_id = Column(Integer, ForeignKey(HAEntityResource.id, ondelete='CASCADE'))
    name = Column(Unicode(255))
    value = Column(Unicode(255))
    type = Column(Unicode(50))
    field = Column(Unicode(50))
    field_datatype = Column(Unicode(50))
    is_environ = Column(Boolean, default=False)
    sequence = Column(Integer)
    def __init__(self, name, value=None, type=None, field=None, field_datatype=None, sequence=None, is_environ=None):
        self.name = name
        self.value = value
        self.type = type
        self.field = field
        self.field_datatype = field_datatype
        self.is_environ = is_environ
        self.sequence = sequence



if __name__ == '__main__':
    print 'Hello'
