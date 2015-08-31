from stackone.controllers.NodeController import NodeController
from stackone.model import *
from stackone.model.Authorization import AuthorizationService
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from stackone.controllers.ControllerImpl import ControllerImpl
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
from tg import session
from stackone.controllers.XMLRPC.stackoneXMLRPC import stackoneXMLRPC
class NodeXMLRPCController(stackoneXMLRPC):
    node_controller = NodeController()
    controller_impl = ControllerImpl()
    def get_platform(self, node_id, type, **result):
        result = None
        result = self.node_controller.get_platform(node_id, type)
        return result

    def get_managed_nodes(self, site_id=None, group_id=None, **result):
        result = None
        result = self.node_controller.get_managed_nodes(group_id, site_id)
        return result

    def get_managed_nodes(self, site_id=None, group_id=None, **result):
        result = None
        result = self.node_controller.get_managed_nodes(group_id, site_id)
        return result

    def get_node_info(self, node_id, level, _dc=None):
        result = None
        result = self.node_controller.get_node_info(node_id, level)
        return result

    def refresh_node_info(self, node_id, level, _dc=None):
        result = None
        result = self.node_controller.refresh_node_info(node_id, level)
        return result

    def get_group_vars(self, group_id, _dc=None):
        result = None
        result = self.node_controller.get_group_vars(group_id)
        return result

    def save_group_vars(self, group_id, _dc=None, **result):
        result = None
        result = self.node_controller.save_group_vars(group_id, attrs)
        return result

    def add_server(self, platform, hostname, username, password, ssh_port, use_keys, is_standby, group_id, protocol='tcp', xen_port=8006, xen_migration_port=8002, address=None, **result):
        result = None
        if platform == 'xen':
            if protocol not in ('tcp', 'ssl', 'ssh_tunnel'):
                return {'msg':'Make sure you entered the exact protocol','success':'false'}
        result = self.node_controller.add_node(platform, hostname, username, password, ssh_port, use_keys, is_standby, group_id, protocol, xen_port, xen_migration_port, address)
        return result

    def edit_server(self, node_id, is_standby, hostname, username, password, platform=None, ssh_port=None, use_keys=None, protocol='tcp', xen_port=8006, xen_migration_port=8002, address=None, **result):
        result = None
        result = self.node_controller.edit_node_cli(node_id, hostname, username, password, platform, ssh_port, use_keys, is_standby, protocol, xen_port, xen_migration_port, address)
        return result

    def change_server_password(self, nodenames, newpassword):
        result = self.node_controller.change_server_password(nodenames, newpassword)
        return result

    def remove_node(self, node_id, force='False'):
        result = None
        result = self.node_controller.remove_node(node_id, eval(force))
        return result

    def get_node_properties(self, node_id):
        result = None
        result = self.node_controller.get_node_properties(node_id)
        return result

    def connect_node(self, node_id, username='root', password=None):
        result = None
        result = self.node_controller.connect_node(node_id, username, password)
        return result

    def vm_action(self, dom_id, node_id, action1, date=None, time=None):
        result = None
        result = self.node_controller.vm_action(dom_id, node_id, action1, date, time)
        return result

    def transfer_node(self, node_id, source_group_id, dest_group_id, forcefully):
        result = None
        result = self.node_controller.transfer_node(node_id, source_group_id, dest_group_id, forcefully)
        return result

    def server_action(self, node_id, action1, date=None, time=None):
        result = None
        result = self.node_controller.server_action(node_id, action1, date, time)
        return result

    def import_vm_config(self, node_id, directory, filenames):
        try:
            result = None
            action = 'import_vm'
            if len(filenames) > 0:
                action = 'import_vms'
            result = self.node_controller.import_vm_config(node_id, directory, filenames, action)
            return result
        except Exception as e:
            print_traceback()

    def import_configs(self, node_id, paths):
        result = None
        action = 'import_vm'
        if len(paths) > 0:
            action = 'import_vms'
        result = self.node_controller.import_configs(node_id, paths, action)
        return result

    def restore_vm(self, node_id, directory, filenames, date=None, time=None):
        result = None
        result = self.node_controller.restore_vm(node_id, directory, filenames, date, time)
        return result

    def save_vm(self, dom_id, node_id, directory, filenames, date=None, time=None):
        result = None
        result = self.node_controller.save_vm(dom_id, node_id, filenames, directory, date, time)
        return result

    def migrate_vm(self, dom_name, dom_id, source_node_id, dest_node_id, live='true', force='false', all='false', date=None, time=None):
        result = None
        result = self.node_controller.migrate_vm(dom_name, dom_id, source_node_id, dest_node_id, live, force, all)
        return result

    def get_vm_config_file(self, dom_id, node_id):
        result = None
        result = self.node_controller.get_vm_config_file(dom_id, node_id)
        return result

    def save_vm_config_file(self, dom_id, node_id, content):
        result = None
        result = self.node_controller.save_vm_config_file(dom_id, node_id, content)
        return result
    # sam 1026
    def remove_vm_config_file(self, dom_id, node_id, force):
        result = None
        result = self.node_controller.remove_vm_config_file(dom_id, node_id,force='force_cli')
        return result
    # sam 1026
    def remove_vm(self, dom_id, node_id, force, date=None, time=None):
        result = None
        result = self.node_controller.remove_vm(dom_id, node_id, date, time,force='force_cli')
        return result

    def provision_vm(self, group_id, node_id, image, vmname, Memory, Vcpu, date=None, time=None):
        result = self.node_controller.cli_provision_vm(group_id, node_id, image, vmname, Memory, Vcpu, date, time)
        return result

    def get_migrate_target_nodes(self, node_id):
        result = None
        result = self.node_controller.get_target_nodes(node_id)
        return result

    def vm_config_settings(self, image_id, config, mode, node_id=None, group_id=None, dom_id=None, vm_name=None, date=None, time=None, _dc=None):
        result = None
        result = self.node_controller.vm_config_settings(image_id, config, mode, node_id, group_id, dom_id, vm_name, date, time)
        return result

    def edit_vm_settings(self, nodeid, domid, memory='', cpu=''):
        result = self.node_controller.edit_vm_settings(nodeid, domid, memory, cpu)
        return result

    def get_vm_config(self, domId, nodeId, _dc=None):
        result = None
        result = self.node_controller.get_vm_config(domId, nodeId)
        return result

    def get_shutdown_event_map(self, _dc=None):
        result = self.node_controller.get_shutdown_event_map()
        return result

    def get_miscellaneous_configs(self, image_id=None, dom_id=None, node_id=None, group_id=None, action=None, _dc=None):
        result = self.node_controller.get_miscellaneous_configs(image_id, dom_id, node_id, group_id, action)
        return result

    def node_get_provisioning_configs(self, image_id=None, _dc=None):
        result = self.node_controller.get_provisioning_configs(image_id)
        return result

    def get_initial_vmconfig(self, image_id=None, mode=None, _dc=None):
        result = self.node_controller.get_initial_vmconfig(image_id, mode)
        return result

    def get_disks(self, image_id=None, mode=None, dom_id=None, node_id=None, group_id=None, action=None, _dc=None):
        result = None
        result = self.node_controller.get_disks(image_id, mode, dom_id, node_id, group_id, action)
        return result

    def get_disks_options_map(self, _dc=None):
        result = self.node_controller.get_disks_options_map()
        return result

    def node_get_disks_type_map(self, type, mode, _dc=None):
        result = self.node_controller.get_disks_type_map(type, mode)
        return result

    def get_vmdevice_map(self, platform, _dc=None):
        result = self.node_controller.get_vmdevice_map(platform)
        return result

    def get_device_mode_map(self, _dc=None):
        result = self.node_controller.get_device_mode_map()
        return result

    def get_ref_disk_format_map(self, format_type, _dc=None):
        result = self.node_controller.get_ref_disk_format_map(format_type)
        return result

    def get_disk_fs_map(self, _dc=None):
        result = self.node_controller.get_disk_fs_map()
        return result

    def get_ref_disk_type_map(self, _dc=None):
        result = self.node_controller.get_ref_disk_type_map()
        return result

    def list_dir_contents(self, node_id=None, directory=None, _dc=None):
        result = None
        result = self.node_controller.get_dir_contents(node_id, directory)
        return dict('true', result)

    def make_dir(self, node_id, parent_dir, dir, _dc=None):
        result = None
        result = self.node_controller.make_dir(node_id, parent_dir, dir)
        return result

    def add_server_pool(self, group_name, site_id):
        result = self.node_controller.add_group(group_name, site_id)
        return result

    def remove_server_pool(self, group_id):
        result = self.node_controller.remove_group(group_id)
        return result

    def migrate_down_vms(self, group_id, status):
        result = self.node_controller.mig_down_vms(group_id, status)
        return result

    def get_alloc_node(self, group_id, image_id=None):
        result = None
        result = self.node_controller.get_alloc_node(group_id, image_id)
        return result

    def get_boot_device(self, dom_id):
        result = None
        result = self.node_controller.get_boot_device(dom_id)
        return result

    def set_boot_device(self, dom_id, boot):
        result = self.node_controller.set_boot_device(dom_id, boot)
        return result

    def get_parent_id(self, node_id):
        result = None
        result = self.node_controller.get_parent_id(node_id)
        return result

    def entity_context(self, node_id):
        result = None
        result = self.node_controller.entity_context(session['auth'], node_id)
        return result

    def get_updated_entities(self, user_name, _dc=None):
        result = None
        result = self.node_controller.get_updated_entities(user_name)
        return result

    def get_servers(self, groupId):
        result = None
        result = self.node_controller.get_nodes(groupId)
        return result

    def list_server_pools(self, site_id):
        result = self.node_controller.list_groups(site_id)
        return result

    def set_server_maintenance(self, node_id, maintenance_info):
        result = None
        result = self.node_controller.set_server_maintenance(node_id, maintenance_info, 'True')
        return result



