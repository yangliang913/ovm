from zope.sqlalchemy import ZopeTransactionExtension
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.ext.declarative import declarative_base
maker = sessionmaker(autoflush=True, autocommit=False, expire_on_commit=False, extension=ZopeTransactionExtension())
zopelessmaker = sessionmaker(autoflush=True, autocommit=False, expire_on_commit=False)
DBSession = scoped_session(maker)
DeclarativeBase = declarative_base()
metadata = DeclarativeBase.metadata
def init_model(engine):
	DBSession.configure(bind=engine)
	zopelessmaker.configure(bind=engine)

from stackone.model.auth import User, Group, Permission, Role
from stackone.model.Entity import EntityRelation, Entity, EntityType, EntityAttribute, entity_index
from stackone.model.Credential import Credential
from stackone.model.Operation import Operation, OperationGroup
from stackone.model.Privilege import Privilege
from stackone.model.RoleEntityPrivilege import RoleEntityPrivilege
from stackone.model.ImageStore import ImageStore, Image, ImageGroup
from stackone.model.Groups import ServerGroup, VMWServerGroup
from stackone.model.Sites import Site, VMWDatacenter
from stackone.model.ManagedNode import ManagedNode
from stackone.model.NetworkServiceNode import NetworkServiceNode, CMSNetworkServiceNode
from stackone.config.ConfigSettings import NodeConfiguration
from stackone.model.VM import VM
from stackone.core.ha.ha_register import *
from stackone.core.ha.ha_fence import *
#from stackone.model.VDCStores import VDCStore
# from stackone.core.platforms.xen.XenNode import XenNode
# from stackone.core.platforms.xen.XenDomain import XenDomain
from stackone.core.platforms.kvm.KVMNode import KVMNode
from stackone.core.platforms.kvm.KVMDomain import KVMDomain
from stackone.core.platforms.vmw.VMWNode import VMWNode
from stackone.core.platforms.vmw.VMWDomain import VMWDomain
from stackone.model.Appliance import ApplianceCatalog, ApplianceFeed, Appliance
from stackone.model.NodeInformation import Category, Component, Instance
from stackone.model.deployment import Deployment
from stackone.model.services import *
from stackone.model.events import *
from stackone.model.availability import *
from stackone.model.Metrics import Metrics, MetricsCurr, MetricsArch, rollupStatus
from stackone.model.SPRelations import ServerDefLink, SPDefLink, DCDefLink, Storage_Stats
from stackone.model.storage import StorageDef
from stackone.model.network import NwDef
from stackone.model.notification import Notification
from stackone.model.EmailSetup import EmailSetup
from stackone.model.CustomSearch import CustomSearch
from stackone.model.DWM import DWM, SPDWMPolicy, DWMPolicySchedule, DWMHistory
from stackone.model.LockManager import CMS_Locks
##from stackone.cloud.DbModel.Account import *
##from stackone.cloud.DbModel.Network import SecurityGroupRule, SecurityGroupRegionRelation
##from stackone.cloud.DbModel.platforms.ec2 import *
##from stackone.cloud.DbModel.platforms.euc import *
##from stackone.cloud.DbModel.platforms.cms import *
##from stackone.cloud.DbModel.CloudProvider import *
##from stackone.cloud.DbModel.StorageDisk import Snapshot, SnapshotRegionRelation
##from stackone.cloud.DbModel.VDC import VDC
##from stackone.cloud.DbModel.AccountTemplate import AccountTemplate
##from stackone.cloud.DbModel.TemplateProvider import TemplateProvider, TemplateGroupType
##from stackone.cloud.DbModel.Quota import *
##from stackone.cloud.DbModel.platforms.cms.CSEP import *
##from stackone.cloud.DbModel.platforms.cms.CMSNetwork import CMSPublicIP
##from stackone.cloud.DbModel.CPTypes import *
from stackone.model.IP import IPPool, PublicIPPool, PrivateIPPool, IPS
from stackone.model.vCenter import VCenter
from stackone.model.PlatformType import *
