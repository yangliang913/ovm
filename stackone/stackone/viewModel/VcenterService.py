from stackone.model import DBSession
from stackone.model.Entity import Entity
import logging
import simplejson as json
from stackone.core.utils.utils import to_unicode, to_str, print_traceback, get_config_text, wait_for_task_completion
from stackone.viewModel.NodeService import NodeService
from stackone.model.services import Task
from stackone.model.UpdateManager import UIUpdateManager
from stackone.model.VcenterManager import VcenterManager
import stackone.core.utils.constants as constants
LOGGER = logging.getLogger('stackone.viewModel')
class VcenterService():
    node_service = NodeService()
    vcenter_manager = VcenterManager()
    #######
    @classmethod
    def get_task_creator(cls):
        return cls.vcenter_manager.get_task_creator()
    def add_vCenter(self, auth, host, port, ssl, username, password):
        try:
            result = None
            result = self.vcenter_manager.add_vCenter(auth,host,port,ssl,username,password)
            return dict(success = True,msg = 'vCenter Added',id = result,host = host,port = port,ssl = ssl,username = username,password = password)
        except Exception,ex:
            err = to_str(ex).replace("'",' ')
            print_traceback()
            return dict(success = False,msg = err)
    def remove_vCenter(self, auth, id):
        try:
            self.vcenter_manager.remove_vCenter(auth,id)
            return dict(success = True,msg = 'vCenter Removed')
        except Exception,ex:
            err = to_str(ex).replace("'",' ')
            return dict(success = False,msg = err)
    def get_vCenters(self, _dc=None):
        result = None
        result = self.vcenter_manager.get_vCenters()
        return result

    def edit_vCenter(self, auth, id, host, port, ssl, username, password):
        try:
            self.vcenter_manager.edit_vCenter(auth,id,host,port,ssl,username,password)
            return dict(success = True,msg = 'vCenter Added',id = id,host = host,port = port,ssl = ssl,username = username,password = password)
        except Exception,ex:
            err = to_str(ex).replace("'",' ')
            return dict(success = False,msg = err)        
    def get_return_dict_for_vcenter_import(self, name, moid, type=None, children=None, selected=False, cpu='', memory='', vms='', actual_name=''):
        if not children:
            children = []
        xtype = type
        if type == 'Datacenter':
            xtype = 'Data Center'
        if type == 'ClusterComputeResource':
            xtype = 'Cluster'
        if type == 'HostSystem':
            xtype = 'Host'
        if type == 'Folder':
            xtype = 'Host Folder'
        return {'uiProvider': 'col', 'moid': moid, 'name': name, 'type': type, 'xtype': xtype, 'cpu': cpu, 'memory': memory, 'vms': vms, 'children': children, 'selected': selected, 'actual_name': actual_name}

    def get_moid(self, instance):
        return VcenterManager.get_moid(instance)

    def is_selected(self, auth, external_id, type, parent_ent=None):
        return self.vcenter_manager.is_selected(auth, external_id, type, parent_ent)

    def format_name_of_managed_object(self, auth, name, external_id, external_manager_id, klass_name):
        entityType = self.vcenter_manager.get_entity_type(klass_name)
        ent = auth.get_entity_by_entity_attributes(self.get_entity_attributes_dict(external_manager_id, external_id), entityType=to_unicode(entityType))
        if ent:
            if name != ent.name:
                res_name = '%s(%s)' % (name, ent.name)
                print 'formated name of managed object: ',
                print res_name
                return res_name
        return name

    def get_managed_objects_from_vcenter(self, auth, vcenter_id):
        from pprint import pprint
        result = []
        vcenter,vcenter_cred = self.vcenter_manager.get_vcenter_credential_dict(vcenter_id)
        vesxi_node = self.vcenter_manager.get_vesxi_node(vcenter_id, hostname=vcenter_cred['hostname'])
        root_folder = self.vcenter_manager.get_root_folder(vesxi_node)
        root_children = self.vcenter_manager.get_child_entities(root_folder)
        for child in root_children:
            child_lst = []
            moid = self.get_moid(child)
            selected = self.vcenter_manager.is_selected(auth, moid, vcenter_id, child.__class__.__name__)
            res_dict = self.get_return_dict_for_vcenter_import(self.format_name_of_managed_object(auth, child.name, moid, vcenter_id, child.__class__.__name__), moid, self.vcenter_manager.get_klass_type(child.__class__.__name__), selected=selected, actual_name=child.name)
            if self.vcenter_manager.is_Folder_instance(child):
                child_lst = self.get_children_from_folder(auth, child, vcenter_id)
            elif self.vcenter_manager.is_Datacenter_instance(child):
                child_lst = self.get_children_from_datacenter(auth, child, vcenter_id)
            res_dict['children'] = child_lst
            result.append(res_dict)
        print '-----result---------',
        print pprint(result)
        return result
