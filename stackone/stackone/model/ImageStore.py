import os
import shutil
import time
import re
import urllib
import urllib2
import urlparse
from stackone.core.utils.utils import to_unicode, to_str, get_cms_common_script_dir, get_stackone_cache_common_script_dir
import stackone.core.utils.constants
from stackone.core.utils.constants import *
from stackone.core.utils.utils import PyConfig, copyToRemote, getHexID, get_config_text
from stackone.core.utils.utils import read_python_conf, copyToRemote, mkdir2, get_path, md5_constructor
from stackone.model.VM import VM
import traceback
from stackone.model.DBHelper import DBHelper
from sqlalchemy import *
from sqlalchemy.types import *
from sqlalchemy import orm
from sqlalchemy.schema import Index
from stackone.model import DeclarativeBase, Entity, DBSession
from stackone.model.Authorization import AuthorizationService
import stackone.core.utils.commands as commands
import stackone.core.utils.exceptions as exceptions
from datetime import datetime
import tg
constants = stackone.core.utils.constants
import logging
LOGGER = logging.getLogger('stackone.model')
class Image(DeclarativeBase):
    VM_TEMPLATE = 'vm_conf.template'
    SCRIPT_NAME = 'provision.sh'
    IMAGE_CONF = 'image.conf'
    IMAGE_DESC = 'description.htm'
    IMAGE_DESC_HTML = 'description.html'
    DEFAULT_AVAILABLE_NETWORKS = [{'name': 'Default', 'value': '$DEFAULT_BRIDGE'}, {'name': 'xenbr0', 'value': 'xenbr0'}, {'name': 'xenbr1', 'value': 'xenbr1'}, {'name': 'xenbr2', 'value': 'xenbr2'}, {'name': 'br0', 'value': 'br0'}, {'name': 'br1', 'value': 'br1'}, {'name': 'br2', 'value': 'br2'}, {'name': 'eth0', 'value': 'eth0'}, {'name': 'eth1', 'value': 'eth1'}, {'name': 'eth2', 'value': 'eth2'}]
    DEFAULT_NETWORK = dict(value='$DEFAULT_BRIDGE', name='Default', nw_id='')
    
    __tablename__ = 'images'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    vm_config = Column(Text)
    image_config = Column(Text)
    location = Column(Unicode(255))
    platform = Column(Unicode(50))
    is_template = Column(Boolean)
    base_location = Column(Unicode(255))
    version = Column(Float)
    prev_version_imgid = Column(Unicode(50))
    os_flavor = Column(Unicode(50))
    os_name = Column(Unicode(50))
    os_version = Column(Unicode(50))
    allow_backup = Column(Boolean)
    type = Column(Unicode(50))
    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': u'None'}
    
    @classmethod
    def set_registry(cls, registry):
        cls.registry = registry
        
    def __init__(self, id, platform, name, location, is_template=False):
        self.id = id
        self.name = name
        self.location = location
        self.is_template = is_template
        self.base_location = ''
        if location:
            self.base_location = os.path.basename(location)
        self.platform = platform
        print 'Name ',
        print name,
        print ' Platform ',
        print platform

    def __repr__(self):
        return to_str({'id': self.id, 'name': self.name, 'location': self.location, 'is_template': self.is_template, 'platform': self.platform})

    #pass
    def get_os_name(self):
        return self.os_name
    def is_allow_backup(self):
        return self.allow_backup
    #pass
    def get_os_flavor(self):
        return self.os_flavor
    #pass
    def get_os_version(self):
        return self.os_version
        
    def get_name(self):
        return self.name

    def get_platform(self):
        return self.platform

    def set_name(self, new_name):
        self.name = new_name

    def get_id(self):
        return self.id

    def get_location(self):
        return self.location

    def get_image_dir(self):
        return self.location
    #pass
    def get_configs(self,host_platform=None):
        template_file = self.get_vm_template()
        if host_platform:
            platform = host_platform
        else:
            platform = self.platform
        platform_object = self.registry.get_platform_object(platform)
        vm_config = platform_object.create_vm_config(filename=template_file, config=self.vm_config)
        vm_config.set_filename(template_file)
        i_config_file = self.get_image_conf()
        img_config = platform_object.create_image_config(filename=i_config_file, config=self.image_config)
        return (vm_config, img_config)

    def get_vm_template(self):
        return os.path.join(self.location, self.VM_TEMPLATE)

    def get_image_conf(self):
        return os.path.join(self.location, self.IMAGE_CONF)

    def get_provisioning_script(self):
        return os.path.join(self.location, self.SCRIPT_NAME)

    def get_provisioning_script_dir(self):
        return os.path.join(self.location)

    def get_image_desc(self):
        return os.path.join(self.location, self.IMAGE_DESC)

    def get_image_desc_html(self):
        return os.path.join(self.location, self.IMAGE_DESC_HTML)

    #pass
    def get_image_store(self, auth):
        from stackone.viewModel import Basic
        return Basic.getImageStore()
    
    def get_args_filename(self, vm_name):
        return self.base_location + '_' + vm_name + '.args'

    def get_image_filename(self, vm_name):
        return self.base_location + '_' + vm_name + '_' + 'image.conf'

    def get_log_filename(self, vm_name):
        return self.base_location + '_' + vm_name + '.log'

    def is_hvm(self):
        v_config,img_config = self.get_configs()
        if v_config:
            return v_config.is_hvm()
        return False


    def set_next_version(self):
        import decimal
        self.version = self.version + decimal.Decimal('0.1')

    def get_latest_version(self):
        return self.get_os_version()

    def get_vms(self):
        vms = DBSession.query(VM).filter(VM.image_id == self.id).all()
        return vms

    def get_older_version_vms(self):
        oldvms = DBSession.query(VM).filter(VM.image_id == self.id).filter(VM.template_version < self.version).all()
        return oldvms
    
    #pass
    def get_provisioning_helper(self):
        from stackone.core.platforms.vmw.VMWHelpers import VMWProvisioningHelper
        return VMWProvisioningHelper()
    #pass
    def get_network_models(self):
        infolist = []
        infolist.append(dict(name='i82551', value='i82551'))
        infolist.append(dict(name='i8255715', value='i8255715'))
        infolist.append(dict(name='i82559er', value='i82559er'))
        infolist.append(dict(name='ne2k-pci', value='ne2k-pci'))
        infolist.append(dict(name='ne2k-isa', value='ne2k-isa'))
        infolist.append(dict(name='pcnet', value='pcnet'))
        infolist.append(dict(name='rtl8139', value='rtl8139'))
        infolist.append(dict(name='rmc91c111', value='rmc91c111'))
        infolist.append(dict(name='lance', value='lance'))
        infolist.append(dict(name='mef-fec', value='mef-fec'))
        infolist.append(dict(name='virtio', value='virtio'))
        return infolist
    #pass
    def get_default_available_networks(self):
        return self.DEFAULT_AVAILABLE_NETWORKS
    #pass   
    def get_default_network(self):
        return self.DEFAULT_NETWORK



Index('img_name', Image.name)

class XenImage(Image):
    __mapper_args__ = {'polymorphic_identity': constants.PLT_XEN}
    def __init__(self, *args, **kwargs):
        Image.__init__(self, *args, **kwargs)



class KvmImage(Image):
    __mapper_args__ = {'polymorphic_identity': constants.PLT_KVM}
    def __init__(self, *args, **kwargs):
        Image.__init__(self, *args, **kwargs)




class ImageGroup(DeclarativeBase):
    __tablename__ = 'image_groups'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    type = Column(Unicode(50))
    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': u'None'}
    def __init__(self, id, name, images):
        self.id = id
        self.name = name
        self.images = images
    #@orm.reconstructor
    def _check_for_dup(self, name):
        for img in self.images.itervalues():
            if name == img.name:
                raise Exception('Image with the same name exists')
                continue


    def add_image(self, image):
        self._check_for_dup(image.name)
        self.images[image.id] = image

    def remove_image(self, image_id):
        del self.images[image_id]

    def get_images(self):
        return self.images

    def get_name(self):
        return self.name

    def set_name(self, new_name):
        self.name = new_name

    def get_id(self):
        return self.id

    def get_image(self, id):
        if id in self.images:
            return self.images[id]


    def get_image_by_name(self, name):
        for img in self.images.itervalues():
            if name == img.name:
                return img
        return None


    def image_exists_by_name(self, name):
        try:
            self._check_for_dup(name)
            return False
        except: 
            return True        
    @orm.reconstructor
    def init_on_load(self):
        self.images = {} 
    def __repr__(self):
        return {'id':to_str(self.id),'name':self.name,'image_ids':self.images.keys()}
    #tianfeng
    @classmethod
    def get_image_group(cls, id):
        image_store = None
        image_store = DBSession.query(cls).filter(cls.id == id).first()
        return image_store
    #pass
    def get_platform(self):
        platform = self.type
        if platform != 'None' and platform:
            return platform
        return constants.GENERIC
            

Index('imggrp_name', ImageGroup.name)
class ImageStore(DeclarativeBase):
    __tablename__ = 'image_stores'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    location = Column(Unicode(255))
    type = Column(Unicode(50))
    __mapper_args__ = {'polymorphic_on': type, 'polymorphic_identity': u'None'}
    STORE_CONF = 'image_store.conf'
    DEFAULT_STORE_LOCATION = '/var/cache/stackone/image_store'
    COMMON_DIR = 'common'
    INVALID_CHARS = '(space,comma,dot,quotes,/,\\|,<,>,!,&,%,.,^)'
    INVALID_CHARS_EXP = '( |/|,|<|>|\\||\\!|\\&|\\%|\\.|\'|"|\\^|\\\\)'
    VM_INVALID_CHARS = '(space,comma,quotes,/,\\|,<,>,!,&,%,.,^)'
    VM_INVALID_CHARS_EXP = '( |/|,|<|>|\\||\\!|\\&|\\%||\'|"|\\^|\\\\)'
    TEMPORARY_DIR_PREFIX = '__'
    #pass
    def image_copytree(self, src_location, dest_location):
        shutil.copytree(src_location, dest_location)
    #pass
    def _clone_image(self, *args, **kwargs):
        return None
    #pass
    def _create_image_from_vm(self, auth, node_id, image_name, image_group_id, context, task_id, dom_image):
        vm_to_image = VMToImage()
        return vm_to_image.create_image_from_vm(auth, node_id, image_name, image_group_id, context, task_id)
    #pass
    def template_delete(self, auth, image_group_id, imageId):
        import transaction
        try:
            msg = ''
            ent = auth.get_entity(imageId)
            print '111111111',imageId
            if ent is not None:
                if not auth.has_privilege('REMOVE_IMAGE', ent):
                    raise Exception(constants.NO_PRIVILEGE)
                vms = DBHelper().filterby(VM, [], [VM.image_id == imageId])
                if len(vms):
                    vms_names = [vm.name for vm in vms]
                    msg = 'Image:%s is used by Virtual Machine(s): %s' %(ent.name,', '.join(vms_names))
                    print msg
                    LOGGER.info(msg)
                    raise Exception('Can not delete Template, ' + ent.name + '. VMs provisioned from this Template exists.')
                self.delete_image_completely_from_cloud(auth, imageId)
                print '#########ent###',ent,imageId
                auth.remove_entity(ent)
                transaction.commit()
                DBHelper().delete_all(Image, [], [Image.prev_version_imgid == imageId])
                transaction.commit()
                print ent,'############ent'
                msg = 'Template Deleted Successfully'
        except Exception as ex:
            traceback.print_exc()
            msg += '\n' + to_str(ex)
            raise Exception(ex)
        return msg

    #pass
    def save_image_from_vm(self, auth, node_id, image_name, image_group_id, context, task_id, dom_image):
        return self._create_image_from_vm(auth, node_id, image_name, image_group_id, context, task_id, dom_image)
    @classmethod
    def getId(cls, name):
        x = md5_constructor(name)
        x.update(to_str(time.time()))
        return x.hexdigest()
    @classmethod
    def sanitize_name(cls, name):
        return re.sub(cls.INVALID_CHARS_EXP,'_', name)
    def _get_location(self, name):
        return os.path.join(self._store_location, self.sanitize_name(name))
    #tianfeng
    @classmethod
    def get_image_store(cls, id):
        image_store = None
        image_store = DBSession.query(cls).filter(cls.id == id).first()
        return image_store
    #pass
    def get_location(self, name):
        return self._get_location(name)
    
    def is_template(self, name):
        return name[0] == '_'

    
    @orm.reconstructor
    def init_on_load(self):
        self.images = {}
        self.image_groups = {}
        self._default = None
        self._default_group = None
        self._excludes = []
        self._hashexcludes =[]
        self._store_location = self.location
        
        
    def new_group(self, name):
        return ImageGroup(getHexID(name, [constants.IMAGE_GROUP]), name, {})

    def new_image(self, name, platform):
        return Image(getHexID(name, [constants.IMAGE]), platform, name, self._get_location(name))

    def __init__(self, registry):
        self._registry = registry
        Image.set_registry(registry)
        ImageUtils.set_registry(registry)
        self._ImageStore__initialize()

    #@orm.reconstructor
    def set_registry(self, registry):
        self._registry = registry
        Image.set_registry(registry)
        ImageUtils.set_registry(registry)

    def _ImageStore__init_images(self, images_info):
        self.images = {}
        imgs = {}
        if images_info:
            imgs = eval(images_info)
        for k,v in imgs.iteritems():
            if v.get('platform') is None:
                v['platform'] = 'xen'
            self.images[k] = Image(v['id'], v['platform'], v['name'], v['location'], v['is_template'])

    def _ImageStore__init_groups(self, groups_info):
        self.image_groups = {}
        igs = {}
        if groups_info:
            igs = eval(groups_info)
        for k,v in igs.iteritems():
            images = {}
            images[id] = [self.images[id] for id in v['image_ids']]
            self.image_groups[k] = ImageGroup(v['id'], v['name'], images)
            if self.image_groups[k].get_name() == 'Common':
                self._default_group = self.image_groups[k]
                continue


    def _init_from_dirs(self, dir=None):
        self._ImageStore__read_store_conf()
        if dir is None or dir == '':
            dir = self._store_location
        for file in os.listdir(dir):
            if file not in self._excludes and file[0] != '.':
                full_file = os.path.join(dir, file)
                if os.path.isdir(full_file):
                    try:
                        id = getHexID(file, [constants.IMAGE])
                        location = full_file
                        name = file
                        if len(name) > 50:
                            name = name[0:50]
                        is_template = self.is_template(name)
                        img = self.create_image_instance(to_unicode(name),to_unicode('xen'),id=id,location=to_unicode(location),is_template=is_template)
                        vm_file = img.get_vm_template()
                        cfg = PyConfig(filename = vm_file)
                        if cfg.get('platform') is not None:
                            img.platform = to_unicode(cfg.get('platform'))
                            img = self.create_image_instance(to_unicode(name),cfg.get('platform'),id=id,location=to_unicode(location),is_template=is_template)
                        else:
                            cfg['platform'] = img.platform
                            cfg.write()
                        img.version = constants.image_starting_version
                        img.prev_version_imgid = id
                        img.os_flavor = to_unicode(cfg['os_flavor'])
                        img.os_name = to_unicode(cfg['os_name'])
                        img.os_version = to_unicode(cfg['os_version'])
                        img.allow_backup = True
                        vm_config,image_config = img.get_configs()
                        img.vm_config = get_config_text(vm_config)
                        img.image_config = get_config_text(image_config)
                        self.images[id] = img
                    except Exception as e:
                        print 'Exception: ',
                        print e
                continue
        common_grp_name = u'Common'
        xen_pv_grp_name = u'Xen Paravirtual'
        kvm_pv_grp_name = u'KVM'
        custom_grp_name = u'Custom'
        vmw_grp_name = u'VMware'
        
        common_images = {}
        xen_pv_images = {}
        kvm_pv_images = {}
        custom_images = {}
        vmw_images = {}
        for id,img in self.images.iteritems():
            if img.platform == 'vmw':
                vmw_images[id] = img
            elif img.is_hvm():
                common_images[id] = img

            elif img.platform == 'xen':
                xen_pv_images[id] = img
            elif img.platform == 'kvm':
                kvm_pv_images[id] = img
            else:
                custom_images[id] = img
                
        for g_name,g_images in ((common_grp_name, common_images), (xen_pv_grp_name, xen_pv_images), (kvm_pv_grp_name, kvm_pv_images),(vmw_grp_name,vmw_images), (custom_grp_name, custom_images)):
            if g_images:
                g = self.create_image_group(g_name,g_images)
                #g = ImageGroup(getHexID(g_name, [constants.IMAGE_GROUP]), g_name, g_images)
                self.image_groups[g.id] = g
        auth = AuthorizationService()
        entities = []
        iss = DBHelper().filterby(Entity, [], [Entity.entity_id == self.id])[0]
        for grp in self.image_groups.itervalues():
            grpimages = grp.images
            grps = DBHelper().filterby(Entity, [], [Entity.name == grp.name])
            if len(grps) == 0:
                grp_ent = auth.add_entity(grp.name, grp.id, to_unicode(constants.IMAGE_GROUP), iss)
                DBHelper().add(grp)
            else:
                grp_ent = grps[0]
                grp.images = grpimages
            entities.append(grp_ent)
            for img in grp.images.itervalues():
                imgs = DBHelper().filterby(Entity, [], [Entity.name == img.name])
                if len(imgs) == 0:
                    DBHelper().add(img)
                    img_ent = auth.add_entity(img.name, img.id, to_unicode(constants.IMAGE), grp_ent)
                else:
                    img_ent = imgs[0]
                entities.append(img_ent)
        return entities
        self._ImageStore__read_store_conf()
        if dir is None or dir == '':
            dir = self._store_location
        for file in os.listdir(dir):
            pass



    def init_scan_dirs(self):
        import transaction
        try:
            auth = AuthorizationService()
            self.scan_dirs(auth, self.id)
        except Exception as e:
            traceback.print_exc()
        transaction.commit()


    def scan_dirs(self, auth, imagestore_id):
        self._ImageStore__read_store_conf()
        dir = self._store_location
        new_imgs = {}
        rej_imgs = []
        img_names = self.get_image_names()
        for file in os.listdir(dir):
            if file not in self._excludes and file[0] != '.':
                full_file = os.path.join(dir, file)
                if file in img_names or file.startswith(self.TEMPORARY_DIR_PREFIX):
                    continue
                if os.path.isdir(full_file):
                    try:
                        id = getHexID(file, [constants.IMAGE])
                        location = full_file
                        name = file
                        if len(name) > 50:
                            name = name[0:50]
                        is_template = self.is_template(name)
                        img = self.create_image_instance(to_unicode(name),to_unicode('xen'),id=id,location=to_unicode(location),is_template=is_template)
                        #img = Image(id, to_unicode('xen'), to_unicode(name), to_unicode(location), is_template)
