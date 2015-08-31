import stackone.core.utils.utils
from stackone.core.utils.utils import getHexID
constants = stackone.core.utils.constants
from sqlalchemy import Column
from sqlalchemy.types import *
from sqlalchemy.schema import Index
from stackone.model import DeclarativeBase
class VDCStore(DeclarativeBase):
    __tablename__ = 'cloud_vdcstores'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(50), nullable=False)
    def __init__(self, name):
        self.name = name
        self.id = getHexID(name, [constants.VDC_FOLDER])



Index('vdcs_name', VDCStore.name)
