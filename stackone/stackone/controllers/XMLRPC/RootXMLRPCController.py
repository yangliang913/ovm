import time
from stackone.controllers.ControllerImpl import ControllerImpl
from stackone.model import *
from stackone.model.Authorization import AuthorizationService
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from tg import session, url
from stackone.core.utils.utils import print_traceback
from stackone.model.Entity import Entity
from stackone.controllers.XMLRPC.stackoneXMLRPC import stackoneXMLRPC
class RootXMLRPCController(stackoneXMLRPC):
    controller_impl = ControllerImpl()
    def user_logout(self, came_from=url('/')):
        self.controller_impl.post_logout(came_from)

    def has_admin_role(self):
        result = self.controller_impl.has_admin_role()
        return result

    def get_nav_nodes(self):
        try:
            result = None
            result = self.controller_impl.get_nav_nodes()
            return result
        except Exception as ex:
            print_traceback()
        return None

    def get_vnc_info(self, node_id, dom_id):
        try:
            result = None
            result = self.controller_impl.get_vnc_info(node_id, dom_id)
        except Exception as ex:
            print_traceback()
        return dict(success=True, vnc=result)

    def get_platforms(self, **result):
        result = None
        result = self.controller_impl.get_platforms()
        return result

    def get_context_menu_items(self, node_id, node_type, _dc=None, menu_combo=None):
        result = None
        result = self.controller_impl.getUserOps(node_id, node_type, menu_combo)
        return dict(success=True, rows=result)

    def get_tasks(self, _dc=None):
        result = None
        result = self.controller_impl.get_tasks()
        return result

    def getNotifications(self, type, list, user, entType=None, _dc=None):
        result = None
        result = self.controller_impl.getNotifications(type, list, user, entType)
        return result

    def getSystemTasks(self, type, user, _dc=None):
        result = None
        result = self.controller_impl.getSystemTasks(type, user)
        return result

    def get_failed_tasks(self, _dc=None):
        result = None
        result = self.controller_impl.get_failed_tasks()
        return result

    def save_email_setup_details(self, desc, servername, port, useremail, password, secure, **result):
        result = None
        result = self.controller_impl.save_email_setup_details(desc, servername, port, useremail, password, secure)
        return result

    def update_email_setup_details(self, uname, pword, desc, servername, port, useremail, password, secure, **result):
        result = None
        result = self.controller_impl.update_email_setup_details(desc, servername, port, useremail, password, secure)
        return result

    def send_test_email(self, desc, servername, port, useremail, password, secure, **result):
        result = self.controller_impl.send_test_email(desc, servername, port, useremail, password, secure)
        return result

    def get_emailsetupinfo(self):
        result = None
        result = self.controller_impl.get_emailsetupinfo()
        return result

    def delete_emailrecord(self, emailsetup_id):
        result = self.controller_impl.delete_emailrecord(emailsetup_id)
        return result

    def get_emailsetup_details(self, emailsetup_id):
        result = None
        result = self.controller_impl.get_emailsetup_details(emailsetup_id)
        return result

    def rpc_loginhandler(self, rpc_login, rpc_pwd):
        try:
            usr = User.by_user_name(rpc_login)
            if usr is not None and usr.validate_password(rpc_pwd) == True:
                return {'success':True,'result':True}
        except Exception as ex:
            print_traceback()
            return  {'success':False,'msg':to_str(ex).replace("'",'')}
        
    def get_entity_id(self, name, type):
        try:
            type_id = self.get_mapped_type(type)
            ent= Entity.find_by_name(name,type_id)
            if ent is not None:
                return {'success':True,'entity_id':ent.entity_id}
            return {'success':False,'msg':'The Entity is not found'}
        
        except Exception as ex:
            print_traceback()
            return  {'success':False,'msg':to_str(ex).replace("'",'')}
        
    def get_mapped_type(self, type):
        type_id = type
        if type == constants.DATA_CENTER:
            type_id = '1'
        elif type == constants.IMAGE_STORE:
            type_id = '2'
        elif type == constants.SERVER_POOL:
            type_id = '3'
        elif type == constants.MANAGED_NODE:
            type_id = '4'
        elif type == constants.DOMAIN:
            type_id = '5'
        elif type == constants.IMAGE_GROUP:
            type_id = '6'
        elif type == constants.IMAGE:
            type_id = '7'
        return type_id

    def get_entity_children(self, entity_id):
        try:
            auth = session['auth']
            entity = auth.get_entity(entity_id)
            if entity is not None:
                children = []
                for child in auth.get_child_entities(entity):
                    children.append(dict({'name':child.name,'type':child.type.name,'id':child.entity_id}))
                return {'success':True,'children':children}
            return {'success':False,'msg':'The Entity is not found'}
        except Exception,ex:
            print_traceback()
            return  {'success':False,'msg':to_str(ex).replace("'",'')}
    def get_task_details(self, task_id):
        try:
            result = self.controller_impl.get_details_task(task_id)
            
        except Exception,ex:
            print_traceback()
            return  dict({'success':False,'msg':to_str(ex).replace("'",'')})
        return dict({'success':True,'msg':result})
    def cmd_retdict(self):
        return dict(success=False, failure=True)

    def cancel_task(self, task_id):
        result = self.controller_impl.cancel_task(task_id)
        return result

    def cancel_backup(self, policy_name):
        result = self.controller_impl.cancel_backup(policy_name)
        return result