#                        img.version = constants.image_starting_version
#                        img.prev_version_imgid = id
                        vm_file = img.get_vm_template()
                        cfg = PyConfig(filename=vm_file)
                        if cfg.get('platform') is not None:
                            img.platform = to_unicode(cfg.get('platform'))
                            img = self.create_image_instance(to_unicode(name),cfg.get('platform'),id=id,location=to_unicode(location),is_template=is_template)
                        else:
                            cfg['platform'] = img.platform
                            cfg.write()
                        img.version = constants.image_starting_version
                        img.prev_version_imgid = id
                        img.os_flavor = to_unicode(cfg['os_flavor'])
                        img.os_name = to_unicode(cfg['os_name'])
                        img.os_version = to_unicode(cfg['os_version'])
                        img.allow_backup = True
                        vm_config,image_config = img.get_configs()
                        img.vm_config = get_config_text(vm_config)
                        img.image_config = get_config_text(image_config)
                        new_imgs[id] = img
                    except Exception as e:
                        traceback.print_exc()
                        rej_imgs.append(to_str(e))
                    continue
        common_grp_name = u'Common'
        xen_pv_grp_name = u'Xen Paravirtual'
        kvm_pv_grp_name = u'KVM'
        custom_grp_name = u'Custom'
        vmw_grp_name = u'VMware'
        common_images = {}
        xen_pv_images = {}
        kvm_pv_images = {}
        custom_images = {}
        vmw_images = {}
        for id,img in new_imgs.iteritems():
            if img.platform == 'vmw':
                vmw_images[id] = img
            elif img.is_hvm():
                common_images[id] = img
                
            elif img.platform == 'xen':
                xen_pv_images[id] = img
                
            elif img.platform == 'kvm':
                kvm_pv_images[id] = img
            else:
                custom_images[id] = img
        new_grps = {}
        for g_name,g_images in ((common_grp_name, common_images), (xen_pv_grp_name, xen_pv_images), (kvm_pv_grp_name, kvm_pv_images),(vmw_grp_name,vmw_images), (custom_grp_name, custom_images)):
            if g_images:
                g = self.create_image_group(g_name,g_images)
                #g = ImageGroup(getHexID(g_name, [constants.IMAGE_GROUP]), g_name, g_images)
                new_grps[g.id] = g
                continue
        entities = []
        iss = DBHelper().filterby(Entity, [], [Entity.entity_id == imagestore_id])[0]
        for grp in new_grps.itervalues():
            grpimages = grp.images
            grps = DBHelper().filterby(Entity, [], [Entity.name == grp.name])
            if len(grps) == 0:
                grp_ent = auth.add_entity(grp.name, grp.id, to_unicode(constants.IMAGE_GROUP), iss)
                DBHelper().add(grp)
            else:
                grp_ent = grps[0]
                grp.images = grpimages
            for img in grp.images.itervalues():
                imgs = DBHelper().filterby(Entity, [], [Entity.name == img.name])
                if len(imgs) == 0:
                    DBHelper().add(img)
                    img_ent = auth.add_entity(img.name, img.id, to_unicode(constants.IMAGE), grp_ent)
                else:
                    img_ent = imgs[0]
                entities.append(img_ent)

    #@orm.reconstructor
    def _ImageStore__initialize(self):
        self.images = {}
        self.image_groups = {}
        self._default = None
        self._default_group = None
        self._excludes = []
        self._hashexcludes = []
        self._store_location = self.location

    def _ImageStore__read_store_conf(self):
        conf_file = os.path.join(self._store_location, self.STORE_CONF)
        conf = read_python_conf(conf_file)
        if conf is not None:
            if conf.has_key('default'):
                self._default = conf['default']
            if conf.has_key('excludes'):
                self._excludes = conf['excludes']
            if conf.has_key('hashexcludes'):
                self._hashexcludes = conf['hashexcludes']


    def _commit(self):
        self.save_image_groups()
        self.save_images()

    def re_initialize(self):
        self._ImageStore__initialize()

    def get_vm_template(self, image_id):
        image = self.images[image_id]
        vm_template = image.get_vm_template()
        return vm_template

    def get_provisioning_script(self, image_id):
        image = self.images[image_id]
        script = image.get_provisioning_script()
        return script

    def get_provisioning_script_dir(self, image_id):
        image = self.images[image_id]
        script_dir = image.get_provisioning_script_dir()
        return script_dir

    def add_image_to_group(self, image_group, image):
        self.images[image.id] = image
        image_group.add_image(image)
        self._commit()

    def remove_image_from_group(self, image_group, image):
        self.images[image.id] = image
        image_group.remove_image(image.id)
        self._commit()

    def get_default_image(self, auth):
        for img in self.get_images(auth).itervalues():
            if img == self._default:
                return img
        return None


    def get_default_image_group(self, auth):
        for grp in self.get_image_groups(auth).itervalues():
            if grp == self._default_group:
                return grp
        return None


    def get_image(self, auth, imageId):
        if imageId is None:
            return None
        ent = auth.get_entity(imageId)
        if ent is not None:
            return DBHelper().find_by_id(Image, imageId)
        return None


    def get_image_by_name(self, image_name):
        imgs = DBHelper().filterby(Image, [], [Image.name == image_name])
        if len(imgs) > 0:
            return imgs[0]


    def get_images(self, auth):
        imgs = {}
        grps = DBHelper().get_all(ImageGroup)
        for grp in grps:
            images = self.get_group_images(auth, grp.id)
            for img in images.itervalues():
                imgs[img.id] = img
        return imgs


    def get_image_names(self):
        imgs = []
        images = DBHelper().get_all(Image)
        for image in images:
            imgs.append(image.name)
        return imgs


    def get_group_images(self, auth, groupId):
        if groupId is None:
            return {}
        ent = auth.get_entity(groupId)
        if ent is not None:
            child_ents = auth.get_entities(to_unicode(constants.IMAGE), parent=ent)
            ids = [child_ent.entity_id for child_ent in child_ents]
            images= DBHelper().filterby(Image,[],[Image.id.in_(ids)])
            result = {}
            for image in images:
                result[image.id] = image
            return result
        return {}

    #pass
    def get_image_groups(self, auth, storeId=None):
        ent = auth.get_entity(storeId)
        result = {}
        img_store_ents = auth.get_entities(to_unicode(constants.IMAGE_STORE), parent=ent)
        if img_store_ents:
            temp_grp_ents = [temp_grp_ent for img_store_ent in img_store_ents for temp_grp_ent in auth.get_entities(to_unicode(constants.IMAGE_GROUP),parent=img_store_ent)]
            #temp_grp_ents = [temp_grp_ent for temp_grp_ent in [img_store_ent  for img_store_ent in  auth.get_entities(to_unicode(constants.IMAGE_GROUP),parent=ent)]]
        else:
            temp_grp_ents = auth.get_entities(to_unicode(constants.IMAGE_GROUP),parent=ent)
        ids = [temp_grp_ent.entity_id for temp_grp_ent in temp_grp_ents]
        img_grps = DBHelper().filterby(ImageGroup,[],[ImageGroup.id.in_(ids)])
        
        for image_group in img_grps:
            result[image_group.id] = image_group
        return result

    @classmethod
    def get_image_group(self, auth, groupId):
        if groupId is None:
            return None
        ent = auth.get_entity(groupId)
        if ent is not None:
            return DBHelper().find_by_id(ImageGroup, groupId)
        return None


    def transfer_image(self, auth, imageId, source_groupId, dest_groupId):
        ent = auth.get_entity(imageId)
        grp = auth.get_entity(dest_groupId)
        if not auth.has_privilege('TRANSFER_IMAGE', ent) or not auth.has_privilege('CREATE_IMAGE', grp):
            raise Exception(constants.NO_PRIVILEGE)
        self.transfer_image_cloud_side_operations(auth, imageId, source_groupId, dest_groupId)
        auth.update_entity(ent, parent=grp)

    def transfer_image_cloud_side_operations(self, auth, imageId, source_groupId, dest_groupId):
        try:
            #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEP, CSEPRegion
            ent = auth.get_entity(imageId)
            if not auth.has_privilege('TRANSFER_IMAGE', ent):
                raise Exception(constants.NO_PRIVILEGE)
            cseps = self.get_cseps_by_image_group(imagegroup_id=source_groupId)
            dest_group = DBHelper().find_by_id(ImageGroup, dest_groupId)
            vms_names_lst = []
            for csep in cseps:
                vms = csep.get_all_vms_by_image_id(imageId)
                if len(vms):
                    vms_names_lst.extend([vm.name for vm in vms])
                    continue
            if len(vms_names_lst):
                msg = 'Image:%s is used by Cloud Virtual Machine(s): %s' % (ent.name, ', '.join(vms_names_lst))
                print msg
                LOGGER.info(msg)
                raise Exception('Can not move Image:%s. Cloud Virtual Machine(s) provisioned from this Image exists.' % ent.name)
        
            else:
                for csep in cseps:
                    if dest_groupId in [temp_gp.id for temp_gp in csep.get_template_groups_from_default_region()]:
                        msg = 'Destination imagegroup:%s is also part of CSEP:%s' %(dest_group.name,csep.name)
                        print msg
                        LOGGER.info(msg)
                    else:
            
                        cp = csep.get_provider()
                        if cp:
                            for vdc in cp.get_vdcs():
                                self.delete_image_from_cloud(auth, imageId, cp, vdc)
        except Exception as ex:
            traceback.print_exc()
            raise ex

    #tianfeng
    def clone_image(self, auth, image_group_id, imageId, new_image_name):
        msg = ''
        new_image_id = ''
        ent = auth.get_entity(imageId)
        imggrp_ent = auth.get_entity(image_group_id)
        if imggrp_ent is None:
            raise Exception('Can not find the Template Group:' + image_group_id)
        if ent is not None:
            if not auth.has_privilege('CREATE_LIKE', ent):
                raise Exception(constants.NO_PRIVILEGE)
    
            if re.sub(ImageStore.INVALID_CHARS_EXP, '', new_image_name) != new_image_name:
                raise Exception('Template name can not contain special chars %s' % ImageStore.INVALID_CHARS)
            if new_image_name == '':
                raise Exception('Template name can not blank')
            try:
                imgs = DBHelper().filterby(Image, [], [Image.name == new_image_name])
                if len(imgs) > 0:
                    raise Exception('Template %s already exists.' % new_image_name)
                else:
                    image = DBHelper().find_by_id(Image, imageId)
                    vm_config,image_config = image.get_configs()
                    src_location = image.get_location()
                    msg += '\n'+ "Cloning Template '%s'" %image.name
                    self._clone_image(auth,image,vm_config,image_config,new_image_name)
                    msg += '\n' + "Creating Template '%s'" % new_image_name
                    new_img = self.create_image_instance(new_image_name, image.get_platform())
                    new_image_id = new_img.id
                    dest_location = new_img.get_location()
                    self.image_copytree(src_location, dest_location)
                    str_vm_config = ''
                    vm_config,image_config = image.get_configs()
                    for name,value in vm_config.options.iteritems():
                        if name == 'image_name':
                            value = to_str(new_img.name)
                        str_vm_config += '%s = %s\n' % (name, repr(value))
                    new_img.vm_config = str_vm_config
                    new_img.image_config = get_config_text(image_config)
                    new_img.os_name = image.get_os_name()
                    new_img.os_flavor = image.get_os_flavor()
                    new_img.os_version = image.get_os_version()
                    new_img.allow_backup = image.is_allow_backup()
                    new_img.version = constants.image_starting_version
                    new_img.prev_version_imgid = new_image_id
                    auth.add_entity(new_img.name, new_image_id, to_unicode(constants.IMAGE), imggrp_ent)
                    DBHelper().add(new_img)
                    msg += '\n' + "Template '%s' cloned successfully" %image.name
                    import transaction
                    transaction.commit()
            except Exception as e:
                traceback.print_exc()
                msg += '\n' + to_str(e)
                raise Exception(e)
            return msg,new_image_id


    def rename_image(self, auth, image_group_id, imageId, new_image_name):
        #from stackone.cloud.DbModel.platforms.cms.CMSCloudProvider import CMSTemplates
        #from stackone.cloud.DbModel.platforms.cms.CMSAccountTemplate import CMSAccountTemplate
        ent = auth.get_entity(imageId)
        if ent is not None:
            if not auth.has_privilege('RENAME_IMAGE', ent):
                raise Exception(constants.NO_PRIVILEGE)
            if re.sub(ImageStore.INVALID_CHARS_EXP, '', new_image_name) != new_image_name:
                raise Exception('Template name can not contain special chars %s' % ImageStore.INVALID_CHARS)
            if new_image_name == '':
                raise Exception('Template name can not blank')
            try:
                imgs = DBHelper().filterby(Image, [], [Image.name == new_image_name])
                if len(imgs) > 0:
                    raise Exception('Template %s already exists.' % new_image_name)
                image = DBHelper().find_by_id(Image, imageId)
                image.set_name(new_image_name)
                auth.update_entity(ent, name=new_image_name)
                DBHelper().add(image)
                cms_acc_temp_qry = DBSession.query(CMSAccountTemplate).filter(CMSAccountTemplate.image_id == imageId).first()
                if cms_acc_temp_qry:
                    cms_acc_temp_qry.name = new_image_name
                    DBSession.add(cms_acc_temp_qry)
                    ccpid = DBSession.query(CMSAccountTemplate.cloud_template_id).filter(CMSAccountTemplate.image_id == imageId).first()
                    if ccpid:
                        cmstemp = DBSession.query(CMSTemplates).filter(CMSTemplates.id == ccpid[0]).first()
                        cmstemp.name = new_image_name
                        DBSession.add(cmstemp)
            except Exception as e:
                raise e
            return image

    #pass
    def create_image(self, auth, groupId, new_image_name, platform, id=None):
        ent = auth.get_entity(groupId)
        image = None
        if ent is not None:
            if not auth.has_privilege('CREATE_IMAGE', ent):
                raise Exception(constants.NO_PRIVILEGE)
            try:
                imgs = DBHelper().filterby(Image, [], [Image.name == new_image_name])
                if len(imgs) > 0:
                    raise Exception('Template %s already exists.' % new_image_name)
                
                image = self.create_image_instance(new_image_name, platform, id)
                auth.add_entity(image.name, image.id, to_unicode(constants.IMAGE), ent)
                DBHelper().add(image)
            except Exception as e:
                traceback.print_exc()
                raise e
            return image


    def delete_image_from_cloud(self, auth, imageId, cp, vdc):
        #from stackone.cloud.DbModel.platforms.cms.CSEP import TemplateContextRelation
        #from stackone.cloud.DbModel.VDC import VDC
        #from stackone.cloud.DbModel.platforms.cms.CMSCloudProvider import CMSTemplates
        #from stackone.cloud.DbModel.platforms.cms.CMSAccountTemplate import CMSAccountTemplate
        #from stackone.cloud.DbModel.Account import VDCTemplates
        from stackone.model.Entity import EntityContext
        try:
            ent = auth.get_entity(imageId)
            if ent is not None:
                if not auth.has_privilege('REMOVE_IMAGE', ent):
                    raise Exception(constants.NO_PRIVILEGE)
                entity_context = EntityContext.get_entity_context(dict(context1 = vdc.id,context2 = cp.id,context3 = None,context4 = None,context5 = None))
                if not entity_context:
                    msg = 'Could not find entity context with context1:%s, context2:%s' (vdc.id,cp.id)
                    print msg
                    LOGGER.info(msg)
                else:
                    temp_cnt_rels_qry = DBSession.query(TemplateContextRelation).filter(TemplateContextRelation.context_id == entity_context.id).filter(TemplateContextRelation.image_id == imageId)
                    temp_cnt_rels = temp_cnt_rels_qry.all()
                    
                    if not len(temp_cnt_rels):
                        msg = 'Image:%s has not attached to any VDCs' %ent.name
                        print msg
                        LOGGER.info(msg)
            
                    else:
                        account = vdc.get_account()
                        cms_acc_temp_qry = DBSession.query(CMSAccountTemplate).filter(CMSAccountTemplate.account_id == account.id).filter(CMSAccountTemplate.image_id == imageId)
                        cms_acc_temp_ids = [temp.id for temp in cms_acc_temp_qry.all()]
                        DBSession.query(VDCTemplates).filter(VDCTemplates.account_id == account.id).filter(VDCTemplates.vdc_id == vdc.id).filter(VDCTemplates.template_id.in_(cms_acc_temp_ids)).delete()
                        cms_acc_temp_qry.delete()
                        temp_cnt_rels_qry.delete()
                        msg = 'Image:%s successfully deleted from TemplateContext, VDC:%s' %(ent.name,vdc.name)
                        print msg
                        LOGGER.info(msg)
                    DBSession.query(CMSTemplates).filter(CMSTemplates.provider_id == cp.id).filter(CMSTemplates.image_id == imageId).delete()
                    msg = 'Image:%s successfully deleted from Cloud Provider:%s' %(ent.name,cp.name)
                    print msg
                    LOGGER.info(msg)
        except Exception as ex:
            traceback.print_exc()
            raise ex
    ###tianfeng 20121214
    def delete_sub_template(self,auth,imageId):
        #from stackone.cloud.DbModel.platforms.cms.CMSCloudProvider import CMSTemplates
        #from stackone.cloud.DbModel.platforms.cms.CMSAccountTemplate import CMSAccountTemplate
        cms_acc_temp_qry = DBSession.query(CMSAccountTemplate).filter(CMSAccountTemplate.image_id == imageId)
        ccpid = DBSession.query(CMSAccountTemplate.cloud_template_id).filter(CMSAccountTemplate.image_id == imageId).first()
        print ccpid,'###########ccpid###############'
        if cms_acc_temp_qry.first():
            new_image_id = cms_acc_temp_qry.first().id
            print new_image_id,'#######niew_image_id'
            cms_acc_temp_qry.delete()
            ent1 = auth.get_entity(new_image_id)
            auth.remove_entity(ent1)
            if ccpid:
                DBSession.query(CMSTemplates).filter(CMSTemplates.id == ccpid[0]).delete()
    def delete_image_completely_from_cloud(self, auth, imageId):
        #from stackone.cloud.DbModel.platforms.cms.CSEP import TemplateContextRelation
        #from stackone.cloud.DbModel.VDC import VDC
        #from stackone.cloud.DbModel.platforms.cms.CMSCloudProvider import CMSTemplates
        #from stackone.cloud.DbModel.platforms.cms.CMSAccountTemplate import CMSAccountTemplate
        #from stackone.cloud.DbModel.Account import VDCTemplates
        try:
            ent = auth.get_entity(imageId)
            if ent is not None:
                if not auth.has_privilege('REMOVE_IMAGE', ent):
                    raise Exception(constants.NO_PRIVILEGE)
                temp_cnt_rels_qry = DBSession.query(TemplateContextRelation).filter(TemplateContextRelation.image_id == imageId)
                temp_cnt_rels = temp_cnt_rels_qry.all()
                if not len(temp_cnt_rels):
                    msg = 'Image:%s has not attached to any VDCs' % ent.name
                    print msg
                    LOGGER.info(msg)
                    #tianfeng
                    self.delete_sub_template(auth, imageId)

                else:
                    vdc_ids = [tcr.context.context1 for tcr in temp_cnt_rels]
                    vdcs = DBSession.query(VDC).filter(VDC.id.in_(vdc_ids)).all()
                    print '\n------vdc_ids-------', vdc_ids
                    vdc_names = [vdc.name for vdc in vdcs]
                    msg = 'Image:%s is used by Virtual Datacenter(s): %s' %(ent.name,', '.join(vdc_names))
                    print msg
                    LOGGER.info(msg)
                    cms_acc_temp_qry = DBSession.query(CMSAccountTemplate).filter(CMSAccountTemplate.image_id == imageId)
                    cms_acc_temp_ids = [temp.id  for temp in cms_acc_temp_qry.all()]
                    DBSession.query(VDCTemplates).filter(VDCTemplates.template_id.in_(cms_acc_temp_ids)).delete()
                    cms_acc_temp_qry.delete()
                    temp_cnt_rels_qry.delete()
                    msg = 'Image:%s successfully deleted from all TemplateContex VDCs' %ent.name
                    print msg
                    LOGGER.info(msg)
                DBSession.query(CMSTemplates).filter(CMSTemplates.image_id == imageId).delete()
                msg = 'Image:%s successfully deleted from all Cloud Providers' %ent.name
                print msg
                LOGGER.info(msg)
        except Exception as ex:
            traceback.print_exc()
            raise ex
    def delete_image(self, auth, image_group_id, imageId):
        try:
            msg = ''
            image = DBHelper().find_by_id(Image,imageId)
            img_location = image.get_location()
            msg = self.template_delete(auth, image_group_id, imageId)
            if os.path.exists(img_location):
                shutil.rmtree(img_location)
        except Exception,ex:
            traceback.print_exc()
            msg += '\n'+to_str(ex)
            raise Exception(msg)
        return msg
            
