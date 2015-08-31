import os
from datetime import datetime
import sys
try:
    from hashlib import sha1
except ImportError:
    sys.exit('ImportError: No module named hashlib\nIf you are on python2.4 this library is not part of python. Please install it. Example: easy_install hashlib')
from sqlalchemy import Table, ForeignKey, Column
from sqlalchemy.types import Unicode, Integer, DateTime, String, Boolean
from sqlalchemy.orm import relation, synonym
from sqlalchemy.schema import Index, Sequence
from stackone.model import DeclarativeBase, metadata, DBSession
from stackone.model.DBHelper import DBHelper
import stackone.core.utils.constants
constants = stackone.core.utils.constants

__all__ = ['User', 'Group', 'Permission']
group_permission_table = Table('group_permission', metadata,
                                Column('group_id', Integer, ForeignKey('groups.group_id', ondelete='CASCADE')),
                                 Column('permission_id', Integer, ForeignKey('permissions.permission_id', ondelete='CASCADE')))
user_group_table = Table('user_group', metadata,
                          Column('user_id', Integer, ForeignKey('users.user_id', ondelete='CASCADE')),
                          Column('group_id', Integer, ForeignKey('groups.group_id', ondelete='CASCADE')))



#group_permission_table = Table('group_permission', metadata,
#    Column('group_id', Integer, ForeignKey('groups.group_id',
#        onupdate="CASCADE", ondelete="CASCADE")),
#    Column('permission_id', Integer, ForeignKey('permissions.permission_id',
#        onupdate="CASCADE", ondelete="CASCADE"))
#)
#user_group_table = Table('user_group', metadata,
#    Column('user_id', Integer, ForeignKey('users.user_id',
#        onupdate="CASCADE", ondelete="CASCADE")),
#    Column('group_id', Integer, ForeignKey('groups.group_id',
#        onupdate="CASCADE", ondelete="CASCADE"))
#)

class User(DeclarativeBase):
    __tablename__ = 'users'

    user_id = Column(Integer, autoincrement=True, primary_key=True)
    firstname=Column(Unicode(50),nullable=False)
    lastname=Column(Unicode(50),nullable=False)
    phone_number=Column(Unicode(20))
    status=Column(Boolean,default=True)
    user_name = Column(Unicode(255), unique=True, nullable=False)
    email_address = Column(Unicode(255), unique=True, nullable=False,
                           info={'rum': {'field':'Email'}})
    display_name = Column(Unicode(255))
    _password = Column('password', Unicode(80),
                       info={'rum': {'field':'Password'}})
    created_by=Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by=Column(Unicode(255))
    modified_date= Column(DateTime,default=datetime.now)
#    gourps = relation('Group', secondary=user_group_table, backref='groups')
#    permissions = relation('Permission', secondary=group_permission_table,backref='groups')
    status = Column(Boolean, default=True)
    type = Column(Unicode(50))
    def __repr__(self):
        return '<User: email="%s", display name="%s">' % (self.email_address, self.display_name)

    def __unicode__(self):
        return self.display_name or self.user_name
    def get_roles(self):
        roles = DBHelper().filterby(Role, [Role.groups], [Group.users.contains(self)])
        return roles
    def has_cloudadmin_role(self):
        roles = self.get_roles()
        for role in roles:
            if role.is_cloud_admin:
                return True
        return False
    def has_role(self, role):
        roles = DBHelper().filterby(Role, [Role.groups], [Group.users.contains(self), Role.id == role.id])
        if len(roles) == 0:
            return False
        return True
    def is_cloud(self):
        if self.type == constants.CLOUD:
            return True
        return False

    @property
    def permissions(self):
        """Return a set of strings for the permissions granted."""
        perms = set()
        for g in self.groups:
            perms = perms | set(g.permissions)
        return perms

    @classmethod
    def by_email_address(cls, email):
        """Return the user object whose email address is ``email``."""
        return DBSession.query(cls).filter(cls.email_address==email).first()

    @classmethod
    def by_user_name(cls, username):
        """Return the user object whose user name is ``username``."""
        return DBSession.query(cls).filter(cls.user_name==username).first()

    def _set_password(self, password):
        """Hash ``password`` on the fly and store its hashed version."""
        hashed_password = password
        
        if isinstance(password, unicode):
            password_8bit = password.encode('UTF-8')
        else:
            password_8bit = password

        salt = sha1()
        salt.update(os.urandom(60))
        hash = sha1()
        hash.update(password_8bit + salt.hexdigest())
        hashed_password = salt.hexdigest() + hash.hexdigest()

        if not isinstance(hashed_password, unicode):
            hashed_password = hashed_password.decode('UTF-8')

        self._password = hashed_password

    def _get_password(self):
        """Return the hashed version of the password."""
        return self._password

    password = synonym('_password', descriptor=property(_get_password,_set_password))
    def validate_password(self, password):
        hashed_pass = sha1()
        hashed_pass.update(password + self.password[:40])
        return self.password[40:] == hashed_pass.hexdigest()    

    def has_group(self,grp):
        for g in self.groups:
            if g.group_name==grp.group_name:
                return True
        return False


  
Index('usr_uname',User.user_name)
class Group(DeclarativeBase):
    __tablename__ = 'groups'
    group_id = Column(Integer, autoincrement=True, primary_key=True)
    group_name = Column(Unicode(255), unique=True, nullable=False)
    display_name = Column(Unicode(255))
    created_by=Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by=Column(Unicode(255))
    modified_date= Column(DateTime,default=datetime.now)
    description=Column(Unicode(50))
    type = Column(Unicode(50))
    users = relation('User', secondary=user_group_table, backref='groups')
    role_id = Column(Integer, ForeignKey('roles.id', ondelete='CASCADE'))   

    @classmethod
    def by_group_name(cls, group_name):
        """Return the group object whose group_name is ``group_name``."""
        return DBSession.query(cls).filter(cls.group_name==group_name).first()

    def __repr__(self):
        return '<Group: name=%s>' % self.group_name
    
    def __unicode__(self):
        return self.group_name
    
    @classmethod
    def by_group_names(cls, group_names):
        return DBSession.query(cls).filter(cls.group_name.in_(group_names)).all()
Index('grp_name',Group.group_name)
# The 'info' argument we're passing to the email_address and password columns
# contain metadata that Rum (http://python-rum.org/) can use generate an
# admin interface for your models.


class Permission(DeclarativeBase):
    
    __tablename__ = 'permissions'
    permission_id = Column(Integer, autoincrement=True, primary_key=True)
    permission_name = Column(Unicode(16), unique=True, nullable=False)
    description = Column(Unicode(255))
    groups = relation(Group, secondary=group_permission_table,
                      backref='permissions')
    
    def __repr__(self):
        return '<Permission: name=%s>' % self.permission_name

    def __unicode__(self):
        return self.permission_name
    
class Role(DeclarativeBase):
    __tablename__ = 'roles'
    id = Column(Integer, Sequence('rolesid_seq'), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    description = Column(Unicode(255))
    created_by = Column(Unicode(255))
    created_date = Column(DateTime)
    modified_by = Column(Unicode(255))
    modified_date = Column(DateTime, default=datetime.now)
    groups = relation('Group', backref='role')
    type = Column(Unicode(50))
    is_cloud_admin = Column(Boolean)
    def __repr__(self):
        return '<Role: name=%s>' % self.name



Index('role_name', Role.name)

