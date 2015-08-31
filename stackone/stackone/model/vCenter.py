import stackone.core.utils.utils
from sqlalchemy.types import *
from sqlalchemy import Column
from sqlalchemy.orm import relation
from sqlalchemy.schema import Index
from stackone.core.utils.utils import getHexID
from stackone.model.Credential import Credential
from stackone.model import DeclarativeBase
from stackone.model import DBSession
class VCenter(DeclarativeBase):
    __tablename__ = 'vcenter'
    id = Column(Unicode(50), primary_key=True)
    host = Column(Unicode(50), nullable=False)
    port = Column(Unicode(50), nullable=False)
    ssl = Column(Unicode(255), nullable=False)
    credential = relation(Credential, primaryjoin=id == Credential.entity_id, foreign_keys=[Credential.entity_id], uselist=False, cascade='all, delete, delete-orphan')
    def __init__(self, host, port, ssl, username, password):
        self.id = getHexID()
        self.port = port
        self.host = host
        self.ssl = ssl
        self.credential = Credential(self.id, u'', username=username, password=password)

    @classmethod
    def get_object_by_id(cls, id):
        return DBSession.query(cls).filter(cls.id == id).first()
    @classmethod
    def remove_by_id(cls, id):
        DBSession.query(Credential).filter(Credential.entity_id == id).delete()
        DBSession.query(VCenter).filter(VCenter.id == id).delete()



