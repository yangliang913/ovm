import traceback
import logging
from stackone.model import DBSession
from stackone.model.Sites import Site
from stackone.model.Groups import ServerGroup
from stackone.model.ManagedNode import ManagedNode
from stackone.model.VM import VM, VMDisks
from stackone.model.ImageStore import ImageStore, ImageGroup, Image
from stackone.model.network import NetworkVMRelation
from stackone.model.SPRelations import DCDefLink, SPDefLink, ServerDefLink
from stackone.model.NodeInformation import Instance
from stackone.config.ConfigSettings import NodeConfiguration
from stackone.model.DWM import DWMPolicySchedule
from stackone.model.VLANManager import VLANIDPoolSPRelation
from stackone.model.PrivateIP import PrivateIPPoolSPRelation
from stackone.model.Backup import SPBackupConfig
from stackone.model.EmailSetup import EmailSetup
from stackone.model.Entity import Entity, EntityAttribute, EntityType
import stackone.core.utils.constants as constants
from stackone.core.utils.utils import to_unicode, to_str, print_traceback, dynamic_map, convert_byte_to, get_config_text
from stackone.model.vCenter import VCenter
from stackone.model.Sites import VMWDatacenter
from stackone.model.Groups import VMWServerGroup
LOGGER = logging.getLogger('stackone.model')
class VcenterManager():
    @classmethod
    def get_task_creator(cls):
        from stackone.viewModel.TaskCreator import TaskCreator
        return TaskCreator()
    def add_vCenter(self, auth, host, port, ssl, username, password):
        try:
            vcenter = DBSession.query(VCenter).filter(VCenter.host == host).first()
            if vcenter:
                raise Exception('vCenter Host already existing')
            else:
                vC = VCenter(host, port, ssl, username, password)
                DBSession.add(vC)
                return vC.id
        except Exception as e:
            traceback.print_exc()
            raise e

    def remove_vcenter_entities(self, auth, ent):
        id = ent.entity_id
        if ent.children:
            for child in ent.children:
                self.remove_vcenter_entities(auth, child)
        print 'VCENTER DELETE : ' + ent.name + '/' + ent.type.name + '/' + id
        DBSession.query(EntityAttribute).filter(EntityAttribute.entity_id == id).delete()
        auth.remove_entity(ent)
        if ent.type.name == constants.DATA_CENTER:
            DBSession.query(EmailSetup).filter(EmailSetup.site_id == id).delete()
            DBSession.query(DCDefLink).filter(DCDefLink.site_id == id).delete()
            DBSession.query(Site).filter(Site.id == id).delete()
        elif ent.type.name == constants.SERVER_POOL:
            DBSession.query(SPDefLink).filter(SPDefLink.group_id == id).delete()
            DBSession.query(SPBackupConfig).filter(SPBackupConfig.sp_id == id).delete()
            DBSession.query(DWMPolicySchedule).filter(DWMPolicySchedule.sp_id == id).delete()
            DBSession.query(PrivateIPPoolSPRelation).filter(PrivateIPPoolSPRelation.sp_id == id).delete()
            DBSession.query(VLANIDPoolSPRelation).filter(VLANIDPoolSPRelation.sp_id == id).delete()
            DBSession.query(ServerGroup).filter(ServerGroup.id == id).delete()
        elif ent.type.name == constants.MANAGED_NODE:
            DBSession.query(NodeConfiguration).filter(NodeConfiguration.node_id == id).delete()
            DBSession.query(ServerDefLink).filter(ServerDefLink.server_id == id).delete()
            DBSession.query(Instance).filter(Instance.node_id == id).delete()
            DBSession.query(ManagedNode).filter(ManagedNode.id == id).delete()
        elif ent.type.name == constants.DOMAIN:
            DBSession.query(NetworkVMRelation).filter(NetworkVMRelation.vm_id == id).delete()
            DBSession.query(VMDisks).filter(VMDisks.vm_id == id).delete()
            DBSession.query(VM).filter(VM.id == id).delete()
        elif ent.type.name == constants.IMAGE_STORE:
            DBSession.query(ImageStore).filter(ImageStore.id == id).delete()
        elif ent.type.name == constants.IMAGE_GROUP:
            DBSession.query(ImageGroup).filter(ImageGroup.id == id).delete()
        elif ent.type.name == constants.IMAGE:
            DBSession.query(Image).filter(Image.id == id).delete()

    def remove_vCenter(self, auth, id):
        try:
            dc_ents = DBSession.query(Entity).join(EntityAttribute).join(EntityType).filter(EntityAttribute.name == constants.EXTERNAL_MANAGER_ID).filter(EntityAttribute.value == id).filter(EntityType.name == constants.DATA_CENTER).all()
            print '\n\n\n\n==',
            print dc_ents
            for dc_ent in dc_ents:
                self.remove_vcenter_entities(auth, dc_ent)
            VCenter.remove_by_id(id)
        except Exception as e:
            traceback.print_exc()
            raise e

    def get_vCenters(self, _dc=None):
        try:
            vcenters = DBSession.query(VCenter)
            result = []
            for row in vcenters:
                c = dict(id=row.id, host=row.host, port=row.port, protocol=row.ssl, username=row.credential.cred_details['username'], password=row.credential.cred_details['password'])
                result.append(c)
            return dict(sucess=True, rows=result)
        except Exception as ex:
            traceback.print_exc()
            raise ex

    def edit_vCenter(self, auth, id, host, port, ssl, username, password):
        try:
            row = DBSession.query(VCenter).filter(VCenter.id == id).first()
            if row == None:
                raise Exception('There is no Entity exists in the database')
            row.host = host
            row.ssl = ssl
            row.port = port
            row.credential.cred_details['username'] = username
            row.credential.cred_details['password'] = password
            DBSession.add(row)
            return None
        except Exception as e:
            traceback.print_exc()
            raise e
        return None

    def get_vcenter(self, vcenter_id):
        return VCenter.get_object_by_id(vcenter_id)

    def get_vcenter_credential(self, vcenter_id):
        vcenter = self.get_vcenter(vcenter_id)
        if not vcenter:
            raise Exception('Could not find vCenter by id: %s' % vcenter_id)
        return (vcenter, vcenter.credential)

    def get_vcenter_credential_dict(self, vcenter_id):
        cred_dict = {}
        vcenter,credential = self.get_vcenter_credential(vcenter_id)
        cred_dict['hostname'] = vcenter.host
        cred_dict['username'] = credential.cred_details['username']
        cred_dict['password'] = credential.cred_details['password']
        return (vcenter, cred_dict)

    def get_klass_type(self, klass):
        from psphere.managedobjects import Datacenter
        from psphere.managedobjects import ClusterComputeResource
        from psphere.managedobjects import HostSystem
        from psphere.managedobjects import VirtualMachine
        from psphere.managedobjects import Folder
        TYPE_DICT = {Datacenter.__name__: Datacenter.__name__, ClusterComputeResource.__name__: ClusterComputeResource.__name__, HostSystem.__name__: HostSystem.__name__, VirtualMachine.__name__: VirtualMachine.__name__, Folder.__name__: Folder.__name__}
        return TYPE_DICT.get(klass)

    def get_entity_type(self, klass_name):
        from psphere.managedobjects import Datacenter
        from psphere.managedobjects import ClusterComputeResource
        from psphere.managedobjects import HostSystem
        from psphere.managedobjects import ComputeResource
        from psphere.managedobjects import VirtualMachine
        from psphere.managedobjects import Folder
        TYPE_MAP = {Datacenter.__name__: to_unicode(constants.DATA_CENTER), ClusterComputeResource.__name__: to_unicode(constants.SERVER_POOL), Folder.__name__: to_unicode(constants.SERVER_POOL), HostSystem.__name__: to_unicode(constants.MANAGED_NODE), ComputeResource.__name__: to_unicode(constants.MANAGED_NODE), VirtualMachine.__name__: to_unicode(constants.DOMAIN)}
        return TYPE_MAP.get(klass_name)

    def get_vesxi_node(self, vcenter_id, hostname=None, username=None, password=None, use_keys=True):
        from stackone.core.platforms.vmw.VMWNode import VMWNode
        return VMWNode(hostname=hostname, username=username, password=password, use_keys=use_keys, external_manager_id=vcenter_id)

    def get_root_folder(self, vesxi_node):
        return vesxi_node.node_proxy.get_root_folder()

    def get_datacenter(self, vesxi_node, name):
        return vesxi_node.node_proxy.get_datacenter(name)

    def get_vms_from_vmfolder(self, vmfolder):
        vms = []
        for child in vmfolder.childEntity:
            if self.is_Folder_instance(child):
                vms.extend(self.get_vms_from_vmfolder(child))
                continue
            if not child.config.template:
                vms.append(child)
                continue
        return vms

    def get_templates_from_vmfolder(self, vmfolder):
        templates = []
        vmfolder.update(properties=['childEntity'])
        for child in vmfolder.childEntity:
            child.update()
            if self.is_Folder_instance(child):
                templates.extend(self.get_templates_from_vmfolder(child))
                continue
            if child.config.template:
                templates.append(child)
                continue
        return templates

    def get_templates_from_host(self, node):
        return node.node_proxy.get_template_list()

    def dc_get_host_folder(self, dc):
        return dc.hostFolder

    def get_child_entities(self, parent):
        return parent.childEntity

    def is_ClusterComputeResource_instance(self, instance):
        from psphere.managedobjects import ClusterComputeResource
        return isinstance(instance, ClusterComputeResource)

    def is_HostSystem_instance(self, instance):
        from psphere.managedobjects import HostSystem
        return isinstance(instance, HostSystem)

    def is_Folder_instance(self, instance):
        from psphere.managedobjects import Folder
        return isinstance(instance, Folder)

    def is_Datacenter_instance(self, instance):
        from psphere.managedobjects import Datacenter
        return isinstance(instance, Datacenter)

    def is_VirtualMachine_instance(self, instance):
        from psphere.managedobjects import VirtualMachine
        return isinstance(instance, VirtualMachine)

    def is_ComputeResource_instance(self, instance):
        from psphere.managedobjects import ComputeResource
        return isinstance(instance, ComputeResource)

    def cluster_get_hosts(self, cluster):
        return cluster.host

    def host_get_vms(self, host):
        return host.vm

    def get_all_datacenters(self, vesxi_node):
        return vesxi_node.get_datacenters()

    def create_vmw_datacenter(self, auth, name, actual_name, moid, vcenter_id, parent_ent=None):
        msg = ''
        entityType = to_unicode(constants.DATA_CENTER)
        dc = None
        update_name = False
        dc_ent = auth.get_entity_by_entity_attributes(self.get_entity_attributes_dict(vcenter_id, moid), entityType)
        if not dc_ent:
            dup_ent = auth.get_entity_by_name(name, entityType=entityType)
            if dup_ent:
                msg += '\nERROR: Could not import Datacenter:%s. It is already exist,please choose different name' % name
                return (msg, None, None)
        if dc_ent:
            update_name = self.can_update_managed_object_name(auth, name, actual_name, dc_ent.name)
            msg += '\nDatacenter: %s already exist' % name
            dc = DBSession.query(VMWDatacenter).filter(VMWDatacenter.id == dc_ent.entity_id).first()
            if dc:
                if update_name:
                    dc.name = name
        if not dc:
            msg += '\nCreating Datacenter: %s' % name
            dc = VMWDatacenter(name)
        DBSession.add(dc)
        if not dc_ent:
            dc_ent = Entity()
            dc_ent.name = dc.name
            dc_ent.entity_id = dc.id
            dc_ent.type_id = 1
            ent_cntx_dict = self.get_entity_context_dict(external_manager_id=vcenter_id, external_id=moid)
            dc_ent.context_id = auth.add_context(ent_cntx_dict)
            DBSession.add(dc_ent)
            admin_role = auth.get_admin_role()
            auth.make_rep_entry(admin_role, dc_ent)
            ent_attr_dict = self.get_entity_attributes_dict(external_manager_id=vcenter_id, external_id=moid)
            self.add_entity_attributes(dc_ent, ent_attr_dict)
        else:
            if not update_name:
                name = None
            auth.update_entity(dc_ent, name=name)
        return (msg, dc, dc_ent)


    def is_selected(self, auth, external_id, external_manager_id, type, parent_ent=None):
        entityType = None
        if type in ('HostSystem',):
            entityType = to_unicode(constants.MANAGED_NODE)
        elif type in ('ClusterComputeResource', 'Folder'):
            entityType = to_unicode(constants.SERVER_POOL)
        elif type in ('Datacenter',):
            entityType = to_unicode(constants.DATA_CENTER)
        ent = auth.get_entity_by_entity_attributes(self.get_entity_attributes_dict(external_manager_id, external_id), entityType, parent_ent)
        if ent:
            return True
        return False

    def get_vcenter_connection(self, hostname, username, password):
        vc = dynamic_map()
        vc.hostname = hostname
        vc.username = username
        vc.password = password
        from stackone.core.platforms.vmw.ESXiProxy import vCenterConnectionCache
        return vCenterConnectionCache.get_connection(vc)

    def test_vcenter_connection(self, auth, hostname, username, password):
        return self.get_vcenter_connection(hostname, username, password)

    def create_vmw_server_pool(self, auth, name, actual_name, moid, vcenter_id, parent_ent=None):
        msg = ''
        entityType = to_unicode(constants.SERVER_POOL)
        sp = None
        update_name = False
        sp_ent = auth.get_entity_by_entity_attributes(self.get_entity_attributes_dict(vcenter_id, moid), entityType)
        if not sp_ent:
            dup_ent = auth.get_entity_by_name(name, entityType=entityType)
            if dup_ent:
                msg += '\nERROR: Could not import Server Pool:%s. It is already exist,please choose different name' % name
                return (msg, None, None)

        if sp_ent:
            update_name = self.can_update_managed_object_name(auth, name, actual_name, sp_ent.name)
            msg += '\nServer Pool: %s already exist' % name
            sp = DBSession.query(VMWServerGroup).filter(VMWServerGroup.id == sp_ent.entity_id).first()
            if sp:
                if update_name:
                    sp.name = name
        if not sp:
            msg += '\nCreating Server Pool: %s' % name
            sp = VMWServerGroup(name)
        DBSession.add(sp)
        if not sp_ent:
            cntx = {'external_manager_id': vcenter_id, 'external_id': moid}
            sp_ent = self.add_vcenter_entity(auth, cntx, sp.name, sp.id, to_unicode(constants.SERVER_POOL), parent_ent)
        else:
            if not update_name:
                name = None
            auth.update_entity(sp_ent, name=name, parent=parent_ent)
        return (msg, sp, sp_ent)


    def can_update_managed_object_name(self, auth, name, actual_name, cvt_name):
        fname = '%s(%s)' % (actual_name, cvt_name)
        if name == fname:
            return False
        return True

    @classmethod
    def get_moid(cls, instance):
        from stackone.core.utils.VMWUtils import get_moid
        return get_moid(instance)
    @classmethod
    def get_entity_attributes_dict(cls, external_manager_id=None, external_id=None):
        attributes_dict = {}
        if external_manager_id:
            attributes_dict[constants.EXTERNAL_MANAGER_ID] = external_manager_id
        if external_id:
            attributes_dict[constants.EXTERNAL_ID] = external_id
        return attributes_dict
    @classmethod
    def get_entity_context_dict(cls, **context):
        ATTRS = ('external_manager_id', 'external_id')
        CNTX = ('context1', 'context2', 'context3', 'context4', 'context5')
        context_map = dict(zip(ATTRS, CNTX))
        context_dict = {}
        for k,v in context.items():
            if k not in ATTRS:
                raise Exception('Invalid entity context attribute')
            if v:
                context_dict[context_map.get(k)] = v
                continue
        print '======context_dict=======',
        print context_dict
        return context_dict
    def get_cluster_summary(self, cluster):
        return cluster.summary

    def get_host_summary(self, host):
        return host.summary

    def get_host_hardwaresummary(self, host):
        summary = self.get_host_summary(host)
        return summary.hardware

    def get_host_memorySize(self, host):
        summary_hardware = self.get_host_hardwaresummary(host)
        mem_size = summary_hardware.memorySize
        print '------mem_size------',
        print mem_size,
        print type(mem_size)
        size = convert_byte_to(mem_size)
        return size

    def get_host_numCpuCores(self, host):
        summary_hardware = self.get_host_hardwaresummary(host)
        return summary_hardware.numCpuCores

    def get_host_number_of_vms(self, host):
        return len(host.vm)

    def get_cluster_totalMemory(self, cluster):
        summary = self.get_cluster_summary(cluster)
        return summary.totalMemory

    def get_cluster_totalCpu(self, cluster):
        summary = self.get_cluster_summary(cluster)
        return summary.totalCpu

    def add_entity_attributes(self, ent, ent_attr_dict):
        EntityAttribute.add_entity_attributes(ent, ent_attr_dict)

    def add_vcenter_entity(self, auth, context_dict, ent_name, ent_id, ent_type, parent_ent):
        external_manager_id = context_dict.get('external_manager_id')
        external_id = context_dict.get('external_id')
        ent_cntx_dict = self.get_entity_context_dict(external_manager_id=external_manager_id, external_id=external_id)
        ent = auth.add_entity(ent_name, ent_id, to_unicode(ent_type), parent_ent, context=ent_cntx_dict)
        ent_attr_dict = self.get_entity_attributes_dict(external_manager_id=external_manager_id, external_id=external_id)
        self.add_entity_attributes(ent, ent_attr_dict)
        return ent



