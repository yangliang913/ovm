import logging
from tg import expose
from stackone.lib.base import BaseController
from stackone.controllers.VcenterController import VcenterController
LOGGER = logging.getLogger('stackone.controllers')
class VcenterAjaxController(BaseController):
    vcenter_controller = VcenterController()
    @expose(template='json')
    def add_vCenter(self, host, port, ssl, username, password):
        result = None
        result = self.vcenter_controller.add_vCenter(host, port, ssl, username, password)
        return result
    @expose(template='json')
    def remove_vCenter(self, id):
        result = None
        result = self.vcenter_controller.remove_vCenter(id)
        return result
    @expose(template='json')
    def get_vCenters(self, _dc=None):
        result = None
        result = self.vcenter_controller.get_vCenters()
        return result
    @expose(template='json')
    def edit_vCenter(self, id, host, port, ssl, username, password):
        result = None
        result = self.vcenter_controller.edit_vCenter(id, host, port, ssl, username, password)
        return result
    @expose(template='json')
    def get_managed_objects_from_vcenter(self,vcenter_id, node=None, _dc=None):
        result = None
        result = self.vcenter_controller.get_managed_objects_from_vcenter(vcenter_id)
        return result
    @expose(template='json')
    def import_managed_objects_from_vcenter(self, vcenter_id, context):
        result = None
        result = self.vcenter_controller.import_managed_objects_from_vcenter(vcenter_id, context)
        return result
    @expose(template='json')
    def test_vcenter_connection(self, hostname, username, password):
        result = None
        result = self.vcenter_controller.test_vcenter_connection(hostname, username, password)
        return result


