from stackone.core.utils.utils import PyConfig
import re
import os
import time
import transaction
from stackone.model.SPRelations import StorageDisks
from stackone.core.utils.NodeProxy import Node
from stackone.model.ManagedNode import ManagedNode
from stackone.core.utils.constants import *
from stackone.core.utils.utils import getHexID
from sqlalchemy import *
from sqlalchemy import orm
from sqlalchemy.orm import relation, backref
from sqlalchemy.types import *
from sqlalchemy.schema import Index, UniqueConstraint
from stackone.model import DeclarativeBase, Entity, EntityType, DBSession
from stackone.model.DBHelper import DBHelper
from stackone.model import DBSession
from stackone.model.availability import AvailState
from stackone.model.Credential import Credential
import logging
LOGGER = logging.getLogger('stackone.model')
from stackone.core.utils.utils import to_unicode, to_str
from datetime import datetime
import transaction
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
LOGGER = logging.getLogger('stackone.model')
class VMOperationException(Exception):
    def __init__(self, message, errno=None):
        if errno:
            Exception.__init__(self, (errno, message))
        else:
            Exception.__init__(self, message)
        self.message = message
        self.errno = errno

    def __repr__(self):
        if self.errno != None:
            return '[Error %s]: %s' % (to_str(self.errno), self.message)
        return self.message



