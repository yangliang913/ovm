import stackone.core.utils.utils
from stackone.core.utils.utils import getHexID
constants = stackone.core.utils.constants
from sqlalchemy import Column
from sqlalchemy.types import *
from sqlalchemy.schema import Index
from stackone.model import DeclarativeBase
class ApplianceCatalog(DeclarativeBase):
    __tablename__ = 'appliance_catalogs'
    id = Column(Unicode(50L), primary_key=True)
    name = Column(Unicode(50L), nullable=False)
    url = Column(Unicode(255L), nullable=False)
    def __init__(self, name):
        self.name = name
        self.id = getHexID(name, [constants.APPLIANCE_CATALOG])



class ApplianceFeed(DeclarativeBase):
    __tablename__ = 'appliance_feeds'
    id = Column(Unicode(50L), primary_key=True)
    provider_id = Column(Unicode(50L), nullable=False)
    provider_name = Column(Unicode(255L))
    feed_name = Column(Unicode(255L), nullable=False)
    provider_url = Column(Unicode(255L))
    provider_logo_url = Column(Unicode(255L))
    feed_url = Column(Unicode(255L), nullable=False)
    def __init__(self, provider_id):
        self.provider_id = provider_id
        self.id = getHexID(provider_id, [constants.APPLIANCE_FEED])



class Appliance(DeclarativeBase):
    __tablename__ = 'appliances'
    id = Column(Unicode(50L), primary_key=True)
    catalog_id = Column(Unicode(255L))
    provider_id = Column(Unicode(50L))
    title = Column(Unicode(255L))
    link_href = Column(Unicode(255L))
    download_href = Column(Unicode(255L))
    type = Column(Unicode(50L))
    description = Column(Text)
    short_description = Column(Text)
    popularity_score = Column(Unicode(5L))
    updated_date = Column(Unicode(50L))
    platform = Column(Unicode(50L))
    arch = Column(Unicode(50L))
    PAE = Column(Boolean, default=False)
    is_hvm = Column(Boolean, default=False)
    filename = Column(Unicode(255L))
    compression_type = Column(Unicode(50L))
    version = Column(Unicode(50L))
    archive = Column(Unicode(50L))
    size = Column('file_size', Integer)
    installed_size = Column(Integer)
    def __init__(self, title):
        self.title = title
        self.id = getHexID()



Index('app_prvdrid', Appliance.provider_id)
