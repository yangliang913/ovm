from stackone import model
# #from stackone.cloud.controller.CSEPAjaxController import CSEPAjaxController
# #from stackone.cloud.controller.CloudAjaxController import CloudAjaxController
# #from stackone.cloud.controller.CloudDashboardAjaxController import \
#     CloudDashboardAjaxController
# #from stackone.cloud.controller.CloudNetworkAjaxController import \
#     CloudNetworkAjaxController
# #from stackone.cloud.controller.CloudProviderAjaxController import \
#     CloudProviderAjaxController
# #from stackone.cloud.controller.CloudStorageAjaxController import \
#     CloudStorageAjaxController
# #from stackone.cloud.controller.CloudTemplateAjaxController import \
#     CloudTemplateAjaxController
from stackone.controllers.ApplianceAjaxController import ApplianceAjaxController
from stackone.controllers.BackupAjaxController import BackupAjaxController
#from stackone.controllers.CMSCloudAjaxController import CMSCloudAjaxController
from stackone.controllers.ControllerImpl import ControllerImpl
from stackone.controllers.DWMAjaxController import DWMAjaxController
from stackone.controllers.DashboardAjaxController import DashboardAjaxController
from stackone.controllers.HAAjaxController import HAAjaxController
from stackone.controllers.ModelAjaxController import ModelAjaxController
from stackone.controllers.NetworkAjaxController import NetworkAjaxController
from stackone.controllers.NodeAjaxController import NodeAjaxController
from stackone.controllers.RestoreAjaxController import RestoreAjaxController
from stackone.controllers.StorageAjaxController import StorageAjaxController
from stackone.controllers.TemplateAjaxController import TemplateAjaxController
from stackone.controllers.XMLRPC.RootXMLRPCController import RootXMLRPCController
from stackone.controllers.error import ErrorController
from stackone.controllers.secure import SecureController
from stackone.core.utils.utils import to_unicode, to_str, print_traceback, \
    get_cms_stacktrace, get_cms_stacktrace_fancy
from stackone.controllers.VcenterAjaxController import VcenterAjaxController
from stackone.lib.base import BaseController
from stackone.model import *
from stackone.model.Authorization import AuthorizationService
from stackone.model.CustomPredicates import has_role
from stackone.model.DBHelper import DBHelper
from stackone.model.FirewallManager import FirewallManager
from stackone.model.UpdateManager import UIUpdateManager
from stackone.viewModel.EmailService import EmailService
from stackone.viewModel.Message import Message
from stackone.viewModel.NodeService import NodeService
from stackone.viewModel.Server import Server
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.viewModel.TaskInfo import TaskInfo
from stackone.viewModel.Userinfo import Userinfo
from pylons.controllers import XMLRPCController
from pylons.controllers.util import forward
from pylons.i18n import ugettext as _, lazy_ugettext as l_
from repoze.what import predicates
from tg import expose, flash, require, url, request, redirect, response, session, \
    config