#    def delete_image(self, auth, image_group_id, imageId):
#        ent = auth.get_entity(imageId)
#        if ent is not None:
#            if not auth.has_privilege('REMOVE_IMAGE', ent):
#                raise Exception(constants.NO_PRIVILEGE)            
#            
#            vms = DBHelper().filterby(VM, [], [VM.image_id == imageId])
#            if len(vms):
#                vms_names = [vm.name for vm in vms]
#                msg = 'Image:%s is used by Virtual Machine(s): %s' %(ent.name,', '.join(vms_names))
#                print msg
#                LOGGER.info(msg)
#                raise Exception('Can not delete Template, ' + ent.name + '. VMs provisioned from this Template exists.')
#            
#            self.delete_image_completely_from_cloud(auth, imageId)
#            image = DBHelper().find_by_id(Image, imageId)
#            img_location = image.get_location()
#            if os.path.exists(img_location):
#                shutil.rmtree(img_location)
#            auth.remove_entity(ent)
#            DBHelper().delete_all(Image, [], [Image.prev_version_imgid == imageId])


    def image_exists_by_name(self, name):
        imgs = DBHelper().filterby(Image, [], [Image.name == name])
        if len(imgs) > 0:
            return True
        return False


    def save_image_desc(self, auth, mgd_node, imageId, content):
        ent = auth.get_entity(imageId)
        if not auth.has_privilege('EDIT_IMAGE_DESCRIPTION', ent):
            raise Exception(constants.NO_PRIVILEGE)
        image = DBHelper().find_by_id(Image, imageId)
        filename = image.get_image_desc_html()
        file = mgd_node.node_proxy.open(filename, 'w')
        file.write(content)
        file.close()


    def save_image_script(self, auth, mgd_node, imageId, content):
        ent = auth.get_entity(imageId)
        if not auth.has_privilege('EDIT_IMAGE_SCRIPT', ent):
            raise Exception(constants.NO_PRIVILEGE)
        image = DBHelper().find_by_id(Image, imageId)
        filename = image.get_provisioning_script()
        file = mgd_node.node_proxy.open(filename, 'w')
        file.write(content)
        file.close()


    def list(self):
        return self.images

    def get_remote_location(self, managed_node):
        store_location = managed_node.config.get(prop_image_store)
        if store_location is None or store_location is '':
            store_location = ImageStore.DEFAULT_STORE_LOCATION
        return store_location

    def get_store_location(self):
        return self._store_location

    def get_common_dir(self):
        return os.path.join(self._store_location, self.COMMON_DIR)

    def add_group(self, auth, group, storeId, csep_context=None):
        ent = auth.get_entity(storeId)
        if not auth.has_privilege('ADD_IMAGE_GROUP', ent):
            raise Exception(constants.NO_PRIVILEGE)
        try:
            grps = DBHelper().filterby(ImageGroup, [], [ImageGroup.name == group.name])
            if len(grps) > 0:
                raise Exception('TemplateGroup %s already exists.' % group.name)
            auth.add_entity(group.name, group.id, to_unicode(constants.IMAGE_GROUP), ent, csep_context=csep_context)
            DBHelper().add(group)
            return group.id
        except Exception as e:
            raise e


    def get_cseps_by_image_group(self, imagegroup_id=None, imagegroup=None):
        #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEP, CSEPRegion
        if not imagegroup:
            if not imagegroup_id:
                raise Exception('imagegroup_id should not be None')
            imagegroup = DBHelper().find_by_id(ImageGroup, imagegroup_id)
        cseps = DBSession.query(CSEP).join((CSEPRegion, CSEPRegion.service_point_id == CSEP.id)).filter(CSEPRegion.template_groups.contains(imagegroup)).all()
        return cseps


    def delete_group(self, auth, groupId):
        #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEPContext
        #from stackone.cloud.DbModel.VDC import VDC
        ent = auth.get_entity(groupId)
        if ent is not None:
            if not auth.has_privilege('REMOVE_IMAGE_GROUP', ent):
                raise Exception(constants.NO_PRIVILEGE)
            group = DBHelper().find_by_id(ImageGroup, groupId)
            cseps = self.get_cseps_by_image_group(imagegroup=group)
            if len(cseps):
                raise Exception('Can not remove Image Group: %s, this is part of Cloud Provider' % ent.name)
            if not auth.is_csep_user():
                if ent.csep_context_id:
                    csep_context = CSEPContext.get_csep_context_by_id(ent.csep_context_id)
                    if not csep_context:
                        msg = 'Could not find csep context for csep_context_id:%s' % ent.csep_context_id
                        print msg
                        LOGGER.info(msg)
                    else:
                        vdc = VDC.get_vdc_by_id(csep_context.vdc_id)
                        if not vdc:
                            msg = 'Could not find Virtual Datacenter, ID:%s' % csep_context.vdc_id
                            print msg
                            LOGGER.error(msg)
                        else:
                            raise Exception('Can not remove Image Group: %s, this is part of Virtual Datacenter: %s.' % (ent.name, vdc.name))
            child_ents = auth.get_entities(to_unicode(constants.IMAGE), parent=ent)
            ids = [child_ent.entity_id for child_ent in child_ents]
            for child_ent in child_ents:
                auth.remove_entity(child_ent)
            auth.remove_entity(ent)
            DBHelper().delete_all(Image, [], [Image.id.in_(ids)])
            DBHelper().delete(group)


    def rename_image_group(self, auth, groupId, new_image_group_name):
        ent = auth.get_entity(groupId)
        if ent is not None:
            if not auth.has_privilege('RENAME_IMAGE_GROUP', ent):
                raise Exception(constants.NO_PRIVILEGE)
            try:
                grps = DBHelper().filterby(ImageGroup, [], [ImageGroup.name == new_image_group_name])
                if len(grps) > 0:
                    raise Exception('TemplateGroup %s already exists.' % new_image_group_name)
                group = DBHelper().find_by_id(ImageGroup, groupId)
                auth.update_entity(ent, name=new_image_group_name)
                group.set_name(new_image_group_name)
                DBHelper().add(group)
                return group
            except Exception as e:
                raise e


    def prepare_env(self, managed_node, image, domconfig, image_conf):
        remote_image_store = managed_node.config.get(prop_image_store)
        if remote_image_store is None:
            remote_image_store = self.DEFAULT_STORE_LOCATION
        scripts_dest = os.path.join(remote_image_store, image.base_location)
        common_dest = os.path.join(remote_image_store, self.COMMON_DIR)
        local_image_store = self.get_store_location()
        scripts_src_dir = image.get_provisioning_script_dir()
        common_src = self.get_common_dir()
        copyToRemote(common_src, managed_node, remote_image_store, hashexcludes=self._hashexcludes)
        copyToRemote(scripts_src_dir, managed_node, remote_image_store, hashexcludes=self._hashexcludes)
        log_dir = managed_node.config.get(prop_log_dir)
        if log_dir is None or log_dir == '':
            log_dir = DEFAULT_LOG_DIR
        log_location = os.path.join(log_dir, 'image_store', image.base_location)
        mkdir2(managed_node, log_location)
        img_conf_filename = None
        name = domconfig['name']
        if image_conf is not None:
            img_conf_base = image.get_image_filename(name)
            img_conf_filename = os.path.join(log_location, img_conf_base)
            image_conf.set_managed_node(managed_node)
            image_conf.save(img_conf_filename)
        return (remote_image_store, scripts_dest, img_conf_filename, log_location)

        

    def execute_provisioning_script(self, auth, managed_node, image_id, dom_config, image_conf):
        external_id = None
        image = self.get_image(auth, image_id)
        image_platform = image.get_platform()
        node_platform = managed_node.get_platform()
        if image_platform != node_platform and not image.is_hvm():
            raise Exception('Image platform (%s) and Server Platform (%s) mismatch.' % (image_platform, node_platform))
        name = dom_config['name']
        image_store_location,script_location,img_conf_filename,log_location = self.prepare_env(managed_node, image, dom_config, image_conf)
        script_name = image.SCRIPT_NAME
        script = os.path.join(script_location, script_name)
        script_args_filename = os.path.join(log_location, image.get_args_filename(name))
        args = managed_node.node_proxy.open(script_args_filename, 'w')
        args.close()
        dom_config['image_conf'] = img_conf_filename
        dom_config.write()
        log_file_base = image.get_log_filename(name)
        log_filename = os.path.join(log_location, log_file_base)
        script_args = ' -x ' + dom_config.filename + ' -p ' + script_args_filename + ' -s ' + image_store_location + ' -i ' + image.base_location + ' -l ' + log_filename + ' -c ' + img_conf_filename
        cmd = script + script_args
        provision_timeout = self.get_provision_timeout(dom_config, image_conf)
        out,exit_code = managed_node.node_proxy.exec_cmd(cmd, timeout=provision_timeout)
        return (out, exit_code, log_filename,external_id)

        

    def get_provision_timeout(self, dom_config, image_conf):
        provision_timeout = 60
        ref_provision_timeout = 0
        try:
            for disk in dom_config['disk']:
                disk_val = disk.split(',')
                disk_image_src_var = disk_val[1] + '_image_src'
                disk_image_src_type_var = disk_val[1] + '_image_src_type'
                if image_conf[disk_image_src_var] is not None and image_conf[disk_image_src_type_var] is not None:
                    try:
                        ref_provision_timeout = int(tg.config.get('larger_timeout'))
                    except Exception as e:
                        print 'Exception: ',
                        print e
                    break
                continue
            if 'provision_timeout' in dom_config.keys():
                try:
                    provision_timeout = int(dom_config['provision_timeout'])
                except Exception as e:
                    print 'Exception: ',
                    print e
            if provision_timeout < ref_provision_timeout:
                provision_timeout = ref_provision_timeout
        except Exception as e:
            traceback.print_exc()
        return provision_timeout
    #pass
    def create_image_instance(self, name, platform, id=None, location=None, is_template=False):
        image = None
        if platform in [constants.PLT_XEN]:
            image = self.create_xen_image(name, platform, id, location, is_template)
        elif platform in [constants.PLT_KVM]:
            image = self.create_kvm_image(name, platform, id, location, is_template)
        elif platform in [constants.PLT_VMW]:
            image = self.create_vmw_image(name, platform, id, location)
        elif platform in [constants.VCENTER]:
            image = self.create_vcenter_image(name, platform, id)
        return image
    ########pass
    def create_xen_image(self, name, platform, id=None, location=None, is_template=False):
        if not id:
            id = getHexID(name, [constants.IMAGE])
        if not location:
            location = self._get_location(name)
        return XenImage(id=id, platform=platform, name=name, location=location, is_template=is_template)
    #pass
    def create_kvm_image(self, name, platform, id=None, location=None, is_template=False):
        if not id:
            id = getHexID(name, [constants.IMAGE])
        if not location:
            location = self._get_location(name)
        return KvmImage(id=id, platform=platform, name=name, location=location, is_template=is_template)
    #pass
    def create_vmw_image(self, name, platform, id=None, location=None):
        if not id:
            id = getHexID(name, [constants.IMAGE])
        try:
            if not location:
                location = self._get_location(name)
        except Exception as e:
            print 'Exception getting location of vmw image: ',
            print e
        return VmwImage(id=id, platform=platform, name=name, location=location)

    #pass
    def create_vcenter_image(self, name, platform, id=None):
        if not id:
            id = getHexID(name, [constants.IMAGE])
        return VcenterImage(id=id, platform=platform, name=name, location=None)
    #tianfeng
    def create_image_group(self, name, images=None, id=None):
        if not images:
            images = {}
        if not id:
            id = getHexID(name, [constants.IMAGE_GROUP])
        return ImageGroup(id=id, name=name, images=images)
    #pass
    def create_vcenter_image_group(self, name, images=None, id=None):
        if not images:
            images = {}
        if not id:
            id = getHexID(name, [constants.IMAGE_GROUP])
        return VcenterImageGroup(id=id, name=name, images=images)
    #pass
    def create_vcenter_templateLib(self, registry, TemplateLibrary_Name):
        locn = tg.config.get(constants.prop_image_store)
        image_store_location = to_unicode(os.path.abspath(locn))
        vimage_store = VcenterImageStore(registry)
        vimage_store.name = TemplateLibrary_Name
        vimage_store.location = image_store_location
        vimage_store._store_location = image_store_location
        vimage_store.id = getHexID()
        return vimage_store
    #pass
    def get_platform(self):
        platform = self.type
        if platform != 'None' and platform:
            return platform
        return constants.GENERIC
    #pass
    def create_image_from_vm(self, auth, node_id, image_name, image_group_id, context, task_id, dom_image):
        return self.save_image_from_vm(auth, node_id, image_name, image_group_id, context, task_id, dom_image)