class VM(DeclarativeBase):
    __doc__ = '\n    This represent Doms. It encapsulates information about\n    running virtual machine : state as well as resource stats\n    '
    RUNNING = 0
    PAUSED = 2
    SHUTDOWN = 3
    CRASHED = 4
    NOT_STARTED = -1
    UNKNOWN = -2
    START = 500
    PAUSE = 510
    RESUME = 520
    REBOOT = 530
    STOP = 540
    KILL = 550
    MIGRATE = 560
    COLLECT = 570
    REMOVE = 580
    EDIT = 590
    HA_FAILOVER = 600
    START_FAILED = None
    PAUSE_FAILED = None
    RESUME_FAILED = None
    REBOOT_FAILED = None
    STOP_FAILED = None
    KILL_FAILED = None
    MIGRATE_FAILED = None
    REMOVE_FAILED = None
    EDIT_FAILED = None
    START_SUCCEEDED = None
    PAUSE_SUCCEEDED = None
    RESUME_SUCCEEDED = None
    REBOOT_SUCCEEDED = None
    STOP_SUCCEEDED = None
    KILL_SUCCEEDED = None
    MIGRATE_SUCCEEDED = None
    REMOVE_SUCCEEDED = None
    EDIT_SUCCEEDED = None
    __tablename__ = 'vms'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    vm_config = Column(Text)
    type = Column(Unicode(50), default='NONE')
    ha_priority = Column(Integer)
    preferred_nodeid = Column(Unicode(50))
    image_id = Column(Unicode(50))
    template_version = Column(Float)
    os_flavor = Column(Unicode(50))
    os_name = Column(Unicode(50))
    os_version = Column(Unicode(50))
    status = Column(Unicode(50))
    created_user = Column(Unicode(255))
    created_date = Column(DateTime)
    allow_backup = Column(Boolean)
    backup_retain_days = Column(Integer)
    credential = relation(Credential, primaryjoin=id == Credential.entity_id, foreign_keys=[Credential.entity_id], uselist=False, cascade='all, delete, delete-orphan')
    current_state = relation(AvailState, primaryjoin=id == AvailState.entity_id, foreign_keys=[AvailState.entity_id], uselist=False, cascade='all, delete, delete-orphan')
    start_taskid = Column(Integer)
    reboot_taskid = Column(Integer)
    shutdown_taskid = Column(Integer)
    delete_taskid = Column(Integer)
    created_taskid = Column(Integer)
    email_id = Column(Unicode(255))
    minutes_before = Column(Integer)
    rep_interval = Column(Integer)
    sticky = Column(Integer, default=0)
    last_email_notification = Column(DateTime)
    csep_id = Column(Unicode(50))
    serverpool_id = Column(Unicode(50))
    cloud_vm_id = Column(Unicode(50))
    __mapper_args__ = {'polymorphic_on': type}
    def __init__(self, node, config=None, vm_info=None):
        if not config and vm_info is None:
            raise Exception('config and vm_info both can not be None')
        self.vm_config = ''
        if config:
            for name,value in config.options.iteritems():
                self.vm_config += '%s = %s\n' % (name, repr(value))
        self.node = node
        self._config = config
        self._vm_info = vm_info
        self.id = None
        self.name = None
        self._is_resident = False
        self.pid = None
        self.init()
        self.id = getHexID(self.name, [constants.DOMAIN])
        self.allow_backup = True
        self.sticky = 0
        self.priority = 0
        self.current_state = AvailState(self.id, EntityType.DOMAIN, self.NOT_STARTED, AvailState.NOT_MONITORING, description=u'New VM')
    @orm.reconstructor 
    def init_on_load(self):
        self.node = None
        self.pid = None
        self._config = self.get_new_config(self.vm_config)
        self._vm_info = None
        self._is_resident = False
    
    #@orm.reconstructor
    #def get_new_config(self, config_param):
    #    return VMConfig(config=config_param)
    ###
    def stop_monitoring(self):
        self.current_state.monit_state = AvailState.NOT_MONITORING
    ###
    def start_monitoring(self):
        self.current_state.monit_state = AvailState.MONITORING
    ###
    def get_state(self):
        if self.current_state:
            return self.current_state.avail_state
        return self.UNKNOWN
    ###
    def is_running(self):
        running = False
        if self.get_state() in [self.RUNNING, self.PAUSED, self.UNKNOWN]:
            running = True
        return running
    
    #add 0906
    def get_image_id(self):
        return self.image_id
    
    def has_image(self):
        if self.get_image_id():
            return True
        return False
    ###
    def get_ui_state(self):
        raw_state = self.get_state()
        if raw_state == self.RUNNING or raw_state == self.UNKNOWN:
            return self.RUNNING
        if raw_state == self.PAUSED:
            return self.PAUSED
        return self.SHUTDOWN
    ###
    def is_monitored(self):
        return self.current_state.monit_state == AvailState.MONITORING
    ###
    def init(self):
        LOGGER.error('Error: Must be implemented by derived class.')
    ###
    def get_platform(self):
        raise Exception('Platform not defined!!' + to_str(self.__class__))
    ###
    def isDom0(self):
        return False
    ###
    def isDomU(self):
        return True
    ###
    def refresh(self):
        try:
            self._vm_info = self.node.get_vmm().refresh(self.pid)
            self.init()
        except VMOperationException as ex:
            self._vm_info = None
            self._is_resident = False
    ###
    def _save(self, filename):
        self.node.get_vmm().save(self.pid, filename)
    ###
    def _monitor(self):
        self.start_monitoring()
        self.node.refresh_vm_avail()
    ###
    def _reboot(self):
        self.node.get_vmm().reboot(self.pid)
        self._vm_info = None
        self._is_resident = False
    ###
    def _start(self, config=None):
        if not config:
            self.node.get_vmm().start(self._config)
        else:
            self.node.get_vmm().start(config)
    ###
    def _shutdown(self):
        self.node.get_vmm().shutdown(self.pid)
        self._vm_info = None
        self._is_resident = False
    ###
    def _destroy(self):
        self.node.get_vmm().destroy(self.pid)
        self._vm_info = None
        self._is_resident = False
    ###
    def _pause(self):
        res = self.node.get_vmm().pause(self.pid)
        return res
    ###
    def _unpause(self):
        res = self.node.get_vmm().unpause(self.pid)
        return res
    ###
    def _suspend(self):
        self.node.get_vmm().suspend(self.pid)
    ###
    def _resume(self):
        self.node.get_vmm().resume(self.pid)
    ###
    def _migrate(self, dest, live, port):
        self.node.get_vmm().migrate(self.pid, dest, live, port)
    ###
    def is_resident(self):
        return self._is_resident
    ###
    def getVCPUs(self):
        c = self.get_config()
        if c:
            return c['vcpus']
        return 1
    ###
    def setVCPUs(self, value):
        self.node.get_vmm().setVCPUs(self.pid, value)
    ###
    def setMem(self, value):
        self.node.get_vmm().setMem(self.pid, value)
    ###add 0906
    def setDownVCPUs(self, value):
        self.node.get_vmm().setDownVCPUs(self.pid, value)
    
    def setDownMem(self, value):
        self.node.get_vmm().setDownMem(self.pid, value)
    
    def attachDisks(self, attach_disk_list):
        self.node.get_vmm().attachDisks(self.pid, attach_disk_list)
    ###
    def detachDisks(self, detach_disk_list):
        self.node.get_vmm().detachDisks(self.pid, detach_disk_list)
    ###
    def get_config(self):
        return self._config
    ###
    def set_config(self, config):
        self._config = config

    ###
    def get_info(self):
        return self._vm_info

    ###
    def get_snapshot(self):
        pass

    ###
    def __getitem__(self, param):
        pass

    ###
    def get_state_string(self):
        state = self.get_state()
        if state == self.RUNNING:
            return 'Running'
        if state == self.PAUSED:
            return 'Paused'
        if state == self.SHUTDOWN:
            return 'Shutdown'
        if state == self.CRASHED:
            return 'Crashed'
        if state == self.UNKNOWN:
            return 'Unknown'
        return 'Unknown'

    ###
    def get_console_cmd(self):
        pass

    ###
    def get_vnc_port(self):
        return None

    ###
    def is_graphical_console(self):
        return False

    ###
    def is_hvm(self):
        if self._config is None:
            return None
        return self._config.is_hvm()

    ###
    def get_platform(self):
        if self._config is None:
            return None
        return self._config.get('platform')

    ###add 0906
    def get_reference_image(self, dom_image_id):
        if not dom_image_id:
            dom_image = self.get_platform_image()
        else:
            from stackone.model.ImageStore import Image
            dom_image = DBSession.query(Image).filter(Image.id == dom_image_id).first()
        return dom_image
    
    def get_image_store(self, auth, image):
        from stackone.model.ImageStore import ImageStore
        image_store = image.get_image_store(auth)
        if image_store == None:
            vm_entity = auth.get_entity(self.id)
            dc_ent = vm_entity.parents[0L].parents[0L].parents[0L]
            image_stores = auth.get_child_entities_by_type(dc_ent, constants.IMAGE_STORE)
            if image_stores:
                image_store = DBSession.query(ImageStore).filter(ImageStore.id == image_stores[0L].entity_id).first()
        return image_store
    
    def get_platform_image(self):
        return None
    
    def get_template_info(self):
        template_info = {}
        template_info['template_name'] = self._config['image_name']
        template_info['template_version'] = '0.0'
        template_info['version_comment'] = ''
        try:
            if self.image_id is not None:
                from stackone.model.ImageStore import Image
                img = DBSession.query(Image).filter(Image.id == self.image_id).one()
                template_info['template_name'] = img.name
                template_info['template_version'] = to_str(self.template_version)
                template_info['version_comment'] = ''
                if self.template_version != img.version:
                    template_info['version_comment'] = '*Current version of the Template is ' + to_str(img.version)
        except Exception as e:
            LOGGER.error(e)
        return template_info

    ###
    def get_os_info(self):
        os_info = {}
        os_info['name'] = self.os_name
        os_info['version'] = self.os_version
        if os_info['name'] is None:
            os_info['name'] = self._config['os_name']
            os_info['version'] = self._config['os_version']
        if os_info['name'] is None:
            os_info['name'] = ''
            os_info['version'] = ''
        return os_info
    def get_new_config(self,config_param):
        return VMConfig(config = config_param)
    ###
    def get_state_dict(self):
        state_dict = {}
        state_dict['start'] = [0, 1]
        state_dict['shutdown'] = [3]
        state_dict['kill'] = [3]
        state_dict['pause'] = [2]
        state_dict['unpause'] = [0, 1]
        state_dict['reboot'] = [0, 1]
        return state_dict

    ###
    def check_action_status(self, action, cmd_result):
        values = self.get_state_dict()[action]
        wait = self.get_wait_time(action)
        timeout_err = action + ' failed due to timeout'
        if action == 'reboot':
            rebooted = self.check_reboot_state(wait)
            if rebooted:
                return True
            else:
                raise Exception(timeout_err)
        if action == 'pause':
            paused = self.check_pause_state(values, wait, cmd_result)
            if paused:
                self.status = to_unicode(constants.PAUSED)
                transaction.commit()
                return True
            else:
                raise Exception(timeout_err)
        if action == 'unpause':
            unpaused = self.check_unpause_state(values, wait, cmd_result)
            if unpaused:
                self.status = to_unicode(constants.RESUMED)
                transaction.commit()
                return True
            else:
                raise Exception(timeout_err)
        result = self.check_state(values, wait)
        if result == False:
            raise Exception(timeout_err)
        else:
            return True
    ###
    def check_state(self, values, wait_time):
        for counter in range(0, wait_time):
            time.sleep(1)
            self.node.refresh()
            metrics = self.node.get_metrics()
            data_dict = None
            if metrics is not None:
                data_dict = metrics.get(self.name)
            if data_dict is not None:
                state = data_dict.get('STATE')
            else:
                state = self.SHUTDOWN
            if state in values:
                return True
        return False
    ###
    def check_pause_state(self, values, wait_time, cmd_result):
        return self.check_state(values, wait_time)
    ###
    def check_unpause_state(self, values, wait_time, cmd_result):
        return self.check_state(values, wait_time)
    ###
    def check_reboot_state(self, wait_time):
        pass
    ###
    def status_check(self):
        if self.status == constants.MIGRATING:
            msg = 'VM ' + self.name + ', is on migration. ' + 'Not updating current metrics.'
            return (False, msg)
        return (True, None)
    ###
    def get_wait_time(self, action):
        config = self.get_config()
        wait_time = config[action + '_time']
        if wait_time is None:
            import tg
            wait_time = tg.config.get(action + '_time')
            wait_time = int(wait_time)
        return wait_time
    ###
    def get_attribute_value(self, name, default):
        value = self.get_config().get(name)
        if value is None:
            value = default
        return value
    ###
    def get_memory(self):
        vm_config = self.get_config()
        mem = 0
        try:
            mem = int(vm_config['memory'])
        except Exception as e:
            print 'Exception: ', e
        return mem
    ###
    def get_sticky(self):
        return self.sticky
    ###
    def get_ha_priority(self):
        if self.ha_priority is not None:
            return self.ha_priority
        return 0
    ###
    def get_vnc_log_level(self):
        config = self.get_config()
        log_level = config.get('vnc_log_level')
        if log_level is None:
            import tg
            log_level = tg.config.get('vnc_log_level')
            log_level = int(log_level)
        if log_level >= 4:
            log_level = 4
        print log_level
        return log_level
    
    #add 0906
    def get_UI_config(self, config=None):
        if not config:
            return self._get_UI_config()
        return config
    def _get_UI_config(self):
        ui_config = {}
        storage_status_object = {}
        disk_stat = []
        vm_config = self.get_config()
        for disk in vm_config.getDisks():
            each_disk = {}
            each_disk['filename'] = disk.filename
            each_disk['device'] = disk.device
            each_disk['mode'] = disk.mode
            each_disk['shared'] = False
            each_disk['size'] = 0L
            each_disk['type'] = disk.type
            each_disk['fs_type'] = disk.fs_type
            each_disk['storage_id'] = ''
            each_disk['storage_disk_id'] = ''
            each_disk['backup_content'] = ''
            each_disk['skip_backup'] = ''
            each_disk['disk_entry'] = disk
            disk_stat.append(each_disk)
        storage_status_object['disk_stat'] = disk_stat
        ui_config['storage_status_object'] = storage_status_object
        return ui_config
    
    @classmethod
    def get_failed_vms(cls, vm_ids=None):
        q = DBSession.query(AvailState).filter(AvailState.monit_state == AvailState.MONITORING).filter(AvailState.avail_state == cls.SHUTDOWN).filter(AvailState.entity_type == EntityType.DOMAIN)
        if vm_ids is not None:
            q = q.filter(AvailState.entity_id.in_(vm_ids))
        f_vms = q.all()
        return f_vms
    
    @classmethod
    def get_running_vms(cls, vm_ent_ids):
        try:
            run_vms = DBSession.query(VM).join((AvailState, AvailState.entity_id == VM.id)).filter(AvailState.avail_state != VM.SHUTDOWN).filter(VM.id.in_(vm_ent_ids)).all()
            return run_vms
        except Exception as e:
            LOGGER.error(e)
            raise e
    
    @classmethod
    def get_shutdown_vms(cls, vm_ent_ids):
        try:
            down_vms = DBSession.query(VM).join((AvailState, AvailState.entity_id == VM.id)).filter(AvailState.avail_state == VM.SHUTDOWN).filter(VM.id.in_(vm_ent_ids)).all()
            return down_vms
        except Exception as e:
            LOGGER.error(e)
            raise e
    
    @classmethod
    def get_sticky_vms_count(cls, node_ent_id):
        """
        During DWM, Check if preferred node is set and is same as current node. (In that case,
        consider it as sticky. i.e. dont move the VM)
        """
        node_ent = DBSession.query(Entity).filter(Entity.entity_id == node_ent_id).first()
        vm_ent_ids = [vm_ent.entity_id for vm_ent in node_ent.children]
        doms = [dom for dom in VM.get_vms(vm_ent_ids) if dom.preferred_nodeid == node_ent_id]
        return len(doms)
            
    @classmethod
    def get_vms(cls, vm_ent_ids):
        try:
            vms = DBSession.query(VM).join((AvailState, AvailState.entity_id == VM.id)).filter(VM.id.in_(vm_ent_ids)).all()
            return vms
        except Exception as e:
            LOGGER.error(e)
            raise e
    
    
