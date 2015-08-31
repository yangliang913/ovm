from sqlalchemy import *
from datetime import datetime
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode
from sqlalchemy.orm import relation, backref
from sqlalchemy.schema import Index, Sequence
from stackone.model.Privilege import Privilege
from stackone.model import DeclarativeBase, metadata, DBSession
class RoleEntityPrivilege(DeclarativeBase):
    __tablename__ = 'role_entity_privileges'
    id = Column(Integer, Sequence('cmsrepid_seq'), primary_key=True)
    role_id = Column(Integer, ForeignKey('roles.id'))
    entity_id = Column(Unicode(50), ForeignKey('entities.entity_id'))
    privilege_id = Column(Integer, ForeignKey(Privilege.id))
    propagate = Column(Boolean, default=True)
    created_by = Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by = Column(Unicode(255))
    modified_date = Column(DateTime, default=datetime.now)
    role = relation('Role', backref='role_rep')
    privilege = relation('Privilege', backref='priv_rep')
    entity = relation('Entity', backref='ent_rep')
    def __repr__(self):
        return '<Entity=%s,Priv=%s,Role=%s>' % (self.entity.name, self.privilege.name, self.role.name)



Index('rep_rid_eid_pid', RoleEntityPrivilege.role_id, RoleEntityPrivilege.entity_id, RoleEntityPrivilege.privilege_id)
