# -*- coding: utf-8 -*-

"""Sample model module."""

from sqlalchemy import *
from datetime import datetime
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref
from sqlalchemy.schema import Index, Sequence
from stackone.core.ha.ha_register import HARegister
from stackone.model import DeclarativeBase, metadata
from stackone.model.DBHelper import DBHelper
from stackone.model import DBSession
from stackone.core.utils.utils import to_unicode, to_str
from stackone.model.Privilege import Privilege
from stackone.model.auth import User, Group, Role
import traceback
import logging
from stackone.core.utils.utils import getHexID
LOGGER = logging.getLogger('stackone.model')

ops_enttypes = Table('ops_enttypes', metadata, Column('op_id', Integer, ForeignKey('operations.id', ondelete='CASCADE')), Column('entity_type_id', Integer, ForeignKey('entity_types.id', ondelete='CASCADE')))
###
class EntityRelation(DeclarativeBase):
    __tablename__ = 'entity_relations'
    id = Column(Integer, Sequence('ent_rel_id_seq'), primary_key=True)
    src_id = Column(Unicode(50))
    dest_id = Column(Unicode(50))
    relation = Column(Unicode(50))
    ###
    def __init__(self, src_id, dest_id, relation):
        self.src_id = src_id
        self.dest_id = dest_id
        self.relation = relation
    ###
    def __repr__(self):
        return '<EntityRelation: name=%s>' % self.relation