Index('vm_name', VM.name)
###
class DiskEntry():
    ###
    def __init__(self, input):
        if isinstance(input, basestring):
            m = re.match('^((tap:)?.*?):(.*),(.*),(.*)$', input)
            if m:
                self.type = m.group(1)
                self.filename = m.group(3)
                self.device = m.group(4)
                self.mode = m.group(5)
            else:
                print 'disk entry : No regexp match for',
                print input
                raise Exception('could not parse disk ' + input)
        else:
            if type(input) in (list, tuple):
                self.type, self.filename, self.device, self.mode = input

    ###
    def __repr__(self):
        return '%s:%s,%s,%s' % (self.type, self.filename, self.device, self.mode)


###
class ImageDiskEntry(DiskEntry):
    CREATE_DISK = 'CREATE_DISK'
    USE_DEVICE = 'USE_DEVICE'
    USE_ISO = 'USE_ISO'
    USE_REF_DISK = 'USE_REF_DISK'
    
    ###
    def __init__(self, input, image_conf):
        DiskEntry.__init__(self, input)
        self.option = None
        self.disk_create = 'no'
        self.size = None
        self.disk_type = ''
        self.fs_type = None
        self.image_src = None
        self.image_src_type = None
        self.image_src_format = None
        self.set_image_conf(image_conf)
    ###   
    def get_file_size(self):
        disk_size = self.get_size()
        if  self.device.find('cdrom')>-1 or self.filename.endswith('.iso') or self.mode == 'r':
            disk_size = 0.0
        return disk_size
    ###    
    def get_size(self):
        return self.size 
    ###    
    def init(self):
        if self.image_conf is None:
            return
        device = self.device
        pos = device.find(':cdrom')
        if pos > -1:
            device = device[0:pos]
        create_var = device + '_disk_create'
        image_src_var = device + '_image_src'
        image_src_type_var = device + '_image_src_type'
        image_src_format_var = device + '_image_src_format'
        size_var = device + '_disk_size'
        disk_fs_type_var = device + '_disk_fs_type'
        disk_type_var = device + '_disk_type'
        self.option = self.CREATE_DISK
        self.disk_create = self.image_conf[create_var]
        self.disk_type = self.image_conf[disk_type_var]
        self.size = self.image_conf[size_var]
        if not self.disk_type:
            if self.type == 'file':
                self.disk_type = 'VBD'
            if self.type == 'phy':  # assume physical device e.g. cdrom
                self.disk_type = ''
        if self.image_conf[image_src_var]:
            self.option = self.USE_REF_DISK
        elif self.type == 'phy':
            self.option = self.USE_DEVICE
        elif self.type == 'file':
            if not self.size and self.filename != '':
                self.option = self.USE_ISO
                self.disk_type = 'ISO'
        if self.option == self.CREATE_DISK or self.option == self.USE_REF_DISK:
            if not self.size:
                self.size = 10000
            if not self.filename:
                self.filename = '$VM_DISKS_DIR/$VM_NAME.disk.xm'
        self.image_src = self.image_conf[image_src_var]
        self.image_src_type = self.image_conf[image_src_type_var]
        self.image_src_format = self.image_conf[image_src_format_var]
        self.fs_type = self.image_conf[disk_fs_type_var]
    ###    
    def is_iso(self):
        if not self.option == self.USE_ISO:
            return self.disk_type == 'ISO'
            
        return self.option == self.USE_ISO
    ###    
    def is_new(self):
        if not self.disk_create == 'yes':
            return self.disk_create == 'YES'
        return self.disk_create == 'yes'
    ###    
    def is_read_only(self):
        return self.mode == 'r'
    ###    
    def set_image_conf(self, image_conf):
        self.image_conf = image_conf
        self.init()
        
    #from vm to image
    def get_config(self, type=None, filename=None, device=None, mode=None):
        if not type:
            type = self.type
        if not filename:
            filename = self.filename
        if not device:
            device = self.device
        if not mode:
            mode = self.mode
        disk_info_str = '%s:%s,%s,%s' % (type, filename, device, mode)
        print 'disk_info_str: %s' % disk_info_str
        return disk_info_str
    def is_physical_device(self):
        return self.type == 'phy'

