from sqlalchemy.orm import mapper, relation
from sqlalchemy.schema import Index, Sequence
from sqlalchemy import Table, ForeignKey, Column, PickleType
from sqlalchemy.types import Integer, Unicode, Boolean, String
from stackone.core.utils.utils import constants, getHexID
from stackone.core.utils.utils import to_unicode, to_str
from stackone.model import DeclarativeBase, metadata, DBSession
from stackone.model.DBHelper import DBHelper
from stackone.model.Credential import Credential
class EmailSetup(DeclarativeBase):
    __tablename__ = 'emailsetup'
    id = Column(Unicode(50L), primary_key=True)
    mail_server = Column(Unicode(255L))
    description = Column(String(200L))
    port = Column(Integer)
    use_secure = Column(Integer)
    site_id = Column(Unicode(50L), ForeignKey('sites.id', ondelete='CASCADE'))
    credential = relation(Credential, primaryjoin=id == Credential.entity_id, foreign_keys=[Credential.entity_id], uselist=False, cascade='all, delete, delete-orphan')
    def __repr__(self):
        return '<EmailSetup: mail_server=%s>' % self.mail_server

    def __init__(self, mail_server, desc, port, use_secure, site_id, useremail, password):
        self.id = getHexID()
        self.mail_server = to_unicode(mail_server)
        self.description = desc
        self.port = port
        self.use_secure = use_secure
        self.site_id = site_id
        self.credential = Credential(self.id, u'', user_email=useremail, password=password)

    def getEmailSetupId(self):
        return self.id



