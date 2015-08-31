import stackone.core.utils.constants as constants
from stackone.viewModel.helpers.WebVMInfoHelper import WebVMInfoHelper
from stackone.viewModel.helpers.WebNodeInfoHelper import WebNodeInfoHelper
class VMWWebHelper():
    def __init__(self, platform_config):
        self.platform_config = platform_config

    def get_vm_info_helper(self):
        return VMWVMInfoHelper()

    def get_node_info_helper(self):
        return VMWNodeInfoHelper()



class VMWVMInfoHelper(WebVMInfoHelper):
    def __init__(self):
        WebVMInfoHelper.__init__(self)

    def get_config_advanced_info(self, config):
        info_list = []
        info_list.append(dict(name='UUID', value=config['uuid']))
        info_list.append(dict(name='Platform', value=config['platform']))
        return info_list

    def get_config_boot_param_info(self, config):
        info_list = []
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

    def get_vm_dashboard_helper(self):
        VMW_VM_DASHBOARD_HELPER = {}
        VMW_VM_DASHBOARD_TABS = [constants.UI_TAB_OVERVIEW, constants.UI_TAB_CONFIG, constants.UI_TAB_BACKUP]
        VMW_VM_DASHBOARD_OVERVIEW_TAB_TABLES = {}
        VMW_VM_DASHBOARD_CONFIG_TAB_TABLES = {constants.UI_TABLE_GENERAL: {}, constants.UI_TABLE_TEMPLATE: {}, constants.UI_TABLE_BOOT: {}, constants.UI_TABLE_ADVANCED: {}, constants.UI_TABLE_STORAGE: {}, constants.UI_TABLE_NETWORK: {}, constants.UI_TABLE_DISPALY: None, constants.UI_TABLE_USB: None}
        VMW_VM_DASHBOARD_BACKUP_TAB_TABLES = {}
        VMW_VM_DASHBOARD_HELPER[constants.UI_TABS] = {}
        VMW_VM_DASHBOARD_HELPER[constants.UI_TABS][constants.UI_TAB_OVERVIEW] = VMW_VM_DASHBOARD_OVERVIEW_TAB_TABLES
        VMW_VM_DASHBOARD_HELPER[constants.UI_TABS][constants.UI_TAB_CONFIG] = VMW_VM_DASHBOARD_CONFIG_TAB_TABLES
        VMW_VM_DASHBOARD_HELPER[constants.UI_TABS][constants.UI_TAB_BACKUP] = VMW_VM_DASHBOARD_BACKUP_TAB_TABLES
        return VMW_VM_DASHBOARD_HELPER



class VMWNodeInfoHelper(WebNodeInfoHelper):
    def __init__(self):
        WebNodeInfoHelper.__init__(self)

    def get_config_network_info(self, auth, node, op):
        info_list = node.get_virtual_networks_info()
        return info_list

    def get_config_storage_info(self, auth, node, op):
        info_list = node.get_storage_resources_info()
        return info_list



