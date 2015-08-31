from sqlalchemy import *
from datetime import datetime
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, Boolean
from sqlalchemy.orm import relation, backref
from sqlalchemy.schema import Index, Sequence
from stackone.model import DeclarativeBase, metadata, DBSession
from stackone.model.DBHelper import DBHelper
from stackone.model.Privilege import Privilege
op_groups_table = Table('operation_opgroup', metadata, Column('op_id', Integer, ForeignKey('operations.id', ondelete='CASCADE')), Column('opgroup_id', Integer, ForeignKey('operation_groups.id', ondelete='CASCADE')))
class Operation(DeclarativeBase):
    __tablename__ = 'operations'
    id = Column(Integer, Sequence('operid_seq'), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    description = Column(Unicode(255))
    display_name = Column(Unicode(255))
    display_id = Column(Unicode(255))
    display = Column(Boolean, default=False)
    has_separator = Column(Boolean, default=False)
    display_seq = Column(Integer)
    icon = Column(Unicode(255))
    created_by = Column(Unicode(50), nullable=True)
    created_date = Column(DateTime)
    modified_by = Column(Unicode(50), nullable=True)
    modified_date = Column(DateTime, default=datetime.now)
    def __repr__(self):
        return '<Operation: name=%s>' % self.name

    def __eq__(self, obj):
        if obj:
            if self.id == obj.id:
                return True
        return False


    def __ne__(self, obj):
        if obj:
            if self.id == obj.id:
                return False

        return True




Index('op_name', Operation.name)
class OperationGroup(DeclarativeBase):
    __tablename__ = 'operation_groups'
    id = Column(Integer, Sequence('opgrpssid_seq'), primary_key=True)
    name = Column(Unicode(255), nullable=False, unique=True)
    description = Column(Unicode(255))
    created_by = Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by = Column(Unicode(255))
    modified_date = Column(DateTime, default=datetime.now)
    operations = relation('Operation', secondary=op_groups_table, backref='opsGroup')
    privilege_id = Column(Integer, ForeignKey(Privilege.id, ondelete='CASCADE'))
    def __repr__(self):
        return '<OperationGroup: name=%s>' % self.name



