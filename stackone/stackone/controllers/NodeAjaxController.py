import pylons
import simplejson as json
from stackone.lib.base import BaseController
from stackone.controllers.ControllerBase import ControllerBase
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.NodeService import NodeService
from stackone.viewModel.VMService import VMService
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
from stackone.model.Authorization import AuthorizationService
from stackone.controllers.XMLRPC.NodeXMLRPCController import NodeXMLRPCController
from pylons.controllers.util import forward
from pylons.controllers import XMLRPCController
LOGGER = logging.getLogger('stackone.controllers')
from stackone.controllers.NodeController import NodeController

class NodeAjaxController(ControllerBase):
    tc = stackone.viewModel.TaskCreator.TaskCreator()
    node_controller = stackone.controllers.NodeController.NodeController()

    @expose(template='json')
    def add_group(self, group_name, site_id):
        result = self.node_controller.add_group(group_name, site_id)
        return result

    @expose(template='json')
    def add_node(self, platform, hostname, username, password, ssh_port, use_keys, is_standby, group_id, protocol=None, xen_port=8006, xen_migration_port=8002, address=None, **kw):
        result = self.node_controller.add_node(platform, hostname, username, password, ssh_port, use_keys, is_standby, group_id, protocol, xen_port, xen_migration_port, address)
        return result

    @expose(template='json')    
    def check_vm_name(self, vm_name, vm_id):
        result = None
        result = self.node_controller.check_vm_name(vm_name, vm_id)
        return result

    @expose(template='json')
    def connect_node(self, node_id, username='root', password=None):
        result = None
        result = self.node_controller.connect_node(node_id, username, password)
        return result

    @expose(template='json')
    def delete_task(self, task_id,_dc=None):
        result = None
        result = self.node_controller.delete_task(task_id)
        return result

    @expose(template='json')
    def edit_node(self, node_id, platform,hostname, username, password, ssh_port, use_keys, is_standby, protocol=None, xen_port=8006, xen_migration_port=8002, address=None, **kw):
        result = None
        result = self.node_controller.edit_node(node_id, platform, hostname, username, password, ssh_port, use_keys, is_standby, protocol, xen_port, xen_migration_port, address)
        return result

    @expose(template='json')
    def edit_task(self, task_id, date, time,_dc=None):
        result = None
        result = self.node_controller.edit_task(task_id, date, time)
        return result

    @expose(template='json')
    def entity_context(self, node_id):
        result = None
        result = self.node_controller.entity_context(node_id)
        return result

    @expose(template='json')
    def get_alloc_node(self, group_id, image_id=None):
        result = None
        result = self.node_controller.get_alloc_node(group_id, image_id)
        return result

    @expose(template='json')
    def get_annotation(self, node_id, _dc=None):
        result = None
        result = self.node_controller.get_annotation(node_id)
        return result

    @expose(template='json')
    def get_boot_device(self, dom_id):
        result = None
        result = self.node_controller.get_boot_device(dom_id)
        return result

    @expose(template='json')
    def get_command(self, node_id, dom_id, cmd,_dc=None):
        result = None
        result = self.node_controller.get_command(node_id, dom_id, cmd)
        return result
    # sam 1025
    @expose(template='json')
    def get_command_list(self, node_id, _dc=None):
        result = None
        result = self.node_controller.get_command_list(node_id)
        return result
    # sam 1025
    @expose(template='json')
    def get_data_store(self, host_id, _dc=None):
        result = None
        result = self.node_controller.get_data_store(host_id)
        return result
    @expose(template='json')
    def get_device_mode_map(self,_dc=None):
        result = self.node_controller.get_device_mode_map()
        return result

    @expose(template='json')
    def get_disk_fs_map(self,_dc=None):
        result = self.node_controller.get_disk_fs_map()
        return result

    @expose(template='json')
    def get_disks(self, image_id=None, mode=None, dom_id=None, node_id=None, group_id=None, action=None, _dc=None):
        result = None
        result = self.node_controller.get_disks(image_id, mode, dom_id, node_id, group_id, action)
        return result

    @expose(template='json')
    def get_disks_options_map(self, _dc=None):
        result = self.node_controller.get_disks_options_map()
        return result

    @expose(template='json')
    def get_disks_type_map(self, type, mode,_dc=None):
        result = self.node_controller.get_disks_type_map(type, mode)
        return result

    @expose(template='json')
    def get_group_vars(self, group_id,_dc=None):
        result = None
        result = self.node_controller.get_group_vars(group_id)
        return result

    @expose(template='json')
    def get_initial_vmconfig(self, image_id=None, mode=None, _dc=None):
        result = self.node_controller.get_initial_vmconfig(image_id, mode)
        return result

    @expose(template='json')
    def get_managed_nodes(self, site_id=None, group_id=None, **kw):
        result = None
        result = self.node_controller.get_managed_nodes(site_id, group_id)
        return result

    @expose(template='json')
    def get_migrate_target_nodes(self, node_id):
        result = None
        result = self.node_controller.get_migrate_target_nodes(node_id)
        return result

    @expose(template='json')
    def get_migrate_target_sps(self, node_id, sp_id):
        result = None
        result = self.node_controller.get_migrate_target_sps(node_id, sp_id)
        return result

    @expose(template='json')
    def get_miscellaneous_configs(self, image_id=None, dom_id=None, node_id=None, group_id=None, action=None, _dc=None):
        result = self.node_controller.get_miscellaneous_configs(image_id, dom_id, node_id, group_id, action)
        return result

    @expose(template='json')
    def get_node_info(self, node_id, level, _dc=None):
        result = None
        result = self.node_controller.get_node_info(node_id, level)
        return result

    @expose(template='json')
    def get_node_properties(self, node_id):
        result = None
        result = self.node_controller.get_node_properties(node_id)
        return result

    @expose(template='json')
    def get_node_status(self, node_id=None, dom_id=None):
        result = self.node_controller.get_node_status(node_id=node_id, dom_id=dom_id)
        return result

    @expose(template='json')
    def get_parent_id(self, node_id):
        result = None
        result = self.node_controller.get_parent_id(node_id)
        return result

    @expose(template='json')
    def get_platform(self, node_id, type, **kw):
        result = None
        result = self.node_controller.get_platform(node_id, type)
        return result

    @expose(template='json')
    def get_provisioning_configs(self, image_id=None, _dc=None):
        result = self.node_controller.get_provisioning_configs(image_id)
        return result

    @expose(template='json')
    def get_quiescent_script_options(self, dom_id=None, node_id=None, _dc=None):
        result = None
        result = self.node_controller.get_quiescent_script_options(dom_id, node_id)
        return result

    @expose(template='json')
    def get_ref_disk_format_map(self, format_type,_dc=None):
        result = self.node_controller.get_ref_disk_format_map(format_type)
        return result

    @expose(template='json')
    def get_ref_disk_type_map(self,_dc=None):
        result = self.node_controller.get_ref_disk_type_map()
        return result

    @expose(template='json')
    def get_schedule_values(self, type,_dc=None):
        result = None
        result = self.node_controller.get_schedule_values(type)
        return result

    @expose(template='json')
    def get_server_maintenance(self, node_id):
        """
        Maintenance
        """
        result = None
        result = self.node_controller.get_server_maintenance(node_id)
        return result

    @expose(template='json')
    def get_servers(self, sp_id, node_id, _dc=None):
        """
        Maintenance
        """
        result = None
        result = self.node_controller.get_servers(sp_id, node_id)
        return result

    @expose(template='json')
    def get_shutdown_event_map(self, _dc=None):
        result = self.node_controller.get_shutdown_event_map()
        return result

    @expose(template='json')
    def get_task_display(self, _dc=None):
        result = None
        result = self.node_controller.get_task_display()
        return result

    @expose(template='json')
    def get_tasks(self, node_id, node_type,display_type=None, _dc=None):
        result = None
        result = self.node_controller.get_tasks(node_id, node_type, display_type)
        return result

    @expose(template='json')
    def get_updated_entities(self, user_name, _dc=None):
        result = None
        result = self.node_controller.get_updated_entities(user_name)
        return result

    @expose(template='json')
    def get_vm_config(self, domId, nodeId, _dc=None):
        result = None
        result = self.node_controller.get_vm_config(domId, nodeId)
        return result

    @expose(template='json')
    def get_vm_config_file(self, dom_id, node_id):
        result = None
        result = self.node_controller.get_vm_config_file(dom_id, node_id)
        return result

    @expose(template='json')
    def get_vmdevice_map(self, platform,_dc=None):
        result = self.node_controller.get_vmdevice_map(platform)
        return result

    @expose(template='json')
    def get_vmschedule_status(self, dom_id, action,_dc=None):
        result = None
        result = self.node_controller.get_vmschedule_status(dom_id, action)
        return result

    @expose(template='json')
    def import_configs(self, node_id, paths,action=None, date=None, time=None):
        result = None
        result = self.node_controller.import_configs(node_id, paths, action, date, time)
        return result

    @expose(template='json')
    def import_vm_config(self, node_id, directory, filenames):
        result = None
        result = self.node_controller.import_vm_config(node_id, directory, filenames)
        return result

    @expose(template='json')
    def is_in_maintenance_mode(self, node_id,_dc=None):
        """
        Maintenance
        """
        result = None
        result = self.node_controller.is_in_maintenance_mode(node_id)
        return result

    @expose(template='json')
    def list_dir_contents(self,  node_id=None, directory=None, _dc=None):
        result = None
        result = self.node_controller.list_dir_contents(node_id, directory)
        return result

    @expose(template='json')
    def list_vm_configs(self, node_id=None, directory=None, _dc=None):
        result = None
        result = self.node_controller.list_vm_configs(node_id, directory)
        return result

    @expose(template='json')
    def make_dir(self, node_id, parent_dir, dir, _dc=None):
        result = None
        result = self.node_controller.make_dir(node_id, parent_dir, dir)
        return result

    @expose(template='json')
    def migrate_vm(self, dom_name, dom_id, source_node_id, dest_node_id, live='true', force='false', all='false', date=None, time=None):
        result = None
        result = self.node_controller.migrate_vm(dom_name, dom_id, source_node_id, dest_node_id, live, force, all)
        return result

    @expose(template='json')
    def process_annotation(self, node_id, text=None, user=None, _dc=None):
        result = None
        result = self.node_controller.process_annotation(node_id, text, user)
        return result

    @expose(template='json')
    def provision_vm(self, image, node_id, group_id, vm_name, memory, vcpus, date=None, time=None):
        result = self.node_controller.cli_provision_vm(image, node_id, group_id, vm_name, memory, vcpus, date, time)
        return result

    @expose(template='json')
    def refresh_node_info(self, node_id, level,_dc=None):
        result = None
        result = self.node_controller.refresh_node_info(node_id)
        return result

    @expose(template='json')
    def remove_group(self, group_id):
        result = self.node_controller.remove_group(group_id)
        return result

    @expose(template='json')
    def remove_node(self, node_id, force='False'):
        result = None
        result = self.node_controller.remove_node(node_id, force)
        return result

    @expose(template='json')
    def remove_vm(self, dom_id, node_id, force='False', date=None, time=None):
        result = None
        result = self.node_controller.remove_vm(dom_id, node_id, date, time, eval(force))
        return result

    @expose(template='json')
    def remove_vm_config_file(self, dom_id, node_id):
        result = None
        result = self.node_controller.remove_vm_config_file(dom_id, node_id,force_cli = True)
        return result

    @expose(template='json')
    def restore_vm(self, node_id, directory, filenames, date=None, time=None):
        file = os.path.join(directory, filenames)
        print '#####restore_vm file#####',file
        result = self.node_controller.restore_vm(node_id, file, date, time)
        return result


    @expose(template='json')
    def save_group_vars(self, group_id, _dc=None, **attrs):
        result = None
        result = self.node_controller.save_group_vars(group_id, attrs)
        return result

    @expose(template='json')
    def save_vm(self, dom_id, node_id, directory, filenames, date=None, time=None):
        result = None
        result = self.node_controller.save_vm(dom_id, node_id,directory,filenames, date, time)
        return result

    @expose(template='json')
    def save_vm_config_file(self, dom_id, node_id, content):
        result = None
        result = self.node_controller.save_vm_config_file(dom_id, node_id, content)
        return result

    @expose(template='json')
    def server_action(self, node_id, action, date=None, time=None):
        result = None
        result = self.node_controller.server_action(node_id, action, date, time)
        return result

    @expose(template='json')
    def set_boot_device(self, dom_id, boot):
        result = self.node_controller.set_boot_device(dom_id, boot)
        return result

    @expose(template='json')
    def set_server_maintenance(self, node_id, maintenance_info):
        """
        Maintenance
        """
        result = None
        result = self.node_controller.set_server_maintenance(node_id, maintenance_info)
        return result

    @expose(template='json')
    def transfer_node(self, node_id, source_group_id, dest_group_id, forcefully):
        result = None
        result = self.node_controller.transfer_node(node_id, source_group_id, dest_group_id, forcefully)
        return result

    @expose(template='json')
    def vm_action(self, dom_id, node_id, action,date=None, time=None):
        result = None
        result = self.node_controller.vm_action(dom_id, node_id, action, date, time)
        return result

    @expose(template='json')
    def vm_config_settings(self, image_id, config, mode, node_id=None, group_id=None, dom_id=None, vm_name=None, date=None, time=None, _dc=None):
        result = None
        result = self.node_controller.vm_config_settings(image_id, config, mode, node_id, group_id, dom_id, vm_name, date, time)
        return result

    @expose()
    def xmlrpc(self):
        return forward(NodeXMLRPCController())
        
    #from vm to image
    @expose(template='json')
    def is_vm_running(self, node_id, _dc=None):
        result = None
        result = self.node_controller.is_vm_running(node_id)
        return result
    ###Vcenter
    @expose(template='json')
    def get_vcenter_nodes(self, vm_id, _dc=None):
        result = None
        result = self.node_controller.get_vcenter_nodes(vm_id)
        return result
    ##archer 20131129
    @expose(template='json')
    def upload_iso(self, file,_dc=None):
        result = self.node_controller.upload_iso(file)
        return result
    @expose(template='json')
    def hot_add_usb(self, dom_id,node_id,usb_info,_dc=None):
        result = self.node_controller.hot_add_usb(dom_id,node_id,usb_info)
        return result
    @expose(template='json')
    def hot_del_usb(self, dom_id,node_id,usb_info,_dc=None):
        result = self.node_controller.hot_del_usb(dom_id,node_id,usb_info)
        return result
    @expose(template='json')
    def get_usb_pci(self, node_id,_dc=None):
        result = self.node_controller.get_usb_pci(node_id)
        return result