from tg.decorators import override_template
from xml.dom import minidom
import stackone.core.utils.constants
import logging
import os
import os
import pprint
import pylons
import simplejson as json
import sys
import tg
__doc__ = 'Main Controller'
__all__ = ['RootController']
sys.path.append('/usr/lib/python2.4/site-packages')
sys.path.append('/usr/lib64/python2.4/site-packages')
sys.path.append('/usr/lib64/python24.zip')
sys.path.append('/usr/lib64/python2.4/plat-linux2')
sys.path.append('/usr/lib64/python2.4/lib-tk')
sys.path.append('/usr/lib64/python2.4/lib-dynload')
sys.path.append('/usr/lib64/python2.4/site-packages/Numeric')
sys.path.append('/usr/lib64/python2.4/site-packages/gtk-2.0')
constants = stackone.core.utils.constants
LOGGER = logging.getLogger('stackone.controllers')
class RootController(BaseController):
    error = ErrorController()
    appliance = ApplianceAjaxController()
    dashboard = DashboardAjaxController()
    model = ModelAjaxController()
    node = NodeAjaxController()
    network = NetworkAjaxController()
    storage = StorageAjaxController()
    template = TemplateAjaxController()
    ha = HAAjaxController()
    controller_impl = ControllerImpl()
    backup = BackupAjaxController()
    restore = RestoreAjaxController()
    tc = TaskCreator()
    dwm = DWMAjaxController()
    # cloud_provider = CloudProviderAjaxController()
    # cloud = CloudAjaxController()
    # cloud_network = CloudNetworkAjaxController()
    # cloud_storage = CloudStorageAjaxController()
    # cloud_template = CloudTemplateAjaxController()
    # cloud_dashboard = CloudDashboardAjaxController()
    #cmscloud = CMSCloudAjaxController()
    # csep = CSEPAjaxController()
    vcenter = VcenterAjaxController()
    @expose(template='json')
    def api_loginhandler(self, api_login, api_pwd):
        try:
            usr = User.by_user_name(api_login)
            if usr is not None and usr.validate_password(api_pwd) == True:
                auth = AuthorizationService()
                auth.user = usr
                session['userid'] = 'admin'
                session['auth'] = auth
                session['username'] = usr.user_name
        except Exception as ex:
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        return {'success': True, 'result': True}
        
        

    @expose('stackone.templates.login')
    def authenticate(self):
        try:
            self.controller_impl.authenticate()
        
        except Exception as e:
            raise Exception('SessionExpired.')

    @expose(template='json')
    def build_fw_stack_trace(self, fw_main_data):
        result = '<html><head><title>stackone Firewall Stack Track</title></head><body><b>stackone Firewall Stack Track</b><br\\><br\\>'
        
        for fw_data in fw_main_data:
            result = result + '<table border=1>'
            nw_svc_host_name = fw_data.get('nw_svc_host_name')
            chain_name = fw_data.get('chain_name')
            table_data = fw_data.get('table_data')
            result = result + '<tr><td>Network service host name</td><td>' + str(nw_svc_host_name) + '</td></tr>'
            result = result + '<tr><td>Chain name</td><td>' + str(chain_name) + '</td></tr>'
        
            for table in table_data:
                (chains, rule_data) = (table.get('chains'), table.get('chains'))
                unwrapped_chains = table.get('unwrapped_chains')
                rule_data = table.get('rule_data')
                result = result + '<tr><td>Chains</td><td>' + str(chains) + '</td></tr>'
                result = result + '<tr><td>Unwrapped chains</td><td>' + str(unwrapped_chains) + '</td></tr>'
            
                for rules_info in table:
                    for rule in rule_data:
                        result = result + '<tr><td>Rule</td><td>' + str(rule) + '</td></tr>'
                
            result = result + '</table><br/>'
        
        result = result + '</body></html>'
        return result

    @expose(template='json')
    def cancel_task(self, task_id):
        self.authenticate()
        result = self.controller_impl.cancel_task(task_id)
        return result

    @expose(template='json')
    def check_license_expire(self, mode=None):
        result = None
        result = self.controller_impl.check_license_expire(mode)
        return result

    @expose(template='json')
    def cms_trace(self):
        if config.get('enable_stack_trace_url') == 'True':
            return get_cms_stacktrace()
        
        return '<html>Stack Trace not enabled.</html>'

    @expose(template='json')
    def cms_trace_fancy(self):
        if config.get('enable_stack_trace_url') == 'True':
            return get_cms_stacktrace_fancy()
        
        return '<html>Stack Trace not enabled.</html>'

    @expose(template='json')
    def delete_emailrecord(self, emailsetup_id):
        result = self.controller_impl.delete_emailrecord(emailsetup_id)
        return result

    @expose(template='json')
    def deployment_info(self, _dc=None):
        try:
            info = self.controller_impl.get_deployment_info()
        
        except Exception as e:
            print 'Exception: ',
            print e
            return dict(success=False, msg=to_str(e).replace("'", ''))
        
        return dict(success=True, info=info)

    @expose(template='json')
    def fw_trace(self):
        if config.get('enable_fw_stack_trace_url') == 'True':
            fw_manager = FirewallManager.get_manager()
            fw_main_data = fw_manager.get_fw_info()
            return self.build_fw_stack_trace(fw_main_data)
        
        return '<html>Firewall Stack Trace not enabled.</html>'
    @expose(template='json')
    def getNotifications(self, type, list, user, entType=None, _dc=None):
        result = None
        result = self.controller_impl.getNotifications(type, list, user, entType)
        return result

    @expose(template='json')
    def getSystemTasks(self, type, user, _dc=None):
        result = None
        result = self.controller_impl.getSystemTasks(type, user)
        return result

    @expose(template='json')
    def get_app_updates(self):
        result = None
        result = self.controller_impl.get_app_updates()
        return result

    @expose(template='json')
    def get_cloudnav_nodes(self):
        result = None
        result = self.controller_impl.get_cloudnav_nodes()
        return result

    @expose(template='json')
    def get_context_menu_items(self, node_id, node_type, _dc=None, menu_combo=None, cp_type=None):
        try:
            result = None
            result = self.controller_impl.getUserOps(node_id, node_type, menu_combo, cp_type)
        except Exception as ex:
            print_traceback()
        
        return dict(success=True, rows=result)

    @expose(template='json')
    def get_cp(self, _dc=None):
        try:
            result = None
            result = self.controller_impl.get_cp()
            return dict(success=True, rows=result)
        except Exception, ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        

    @expose(template='json')
    def get_emailsetup_details(self, emailsetup_id):
        result = None
        result = self.controller_impl.get_emailsetup_details(emailsetup_id)
        return result

    @expose(template='json')
    def get_emailsetupinfo(self, _dc=None):
        result = self.controller_impl.get_emailsetupinfo()
        return result

    @expose(template='json')
    def get_entity_id(self, name, type):
        try:
            ent = Entity.find_by_name(name, type)
            if ent is not None:
                result = ent.entity_id
                return result
            
            return {'success': False, 'msg': 'The Entity is not found'}
            
        except Exception as ex:
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    @expose(template='json')
    def get_failed_tasks(self, _dc=None):
        result = None
        result = self.controller_impl.get_failed_tasks()
        return result

    @expose(template='json')
    def get_nav_nodes(self):
        result = None
        result = self.controller_impl.get_nav_nodes()
        return result

    @expose(template='json')
    def get_platforms(self, **kw):
        try:
            result = None
            result = self.controller_impl.get_platforms()
            return dict(success=True, rows=result)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        

    @expose(template='json')
    def get_provider_types(self, _dc=None):
        try:
            result = None
            result = self.controller_impl.get_provider_types()
            return dict(success=True, rows=result)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        

    @expose(template='json')
    def get_ssh_info(self, node_id, client_platform):
        result = None
        result = self.controller_impl.get_ssh_info(node_id, client_platform)
        return result

    @expose(template='json')
    def get_tasks(self, _dc=None):
        result = None
        result = self.controller_impl.get_tasks()
        return result

    @expose(template='json')
    def get_used_ports_info(self):
        if config.get('enable_used_ports_url') == 'True':
            return self.controller_impl.get_used_ports_info()
        return '<html>Port information url not enabled.</html>'

    @expose(template='json')
    def get_vnc_info(self, node_id, dom_id):
        result = None
        result = self.controller_impl.get_vnc_info(node_id, dom_id)
        return result

    @expose(template='stackone.templates.dashboard')
    def index(self):
        result = None
        if session.get('username') is not None:
            user = DBSession.query(User).filter_by(user_name=session.get('username')).first()
            if user is not None and user.is_cloud():
                if session['cloud_only'] == True:
                    override_template(self.index, 'genshi:stackone.templates.clouddashboard')
            
        result = self.controller_impl.index()
        return dict(result)
        
       

    @expose(template='json')
    def lisence_info(self, _dc=None):
        result = []
        try:
            result = self.controller_impl.lisence_info()
        
        except Exception as e:
            print 'Exception: ',
            print e
            return dict(success=False, msg=to_str(e).replace("'", ''))
        
        return dict(success=True, info=result)

    @expose('stackone.templates.login')
    def login(self, came_from='/'):
        result = None
        result = self.controller_impl.login(came_from)
        return result

    @expose()
    def post_login(self, userid, group, ldap_user, user_details, came_from='/'):
        result = None
        result = self.controller_impl.post_login(userid, group, ldap_user, user_details, came_from)
        return result

    @expose()
    def post_logout(self, came_from='/'):
        self.controller_impl.post_logout(came_from)
        return dict(page='login', version=constants._version, came_from=came_from)


    @expose(template='json')
    def save_email_setup_details(self, desc, servername, port, useremail, password, secure, **kw):
        result = None
        result = self.controller_impl.save_email_setup_details(desc, servername, port, useremail, password, secure)
        return result
    #sam 1025
    @expose()
    def perf_debug(self, **kwargs):
    	#return set_or_get_perf_debug(**kwargs)
        return
    @expose(template='json')
    def send_test_email(self, desc, servername, port, useremail, password, secure, **kw):
        try:
            msgreceived = self.controller_impl.send_test_email(desc, servername, port, useremail, password, secure)
            
        except Exception as ex:
            print ex
            return dict(success=False, msg='Test Failed: ' + to_str(ex).replace("'", ''))
        return {'success': True, 'msg': msgreceived}

    @expose(template='json')
    def server_sync(self, node_id, def_type, sync_forcefully=False):
        result = None
        result = self.controller_impl.server_sync(node_id, def_type, sync_forcefully)
        return result

    @expose(template='json')
    def servicepoint_login(self, came_from='/', **kwargs):
        result = None
        
        try:
            status = self.controller_impl.user_login(kwargs)
            
            if status.get('success'):
                user = status.get('user')
                group = status.get('group')
                ldap_user = status.get('ldap_user')
                user_details = status.get('user_details')
                result = self.post_login(user, group, ldap_user, user_details, came_from=url('/'))
                usr = DBSession.query(User).filter_by(user_name=user).first()
                auth = AuthorizationService()
                auth.user = usr
                #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEP
                # servicepoint_name = kwargs.get('csep_name')
                # servicepoint = DBSession.query(CSEP).filter(CSEP.name == servicepoint_name).first()
                # if servicepoint is None:
                #     msg = 'Cloud Service not found'
                #     return "{success:false,msg:'" + msg.replace("'", ' ') + "'}"
                
                # if auth.has_servicepoint_role(servicepoint):
                #     session['user'] = user
                #     session['auth'] = auth
                #     session['userid'] = usr.user_id
                #     session['servicepoint_id'] = servicepoint.id
                # else:
                #     return "{success:false,msg:'user has no permission on the Cloud Service'}"
                
                return result
                
            msg = status.get('msg')
            return "{success:false,msg:'" + msg.replace("'", ' ') + "'}"
            
        except Exception as e:
            print 'Exception: ',
            print e
            import traceback
            traceback.print_exc()
            return "{success:false,msg:'" + str(e).replace("'", ' ') + "'}"


    @expose(template='json')
    def sync_all(self, def_type, site_id=None, group_id=None):
        result = None
        result = self.controller_impl.sync_all(def_type, site_id, group_id)
        return result

    @expose(template='json')
    def sync_defn(self, server_ids, def_id, defType, site_id=None, group_id=None):
        result = None
        result = self.controller_impl.sync_defn(server_ids, def_id, defType, site_id, group_id)
        return result

    @expose(template='json')
    def task_trace(self):
        if config.get('enable_stack_trace_url') == 'True':
            return self.tc.get_running_task_info()
        
        return '<html>Stack Trace not enabled.</html>'

    @expose(template='json')
    def update_email_setup_details(self, desc, servername, port, useremail, password, secure, **kw):
        result = self.controller_impl.update_email_setup_details(desc, servername, port, useremail, password, secure)
        return result

    @expose()
    def user_login(self, came_from='/', **kwargs):
        result = None
        
        try:
            status = self.controller_impl.user_login(kwargs)
            if status.get('success'):
                user = status.get('user')
                group = status.get('group')
                ldap_user = status.get('ldap_user')
                user_details = status.get('user_details')
                result = self.post_login(user, group, ldap_user, user_details, came_from=url('/'))
                return result
            
            msg = status.get('msg')
            return "{success:false,msg:'" + msg.replace("'", ' ') + "'}"
            
        except Exception as e:
            print 'Exception: ',
            print e
            import traceback
            traceback.print_exc()
            return "{success:false,msg:'" + str(e).replace("'", ' ') + "'}"
        

    @expose('stackone.templates.login')
    def user_logout(self, came_from='/'):
        return self.post_logout(came_from)

    @expose()
    def xmlrpc(self, *args, **kw):
        try:
            self.authenticate()
        
        except Exception as e:
            raise e
        
        return forward(RootXMLRPCController())