Index('imgstr_name', ImageStore.name)
import sys
def get_template_location():
    path,tfile = get_path('appliance', ['stackone/core'])
    if path:
        return tfile
    else:
        msg = "ERROR: Couldn't find appliance_template. This is mostly installation problem."
        print msg
        raise Exception(msg)


import string
class ImageUtils():
    compressed_ext = ['.zip', '.gz']
    APPLIANCE_TEMPLATE_LOCATION = get_template_location()
    
    @classmethod
    def set_registry(cls, registry):
        cls.registry = registry
    @classmethod
    def download_appliance(cls, local, appliance_url, image_dir, filename=None,progress =  None):
        if appliance_url[0] == '/' :
            appliance_url = "file://" + appliance_url

        if appliance_url.find("file://") == 0:
            file_cp = True
            msg = "Copying"
        else:
            file_cp = False
            msg = "Downloading"

        fd = None
        # Tweaks to get around absence of filename and size
        try:
            opener = urllib2.build_opener()
            req = urllib2.Request(appliance_url)
            req.add_header("User-Agent", fox_header)
            fd = opener.open(req)
            url = fd.geturl()
            path = urlparse.urlparse(urllib.url2pathname(url))[2]
            if not filename:
                filename = path.split('/')[-1]

            clen = fd.info().get("Content-Length")
            if clen is not None:
                content_len = int(clen)
            else:
                content_len = -1


            print url, filename, content_len
            ex = None
            download_file = os.path.join(image_dir, filename)
            if not local.node_proxy.file_exists(download_file):
                if file_cp:
                    try:
                        try:
                            src = path
                            dest = download_file
                            if progress:
                                progress.update(progress.START_PULSE,
                                                "Copying " + src +
                                                " to \n" + dest )  
                            if src.find("/dev/") == 0 or \
                                    dest.find("/dev/") == 0:
                                
                                (out, code) = local.node_proxy.exec_cmd("dd if=" + \
                                                                      src + \
                                                                      " of=" + \
                                                                       dest,timeout=get_template_timeout())
                            else:

                                (out, code) = local.node_proxy.exec_cmd("cp -a " + \
                                                                      src + \
                                                                      " " + \
                                                                      dest,timeout=get_template_timeout())
                            if code != 0:
                                raise Exception(out)

                            if progress and not progress.continue_op():
                                raise Exception("Canceled by user.")

                        except Exception, ex:
                            traceback.print_exc()
                            if progress:
                                progress.update(progress.CANCELED,to_str(ex))
                            raise
                    finally:
                        if progress and not ex:
                            progress.update(progress.STOP_PULSE, "Copying done")
                        if progress and not progress.continue_op():
                            local.node_proxy.remove(download_file)
                        
                else: # url download
                    df = None
                    try:
                        df = open(download_file,"wb")
                        chunk_size = 1024 * 64
                        chunks = content_len / chunk_size + 1
                        x = fd.read(chunk_size)
                        c = 1
                        p = 1.0 / chunks
                        if progress:
                            progress.update(progress.SET_FRACTION,
                                            msg,(p * c))
                        while  x is not None and x != "":
                            df.write(x)
                            #print "wrote ", c, chunks, p * c
                            if progress:
                                progress.update(progress.SET_FRACTION, None,(p * c))
                                if not progress.continue_op():
                                    raise Exception("Canceled by user.") 

                            c = c + 1
                            x = fd.read(chunk_size)
                    finally:
                        if df:
                            df.close()
                        if progress and not progress.continue_op():
                            local.node_proxy.remove(download_file)
        finally:
            if fd:
                fd.close()

        return download_file

    @classmethod
    def get_file_ext(cls, filename):
        # return filename and ext
        file = filename
        dot_index = filename.rfind(".")
        ext = ""
        if dot_index > -1:
            ext = filename[dot_index:]
            file = filename[:dot_index]

        return (file, ext)

    @classmethod
    def open_package(cls, local, downloaded_filename, image_dir, progress=None):
        uzip = None
        utar = None

        (f, e) = ImageUtils.get_file_ext(downloaded_filename)
        if e in cls.compressed_ext:
            if e == ".gz":
                uzip = "gunzip -f"
            elif e == ".zip":
                uzip = "unzip -o -d " + image_dir

        if uzip:
            if progress:
                progress.update(progress.START_PULSE, "Unzipping " + downloaded_filename)
            msg = None
            ex = None
            try:
                try:
                    (output, code) = local.node_proxy.exec_cmd(uzip + " " + \
                                            downloaded_filename,timeout=get_template_timeout())
                    if code != 0 :
                        msg = "Error unzipping " + \
                              downloaded_filename + ":" + \
                              output
                        print msg
                        raise Exception(msg)

                    if e == ".zip":
                        local.node_proxy.remove(downloaded_filename)

                    if progress and not progress.continue_op():
                        raise Exception("Canceled by user.")
                    
                except Exception, ex:
                    if progress:
                        progress.update(progress.CANCELED,to_str(ex))
                    raise
            finally:
                if progress and not ex:
                    progress.update(progress.STOP_PULSE, "Unzipping done")
            
        # untar if required
        if downloaded_filename.find(".tar") > -1:
            ex = None
            untar = "tar xvf "
            msg = None

            try:
                try:
                    tar_file = downloaded_filename[0:downloaded_filename.find(".tar") + 4]
                    tar_loc = os.path.dirname(tar_file)
                    if progress:
                        progress.update(progress.START_PULSE,
                                        "Opening archive " + tar_file)
                    (output, code) = local.node_proxy.exec_cmd(untar + " " +
                                                               tar_file +
                                                               " -C " +
                                                               tar_loc,timeout=get_template_timeout())
                    if code != 0:
                        print "Error untaring ", tar_file
                        raise Exception("Error untaring " +  tar_file + " " +
                                        output)
                
                    if progress and not progress.continue_op():
                        raise Exception("Canceled by user.")
                
                except Exception, ex:
                    if progress:
                        progress.update(progress.CANCELED,to_str(ex))
                    raise
                
            finally:
                if progress and not ex:
                    progress.update(progress.STOP_PULSE,"Opening archive done.")


    @classmethod
    def get_vm_conf_template(cls, node, appliance_entry, cfg,disk_info):
        appliance_base = cls.APPLIANCE_TEMPLATE_LOCATION
        platform = cls.get_platform(appliance_entry)
        p = cls.registry.get_platform_object(platform)
        vm_template_file = p.select_vm_template(appliance_base,
                                                platform,
                                                appliance_entry,
                                                cfg)
        vm_template = p.create_vm_config(filename=vm_template_file)
        vm_template.dump()
        value_map = {"MEMORY" : 256,
                     "VCPUS" : 1,
                     "RAMDISK" : '',
                     "EXTRA" : '',
                     "KERNEL" : ''
                     }

        default_cfg = {}
        default_cfg["memory"] = 256
        default_cfg["vcpus"] = 1


        if cfg is not None:
            value_map["MEMORY"] = cfg.get("memory") or default_cfg["memory"]
            value_map["VCPUS"] = cfg.get("vcpus") or default_cfg["vcpus"]
            value_map["RAMDISK"] = ""
            if cfg.get("extra") :
                value_map["EXTRA"] = cfg.get("extra")
            else:
                value_map["EXTRA"] = ""

                
        if appliance_entry.get("is_hvm") and \
               to_str(appliance_entry["is_hvm"]).lower() == "true" :
            pass
            ### Taken care by the hvm template now.
            ### Still issue of computed kernel is tricky to fix.