Index('er_sid_did_reln', EntityRelation.src_id, EntityRelation.dest_id, EntityRelation.relation)
###
class Entity(DeclarativeBase):
    __tablename__ = 'entities'
    id = Column(Integer)
    name = Column(Unicode(255), nullable=False)
    created_by = Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by = Column(Unicode(255))
    modified_date = Column(DateTime, default=datetime.now)
    entity_id = Column(Unicode(50), primary_key=True)
    type_id = Column(Integer, ForeignKey('entity_types.id', ondelete='CASCADE'))
    context_id = Column(Unicode(50), primary_key=True, default=None, nullable=True)
    csep_context_id = Column(Unicode(255), primary_key=True, default=None, nullable=True)
    attributes = relation('EntityAttribute', backref='entity', cascade='all, delete, delete-orphan')
    ha = relation(HARegister, primaryjoin=entity_id == HARegister.entity_id, foreign_keys=[HARegister.entity_id], uselist=False, cascade='all, delete, delete-orphan')
    def get_external_manager_id(self):
        return DBSession.query(EntityAttribute).filter(EntityAttribute.entity_id == self.entity_id).filter(EntityAttribute.name == 'external_manager_id').first()
    def get_external_id(self):
        return DBSession.query(EntityAttribute).filter(EntityAttribute.entity_id == self.entity_id).filter(EntityAttribute.name == 'external_id').first()
    ###
    def _get_children(self):
        relns = DBSession.query(EntityRelation).filter(and_(EntityRelation.src_id == self.entity_id, EntityRelation.relation == u'Children')).all()
        rels=[x.dest_id for x in relns]
        return DBSession.query(Entity).filter(Entity.entity_id.in_(rels)).all()

    ###
    def _get_parents(self):
        relns = DBSession.query(EntityRelation).filter(and_(EntityRelation.dest_id == self.entity_id, EntityRelation.relation == u'Children')).all()
        rels=[x.src_id for x in relns]
        return DBSession.query(Entity).filter(Entity.entity_id.in_(rels)).all()

    children = property(_get_children)
    parents = property(_get_parents)
    ###
    def get_ha(self):
        return self.ha
    
    ###
    def set_ha(self, registered=False):
        if self.ha is None and registered == False:
            return None
        if self.ha is None:
            self.ha = HARegister(self.entity_id, True)
        else:
            if self.ha.registered == registered:
                return None
            self.ha.registered = registered

        for child in self.children:
            child.set_ha(registered)

        return None

    ###
    def ha_registered(self):
        if self.ha is not None:
            return self.ha.registered
        return False

    ###
    @classmethod
    def get_attribute_value(cls, entity_id, name, default):
        res = DBSession.query(EntityAttribute).filter(EntityAttribute.name == name).filter(EntityAttribute.entity_id == entity_id).first()
        if res:
            return res.value
        return default
    ###
    @classmethod
    def find_by_name(self, name, type_id):
        ents = DBSession.query(Entity).filter(Entity.name == name).filter(Entity.type_id==type_id).all()
        if len(ents)==1:
            return ents[0]
    ###    
    def __repr__(self):
        return '<Entity: name=%s>' % self.name
    ###
    @classmethod
    def getEntityName(self,Id):
        EntityName=''
        ent=DBSession.query(Entity).filter(Entity.entity_id==Id).first()
        if ent is not None:
            EntityName=ent.name
            return EntityName
        else:
            return EntityName

    ###
    @classmethod
    def get_hierarchy(cls,entity_id):
        result=[]
        try:
            entity=DBSession.query(cls).filter(cls.entity_id==entity_id).first()
            while entity is not None:
                result.append(entity.entity_id)
                if len(entity.parents)!=0:
                    entity=entity.parents[0]
                else:
                    break
        except Exception,ex:
            LOGGER.error(to_str(ex).replace("'",""))
            traceback.print_exc()
            raise ex
        return result

    ###
    @classmethod
    def get_users_groups(cls, entity_id):
        result = []
        try:
            filters = []
            filters.append(cls.entity_id == entity_id)
            filters.append(Privilege.id != None)
            result = DBSession.query(User,Group)\
            .join(User.groups).join(Group.role)\
            .join(Role.role_rep).join(Privilege).join(Entity)\
            .filter(Entity.entity_id == entity_id).filter(Privilege.id != None).all()
        except Exception,ex:
            LOGGER.error(to_str(ex).replace("'",''))
            traceback.print_exc(ex)
        return result
    
    ###
    @classmethod        
    def get_entities(cls,entity_ids):
        ents = None
        try:
            ents = DBSession.query(Entity).filter(Entity.entity_id.in_(entity_ids)).all()
        except Exception ,e:
            LOGGER.error(e)
        return ents
    ###
    @classmethod    
    def get_entity(cls, entity_id, type_id=None, context_id=None):
        ent = None
        try:
            qry =  DBSession.query(cls).filter(cls.entity_id == entity_id)
            if type_id:
                qry = qry.filter(cls.type_id == type_id)
            if context_id:
                qry = qry.filter(cls.context_id == context_id)
            ent = qry.first()
        except Exception,e:
            LOGGER.error(e)
        return ent
    @classmethod
    def get_entity_by_unique_keys(cls, name, entity_type, context_id):
        ent_type = DBSession.query(EntityType).filter(EntityType.name == entity_type).first()
        if ent_type:
            return DBSession.query(Entity).filter(Entity.name==name).filter(Entity.type_id == ent_type.id).filter(Entity.context_id == context_id).first()
        return None
