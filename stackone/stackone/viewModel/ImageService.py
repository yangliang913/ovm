import os
import time
import datetime
from stackone.model.ImageStore import ImageUtils, Image, ImageStore, ImageGroup, VMToImage
from stackone.model.ManagedNode import ManagedNode
from stackone.core.utils.utils import Worker, constants
from stackone.viewModel.ApplianceEntryVO import ApplianceEntryVO
from stackone.viewModel.ImageInfoVO import ImageInfoVO, ImageGroupInfoVO
from stackone.viewModel.ResponseInfo import ResponseInfo
from stackone.model.DBHelper import DBHelper
from stackone.model.Entity import Entity
from stackone.model.VM import VM
from stackone.model import DBSession
import Basic
import logging
LOGGER = logging.getLogger('stackone.viewModel')
import stackone.core.appliance.xva
xva = stackone.core.appliance.xva
from stackone.core.utils.utils import to_unicode, to_str, print_traceback, get_platform_name
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from stackone.model.Authorization import AuthorizationService
from stackone.viewModel.VMService import VMService
from stackone.viewModel.NodeService import NodeService
class ImageService():
    def __init__(self):
        self.image_store = Basic.getImageStore()
        self.appliance_store = Basic.getApplianceStore()
            
    def get_image(self, auth, image_id):
        return self.image_store.get_image(auth, image_id)

    def get_group(self, auth, group_id):
        return self.image_store.get_image_group(auth, group_id)

    def get_groups(self, auth, store_id=None):
        image_groups = self.image_store.get_image_groups(auth, store_id).itervalues()
        return image_groups

    def get_group_images(self, auth, group_id):
        images = self.image_store.get_group_images(auth, group_id)
        return images

    def get_image_groups(self, auth, store_id=None):
        image_groups = self.get_groups(auth, store_id)
        result = []
        for image_group in image_groups:
            childnode = NodeService().get_childnodestatus(auth, image_group.id)
            result.append({'NODE_NAME':image_group.name,'NODE_ID':image_group.id,
                            'NODE_TYPE':constants.IMAGE_GROUP,'NODE_CHILDREN':childnode})
        return result

    def get_images(self, auth, group_id, platform=None):
        images = self.get_group_images(auth, group_id)
        result = []
        if images:
            image_list = [ x for x in images.itervalues() if (platform is None or x.platform == platform)]
            #for image_list in images.itervalues():
            image_list.sort(key=(lambda (x): x.get_name()))
        else:
            image_list = []

        for image in image_list:
            childnode=NodeService().get_childnodestatus(auth,image.id)
            result.append({'NODE_NAME':image.name,'NODE_ID':image.id,
                            'NODE_TYPE':constants.IMAGE,'NODE_CHILDREN':childnode})
        return result

    def check_image_exists(self, auth, image_name):
        try:
            if self.image_store.image_exists_by_name(image_name):
                return "{success: true,exists:true,msg: 'Image with the same name exists.'}"
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return "{success: false,msg: '" + to_str(ex).replace("'", '') + "'}"
        return "{success: true,exists:false,msg: 'Success'}"

    
    def get_image_info(self, auth, image_id, group_id=None, platform=None):
        image = self.get_image(auth, image_id)
        filename = image.get_image_desc_html()
        text = 'No description file (%s) for %s ' % (filename, image.get_name())
        if os.path.exists(filename):
            file = Basic.local_node.node_proxy.open(filename)
            lines = file.readlines()
            text = ''.join(lines)
            file.close()
        return text

    def get_image_store_info(self, auth, store_id):
        text = """<body>
            <div style="" class="templatebackground"><center>
            <span style=\"font-size: 180%; font-family: serif; color:blue;text-align:
            center;\">
            Template Library
            </span>
            <br/>
            <span style=\"font-size: 150%; font-family: serif;
            color:#0000FF;text-align: left\">
            Template Library Location:
            </span>"""
        text = text+"""
            <span style=\"font-size: 125%; font-family: serif;color:#0000FF;text-align: left\">"""+\
            self.image_store.get_store_location()+"</span>"
        text = text + """</div></center><br/>
            <span style=\"font-size: 150%; font-family: serif;color:#0000FF;text-align: left\">
            Available Template Groups:
            <br><br>
            </span>
            <ol >
            """
        groups = self.image_store.get_image_groups(auth, store_id)
        group_list = []
        if groups:
            group_list = [x for x in groups.itervalues]
            group_list.sort(key=(lambda x: x.get_name()))
        i = 0
        for grp in group_list:
            i += 1
            text = text + "<li>" + \
            "<span style=\"padding-left:10px;font-size: 125%; font-family: serif;color:#0000FF;text-align: left\">"+\
            to_str(i)+". "+grp.get_name() + "</span></li>" + "\n"
        footer = '</ol></body>'
        text = text + footer
        return text

    def get_image_group_info(self, auth, image_group_id):
        text = """<body>
        <div style="" class="templatebackground" ><center>
         <span style=\"font-size: 180%; font-family: serif; color:blue;text-align:
        center;\">""" +\
        self.get_group(auth,image_group_id).get_name() + \
        """
        </span>
        <br/>
        <span style=\"font-size: 150%; font-family: serif;
        color:#0000FF;text-align: left\">
        Templates Location:
        </span>"""
        text = text +"""
        <span style=\"font-size: 125%; font-family: serif;color:#0000FF;text-align: left\">"""+\
        self.image_store.get_store_location() +"</span>"
        text = text + """</div><br/>
        <span style=\"font-size: 150%; font-family: serif;color:#0000FF;text-align: left\">
        Available Templates: <br><br>
        </span>
        <ol >
        """
        images = self.get_group_images(auth, image_group_id)
        image_list = []

        if images:
            image_list = [x for x in images.itervalues]
            image_list.sort(key=(lambda x: x.get_name()))
        i = 0
        for img in image_list:
            i += 1
            text = text + '<li>' + '<span style="padding-left:10px;font-size: 125%; font-family: serif;color:#0000FF;">' + to_str(i) + '. ' + img.get_name() + '</span></li>' + '\n'
        footer = '</ol></body>'
        text = text + footer
        return text

    def get_image_script(self, auth, image_id):
        image = self.get_image(auth, image_id)
        filename = image.get_provisioning_script()
        text = 'No provisioning script for %s ' % image.get_name()
        if os.path.exists(filename):
            file = Basic.local_node.node_proxy.open(filename)
            lines = file.readlines()
            text = ''.join(lines)
            file.close()
        return text

    def save_image_script(self, auth, image_id, content):
        try:
            mgd_node = Basic.local_node
            self.image_store.save_image_script(auth, mgd_node, image_id, content)
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")
        return "{success: true,msg: 'Success'}"
        
    def save_image_desc(self, auth, image_id, content):
        #LOGGER.info('+++++++++ImageService.save_image_desc+++++++++++++++')
        try:
            mgd_node = Basic.local_node
            self.image_store.save_image_desc(auth, mgd_node, image_id, content)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")
        return "{success: true,msg: 'Success'}"
        
    def add_image_group(self, auth, group_name, store_id, csep_context=None):
        group = self.image_store.new_group(group_name)
        return self.image_store.add_group(auth, group, store_id, csep_context)

    def remove_image_group(self, auth, group_id):
        try:
            self.image_store.delete_group(auth, group_id)
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            return "{success: false,msg: '" + to_str(ex).replace("'", '') + "'}"

        return "{success: true,msg: 'Success'}"

    def rename_image_group(self, auth, group_id, group_name):
        try:
            self.image_store.rename_image_group(auth, group_id, group_name)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return "{success: false,msg: '" + to_str(ex).replace("'", '') + "'}"

        return "{success: true,msg: 'Success'}"
        
    def remove_image(self, auth, image_id, group_id):
        try:
            im = self.get_image(auth,image_id)
            image_store = im.get_image_store(auth)
            msg = image_store.delete_image(auth, group_id, image_id)
            return msg
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise Exception("{success: false,msg: '" + to_str(ex).replace("'", '') + "'}")
        
    def rename_image(self, auth, image_id, image_name, group_id):
        try:
            self.image_store.rename_image(auth, group_id, image_id, image_name)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return "{success: false,msg: '" + to_str(ex).replace("'", '') + "'}"

        return "{success: true,msg: 'Success'}"
        
    def clone_image(self, auth, image_id, image_name, group_id):
        print '=======\n',
        print group_id,
        print image_id,
        print image_name
        image = DBSession.query(Image).filter(Image.id == image_id).first()
        image_store = image.get_image_store(auth)
        msg,image_id = image_store.clone_image(auth,group_id,image_id,image_name)
        return msg,image_id

    def transfer_image(self, auth, image_id, source_group_id, dest_group_id):
        try:
            self.image_store.transfer_image(auth, image_id, source_group_id, dest_group_id)
        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return "{success: true,msg: 'Success'}"
        
    def get_target_images(self, auth, nodeId, imageGroupId):
        try:
            manager = Basic.getGridManager()
            managed_node = manager.getNode(auth, nodeId)
            if managed_node is None:
                raise Exception('Cannot find the Managed Node.')
            result = []
            image_groups = {}
            if imageGroupId is not None:
                image_group = self.image_store.get_image_group(auth, imageGroupId)
                image_groups = {image_group.get_id():image_group}
            else:
                image_groups = self.image_store.get_image_groups(auth)
            
            for image_group in image_groups.itervalues():
                images = self.image_store.get_group_images(auth, image_group.id)
                for image in images.itervalues():
                    if managed_node.is_image_compatible(image) and not image.is_template:
                        result.append(dict(name=image.get_name(), id=image.get_id(), group_id=image_group.get_id()))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', images=result)

    def get_target_image_groups(self, auth, nodeId):
        try:
            manager = Basic.getGridManager()
            managed_node = manager.getNode(auth, nodeId)
            result = []
            if managed_node is None:
                raise Exception('Cannot find the Managed Node.')

            result = []
            mnode_ent = auth.get_entity(managed_node.id)
            dc_ent = mnode_ent.parents[0].parents[0]
            
            image_groups = self.image_store.get_image_groups(auth,dc_ent.entity_id)

            for image_group in image_groups.itervalues():
                count = 0
                images = self.get_group_images(auth, image_group.id)

                for image in images.itervalues():
                    if managed_node.is_image_compatible(image):
                        count = count + 1
                        break
                if count > 0:
                    result.append(dict(name=image_group.get_name(), id=image_group.get_id()))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', image_groups=result)

    def get_image_vm_info(self, image_id):
        result = []
        try:
            img = DBSession.query(Image).filter(Image.id == image_id).one()
        except Exception as e:
            pass
        vm = DBSession.query(VM).filter(VM.image_id == image_id).all()
        for v in vm:
            vname = v.name
            vid = v.id
            ent = DBSession.query(Entity).filter(Entity.entity_id == vid).one()
            ename = ent.parents[0].name
            vm_config = v.get_config()
            vm_comment = ''
            if v.template_version != img.version:
                vm_comment = ' *Current version of the Template is ' + to_str(img.version)
            result.append(dict(icon='show', vmid=vid, vm=vname, server=ename, memory=vm_config['memory'], cpu=vm_config['vcpus'], template_version=to_str(v.template_version), vm_comment=vm_comment, node_id=vid))
        return result

    def get_template_version_info(self, auth, image_id):
        result = []
        try:
            img = DBSession.query(Image).filter(Image.id == image_id).one()
        except Exception as e:
            pass
        if img is not None:
            vms = img.get_older_version_vms()
            for v in vms:
                vname = v.name
                vid = v.id
                ent = auth.get_entity(vid)
                ename = ent.parents[0].name
                result.append(dict(vmid=vid, node_id=vid, vm=vname, server=ename, template_version=to_str(v.template_version)))
        return result

    def get_template_details(self, image_id):
        result = []
        image_instance = DBSession.query(Image).filter(Image.id == image_id).first()
        platform = image_instance.platform
        configs = image_instance.get_configs()
        version = image_instance.version
        vm_config = configs[0]
        ent = DBSession.query(Entity).filter(Entity.entity_id == image_id).one()
        templateGroupName = ent.parents[0].name
        result.append(dict(name='Name', value=ent.name, imageid=image_id))
        result.append(dict(name='Version', value=to_str(version), imageid=image_id))
        result.append(dict(name='Group', value=templateGroupName, imageid=image_id))
        result.append(dict(name='Platform', value=get_platform_name(platform), imageid=image_id))
        result.append(dict(name='Virtual CPUs', value=vm_config['vcpus'], imageid=image_id))
        result.append(dict(name='Memory', value=to_str(vm_config['memory']) + ' MB'))
        return result

    def get_boot_info(self, image_id):
        result = []
        image_instance = DBSession.query(Image).filter(Image.id == image_id).first()
        platform = image_instance.platform
        configs = image_instance.get_configs()
        vm_config = configs[0]
        ent = DBSession.query(Entity).filter(Entity.entity_id == image_id).one()
        result.append(dict(name='Boot Loader', value=vm_config['bootloader']))
        result.append(dict(name='Kernel', value=vm_config['kernel']))
        result.append(dict(name='RAMDisk', value=vm_config['ramdisk']))
        result.append(dict(name='Root Device', value=vm_config['root']))
        result.append(dict(name='Kernel Arguments', value=vm_config['extra']))
        result.append(dict(name='On Power Off', value=vm_config['on_shutdown']))
        result.append(dict(name='On Reboot', value=vm_config['on_reboot']))
        result.append(dict(name='On Crash', value=vm_config['on_crash']))
        return result

    def get_vm_status(self, image_id):
        result = []
        vms = DBSession.query(VM).filter(VM.image_id == image_id).all()
        count_run = 0
        for vm in vms:
            vm_state = vm.get_state_string()
            if vm_state == 'Running' or vm_state == 'Blocked':
                count_run += 1
        result.append(dict(name='Provisioned VMs:', value=to_str(len(vms))))
        result.append(dict(name='Running VMs:', value=to_str(count_run)))
        return result

    def get_piechart_data(self, image_id):
        result = []
        image_vms = DBSession.query(VM).filter(VM.image_id == image_id).all()
        total_image_vms = len(image_vms)
        all_vms = DBSession.query(VM).all()
        image_instance = DBSession.query(Image).filter(Image.id == image_id).first()
        image_name = image_instance.name
        total_vms = len(all_vms)
        if total_vms == 0:
            result.append(dict(total=to_str(0), label='No VMs provisioned'))
            return result
        result.append(dict(value=to_str(total_vms - total_image_vms), label='Other Templates'))
        result.append(dict(value=to_str(total_image_vms), label=image_name))
        return result
    def get_imagestore_details(self, auth, imagestore_id):
        result = []
        imagestore_entity = auth.get_entity(imagestore_id)
        if imagestore_entity is not None:
            for imagegroup_instance in auth.get_child_entities(imagestore_entity):
                group_name = imagegroup_instance.name
                for image_instance in auth.get_child_entities(imagegroup_instance):
                    image_name = image_instance.name
                    vms = DBSession.query(VM).filter(VM.image_id == image_instance.entity_id).all()
                    img = DBSession.query(Image).filter(Image.id == image_instance.entity_id).one()
                    desc_string = image_name
                    desc_string = desc_string + ' template creates a 10G virtual disk (vbd) for use as the primary hard drive. The VM boots from a bootable Linux CD/DVD which, in turn, should kick off the distribution specific installation routine and deploy the OS on the primary hard drive.'
                    result.append(dict(tg=group_name, template=image_name, version=to_str(img.version), vm_num=to_str(len(vms)), desc=desc_string, image_id=image_instance.entity_id, node_id=image_instance.entity_id))
        return result

    def scan_imagestore_details(self, auth, imagestore_id):
        images = DBHelper().get_all(Image)
        img_names = [image.name for image in images]
        entities, rej_imgs = self.image_store.scan_dirs(auth, imagestore_id)
        ent_names = [ent.name for ent in entities]
        new_imgs=[]
        for name in ent_names:
            if name not in img_names:
                new_imgs.append(name)
        return (new_imgs, rej_imgs)

    def get_imagestore_count(self, auth, imagestore_id):
        imagestore_entity = auth.get_entity(imagestore_id)
        if imagestore_entity is None:
            return 0
        return len(auth.get_child_entities(imagestore_entity))

    def get_imagestore_summary_info(self, auth, imagestore_id):
        result = []
        imagestore_entity = auth.get_entity(imagestore_id)
        location = self.image_store.get_store_location()
        if imagestore_entity is None:
            count = 0
        else:
            count = len(auth.get_child_entities(imagestore_entity))
        result.append(dict(name='Template Groups', value=count))
        result.append(dict(name='Location', value=location))
        return result

    def get_imagegrp_summary_info(self, auth, grp_id):
        result = []
        grp = auth.get_entity(grp_id)
        count = len(auth.get_child_entities(grp))
        result.append(dict(name='Group Name', value=grp.name))
        result.append(dict(name='Total Templates', value=count))
        return result

    def get_imagegroup_details(self, auth, imagegroup_id):
        result = []
        imagegroup_entity = auth.get_entity(imagegroup_id)
        if imagegroup_entity:
            for image_entity_instance in auth.get_child_entities(imagegroup_entity):
                image_name = image_entity_instance.name
                modifier = image_entity_instance.modified_by
                m_date = image_entity_instance.modified_date.strftime('%Y-%m-%d')
                image_instance = DBSession.query(Image).filter(Image.id == image_entity_instance.entity_id).first()
                is_hvm = image_instance.is_hvm()
                if is_hvm:
                    hvm = 'yes'
                else:
                    hvm = 'no'
                configs = image_instance.get_configs()
                image_vm_config = configs[0]
                vms = DBSession.query(VM).filter(VM.image_id == image_entity_instance.entity_id).all()
                result.append(dict(template=image_name, version=to_str(image_instance.version), vm_num=to_str(len(vms)), cpu=image_vm_config['vcpus'], memory=image_vm_config['memory'], hvm=hvm, modifier=to_str(modifier), modified_date=m_date, image_id=image_entity_instance.entity_id, node_id=image_entity_instance.entity_id))
        return result

    def get_imagegroup_count(self, auth, imagegroup_id):
        imagegroup_entity = auth.get_entity(imagegroup_id)
        return dict(group_name=imagegroup_entity.name, num_templates=len(auth.get_child_entities(imagegroup_entity)))
    

    #from vm to image
    def is_image_exist(self, auth, image_name):
        return self.image_store.image_exists_by_name(image_name)
    
    #from vm to image   
    def create_image_from_vm_recovery_cleaning(self, auth, node_id, image_name, image_group_id, context, task_id):
        vm_to_image = VMToImage()
        return vm_to_image.create_image_from_vm_recovery_cleaning(auth, node_id, image_name, image_group_id, context, task_id)
    
    #from vm to image
    def create_image_from_vm(self, auth, node_id, image_name, image_group_id, context, task_id):
        from stackone.model.UpdateManager import UIUpdateManager
        import simplejson as json
        context_dct = json.loads(context)
        ref_image_id = context_dct.get('ref_image_id')
        vm_ent = auth.get_entity(node_id)
        if not vm_ent:
            raise Exception('Can not find the Virtual Machine')
        dom = DBSession.query(VM).filter(VM.id == node_id).first()
        if not dom:
            raise Exception('Can not find the Virtual Machine')
        dom_image_id = dom.image_id
        if not dom_image_id:
            dom_image_id = ref_image_id
        dom_image = dom.get_reference_image(dom_image_id)
        if not dom_image:
            msg = 'Can not find the Template:%s associated with the Virtual Machine:%s' % (dom_image_id, dom.name)
            raise Exception(msg)
        image_store = dom.get_image_store(auth, dom_image)
        msg = image_store.create_image_from_vm(auth, node_id, image_name, image_group_id, context, task_id, dom_image)
        UIUpdateManager().set_updated_entities(image_group_id)
        return msg
    
    #from vm to image
    def get_all_image_groups(self, auth, imagestore_id):
        try:
            result = []
            image_groups = self.image_store.get_image_groups(auth)
            for image_group in image_groups.itervalues():
                result.append(dict(id=image_group.id, name=image_group.name))
            return result
        except Exception as ex:
            raise ex
    
    #add 0905
    def get_all_images(self, auth, group_id):
        try:
            result = []
            images = self.image_store.get_group_images(auth, group_id)
            for image in images.itervalues():
                result.append(dict(id=image.id, name=image.name))
            return result
        except Exception as ex:
            raise ex
        
        
class ServiceInfo():
    def __init__(self, return_code, svc_name, message=None):
        self.return_code = return_code
        self.svc_name = svc_name
        self.message = None

    def toXml(self, doc):
        xmlNode = doc.createElement(self.svc_name)
        xmlNode.setAttribute('returnCode', to_str(self.return_code))
        xmlNode.setAttribute('message', to_str(self.message))
        return xmlNode



