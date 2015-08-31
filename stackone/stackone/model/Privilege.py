from sqlalchemy import *
from datetime import datetime
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref
from sqlalchemy.schema import Index, Sequence
from stackone.model import DeclarativeBase, metadata, DBSession
from stackone.model.DBHelper import DBHelper
class Privilege(DeclarativeBase):
    __tablename__ = 'cprivileges'
    id = Column(Integer, Sequence('privid_seq'), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    created_by = Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by = Column(Unicode(255))
    modified_date = Column(DateTime, default=datetime.now)
    opGroups = relation('OperationGroup', backref='privilege')
    type = Column(Unicode(50))
    def __repr__(self):
        return '<Privilege: name=%s>' % self.name

    



Index('prvge_name', Privilege.name)
opgroups_privileges = Table('opgroups_privileges', metadata, Column('opgroup_id', Integer, ForeignKey('operation_groups.id', ondelete='CASCADE')), Column('privilege_id', Integer, ForeignKey(Privilege.id, ondelete='CASCADE')))
