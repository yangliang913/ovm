import sys
import os
import re
import types
import time
from stackone.core.utils.utils import search_tree, PyConfig, mktempfile
from stackone.core.utils.NodeProxy import Node
from stackone.core.utils.constants import *
from stackone.model.VM import *
from stackone.core.platforms.vmw.VMWConstants import my_platform
from stackone.core.utils.utils import getHexID
from stackone.model.availability import AvailState
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
LOGGER = logging.getLogger('core.platforms.vmw')
class VMWDomain(VM):
    __mapper_args__ = {'polymorphic_identity': u'vmw'}
    def __init__(self, node, config=None, vm_info=None):
        VM.__init__(self, node, config, vm_info)

    def init(self):
        if self._config:
            self.name = self._config.name
            self._is_resident = False
        else:
            if self._vm_info:
                self.name = self._vm_info.name
                self.pid = self._vm_info.id
                self._is_resident = self._vm_info.state != 'poweredOff'

    def get_new_config(self, config_param):
        return VMWConfig(config=config_param)

    def set_vm_info(self, vm_info):
        self._vm_info = vm_info
        self.name = self._vm_info.name
        self.pid = self._vm_info.id
        self._is_resident = self._vm_info.state != 'poweredOff'

    def get_platform(self):
        return my_platform

    def get_platform_image(self):
        from stackone.model.ImageStore import VcenterImage
        platform = self.get_platform()
        return VcenterImage(getHexID(), platform, 'VMWTempImg', location=None)

    def __getitem__(self, param):
        if param == 'name':
            return self.name
        if self._vm_info:
            return self._vm_info[param]
        return None

    def _save(self, filename):
        cfg = self.get_config()
        if cfg is None:
            raise Exception('Can not save snapshot without associated config.')
        self.node.get_vmm().save(self.pid, filename, cfg)
        return None

    def _migrate(self, dest, live, port):
        self.node.get_vmm().migrate(self.pid, dest, live, port, None)
        return None

    def get_console_cmd(self):
        return None

    def get_vnc_port(self):
        if self._vm_info is not None:
            vnc_port_string = self._vm_info.get('vnc')
            if vnc_port_string and vnc_port_string[0] == ':':
                return int(vnc_port_string[1:])
        return None

    def is_graphical_console(self):
        return True

    def get_snapshot(self):
        if self._stats == None:
            self._stats = VMWStats(self)
        return self._stats.get_snapshot()

    def check_pause_state(self, values, wait_time, cmd_result):
        return cmd_result == True

    def check_unpause_state(self, values, wait_time, cmd_result):
        return cmd_result == True

    def check_reboot_state(self, wait_time):
        time.sleep(wait_time)
        return True

    def status_check(self):
        cont,msg = VM.status_check(self)
        if cont == False:
            return (cont, msg)
        if self.status == constants.PAUSED:
            msg = 'Virtual Machine ' + self.name + '(VMW) is in Paused state.'
            return (True, msg)
        return (True, None)

    def get_UI_config(self, config=None):
        return self._get_UI_config()



class VMWConfig(VMConfig):
    def __init__(self, node=None, filename=None, config=None):
        VMConfig.__init__(self, node, filename, config)

    def validate(self):
        result = []
        if not self['name']:
            result.append('Missing domain name.')
        if not self['disk']:
            result.append('Missing disk specification.')
        return result

    def write(self):
        self.name = self['name']
        self.stackone_generated = True

    def write_contents(self, contents):
        pass

    def delete_config_file(self):
        pass

    def get_storage_stats(self):
        if self.storage_stats is None:
            self.storage_stats = self.get_disk_manager()
        return self.storage_stats

    def get_disk_manager(self):
        return VMWDiskManager(self)



class VcenterConfig(VMWConfig):
    def __init__(self, node=None, filename=None, config=None):
        self.name = filename
        VMWConfig.__init__(self, node, filename, config=config)
        if self.config or self.filename:
            self.lines = self.read_conf()

    def get_config_using_external_source(self):
        cmd = ''
        lines = []
        return (lines, cmd)

    def write(self, full_edit=False):
        pass

    def is_hvm(self):
        return True

    def create_image_config(self, filename=None, config=None):
        from stackone.core.utils.VMWUtils import convert_config_dict_to_str
        image_config = {}
        if self.managed_node:
            devices = self.managed_node.node_proxy.get_virtual_disks(self.filename)
            disk_map = {}
            for device in devices:
                disk_map[device.backing.fileName] = device
            for disk in self['disk']:
                disk_val = disk.split(',')
                disk_device = disk_val[1]
                disk_name = disk_val[0].split(':')[1]
                if disk_name in disk_map.keys():
                    size = 0
                    size = disk_map[disk_name].capacityInKB
                    if size:
                        size = int(size) / 1024
                    image_config[disk_device + '_disk_size'] = str(size)
                    image_config[disk_device + '_disk_create'] = 'yes'
                    image_config[disk_device + '_disk_type'] = 'VDB'
                config = convert_config_dict_to_str(image_config)
        vc = VcenterConfig(filename=filename, config=config)
        return vc



class VMWDiskManager(VMDiskManager):
    def __init__(self, config):
        VMDiskManager.__init__(self, config)
        self.virtual_disks = []

    def get_disk_size(self, de, filename=None, vm_name=None):
        print '==filename==de==vm_name==',
        print filename,
        print de,
        print vm_name
        size = None
        dev_type = self.UNKNOWN
        if vm_name:
            if not de:
                msg = 'Invalid Diskentry:%s' % de
                raise Exception(msg)
            if de.is_iso() or de.is_physical_device():
                return (size, dev_type)
            if not self.virtual_disks:
                self.virtual_disks = self.config.managed_node.node_proxy.get_virtual_disks(vm_name)
            for disk in self.virtual_disks:
                print '==filename==disk.backing.fileName==',
                print filename,
                print disk.backing.fileName
                if filename == disk.backing.fileName:
                    size = disk.capacityInKB
                    if size:
                        size = int(size) * 1024
                    return (size, dev_type)
            msg = 'Could not find disk:%s of VM:%s' % (filename, vm_name)
            LOGGER.error(msg)
        return (size, dev_type)

    def _get_datastore_path(self, filename):
        pattn = re.compile('^\\[.*]')
        type = self.UNKNOWN
        disk_name = filename.split('/')[-1]
        datastore_path = filename[:-len(disk_name)]
        match = pattn.match(datastore_path)
        if match:
            type = self.BLOCK
        return (datastore_path, disk_name)

    def update_disks(self):
        self.config[self.DISK] =['%r' % disk for disk in self.get_disks_from_vm()]


    def get_disks_from_vm(self):
        disks = []
        if self.config.managed_node:
            disks = self.config.managed_node.node_proxy.get_config_disks(self.config.name)
        return disks



class VMWStats(VMStats):
    def __init__(self, vm):
        VMStats.__init__(self, vm)

    def get_snapshot(self):
        return self.stat