######################
    def get_children_from_folder(self, auth, folder, vcenter_id):
        msg = 'Getting Folder: %s' % folder.name
        print msg
        LOGGER.info(msg)
        result = []
        child_entities = self.vcenter_manager.get_child_entities(folder)
        for child_ent in child_entities:
            child = []
            moid = self.get_moid(child_ent)
            selected = self.vcenter_manager.is_selected(auth, moid, vcenter_id, child_ent.__class__.__name__)
            res_dict = self.get_return_dict_for_vcenter_import(self.format_name_of_managed_object(auth, child_ent.name, moid, vcenter_id, child_ent.__class__.__name__), moid, self.vcenter_manager.get_klass_type(child_ent.__class__.__name__), selected=selected, actual_name=child_ent.name)
            if self.vcenter_manager.is_Datacenter_instance(child_ent):
                child = self.get_children_from_datacenter(auth, child_ent, vcenter_id)
                res_dict['children'] = child
                result.append(res_dict)
                continue
            if self.vcenter_manager.is_ClusterComputeResource_instance(child_ent):
                child = self.get_hosts_from_cluster(auth, child_ent, vcenter_id)
                res_dict['children'] = child
                result.append(res_dict)
                continue
            if self.vcenter_manager.is_HostSystem_instance(child_ent):
                child = self.get_host(auth, child_ent, vcenter_id)
                res_dict['children'] = child
                result.append(res_dict)
                continue
            if self.vcenter_manager.is_Folder_instance(child_ent):
                child = self.get_children_from_folder(auth, child_ent, vcenter_id)
                res_dict['children'] = child
                result.append(res_dict)
                continue
            if self.vcenter_manager.is_ComputeResource_instance(child_ent):
                child = self.get_hosts_from_compute_resource(auth, child_ent, vcenter_id)
                result.extend(child)
                continue
        return result

    def get_children_from_datacenter(self, auth, dc, vcenter_id):
        msg = 'Getting Datacenter: %s' % dc.name
        print msg
        LOGGER.info(msg)
        result = []
        host_folder = self.vcenter_manager.dc_get_host_folder(dc)
        child_entities = self.vcenter_manager.get_child_entities(host_folder)
        for child_ent in child_entities:
            child = []
            moid = self.get_moid(child_ent)
            selected = self.vcenter_manager.is_selected(auth, moid, vcenter_id, child_ent.__class__.__name__)
            res_dict = self.get_return_dict_for_vcenter_import(self.format_name_of_managed_object(auth, child_ent.name, moid, vcenter_id, child_ent.__class__.__name__), moid, self.vcenter_manager.get_klass_type(child_ent.__class__.__name__), selected=selected, actual_name=child_ent.name)
            if self.vcenter_manager.is_ClusterComputeResource_instance(child_ent):
                child = self.get_hosts_from_cluster(auth, child_ent, vcenter_id)
                res_dict['children'] = child
                result.append(res_dict)
                continue
            if self.vcenter_manager.is_HostSystem_instance(child_ent):
                child = self.get_host(auth, child_ent, vcenter_id)
                res_dict['children'] = child
                result.append(res_dict)
                continue
            if self.vcenter_manager.is_Folder_instance(child_ent):
                child = self.get_children_from_folder(auth, child_ent, vcenter_id)
                res_dict['children'] = child
                result.append(res_dict)
                continue
            if self.vcenter_manager.is_ComputeResource_instance(child_ent):
                child = self.get_hosts_from_compute_resource(auth, child_ent, vcenter_id)
                result.extend(child)
                continue
        return result

    def get_hosts_from_cluster(self, auth, cluster, vcenter_id):
        msg = 'Getting cluster: %s' % cluster.name
        print msg
        LOGGER.info(msg)
        result = []
        hosts = self.vcenter_manager.cluster_get_hosts(cluster)
        for host in hosts:
            res = self.get_host(auth, host, vcenter_id)
            result.extend(res)
        return result

    def get_hosts_from_compute_resource(self, auth, compute_resource, vcenter_id):
        msg = 'get_hosts_from_compute_resource: %s' % compute_resource.name
        print msg
        LOGGER.info(msg)
        result = []
        hosts = self.vcenter_manager.cluster_get_hosts(compute_resource)
        for host in hosts:
            res = self.get_host(auth, host, vcenter_id)
            result.extend(res)
        return result

    def get_host(self, auth, host, vcenter_id):
        msg = 'Getting host: %s' % host.name
        print msg
        LOGGER.info(msg)
        moid = self.get_moid(host)
        selected = self.vcenter_manager.is_selected(auth, moid, vcenter_id, host.__class__.__name__)
        res = self.get_return_dict_for_vcenter_import(self.format_name_of_managed_object(auth, host.name, moid, vcenter_id, host.__class__.__name__), moid, self.vcenter_manager.get_klass_type(host.__class__.__name__), selected=selected, cpu=self.vcenter_manager.get_host_numCpuCores(host), memory=self.vcenter_manager.get_host_memorySize(host), vms=self.vcenter_manager.get_host_number_of_vms(host), actual_name=host.name)
        return [res]

    def get_vms_from_host(self, host):
        result = []
        vms = self.vcenter_manager.host_get_vms(host)
        for vm in vms:
            res = self.get_vm(vm)
            result.extend(res)
        return result

    def get_vm(self, vm):
        msg = 'Getting VM: %s' % vm.name
        print msg
        LOGGER.info(msg)
        res = self.get_return_dict_for_vcenter_import(self.format_name_of_managed_object(auth, vm.name, moid, vcenter_id, vm.__class__.__name__), self.get_moid(vm), self.vcenter_manager.get_klass_type(vm.__class__.__name__))
        return [res]

    def test_vcenter_connection(self, auth, hostname, username, password):
        try:
            self.vcenter_manager.test_vcenter_connection(auth,hostname,username,password)
            return dict(success = True,msg = 'Successfully connected to vCenter')
        except Exception,ex:
            err = to_str(ex).replace("'",' ')
            LOGGER.error(':' + err)
            print_traceback()
            return dict(success = False,msg = err)
            
    def get_entity_attributes_dict(self, external_manager_id, external_id):
        return self.vcenter_manager.get_entity_attributes_dict(external_manager_id, external_id)

    def validate_duplicate_entity(self, auth, name, moid, vcenter_id, entity_type, display_type):
        ent = auth.get_entity_by_entity_attributes(self.get_entity_attributes_dict(vcenter_id, moid), entity_type)
        if not ent:
            dup_ent = auth.get_entity_by_name(name, entityType=entity_type)
            if dup_ent:
                msg = '%s:%s already exist,please choose a different name' % (display_type, name)
                raise Exception(msg)
        else:
            if ent.name != name:
                dup_ent = auth.get_entity_by_name(name, entityType=entity_type)
                if dup_ent:
                    msg = '%s:%s already exist,please a choose different name' % (display_type, name)
                    raise Exception(msg)

    def validate_vcenter(self, auth, vcenter_id, context):
        context = json.loads(context)
        selected_objects = context.get('selected_objects')
        print '=====selected_objects=========',
        print selected_objects
        for item in selected_objects:
            dc = item.get('dc')
            dcname = dc.get('name')
            dc_moid = dc.get('moid')
            entityType = to_unicode(constants.DATA_CENTER)
            self.validate_duplicate_entity(auth, dcname, dc_moid, vcenter_id, entityType, display_type=to_unicode(constants.TXT_DC))
            hosts = item.get('hosts', [])
            parent = item.get('parent', {})
            parent_name = parent.get('name')
            parent_type = parent.get('type')
            parent_moid = parent.get('moid')
            entityType = to_unicode(constants.SERVER_POOL)
            self.validate_duplicate_entity(auth, parent_name, parent_moid, vcenter_id, entityType, display_type=to_unicode(constants.TXT_SP))
            entityType = to_unicode(constants.MANAGED_NODE)
            for host in hosts:
                hostname = host.get('name')
                host_moid = host.get('moid')
                self.validate_duplicate_entity(auth, hostname, host_moid, vcenter_id, entityType, display_type=to_unicode(constants.TXT_SRVR))

    def import_managed_objects_from_vcenter(self, auth, site_id, vcenter_id, context):
        from stackone.model.ManagedNode import ManagedNode
        msg = ''
        context = json.loads(context)
        selected_objects = context.get('selected_objects')
        platform = 'vmw'
        vcenter = self.vcenter_manager.get_vcenter(vcenter_id)
        if vcenter:
            msg += '\nImporting vCenter %s' % vcenter.host
        from pprint import pprint
        print '====================',
        print pprint(selected_objects)
        tc = self.vcenter_manager.get_task_creator()
        for item in selected_objects:
            dc = item.get('dc')
            dcname = dc.get('name')
            dc_moid = dc.get('moid')
            dc_actual_name = dc.get('actual_name')
            lmsg,dc_obj,dc_ent = self.vcenter_manager.create_vmw_datacenter(auth, dcname, dc_actual_name, dc_moid, vcenter_id)
            msg += lmsg
            if not dc_ent:
                continue
            hosts = item.get('hosts', [])
            parent = item.get('parent', {})
            parent_name = parent.get('name')
            parent_type = parent.get('type')
            parent_moid = parent.get('moid')
            parent_actual_name = parent.get('actual_name')
            lmsg,sp,sp_ent = self.vcenter_manager.create_vmw_server_pool(auth, parent_name, parent_actual_name, parent_moid, vcenter_id, parent_ent=dc_ent)
            msg += lmsg
            if not sp_ent:
                continue
            print '======hosts=========',
            print hosts
            for host in hosts:
                node_id = None
                hostname = host.get('name')
                host_moid = host.get('moid')
                username = ''
                password = ''
                ssh_port = 22
                protocol = ''
                xen_port = '8006'
                xen_migration_port = '8002'
                use_keys = 'true'
                host_ent = auth.get_entity_by_entity_attributes(self.get_entity_attributes_dict(vcenter_id, host_moid), entityType=to_unicode(constants.MANAGED_NODE))
                if host_ent:
                    node_id = host_ent.entity_id
                    msg += '\nServer: %s already exist' % hostname
                    auth.update_entity(host_ent, parent=sp_ent)
                    vesxi_node_id = host_ent.entity_id
                    task_id = tc.import_vm_action(auth, vesxi_node_id, action='import_vms', paths='', external_manager_id=vcenter_id)
                    msg += '\nImport Virtual Machines Task submitted, server:%s, Task id:%s' % (hostname, task_id)
                else:
                    msg += '\nCreating Server: %s \n' % hostname
                    result = self.node_service.add_node(auth, sp_ent.entity_id, platform, hostname, ssh_port, username, password, protocol, xen_port, xen_migration_port, use_keys, external_manager_id=vcenter_id, external_id=host_moid)
                    if not result.get('success'):
                        msg += 'ERROR:' + result.get('msg')
                        continue
                    msg += result.get('msg')
                    node_id = result.get('node_id')
                print '###########=========Import vCenter Templates==========###########'
                mnode = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
                if not mnode:
                    msg += '\nCould not find Server with ID:%s' % node_id
                    continue
                task_id = tc.import_vcenter_templates_task(auth, node_id, dc_ent.entity_id, vcenter_id, dc)
                msg += '\nImport Templates Task submitted, server:%s, Task id:%s' % (mnode.hostname, task_id)
            import transaction
            transaction.commit()
            print '#UIUpdateManager: Updating Entities'
            UIUpdateManager().set_updated_entities('0')
        return msg

    def import_vcenter_templates(self, auth, node_id, dc_id, vcenter_id, dc):
        from stackone.viewModel import Basic
        from stackone.model.ManagedNode import ManagedNode
        from stackone.model.ImageStore import VcenterImage, VcenterImageGroup, ImageStore
        import transaction
        image_store = Basic.getImageStore()
        registry = Basic.getPlatformRegistry()
        msg = ''
        dcname = dc.get('name')
        dc_moid = dc.get('moid')
        dc_actual_name = dc.get('actual_name')
        mnode = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
        if not mnode:
            msg += '\nCould not find Server with ID:%s' % node_id
            raise Exception(msg)
        msg += '\nImporting Templates from Server: %s' % mnode.hostname
        templates = self.vcenter_manager.get_templates_from_host(mnode)
        temp_lib_ent = None
        dc_ent = auth.get_entity(dc_id)
        if not dc_ent:
            msg += '\nCould not find Datacenter'
            raise Exception(msg)
        temp_lib_ents = auth.get_child_entities_by_type(dc_ent, constants.IMAGE_STORE)
        TemplateLibrary_Name = dcname + '_TemplateLibrary'
        if temp_lib_ents:
            temp_lib_ent = temp_lib_ents[0]
        else:
            msg += '\nCreating Vcenter TemplateLibrary %s' % TemplateLibrary_Name
            vimage_store = image_store.create_vcenter_templateLib(registry, TemplateLibrary_Name)
            DBSession.add(vimage_store)
            transaction.commit()
            temp_lib_ent = auth.add_entity(vimage_store.name, vimage_store.id, to_unicode(constants.IMAGE_STORE), dc_ent)
            if not temp_lib_ent:
                msg += '\nCould not find Vcenter Template Library'
                raise Exception(msg)
        img_gp_ent = auth.get_entity_by_entity_attributes(self.get_entity_attributes_dict(external_manager_id=vcenter_id, external_id=dc_moid), entityType=to_unicode(constants.IMAGE_GROUP))
        if not img_gp_ent:
            msg += '\nCreating Image Group %s' % dcname
            img_gp = image_store.create_vcenter_image_group(dcname)
            DBSession.add(img_gp)
            cntx = {'external_manager_id': vcenter_id, 'external_id': dc_moid}
            img_gp_ent = self.vcenter_manager.add_vcenter_entity(auth, cntx, img_gp.name, img_gp.id, to_unicode(constants.IMAGE_GROUP), temp_lib_ent)
        else:
            img_gp = DBSession.query(VcenterImageGroup).filter(VcenterImageGroup.id == img_gp_ent.entity_id).first()
            img_gp.name = dcname
            DBSession.add(img_gp)
            msg += '\nImage Group %s already exist' % dcname
        for template in templates:
            img_name = template.config.name
            moid = self.get_moid(template)
            img_ent = auth.get_entity_by_entity_attributes(self.get_entity_attributes_dict(external_manager_id=vcenter_id, external_id=moid), entityType=to_unicode(constants.IMAGE))
            if not img_ent:
                image = image_store.create_image_instance(img_name, constants.VCENTER)
                msg += '\nCreated Image:%s' % img_name
            else:
                image = DBSession.query(VcenterImage).filter(VcenterImage.name == img_name).first()
                msg += '\nUpdating Image:%s' % img_name
            vm_config = image.get_vm_config(mnode)
            image_config = image.get_image_config(vm_config)
            vm_config['dc_actual_name'] = dc_actual_name
            vm_config['dc_name'] = dcname
            vm_config['external_manager_id'] = vcenter_id
            image.vm_config = get_config_text(vm_config)
            image.image_config = get_config_text(image_config)
            DBSession.add(image)
            if not img_ent:
                cntx = {'external_manager_id': vcenter_id, 'external_id': moid}
                self.vcenter_manager.add_vcenter_entity(auth, cntx, img_name, image.id, to_unicode(constants.IMAGE), img_gp_ent)
                continue
        import transaction
        transaction.commit()
        print '#UIUpdateManager: Updating Entities'
        UIUpdateManager().set_updated_entities(img_gp_ent.entity_id)
        return msg



