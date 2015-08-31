from stackone.core.utils.utils import to_unicode, to_str, print_traceback, get_default_datacenter
from tg import session
from stackone.viewModel.VcenterService import VcenterService
from stackone.controllers.ControllerBase import ControllerBase
class VcenterController(ControllerBase):
    vcenter_service = VcenterService()
    def add_vCenter(self, host, port, ssl, username, password):
        try:
            result = None
            self.authenticate()
            result = self.vcenter_service.add_vCenter(session['auth'], host,port,ssl,username,password)
            return result
        except Exception,ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'",'')}
    def remove_vCenter(self, id):
        result = None
        self.authenticate()
        result = self.vcenter_service.remove_vCenter(session['auth'], id)
        return result

    def get_vCenters(self, _dc=None):
        result = None
        result = self.vcenter_service.get_vCenters()
        return result

    def edit_vCenter(self, id, host, port, ssl, username, password):
        try:
            result = None
            self.authenticate()
            result = self.vcenter_service.edit_vCenter(session['auth'],id, host,port,ssl,username,password)
            return result
        except Exception,ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'",'')}
    def get_managed_objects_from_vcenter(self, vcenter_id):
        try:
            import simplejson as json
            result = None
            self.authenticate()
            result = self.vcenter_service.get_managed_objects_from_vcenter(session['auth'],vcenter_id)
            return json.dumps(result)
        except Exception,ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'",'')}
                
    def import_managed_objects_from_vcenter(self, vcenter_id, context):
        try:
            result = None
            self.authenticate()
            default_dc = get_default_datacenter()
            site_id = default_dc.id
            self.vcenter_service.validate_vcenter(session['auth'],vcenter_id,context)
            tc = self.vcenter_service.get_task_creator()
            result = tc.import_vcenter_task(session['auth'],site_id,vcenter_id,context)
            return {'result':result,'success':True,'msg':'Import vCenter task submitted'}
        except Exception,ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'",'')}
            
            
    def test_vcenter_connection(self, hostname, username, password):
        result = None
        self.authenticate()
        result = self.vcenter_service.test_vcenter_connection(session['auth'], hostname, username, password)
        return result



