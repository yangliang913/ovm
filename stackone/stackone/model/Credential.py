from stackone.core.utils.utils import getHexID
from sqlalchemy import Column, ForeignKey, PickleType
from sqlalchemy.types import *
from sqlalchemy.schema import Index
from stackone.model import DeclarativeBase
class Credential(DeclarativeBase):
    __tablename__ = 'credentials'
    id = Column(Unicode(50), primary_key=True)
    entity_id = Column(Unicode(50))
    cred_type = Column(Unicode(50))
    cred_details = Column(PickleType)
    def __init__(self, entity_id, type, **kwargs):
        self.id = getHexID()
        self.entity_id = entity_id
        self.cred_type = type
        self.cred_details = kwargs



Index('cred_eid', Credential.entity_id)
