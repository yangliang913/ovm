from stackone.core.utils.utils import to_unicode, to_str, get_string_status
import stackone.core.utils.constants as constants
from stackone.model.VM import VM, VMDiskManager
from stackone.viewModel.NetworkService import NetworkService
class WebVMInfoHelper():
    def __init__(self):
        pass

    def append_info(self, vm, name, param, typ, id):
        if not vm:
            return {}
        value = vm[param]
        if value:
            if type(value) == int:
                value = to_str(value)
            return dict(id=typ + to_str(id), label=name, value=value, type=typ, extra='')
            
        config = vm.get_config()
        if config:
            value = config[param]
            if value:
                if type(value) == int:
                    value = to_str(value)
                return dict(id=typ + to_str(id), label=name, value=value, type=typ, extra='')
                
        return dict(id=typ + to_str(id), label=name, value='N/A', type=typ, extra='')

    def get_categories(self):
        return [('GEN', 'General'), ('BOOT', 'Boot'), ('RESOURCE', 'Resource')]

    def get_category_keys(self):
        return {'GEN': [('name', 'Name'), ('filename', 'Filename')], 'BOOT': [('on_crash', 'On Crash'), ('on_reboot', 'On Reboot')], 'RESOURCE': [('memory', 'Memory'), ('vcpus', 'CPU'), ('vif', 'Network'), ('disk', 'Disks')]}

    def get_vm_info(self, vm):
        result = []
        cat_keys = self.get_category_keys()
        for cat in self.get_categories():
            i = 0
            for k in cat_keys[cat]:
                result.append(self.append_info(vm, k_label, k, cat_label, i))
                i += 1
        return result

    def get_config_general_info(self, config, dom, mnode, os):
        info_list = []
        info_list.append(dict(name='Name', value=dom.name))
        info_list.append(dict(name='Server', value=mnode.hostname))
        info_list.append(dict(name='Virtual CPUs', value=config['vcpus']))
        info_list.append(dict(name='Memory', value=to_str(config['memory']) + ' MB'))
        info_list.append(dict(name='Guest OS', value=os))
        return info_list

    def get_config_boot_param_info(self, config):
        info_list = []
        info_list.append(dict(name='Bootloader', value=config['bootloader']))
        info_list.append(dict(name='Kernel', value=config['kernel']))
        info_list.append(dict(name='Ramdisk', value=config['ramdisk']))
        info_list.append(dict(name='Root Device', value=config['root']))
        info_list.append(dict(name='Kernel Args', value=config['extra']))
        info_list.append(dict(name='On Power off', value=config['on_shutdown']))
        info_list.append(dict(name='On Reboot', value=config['on_reboot']))
        info_list.append(dict(name='On Crash', value=config['on_crash']))
        boot_device = ''
        if config['boot'] == 'd':
            boot_device = 'CD ROM'
        else:
            boot_device = 'Disk'
        info_list.append(dict(name='Boot Device', value=boot_device))
        return info_list

    def get_config_template_info(self, config):
        info_list = []
        info_list.append(dict(name='Name', value=config['template_name']))
        info_list.append(dict(name='Version', value=config['template_version'] + '' + config['version_comment']))
        return info_list

    def get_config_display_info(self, config):
        info_list = []
        info_list.append(dict(name='VNC', value=get_string_status(config['vnc'])))
        info_list.append(dict(name='Use Unused Display', value=get_string_status(config['vncunused'])))
        info_list.append(dict(name='SDL', value=get_string_status(config['sdl'])))
        info_list.append(dict(name='Standard Vga', value=get_string_status(config['stdvga'])))
        return info_list

    def get_config_usb_device_info(self, config):
        info_list = []
        info_list.append(dict(name='USB Enabled', value=get_string_status(config['usb'])))
        info_list.append(dict(name='USB Device', value=config['usbdevice']))
        return info_list

    def get_config_advanced_info(self, config):
        info_list = []
        info_list.append(dict(name='Architecture Lib directory', value=config['arch_libdir']))
        info_list.append(dict(name='UUID', value=config['uuid']))
        info_list.append(dict(name='Platform', value=config['platform']))
        info_list.append(dict(name='Network Mode', value=config['network_mode']))
        info_list.append(dict(name='Shadow Memory', value=config['shadow_memory']))
        info_list.append(dict(name='PAE', value=get_string_status(config['pae'])))
        info_list.append(dict(name='ACPI', value=get_string_status(config['acpi'])))
        info_list.append(dict(name='APIC', value=get_string_status(config['apic'])))
        info_list.append(dict(name='Architecture', value=config['arch']))
        info_list.append(dict(name='Device Model', value=config['device_model']))
        info_list.append(dict(name='Builder', value=config['builder']))
        return info_list

    def get_config_network_info(self, config):
        info_list = []
        vifs = config.getNetworks()
        for vif in vifs:
            info_list.append(NetworkService().get_nw_entry(vif))
        return info_list

    def get_config_storage_info(self, config):
        info_list = []
        disks = VMDiskManager(config).getDisks()
        for disk in disks:
            is_remote = config.get_storage_stats().get_remote(disk.disk_name)
            if is_remote == True:
                sharedVal = 'Yes'
            else:
                sharedVal = 'No'
        info_list.append(dict(type=disk.disk_type, filename=disk.disk_name, device=disk.dev_type, mode=disk.read_write, shared=sharedVal, size=disk.disk_size))
        return info_list

    def get_vm_dashboard_helper(self):
        return None


