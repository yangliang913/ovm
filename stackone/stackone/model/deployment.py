from sqlalchemy import *
from sqlalchemy import Column
from sqlalchemy.types import Integer, Unicode, Float
from stackone.model import DeclarativeBase
class Deployment(DeclarativeBase):
    __tablename__ = 'deployment'
    deployment_id = Column(Unicode(50), primary_key=True)
    version = Column(Unicode(50))
    max_sp = Column(Integer, default=0)
    max_server = Column(Integer, default=0)
    max_vm = Column(Integer, default=0)
    max_tg = Column(Integer, default=0)
    max_template = Column(Integer, default=0)
    l_info = Column(PickleType)
    l_id = Column(Unicode(255))
    update_checked_date = Column(DateTime)
    cms_started = Column(DateTime)
    cms_deployed = Column(DateTime)
    cms_end = Column(DateTime)
    xen_server = Column(Integer, default=0)
    kvm_server = Column(Integer, default=0)
    vms = Column(Integer, default=0)
    users = Column(Integer, default=0)
    templates = Column(Integer, default=0)
    sps = Column(Integer, default=0)
    storages = Column(Integer, default=0)
    networks = Column(Integer, default=0)
    distro_name = Column(Unicode(50))
    distro_ver = Column(Unicode(50))
    tot_sockets = Column(Integer, default=0)
    tot_cores = Column(Integer, default=0)
    tot_mem = Column(Float)
    host_cores = Column(Integer, default=0)
    host_sockets = Column(Integer, default=0)
    host_mem = Column(Float)
    def __repr__(self):
        return '<deployment: id=%s>' % self.deployment_id