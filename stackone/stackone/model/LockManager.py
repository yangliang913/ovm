from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, DateTime, Text
from datetime import datetime
from sqlalchemy.schema import Index, Sequence
from stackone.model import DeclarativeBase, metadata, DBSession
import traceback
import transaction
class CMS_Locks(DeclarativeBase):
    __tablename__ = 'cms_locks'
    id = Column(Integer, Sequence('cms_lock_id_seq'), primary_key=True)
    sub_system = Column(Unicode(50))
    entity_id = Column(Unicode(50))
    operation = Column(Unicode(50))
    table_name = Column(Unicode(50))
    def __init__(self, sub_system, entity_id, operation, table_name):
        self.sub_system = sub_system
        self.entity_id = entity_id
        self.operation = operation
        self.table_name = table_name



class LockManager():
    def get_lock(self, sub_system, entity_id, operation, table_name):
        lock_m = DBSession.query(CMS_Locks).with_lockmode('update').filter(CMS_Locks.sub_system == sub_system).filter(CMS_Locks.entity_id == entity_id).filter(CMS_Locks.operation == operation).filter(CMS_Locks.table_name == table_name).all()
        if len(lock_m) == 0:
            lm = CMS_Locks(sub_system, entity_id, operation, table_name)
            DBSession.add(lm)


    def release_lock(self):
        transaction.commit()