###
class vifEntry():
    ###
    def __init__(self, vif_str, image_config=None):
        self.vif_map = {}
        if vif_str:
            self.vif_map= dict([[z.strip() for z in y.split("=")] for y in [x.strip() for x in vif_str.split(",")]])
    ###
    def get_mac(self):
        return self.vif_map.get('mac')
    ###
    def set_mac(self, v):
        self.vif_map['mac'] = v
    ###
    def get_bridge(self):
        return self.vif_map.get('bridge')
    ###
    def set_bridge(self, v):
        self.vif_map['bridge'] = v
    ###
    def get_item(self, item):
        return self.vif_map.get(item, '')
    ###
    def __repr__(self):
        s = ''
        def_keys = ['mac', 'bridge']
        keys = self.vif_map.keys()
        for k in def_keys:
            if k in keys:
                keys.remove(k)
                
        for k in def_keys + keys:
            v = self.vif_map.get(k)
            if v is not None:
                if s != '':
                    s = s + ','
                s = s + '%s=%s' % (k, v)
        return s



import stat
###
class VMStorageStat():
    STORAGE_STATS = 'STORAGE_STATS'
    DISK_STATS = 'DISK_STATS'
    LOCAL_ALLOC = 'LOCAL_ALLOCATION'
    SHARED_ALLOC = 'SHARED_ALLOCATION'
    DISK_NAME = 'DISK_NAME'
    DISK_SIZE = 'DISK_SIZE'
    DISK_DEV_TYPE = 'DEV_TYPE'
    DISK_IS_LOCAL = 'IS_LOCAL'
    BACKUP_CONTENT = 'BACKUP_CONTENT'
    BLOCK = 'BLOCK'
    FILE = 'FILE'
    UNKNOWN = 'UKNOWN'
    STORAGE_DISK_ID = 'STORAGE_DISK_ID'
    GB_BYTES = 1073741824.0
    ###
    def __init__(self, config):
        self.config = config
        if self.config[self.STORAGE_STATS]:
            self.storage_stats = self.config[self.STORAGE_STATS]
        else:
            self.storage_stats = {}
            self.config[self.STORAGE_STATS] = self.storage_stats
        self.disk_stats = {}
        if self.storage_stats is not None:
            ds = self.storage_stats.get(self.DISK_STATS)
            if ds is None:
                self.storage_stats[self.DISK_STATS] = self.disk_stats
            else:
                self.disk_stats = ds
        self.local_allocation = self.storage_stats.get(self.LOCAL_ALLOC)
        if not self.local_allocation:
            self.local_allocation = 0
        self.shared_allocation = self.storage_stats.get(self.SHARED_ALLOC)
        if not self.shared_allocation:
            self.shared_allocation = 0
        self.storage_disk_id = None
    ###
    def get_storage_disk_id(self, filename):
        file_exists = False
        for de in self.config.getDisks():
            if filename == de.filename:
                file_exists = True
        storage_disk_id = ''
        if file_exists == True:
            de_stat = self.disk_stats.get(filename)
            if de_stat is not None:
                storage_disk_id = de_stat[self.STORAGE_DISK_ID]
                return storage_disk_id
            return storage_disk_id
        else:
            return storage_disk_id
    ###
    def set_storage_disk_id(self, filename, storage_disk_id):
        file_exists = False
        for de in self.config.getDisks():
            if filename == de.filename:
                file_exists = True
                
        if file_exists == True:
            de_stat = self.disk_stats.get(filename)
            if de_stat is not None:
                de_stat[self.STORAGE_DISK_ID] = storage_disk_id
            else:
                de_stat = { self.DISK_NAME : filename,
                            self.DISK_SIZE : 0,
                            self.DISK_DEV_TYPE : self.UNKNOWN,
                            self.DISK_IS_LOCAL : not is_remote,
                            self.BACKUP_CONTENT : '/',
                            self.STORAGE_DISK_ID : storage_disk_id
                            }
        else:
            print 'disk not found in ',
            #print disk_names
            raise Exception('disk ' + filename + ' not found')
    ###
    def set_remote(self, filename, is_remote):
        disk_names = [de.filename for de in self.config.getDisks()]
        if filename in disk_names:
            de_stat = self.disk_stats.get(filename)
            if de_stat is not None :
                de_stat[self.DISK_IS_LOCAL] = not is_remote
            else:
                de_stat = { self.DISK_NAME : filename,
                                self.DISK_SIZE : 0,
                                self.DISK_DEV_TYPE : self.UNKNOWN,
                                self.DISK_IS_LOCAL : not is_remote,
                                self.BACKUP_CONTENT : '/',
                                }
                self.disk_stats[filename] = de_stat
        else:
            print "disk not found in ", disk_names
            raise Exception("disk " + filename + " not found" )

    ###
    def get_remote(self, filename):
        disk_names = [de.filename for de in self.config.getDisks()]
        if filename in disk_names:
            de_stat = self.disk_stats.get(filename)
            if de_stat is not None :
                return (not de_stat[self.DISK_IS_LOCAL])
            else:
                return False
        else:
            return False

    ###
    def update_stats(self):
        for de in self.config.getDisks():
            (disk_size, disk_dev_type) = self.get_disk_size(de)
            de_stat = self.disk_stats.get(de.filename)
            disk_is_local = True  # for now.
            if de_stat:
                de_stat[self.DISK_SIZE] = disk_size
                de_stat[self.DISK_DEV_TYPE] = disk_dev_type
                try:
                    storage_disk_id = de_stat[self.STORAGE_DISK_ID]
                except Exception, ex:
                    de_stat[self.STORAGE_DISK_ID] = None
            else:
                storage_disk_id = self.get_storage_disk_id(de.filename)
                de_stat = {
                    self.DISK_NAME: de.filename,
                    self.DISK_SIZE: disk_size,
                    self.DISK_DEV_TYPE: disk_dev_type,
                    self.DISK_IS_LOCAL: disk_is_local,
                    self.BACKUP_CONTENT: de.backup_content,
                    self.STORAGE_DISK_ID: storage_disk_id,
                    }
                self.disk_stats[de.filename] = de_stat
       # some disks might have been deleted
       # as well as recompute totals.
        total_local = 0
        total_shared = 0
        disk_names = [de.filename for de in self.config.getDisks()]
        to_be_deleted = []
        for ds in self.disk_stats.itervalues():
            d_size = ds[self.DISK_SIZE]
            if d_size is None:
                d_size = 0
            if ds[self.DISK_NAME] not in disk_names:
                to_be_deleted.append(ds[self.DISK_NAME])
            else:
                if ds[self.DISK_IS_LOCAL]:
                    total_local += d_size
                else:
                    total_shared += d_size
        for key in to_be_deleted:
            del self.disk_stats[key]
       # import pprint; pprint.pprint( self.disk_stats )
        self.storage_stats[self.LOCAL_ALLOC] = total_local
        self.storage_stats[self.SHARED_ALLOC] = total_shared
        self.config[self.STORAGE_STATS] = self.storage_stats
    ###
    def get_shared_total(self):
        total = self.storage_stats.get(self.SHARED_ALLOC)
        if total:
            total = total / self.GB_BYTES
        else:
            total = 0
        return total
    ###
    def get_local_total(self):
        total = self.storage_stats.get(self.LOCAL_ALLOC)
        if total:
            total = total / self.GB_BYTES
        else:
            total = 0
        return total
    ###
    def get_disk_size(self, de):
        size = None
        dev_type = self.UNKNOWN
        filename = de.filename
        if filename and self.config.managed_node.node_proxy.file_exists(de.filename):
            f_stat = self.config.managed_node.node_proxy.stat(filename)
            if self.config.managed_node.is_remote():
                mode = f_stat.st_mode
            else:
                mode = f_stat[stat.ST_MODE]
            dev_type = self.FILE
            if stat.S_ISREG(mode):
                dev_type = self.FILE
            else:
                dev_type = self.BLOCK
            if not stat.S_ISREG(mode) and not stat.S_ISBLK(mode):
                print 'unknown disk type :',
                print de.filename,
                print f_stat
                return (None, dev_type)
            if filename.find('/dev') == 0:
                dev_type = self.BLOCK
                try:
                    cmd = 'python -c "import os; filename=\'%s\'; fd=open(filename,\'r\'); fd.seek(0,2); size=fd.tell() ; fd.close(); print size" ' % filename
                    output, code = self.config.managed_node.node_proxy.exec_cmd(cmd)
                    if code == 0:
                        size = eval(output)
                    else:
                        raise Exception(output)
                except Exception as ex:
                    print 'error getting disk size for ',
                    print filename,
                    print ex
                finally:
                    pass
            else:
                if self.config.managed_node.is_remote():
                    size = f_stat.st_size
                else:
                    size = f_stat[stat.ST_SIZE]
        else:
            print 'Error getting disk size for',
            print filename,
            print '(filename does not exist.)'
        return (size, dev_type)