##             value_map["BOOT_LOADER"]=""
                                
##             vm_template["vnc"] = 1
##             vm_template["sdl"] = 0
##             vm_template["builder"] = "hvm"
##             # special handing for these :Kludge
##             vm_template.lines.append('device_model="/usr/" + arch_libdir + "/xen/bin/qemu-dm"\n')
##             del vm_template["kernel"]
##             vm_template.lines.append('kernel="/usr/" + arch_libdir + "/xen/boot/hvmloader"')
##             # make it a customizable option
##             computed_options = vm_template.get_computed_options()
##             computed_options.append("kernel")
##             computed_options.append("device_model")
##             vm_template.set_computed_options(computed_options)
        else:
            value_map["BOOT_LOADER"]="/usr/bin/pygrub"
            value_map["KERNEL"] = ""

        disks_directive = []
        # now lets generate the disk entries
        for di in disk_info:
            de, dpes = di
            (proto, device, mode) = de

            disk_entry = proto + "$VM_DISKS_DIR" + "/$VM_NAME." + device+ \
                         ".disk.xm"
            disk_entry += "," + device+ ","  + mode
            
            disks_directive.append(disk_entry)

        vm_template["disk"] = disks_directive
        if appliance_entry.get("provider_id"):
            vm_template["provider_id"] = appliance_entry.get("provider_id")

        vm_template.instantiate_config(value_map)
        
        # Add the defaults if not already set
        for k in default_cfg:
            if not vm_template.has_key(k):
                if cfg and cfg.get(k):
                    vm_template[k] = cfg[k]
                else:
                    vm_template[k] = default_cfg[k]
                
        return vm_template
    @classmethod
    def get_platform(cls, appliance_entry):
        platform = appliance_entry.get("platform")
        if platform:
            platform =  platform.lower()
        return platform

    @classmethod
    def get_image_config(cls, node, appliance_entry, disk_info, image_dir):
        appliance_base = cls.APPLIANCE_TEMPLATE_LOCATION
        platform = cls.get_platform(appliance_entry)
        p = cls.registry.get_platform_object(platform)
        image_conf_template_file = p.select_image_conf_template(appliance_base,
                                                                platform,
                                                                appliance_entry)
        image_conf_template =p.create_image_config(filename=image_conf_template_file)
                                 
        disks = []
        ndx = 0
        for di in disk_info:
            de, dpes = di
            (proto,device, mode) = de

            for dpe in dpes:
                dpe_name, dpe_val = dpe
                image_conf_template[dpe_name] = dpe_val

            # adjust the dev_image_src in the template form
            src = image_conf_template.get(device + "_image_src")
            if src:
                pos = src.find(image_dir)
                if pos == 0 :
                    src = '$IMAGE_STORE/$IMAGE_LOCATION/' + \
                          src[(len(image_dir) + 1):]
                    image_conf_template[device + "_image_src"] = src

        return image_conf_template
    @classmethod
    def create_files(cls, local, appliance_entry, image_store, image_group_id,image, vm_template, image_conf, force):
        vm_conf_file =image.get_vm_template()
        image_conf_file =image.get_image_conf()
        prov_script = image.get_provisioning_script()
        desc_file = image.get_image_desc_html()
        
        image.vm_config=get_config_text(vm_template)
        image.image_config=get_config_text(image_conf)
        image.version=constants.image_starting_version
        image.prev_version_imgid=image.id
        image.os_flavor=vm_template.get('os_flavor')
        image.os_name=vm_template.get('os_name')
        image.os_version=vm_template.get('os_version')
        image.allow_backup = True
        DBHelper().add(image)
        
        if force or not local.node_proxy.file_exists(vm_conf_file):
            vm_template.save(vm_conf_file)
            print "Created ", vm_conf_file
        if force or  not local.node_proxy.file_exists(image_conf_file):  
            image_conf.save(image_conf_file)
            print "Created ", image_conf_file
        if force or  not local.node_proxy.file_exists(prov_script):
            platform = cls.get_platform(appliance_entry)
            p = cls.registry.get_platform_object(platform)
            a_base = cls.APPLIANCE_TEMPLATE_LOCATION
            src_script = p.select_provisioning_script(a_base,
                                                      platform,
                                                      appliance_entry)
            shutil.copy(src_script, prov_script)
            print "Created ", prov_script
        if force or  not local.node_proxy.file_exists(desc_file):
            cls.create_description(local, image_store, image,
                                   appliance_entry)
    @classmethod
    def create_description(cls, local,\
                           image_store,image, appliance_entry,\
                           desc_meta_template=None,html_desc_meta_template=None):
        # basically read the template, instantiate it and write it
        # as desc file.
        platform = cls.get_platform(appliance_entry)
        p = cls.registry.get_platform_object(platform)
        a_base = cls.APPLIANCE_TEMPLATE_LOCATION
        if not desc_meta_template :
            desc_meta_template = p.select_desc_template(a_base,
                                                        platform,
                                                        appliance_entry)
        
        if not html_desc_meta_template :
            html_desc_meta_template = p.select_html_desc_template(a_base,
                                                        platform,
                                                        appliance_entry)

        content = None
        try:
            f = open(desc_meta_template, "r")
            content = f.read()
        finally:
            if f: f.close()

        html_content = None
        try:
            f = open(html_desc_meta_template, "r")
            html_content = f.read()
        finally:
            if f: f.close()

        if not content : # should always find the template
            return
        
        val_map = {}
        for key, ae_key in  (("NAME", "title"),
                             ("URL", "link"),
                             ("PROVIDER", "provider"),
                             ("PROVIDER_URL", "provider_url"),
                             ("PROVIDER_LOGO_URL", "provider_logo_url"),
                             ("DESCRIPTION","description")):
            v = appliance_entry.get(ae_key)
            if v :
                #v = str(v)
                val_map[key] = v

        val_map["IMAGE_NAME"] = image.base_location

        # add extra requirements
        e_req = ""
        if appliance_entry.get('is_hvm') and \
           to_str(appliance_entry.get('is_hvm')).lower() == "true":
            e_req = e_req + ", " + "HVM / VT Enabled h/w"

        if appliance_entry.get("PAE") :  
            if to_str(appliance_entry.get("PAE")).lower()=="true" :
                e_req = e_req + ", " + "PAE"
            else:
                e_req = e_req +"," + "NON-PAE"
                
        if appliance_entry.get("arch"):
            e_req = e_req + ", " + appliance_entry.get("arch")

        val_map["EXTRA_REQUIREMENTS"] = e_req

        # We are putting some template specific stuff.
        provider_href = ""
        provider_logo_href = ""
        provider_str = ""

        if val_map.get("PROVIDER_URL"):
            provider_href = '<a href="$PROVIDER_URL">$PROVIDER</a>'
        else:
            provider_href = "$PROVIDER"
            
        if val_map.get("PROVIDER_LOGO_URL"):
            provider_logo_href = '<img src="$PROVIDER_LOGO_URL"/>'
            
        provider_str = provider_href + provider_logo_href
        if provider_str == "":
            provider_str = "Unknown (Manually Imported)"

        provider_str = string.Template(provider_str).safe_substitute(val_map)
        val_map["PROVIDER_STR"] = provider_str

        appliance_contact = ""
        
        if val_map.get("URL"):
            appliance_contact = 'Visit <a href="$URL">$NAME</a> for more information on the appliance. <br/>'
        appliance_contact = string.Template(appliance_contact).safe_substitute(val_map)
        
        val_map["APPLIANCE_CONTACT"] = appliance_contact
        template_str = string.Template(content)
        new_content = template_str.safe_substitute(val_map)
        desc_file = image.get_image_desc()

        try:
            fout = open(desc_file, "w")
            fout.write(new_content)
        finally:
            if fout:
                fout.close()

        template_str = string.Template(html_content)
        new_content = template_str.safe_substitute(val_map)
        html_desc_file = image.get_image_desc_html()
        try:
            fout = open(html_desc_file, "w")
            fout.write(new_content)
        finally:
            if fout:
                fout.close()

    @classmethod
    def import_fs(cls, auth, local,\
                  appliance_entry,\
                  image_store,\
                  image_group_id, \
                  image_name, platform,\
                  force, progress = None):

            appliance_url = appliance_entry["href"]

            image_dir = image_store._get_location(image_name) 

            if not local.node_proxy.file_exists(image_dir):
                mkdir2(local, image_dir)

            # fetch the image
            filename = appliance_entry.get("filename")
            ###DIRTY FIX... need to check which transaction is going on
            import transaction
            transaction.commit()
            downloaded_filename = ImageUtils.download_appliance(local,
                                                                appliance_url,
                                                                image_dir,
                                                                filename,
                                                                progress)

            #Make the image entry into the database after the appliance is downloaded.
            #so that database and image store filesystem will be in sync
            #for image_group in image_store.get_image_groups(auth).values():
#            if image_store.image_exists_by_name(image_name):
#                raise Exception("Image "+image_name+" already exists.")
            image = image_store.create_image(auth,image_group_id, image_name, platform)  

            # TBD : need to formalize this in to package handlers.
            if appliance_entry["type"] =="FILE_SYSTEM":
                disk_info = []
                di = get_disk_info("hda", downloaded_filename, "w")
                disk_info.append(di)
            elif appliance_entry["type"] == "JB_ARCHIVE":
                # gunzip/unzip the archive
                ImageUtils.open_package(local, downloaded_filename, image_dir,
                                        progress)
                
                disk_location = search_disks(image_dir)
                # clean up vmdk and other files.
                adjust_jb_image(local, disk_location, progress)
                disk_info = get_jb_disk_info(disk_location)

            vm_template = ImageUtils.get_vm_conf_template(local,
                                                          appliance_entry,
                                                          None, disk_info)
            
            image_conf  = ImageUtils.get_image_config(local, appliance_entry,
                                                    disk_info,
                                                    image_dir)

            ImageUtils.create_files(local, appliance_entry,
                                    image_store, image_group_id, image,
                                    vm_template, image_conf, force)

            return True



import glob
def search_disks(image_dir):
    disk_location = glob.glob(image_dir + '/disks')
    if len(disk_location) <= 0:
        disk_location = glob.glob(image_dir + '/*/disks')
    if len(disk_location) <= 0:
        disk_location = glob.glob(image_dir + '/*/*/disks')
    if len(disk_location) <= 0:
        raise Exception('disk directory not found under ' + image_dir)
    disk_location = disk_location[0]
    return disk_location


def adjust_jb_image(local, disk_location, progress=None):
    for file in ("root.hdd", "root/root.hdd", "var.hdd", "swap.hdd"):
        root_fs = os.path.join(disk_location, file)
        if os.path.exists(root_fs):
            ex =None
            try:
                try:
                    # compress it
                    if progress:
                        progress.update(progress.START_PULSE,
                                        "Compressing " + root_fs)
                    (output, code) = local.node_proxy.exec_cmd("gzip " + root_fs, timeout=get_template_timeout())
                    if code !=0 :
                        raise Exception("Could not gzip " + root_fs + ":" +  output)
                    if progress and not progress.continue_op():
                        raise Exception("Canceled by user.")
                
                except Exception, ex:
                    if progress:
                        progress.update(progress.CANCELED,to_str(ex))
                    raise
                
            finally:
                if progress and not ex:
                    progress.update(progress.STOP_PULSE,"Compressing %s done." % root_fs)

        
    # the .hdd file that is shipped is not suitable for Xen.
    # the data.hdd.gz is what we are looking for.
    # remove all other files
    data_disk = os.path.join(disk_location, "data")
    if os.path.exists(data_disk):
        for exp in ("/*.vmdk", "/*.vhd", "/*.hdd"):
            files  = glob.glob(data_disk + exp)   
            for f in files:
                local.node_proxy.remove(f)


