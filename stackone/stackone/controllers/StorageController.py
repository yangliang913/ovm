import pylons
import simplejson as json
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.core.utils.utils import wait_for_task_completion
from stackone.model import *
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.viewModel.StorageService import StorageService
from stackone.viewModel import Basic
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
import stackone.core.utils.constants
from stackone.viewModel import Basic
constants = stackone.core.utils.constants
from stackone.model.storage import StorageManager
from stackone.core.utils.utils import getHexID
import logging
import tg
import os
LOGGER = logging.getLogger('stackone.controllers')
from stackone.controllers.ControllerBase import ControllerBase
class StorageController(ControllerBase):
    tc = TaskCreator()
    manager = Basic.getGridManager()
    storage_service = StorageService()
    def get_storage_def_list(self, site_id=None, op_level=None, group_id=None, _dc=None):
        
        try:
            result = None
            self.authenticate()
            result = self.storage_service.get_storage_def_list(session['auth'], site_id, group_id, op_level)

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}

        return result


    def get_dc_storage_def_list(self, site_id=None, group_id=None, _dc=None):
        try:
            result = None
            self.authenticate()
            result = self.storage_service.get_dc_storage_def_list(session['auth'], site_id, group_id)

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}
        return result


    def get_storage_types(self, **result):
        try:
            self.authenticate()
            result = self.storage_service.get_storage_types()

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}

        return result


    def add_storage_def(self, type, site_id=None, op_level=None, group_id=None, node_id=None, sp_ids=None, added_manually=False, opts=None, cli=False):
        try:
            result = None
            self.authenticate()
            if cli == True:
                result = self.storage_service.add_storage_def_cli(session['auth'], site_id, group_id, node_id, type, opts, op_level, sp_ids, added_manually)
            else:
                self.tc.add_storage_def_task(session['auth'], site_id, group_id, node_id, type, opts, op_level, sp_ids, added_manually)
                result = "{success: true,msg: 'Task submitted.'}"

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}

        return result


    def edit_storage_def(self, storage_id, type, site_id=None, group_id=None, op_level=None, sp_ids=None, kw=None):
        try:
            result = None
            self.authenticate()
            result = self.storage_service.edit_storage_def(session['auth'], storage_id, site_id, group_id, type, op_level, sp_ids, kw)

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}

        return result


    def is_storage_allocated(self, storage_id):
        try:
            result = None
            result = self.storage_service.is_storage_allocated(storage_id)

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}

        return result


    def remove_storage_def(self, storage_id, site_id=None, op_level=None, group_id=None):
        try:
            result = None
            self.authenticate()
            self.tc.remove_storage_def_task(session['auth'], storage_id, site_id, group_id, op_level)
            result = "{success: true,msg: 'Task submitted.'}"

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}

        return result


    def remove_storage_def_cli(self, storage, site_id, op_level, group_id=None):
        try:
            self.authenticate()
            result = self.storage_service.remove_storage_def_cli(session['auth'], storage, site_id, op_level, group_id)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

        return dict(success=True, msg=result)


    def rename_storage_def(self, storage_id, new_name, group_id=None):
        try:
            result = None
            self.authenticate()
            result = self.storage_service.rename_storage_def(session['auth'], new_name, storage_id, group_id)

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}

        return result


    def storage_def_test(self, type, storage_id, mode, site_id=None, op_level=None, group_id=None, node_id=None, show_available='true', vm_config_action=None, disk_option=None, kw=None):
        try:
            result = None
            self.authenticate()
            result = self.storage_service.storage_def_test(session['auth'], storage_id, node_id, group_id, site_id, type, mode, kw, op_level, show_available, vm_config_action, disk_option)

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}

        return result


    def storage_def_test_cli(self, type, storage_name, mode, site_id, op_level, node_id, show_available='true', group_id=None, vm_config_action=None, disk_option=None, kw=None):
        try:
            self.authenticate()
            result = self.storage_service.storage_def_test_cli(session['auth'], storage_name, node_id, group_id, site_id, type, mode, kw, op_level, show_available, vm_config_action, disk_option)
            print result,
            print '\n\n\n\n=thi s is the controler'
            return result

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}


    def associate_defns(self, def_ids, def_type, site_id=None, op_level=None, group_id=None):
        self.authenticate()

        try:
            self.tc.associate_defns_task(session['auth'], site_id, group_id, def_type, def_ids, op_level)

        except Exception as ex:
            print_traceback()
            return "{success: false,msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"

        return "{success: true,msg: 'Task submitted.'}"


    def associate_definitions(self, storage, site_id, op_level, group_id):
        self.authenticate()

        try:
            storageDef = self.storage_service.storage_definition(storage)
            if storageDef:
                def_type = storageDef.type
                def_ids = storageDef.id
            else:
                return dict(success=False, msg='The storage definition with name ' + storage + ' does not exists')

            result = self.tc.associate_defns_task(session['auth'], site_id, group_id, def_type, def_ids, op_level)

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}

        return 'result'


    def get_server_storage_def_list(self, def_id, defType, site_id, group_id):
        try:
            result = None
            self.authenticate()
            result = self.storage_service.get_server_def_list(session['auth'], site_id, group_id, def_id)

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}

        return result


    def get_sp_list(self, site_id, def_id=None, _dc=None):
        
        result = None
        try:
            result = self.manager.get_sp_list(site_id, def_id, session['auth'])

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

        return result


    def RemoveScanResult(self):
        result = self.storage_service.RemoveScanResult()
        return result

    def SaveScanResult(self, storage_id):
        result = self.storage_service.SaveScanResult(storage_id)
        return result

    def add_storage_disk_cli(self, add_manually, group_id, storage, actual_size, allocated_size, unique_path, current_portal=None, target=None, state=None, lun=None, storage_allocated=False):
        try:
            storageDef = self.storage_service.storage_definition(storage)
            if storageDef:
                storage_id = storageDef.id
            else:
                return dict(success=False, msg='The storage definition with name ' + storage + ' does not exists')

            result = self.add_storage_disk(add_manually, group_id, storage_id, actual_size, allocated_size, unique_path, current_portal, target, state, lun, storage_allocated)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

        return result


    def add_storage_disk(self, add_manually, group_id, storage_id, actual_size, allocated_size, unique_path, current_portal, target, state, lun, storage_allocated):
        result = self.storage_service.add_storage_disk_manually(add_manually, session['auth'], group_id, storage_id, actual_size, allocated_size, unique_path, current_portal, target, state, lun, storage_allocated)
        return result

    def remove_storage_disk(self, storage_disk_id):
        result = self.storage_service.remove_storage_disk_manually(storage_disk_id)
        return result

    def remove_storage_disk_cli(self, storage_disk_name):
        result = self.storage_service.remove_storage_disk_cli(storage_disk_name)
        return result

    def mark_storage_disk(self, storage_disk_id, used):
        result = self.storage_service.mark_storage_disk(storage_disk_id, used)
        return result

    def mark_storage_disk_cli(self, storage, used):
        result = self.storage_service.mark_storage_disk_cli(storage, used)
        return result

    def create_disk(self, context, managed_node=None):
        storage_disk_id = ''
        storage_id = ''
        hex_id = getHexID()

        try:
            if not managed_node:
                managed_node,storage_id,create_flag, delete_flag= StorageManager().get_storage_and_node()
            context['hex_id'] = hex_id
            task_id = self.tc.create_disk_task(session['auth'], context, managed_node.id)
            finish,status = wait_for_task_completion(task_id, 5000)
            if (finish == True) and (status == Task.SUCCEEDED):
                disk = StorageManager().get_reserve_disk(hex_id)
                if disk:
                    storage_id = disk.storage_id
                    storage_disk_id = disk.id
                    StorageManager().unreserve_disk(storage_disk_id)
            return (storage_disk_id, storage_id)

        except Exception as ex:
            print_traceback()
            StorageManager().unreserve_disk(hex_id)
            raise Exception('Storage disk creation is failed')




    def remove_disk(self, context, managed_node=None):
        storage_disk_id = ''

        try:
            storage_disk_id = context.get('storage_disk_id')
            LOGGER.debug('###storage_disk_id=' + to_str(storage_disk_id))
            if not managed_node:
                managed_node,storage_id,create_flag,delete_flag = StorageManager().get_storage_and_node()

            task_id = self.tc.remove_disk_task(session['auth'], context, managed_node.id)
            finish,status = wait_for_task_completion(task_id, 5000L)
            return storage_disk_id

        except Exception as ex:
            print_traceback()
            raise Exception('Storage disk removal is failed')




