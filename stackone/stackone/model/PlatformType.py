from sqlalchemy import *
from sqlalchemy.types import Integer, Unicode
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.orm import relation, backref
from stackone.model import DeclarativeBase, metadata
from stackone.core.utils.utils import getHexID
from stackone.model import DBSession
import stackone.core.utils.constants as constants
ops_plateforms_table = Table('platformtype_ops', metadata, Column('op_id', Integer, ForeignKey('operations.id', ondelete='CASCADE')), Column('platform_type_id', Unicode(50), ForeignKey('platform_type.id', ondelete='CASCADE')))

class PlatformType(DeclarativeBase):
    __tablename__ = 'platform_type'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50), nullable=False)
    display = Column(Unicode(255), nullable=False)
    desc = Column(Unicode(255))
    operations = relation('Operation', secondary=ops_plateforms_table, backref='platformType')
    def __init__(self, platform_type, display, desc=None):
        self.id = getHexID()
        self.name = platform_type
        self.display = display
        self.desc = desc

    @classmethod
    def filter_ops(cls, platform_type, ops):
        ptf = DBSession.query(cls).filter(cls.name == platform_type).first()
        if ptf:
            common_ops = list(set(ptf.operations) & set(ops))
            if common_ops:
                return sorted(common_ops, key=(lambda x: x.display_seq))
            if common_ops == [] and platform_type == constants.VCENTER:
                return []
        return ops