entity_index = Index('ix_entities_name_type_context', Entity.name, Entity.type_id, Entity.context_id, unique=True)
###
class EntityType(DeclarativeBase):
    __tablename__ = 'entity_types'
    DATA_CENTER = 1
    IMAGE_STORE = 2
    SERVER_POOL = 3
    MANAGED_NODE = 4
    DOMAIN = 5
    IMAGE_GROUP = 6
    IMAGE = 7
    APPLIANCE = 8
    EMAIL = 9
    CLOUD_VM = 10
    CLOUD_TEMPLATE = 11
    CLOUD_OUT_OF_BOX_TEMPLATE = 12
    VDC_FOLDER = 13
    CLOUD_PROVIDER_FOLDER = 14
    CLOUD_PROVIDER = 15
    VDC = 16
    TMP_LIB = 17
    CLOUD_TMPGRP = 18
    CMS_SERVICE_POINT = 19
    VDC_VM_FOLDER = 20
    
    id = Column(Integer, Sequence('enttypid_seq'), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    display_name = Column(Unicode(255))
    created_by = Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by = Column(Unicode(255))
    modified_date = Column(DateTime, default=datetime.now)
    entities = relation('Entity', backref='type')
    ops = relation('Operation', secondary=ops_enttypes, backref='entityType')
    
    ###
    def __repr__(self):
        return '<EntityType: name=%s>' % self.name



Index('etype_name', EntityType.name)
###
class EntityAttribute(DeclarativeBase):
    __tablename__ = 'entity_attributes'
    id = Column(Integer, Sequence('id_seq'), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    value = Column(Unicode(255))
    entity_id = Column(Unicode(50), ForeignKey('entities.entity_id', ondelete='CASCADE'))
    
    ###
    def __init__(self, name, value):
        self.name = name
        self.value = value

    ###
    def __repr__(self):
        return '<EntityAttribute: name=%s>' % self.name

    ###
    @classmethod
    def add_entity_attribute(cls, ent_obj, key, value, entity_id=None):
        try:
            if entity_id:
                ent_obj = Entity.get_entity(entity_id)
            ent_atr = cls(key, value)
            ent_obj.attributes.append(ent_atr)
            DBSession.add(ent_atr)
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
            raise ex
    @classmethod
    def add_entity_attributes(cls, ent_obj, properties):
        try:
            for key,value in properties.items():
                cls.add_entity_attribute(ent_obj,key,value)
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
            raise ex        
###           
class EntityTasks(DeclarativeBase):
    __tablename__ = 'entity_tasks'
    worker = Column(Unicode(255), primary_key=True)
    entity_id = Column(Unicode(50), primary_key=True)
    worker_id = Column(Unicode(50))
    finished = Column(Boolean)
    start_time = Column(DateTime)
    estimated_time = Column(DateTime)
    end_time = Column(DateTime)
    last_ping_time = Column(DateTime)
    ###
    def __init__(self, worker, worker_id, entity_id, finished, start_time, estimated_time=None, last_ping_time=None):
        self.worker = worker
        self.worker_id = worker_id
        self.entity_id = entity_id
        self.finished = finished
        self.start_time = start_time
        self.estimated_time = estimated_time
        self.last_ping_time = last_ping_time
    ###
    def __repr__(self):
        return '<Entity=%s, task=%s, time=%s>' % (self.entity_id, self.worker_id, self.start_time)



###
class EntityContext(DeclarativeBase):
    __tablename__ = 'entity_context'
    ENTITY_CONTEXT = ['context1', 'context2', 'context3', 'context4', 'context5']
    id = Column(Unicode(50), primary_key=True)
    context1 = Column(Unicode(255), nullable=True)
    context2 = Column(Unicode(255), nullable=True)
    context3 = Column(Unicode(255), nullable=True)
    context4 = Column(Unicode(255), nullable=True)
    context5 = Column(Unicode(255), nullable=True)
    ###
    def __init__(self, context):
        self.id = getHexID()
        if not isinstance(context, dict):
            LOGGER.debug('Entity context should be a dictionary')
            raise Exception('Entity context should be a dictionary')

        for k,v in context.items():
            setattr(self, k, v)

    ###
    def __str__(self):
        return '(%s, context1:%s, context2:%s,context3:%s, context4:%s,context5:%s)' % (self.__class__, self.context1, self.context2, self.context3, self.context4, self.context5)

    ###
    @classmethod
    def get_entity_context(cls, context_dict):
        """
        query from 'entity_context' based on 'context_dict'.
        """
        ent_ctx = None
        try:
            if not isinstance(context_dict, dict):
                LOGGER.debug('Entity context should be a dictionary')
                raise Exception('Entity context should be a dictionary')
                
            qry = DBSession.query(cls)
            for k, v in context_dict.items():
                qry = qry.filter(getattr(cls, k) == v)
            ent_ctx = qry.first()
        except Exception as e:
            LOGGER.error(e)
            traceback.print_exc()
            raise e
        return ent_ctx
    
    ###
    @classmethod
    def remove_context(cls, context_id):
        try:
            DBSession.query(cls).filter(cls.id == context_id).delete()
        except Exception as e:
            LOGGER.error(e)
            traceback.print_exc()
            raise e

    ###
    @classmethod
    def get_entity_context_by_id(cls, context_id):
        return DBSession.query(cls).filter(cls.id == context_id).first()