def get_jb_disk_info(disk_location):
    disk_info = []

    for file in ("root.hdd", "root.hdd.gz",
                 "root/root.hdd", "root/root.hdd.gz"):
        root_fs = os.path.join(disk_location, file)
        if os.path.exists(root_fs):
            di = get_disk_info("hda", root_fs, "w")
            disk_info.append(di)
            break

    for file in ("swap.hdd", "swap.hdd.gz"):
        swap_fs = os.path.join(disk_location, file)
        if os.path.exists(swap_fs):
            di = get_disk_info("hdb", swap_fs, "w")
            disk_info.append(di)
            break

    var_found = False
    for file in ("var.hdd", "var.hdd.gz"):
        var_fs = os.path.join(disk_location, file)
        if os.path.exists(var_fs):
            di = get_disk_info("hdd", var_fs, "w") # hdc reserved for cdrom
            disk_info.append(di)
            var_found = True
            break
        
    if not var_found:
        # for new version of jumpbox. (get exact version here)
        data_fs = os.path.join(disk_location, "data/data.xen.tgz")
        if os.path.exists(data_fs):
            di = get_disk_info("hdd", data_fs, "w") # hdc reserved for cdrom
            disk_info.append(di)
        else:
            # generate de for hdd

            # generate dpe so as to satify the following
            
            # need to create a data dir with 10GB sparse file
            # ext3 file system
            # label as 'storage'
            pass

    if len(disk_info) <=0 :
        raise Exception("No disks found from JumpBox Archive.")

    return disk_info


def get_disk_info(device_name, filename, mode, proto='file:'):
    (uncompressed_file, ext) = ImageUtils.get_file_ext(filename)

    de = (proto,device_name, mode)
    d = device_name
    dpes = [ ("%s_disk_create" % d, "yes"),
             ("%s_image_src" % d, filename),
             ("%s_image_src_type" % d, "disk_image")]

    if ext in (".gz", ):
        dpes.append(("%s_image_src_format" % d, "gzip"))
    elif ext in (".tgz", ):
        dpes.append(("%s_image_src_format" % d, "tar_gzip"))
    elif ext in (".bz2", ):
        dpes.append(("%s_image_src_format" % d, "bzip"))
    elif ext in (".tbz2", ):
        dpes.append(("%s_image_src_format" % d, "tar_bzip"))

    return (de, dpes)


def get_template_timeout(default=None):
    if default is None:
        default = 10
    val = default
    try:
        val = int(tg.config.get("template_timeout"))
    except Exception, e:
        print "Exception: ", e
    return val