###
class VMConfig(PyConfig):
    imps = ['import sys', 'import os', 'import os.path']
    signature = '# Automtically generated by stackone\n'
    def __init__(self, node=None, filename=None, config=None):
        self.stackone_generated = False
        self.storage_stats = None
        PyConfig.__init__(self, node, filename, VMConfig.signature, config)
        if filename is None and config is None:
            return None
        if len(self.lines) > 0L:
            if self.lines[0L].find(self.signature) >= 0L:
                self.stackone_generated = True
        if self['name'] is None:
            raise Exception('No dom name specified')
        self.name = self['name']
        self.id = self['uuid']
        return None

    ###add 0906
    def get_provision_timeout(self, image_conf):
        provision_timeout = 60L
        try:
            ref_provision_timeout = 0L
            for disk in self['disk']:
                disk_val = disk.split(',')
                disk_image_src_var = disk_val[1L] + '_image_src'
                disk_image_src_type_var = disk_val[1L] + '_image_src_type'
                if image_conf[disk_image_src_var] is not None and image_conf[disk_image_src_type_var] is not None:
                    try:
                        import tg
                        ref_provision_timeout = int(tg.config.get('larger_timeout'))
                    except Exception as e:
                        print 'Exception: ',
                        print e
                    break
            provision_timeout = int(self['provision_timeout'])
            try:
                provision_timeout = int(self['provision_timeout'])
            except Exception as e:
                print 'Exception: ',
                print e
            if provision_timeout < ref_provision_timeout:
                provision_timeout = ref_provision_timeout
        except Exception as e:
            import traceback
            traceback.print_exc()
        return provision_timeout

    def read_config(self, init_glob=None, init_locs=None):
        globs = {}
        locs = {}
        cmd = '\n'.join(self.imps)
        exec cmd in globs, locs
        return PyConfig.read_config(self, globs, locs)
    ###
    def read_conf(self, init_glob=None, init_locs=None):
        globs = {}
        locs = {}
        cmd = '\n'.join(self.imps)
        exec cmd in globs, locs
        return PyConfig.read_conf(self, globs, locs)
    ###
    def __setitem__(self, name, item):
        self.options[name] = item
        if name == 'name':
            self.name = item
    ###
    def set_name(self, name):
        self.name = name
        self['name'] = name
    ###
    def set_id(self, id):
        self.id = id
        self['uuid'] = id
    ###
    def getDisks(self, image_config=None):
        reslist = []
        print self
        if self['disk'] is not None:
            for str in self['disk']:
                if str != '':
                    reslist.append(ImageDiskEntry(str, image_config))
        return reslist
    ###
    def getNetworks(self, image_config=None):
        reslist = []
        if self['vif'] is not None:
            for str in self['vif']:
                if str != '':
                    reslist.append(vifEntry(str, image_config))
        return reslist
    ###
    def write(self):
        self.name = self['name']
        if not self.filename:
            self.filename = os.path.join('/var/cache/stackone/vm_configs/', self.name)
        PyConfig.write(self)
        self.stackone_generated = True
    ###
    def is_stackone_generated(self):
        return self.stackone_generated
    ###
    def get_contents(self):
        contents = self.managed_node.get_config_contents(self.filename)
        return contents
