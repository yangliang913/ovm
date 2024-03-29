import stackone.core.utils.utils
from stackone.core.utils.utils import getHexID, uuidToString, randomUUID
constants = stackone.core.utils.constants
from sqlalchemy.orm import relation
from sqlalchemy import Column, ForeignKey
from sqlalchemy.types import *
from sqlalchemy.schema import Index
from stackone.model import DeclarativeBase
class Category(DeclarativeBase):
    __tablename__ = 'nodeinfo_categories'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50), nullable=False)
    display_name = Column(Unicode(50), nullable=False)
    components = relation('Component', backref='category')
    def __init__(self, name):
        self.name = name
        self.id = getHexID(name, [constants.NODEINFO_CATEGORY])



Index('ctgry_name', Category.name)
class Component(DeclarativeBase):
    __tablename__ = 'nodeinfo_components'
    id = Column(Unicode(50), primary_key=True)
    type = Column(Unicode(50), nullable=False)
    display_name = Column(Unicode(50), nullable=False)
    category_id = Column(Unicode(50), ForeignKey('nodeinfo_categories.id'))
    instances = relation('Instance', backref='component')
    def __init__(self, type):
        self.type = type
        self.id = getHexID(type, [constants.NODEINFO_COMPONENT])

    def __repr__(self):
        return self.display_name



Index('cmpnt_type', Component.type)
class Instance(DeclarativeBase):
    __tablename__ = 'nodeinfo_instances'
    id = Column(Unicode(50), primary_key=True)
    node_id = Column(Unicode(50), ForeignKey('managed_nodes.id'))
    component_id = Column(Unicode(50), ForeignKey('nodeinfo_components.id'))
    name = Column(Unicode(50), nullable=False)
    display_name = Column(Unicode(50), nullable=True)
    value = Column(Text)
    def __init__(self, name):
        self.name = name
        self.id = getHexID()

    def __repr__(self):
        return self.name



Index('instnce_nid_name', Instance.node_id, Instance.name)
