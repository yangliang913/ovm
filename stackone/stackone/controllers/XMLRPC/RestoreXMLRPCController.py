import pylons
from stackone.model import *
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
constants = stackone.core.utils.constants
LOGGER = logging.getLogger('stackone.controllers')
from stackone.controllers.XMLRPC.stackoneXMLRPC import stackoneXMLRPC
from stackone.controllers.RestoreController import RestoreController
class RestoreXMLRPCController(stackoneXMLRPC):
    restore_controller = RestoreController()
    def restore_vm(self, vm_id, config_name, datetime, _dc=None):
        result = self.restore_controller.restore_frombackup(vm_id, config_name, datetime)
        return result

    def get_backup_result_info(self, sp_id, vm_id, _dc=None):
        result = self.restore_controller.get_backupresult_info(sp_id, vm_id,_dc=None)
        return result

    def restore_count(self, vm_id):
        result = self.restore_controller.restore_count(vm_id)
        return result

    def get_vm_backups(self, vm_id):
        result = self.restore_controller.get_vm_backups(vm_id)
        return result



