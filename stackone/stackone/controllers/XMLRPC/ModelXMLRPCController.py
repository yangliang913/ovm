from stackone.model import *
from stackone.model.Authorization import AuthorizationService
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from stackone.viewModel.Userinfo import Userinfo
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
from tg import session
from stackone.controllers.ModelController import ModelController
from stackone.controllers.XMLRPC.stackoneXMLRPC import stackoneXMLRPC
class ModelXMLRPCController(stackoneXMLRPC):
    model_controller = ModelController()
    user_info = Userinfo()
    # sam 1026
    def get_users(self, type, _dc=None):
        result = self.model_controller.get_users(type)
        return result

    def get_cloud_users(self, _dc=None):
        result = self.model_controller.get_cloud_users()
        return result

    def user_information(self, username):
        result = self.model_controller.user_information(username)
        return result

    def has_permission(self, operation, entname, username=None):
        try:
            result = self.model_controller.has_permission(operation,entname,username)
            return result
        except Exception as e:
            print_traceback()
            return dict({'success':False,'msg':to_str(e)})
    def list_user_operations(self, entname, username=None):
        try:
            result = self.model_controller.list_user_operations(entname,username)
            return result
        except Exception as e:
            print_traceback()
            return dict({'success':False,'msg':to_str(e)})
            
    def get_user_status_map(self, _dc=None):
        result = None
        result = self.model_controller.get_user_status_map()
        return result
    # sam 1026
    def save_user_det(self, username, fname, lname, displayname, password, email, status, phone, type):
        user = self.user_info.get_user(username)
        if user == None:
        		if not self.user_info.check_email(email):
        				result = dict(False,'Email already exist')
            		result = self.model_controller.save_user_det(None, username, fname, lname, displayname, password, email, phone, status,type)
        else:
            result = dict(False, 'The user with username ' + username + ' already exists')
        return result

    def delete_user(self, username):
        result = None
        user = self.user_info.get_user(username)
        if user != None:
            result = self.model_controller.delete_user(user.user_id)
        else:
            result = dict(False, 'The user with username ' + username + ' does not exists')
        return result

    def updatesave_user_det(self, userid, username, fname, lname, displayname, email, phone, status, groupids, changepass, newpasswd):
        result = None
        result = self.model_controller.updatesave_user_det(userid, username, fname, lname, displayname, email, phone, status, groupids, changepass, newpasswd)
        return result

    def addgroup_to_user(self, username, groupnames):
        addgroup = self.model_controller.addgroup_to_user(username, groupnames)
        return addgroup

    def removegroup_from_user(self, username, groupnames):
        result = self.model_controller.deletegroup_from_user(username, groupnames)
        return result

    def edit_user_det(self, userid):
        result = None
        result = self.model_controller.edit_user_det(userid)
        return result

    def change_user_password(self, newpasswd, oldpasswd):
        result = None
        userid = session['userid']
        result = self.model_controller.change_user_password(userid, newpasswd, oldpasswd)
        return result

    def get_opsgroups(self, like=None, _dc=None):
        result = None
        result = self.model_controller.get_opsgroups(like)
        return result

    def addoperation_to_opsgroup(self, opsgroup, operations, like=None):
        result = self.model_controller.addoperation_to_opsgroup(opsgroup, operations, like)
        return result

    def removeoperation_from_opsgroup(self, op_group, operations, like=None):
        result = self.model_controller.deleteoperation_from_opsgroup(op_group, operations, like)
        return result

    def get_entities(self, enttype_id, _dc=None):
        result = None
        result = self.model_controller.get_entities(enttype_id)
        return result

    def get_groups_map(self, userid=None, _dc=None):
        result = None
        result = self.model_controller.get_groups_map(userid)
        return result

    def get_users_map(self, groupid=None, _dc=None):
        result = None
        result = self.model_controller.get_users_map(groupid)
        return result

    def get_togroups_map(self, userid, _dc=None):
        result = None
        result = self.model_controller.get_togroups_map(userid)
        return result

    def delete_group(self, groupname):
        result = None
        group = self.user_info.get_group(groupname)
        if group != None:
            result = self.model_controller.delete_group(group.group_id)
        else:
            result = dict(False, 'The group with groupname ' + groupname + ' does not exists')
        return result
    # sam 1026
    def get_groupsdetails(self, type, _dc=None):
        result = None
        result = self.model_controller.get_groupsdetails(type)
        return result

    def group_info(self, groupname):
        pass
        
    def save_group_details(self, groupname, rolename, desc, type):
        result = None
        role = self.user_info.get_role(rolename)
        print role
        group = self.user_info.get_group(groupname)
        if group == None:
            result = self.model_controller.save_group_details(None, groupname, '', role.id, desc,type)
        else:
            result = dict(False, 'The group with groupname ' + groupname + ' already exists')
        return result

    def updatesave_group_details(self, groupid, groupname, userids, desc):
        result = None
        result = self.model_controller.updatesave_group_details(groupid, groupname, userids, desc)
        return result

    def adduser_to_group(self, groupname, usernames):
        result = self.model_controller.adduser_to_group(groupname, usernames)
        return result

    def removeuser_from_group(self, groupname, usernames):
        result = self.model_controller.deleteuser_from_group(groupname, usernames)
        return result

    def addrole_to_group(self, groupname, role):
        result = self.model_controller.addrole_to_group(groupname, role)
        return result

    def edit_group_details(self, groupid):
        result = None
        result = self.model_controller.edit_group_details(groupid)
        return result

    def get_tousers_map(self, groupid, _dc=None):
        result = None
        result = self.model_controller.get_tousers_map(groupid)
        return result

    def save_opsgroup_details(self, op_group, op_group_desc, name, operations):
        result = None
        opids = ''
        opsgrpid = self.user_info.get_opsgroup_id(op_group)
        opsgrouppriv = self.user_info.get_privilege(name)
        opnames = operations.split(',')
        for opname in opnames:
            operation = self.user_info.get_operation(opname)
            opid = to_str(operation.id)
            opids += opid + ','
        opids = opids[0:-1]
        if opsgrpid == None:
            result = self.model_controller.save_opsgroup_details(op_group, op_group_desc, opsgrouppriv.id, opids)
        else:
            result = dict(False, 'The operationgroup with groupname ' + op_group + ' already exists')
        return result

    def create_like_opsgroup(self, groupname, newgroupname, description=None):
        result = self.model_controller.create_like_opsgroup(groupname, newgroupname, description)
        return result

    def updatesave_opsgroup_details(self, opsgroupid, opsgroupname, opsgroupdesc, operation):
        result = None
        result = self.model_controller.updatesave_opsgroup_details(opsgroupid, opsgroupname, opsgroupdesc, operation)
        return result

    def edit_opsgroup_details(self, opsgroupid):
        result = None
        result = self.model_controller.edit_opsgroup_details(opsgroupid)
        return result

    def get_operations_map(self, opsgrpid=None, _dc=None):
        result = None
        result = self.model_controller.get_operations_map(opsgrpid)
        return result

    def get_tooperations_map(self, opsgroupid, _dc=None):
        result = None
        result = self.model_controller.get_tooperations_map(opsgroupid)
        return result

    def delete_opsgroup(self, opsgroupname):
        result = None
        opsgroupid = self.user_info.get_opsgroup_id(opsgroupname)
        if opsgroupid != None:
            result = self.model_controller.delete_opsgroup(opsgroupid)
        else:
            result = dict(False, 'The operationgroup with groupname ' + opsgroupname + ' does not exists')
        return result

    def get_operations(self, like=None, _dc=None):
        result = None
        result = self.model_controller.get_operations(like)
        return result

    def save_oper_det(self, opname, descr, context_disp, entityid, dispname, icon):
        result = None
        result = self.model_controller.save_oper_det(opname, descr, context_disp, entityid, dispname, icon)
        return result

    def edit_op_det(self, opid, enttype):
        result = None
        result = self.model_controller.edit_op_det(opid, enttype)
        return result

    def updatesave_op_det(self, opid, opname, desc, entid, context_disp, dispname, icon):
        result = None
        result = self.model_controller.updatesave_op_det(opid, opname, desc, entid, context_disp, dispname, icon)
        return result

    def delete_operation(self, name):
        result = None
        opsid = self.user_info.get_operation_id(name)
        if opsid != None:
            result = self.model_controller.delete_operation(opsid)
        else:
            result = dict(False, 'The operation with name ' + name + ' does not exists')
        return result

    def get_entitytype_map(self, opid=None, _dc=None):
        result = None
        result = self.model_controller.get_entitytype_map(opid)
        return result

    def get_toentitytype_map(self, opid, _dc=None):
        result = None
        result = self.model_controller.get_toentitytype_map(opid)
        return result

    def get_enttype(self, _dc=None):
        result = None
        result = self.model_controller.get_enttype()
        return result

    def get_enttype_for_chart(self, _dc=None):
        result = None
        result = self.model_controller.get_enttype_for_chart()
        return result

    def save_enttype_details(self, enttypename, dispname):
        result = None
        result = self.model_controller.save_enttype_details(enttypename, dispname)
        return result

    def edit_enttype_details(self, enttypeid):
        result = None
        result = self.model_controller.edit_enttype_details(enttypeid)
        return result
    # sam 1026
    def get_roles(self, type, _dc=None):
        result = None
        result = self.model_controller.get_roles(type)
        return result

    def get_roles_map(self, _dc=None):
        result = None
        result = self.model_controller.get_roles_map()
        return result
    # sam 1026
    def add_role(self, rolename, roledesc, type):
        rolename = to_unicode(rolename)
        roledesc = to_unicode(roledesc)
        role = self.user_info.get_role(rolename)
        if role == None:
            result = self.model_controller.add_role(rolename, roledesc, type, None, True)
        else:
            result = dict(False, 'The role with rolename ' + rolename + ' already exists')
        return result

    def create_like_role(self, rolename, newrolename, description=None):
        result = self.model_controller.create_like_role(rolename, newrolename, description)
        return result

    def assign_entity_privilege(self, rolename, entities, privilege):
        result = self.model_controller.assign_entity_privilege(rolename, entities, privilege)
        return result

    def remove_entity_privilege(self, rolename, entities):
        result = self.model_controller.remove_entity_privilege(rolename, entities)
        return result

    def addopsgroup_to_privilege(self, privilege, op_groups):
        result = self.model_controller.addopsgroup_to_privilege(privilege, op_groups)
        return result

    def removeopsgroup_from_privilege(self, privilege, op_groups):
        result = self.model_controller.deleteopsgroup_from_privilege(privilege, op_groups)
        return result

    def update_role(self, roleid, rolename, roledesc, reps):
        result = None
        result = self.model_controller.update_role(roleid, rolename, roledesc, reps)
        return result

    def delete_role(self, rolename):
        result = None
        role = self.user_info.get_role(rolename)
        if role != None:
            result = self.model_controller.delete_role(role.id)
        else:
            result = dict(False, 'The role with rolename ' + rolename + ' does not exists')
        return result

    def get_role_details(self, roleid):
        result = None
        result = self.model_controller.get_role_details(roleid)
        return result

    def get_role_rep(self, roleid=None, _dc=None):
        result = None
        result = self.model_controller.get_role_rep(roleid)
        return result

    def get_privileges(self, _dc=None):
        result = None
        result = self.model_controller.get_privileges()
        return result

    def get_privileges4opsg(self, _dc=None):
        result = None
        result = self.model_controller.get_privileges4opsg()
        return result

    def edit_privilege_det(self, privilegeid):
        result = None
        result = self.model_controller.edit_privilege_det(privilegeid)
        return result

    def get_opsgroups_map(self, privid=None, _dc=None):
        result = None
        result = self.model_controller.get_opsgroups_map(None)
        return result

    def get_toopsgroups_map(self, privilegeid, _dc=None):
        result = None
        result = self.model_controller.get_toopsgroups_map(privilegeid)
        return result

    def save_privilege_details(self, privilege, op_group):
        result = None
        privilegeid = None
        opsgroupid = to_str(self.user_info.get_opsgroup_id(op_group))
        pvlge = self.user_info.get_privilege(privilege)
        if pvlge == None:
            result = self.model_controller.save_privilege_details(privilegeid, privilege, opsgroupid)
        else:
            result = dict(False, 'The privilege with name ' + privilege + ' already exists')
        return result

    def updatesave_privilege_details(self, privilegeid, privilegename, opsgrups):
        result = None
        result = self.model_controller.updatesave_privilege_details(privilegeid, privilegename, opsgrups)
        return result

    def delete_privilege(self, name):
        result = None
        pvlge = self.user_info.get_privilege(name)
        if pvlge != None:
            result = self.model_controller.delete_privilege(pvlge.id)
        else:
            result = dict(False, 'The privilege with name ' + name + ' does not exists')
        return result

    def get_enttype(self, _dc=None):
        result = None
        result = self.model_controller.get_enttype()
        return result

    def get_enttype_for_chart(self, _dc=None):
        result = None
        result = self.model_controller.get_enttype_for_chart()
        return result

    def save_enttype_details(self, enttypename, dispname):
        result = None
        result = self.model_controller.save_enttype_details(enttypename, dispname)
        return result

    def edit_enttype_details(self, enttypeid):
        result = None
        result = self.model_controller.edit_enttype_details(enttypeid)
        return result

    def updatesave_enttype_details(self, enttypeid, enttypename, dispname):
        result = None
        result = self.model_controller.updatesave_enttype_details(enttypeid, enttypename, dispname)
        return result

    def delete_enttype(self, enttypeid):
        result = None
        result = self.model_controller.delete_enttype(enttypeid)
        return result



