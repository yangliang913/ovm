from stackone.core.utils.utils import getHexID
from sqlalchemy import Column, ForeignKey, DateTime, Text, Boolean, Unicode
from sqlalchemy.types import *
from sqlalchemy.schema import Index
from tg import session
from stackone.model import DeclarativeBase
from sqlalchemy.schema import Index, Sequence
class Notification(DeclarativeBase):
    __tablename__ = 'notification'
    id = Column(Integer, Sequence('notifyid_seq'), primary_key=True)
    task_id = Column(Unicode(50))
    task_name = Column(Unicode(255))
    user_name = Column(Unicode(255))
    mail_status = Column(Boolean, default=False)
    emailId = Column(Unicode(255), nullable=False)
    error_time = Column(DateTime)
    error_msg = Column(Text)
    subject = Column(Unicode(255))
    def __init__(self, task_id, task_name, timestamp, error_msg, user, email, subject=None):
        self.task_id = task_id
        self.task_name = task_name
        self.user_name = user
        self.emailId = email
        self.error_time = timestamp
        self.error_msg = error_msg
        self.subject = subject

    def __repr__(self):
        return '<Notification with id %s and timestamp %s returned %s>' % (self.id, self.error_time, self.mail_status)



#Index('nc_ms', Notification.mail_status)
