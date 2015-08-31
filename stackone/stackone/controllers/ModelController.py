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
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
from stackone.controllers.XMLRPC.StorageXMLRPCController import StorageXMLRPCController
LOGGER = logging.getLogger('stackone.controllers')
from stackone.model.Authorization import AuthorizationService
from pylons.controllers.util import forward
from pylons.controllers import XMLRPCController
from stackone.viewModel.Userinfo import Userinfo

class ModelController(ControllerBase):

    user_info = stackone.viewModel.Userinfo.Userinfo()
    
    
    def add_role(self, rolename, roledesc, reps, type, is_cloudadmin, cli=False):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            result = self.user_info.add_role(session['userid'], rolename, roledesc, reps, type, is_cloudadmin, cli)
            return {'success': True, 'msg': 'Role Added.'}
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        return {'success': True, 'roles_det': result}

    
    def addgroup_to_user(self, username, groupnames):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            addgroup = self.user_info.addgroup_touser_det(username, groupnames)
            return addgroup
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def addoperation_to_opsgroup(self, opsgroup, operations, like=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.addoperation_toopsgroup(opsgroup, operations, like)
            return result
        
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

    
    def addopsgroup_to_privilege(self, privilege, opsgroups):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.addopsgroup_toprivilege_det(privilege, opsgroups)
            return result
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

    
    def addrole_to_group(self, groupname, role):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.addrole_togroup_det(groupname, role)
            return result
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def adduser_to_group(self, groupname, usernames):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.adduser_togroup_det(groupname, usernames)
            return result
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def assign_entity_privilege(self, rolename, entities, privilegename):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.assign_entity_privilege(rolename, entities, privilegename)
            return result
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))


    
    def change_user_password(self, userid, newpasswd, oldpasswd):
        try:
            result = None
            self.authenticate()
            if userid != '' and userid != session['userid']:
                if session['auth'].is_admin_role() == False:
                    return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.change_user_password(userid, newpasswd, oldpasswd)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        return {'success': True, 'user_det': result}

    
    def create_like_opsgroup(self, groupname, newgroupname, description=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.create_like_opsgroup(session['userid'], groupname, newgroupname, description)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return result

    
    def create_like_role(self, rolename, newrolename, description=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.create_like_role(session['userid'], rolename, newrolename, description)
            return result
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def delete_enttype(self, enttypeid):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            self.user_info.delete_enttype(enttypeid)
            return {'success': True, 'msg': 'Entitytype Removed.'}
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def delete_group(self, groupid):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            self.user_info.delete_group(groupid)
            return {'success': True, 'msg': 'Group Removed.'}
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def delete_operation(self, opid):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            self.user_info.delete_operation(opid)
            return {'success': True, 'msg': 'Operation Deleted.'}
        
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

    
    def delete_opsgroup(self, opsgroupid):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            self.user_info.delete_opsgroup(opsgroupid)
            return {'success': True, 'msg': 'Opsgroup Removed.'}
        
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def delete_privilege(self, privilegeid):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            self.user_info.delete_privilege(privilegeid)
            return {'success': True, 'msg': 'Privilege Deleted.'}
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def delete_role(self, roleid):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            self.user_info.delete_role(roleid)
            return {'success': True, 'msg': 'Role Deleted.'}
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

    
    def delete_user(self, userid):
        try:
            self.authenticate()
            self.user_info.delete_user(userid)
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            return {'success': True, 'msg': 'User Removed.'}
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def deletegroup_from_user(self, username, groupnames):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.deletegroup_fromuser_det(username, groupnames)
            return result
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def deleteoperation_from_opsgroup(self, opsgroup, operations, like=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.deleteoperation_fromopsgroup(opsgroup, operations, like)
            return result
        
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

    
    def deleteopsgroup_from_privilege(self, privilege, opsgroups):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.deleteopsgroup_fromprivilege_det(privilege, opsgroups)
            return result
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

    
    def deleteuser_from_group(self, groupname, usernames):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.deleteuser_fromgroup_det(groupname, usernames)
            return result
        
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def edit_enttype_details(self, enttypeid):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.edit_enttype_details(enttypeid)
        
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'edit_enttype_det': result}

    
    def edit_group_details(self, groupid):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.edit_group_details(groupid)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        return {'success': True, 'edit_group_det': result}

    
    def edit_op_det(self, opid, enttype):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.edit_op_det(opid, enttype)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        return {'success': True, 'edit_op_det': result}

    
    def edit_opsgroup_details(self, opsgroupid):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.edit_opsgroup_details(opsgroupid)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'edit_opsgroup_det': result}

    
    def edit_privilege_det(self, privilegeid):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.edit_privilege_det(privilegeid)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        return {'success': True, 'edit_privilege_det': result}

    
    def edit_user_det(self, userid):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.edit_user_det(userid)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        return {'success': True, 'edit_user_det': result}

    
    def get_cloud_users(self, type, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_cloud_users(type)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_cloud_users_list(self, vdc_id=None, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_cloud_users_list(vdc_id)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_entities(self, enttype_id, _dc=None):
        try:
            self.authenticate()
            result = self.user_info.get_entities(enttype_id)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        return dict(success=True, rows=result)

    
    def get_entities_bytype(self, type, parententityid=None, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_entities_bytype(session['auth'], type, parententityid)
            return result
        
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

    
    def get_entitytype_map(self, opid=None, _dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_entitytype_map(opid)
            return {'success': True, 'entitytype_det': result}
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

    
    def get_entitytype_role(self, type, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            result = self.user_info.get_entitytype_role(type)
        
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_enttype(self, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_enttype()
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_enttype_for_chart(self, _dc=None):
        try:
            self.authenticate()
            result = self.user_info.get_enttype_for_chart(session['auth'].user)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_groups_map(self, userid=None, _dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_groups_map(userid)
            return {'success': True, 'group_det': result}
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        

    
    def get_groupsdetails(self, type, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_groupsdetails(type)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_operations(self, like=None, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_operations(like)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_operations_map(self, opsgrpid=None, _dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_operations_map(opsgrpid)
            return {'success': True, 'operation_det': result}
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        

    
    def get_opsgroups(self, like=None, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_opsgroups(like)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_opsgroups_map(self, privid=None, _dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_opsgroups_map(privid)
            return {'success': True, 'opsgroup_det': result}
        
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        

    
    def get_privileges(self, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_privileges()
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_privileges4opsg(self, type, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_privileges4opsg(type)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_role_details(self, roleid):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_role_details(roleid)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, role=result)

    
    def get_role_rep(self, roleid=None, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_role_rep(roleid)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_roles(self, type, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_roles(type)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_roles_map(self, type, _dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_roles_map(type)
            return {'success': True, 'role_det': result}
        
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

    
    def get_toentitytype_map(self, opid, _dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_toentitytype_map(opid)
            return {'success': True, 'toentitytype_det': result}
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        

    
    def get_togroups_map(self, userid, _dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_togroups_map(userid)
            return {'success': True, 'togroup_det': result}
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        

    
    def get_tooperations_map(self, opsgroupid, _dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_tooperations_map(opsgroupid)
            return {'success': True, 'tooperations_det': result}
        
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def get_toopsgroups_map(self, privilegeid, _dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_toopsgroups_map(privilegeid)
            return {'success': True, 'toopsgroup_det': result}
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        

    
    def get_tousers_map(self, groupid, _dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_tousers_map(groupid)
            return {'success': True, 'touser_det': result}
        
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def get_user_role_map(self, _dc=None):
        result = None
        self.authenticate()
        result = self.user_info.get_user_role_map()
        return result

    
    def get_user_status_map(self, _dc=None):
        result = None
        self.authenticate()
        if session['auth'].is_admin_role() == False:
            return dict(success=False, msg=constants.NO_PRIVILEGE)
        
        result = self.user_info.get_user_status_map()
        return result

    
    def get_users(self, type, _dc=None):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_users(type)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        
        return dict(success=True, rows=result)

    
    def get_users_map(self, type, groupid=None, _dc=None):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.get_users_map(type, groupid)
            return {'success': True, 'user_det': result}
        
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
    
    def group_info(self, groupname):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, message=constants.NO_PRIVILEGE)
            
            result = self.user_info.groupinfo(groupname)
            return result
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

    
    def has_permission(self, type, groupid=None, _dc=None):
        auth = AuthorizationService()
        ent = self.user_info.get_entity(entname)
        if ent is None:
            return dict(success=False, result='The entity does not exists')
        
        try:
            if username != None and username != '':
                if session['auth'].is_admin_role() == False:
                    return dict(success=False, result=constants.NO_PRIVILEGE)
                
                userobj = self.user_info.get_user(username)
                if userobj != None:
                    auth.user = userobj
                    return dict(success=True, result=auth.has_privilege(operation, ent))
                
                return dict(success=False, result='The user does not exists')
            
            permits = session['auth'].has_privilege(operation, ent)
            return dict(success=True, result=permits)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, result=to_str(ex).replace("'", ''))
        

    
    def list_user_operations(self, entname, username=None):
        result = []
        
        try:
            ent = self.user_info.get_entity(entname)
            if ent is None:
                return dict(success=False, msg='The entity does not exists')
            
            if username != None and username != '':
                if session['auth'].is_admin_role() == False:
                    return dict(success=False, msg=constants.NO_PRIVILEGE)
                
                userobj = self.user_info.get_user(username)
                if userobj != None:
                    auth = AuthorizationService()
                    auth.user = userobj
                    ops = auth.get_ops(ent)
                else:
                    return dict(success=False, msg='The user does not exists')
                
            else:
                ops = session['auth'].get_ops(ent)
                    
            for op in ops:
                result.append(op.name)
            
            return dict(success=True, ops=result)
            
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))


    
    def remove_entity_privilege(self, rolename, entities):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.remove_entity_privilege(rolename, entities)
            return result
        
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

    
    def save_enttype_details(self, enttypename, dispname):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.save_enttype_details(session['userid'], enttypename, dispname)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'opsgroup_det': result}

    
    def save_group_details(self, groupid, groupname, userids, role, desc, type):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.save_group_details(session['userid'], groupid, groupname, userids, role, desc, type)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'group_det': result}

    
    def save_oper_det(self, opname, descr, context_disp, entityid, dispname, icon):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.save_oper_det(session['userid'], opname, descr, context_disp, entityid, dispname, icon)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        return {'success': True, 'operation_det': result}

    
    def save_opsgroup_details(self, opsgroupname, opsgroupdesc, opsgrouppriv, operation):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.save_opsgroup_details(session['userid'], opsgroupname, opsgroupdesc, opsgrouppriv, operation)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'opsgroup_det': result}

    
    def save_privilege_details(self, privilegeid, privilegename, opsgrups):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.save_privilege_details(session['userid'], privilegeid, privilegename, opsgrups)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        return {'success': True, 'privilege_det': result}

    
    def save_user_det(self, userid, username, fname, lname, displayname, password, email, phone, status, type):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.save_user_det(session['userid'], userid, username, fname, lname, displayname, password, email, phone, status, type)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'user_det': result}

    
    def update_role(self, roleid, rolename, roledesc, reps, type, is_cloudadmin):
        try:
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            self.user_info.update_role(session['userid'], roleid, rolename, roledesc, reps, type, is_cloudadmin)
            return {'success': True, 'msg': 'Role Updated.'}
            
        except Exception as ex:
            print_traceback()
            print ex
            return dict(success=False, msg=to_str(ex).replace("'", ''))

    
    def updatesave_enttype_details(self, enttypeid, enttypename, dispname):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.updatesave_enttype_details(session['userid'], enttypeid, enttypename, dispname)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'opsgroup_det': result}

    
    def updatesave_group_details(self, groupid, groupname, userids, role, desc):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.updatesave_group_details(session['userid'], groupid, groupname, userids, role, desc)
        
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'group_det': result}

    
    def updatesave_op_det(self, opid, opname, desc, entid, context_disp, dispname, icon):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.updatesave_op_det(session['userid'], opid, opname, desc, entid, context_disp, dispname, icon)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'operation_det': result}

    
    def updatesave_opsgroup_details(self, opsgroupid, opsgroupname, opsgroupdesc, opsgrouppriv, operation):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.updatesave_opsgroup_details(session['userid'], opsgroupid, opsgroupname, opsgroupdesc, opsgrouppriv, operation)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'opsgroup_det': result}

    
    def updatesave_privilege_details(self, privilegeid, privilegename, opsgrups):
        try:
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.updatesave_privilege_details(session['userid'], privilegeid, privilegename, opsgrups)
            
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'privilege_det': result}

    
    def updatesave_user_det(self, userid, username, fname, lname, displayname, email, phone, status, changepass, newpasswd):
        try:
            print userid, username, fname, lname, displayname, email, phone, status,'########################'
            result = None
            self.authenticate()
            if session['auth'].is_admin_role() == False:
                return dict(success=False, msg=constants.NO_PRIVILEGE)
            
            result = self.user_info.updatesave_user_det(session['userid'], userid, username, fname, lname, displayname, email, phone, status, changepass, newpasswd)
        
        except Exception as ex:
            print_traceback()
            return {'success': False, 'msg': to_str(ex).replace("'", '')}
        
        return {'success': True, 'user_det': result}

    
    def user_information(self, username):
        self.authenticate()
        if session['auth'].is_admin_role() == False:
            return dict(success=False, message=constants.NO_PRIVILEGE)
        
        result = self.user_info.userinfo(username)
        return result

