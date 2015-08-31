from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref
from stackone.model import DeclarativeBase, metadata, DBSession
class RoleEntityOp(DeclarativeBase):
    __tablename__ = 'role_entity_ops'
    id = Column(Integer, primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id', onupdate='CASCADE', ondelete='CASCADE'))
    entity_id = Column(Unicode(50), ForeignKey('entities.entity_id', onupdate='CASCADE', ondelete='CASCADE'))
    op_id = Column(Integer, ForeignKey('operations.id', onupdate='CASCADE', ondelete='CASCADE'))
    role = relation('Role', backref='r_role')
    op = relation('Operation', backref='op_role')
    entity = relation('Entity', backref='ent_role')


