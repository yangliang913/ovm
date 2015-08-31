from stackone.model import *
from stackone.model.Authorization import AuthorizationService
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from tg import session
from stackone.controllers.StorageController import StorageController
from stackone.controllers.XMLRPC.stackoneXMLRPC import stackoneXMLRPC
class StorageXMLRPCController(stackoneXMLRPC):
    storage_controller = StorageController()
    def get_storage_def_list(self, site_id=None, op_level=None, group_id=None, _dc=None):
        result = None
        result = self.storage_controller.get_storage_def_list(site_id, op_level, group_id)
        return result

    def get_dc_storage_def_list(self, site_id=None, group_id=None, _dc=None):
        result = None
        result = self.storage_controller.get_dc_storage_def_list(site_id, group_id)
        return result

    def get_storage_types(self, **result):
        result = self.storage_controller.get_storage_types()
        return result

    def add_storage_def(self, type, site_id, opts, op_level, group_id=None, node_id=None, sp_ids=None, added_manually=False, cli=True):
        result = self.storage_controller.add_storage_def(type, site_id, op_level, group_id, node_id, sp_ids, added_manually, opts, cli)
        return result

    def edit_storage_def(self, storage_id, type, site_id=None, group_id=None, op_level=None, sp_ids=None, **result):
        result = None
        result = self.storage_controller.edit_storage_def(storage_id, type, site_id, group_id, op_level, sp_ids)
        return result

    def is_storage_allocated(self, storage_id):
        result = None
        result = self.storage_controller.is_storage_allocated(storage_id)
        return result

    def remove_storage_def(self, storage_id, site_id, op_level, group_id=None):
        result = self.storage_controller.remove_storage_def_cli(storage_id, site_id, op_level, group_id)
        return result

    def rename_storage_def(self, storage_id, new_name, group_id=None):
        result = None
        result = self.storage_controller.rename_storage_def(storage_id, new_name, group_id)
        return result

    def test_storage_def(self, type, storage_name, mode, site_id, op_level, node_id):
        result = self.storage_controller.storage_def_test_cli(type, storage_name, mode, site_id, op_level, node_id)
        return result

    def associate_definitions(self, storage, site_id, op_level, group_id):
        result = self.storage_controller.associate_definitions(storage, site_id, op_level, group_id)
        return result

    def get_server_storage_def_list(self, def_id, defType, site_id=None, group_id=None, _dc=None):
        result = None
        result = self.storage_controller.get_server_storage_def_list(def_id, defType, site_id, group_id)
        return result

    def get_sp_list(self, site_id, def_id=None, _dc=None):
        result = self.storage_controller.get_sp_list(site_id, def_id)
        return result

    def RemoveScanResult(self):
        result = self.storage_controller.RemoveScanResult()
        return result

    def SaveScanResult(self, storage_id):
        result = self.storage_controller.SaveScanResult(storage_id)
        return result

    def add_storage_disk(self, add_manually, group_id, storage, actual_size, allocated_size, unique_path):
        result = self.storage_controller.add_storage_disk_cli(add_manually, group_id, storage, actual_size, allocated_size, unique_path)
        return result

    def remove_storage_disk(self, storage_disk_name):
        result = self.storage_controller.remove_storage_disk_cli(storage_disk_name)
        return result

    def mark_storage_disk(self, storage, used):
        result = self.storage_controller.mark_storage_disk_cli(storage, used)
        return result



