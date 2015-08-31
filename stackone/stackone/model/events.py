# -*- coding: utf-8 -*-

from stackone.model import DeclarativeBase
from sqlalchemy import Column, Integer, String, Table
from sqlalchemy import DateTime, PickleType, Boolean, Unicode
import logging
from sqlalchemy.schema import Index, Sequence
logger = logging.getLogger('stackone.availability.model')
ImmutablePickleType = PickleType(False)

###
class Subscriber(DeclarativeBase):
    __tablename__ = 'subscribers'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(128))
    event_type = Column(Unicode(32))
    cls = Column(ImmutablePickleType)

    ###
    def __init__(self, name, event_type, cls):
        self.name = name
        self.event_type = event_type
        self.cls = cls

    ###
    def __repr__(self):
        return 'Subscriber %s is listed for event type %s' % (self.name, self.event_type)


###
class Event(DeclarativeBase):
    __tablename__ = 'events'
    event_id = Column(Integer, Sequence('eventid_seq'), primary_key=True)
    entity_id = Column(Unicode(256))
    event_type = Column(Unicode(32), default='Generic')
    timestamp = Column(DateTime)
    contents = Column(ImmutablePickleType)
    
    __mapper_args__ = {'polymorphic_on': event_type}

    ###
    def __init__(self, entity_id, contents, timestamp=None):
        self.entity_id = entity_id
        if timestamp is None:
            timestamp = datetime.now()
        self.timestamp = timestamp
        self.contents = contents
        return None
    ###
    def __repr__(self):
        return 'Event type %s on entity %s raised on %s' % (self.event_type, self.entity_id, self.timestamp)

    ###
    def get(self, param):
        if self.contents is not None:
            return self.contents[param]