#        f = self.managed_node.node_proxy.open(self.filename)
#        lines = f.readlines()
#        f.close()
#        contents = ''.join(lines)
#        return contents
    ###
    def write_contents(self, contents):
        outfile = self.managed_node.node_proxy.open(self.filename, 'w')
        outfile.write(contents)
        outfile.close()
    ###add 0906
    def delete_config_file(self):
        domfilename = self.filename
        if domfilename and self.managed_node.node_proxy.file_exists(domfilename):
            self.managed_node.node_proxy.remove(domfilename)
    
    def validate(self):
        result = []
        return result
    ###
    def is_hvm(self):
        if self['builder'] == 'hvm':
            return True
        return False
    ###
    def update_storage_stats(self):
        storage_stat = self.get_storage_stats()
        storage_stat.update_stats()
    
    #add 0906
    def update_storage_disks(self):
        storage_stat = self.get_storage_stats()
        storage_stat.update_disks()
    ###
    def set_remote(self, remote_map):
        storage_stat = self.get_storage_stats()
        for d in self.getDisks():
            d_name = d.filename
            is_remote = remote_map.get(d_name)
            if is_remote is not None:
                storage_stat.set_remote(d_name, is_remote)
    ###
    def get_storage_stats(self):
        if self.storage_stats is None:
            #self.storage_stats = VMDiskManager(self)
            self.storage_stats = self.get_disk_manager()
        return self.storage_stats
    
    #add 0906
    def get_disk_manager(self):
        return VMDiskManager(self)


###
class VMStats():
    ###
    def __init__(self, vm):
        self.vm = vm
        self.stat = {}
    ###
    def get_snapshot(self):
        return self.stat


###
class VMDisks(DeclarativeBase):
    __tablename__ = 'vm_disks'
    id = Column(Unicode(50), primary_key=True)
    vm_id = Column(Unicode(50), ForeignKey('vms.id'))
    disk_name = Column(Unicode(300))
    disk_size = Column(Float)
    dev_type = Column(Unicode(50))
    read_write = Column(Unicode(50))
    disk_type = Column(Unicode(50))
    is_shared = Column(Boolean)
    file_system = Column(Unicode(50))
    vm_memory = Column(Float)
    backup_content = Column(Unicode(500))
    sequence = Column(Integer)
    skip_backup = Column(Boolean)
    fk_VMDisks_VM = relation('VM', backref='VMDisks')
    ###
    def __init__(self):
        pass
    ###
    def get_disk_size(self):
        disk_size = self.disk_size
        if self.dev_type.find('cdrom') > -1 or self.disk_name.endswith('.iso') or self.read_write == 'r':
            disk_size = 0.0
        return disk_size



Index('vdisk_disk_name', VMDisks.disk_name)
###
class VMStorageLinks(DeclarativeBase):
    __tablename__ = 'vm_storage_links'
    __table_args__ = (UniqueConstraint('vm_disk_id', 'storage_disk_id', name='ucVMStorageLinks'), {})
    id = Column(Unicode(50), primary_key=True)
    vm_disk_id = Column(Unicode(50), ForeignKey('vm_disks.id'))
    storage_disk_id = Column(Unicode(50), ForeignKey('storage_disks.id'))
    fk_VMStorageLinks_VMDisks = relation('VMDisks', backref='VMStorageLinks')
    fk_VMStorageLinks_StorageDisks = relation('StorageDisks', backref='VMStorageLinks')
    ###
    def __init__(self):
        pass