#from vm to image
class VMToImage():
    IMG_KEY_HOSTNAME = 'HOSTNAME'
    IMG_KEY_PID_FILE = 'PID_FILE'
    IMG_IMAGE_STORE = 'IMAGE_STORE'
    IMG_SHARED_LOCATION = 'SHARED_LOCATION'
    IMG_SHARED_LOCATION_DISK_DIR_PREFIX = 'IMG_'
    IMG_DISKS_DIR = 'disks'
    VM_DISK_LOCATION = '/var/cache/stackone/vm_disks'
    BLOCK_DEVICE_ROOT = '/dev'
    KILL_PROCESS_SCRIPT = 'kill_process.sh'
    
    ###
    def __init__(self):
        from stackone.viewModel import Basic
        self.image_store = Basic.getImageStore()
        self.task_msg = ''
        self.task_id = None

    ###pppp
    def create_image_from_vm_recovery_cleaning(self, auth, node_id, image_name, image_group_id, context, task_id):
        import simplejson as json
        from stackone.model.ManagedNode import ManagedNode
        from stackone.viewModel import Basic
        from stackone.model.services import Task
        new_image_name = image_name
        context_dct = json.loads(context)
        copy_mode = context_dct.get('disk_copy_mode', self.IMG_IMAGE_STORE)
        shared_loc = context_dct.get('shared_loc', '')
        self.task_msg = 'Recovery Task'
        self.task_id = task_id
        self.image_store_image_dir = self.get_image_store_image_dir(new_image_name)
        (self.image_store_tempo_disk_pardir, self.image_store_tempo_disk_dir) = self.get_image_store_tempo_disk_dir(new_image_name)
        self.shared_loc_disks_dir = self.get_shared_loc_disks_dir(shared_loc, new_image_name)
        self.task_msg += '\nMode : %s' % copy_mode
        local = Basic.local_node
        if self.image_store.image_exists_by_name(image_name):
            msg = 'Template %s already exist' % image_name
            LOGGER.info(msg)
            self.task_msg += '\n' + msg
            if copy_mode == self.IMG_IMAGE_STORE:
                if self.image_store_tempo_disk_pardir:
                    msg = 'Cleaning temporary location %s' % self.image_store_tempo_disk_pardir
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                    if os.path.exists(self.image_store_tempo_disk_pardir):
                        shutil.rmtree(self.image_store_tempo_disk_pardir)
                        msg = 'Cleaned temporary location %s' % self.image_store_tempo_disk_pardir
                        print msg
                        LOGGER.info(msg)
                        self.task_msg += '\n' + msg
        else:
            dom = DBSession.query(VM).filter(VM.id == node_id).first()
            if dom:
                dom_ent = auth.get_entity(dom.id)
                dom_image_id = dom.image_id
                node_ents = dom_ent.parents
                if not node_ents:
                    msg = 'Can not find the Server'
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                    raise Exception(self.task_msg)
                else:   
                    node_ent = node_ents[0]
                node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_ent.entity_id).first()
                try:
                    dom_image = DBSession.query(Image).filter(Image.id == dom_image_id).first()
                    self.disk_copy_timeout = self.get_provision_timeout(dom, dom_image)
                    dest_node = node
                    host_name, pid_file = self.get_hostname_pidfile_from_taskcontext(task_id)
                    if host_name and pid_file:
                        host_node = DBSession.query(ManagedNode).filter(ManagedNode.hostname == host_name).first()
                        if host_node:
                            msg = self.kill_process(host_node, pid_file)
                            print msg
                            LOGGER.info(msg)
                            self.task_msg += '\n' + msg
                    
                    image_store_image_dir = self.get_image_store_image_dir(new_image_name)
                    if copy_mode == self.IMG_IMAGE_STORE:
                        if self.image_store_tempo_disk_pardir:
                            msg = 'Cleaning temporary location %s' % self.image_store_tempo_disk_pardir
                            print msg
                            LOGGER.info(msg)
                            self.task_msg += '\n' + msg
                            status, msg = self.remove_directory(local, self.image_store_tempo_disk_pardir, timeout = self.disk_copy_timeout)
                            print msg
                            LOGGER.info(msg)
                            self.task_msg += '\n' + msg
                            
                    if copy_mode == self.IMG_SHARED_LOCATION:
                        if self.shared_loc_disks_dir:
                            msg = 'Cleaning shared location %s' % self.shared_loc_disks_dir
                            print msg
                            LOGGER.info(msg)
                            self.task_msg += '\n' + msg
                            status, msg = self.remove_directory(dest_node, self.shared_loc_disks_dir, timeout=self.disk_copy_timeout)
                            print msg
                            LOGGER.info(msg)
                            self.task_msg += '\n' + msg
                    
                    msg = 'Cleaning image location %s' % image_store_image_dir
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                    status, msg = self.remove_directory(local, image_store_image_dir, timeout = self.disk_copy_timeout)
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                except Exception as ex:
                    traceback.print_exc()
                    self.task_msg += '\n' + to_str(ex)
                    LOGGER.info(self.task_msg)
                    raise Exception(self.task_msg)
        self.task_msg += '\nRecovery Task Completed successfully'
        LOGGER.info(self.task_msg)
        return self.task_msg

    ###
    def kill_process(self, host_node, pid_file, time_count=60):
        res_msg = 'Killing Process'
        scripts_dir = os.path.join(tg.config.get('stackone_cache_dir'), 'common/scripts')
        script_path = scripts_dir + '/' + 'kill_process.sh'
        if host_node:
            cmd = script_path + ' ' + ' $(<' + pid_file + ')' + ' ' + str(time_count)
            print 'cmd: ', cmd
            output, exit_code = host_node.node_proxy.exec_cmd(cmd, timeout=self.disk_copy_timeout)
            if not exit_code:
                msg = 'Process successfully killed, %s' % output
                res_msg += '\n' + msg
            else:
                msg = '%s' % output
                res_msg += '\n' + msg
                
        return res_msg

    ###
    def get_hostname_pidfile_from_taskcontext(self, task_id):
        from stackone.model.services import Task
        task = DBSession.query(Task).filter(Task.task_id == task_id).first()
        task_context = task.context
        host_name = task_context.get(self.IMG_KEY_HOSTNAME, None)
        pid_file = task_context.get(self.IMG_KEY_PID_FILE, None)
        return (host_name, pid_file)

    ###
    def get_provision_timeout(self, dom, image):
        img_vm_config, img_image_config = image.get_configs()
        dom_vm_config = dom.get_config()
        provision_timeout = self.image_store.get_provision_timeout(dom_vm_config, img_image_config)
        msg = 'VM to Template Timeout:%s' % provision_timeout
        print msg
        LOGGER.info(msg)
        return provision_timeout

    ###
    def _create_disk_dir_in_dest_node(self, node, copy_mode, new_image_name, shared_loc):
        try:
            if copy_mode == self.IMG_IMAGE_STORE:
                msg = 'Creating temporary directory %s on node %s' % (self.image_store_tempo_disk_dir, node.hostname)
                print msg
                LOGGER.info(msg)
                self.task_msg += '\n' + msg
                self.create_dir(node, self.image_store_tempo_disk_dir)
                msg = 'Created temporary directory %s on node %s' % (self.image_store_tempo_disk_dir, node.hostname)
                print msg
                LOGGER.info(msg)
                self.task_msg += '\n' + msg
            else:
                if copy_mode == self.IMG_SHARED_LOCATION:
                    if not node.node_proxy.file_exists(shared_loc):
                        msg = 'Shared location %s does not exist on managed node:%s' % (shared_loc, node.hostname)
                        print msg
                        LOGGER.info(msg)
                        self.task_msg += '\n' + msg
                        raise Exception(self.task_msg)
                    
                    msg = 'Creating shared directory %s on node %s' % (self.shared_loc_disks_dir, node.hostname)
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                    self.create_dir(node, self.shared_loc_disks_dir)
                    msg = 'Created shared directory %s on node %s' % (self.shared_loc_disks_dir, node.hostname)
                    LOGGER.info(msg)
                    print msg
                    self.task_msg += '\n' + msg
            
            return None
            
        except exceptions.FileExist as ex:
            traceback.print_exc()
            self.task_msg += '\n' + to_str(ex)
            msg = 'Template %s already exist' % new_image_name
            self.task_msg += '\n' + msg
            raise Exception(self.task_msg)
        
        except Exception as ex:
            traceback.print_exc()
            self.task_msg += '\n' + to_str(ex)
            if copy_mode == self.IMG_IMAGE_STORE:
                if self.image_store_tempo_disk_pardir:
                    msg = 'Removing temporary location %s' % self.image_store_tempo_disk_pardir
                    print msg
                    self.task_msg += '\n' + msg
                    status,msg = self.remove_directory(node, self.image_store_tempo_disk_pardir, timeout=self.disk_copy_timeout)
                    print msg
                    self.task_msg += '\n' + msg
            
            if copy_mode == self.IMG_SHARED_LOCATION:
                if self.shared_loc_disks_dir:
                    msg = 'Removing shared location %s' % self.shared_loc_disks_dir
                    print msg
                    self.task_msg += '\n' + msg
                    status,msg = self.remove_directory(node, self.shared_loc_disks_dir, timeout=self.disk_copy_timeout)
                    print msg
                    self.task_msg += '\n' + msg

            raise Exception(self.task_msg)

    ###
    def get_pid_file_path(self, copy_mode):
        pid_file_location = None
        if copy_mode == self.IMG_IMAGE_STORE:
            pid_file_location = self.image_store_tempo_disk_dir
        elif copy_mode == self.IMG_SHARED_LOCATION:
            pid_file_location = self.shared_loc_disks_dir
        if not pid_file_location:
            raise Exception('pid file does not specified')
            
        return pid_file_location + '/' + 'pid_file'

    ###
    def _copy_disks_to_dest_node(self, task_id, dest_node, copy_mode, new_image_name, disks, node_username, node_address, exec_path, cd_exec_path):
        from stackone.model.ManagedNode import ManagedNode
        ref_disk_config_dict = {}
        disk_cnt = 1
        disks_config_lst = []
        disks_path = self._get_disks_path(copy_mode)
        
        try:
            task_context_dict = {}
            task_context_dict[self.IMG_KEY_HOSTNAME] = dest_node.hostname
            task_context_dict[self.IMG_KEY_PID_FILE] = self.get_pid_file_path(copy_mode)
            self.set_value_in_task_context(task_id, task_context_dict)
            for disk in disks:
                disk_filename = None
                msg = 'Disk Name :%s, is_iso:%s:, is_read_only:%s' % (disk.device, disk.is_iso(), disk.is_read_only())
                print msg
                LOGGER.info(msg)
                print 'Disk :', vars(disk)
                if not disk.is_iso() and not disk.is_read_only():
                    source_disk_path = disk.filename
                    source_disk_name = disk.filename.split('/')[-1]
                    source_disk_dir = disk.filename[:-len(source_disk_name)]
                    new_disk_name = 'disk%s.xm' % disk_cnt
                    dest_disk_path = disks_path % new_disk_name
                    msg = 'Original disk: %s, New path: %s' % (disk.filename, dest_disk_path)
                    print msg
                    LOGGER.info(msg)
                    disk_filename = self.VM_DISK_LOCATION + '/$VM_NAME.disk%s.xm' % disk_cnt
                    disk_cnt += 1
                    cmd = self.get_cmd_disk_copy(copy_mode, source_disk_path=source_disk_path, node_username=node_username, node_address=node_address, dest_disk_path=dest_disk_path, source_disk_dir=source_disk_dir, source_disk_name=source_disk_name)
                    msg = 'Copying disk %s to %s, Time:%s' % (source_disk_path, dest_disk_path, datetime.now())
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                    output, exit_code = dest_node.node_proxy.exec_cmd(cmd, exec_path=exec_path, params=None, cd=cd_exec_path, timeout=self.disk_copy_timeout, pid_file=self.get_pid_file_path(copy_mode))
                    msg = 'output:%s exit_code:%s' % (output, exit_code)
                    print msg
                    LOGGER.info(msg)
                    if exit_code:
                        msg = 'Can not copy disk %s to %s' % (source_disk_path, dest_disk_path)
                        msg += '\n %s' % output
                        print msg
                        LOGGER.info(msg)
                        raise Exception(msg)

                    else:
                        msg = 'Disk %s Successfully Copied to %s , Time:%s, %s' % (source_disk_path, dest_disk_path, datetime.now(), output)
                        print msg
                        LOGGER.info(msg)
                        self.task_msg += '\n' + msg
                        ref_disk_config_dict.update(self.create_ref_disk_config_dict(disk.device, dest_disk_path))
                        
                        if copy_mode == self.IMG_IMAGE_STORE:
                            msg = 'Renaming disk %s to %s' % (source_disk_name, new_disk_name)
                            print msg
                            LOGGER.info(msg)
                            self.task_msg += '\n' + msg
                            old_name = self.image_store_tempo_disk_dir + '/' + source_disk_name
                            new_name = self.image_store_tempo_disk_dir + '/' + new_disk_name
                            status, msg = self.rename_file(dest_node, old_name, new_name)
                            if not status:
                                raise Exception(msg)
                            else:
                                print msg
                                LOGGER.info(msg)
                                self.task_msg += '\n' + msg
                disk_info = disk.get_config(filename=disk_filename)
                disks_config_lst.append(disk_info)
                
                
            msg = 'Disks are Successfully Copied'
            print msg
            LOGGER.info(msg)
            self.task_msg += '\n' + msg
            return (ref_disk_config_dict, disks_config_lst)
        except Exception as ex:
            traceback.print_exc()
            self.task_msg += '\n' + to_str(ex)
            host_name, pid_file = self.get_hostname_pidfile_from_taskcontext(task_id)
            print 'host_name: pid_file:',
            print host_name,
            print pid_file
            if host_name and pid_file:
                host_node = DBSession.query(ManagedNode).filter(ManagedNode.hostname == host_name).first()
                if host_node:
                    msg = self.kill_process(host_node, pid_file)
                    self.task_msg += '\n' + msg
                
            if copy_mode == self.IMG_IMAGE_STORE:
                if self.image_store_tempo_disk_pardir:
                    msg = 'Removing temporary location %s' % self.image_store_tempo_disk_pardir
                    print msg
                    self.task_msg += '\n' + msg
                    status, msg = self.remove_directory(dest_node, self.image_store_tempo_disk_pardir, timeout=self.disk_copy_timeout)
                    print msg
                    self.task_msg += '\n' + msg
                
            if copy_mode == self.IMG_SHARED_LOCATION:
                if self.shared_loc_disks_dir:
                    msg = 'Removing shared location %s' % self.shared_loc_disks_dir
                    print msg
                    self.task_msg += '\n' + msg
                    status, msg = self.remove_directory(dest_node, self.shared_loc_disks_dir, timeout=self.disk_copy_timeout)
                    print msg
                    self.task_msg += '\n' + msg
                
            raise Exception(self.task_msg)
        #[NODE: 1500]
    ###
    def _clone_image_from_vm(self, auth, dest_node, dom_image_id, new_image_name, copy_mode, ref_disk_config_dict, disks_config_lst, img_grp_ent, networks_info_str_list):
        new_image = None
        try:
            image_store_image_dir = self.get_image_store_image_dir(new_image_name)
            msg = 'Copying Image directory'
            print msg
            LOGGER.info(msg)
            self.task_msg += '\n' + msg
            ext_image = DBSession.query(Image).filter(Image.id == dom_image_id).first()
            ext_img_dir = ext_image.get_location()
            self.clone_image_dir(ext_img_dir, image_store_image_dir)
            msg = 'Copied Image directory'
            print msg
            LOGGER.info(msg)
            self.task_msg += '\n' + msg
            if copy_mode == self.IMG_IMAGE_STORE:
                493
                msg = 'Moving disks from %s to %s' % (self.image_store_tempo_disk_dir, image_store_image_dir)
                print msg
                LOGGER.info(msg)
                self.task_msg += '\n' + msg
                status, msg = self.copy_directory(dest_node, self.image_store_tempo_disk_dir, image_store_image_dir, timeout=self.disk_copy_timeout)
                
                if not status:
                    raise Exception(msg)
                else:
                    msg = 'Disks are copied from %s to %s' % (self.image_store_tempo_disk_dir, image_store_image_dir)
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                    msg = 'Removing location %s' % self.image_store_tempo_disk_pardir
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                    status, msg = self.remove_directory(dest_node, self.image_store_tempo_disk_pardir, timeout=self.disk_copy_timeout)
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
            
            msg = 'Creating Image'
            print msg
            LOGGER.info(msg)
            self.task_msg += '\n' + msg
            new_image = self.image_store.create_image_instance(new_image_name,ext_image.get_platform(),location = image_store_image_dir)
            #new_image = Image(getHexID(), ext_image.get_platform(), new_image_name, image_store_image_dir)
            print '>>>>>>>>>>>', new_image
            self.copy_ext_image_settings(ext_image, new_image)
            img_vm_config, img_image_config = new_image.get_configs()
            for key, value in ref_disk_config_dict.items():
                print '>>>>>>>>>>><<<<<<<<<', key, value
                img_image_config[key] = value
            
            img_vm_config['disk'] = disks_config_lst
            img_vm_config['vif'] = networks_info_str_list
            new_image.vm_config = get_config_text(img_vm_config)
            new_image.image_config = get_config_text(img_image_config)
            img_image_config.write()
            img_vm_config.write()
            DBSession.add(new_image)
            img_grp_ent = auth.get_entity(img_grp_ent.entity_id)
            auth.add_entity(new_image.name, new_image.id, to_unicode(constants.IMAGE), img_grp_ent)
            msg = 'Template %s Successfully Created.' % new_image_name
            print msg
            LOGGER.info(msg)
            self.task_msg += '\n' + msg
            return self.task_msg
            
        except exceptions.FileExist as ex:
            traceback.print_exc()
            self.task_msg += '\n' + to_str(ex)
            msg = 'Template %s already exist' % new_image_name
            print msg
            LOGGER.info(msg)
            self.task_msg += '\n' + msg
            raise Exception(self.task_msg)
            
        except Exception as ex:
            traceback.print_exc()
            self.task_msg += '\n' + to_str(ex)
            if copy_mode == self.IMG_IMAGE_STORE:
                if self.image_store_tempo_disk_pardir:
                    msg = 'Removing temporary location %s' % self.image_store_tempo_disk_pardir
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                    status, msg = self.remove_directory(dest_node, self.image_store_tempo_disk_pardir, timeout=self.disk_copy_timeout)
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                
            if copy_mode == self.IMG_SHARED_LOCATION:
                if self.shared_loc_disks_dir:
                    msg = 'Removing shared location %s' % self.shared_loc_disks_dir
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                    status, msg = self.remove_directory(dest_node, self.shared_loc_disks_dir, timeout=self.disk_copy_timeout)
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                
            if image_store_image_dir:
                msg = 'Removing Image location %s' % image_store_image_dir
                print msg
                LOGGER.info(msg)
                self.task_msg += '\n' + msg
                status, msg = self.remove_directory(dest_node, image_store_image_dir, timeout=self.disk_copy_timeout)
                print msg
                LOGGER.info(msg)
                self.task_msg += '\n' + msg
            
                
            if new_image:
                msg = 'Removing image from db'
                print msg
                LOGGER.info(msg)
                self.task_msg += '\n' + msg
                img = DBSession.query(Image).filter(Image.id == new_image.id).delete()
                print 'img:',img
                ent = auth.get_entity(new_image.id)
                if ent:
                    msg = 'Removing entity %s from db' % ent.name
                    print msg
                    LOGGER.info(msg)
                    self.task_msg += '\n' + msg
                    auth.remove_entity(ent)
                    
            raise Exception(self.task_msg)
            
    ###
    def get_image_store_tempo_disk_dir(self, new_image_name):
        tempo_dir_name = self.image_store.TEMPORARY_DIR_PREFIX + new_image_name
        image_store_tempo_dir = self.get_image_store_image_dir(tempo_dir_name)
        image_store_tempo_disk_dir = image_store_tempo_dir + '/' + self.IMG_DISKS_DIR
        return (image_store_tempo_dir, image_store_tempo_disk_dir)

    ###
    def get_shared_loc_disks_dir(self, shared_loc, new_image_name):
        if not shared_loc:
            return None
            
        dir = shared_loc + '/' + self.IMG_SHARED_LOCATION_DISK_DIR_PREFIX + new_image_name
        return dir

    ###
    def _get_disks_path(self, copy_mode):
        disk_path = ''
        if copy_mode == self.IMG_IMAGE_STORE:
            disk_path = '$IMAGE_STORE/$IMAGE_LOCATION/disks/%s'
        elif copy_mode == self.IMG_SHARED_LOCATION:
            disk_path = self.shared_loc_disks_dir + '/%s'
        
        return disk_path
    
    ###pass
    def create_image_from_vm(self, auth, node_id, image_name, image_group_id, context, task_id):
        import simplejson as json
        from stackone.model.ManagedNode import ManagedNode
        from stackone.viewModel import Basic
        from stackone.model.services import Task
        new_image_name = image_name
        context_dct = json.loads(context)
        copy_mode = context_dct.get('disk_copy_mode', self.IMG_IMAGE_STORE)
        shared_loc = context_dct.get('shared_loc', None)
        ref_image_id = context_dct.get('ref_image_id')
        
        self.task_msg = ''
        self.task_id = task_id
        self.image_store_image_dir = self.get_image_store_image_dir(new_image_name)
        self.image_store_tempo_disk_pardir, self.image_store_tempo_disk_dir = self.get_image_store_tempo_disk_dir(new_image_name)
        self.shared_loc_disks_dir = self.get_shared_loc_disks_dir(shared_loc, new_image_name)
        vm_ent = auth.get_entity(node_id)
        
        if not vm_ent:
            raise Exception('Can not find the Virtual Machine')
            
        if vm_ent:
            if not auth.has_privilege('CREATE_IMAGE_FROM_VM', vm_ent):
                raise Exception(constants.NO_PRIVILEGE)
            
            if re.sub(self.image_store.INVALID_CHARS_EXP, '', image_name) != image_name:
                raise Exception('Template name can not contain special chars %s' % self.image_store.INVALID_CHARS)
            
            if image_name == '':
                raise Exception('Template name can not blank')
        
        img_grp_ent = auth.get_entity(image_group_id)
        if not img_grp_ent:
            msg = 'Can not find the Template Group'
            raise Exception(msg)
        
        self.task_msg += 'Mode : %s' % copy_mode

        dom = DBSession.query(VM).filter(VM.id == node_id).first()
        if not dom:
            raise Exception('Can not find the Virtual Machine')
        else:
            dom_image_id = dom.image_id
            if not dom_image_id:
                dom_image_id = ref_image_id
                msg = 'Find reference image:%s' %dom_image_id
                self.task_msg += '\n' + msg
                if not dom_image_id:
                    msg = "Can't create template, Virtual Machine:%s doesn't have template associated with it" %dom.name
                    self.task_msg += '\n' + msg
                    raise Exception(self.task_msg)
            vm_name = dom.name
            dom_ent = auth.get_entity(dom.id)
            node_ents = dom_ent.parents
            local = Basic.getManagedNode()
            if not node_ents:
                msg = 'Can not find the Server'
                raise Exception(msg)
            else:
                node_ent = node_ents[0]
            node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_ent.entity_id).first()
            node_username = node.get_credentials().get('username')
            node_address = node.get_address()
            try:
                #1375
                dom_image = DBSession.query(Image).filter(Image.id == dom_image_id).first()
                if not dom_image:
                    msg = 'Can not find the Template:%s associated with the Virtual Machine:%s' %(dom_image_id,dom.name)
                    self.task_msg += '\n' + msg
                    raise Exception(self.task_msg)
                self.disk_copy_timeout = self.get_provision_timeout(dom, dom_image)
                dom_vm_config = dom.get_config()
                disks = dom_vm_config.getDisks()
                networks = dom_vm_config.getNetworks()
                
                exec_path = None
                cd_exec_path = False
                dest_node = node
                if copy_mode == self.IMG_IMAGE_STORE:
                    exec_path = self.image_store_tempo_disk_dir
                    cd_exec_path = True
                    dest_node = local
                elif copy_mode == self.IMG_SHARED_LOCATION:
                    msg = 'Shared Location: %s' % shared_loc
                    self.task_msg += '\n' + msg
                    msg = 'Copying kill_process script to destination node: %s' %dest_node.hostname
                    LOGGER.info(msg)
                    print msg
                    kill_ps_script = os.path.join(tg.config.get('common_script'),self.KILL_PROCESS_SCRIPT)
                    copyToRemote(kill_ps_script,dest_node,os.path.join(tg.config.get('stackone_cache_dir'),'common/scripts'))
                    msg = 'Copied kill_process script to destination node: %s' %dest_node.hostname
                    LOGGER.info(msg)
                    print msg
                    
                self._create_disk_dir_in_dest_node(dest_node, copy_mode, new_image_name, shared_loc)
                ref_disk_config_dict, disks_config_lst = self._copy_disks_to_dest_node(task_id, dest_node, copy_mode, new_image_name, disks, node_username, node_address, exec_path, cd_exec_path)
                networks_info_str_list = self.get_networks_info_str(networks)
                
                self._clone_image_from_vm(auth, dest_node, dom_image_id, new_image_name, copy_mode, ref_disk_config_dict, disks_config_lst, img_grp_ent,networks_info_str_list)
                import transaction
                transaction.commit()
                LOGGER.info(self.task_msg)
                return self.task_msg
    
            #[NODE: 1018]
            except Exception as ex:
                LOGGER.info(ex)
                traceback.print_exc()
                raise ex

        #[NODE: 1068]

    ###
    def update_task_context(self, task, context):
        import transaction
        transaction.begin()
        task.context = context
        DBSession.add(task)
        transaction.commit()

    ###
    def set_value_in_task_context(self, task_id, task_context_dict):
        from stackone.model.services import Task
        task = DBSession.query(Task).filter(Task.task_id == task_id).first()
        task_context = task.context
        task_context.update(task_context_dict)
        self.update_task_context(task, task_context)

    ###
    def set_task_context(self, task_id, context):
        from stackone.model.services import Task
        task = DBSession.query(Task).filter(Task.task_id == task_id).first()
        self.update_task_context(task, context)

    ###
    def get_task_context(self, task_id):
        from stackone.model.services import Task
        task = DBSession.query(Task).filter(Task.task_id == task_id).first()
        return task.context

    ###
    def create_dir(self, node, dir):
        if not node.node_proxy.file_exists(dir):
            mkdir2(node, dir)
        else:
            msg = 'File exists: %s' % dir
            print msg
            raise exceptions.FileExist(msg)

    ###
    def create_ref_disk_config_dict(self, device, dest_disk_path):
        ref_disk_config_dict = {}
        ref_disk_config_dict['%s_disk_create' % device] = 'yes'
        ref_disk_config_dict['%s_image_src_type' % device] = 'disk_image'
        ref_disk_config_dict['%s_image_src' % device] = dest_disk_path
        return ref_disk_config_dict

    ###
    def move_directory(self, node, source_dir, dest_dir, timeout=-1):
        cmd = commands.get_cmd_move(source_dir, dest_dir)
        msg = 'MV Command: %s' % cmd
        print msg
        LOGGER.info(msg)
        output, exit_code = node.node_proxy.exec_cmd(cmd, timeout=timeout)
        if exit_code:
            msg = 'Can not move directory %s to %s, %s' % (source_dir, dest_dir, output)
            return (False, msg)
        
        msg = 'Directory %s successfully moved to %s, %s' % (source_dir, dest_dir, output)
        return (True, msg)
        
    ###
    def copy_directory(self, node, source_dir, dest_dir, timeout=-1):
        options = '-arf'
        cmd = commands.get_cmd_cp(source_dir, dest_dir, options)
        msg = 'Copy Command: %s' % cmd
        print msg
        LOGGER.info(msg)
        output, exit_code = node.node_proxy.exec_cmd(cmd, timeout=timeout)
        if exit_code:
            msg = 'Can not copy directory %s to %s, %s' % (source_dir, dest_dir, output)
            return (False, msg)
        
        msg = 'Directory %s successfully copied to %s, %s' % (source_dir, dest_dir, output)
        return (True, msg)

    ###
    def remove_directory(self, node, dir, timeout=-1):
        msg = ''
        if not node.node_proxy.file_exists(dir):
            msg = '%s, does not exist' % dir
            print msg
            LOGGER.error(msg)
        else:
            cmd = commands.get_cmd_remove_dir(dir)
            print 'cmd : ',
            print cmd
            output, exit_code = node.node_proxy.exec_cmd(cmd, timeout=timeout)
            if exit_code:
                msg = 'Can not remove: %s, %s' % (dir, output)
                LOGGER.error(msg)
                return (False, msg)
                
            msg = 'Removed %s, %s' % (dir, output)
        
        return (True, msg)

    ###
    def get_cmd_disk_copy(self, copy_mode, source_disk_path=None, node_username=None, node_address=None, dest_disk_path=None, source_disk_dir=None, source_disk_name=None):
        if copy_mode == self.IMG_IMAGE_STORE:
            if source_disk_path.startswith(self.BLOCK_DEVICE_ROOT):
                cmd = commands.get_cmd_copy_block_device_from_remote(node_username, node_address, source_disk_path, source_disk_name)
            else:
                cmd = commands.get_cmd_copy_file_from_remote(node_username, node_address, source_disk_dir, source_disk_name)
        elif copy_mode == self.IMG_SHARED_LOCATION:
            if source_disk_path.startswith(self.BLOCK_DEVICE_ROOT):
                cmd = commands.get_cmd_dd(source_disk_path, dest_disk_path)
            else:
                cmd = commands.get_cmd_cp(source_disk_path, dest_disk_path)
        
        print 'Command: ',
        print cmd
        LOGGER.info('Command: %s' % cmd)
        return cmd
    
    ###
    def rename_file(self, node, old_file_path, new_file_path):
        msg = ''
        if not node.node_proxy.file_exists(old_file_path):
            msg = '%s, does not exist' % old_file_path
            print msg
            LOGGER.error(msg)
            return (False, msg)
        
        output = node.node_proxy.rename(old_file_path, new_file_path)
        if not output:
            msg = 'Renamed %s to %s,  %s' % (old_file_path, new_file_path, output)
        
        return (True, msg)
    
    ###
    def get_image_store_image_dir(self, image_name):
        return self.image_store.get_location(image_name)

    ###
    def clone_image(self, auth, image_group_id, dom_image_id, new_image_name, commit=False):
        return self.image_store.clone_image(auth, image_group_id, dom_image_id, new_image_name, commit)

    ###
    def clone_image_dir(self, src_location, dest_location):
        if os.path.exists(dest_location):
            msg = 'File exists: %s' % dest_location
            print msg
            raise exceptions.FileExist(msg)
        
        shutil.copytree(src_location, dest_location)
    
    ###
    def copy_ext_image_settings(self, ext_img, new_img):
        str_vm_config = ''
        vm_config, image_config = ext_img.get_configs()
        for name, value in vm_config.options.iteritems():
            if name == 'image_name':
                value = to_str(new_img.name)
            str_vm_config += '%s = %s\n' % (name, repr(value))
        
        new_img.vm_config = str_vm_config
        new_img.image_config = get_config_text(image_config)
        new_img.os_name = ext_img.os_name
        new_img.os_flavor = ext_img.os_flavor
        new_img.os_version = ext_img.os_version
        new_img.allow_backup = ext_img.allow_backup
        new_img.version = constants.image_starting_version
        new_img.prev_version_imgid = new_img.id
        return new_img
    def get_networks_info_str(self, networks):
        networks_info_list = []
        for net in networks:
            networks_info_list.append('%r' % net)
        return networks_info_list
