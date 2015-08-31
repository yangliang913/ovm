import stackone.core.utils.utils
from stackone.core.utils.utils import getHexID
constants = stackone.core.utils.constants
from sqlalchemy import Column
from sqlalchemy.types import *
from sqlalchemy.schema import Index
from stackone.model import DeclarativeBase
from stackone.model import DBSession
class Site(DeclarativeBase):
    __tablename__ = 'sites'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50), nullable=False)
    type = Column(Unicode(50), default=None)
    __mapper_args__ = {'polymorphic_on': type}
    def __init__(self, name):
        self.name = name
        self.id = getHexID(name, [constants.DATA_CENTER])

    def get_platform(self):
        platform = self.type
        if platform:
            return platform
        return constants.GENERIC
    @classmethod
    def get_datacenter(cls, id):
        cd = None
        dc = DBSession.query(cls).filter(cls.id == id).first()
        return dc

Index('s_name', Site.name)
class VMWDatacenter(Site):
    __mapper_args__ = {'polymorphic_identity': u'vcenter'}
    def __init__(self, name):
        Site.__init__(self, name)