###
class VMDiskManager():
    DISK = 'disk'
    STORAGE_STATS = 'STORAGE_STATS'
    DISK_STATS = 'DISK_STATS'
    LOCAL_ALLOC = 'LOCAL_ALLOCATION'
    SHARED_ALLOC = 'SHARED_ALLOCATION'
    DISK_NAME = 'DISK_NAME'
    DISK_SIZE = 'DISK_SIZE'
    DISK_DEV_TYPE = 'DEV_TYPE'
    DISK_IS_LOCAL = 'IS_LOCAL'
    BACKUP_CONTENT = 'BACKUP_CONTENT'
    BLOCK = 'BLOCK'
    FILE = 'FILE'
    UNKNOWN = 'UKNOWN'
    STORAGE_DISK_ID = 'STORAGE_DISK_ID'
    GB_BYTES = 1073741824.0
    ###
    def __init__(self, config):
        self.config = config
        self.storage_stats = {}
        self.vm_id = None
        if self.config:
            vm = DBSession.query(VM).filter_by(id=to_unicode(config.id)).first()
            if vm:
                self.vm_id = vm.id
                self.storage_stats = self.get_storage_stats(vm.id)
        self.disk_stats = {}
        if self.storage_stats is not None:
            ds = self.storage_stats.get(self.DISK_STATS)
            if ds is None:
                self.storage_stats[self.DISK_STATS] = self.disk_stats
            else:
                self.disk_stats = ds
        self.local_allocation = self.storage_stats.get(self.LOCAL_ALLOC)
        if not self.local_allocation:
            self.local_allocation = 0
        self.shared_allocation = self.storage_stats.get(self.SHARED_ALLOC)
        if not self.shared_allocation:
            self.shared_allocation = 0
        self.storage_disk_id = None
    ###add 0906
    def update_disks(self):
        pass
    
    def update_stats(self):
        vm = DBSession.query(VM).filter_by(id=self.config.id).first()
        if vm:
            disks = self.getDisks(vm.id)
        else:
            disks = self.config.getDisks()
        if disks:
            for de in disks:
                if vm:
                    filename = de.disk_name
                else:
                    filename = de.filename
                (disk_size, disk_dev_type) = self.get_disk_size(de)
                de_stat = self.disk_stats.get(filename)
                disk_is_local = True  # for now.
                if de_stat:
                    de_stat[self.DISK_SIZE] = disk_size
                    de_stat[self.DISK_DEV_TYPE] = disk_dev_type
                    try:
                        storage_disk_id = de_stat[self.STORAGE_DISK_ID]
                    except Exception, ex:
                        de_stat[self.STORAGE_DISK_ID] = None
                else:
                    storage_disk_id = self.get_storage_disk_id(filename)
                    de_stat = {
                        self.DISK_NAME: filename,
                        self.DISK_SIZE: disk_size,
                        self.DISK_DEV_TYPE: disk_dev_type,
                        self.DISK_IS_LOCAL: disk_is_local,
                        self.STORAGE_DISK_ID: storage_disk_id,
                        }
                    self.disk_stats[filename] = de_stat
        # some disks might have been deleted
        # as well as recompute totals.
        total_local = 0
        total_shared = 0
        if vm:
            disk_names = [de.disk_name for de in disks]
        else:
            disk_names = [de.filename for de in disks]
        to_be_deleted = []
        for ds in self.disk_stats.itervalues():
            d_size = ds[self.DISK_SIZE]
            if d_size is None:
                d_size = 0
            if ds[self.DISK_NAME] not in disk_names:
                to_be_deleted.append(ds[self.DISK_NAME])
            else:
                if ds[self.DISK_IS_LOCAL]:
                    total_local += d_size
                else:
                    total_shared += d_size
        for key in to_be_deleted:
            del self.disk_stats[key]
        # import pprint; pprint.pprint( self.disk_stats )
        self.storage_stats[self.LOCAL_ALLOC] = total_local
        self.storage_stats[self.SHARED_ALLOC] = total_shared
        self.config[self.STORAGE_STATS] = self.storage_stats

    ###
    def get_shared_total(self):
        total = self.storage_stats.get(self.SHARED_ALLOC)
        if total:
            total = total / self.GB_BYTES
        else:
            total = 0
        return total
    ###
    def get_local_total(self):
        total = self.storage_stats.get(self.LOCAL_ALLOC)
        if total:
            total = total / self.GB_BYTES
        else:
            total = 0
        return total
    ###
    def get_disk_size(self, de, filename=None, vm_name=None):
        size = None
        dev_type = self.UNKNOWN
        try:
            if not filename:
                try:
                    filename = de.disk_name
                except Exception, ex:
                    filename = de.filename
            if filename == '/dev/cdrom':
                return (0, self.UNKNOWN)
            if filename \
                and self.config.managed_node.node_proxy.file_exists(filename):
                f_stat = \
                    self.config.managed_node.node_proxy.stat(filename)
                if self.config.managed_node.is_remote():
                    mode = f_stat.st_mode
                else:
                    mode = f_stat[stat.ST_MODE]
                dev_type = self.FILE
                if stat.S_ISREG(mode):
                    dev_type = self.FILE
                else:
                    dev_type = self.BLOCK
                if not stat.S_ISREG(mode) and not stat.S_ISBLK(mode):
                    print 'unknown disk type :', filename, f_stat
                    return (None, dev_type)
                if filename.find('/dev') == 0:
                    # assume block device
                    dev_type = self.BLOCK
                    try:
                        try:
                            cmd = \
                                """python -c "import os; filename='%s'; fd=open(filename,'r'); fd.seek(0,2); size=fd.tell() ; fd.close(); print size" """ \
                                % filename
                            (output, code) = \
                                self.config.managed_node.node_proxy.exec_cmd(cmd)
                            # print "cmd ", cmd, " code -> " , code, " out-> ", output
                            if code == 0:
                                size = eval(output)
                            else:
                                raise Exception(output)
                        except Exception, ex:
                            print 'error getting disk size for ', \
                                filename, ex
                    finally:
                        pass
                else:
                    if self.config.managed_node.is_remote():
                        size = f_stat.st_size
                    else:
                        size = f_stat[stat.ST_SIZE]  # TO DO Sparse handling
            else:
                print 'Error getting disk size for', filename, \
                    '(filename does not exist.)'
        except Exception, ex:
            import traceback
            traceback.print_exc()
            error_msg = to_str(ex).replace("'", '')
            LOGGER.error('Error getting disk size for '
                         + to_str(filename) + '. Error description: '
                         + to_str(error_msg))
            return (size, dev_type)
        return (size, dev_type)

    ###
    def get_new_disk_entry(self):
        vm_disk = VMDisks()
        return vm_disk
    ###
    def getDisks(self, vm_id=None):
        vm_disks = []
        if not vm_id:
            vm_id = self.vm_id
        vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
        return vm_disks
    ###
    def get_storage_stats(self, vm_id=None):
        storage_stats = {}
        disk_stats = {}
        disk_detail = {}
        if not vm_id:
            vm_id = self.vm_id
        if vm_id:
            vm_disks = DBSession.query(VMDisks).filter_by(vm_id=vm_id)
            for vm_disk in vm_disks:
                disk_detail = {}
                disk_detail['DEV_TYPE'] = vm_disk.dev_type
                disk_detail['IS_LOCAL'] = self.get_remote(vm_disk.disk_name)
                disk_detail['DISK_SIZE'] = vm_disk.disk_size
                disk_detail['DISK_NAME'] = vm_disk.disk_name
                disk_detail['BACKUP_CONTENT'] = vm_disk.backup_content
                storage_disk_id = None
                vm_storage_link = DBSession.query(VMStorageLinks).filter_by(vm_disk_id=vm_disk.id).first()
                if vm_storage_link:
                    storage_disk_id = vm_storage_link.storage_disk_id
                disk_detail['STORAGE_DISK_ID'] = storage_disk_id
                disk_stats[vm_disk.disk_name] = disk_detail
            storage_stats['LOCAL_ALLOCATION'] = 0
            storage_stats['SHARED_ALLOCATION'] = 0
            storage_stats['DISK_STATS'] = disk_stats
        return storage_stats
    ###
    def get_disk_stat(self, vm_id, filename):
        disk_detail = {}
        storage_disk = DBSession.query(StorageDisks).filter_by(unique_path=filename).first()
        if storage_disk:
            vm_disk = DBSession.query(VMDisks).filter_by(vm_id=vm_id, disk_name=filename).first()
            if vm_disk:
                disk_detail = {}
                disk_detail['DEV_TYPE'] = vm_disk.dev_type
                disk_detail['IS_LOCAL'] = self.get_remote(vm_disk.disk_name)
                disk_detail['DISK_SIZE'] = vm_disk.disk_size
                disk_detail['DISK_NAME'] = vm_disk.disk_name
                disk_detail['BACKUP_CONTENT'] = vm_disk.backup_content
                disk_detail['STORAGE_DISK_ID'] = storage_disk.id
        return disk_detail
    ###
    def get_remote(self, filename):
        isLocal = True
        vm_disk = DBSession.query(VMDisks).filter_by(disk_name=filename).first()
        if vm_disk:
            isLocal = vm_disk.is_shared
        return isLocal
    ###
    def set_remote(self, filename, is_remote):
        try:
            disk_names = []
            vm = \
                DBSession.query(VM).filter_by(name=self.config.name).first()
            if vm:
                disk_names = [de.disk_name for de in
                              self.getDisks(vm.id)]
                if filename in disk_names:
                    de_stat = self.get_disk_stat(vm.id, filename)  # self.disk_stats.get(filename)
                    if de_stat is not None:
                        de_stat[self.DISK_IS_LOCAL] = not is_remote
                    else:
                        de_stat = {
                            self.DISK_NAME: filename,
                            self.DISK_SIZE: 0,
                            self.DISK_DEV_TYPE: self.UNKNOWN,
                            self.DISK_IS_LOCAL: not is_remote,
                            self.BACKUP_CONTENT: '/'
                            }
                                    # self.STORAGE_DISK_ID : ""
                        self.disk_stats[filename] = de_stat
        except Exception, ex:
            LOGGER.error('Error in set_remote(): ' + str(ex))
    

    ###
    def get_storage_disk_id(self, filename):
        storage_disk_id = None
        storage_disk = DBSession.query(StorageDisks).filter_by(unique_path=filename).first()
        if storage_disk:
            storage_disk_id = storage_disk.id
        return storage_disk_id
    ###
    def set_storage_disk_id(self, filename, storage_disk_id):
        try:
            file_exists = False
            vm = \
                DBSession.query(VM).filter_by(name=self.config.name).first()
            if vm:
                for de in self.getDisks(vm.id):
                    if filename == de.disk_name:
                        file_exists = True
                if file_exists == True:
                    de_stat = self.get_disk_stat(vm.id, filename)  # self.disk_stats.get(filename)
                    if de_stat is not None:
                        de_stat[self.STORAGE_DISK_ID] = storage_disk_id
                    else:
                        de_stat = {
                            self.DISK_NAME: filename,
                            self.DISK_SIZE: 0,
                            self.DISK_DEV_TYPE: self.UNKNOWN,
                            self.DISK_IS_LOCAL: not is_remote,
                            self.BACKUP_CONTENT: '/',
                            self.STORAGE_DISK_ID: storage_disk_id,
                            }
        except Exception, ex:
            LOGGER.error('Error in set_storage_disk_id(): ' + str(ex))
           

    ###
    def get_storage_id(self, filename):
        storage_id = None
        storage_disk = DBSession.query(StorageDisks).filter_by(unique_path=filename).first()
        if storage_disk:
            storage_id = storage_disk.storage_id
        return storage_id

    
###
class OutsideVM(DeclarativeBase):
    __tablename__ = 'outside_vms'
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    node_id = Column(Unicode(50), nullable=False)
    status = Column(Integer)
    ###
    def __init__(self, name, node_id, status):
        self.id = getHexID(name, [constants.DOMAIN])
        self.name = name
        self.node_id = node_id
        self.status = status
    ###
    @classmethod
    def onRemoveNode(cls, node_id):
        DBSession.query(OutsideVM).filter(OutsideVM.node_id
                == node_id).delete()


Index('ovm_nid_name', OutsideVM.node_id, OutsideVM.name)