####Vcenter
class VmwImage(Image):
    DEFAULT_NETWORK = dict(value='vSwitch0:VM Network', name='Default', nw_id='')
    DEFAULT_AVAILABLE_NETWORKS = [DEFAULT_NETWORK]
    __mapper_args__ = {'polymorphic_identity': constants.PLT_VMW}
    def __init__(self, *args, **kwargs):
        Image.__init__(self, *args, **kwargs)

    def get_network_models(self):
        infolist = []
        infolist.append(dict(name='E1000', value='VirtualE1000'))
        infolist.append(dict(name='E1000e', value='VirtualE1000e'))
        infolist.append(dict(name='VMXNET', value='VirtualVmxnet'))
        infolist.append(dict(name='VMXNET 2', value='VirtualVmxnet2'))
        infolist.append(dict(name='VMXNET 3', value='VirtualVmxnet3'))
        return infolist



class VcenterImage(Image):
    __mapper_args__ = {'polymorphic_identity': constants.VCENTER}
    def __init__(self, *args, **kwargs):
        Image.__init__(self, *args, **kwargs)

    def get_configs(self, host_platform=None):
        self.platform = constants.PLT_VMW
        vm_config = self.get_vm_config()
        img_config = self.get_image_config(vm_config)
        return (vm_config, img_config)

    def get_vm_config(self, node=None):
        self.platform = constants.PLT_VMW
        platform_object = self.registry.get_platform_object(self.platform)
        vm_config = platform_object.create_vcenter_vm_config(node=node, filename=self.name, config=self.vm_config)
        return vm_config

    def get_image_config(self, vm_config=None):
        self.platform = constants.PLT_VMW
        platform_object = self.registry.get_platform_object(self.platform)
        img_config = platform_object.create_vcenter_image_config(vm_config, filename=self.name, config=self.image_config)
        return img_config

    def get_provisioning_helper(self):
        from stackone.core.platforms.vmw.VMWHelpers import VcenterProvisioningHelper
        return VcenterProvisioningHelper()

    def get_older_version_vms(self):
        return []

    def get_latest_version(self):
        return self.get_os_version()

    def get_os_name(self):
        v_config = self.get_configs()
        if v_config:
            return v_config['guestFullName']

    def get_os_flavor(self):
        v_config = self.get_configs()
        if v_config:
            return v_config['guestId']

    def get_os_version(self):
        v_config = self.get_configs()
        if v_config:
            return v_config['version']

    def is_allow_backup(self):
        return self.allow_backup

    def get_image_store(self, auth):
        image_ent = auth.get_entity(self.id)
        if image_ent == None:
            return None
        ent = image_ent.parents[0L].parents[0L]
        image_store = DBSession.query(ImageStore).filter(ImageStore.id == ent.entity_id).first()
        return image_store

    def get_image_desc_html(self):
        return ''
#Index('imggrp_name', ImageGroup.name)
class VcenterImageGroup(ImageGroup):
    __mapper_args__ = {'polymorphic_identity': constants.VCENTER}
    def __init__(self, *args, **kwargs):
        ImageGroup.__init__(self, *args, **kwargs)


class VcenterImageStore(ImageStore):
    __mapper_args__ = {'polymorphic_identity': constants.VCENTER}
    def __init__(self, *args, **kwargs):
        ImageStore.__init__(self, *args, **kwargs)

    def _clone_image(self, auth, image, vm_config, image_config, new_image_name):
        img_ent = auth.get_entity(image.id)
        img_ent_attr = img_ent.get_external_manager_id()
        external_manager_id = img_ent_attr.value
        config_context = {}
        config_context['mob_name'] = image.name
        config_context['dest_host'] = vm_config['host']
        config_context['external_manager_id'] = external_manager_id
        config_context['name'] = new_image_name
        config_context['vmfolder'] = vm_config['vmfolder']
        disks = vm_config.getDisks(image_config)
        config_context['disks'] = disks
        phelper = image.get_provisioning_helper()
        phelper.clone_image(vm_config, config_context=config_context)

    def save_image_from_vm(self, auth, node_id, image_name, image_group_id, context, task_id, dom_image):
        res_msg = 'Creating Template from VM'
        from stackone.model.ManagedNode import ManagedNode
        from stackone.model.VcenterManager import VcenterManager
        import simplejson as json
        try:
            context = json.loads(context)
            esxi_host_id = context.get('node_id')
            datastore_name = context.get('datastore_name')
            esxi_node = DBSession.query(ManagedNode).filter(ManagedNode.id == esxi_host_id).first()
            if not esxi_node:
                raise Exception('Could not find node with ID:%s' % esxi_host_id)
            vm_ent = auth.get_entity(node_id)
            img_gp_ent = auth.get_entity(image_group_id)
            if not vm_ent:
                msg = 'Can not find the Virtual Machine'
                res_msg += '\n' + msg
                raise Exception(res_msg)
            dom = DBSession.query(VM).filter(VM.id == node_id).first()
            if not dom:
                msg = 'Can not find the Virtual Machine'
                res_msg += '\n' + msg
                raise Exception(res_msg)
            dom_vm_config = dom.get_config()
            host_ent = vm_ent.parents[0L]
            mnode = DBSession.query(ManagedNode).filter(ManagedNode.id == host_ent.entity_id).first()
            msg = 'Creating Template on vcenter'
            res_msg += '\n' + msg
            config_context = {}
            config_context['dest_datastore'] = datastore_name
            config_context['dest_host'] = esxi_node.hostname
            config_context['external_manager_id'] = mnode.external_manager_id
            config_context['name'] = image_name
            config_context['mob_name'] = dom.name
            config_context['vmfolder'] = dom_vm_config['vmfolder']
            disks = dom_vm_config.getDisks()
            config_context['disks'] = disks
            moid = self._create_image_from_vm(auth, dom_vm_config, dom_image, config_context)
            msg = 'Template %s (moid:%s) successfully created on vcenter' % (image_name, moid)
            res_msg += '\n' + msg
            new_img = self.create_image_instance(image_name)
            msg = 'Getting Template config info'
            res_msg += '\n' + msg
            vm_config = new_img.get_vm_config(mnode)
            image_config = new_img.get_image_config(vm_config)
            new_img.vm_config = get_config_text(vm_config)
            new_img.image_config = get_config_text(image_config)
            DBSession.add(new_img)
            cntx = {'external_manager_id': mnode.external_manager_id, 'external_id': moid}
            VcenterManager().add_vcenter_entity(auth, cntx, new_img.name, new_img.id, to_unicode(constants.IMAGE), img_gp_ent)
            import transaction
            transaction.commit()
            msg = 'Template Successfully created'
            res_msg += '\n' + msg
            return res_msg
        except Exception as ex:
            res_msg += '\n' + to_str(ex)
            raise Exception(res_msg)

    def _create_image_from_vm(self, auth, dom_vm_config, dom_image, config_context=None):
        from stackone.core.utils.VMWUtils import get_moid
        if not config_context:
            config_context = {}
        phelper = dom_image.get_provisioning_helper()
        result = phelper.create_image_from_vm(dom_vm_config, config_context)
        if not result['success']:
            raise Exception(result['msg'])
        mob_img = result['result']
        if not mob_img:
            raise Exception(result['msg'])
        return get_moid(mob_img)

    def delete_image(self, auth, image_group_id, imageId):
        try:
            msg = ''
            image = DBSession.query(Image).filter(Image.id == imageId).first()
            vm_config,image_config = image.get_configs()
            phelper = image.get_provisioning_helper()
            msg += phelper.delete_image(vm_config)
            self.template_delete(auth, image_group_id, imageId)
        except Exception as ex:
            traceback.print_exc()
            raise ex
        return msg

    def image_copytree(self, *args, **kwargs):
        pass
    #pass
    def create_image_instance(self, name, platform=None, id=None, location=None, is_template=False):
        image = None
        platform = constants.VCENTER
        image = self.create_vcenter_image(name, platform)
        return image
