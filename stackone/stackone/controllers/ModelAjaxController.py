import pylons
import simplejson as json
from stackone.controllers.ControllerBase import ControllerBase
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
from stackone.controllers.XMLRPC.StorageXMLRPCController import StorageXMLRPCController
LOGGER = logging.getLogger('stackone.controllers')
from stackone.model.Authorization import AuthorizationService
from pylons.controllers.util import forward
from pylons.controllers import XMLRPCController
from stackone.controllers.ModelController import ModelController

class ModelAjaxController(ControllerBase):
    model_controller = stackone.controllers.ModelController.ModelController()

    @expose(template='json')
    def add_role(self, rolename, roledesc, reps, type, is_cloudadmin=None):
        result = None
        result = self.model_controller.add_role(rolename, roledesc, reps, type, is_cloudadmin)
        return result

    @expose(template='json')
    def change_user_password(self, userid, newpasswd, oldpasswd):
        result = None
        result = self.model_controller.change_user_password(userid, newpasswd, oldpasswd)
        return result

    @expose(template='json')
    def delete_enttype(self, enttypeid):
        result = None
        result = self.model_controller.delete_enttype(enttypeid)
        return result

    @expose(template='json')
    def delete_group(self, groupid):
        result = None
        result = self.model_controller.delete_group(groupid)
        return result

    @expose(template='json')
    def delete_operation(self, opid):
        result = None
        result = self.model_controller.delete_operation(opid)
        return result

    @expose(template='json')
    def delete_opsgroup(self, opsgroupid):
        result = None
        result = self.model_controller.delete_opsgroup(opsgroupid)
        return result

    @expose(template='json')
    def delete_privilege(self, privilegeid):
        result = None
        result = self.model_controller.delete_privilege(privilegeid)
        return result

    @expose(template='json')
    def delete_role(self, roleid):
        result = None
        result = self.model_controller.delete_role(roleid)
        return result

    @expose(template='json')
    def delete_user(self, userid):
        result = None
        result = self.model_controller.delete_user(userid)
        return result

    @expose(template='json')
    def edit_enttype_details(self, enttypeid):
        result = None
        result = self.model_controller.edit_enttype_details(enttypeid)
        return result

    @expose(template='json')
    def edit_group_details(self, groupid):
        result = None
        result = self.model_controller.edit_group_details(groupid)
        return result

    @expose(template='json')
    def edit_op_det(self, opid, enttype):
        result = None
        result = self.model_controller.edit_op_det(opid, enttype)
        return result

    @expose(template='json')
    def edit_opsgroup_details(self, opsgroupid):
        result = None
        result = self.model_controller.edit_opsgroup_details(opsgroupid)
        return result

    @expose(template='json')
    def edit_privilege_det(self, privilegeid):
        result = None
        result = self.model_controller.edit_privilege_det(privilegeid)
        return result

    @expose(template='json')
    def edit_user_det(self, userid):
        result = None
        result = self.model_controller.edit_user_det(userid)
        return result

    @expose(template='json')
    def get_cloud_users(self, type, _dc=None):
        result = None
        result = self.model_controller.get_cloud_users(type)
        return result

    @expose(template='json')
    def get_cloud_users_list(self, vdc_id=None, _dc=None):
        result = None
        result = self.model_controller.get_cloud_users_list(vdc_id)
        return result

    @expose(template='json')
    def get_entities(self, enttype_id, _dc=None):
        result = None
        result = self.model_controller.get_entities(enttype_id)
        return result

    @expose(template='json')
    def get_entities_bytype(self, type, parententityid=None, _dc=None):
        result = None
        result = self.model_controller.get_entities_bytype(type, parententityid)
        return result

    @expose(template='json')
    def get_entitytype_map(self, opid=None, _dc=None):
        result = None
        result = self.model_controller.get_entitytype_map(opid)
        return result

    @expose(template='json')
    def get_entitytype_role(self, type, _dc=None):
        result = None
        result = self.model_controller.get_entitytype_role(type)
        return result

    @expose(template='json')
    def get_enttype(self, _dc=None):
        result = None
        result = self.model_controller.get_enttype()
        return result

    @expose(template='json')
    def get_enttype_for_chart(self, _dc=None):
        result = None
        result = self.model_controller.get_enttype_for_chart()
        return result

    @expose(template='json')
    def get_groups_map(self, userid=None, _dc=None):
        result = None
        result = self.model_controller.get_groups_map(userid)
        return result

    @expose(template='json')
    def get_groupsdetails(self, type, _dc=None):
        result = None
        result = self.model_controller.get_groupsdetails(type)
        return result

    @expose(template='json')
    def get_operations(self, _dc=None):
        result = None
        result = self.model_controller.get_operations()
        return result

    @expose(template='json')
    def get_operations_map(self, opsgrpid=None, _dc=None):
        result = None
        result = self.model_controller.get_operations_map(opsgrpid)
        return result

    @expose(template='json')
    def get_opsgroups(self, _dc=None):
        result = None
        result = self.model_controller.get_opsgroups()
        return result

    @expose(template='json')
    def get_opsgroups_map(self, privid=None, _dc=None):
        result = None
        result = self.model_controller.get_opsgroups_map(privid=None)
        return result

    @expose(template='json')
    def get_privileges(self, _dc=None):
        result = None
        result = self.model_controller.get_privileges()
        return result

    @expose(template='json')
    def get_privileges4opsg(self, type, _dc=None):
        result = None
        result = self.model_controller.get_privileges4opsg(type)
        return result

    @expose(template='json')
    def get_role_details(self, roleid):
        result = None
        result = self.model_controller.get_role_details(roleid)
        return result

    @expose(template='json')
    def get_role_rep(self, roleid=None, _dc=None):
        result = None
        result = self.model_controller.get_role_rep(roleid)
        return result

    @expose(template='json')
    def get_roles(self, type, _dc=None):
        result = None
        result = self.model_controller.get_roles(type)
        return result

    @expose(template='json')
    def get_roles_map(self, type, _dc=None):
        result = None
        result = self.model_controller.get_roles_map(type)
        return result

    @expose(template='json')
    def get_toentitytype_map(self, opid, _dc=None):
        result = None
        result = self.model_controller.get_toentitytype_map(opid)
        return result

    @expose(template='json')
    def get_togroups_map(self, userid, _dc=None):
        result = None
        result = self.model_controller.get_togroups_map(userid)
        return result

    @expose(template='json')
    def get_tooperations_map(self, opsgroupid, _dc=None):
        result = None
        result = self.model_controller.get_tooperations_map(opsgroupid)
        return result

    @expose(template='json')
    def get_toopsgroups_map(self, privilegeid, _dc=None):
        result = None
        result = self.model_controller.get_toopsgroups_map(privilegeid)
        return result

    @expose(template='json')
    def get_tousers_map(self, groupid, _dc=None):
        result = None
        result = self.model_controller.get_tousers_map(groupid)
        return result

    @expose(template='json')
    def get_user_role_map(self, _dc=None):
        result = None
        result = self.model_controller.get_user_role_map()
        return result

    @expose(template='json')
    def get_user_status_map(self, _dc=None):
        result = None
        result = self.model_controller.get_user_status_map()
        return result

    @expose(template='json')
    def get_users(self, type, _dc=None):
        result = None
        result = self.model_controller.get_users(type)
        return result

    @expose(template='json')
    def get_users_map(self, type, groupid=None, _dc=None):
        result = None
        result = self.model_controller.get_users_map(type, groupid)
        return result


    @expose(template='json')
    def save_enttype_details(self, enttypename, dispname):
        result = None
        result = self.model_controller.save_enttype_details(enttypename, dispname)
        return result

    @expose(template='json')
    def save_group_details(self, groupid, groupname, userids, role, desc, type):
        result = None
        result = self.model_controller.save_group_details(groupid, groupname, userids, role, desc, type)
        return result

    @expose(template='json')
    def save_oper_det(self, opname, descr, context_disp, entityid, dispname, icon):
        result = None
        result = self.model_controller.save_oper_det(opname, descr, context_disp, entityid, dispname, icon)
        return result

    @expose(template='json')
    def save_opsgroup_details(self, opsgroupname, opsgroupdesc, opsgrouppriv, operation):
        result = None
        result = self.model_controller.save_opsgroup_details(opsgroupname, opsgroupdesc, opsgrouppriv, operation)
        return result

    @expose(template='json')
    def save_privilege_details(self, privilegeid, privilegename, opsgrups):
        result = None
        result = self.model_controller.save_privilege_details(privilegeid, privilegename, opsgrups)
        return result

    @expose(template='json')
    def save_user_det(self, userid, username, fname, lname, displayname,password, email, phone, status, type):
        result = self.model_controller.save_user_det(userid, username, fname, lname, displayname, password, email, phone, status, type)
        return result

    @expose(template='json')
    def update_role(self, roleid, rolename, roledesc, reps, type, is_cloudadmin=None):
        result = None
        result = self.model_controller.update_role(roleid, rolename, roledesc, reps, type, is_cloudadmin)
        return result

    @expose(template='json')
    def updatesave_enttype_details(self, enttypeid, enttypename, dispname):
        result = None
        result = self.model_controller.updatesave_enttype_details(enttypeid, enttypename, dispname)
        return result

    @expose(template='json')
    def updatesave_group_details(self, groupid, groupname, userids, role, desc):
        result = None
        result = self.model_controller.updatesave_group_details(groupid, groupname, userids, role, desc)
        return result

    @expose(template='json')
    def updatesave_op_det(self, opid, opname, desc, entid, context_disp, dispname, icon):
        result = None
        result = self.model_controller.updatesave_op_det(opid, opname, desc, entid, context_disp, dispname, icon)
        return result

    @expose(template='json')
    def updatesave_opsgroup_details(self, opsgroupid, opsgroupname, opsgroupdesc, opsgrouppriv, operation):
        result = None
        result = self.model_controller.updatesave_opsgroup_details(opsgroupid, opsgroupname, opsgroupdesc, opsgrouppriv, operation)
        return result

    @expose(template='json')
    def updatesave_privilege_details(self, privilegeid, privilegename, opsgrups):
        result = None
        result = self.model_controller.updatesave_privilege_details(privilegeid, privilegename, opsgrups)
        return result

    @expose(template='json')
    def updatesave_user_det(self, userid, username, fname, lname, displayname, email, phone, status, changepass, newpasswd):
        result = None
        result = self.model_controller.updatesave_user_det(userid, username, fname, lname, displayname, email, phone, status, changepass, newpasswd)
        return result

    @expose()
    def xmlrpc(self):
        return forward(ModelXMLRPCController())

