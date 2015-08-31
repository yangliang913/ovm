# -*- coding: utf-8 -*-
import pylons
import simplejson as json
from stackone.lib.base import BaseController
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.NodeService import NodeService
from stackone.viewModel.VMService import VMService
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.controllers.ControllerImpl import ControllerImpl
from stackone.core.utils.utils import to_unicode, to_str, print_traceback, performance_debug
from stackone.model import DBSession
from stackone.model.VM import VM
from stackone.model.services import Task
import stackone.core.utils.constants
constants = stackone.core.utils.constants
DEBUG_CAT = constants.DEBUG_CATEGORIES
from stackone.model.Maintenance import Maintenance
import logging
import tg
import os
LOGGER = logging.getLogger('stackone.controllers')
from pylons.controllers import XMLRPCController
import os
import pprint
from stackone.controllers.ControllerBase import ControllerBase
class NodeController(ControllerBase):
    __doc__ = '\n\n    '
    tc = TaskCreator()
    node_service = NodeService()
    vm_service = VMService()
    def get_platform(self, node_id, type, **result):
        try:
            self.authenticate()
            result = self.node_service.get_platform(session['auth'], node_id, type)

        except Exception as ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'", '')}
        return dict(success='true', platform=result)


    def get_managed_nodes(self, site_id=None, group_id=None, **result):
        result = None
        self.authenticate()
        result = self.node_service.get_managed_nodes(session['auth'], group_id, site_id)
        return result

    def get_node_info(self, node_id, level, _dc=None):
        result = None
        self.authenticate()
        if level == constants.DOMAIN:
            result = self.node_service.get_vm_info(session['auth'], node_id)
        else:
            if level == constants.MANAGED_NODE:
                result = self.node_service.get_node_info(session['auth'], node_id)

        return result


    def refresh_node_info(self, node_id, level, _dc=None):
        result = None
        self.authenticate()
        if level == constants.MANAGED_NODE:
            result = self.node_service.refresh_node_info(session['auth'], node_id)

        return result


    def get_group_vars(self, group_id, _dc=None):
        result = None
        self.authenticate()
        result = self.node_service.get_group_vars(session['auth'], group_id)
        return result

    def save_group_vars(self, group_id, attrs):
        result = None
        self.authenticate()
        result = self.node_service.save_group_vars(session['auth'], group_id, attrs)
        return result

    def add_node(self, platform, hostname, username, password, ssh_port, use_keys, is_standby, group_id, protocol, xen_port, xen_migration_port, address, **kw):
        try:
            result = None
            self.authenticate()
            result = self.node_service.add_node(session['auth'], group_id, platform, hostname, ssh_port, username, password, protocol, xen_port, xen_migration_port, use_keys, address, is_standby)
            return result

        except Exception as ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'", '')}


    def edit_node(self, node_id, platform, hostname, username, password, ssh_port, use_keys, is_standby, protocol=None, xen_port=8006L, xen_migration_port=8002L, address=None, **result):
        try:
            result = None
            self.authenticate()
            result = self.node_service.edit_node(session['auth'], node_id, platform, hostname, ssh_port, username, password, protocol, xen_port, xen_migration_port, use_keys, address, is_standby)
            return result

        except Exception as ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'", '')}


    def edit_node_cli(self, node_id, platform, hostname, username, password, ssh_port, use_keys, is_standby, protocol=None, xen_port=8006L, xen_migration_port=8002L, address=None, **result):
        try:
            result = None
            self.authenticate()
            node = self.node_service.get_managed_node(session['auth'], node_id)
            if (platform == None) or (platform == False):
                platform = node.get_platform()
            credentials = node.get_credentials()
            if (username == False):
                username = credentials['username']
            if (ssh_port == False) or (ssh_port == None):
                ssh_port = credentials['ssh_port']
            if use_keys == None:
                use_keys = credentials['use_keys']

            if is_standby == 'no':
                is_standby = 'False'

            result = self.node_service.edit_node(session['auth'], node_id, platform, hostname, ssh_port, username, password, protocol, xen_port, xen_migration_port, use_keys, address, is_standby)
            return result

        except Exception as ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'", '')}



    def change_server_password(self, node_ids, newpassword):
        try:
            self.authenticate()
            result = self.node_service.change_server_password(session['auth'], node_ids, newpassword)

        except Exception as e:
            print_traceback()
            return dict(success=False, msg=to_str(e))

        return dict(success=True, result=result)


    def remove_node(self, node_id, force='False'):
        result = None
        self.authenticate()
        result = self.node_service.remove_node(session['auth'], node_id, eval(force))
        return result

    def get_node_properties(self, node_id):
        try:
            self.authenticate()
            result = self.node_service.get_node_properties(session['auth'], node_id)
            return dict(success=True, node=result.toJson())

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def connect_node(self, node_id, username='root', password=None):
        result = None
        self.authenticate()
        result = self.node_service.connect_node(session['auth'], node_id, username, password)
        return result

    def vm_action(self, dom_id, node_id, action, date=None, time=None):
        self.authenticate()
        try:
            dom = DBSession().query(VM).filter(VM.id == dom_id).one()
            tasks = DBSession.query(Task).filter(Task.task_id.in_([dom.start_taskid, dom.shutdown_taskid])).all()
            if len(tasks) > 0 and len(tasks[0].result) == 0 and action == tasks[0].name:
                self.tc.delete_task([tasks[0].task_id])
            result = to_str(self.tc.vm_action(session['auth'], dom_id, node_id, action, date, time))
            wait_time = None
            if action == constants.START:
                dom.start_taskid = result
                wait_time = dom.get_wait_time('view_console')
            else:
                if action == constants.SHUTDOWN:
                    dom.shutdown_taskid = result

            DBSession.add(dom)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex))

        return dict(success=True, msg='Task submitted.', taskid=result, wait_time=wait_time)

        


    def transfer_node(self, node_id, source_group_id, dest_group_id, forcefully):
        result = None
        self.authenticate()
        result = self.node_service.transfer_node(session['auth'], node_id, source_group_id, dest_group_id, forcefully)
        return result

    def server_action(self, node_id, action, date=None, time=None):
        self.authenticate()
        try:
            result = to_str(self.tc.server_action(session['auth'], node_id, action, date, time))

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex))

        return dict(success=True, msg='Task submitted.', taskid=result)


    def import_vm_config(self, node_id, directory, filenames, action=False, date=None, time=None):
        self.authenticate()
        path = ''
        paths = ''
        try:
            for filename in filenames:
                path = os.path.join(directory, filename)
                paths += path + ','

            paths = paths[0:-1]
            doms = self.import_configs(node_id, paths, action, date, time)

        except Exception as ex:
            print_traceback()
            err = to_str(ex).replace("'", ' ')
            LOGGER.error(err)
            return dict(success=False, msg=err)

        return doms


    def import_configs(self, node_id, paths, action=False, date=None, time=None):
        self.authenticate()

        try:
            result = to_str(self.tc.import_vm_action(session['auth'], node_id, action, paths, date, time))

        except Exception as ex:
            print_traceback()
            err = to_str(ex).replace("'", ' ')
            LOGGER.error(err)
            return dict(success=False, msg=err)

        return dict(success=True, msg='Import Virtual Machine task submitted', taskid=result)


    def restore_vm(self, node_id, file, date=None, time=None):
        self.authenticate()
        try:
            result = to_str(self.tc.restore_vm(session['auth'], node_id, file, date, time))
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex))

        return dict(success=True, msg='Restore Virtual Machine task submitted.', taskid=result)


    def save_vm(self, dom_id, node_id, directory, filenames, date=None, time=None):
        self.authenticate()

        try:
            file = os.path.join(directory, filenames)
            result = self.tc.save_vm(session['auth'], dom_id, node_id, directory,file,date, time)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", '').replace('\n', ''))

        return dict(success=True, msg='Snapshot Virtual Machine task submitted', taskid=result)


    def migrate_vm(self, dom_name, dom_id, source_node_id, dest_node_id, live='true', force='false', all='false', date=None, time=None):
        self.authenticate()
        result = self.node_service.migrate_vm(session['auth'], dom_name, dom_id, source_node_id, dest_node_id, live, force, all)

        try:
            if result.get('submit', None) == True:
                taskid = self.tc.migrate_vm(session['auth'], result['dom_list'], source_node_id, dest_node_id, live, force, all, date, time)
                return dict(success=True, msg='Migrate Task submitted.', taskid=taskid)

            return result

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex))

        return result


    def get_vm_config_file(self, dom_id, node_id):
        result = None
        self.authenticate()

        try:
            result = self.node_service.get_vm_config_file(session['auth'], dom_id, node_id)
            result = json.dumps(dict(success=True, content=result))
            return result

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))



    def save_vm_config_file(self, dom_id, node_id, content):
        result = None
        self.authenticate()
        result = self.node_service.save_vm_config_file(session['auth'], dom_id, node_id, content)
        return result
    # sam 1025
    def remove_vm_config_file(self, dom_id, node_id, force_cli=False):
        status = {}
        self.authenticate()
        try:
            if force_cli != True:
                status = self.node_service.get_node_status(session['auth'],node_id=node_id, dom_id=dom_id)
                if status and status['part_of_vdc']==True:
                    raise Exception('This VM is part of VDC .This operation is not recommended.')
            self.node_service.remove_vm_config_file(session['auth'],dom_id,node_id)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        return dict(success=True, msg='VM config removed.')

    #sam 1025
    def remove_vm(self, dom_id, node_id, date=None, time=None, force=False, force_cli=False):
        self.authenticate()
        status = {}
        try:
            if force_cli != True:
                status = self.node_service.get_node_status(session['auth'],node_id=node_id,dom_id=dom_id)
                if status and status['part_of_vdc'] == True:
                    raise Exception('This VM is part of VDC .This operation is not recommended.')
            dom = DBSession().query(VM).filter(VM.id == dom_id).one()
            tasks = DBSession.query(Task).filter(Task.task_id.in_([dom.delete_taskid])).all()
            if len(tasks) > 0 and len(tasks[0].result) == 0:
                self.tc.delete_task([tasks[0].task_id])

            result = to_str(self.tc.vm_remove_action(session['auth'], dom_id, node_id, force, date, time))
            if date is not None and time is not None:
                dom.delete_taskid = result
                DBSession.add(dom)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex))

        return dict(success=True, msg='Remove Virtual Machine Task Submitted.', taskid=result)

        

    def get_node_status(self, node_id=None, dom_id=None):
        
        try:
            result = self.node_service.get_node_status(session['auth'],node_id=node_id, dom_id=dom_id)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex))

        return dict(success=True, result=result)


    def get_migrate_target_nodes(self, node_id):
        result = None
        self.authenticate()
        
        try:
            result = self.node_service.get_target_nodes(session['auth'], node_id=node_id)

        except Exception as ex:
            print_traceback()
            return dict(success='false', msg=to_str(ex).replace("'", ''))

        return dict(success='true', nodes=result)


    def get_migrate_target_sps(self, node_id, sp_id):
        result = None
        self.authenticate()
        
        try:
            result = self.node_service.get_migrate_target_sps(session['auth'], node_id=node_id, sp_id=sp_id)

        except Exception as ex:
            print_traceback()
            return dict(success='false', msg=to_str(ex).replace("'", ''))

        return dict(success='true', nodes=result)


    def vm_config_settings(self, image_id, config, mode, node_id=None, group_id=None, dom_id=None, vm_name=None, date=None, time=None, _dc=None):
        self.authenticate()

        try:
            if mode in ('PROVISION_VM',):
                self.handle_provisioning(session['auth'], image_id, config, mode, node_id, group_id, dom_id, vm_name, date, time)
                result = None
            else:
                if mode in ('EDIT_VM_INFO',):
                    self.tc.config_settings(session['auth'], image_id, config, mode, node_id, group_id, dom_id, vm_name, date, time)
                    result = None
                else:
                    result = self.node_service.vm_config_settings(session['auth'], image_id, config, mode, node_id, group_id, dom_id, vm_name)

        except Exception as e:
            print_traceback()
            return dict(success=False, msg='Error:' + to_str(e).replace("'", ' '))

        return dict(success=True, vm_config=result)


    def check_vm_name(self, vm_name, vm_id):
        query = DBSession.query(VM)
        if vm_id:
            query = query.filter(not_(VM.id == vm_id))
        vm = query.filter(VM.name == vm_name).first()
        if vm:
            return dict(success=False, msg='VM <b>' + vm_name + '</b> already exists.')

        return dict(success=True, msg='')


    def handle_provisioning(self, auth, image_id, config, mode, node_id=None, group_id=None, dom_id=None, vm_name=None, date=None, time=None):
        try:
            import simplejson as json
            prov_config = json.loads(config)
            scheduling_dic = prov_config.get('scheduling_object')
            print 'scheduling_dic==',
            print scheduling_dic
            if scheduling_dic.get('prov_on') == 'Later':
                date = scheduling_dic.get('prov_date')
                time = scheduling_dic.get('prov_time')
                self.tc.config_settings(auth, image_id, config, mode, node_id, group_id, dom_id, vm_name, date, time)
            else:
                self.tc.config_settings(auth, image_id, config, mode, node_id, group_id, dom_id, vm_name, None, None)

        except Exception as e:
            print_traceback()


    def edit_vm_settings(self, nodeid, domid, memory, cpu):
        self.authenticate()
        
        try:
            result = self.node_service.edit_vm_information(session['auth'], nodeid, domid, memory, cpu)

        except Exception as e:
            print_traceback()
            return dict(success=False, msg='Error:' + to_str(e).replace("'", ' '))

        return dict(success=True, msg=result)


    def cli_provision_vm(self, group_id, node_id, image, vmname, memory, vcpu, date, time, cloud=False):
        try:
            self.authenticate()
            image_id = self.get_entity_id(image, '7')
            if type(image_id) != {}:
                taskid = self.tc.config_settings(session['auth'], image_id, None, 'PROVISION_VM', node_id, group_id, None, vmname, date, time, True, int(memory), int(vcpu), cloud)
                return dict(success=True, msg='Provisioning task of %s completed' % vmname, taskid=taskid)

            return dict(success=False, msg=image_id['msg'])

        except Exception as e:
            print_traceback()
            return dict(success=False, msg='Error:' + to_str(e).replace("'", ' '))



    def create_cms_cloud_vm(self, sp_id, node_id, image, vmname, memory, vcpu, cloud, date=None, time=None, csep_context=None, network=None, csep_id=None, vdc_name=None):
        try:
            self.authenticate()
            taskid = self.tc.config_settings(session['auth'], image.id, None, 'PROVISION_VM', node_id, sp_id, None, vmname, date, time, True, memory, vcpu, cloud, csep_context, network, csep_id, vdc_name)
            return dict(success=True, msg='Provisioning task of %s completed' % vmname, taskid=taskid)

        except Exception as e:
            print_traceback()
            return dict(success=False, msg='Error:' + to_str(e).replace("'", ' '))



    def get_vm_config(self, domId, nodeId, _dc=None):
        self.authenticate()

        try:
            result = self.node_service.get_vm_config(session['auth'], domId, nodeId)

        except Exception as e:
            print_traceback()
            return dict(success=False, msg='Error:' + to_str(e).replace("'", ' '))

        return dict(success=True, vm_config=result)


    def get_shutdown_event_map(self, _dc=None):
        self.authenticate()
        result = self.node_service.get_shutdown_event_map()
        return result

    def get_miscellaneous_configs(self, image_id=None, dom_id=None, node_id=None, group_id=None, action=None, _dc=None):
        
        try:
            self.authenticate()
            result = self.vm_service.get_miscellaneous_configs(session['auth'], image_id, dom_id, node_id, group_id, action)
            return result

        except Exception as e:
            print_traceback()
            return dict(success=False, msg='Error:' + to_str(e).replace("'", ' '))


    def get_provisioning_configs(self, image_id=None, _dc=None):
        try:
            self.authenticate()
            result = self.vm_service.get_provisioning_configs(session['auth'], image_id)
            return result

        except Exception as e:
            print_traceback()
            return dict(success=False, msg='Error:' + to_str(e).replace("'", ' '))


    def get_initial_vmconfig(self, image_id=None, mode=None, _dc=None):
        self.authenticate()
        result = self.vm_service.get_initial_vmconfig(session['auth'], image_id, mode)
        return dict(success=True, vm_config=result)

    def get_disks(self, image_id=None, mode=None, dom_id=None, node_id=None, group_id=None, action=None, _dc=None):
        result = None
        self.authenticate()

        try:
            result = self.vm_service.get_disks(session['auth'], image_id, mode, dom_id, node_id, group_id, action)

        except Exception as e:
            print_traceback()
            return dict(success=False, msg=to_str(e))

        return dict(success=True, disks=result)


    def get_disks_options_map(self, _dc=None):
        result = None
        self.authenticate()
        result = self.vm_service.get_disks_options_map()
        return result

    def get_disks_type_map(self, type, mode, _dc=None):
        result = None
        self.authenticate()
        result = self.vm_service.get_disks_type_map(type, mode)
        return result

    def get_vmdevice_map(self, platform, _dc=None):
        result = None
        self.authenticate()
        result = self.vm_service.get_vmdevice_map(platform)
        return result

    def get_device_mode_map(self, _dc=None):
        result = None
        self.authenticate()
        result = self.vm_service.get_device_mode_map()
        return result

    def get_ref_disk_format_map(self, format_type, _dc=None):
        result = None
        self.authenticate()
        result = self.vm_service.get_ref_disk_format_map(format_type)
        return result

    def get_disk_fs_map(self, _dc=None):
        result = None
        self.authenticate()
        result = self.vm_service.get_disk_fs_map()
        return result

    def get_ref_disk_type_map(self, _dc=None):
        result = None
        self.authenticate()
        result = self.vm_service.get_ref_disk_type_map()
        return result

    def list_dir_contents(self, node_id=None, directory=None, _dc=None):
        result = None
        self.authenticate()
        
        try:
            result = self.node_service.get_dir_contents(session['auth'], node_id, directory)
            #return dict(success=False, msg='Error:' + to_str(e).replace("'", ' '))

        except Exception as ex:
            print_traceback()
            x = to_str(ex)
            err = ''
            if x.startswith('[Errno 2] No such file or directory:'):
                err = 'NoDirectory'
            return 'err'

        return dict(success='true', rows=result)


    def list_vm_configs(self, node_id=None, directory=None, _dc=None):
        result = None
        self.authenticate()
        
        try:
            result = self.node_service.list_vm_configs(session['auth'], node_id, directory)

        except Exception as ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'", '')}

        return dict(success='true', rows=result)


    def make_dir(self, node_id, parent_dir, dir, _dc=None):
        result = None
        self.authenticate()
        result = self.node_service.make_dir(session['auth'], node_id, parent_dir, dir)
        return result

    def add_group(self, group_name, site_id):
        self.authenticate()

        try:
            self.node_service.add_group(session['auth'], group_name, site_id)

        except Exception as ex:
            print_traceback()
            return ("{success:false,msg:'", to_str(ex).replace("'", ''), "'}")

        return ("{success: true,msg:'Server Pool ", group_name, " Added.'}")


    def remove_group(self, group_id):
        self.authenticate()

        try:
            self.node_service.remove_group(session['auth'], group_id)

        except Exception as ex:
            print_traceback()
            return ("{success:false,msg:'", to_str(ex).replace("'", ''), "'}")

        return "{success: true,msg:'Server Pool Removed.'}"


    def mig_down_vms(self, group_id, status):
        self.authenticate()

        try:
            self.node_service.mig_down_vms(session['auth'], group_id, status)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

        return dict(success=True, msg='')


    def get_alloc_node(self, group_id, image_id=None):
        result = None
        self.authenticate()
        result = self.node_service.get_alloc_node(session['auth'], group_id, image_id)
        return result

    def get_boot_device(self, dom_id):
        result = None
        self.authenticate()
        result = self.node_service.get_boot_device(session['auth'], dom_id)
        return result

    def set_boot_device(self, dom_id, boot):
        self.authenticate()
        result = self.node_service.set_boot_device(session['auth'], dom_id, boot)
        return result

    def get_parent_id(self, node_id):
        try:
            result = None
            self.authenticate()
            result = self.node_service.get_parent_id(session['auth'], node_id)

        except Exception as ex:
            print_traceback()
            return ("{success:false,msg:'", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', node_details=result)


    def entity_context(self, node_id):
        try:
            result = None
            self.authenticate()
            result = self.node_service.entity_context(session['auth'], node_id)

        except Exception as ex:
            print_traceback()
            return ("{success:false,msg:'", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', node_details=result)


    def get_updated_entities(self, user_name, _dc=None):
        try:
            result = None
            self.authenticate()
            result = self.node_service.get_updated_entities(user_name, session['group_names'])

        except Exception as ex:
            print_traceback()
            return "{success:false,msg:'"+to_str(ex).replace("'", '')+"'}"

        return dict(success='true', node_ids=result)


    def get_entity_id(self, name, type):
        result = ControllerImpl().get_entityid(name, type)
        return result

    def get_quiescent_script_options(self, dom_id=None, node_id=None, _dc=None):
        result = []
        self.authenticate()
        if dom_id:
            result = self.node_service.get_quiescent_script_options(session['auth'], dom_id, node_id)

        return dict(success='true', rows=result)


    def get_tasks(self, node_id, node_type, display_type=None):
        result = None

        try:
            result = self.node_service.get_tasks(session['auth'], node_id, node_type, display_type)

        except Exception as ex:
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', rows=result)


    def get_task_display(self):
        result = None
        result = self.node_service.get_task_display()
        return result

    def get_vmschedule_status(self, dom_id, action):
        result = None
        result = self.node_service.get_vmschedule_status(dom_id, action)
        return result

    def delete_task(self, task_id):
        result = None
        result = self.node_service.delete_task(task_id)
        return result

    def edit_task(self, task_id, date, time):
        result = None
        result = self.node_service.edit_task(task_id, date, time)
        return result

    def get_schedule_values(self, type):
        result = None
        result = self.node_service.get_schedule_values(type)
        return result
    #sam 1025
    def get_command_list(self, node_id):
        result = None
        result = self.vm_service.get_command_list(session['auth'],node_id)
        return result
    # sam 1025
    def get_data_store(self, host_id):
        info = None
        try:
            info = self.node_service.get_data_store(session['auth'],host_id)
            return dict(success=True, info=info)
        except Exception as ex:
            print_traceback()
            return dict(success=False,msg='Could not retrieve datastore list')
    def get_command(self, node_id, dom_id, cmd):
        result = None
        result = self.vm_service.get_command(session['auth'], node_id, dom_id, cmd)
        return result

    def get_server_maintenance(self, node_id):
        result = None
        result = self.node_service.get_server_maintenance(session['auth'], node_id)
        return result

    def set_server_maintenance(self, node_id, maintenance_info, cli=None):
        result = None
        if cli == 'True':
            info = maintenance_info
        else:
            print 'here==========Server maintenance======='
            info = json.loads(maintenance_info)
            info = info['info']

        result = self.node_service.do_server_maintenance(session['auth'], node_id, info)
        return result


    def get_servers(self, sp_id, node_id):
        result = None
        result = self.node_service.get_servers(session['auth'], sp_id, node_id)
        return result

    def is_in_maintenance_mode(self, node_id):
        result = None
        result = self.node_service.is_in_maintenance_mode(session['auth'], node_id)
        return result

    def process_annotation(self, node_id, text=None, user=None):
        self.authenticate()
        try:
            if user is None and text is None:
                result = self.node_service.get_annotation(session['auth'], node_id)
                if result.get('annotate'):
                    result = to_str(self.tc.clear_annotation(session['auth'], node_id))
                else:
                    return dict(success=False, msg='No annotations defined.')
            else:
                if user is not None:
                    result = to_str(self.tc.edit_annotation(session['auth'], node_id, text, user))
                else:
                    result = to_str(self.tc.add_annotation(session['auth'], node_id, text, user))

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex))

        return dict(success=True, msg='Task submitted.', taskid=result)

        

    def get_annotation(self, node_id):
        self.authenticate()
        result = None
        result = self.node_service.get_annotation(session['auth'], node_id)
        return result
        
    #from vm to image 
    def is_vm_running(self, node_id):
        self.authenticate()
        result = None
        result = self.vm_service.is_vm_running(session['auth'], node_id)
        return result
    #Vcenter
    def get_vcenter_nodes(self, vm_id):
        result = None
        result = self.node_service.get_vcenter_nodes(session['auth'], vm_id)
        return result
    # sam 1025
    def get_vnc_info_for_cloudcmsvm(self, auth, node_id, dom_id, address):
        result = self.node_service.get_vnc_info(auth, node_id, dom_id, address)
        return result
    ### archer 20131129
    def upload_iso(self,file):
        result = self.node_service.upload_iso(session['auth'],file)
        return result
    
    def hot_add_usb(self,dom_id,node_id,usb_info):
        result = self.node_service.hot_add_usb(session['auth'],dom_id,node_id,usb_info)
        return result
    def hot_del_usb(self,dom_id,node_id,usb_info):
        result = self.node_service.hot_del_usb(session['auth'],dom_id,node_id,usb_info)
        return result
    def get_usb_pci(self, node_id):
        result = self.node_service.get_usb_pci(session['auth'],node_id)
        return result       
