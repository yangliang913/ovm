from sqlalchemy import *
from sqlalchemy.orm import mapper, relation
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Integer, Unicode, Boolean, DateTime, Text
from datetime import datetime
from sqlalchemy.schema import Index, Sequence
from stackone.model import DeclarativeBase, metadata, DBSession
class HARegister(DeclarativeBase):
    NOT_ACTIVE = 0
    DOWN_CONFIRMATION = 1
    STONITH = 2
    FAIL_OVER = 3
    POST_FAILOVER = 4
    FAILOVER_COMPLETE = 5
    __tablename__ = 'ha_registration'
    entity_id = Column(Unicode(50), primary_key=True)
    registered = Column(Boolean)
    ha_state = Column(Integer, default=NOT_ACTIVE)
    description = Column(Unicode(255))
    def __init__(self, entity_id, registered=True, description=None):
        self.entity_id = entity_id
        self.registered = registered
        self.description = description

    def register(self):
        self.registered = True

    def unregister(self):
        self.registered = False

    def set_ha_state(self, ha_state):
        self.ha_state = ha_state

    def get_ha_state(self):
        return self.ha_state

    def set_description(self, description=None):
        self.description = description

    def get_description(self):
        return self.description



class HAHistory(DeclarativeBase):
    __tablename__ = 'ha_history'
    entity_id = Column(Unicode(50), primary_key=True)
    ha_state = Column(Integer, primary_key=True, autoincrement=False)
    timestamp = Column(DateTime, primary_key=True)
    description = Column(Unicode(255))
    def __init__(self, entity_id, ha_state, description=None):
        self.entity_id = entity_id
        self.ha_state = ha_state
        self.description = description
        self.timestamp = datetime.now()



class HAEvent(DeclarativeBase):
    __tablename__ = 'ha_events'
    IDLE = 0
    STARTED = 1
    FAILED = 2
    SUCCEEDED = 3
    PARTIAL_SUCCESS = 4
    FAILURE = 'Failure'
    SUCCESS = 'Success'
    PARTIAL = 'Partial Success'
    event_id = Column(Integer, Sequence('event_id_seq'), primary_key=True)
    entity_id = Column(Unicode(256))
    sp_id = Column(Unicode(256))
    avail_state = Column(Integer)
    status = Column(Integer)
    event_time = Column(DateTime)
    timestamp = Column(DateTime)
    def __init__(self, entity_id, sp_id, avail_state, event_time):
        self.entity_id = entity_id
        self.sp_id = sp_id
        self.avail_state = avail_state
        self.event_time = event_time
        self.timestamp = datetime.now()
        self.status = self.IDLE

    def mark_started(self,task_id):
        self.status = self.STARTED
        self.task_id = task_id

    def mark_finished(self, status):
        if status == self.FAILURE:
            self.status = self.FAILED
        else:
            if status == self.SUCCESS:
                self.status = self.SUCCEEDED
            else:
                if status == self.PARTIAL:
                    self.status = self.PARTIAL_SUCCESS



Index('hae_spid_st', HAEvent.sp_id, HAEvent.status)
class HAEventLog(DeclarativeBase):
    __tablename__ = 'ha_event_log'
    id = Column(Integer, Sequence('ha_event_id_seq'), primary_key=True)
    event_id = Column(Integer)
    entity_id = Column(Unicode(256))
    timestamp = Column(DateTime)
    msg = Column(Text)
    def __init__(self, event_id, entity_id, msg):
        self.event_id = event_id
        self.entity_id = entity_id
        self.msg = msg
        self.timestamp = datetime.now()



class HAStatus(DeclarativeBase):
    __tablename__ = 'ha_status'
    event_id = Column(Integer, primary_key=True, autoincrement=False)
    entity_id = Column(Unicode(255), primary_key=True)
    task_id = Column(Integer, primary_key=True, autoincrement=False)
    task_status = Column(Integer)
    sp_id = Column(Unicode(255))
    action = Column(Unicode(255))
    step_number = Column(Integer)
    failover_status = Column(Integer)
    timestamp = Column(DateTime)
    msg = Column(Text)
    execution_context = Column(PickleType)
    def __init__(self, sp_id, event_id, entity_id, task_id, task_status):
        self.sp_id = sp_id
        self.event_id = event_id
        self.entity_id = entity_id
        self.task_status = task_status
        self.task_id = task_id
        self.timestamp = datetime.now()



if __name__ == '__main__':
    print 'Hello'
