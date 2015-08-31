import tg
from sqlalchemy.sql.expression import not_
from sqlalchemy.orm import eagerload
from stackone.model.DBHelper import DBHelper
from stackone.model.deployment import Deployment
from stackone.model.auth import User, Group, Role
from stackone.model.Operation import Operation, OperationGroup
from stackone.model.Privilege import Privilege
from stackone.model.services import Task
from stackone.model.Entity import Entity, EntityType
from stackone.model.VM import VM
from stackone.model.ManagedNode import ManagedNode
from stackone.model.RoleEntityPrivilege import RoleEntityPrivilege
from stackone.core.services.tasks import *
##from stackone.cloud.core.model.CloudTasks import *
import simplejson as json
from datetime import datetime
from stackone.model import DBSession
from stackone.core.utils.utils import to_unicode, to_str, print_traceback, convert_to_CMS_TZ
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from pylons.i18n import ugettext as _
from datetime import datetime, timedelta
import logging
import Basic
LOGGER = logging.getLogger('stackone.viewModel')
class Userinfo():
    def save_user_det(self, login, userid, username, fname, lname, displayname, password, email, phone, status, type):
        user1 = DBSession.query(User).filter(User.user_name == username).first()
        if user1 is None:
            if not self.check_email(email):
                return 'Email_exist'
            self.check_email(email)
            result = []
            user = User()
            user.password = password
            user.firstname = fname
            user.lastname = lname
            user.display_name = displayname
            user.user_name = username
            user.phone_number = phone
            user.email_address = email
            user.created_by = login
            user.modified_by = login
            user.type = type
            user.created_date = datetime.now()
            if status == 'InActive':
                user.status = False
            DBHelper().add(user)
            return result
        result = 'False'
        return result
        return None

    def delete_user(self, userid):
        userid = int(userid)
        user = DBSession.query(User).filter(User.user_id == userid).first()
        if user is not None:
            if user.user_name in constants.DEFAULT_USERS:
                raise Exception('Can not delete ' + user.user_name + ' user.')
            DBHelper().delete_all(User, [], [User.user_id == userid])
        return None

    def check_email(self, email, userid=None):
        query = DBSession.query(User).filter(User.email_address == email)
        if userid is not None:
            query = query.filter(User.user_id != userid)
        obj = query.first()
        if obj is None:
            return True
        return False
        return None

    def updatesave_user_det(self, login, userid, username, fname, lname, displayname, email, phone, status, changepass, newpasswd):
        result = []
        self.check_email(email, userid)
        
        if not self.check_email(email, userid):
            self.check_email(email, userid)
            return 'Email_exist'
        
        user = DBSession.query(User).filter(User.user_id == userid).first()
        user.user_name = username
        user.firstname = fname
        user.lastname = lname
        user.display_name = displayname
        user.email_address = email
        user.phone_number = phone
        user.modified_date = datetime.now()
        user.modified_by = login
        newpasswd = newpasswd
        if changepass == 'true':
            user.password = newpasswd
        if status == 'InActive':
            user.status = False
        else:
            user.status = True
        DBHelper().update(user)
        return result

    def addgroup_touser_det(self, username, groupnames):
        msg = ''
        user = DBSession.query(User).filter(User.user_name == username).first()
        
        if user!=None:
            listreject = []
            try:
                for groupname in groupnames:
                    group = DBSession.query(Group).filter(Group.group_name == groupname).first()
                    if group != None:
                        user.groups.append(group)

                    listreject.append(groupname)

                DBHelper().update(user)
                if listreject != []:
                    msg += 'some groups does not exists' + to_str(listreject)
                else:
                    msg = 'The groups successfully added'

            except Exception as ex:
                print ex
                return dict(success=False, msg=to_str(ex))

            return dict(success=True, msg=msg)

        msg = 'The user ' + username + ' does not exists'
        return dict(success=True, msg=msg)
        return None
        
        
        
    def deletegroup_fromuser_det(self, username, groupnames):
        msg = ''
        user = DBSession.query(User).filter(User.user_name == username).first()
        
        if user!=None:
            listreject = []
            try:
                for groupname in groupnames:
                    group = DBSession.query(Group).filter(Group.group_name == groupname).first()
                    if group != None:
                        user.groups.remove(group)
                    else:
                        listreject.append(groupname)

                DBHelper().update(user)
                if listreject != []:
                    msg += 'some groups does not exists' + to_str(listreject)
                else:
                    msg = 'The groups successfully deleted'

            except Exception as ex:
                print ex
                return dict(success=False, msg=to_str(ex))

            return dict(success=True, msg=msg)

        msg = 'The user ' + username + ' does not exists'
        return dict(success=True, msg=msg)

        
    def edit_user_det(self, userid):
        result = []
        gnames = ''
        user = DBSession.query(User).filter(User.user_id == userid).first()
        for g in user.groups:
            gnames += g.group_name + ','
        if user.status == True:
            status = 'Active'
        else:
            status = 'InActive'
        result.append(dict(userid=user.user_id, username=user.user_name, fname=user.firstname, lname=user.lastname, displayname=user.display_name, password=user._password, repass=user._password, phone=user.phone_number, email=user.email_address, status=status, createdby=user.created_by, modifiedby=user.modified_by, createddate=user.created_date, modifieddate=user.modified_date, groupname=gnames))
        return result

        
    def change_user_password(self, userid, newpasswd, oldpasswd):
        result = []
        user = DBSession.query(User).filter(User.user_name == userid).first()
        if not user:
            raise Exception('Can not find this user. Maybe this is a ldap user.')
        if user.validate_password(oldpasswd):
            user.password = newpasswd
            DBHelper().update(user)
            return result
        raise Exception('Old Password is not valid.<br>Please enter valid Password.')

        
    def get_togroups_map(self, userid):
        result = []
        user = DBSession.query(User).filter(User.user_id == userid).first()
        groups = user.groups
        for g in groups:
            gid = g.group_id
            gname = g.group_name
            result.append(dict(groupid=gid, groupname=gname))
        return result

    def get_users(self, type):
        result = []
        users = DBSession.query(User).filter(User.type == type).all()
        for u in users:
            strgroup = ''
            uid = u.user_id
            uname = u.user_name
            name = ''
            if u.firstname is not None:
                name = u.firstname + ' ' + u.lastname
            for g in u.groups:
                strgroup += g.group_name + ','
            strgroup = strgroup[0:-1]
            result.append(dict(userid=uid, username=uname, name=name, group=strgroup))
        return result

    def get_cloud_users_list(self, vdc_id=None):
        result = []
        groups = []
        try:
            if vdc_id != None:
                gids = []
                vdc = DBSession.query(VDC).filter(VDC.id == vdc_id).first()
                if vdc != None:
                    gids.append(vdc.operator_group_id)
                    gids.append(vdc.user_group_id)
                    print gids
                    groups = DBSession.query(Group).filter(Group.group_id.in_(gids)).all()
            cseps = DBSession.query(CSEP.group_id).all()
            csep_group_ids=[to_str(csep.group_id) for csep in cseps]
            csep_groups=DBSession.query(Group).filter(Group.group_id.in_(csep_group_ids)).all()
            users=DBSession.query(User).all()
            for u in users:
                if u.user_name == constants.DEFAULT_USERS[0]:
                    continue
                if len(set(u.groups) & set(csep_groups)):
                    msg='Skip csep user: %s' % u.user_name
                    print msg
                    LOGGER.info(msg)
                    continue
                
                strgroup=''
                sts=''
                uid=u.user_id
                uname=u.user_name
                name=''
                grp_lst=[]
                if u.firstname is not None:
                    name=u.firstname + ' ' + u.lastname
                    
                grp=''
                for g in u.groups:
                    strgroup += g.group_name + ','
                    grp_lst.append(g.group_name)
                    groupstr=g.group_name.split('-')
                    if len(groupstr)==2:
                        if groupstr[1]:
                            if grp=='':
                                grp += groupstr[1]
                            else:
                                grp += ',' + groupstr[1]
                strgroup=strgroup[0:-1]
                if vdc!=None:
                    (a, b) = [group.group_name for group in groups]
                    
                    if a not in grp_lst and b not in grp_lst:
                        sts += 'False'
                    else:
                        sts += 'True'
                        
                if u.status == True:
                    status='Active'
                else:
                    status='InActive'
                result.append(dict(userid=uid, username=uname, name=name, fname=u.firstname, lname=u.lastname, nname=u.display_name, email=u.email_address, phone=u.phone_number, status=status, rol=grp, vdc=strgroup, sts=sts))

        except Exception as e:
            print_traceback()

        return result



    def get_cloud_users(self, type):
        result = []
        operatoruser = ''
        users = DBSession.query(User).filter(User.type == type).all()
        for u in users:
            strgroup = ''
            uid = u.user_id
            uname = u.user_name
            name = ''
            if u.firstname is not None:
                name = u.firstname + ' ' + u.lastname
            for g in u.groups:
                strgroup += g.group_name + ','
            strgroup = strgroup[0:-1]
            result.append(dict(userid=uid, username=uname, name=name, vdc=strgroup))
        return result

    def userinfo(self, username):
        userinfo = {}
        msg = 'The User ' + username + ' does not exists'
        
        try:
            user = DBSession.query(User).filter(User.user_name == username).first()
            
            if user!=None:
                if user.phone_number == '' or user.phone_number == None:
                    tphone = 'Nil'
                else:
                    tphone = user.phone_number
                userinfo['Firstname'] = user.firstname
                userinfo['Lastname'] = user.lastname
                userinfo['Telephone'] = tphone
                userinfo['Email'] = user.email_address
                userinfo['Display Name'] = user.display_name
                grps = ''

                for grp in user.groups:
                    grps += grp.group_name + ','

                userinfo['Groups'] = grps
                return dict(success=True, info=userinfo)

            return dict(success=False, message=msg)

        except Exception as e:
            print_traceback()
            return dict(success=False, message=to_str(e))

        return None

    def get_user(self, username):
        user = None
        user = DBSession.query(User).filter(User.user_name == username).first()
        return user

    def save_group_details(self, login, groupid, groupname, userids, role, desc, type):
        dupGrp = None
        group = Group()
        db = DBHelper()
        session = DBHelper().get_session()
        dupGrp = session.query(Group).filter(Group.group_name == groupname).first()
        if dupGrp is None:
            result = []
            group.group_name = groupname
            group.role_id = role
            group.created_by = login
            group.modified_by = login
            group.created_date = datetime.now()
            group.description = desc
            group.type = type
            L = userids.split(',')
            if userids != '':
                for i in L:
                    user = session.query(User).filter(User.user_id == int(i)).first()
                    group.users.append(user)
            db.add(group)
            return result
        result = 'False'
        return result
        return None

    def create_group(self, user_name, groupname, role_id, desc, type, userids):
        try:
            dupGrp = DBSession.query(Group).filter(Group.group_name == groupname).first()
            if not dupGrp:
                dupGrp
                group = Group()
                group.group_name = groupname
                group.role_id = role_id
                group.created_by = user_name
                group.modified_by = user_name
                group.created_date = datetime.now()
                group.description = desc
                group.type = type
                L = userids.split(',')
                if userids != '':
                    for i in L:
                        user = DBSession.query(User).filter(User.user_id == int(i)).first()
                        group.users.append(user)
                DBSession.add(group)
                return group
            return dupGrp
        except Exception as ex:
            LOGGER.error(str(ex))
            traceback.print_exc()
            raise ex

    def get_group(self, groupname):
        group = None
        group = DBSession.query(Group).filter(Group.group_name == groupname).first()
        return group

    def groupinfo(self, groupname):
        groupinfo = {}
        msg = 'The group ' + groupname + ' does not exists'
        group = DBSession.query(Group).filter(Group.group_name == groupname).first()
        try:
            if group!=None:
                if group.created_by == '':
                    crby = 'Administrator'
                else:
                    crby = group.created_by

                groupinfo['name'] = groupname
                groupinfo['display_name'] = group.display_name
                groupinfo['createdby'] = crby
                groupinfo['description'] = group.description
                return dict(success=True, message=groupinfo)

            return dict(success=False, message=msg)

        except Exception as e:
            return dict(success=False, message=to_str(e))

        return None
        
        
    def delete_group(self, groupid):
        groupid = int(groupid)
        group = DBSession.query(Group).filter(Group.group_id == groupid).first()
        if group is not None:
            if group.group_name in constants.DEFAULT_GROUPS:
                raise Exception('Can not delete ' + group.group_name + ' group.')
            DBHelper().delete_all(Group, [], [Group.group_id == groupid])
        return None

    def updatesave_group_details(self, login, groupid, groupname, userids, role, desc):
        result = []
        group = Group()
        session = DBHelper().get_session()
        crole = session.query(Role).filter(Role.id == role).first()
        if groupname in constants.DEFAULT_GROUPS:

            if crole.name not in constants.DEFAULT_ROLES:
                raise Exception('Can not change role for ' + groupname)
            user = session.query(User).filter(User.user_name == constants.DEFAULT_USERS[0]).first()
            new_ids = []
            if userids != '':
                new_ids =userids.split(',')

            new_ids=[int(id) for id in new_ids]

            if user.user_id not in new_ids:
                raise Exception('Can not remove user ' + user.user_name + ' from ' + groupname)

        group = session.query(Group).filter(Group.group_id == groupid).first()
        group.group_name = groupname
        group.role_id = role
        group.description = desc
        group.modified_date = datetime.now()
        group.modified_by = login
        
        for user in group.users:
            group.users.remove(user)
        if userids != '':
            L = userids.split(',')
            for i in L:
                user = session.query(User).filter(User.user_id == int(i)).first()
                group.users.append(user)
        DBHelper().update(group)
        return result


    def adduser_togroup_det(self, groupname, usernames):
        msg = ''
        group = DBSession.query(Group).filter(Group.group_name == groupname).first()
        
        if group!=None:
            listreject = []
            try:
                for username in usernames:
                    user = DBSession.query(User).filter(User.user_name == username).first()
                    if user != None:
                        group.users.append(user)

                    listreject.append(username)

                DBHelper().update(group)
                if listreject != []:
                    msg += 'some users does not exists' + to_str(listreject)
                else:
                    msg = 'Users successfully added.'

            except Exception as ex:
                print_traceback()
                return dict(success=False, msg=to_str(ex))

            return dict(success=True, msg=msg)

        msg = 'The group ' + groupname + ' does not exists'
        return dict(success=True, msg=msg)
        return None

        
    def deleteuser_fromgroup_det(self, groupname, usernames):
        msg = ''
        group = DBSession.query(Group).filter(Group.group_name == groupname).first()
        
        if group!=None:
            listreject = []
            try:
                for username in usernames:
                    user = DBSession.query(User).filter(User.user_name == username).first()
                    if user != None:
                        group.users.remove(user)

                    listreject.append(username)

                DBHelper().update(group)
                if listreject != []:
                    msg += 'some groups does not exists' + to_str(listreject)
                else:
                    msg = 'Users successfully deleted.'

            except Exception as ex:
                print_traceback()
                return dict(success=False, msg=to_str(ex))

            return dict(success=True, msg=msg)

        msg = 'The group ' + groupname + ' does not exists'
        return dict(success=True, msg=msg)
        return None
        
        
    def addrole_togroup_det(self, groupname, rolename):
        result = None
        try:
            group = DBSession.query(Group).filter(Group.group_name == groupname).first()
            if group == None:
                return dict(success=False, msg='The group ' + groupname + ' does not exists')

            role = DBSession.query(Role).filter(Role.name == rolename).first()
            if role == None:
                return dict(success=False, msg='The role ' + rolename + ' does not exists')

            if group.role_id == role.id:
                result = 'The role ' + rolename + ' is already assigned to the group ' + groupname
                return dict(success=False, msg=result)

            group.role_id = role.id
            DBHelper().update(group)
            return dict(success=True, msg='The role ' + rolename + ' is added to ' + groupname)

        except Exception as ex:
            print ex
            return dict(success=False, msg=to_str(ex))

        return None

        
    def get_groupsdetails(self, type):
        result = []
        groups = DBSession.query(Group).filter(Group.type == type).all()
        for g in groups:
            groupid = g.group_id
            groupname = g.group_name
            groupdesc = g.description
            rolename = ''
            if g.role is not None:
                rolename = g.role.name
            result.append(dict(groupid=groupid, groupname=groupname, rolename=rolename, desc=groupdesc))
        return result

    def edit_group_details(self, groupid):
        result = []
        group = Group()
        session = DBHelper().get_session()
        group = session.query(Group).filter(Group.group_id == groupid).first()
        role = group.role
        srole = ''
        roleid = ''
        if role is not None:
            srole = role.name
            roleid = role.id
        print 'Role under edit group is ',
        print srole
        result.append(dict(groupid=group.group_id, groupname=group.group_name, role=srole, roleid=roleid, createdby=group.created_by, modifiedby=group.modified_by, createddate=group.created_date, modifieddate=group.modified_date, desc=group.description))
        return result

    def get_tousers_map(self, groupid):
        result = []
        session = DBHelper().get_session()
        group = session.query(Group).filter(Group.group_id == groupid).first()
        users = group.users
        for u in users:
            uid = u.user_id
            uname = u.user_name
            result.append(dict(userid=uid, username=uname))
        return result

    def get_groups_map(self, userid=None):
        result = []
        session = DBHelper().get_session()
        groups = DBHelper().get_all(Group)
        user = session.query(User).filter(User.user_id == userid).first()
        for g in groups:
            gid = g.group_id
            gname = g.group_name
            result.append(dict(groupid=gid, groupname=gname))
        if userid is None:
            return result
        for grp in user.groups:
            i = 0
            for group in result:
                if grp.group_id == group['groupid']:
                    del result[i]
                    break
                i += 1
        return result

    def get_users_map(self, type, groupid=None):
        result = []
        users = DBSession.query(User).filter(User.type == type).all()
        session = DBHelper().get_session()
        group = session.query(Group).filter(Group.group_id == groupid).first()
        for u in users:
            uid = u.user_id
            uname = u.user_name
            result.append(dict(userid=uid, username=uname))
        if groupid is None:
            return result
        for grp in group.users:
            i = 0
            for user in result:
                if grp.user_id == user['userid']:
                    del result[i]
                    break
                i += 1
        return result

    def get_tooperations_map(self, opsgroupid):
        result = []
        session = DBHelper().get_session()
        opsgroup = session.query(OperationGroup).filter(OperationGroup.id == opsgroupid).first()
        operatiions = opsgroup.operations
        for o in operatiions:
            oid = o.id
            oname = o.name
            result.append(dict(operationid=oid, operationname=oname))
        return result

    def get_operations_map(self, opsgrpid=None):
        result = []
        operation = DBHelper().get_all(Operation)
        session = DBHelper().get_session()
        opsgroup = session.query(OperationGroup).filter(OperationGroup.id == opsgrpid).first()
        for o in operation:
            opid = o.id
            opname = o.name
            result.append(dict(operationid=opid, operationname=opname))
        if opsgrpid is None:
            return result
        for oprs in opsgroup.operations:
            i = 0
        for operation in result:
            if oprs.id == operation['operationid']:
                del result[i]
                break
            i += 1
        return result

    def save_opsgroup_details(self, login, opsgroupname, opsgroupdesc, opsgrouppriv, operation):
        dupOpsgrp = None
        db = DBHelper()
        session = DBHelper().get_session()
        dupOpsgrp = session.query(OperationGroup).filter(OperationGroup.name == opsgroupname).first()
        opsgroup = OperationGroup()
        if dupOpsgrp is None:
            result = []
            opsgroup.name = opsgroupname
            opsgroup.description = opsgroupdesc
            opsgroup.privilege_id = opsgrouppriv
            opsgroup.created_by = login
            opsgroup.modified_by = login
            opsgroup.created_date = datetime.now()
            L = operation.split(',')
            for i in L:
                oper = session.query(Operation).filter(Operation.id == int(i)).first()
                opsgroup.operations.append(oper)
            db.add(opsgroup)
            return result
        result = 'False'
        return result
        return None

    def create_like_opsgroup(self, login, opsgroup, newopsgroup, description):
        db = DBHelper()
        newopsGroup = DBSession.query(OperationGroup).filter(OperationGroup.name == newopsgroup).first()
        if newopsGroup != None:
            return dict(success=False, msg='The operationgroup ' + newopsgroup + ' already exists')
        opsGroup = DBSession.query(OperationGroup).filter(OperationGroup.name == opsgroup).first()
        if description != '':
            desc = description
        else:
            desc = opsGroup.description
        newopsGroup = OperationGroup()
        if opsGroup != None:
            newopsGroup.name = newopsgroup
            newopsGroup.description = desc
            newopsGroup.operations = opsGroup.operations
            newopsGroup.created_by = login
            newopsGroup.modified_by = login
            newopsGroup.created_date = datetime.now()
            newopsGroup.privilege_id = opsGroup.privilege_id
            db.add(newopsGroup)
            return dict(success=True, msg='success')
        return dict(success=False, msg='The operationgroup ' + opsgroup + ' does not exists')
        return None

    def addoperation_toopsgroup(self, opsgroupname, operationnames, like=None):
        msg = ''
        opsgroup = DBSession.query(OperationGroup).filter(OperationGroup.name == opsgroupname).first()
        if opsgroup!=None:
            listreject = []
            try:
                for opname in operationnames:
                    op = self.get_operation(opname)
                    if op != None:
                        opsgroup.operations.append(op)
                        continue
                if like!='' and like!=None:
                    listreject.append(opname)

                    operations = DBHelper().filterby(Operation, [], [Operation.name.like(like)])

                    for op in operations:
                        opsgroup.operations.append(op)

                DBHelper().update(opsgroup)
                if listreject != []:
                    msg += 'Following operations does not exist :' + to_str(listreject)
                else:
                    msg = 'Operations successfully added.'

            except Exception as ex:
                print_traceback()
                return dict(success=False, msg=to_str(ex))

            return dict(success=True, msg=msg)

        msg = 'The operation group ' + opsgroupname + ' does not exists'
        return dict(success=False, msg=msg)
        return None
        
        
    def deleteoperation_fromopsgroup(self, opsgroupname, operationnames, like=None):
        msg = ''
        opsgroup = DBSession.query(OperationGroup).filter(OperationGroup.name == opsgroupname).first()
        
        if opsgroup!=None:
            listreject = []
            
            try:
                for opname in operationnames:
                    op = self.get_operation(opname)

                    if op!=None:
                        if op in opsgroup.operations:
                            opsgroup.operations.remove(op)


                    listreject.append(opname)

                if like != '' and like != None:
                    operations = DBHelper().filterby(Operation, [], [Operation.name.like(like)])
                    for op in operations:
                        if op in opsgroup.operations:
                            opsgroup.operations.remove(op)
                
                DBHelper().update(opsgroup)
                if listreject != []:
                    msg += 'Following operations does not exist :' + to_str(listreject)
                else:
                    msg = 'Operations successfully removed.'

            except Exception as ex:
                print_traceback()
                return dict(success=False, msg=to_str(ex))

            return dict(success=True, msg=msg)

        msg = 'The operation group ' + opsgroupname + ' does not exists'
        return dict(success=False, msg=msg)
        return None
        

    def get_opsgroup_id(self, name):
        opsgroup = None
        opsgroup = DBSession.query(OperationGroup).filter(OperationGroup.name == name).first()
        try:
            if opsgroup:
                opsgroupid = opsgroup.id
                return opsgroupid
        except Exception as ex:
            print ex
        return None

        
    def updatesave_opsgroup_details(self, login, opsgroupid, opsgroupname, opsgroupdesc, opsgrouppriv, operation):
        result = []
        opsgroup = OperationGroup()
        db = DBHelper()
        session = DBHelper().get_session()
        opsgroup = session.query(OperationGroup).filter(OperationGroup.id == opsgroupid).first()
        opsgroup.name = opsgroupname
        opsgroup.description = opsgroupdesc
        opsgroup.privilege_id = opsgrouppriv
        opsgroup.modified_date = datetime.now()
        opsgroup.modified_by = login
        operation = operation[0:-1]
        L = operation.split(',')
        for i in L:
            operation = session.query(Operation).filter(Operation.id == int(i)).first()
            opsgroup.operations.append(operation)
        db.update(opsgroup)
        return result

        
    def edit_opsgroup_details(self, opsgroupid):
        result = []
        session = DBHelper().get_session()
        opsgroup = session.query(OperationGroup).filter(OperationGroup.id == opsgroupid).first()
        opsgrpid = opsgroup.id
        opsgrpname = opsgroup.name
        opsgrpdesc = opsgroup.description
        opsgrppriv = opsgroup.privilege_id
        opsgroupprivname = ''
        if opsgroup.privilege is not None:
            opsgroupprivname = opsgroup.privilege.name
        result.append(dict(opsgroupid=opsgrpid, opsgroupname=opsgrpname, opsgroupdesc=opsgrpdesc, opsgrouppriv=opsgrppriv, opsgroupprivname=opsgroupprivname, createdby=opsgroup.created_by, modifiedby=opsgroup.modified_by, createddate=opsgroup.created_date, modifieddate=opsgroup.modified_date))
        return result

        
    def get_opsgroups(self, like=None):
        result = []
        filters = []
        if like != '' and like != None:
            filters.append(OperationGroup.name.like(like))
        opsgrp = DBHelper().filterby(OperationGroup, [], filters)
        for og in opsgrp:
            i = 0
            sname = og.name
            opsgroupid = og.id
            strop = ''
            stropid = ''
            for o in og.operations:
                strop = o.name
                desc = o.description
                opsgroupname = ''
                stropid = o.id
                if i == 0:
                    opsgroupname = og.name
                i += 1
                for e in o.entityType:
                    strent = e.display_name
                result.append(dict(opsgroupid=opsgroupid, opsgrpname=opsgroupname, opname=strop, opid=stropid, desc=desc, entitytype=strent, searchName=sname))
        return result

        
    def delete_opsgroup(self, opsgroupid):
        opsgroupid = int(opsgroupid)
        DBHelper().delete_all(OperationGroup, [], [OperationGroup.id == opsgroupid])

        
    def get_entities(self, enttype_id):
        result = []
        entities = DBSession.query(Entity).filter(Entity.type_id == enttype_id)
        for ent in entities:
            result.append(dict(entid=ent.entity_id, entname=ent.name))
        return result

    def get_user_status_map(self):
        try:
            result = []
            
            dic = {'Active':'Active','InActive':'InActive'}
            for key in dic.keys():
                result.append(dict(id=dic[key], value=key))

        except Exception as ex:
            print_traceback()
            LOGGER.error(str(ex).replace("'", ''))
            return ("{success: false,msg: '", str(ex).replace("'", ''), "'}")

        return dict(success='true', user_status=result)


    def get_user_role_map(self):
        try:
            result = []
            dic={'Operator':'Operator','User':'User'}
            for key in dic.keys():
                result.append(dict(id=dic[key], value=key))

        except Exception as ex:
            print_traceback()
            LOGGER.error(str(ex).replace("'", ''))
            return dict(success=False, msg=str(ex).replace("'", ''))

        return dict(success=True, user_role=result)

        
    def save_privilege_details(self, login, privilegeid, privilegename, opsgrups):
        dupPriv = None
        session = DBHelper().get_session()
        dupPriv = session.query(Privilege).filter(Privilege.name == privilegename).first()
        if dupPriv is None:
            result = []
            db = DBHelper()
            priv = Privilege()
            priv.name = privilegename
            priv.created_by = login
            priv.modified_by = login
            priv.created_date = datetime.now()
            if opsgrups != '':
                L = opsgrups.split(',')
                for i in L:
                    opsgroup = DBHelper().find_by_id(OperationGroup, int(i))
                    priv.opGroups.append(opsgroup)
            db.add(priv)
            return result
        result = 'False'
        return result
        return None

    def addopsgroup_toprivilege_det(self, privilegename, opsgroupnames):
        privilege = DBSession.query(Privilege).filter(Privilege.name == privilegename).first()

        if privilege!=None:
            listreject = []

            try:
                for opsname in opsgroupnames:
                    opsgroup = DBSession.query(OperationGroup).filter(OperationGroup.name == opsname).first()
                    if opsgroup != None:
                        privilege.opGroups.append(opsgroup)
                        continue

                    listreject.append(opsname)

                DBHelper().update(privilege)
                if listreject != []:
                    result += 'some operationgroups does not exists' + to_str(listreject)
                else:
                    result = 'The operationgroups are added '

            except Exception as ex:
                print_traceback()
                return dict(success=False, msg=to_str(ex))

            return dict(success=True, msg=result)

        result = 'The privilege ' + privilegename + ' does not exists'
        return dict(success=True, msg=result)
        return None

        
        
    def deleteopsgroup_fromprivilege_det(self, privilegename, opsgroupnames):
        result = ''
        privilege = DBSession.query(Privilege).filter(Privilege.name == privilegename).first()
        if privilege!=None:
            listreject = []
            try:
                for opsname in opsgroupnames:
                    opsgroup = DBSession.query(OperationGroup).filter(OperationGroup.name == opsname).first()
                    if opsgroup != None:
                        privilege.opGroups.remove(opsgroup)
                        continue

                    listreject.append(opsname)

                DBHelper().update(privilege)
                if listreject != []:
                    result += 'some operationgroups does not exists' + to_str(listreject)
                else:
                    result = 'The operationgroups are deleted '

            except Exception as ex:
                print_traceback()
                return dict(success=False, msg=to_str(ex))

            return dict(success=True, msg=result)

        result = 'The privilege ' + privilegename + ' does not exists'
        return dict(success=True, msg=result)
        return None

        
    def get_privileges(self):
        result = []
        privs = DBHelper().get_all(Privilege)
        for p in privs:
            pid = p.id
            sname = p.name
            i = 0
            for opgs in p.opGroups:
                pname = ''
                strgroup = ''
                desc = ''
                if i == 0:
                    pname = p.name
                i += 1
                strgroup = opgs.name
                desc = opgs.description
                result.append(dict(privilegeid=pid, privilegename=pname, opgroups=strgroup, desc=desc, searchName=sname))
        return result

    def get_privileges4opsg(self, type):
        result = []
        priv = DBSession().query(Privilege).filter(Privilege.type == type).all()
        for p in priv:
            privid = p.id
            privname = p.name
            result.append(dict(privid=privid, privname=privname))
        return result

    def get_privileges4opsg_two(self):
        result = []
        result.append(dict(privid='1', privname='FULL'))
        result.append(dict(privid='2', privname='OPERATOR'))
        result.append(dict(privid='3', privname='VIEW'))
        return result

    def edit_privilege_det(self, privid):
        result = []
        priv = Privilege()
        session = DBHelper().get_session()
        priv = session.query(Privilege).filter(Privilege.id == privid).first()
        result.append(dict(privilegeid=priv.id, privilegename=priv.name, createdby=priv.created_by, modifiedby=priv.modified_by, createddate=priv.created_date, modifieddate=priv.modified_date))
        return result

    def get_toopsgroups_map(self, privilegeid):
        result = []
        session = DBHelper().get_session()
        privilige = session.query(Privilege).filter(Privilege.id == privilegeid).first()
        opsgroups = privilige.opGroups
        for op in opsgroups:
            opsgrpid = op.id
            opsgrpname = op.name
            result.append(dict(opsgroupid=opsgrpid, opsgroupname=opsgrpname))
        return result

    def get_opsgroups_map(self, privid=None):
        result = []
        session = DBHelper().get_session()
        opsgroups = DBHelper().get_all(OperationGroup)
        privilige = session.query(Privilege).filter(Privilege.id == privid).first()
        for g in opsgroups:
            gid = g.id
            gname = g.name
            result.append(dict(opsgroupid=gid, opsgroupname=gname))
        if privid is None:
            return result
        for opsgrp in privilige.opGroups:
            i = 0
            for privilige in result:
                if opsgrp.id == privilige['opsgroupid']:
                    del result[i]
                    break
                i += 1
        return result

    def updatesave_privilege_details(self, login, privilegeid, privilegename, opsgrups):
        result = []
        priv = DBHelper().find_by_id(Privilege, privilegeid)
        priv.name = privilegename
        priv.modified_date = datetime.now()
        priv.modified_by = login
        for opsgroup in priv.opGroups:
            priv.opGroups.remove(opsgroup)
        opsgrups = opsgrups[0:-1]
        if opsgrups != '':
            L = opsgrups.split(',')
            for i in L:
                opsgroup = DBHelper().find_by_id(OperationGroup, int(i))
                priv.opGroups.append(opsgroup)
        DBHelper().update(priv)
        return result

        
        
    def delete_privilege(self, privilegeid):
        privilegeid = int(privilegeid)
        DBHelper().delete_all(Privilege, [], [Privilege.id == privilegeid])
        DBHelper().delete_all(RoleEntityPrivilege, [], [RoleEntityPrivilege.privilege_id == privilegeid])

    def get_roles(self, type, auth=None):
        result = []
        roles = DBSession.query(Role).filter(Role.type == type).all()
        for r in roles:
            rid = r.id
            rname = r.name
            if r.description is None:
                description = ''
            else:
                description = r.description
            result.append(dict(roleid=rid, rolename=rname, description=description))
        return result

    def add_role(self, login, rolename, roledesc, reps, type, is_cloudadmin, cli):
        role = Role()
        duprole = None
        session = DBHelper().get_session()
        duprole = session.query(Role).filter(Role.name == rolename).first()
        
        if duprole is None:
            result = []
            if cli != True:
                reps = json.loads(reps)
            role.name = rolename
            role.description = roledesc
            role.created_by = login
            role.modified_by = login
            role.created_date = datetime.now()
            role.type = type
            role.is_cloud_admin = is_cloudadmin == 'true'
            DBHelper().add(role)
            privs = DBHelper().get_all(Privilege)
            privileges = {}
            is_granular = tg.config.get(constants.GRANULAR_USER_MODEL)
            for priv in privs:
                privileges[priv.name] = priv

            for xx in reps['reps']:
                ent = DBHelper().filterby(Entity, [], [Entity.entity_id == xx['entityid']])

                if is_granular!='True':
                    types_list = [constants.DATA_CENTER, constants.IMAGE_STORE, constants.IMAGE_GROUP, constants.SERVER_POOL]
                    if type == constants.CLOUD:
                        types_list.extend([constants.VDC, constants.VDC_VM_FOLDER, constants.TMP_LIB, constants.CLOUD_TMPGRP])
                    if ent[0].type.name in types_list:
                        rep = RoleEntityPrivilege()
                        rep.role = role
                        rep.entity_id = xx['entityid']
                        rep.privilege = privileges[to_str(xx['privilegename'])]
                        DBHelper().add(rep)
                    
                    if ent[0].type.name in [constants.IMAGE_GROUP,constants.SERVER_POOL,constants.VDC,constants.VDC_VM_FOLDER,constants.CLOUD_TMPGRP]:
                        self.add_rep(role, ent[0].children, privileges[to_str(xx['privilegename'])])

                else:

                    rep = RoleEntityPrivilege()
                    rep.role = role
                    rep.entity_id = xx['entityid']
                    rep.privilege = privileges[to_str(xx['privilegename'])]
                    rep.propagate = to_str(xx['propagate'])=='true'
                    DBHelper().add(rep)

            return result

        raise Exception('Role with the Name ' + rolename + ' already exists')

        return None
        
        
    def get_roles_map(self, type):
        result = []
        roles = DBSession.query(Role).filter(Role.type == type).all()
        for r in roles:
            roleid = r.id
            rolename = r.name
            result.append(dict(roleid=roleid, rolename=rolename))
        return result

    def get_role_details(self, roleid):
        roleid = int(roleid)
        role = DBHelper().find_by_id(Role, roleid)
        if role.description is None:
            description = ''
        else:
            description = role.description
        return dict(id=role.id, name=role.name, description=description, is_cloudadmin=role.is_cloud_admin, createdby=role.created_by, modifiedby=role.modified_by, createddate=role.created_date, modifieddate=role.modified_date)



    def create_like_role(self, login, rolename, newrolename, description):
        db = DBHelper()
        newrole = DBSession.query(Role).filter(Role.name == newrolename).first()
        if newrole != None:
            return dict(success=False, msg='The role ' + newrolename + ' already exists')
        role = DBSession.query(Role).filter(Role.name == rolename).first()
        if description:
            desc = description
        else:
            desc = role.description
        newrole = Role()
        if role != None:
            newrole.name = newrolename
            newrole.description = desc
            newrole.type = role.type
            #newrole.groups = role.groups
            newrole.created_by = login
            newrole.modified_by = login
            newrole.created_date = datetime.now()
            db.add(newrole)
            reps = DBSession.query(RoleEntityPrivilege).filter(RoleEntityPrivilege.role_id == role.id).all()
            for rep in reps:
                rep1 = RoleEntityPrivilege()
                rep1.role = newrole
                rep1.entity_id = rep.entity_id
                rep1.privilege = rep.privilege
                rep1.propagate = rep.propagate
                db.add(rep1)
            return dict(success=True, msg='success')
        return dict(success=False, msg='The role ' + rolename + ' does not exists')

    def update_role(self, login, roleid, rolename, roledesc, reps, type, is_cloudadmin):
        roleid = int(roleid)
        reps = json.loads(reps)
        role = DBHelper().find_by_id(Role, roleid)
        role.name = rolename
        role.description = roledesc
        role.modified_by = login
        role.modified_date = datetime.now()
        role.is_cloud_admin = is_cloudadmin == 'true'
        DBHelper().add(role)
        privs = DBHelper().get_all(Privilege)
        privileges = {}
        is_granular = tg.config.get(constants.GRANULAR_USER_MODEL)
        for priv in privs:
            privileges[priv.name] = priv
        DBHelper().delete_all(RoleEntityPrivilege, [], [RoleEntityPrivilege.role_id == roleid])
        for xx in reps['reps']:
            ent = DBHelper().filterby(Entity, [], [Entity.entity_id == xx['entityid']])
            if is_granular != 'True':
                types_list = [constants.DATA_CENTER, constants.IMAGE_STORE, constants.IMAGE_GROUP, constants.SERVER_POOL]
                if type == constants.CLOUD:
                    types_list.extend([constants.VDC, constants.VDC_VM_FOLDER, constants.TMP_LIB, constants.CLOUD_TMPGRP])
            
                if ent[0].type.name in types_list:
                    rep = RoleEntityPrivilege()
                    rep.role = role
                    rep.entity_id = xx['entityid']
                    rep.privilege = privileges[to_str(xx['privilegename'])]
                    DBHelper().add(rep)
                    
                    if ent[0].type.name in [constants.IMAGE_GROUP,constants.SERVER_POOL,constants.VDC,constants.VDC_VM_FOLDER,constants.CLOUD_TMPGRP]:
                        self.add_rep(role, ent[0].children, privileges[to_str(xx['privilegename'])])

            else:

                rep = RoleEntityPrivilege()
                rep.role = role
                rep.entity_id = xx['entityid']
                rep.privilege = privileges[to_str(xx['privilegename'])]
                DBHelper().add(rep)

            
    def get_role(self, rolename):
        role = None
        role = DBSession.query(Role).filter(Role.name == rolename).first()
        return role

    def delete_role(self, roleid):
        roleid = int(roleid)
        role = DBSession.query(Role).filter(Role.id == roleid).first()
        if role is not None:
            if role.name in constants.DEFAULT_ROLES:
                raise Exception('Can not delete ' + role.name + ' role.')
            DBHelper().delete_all(RoleEntityPrivilege, [], [RoleEntityPrivilege.role_id == roleid])
            DBHelper().delete_all(Role, [], [Role.id == roleid])
        return None

    def get_role_rep(self, roleid):
        result = []
        is_granular_ui = self.is_granular_ui()
        filter = []
        if is_granular_ui != 'True':
            types = DBHelper().filterby(EntityType.id, [], [EntityType.name.in_([to_unicode(constants.MANAGED_NODE), to_unicode(constants.IMAGE), to_unicode(constants.DOMAIN), constants.CLOUD_VM, constants.CLOUD_TEMP, constants.VDC_VM_FOLDER, constants.CLOUD_TMPGRP, constants.TMP_LIB])])
            for type in types:
                filter.append(type.id)
        ents = DBHelper().filterby(Entity, [], [not_(Entity.type_id.in_(filter))])
        if roleid is None:
            for ent in ents:
                result_dict = {}
                result_dict['entityid'] = ent.entity_id
                result_dict['entityname'] = ent.name
                result_dict['entitytype'] = ent.type.display_name
                result_dict['privilegename'] = 'None'
                result_dict['propagate'] = False
                result.append(result_dict)
        else:
            roleid = int(roleid)
            reps = DBHelper().filterby(RoleEntityPrivilege, [], [RoleEntityPrivilege.role_id == roleid])
            reps_dict = {}
            for rep in reps:
                if rep.privilege is not None:
                    reps_dict[rep.entity_id] = rep.privilege.name
                    prop = False
                    if rep.propagate:
                        prop = rep.propagate
                    reps_dict[rep.entity_id + 'PROP'] = prop
            for ent in ents:
                if reps_dict.has_key(ent.entity_id):
                    result_dict = {}
                    result_dict['entityid'] = ent.entity_id
                    result_dict['entityname'] = ent.name
                    result_dict['entitytype'] = ent.type.display_name
                    result_dict['privilegename'] = reps_dict.get(ent.entity_id, 'None')
                    result_dict['propagate'] = reps_dict[ent.entity_id + 'PROP']
                    result.append(result_dict)
        return result

    def get_entitytype_role(self, type):
        result = []
        is_granular_ui = self.is_granular_ui()
        filter = not_(EntityType.name.in_([to_unicode(constants.EMAIL), to_unicode(constants.APPLIANCE)]))
        if is_granular_ui != 'True':
            filter = EntityType.name.in_([to_unicode(constants.DATA_CENTER), to_unicode(constants.SERVER_POOL), to_unicode(constants.IMAGE_STORE), to_unicode(constants.IMAGE_GROUP), to_unicode(constants.CLOUD_PROVIDER_FOLDER), constants.VDC_FOLDER, to_unicode(constants.VDC)])
        if type == constants.CLOUD:
            if is_granular_ui == 'True':
                filter = EntityType.name.in_([to_unicode(constants.VDC), constants.CLOUD_VM, constants.VDC_VM_FOLDER, constants.TMP_LIB, constants.CLOUD_TMPGRP])
            else:
                filter = EntityType.name.in_([to_unicode(constants.VDC)])
        if type == 'VDC_Cloud':
            filter = EntityType.name.in_([constants.VDC_VM_FOLDER, constants.TMP_LIB])
        if type == 'VDC_granular_Cloud':
            filter = EntityType.name.in_([constants.VDC_VM_FOLDER, constants.TMP_LIB])
        ent_types = DBSession.query(EntityType).filter(filter).all()
        for type in ent_types:
            result.append(dict(typeid=type.id, name=type.name, display=type.display_name))
        return result

    def is_granular_ui(self):
        is_granular_ui = tg.config.get(constants.GRANULAR_USER_MODEL)
        return is_granular_ui

    def get_entities_bytype(self, auth, type, parententityid):
        result = []
        (grnd_parent_name, parent_name) = ('', '')
        ents = []
        is_granular_ui = self.is_granular_ui()
        #from stackone.cloud.DbModel.TemplateProvider import TemplateProvider
        if parententityid is not None:
            parent_ent = DBSession.query(Entity).filter(Entity.entity_id == parententityid).first()

            if parent_ent is not None:
                if parent_ent.type.name == constants.VDC and is_granular_ui!='True':
                    child_ents = parent_ent.children

                    ents=[ent for ent in child_ents if ent.type.name == constants.TMP_LIB]
                    #aasdf = [a for a in [1,2,3] if a >= 2]
                else:
                    ents = parent_ent.children

                if len(ents) == 0:
                    return dict(success=False, msg='There are no child entities for ' + parent_ent.name)

            else:
                return dict(success=False, msg='There is no such entity ')
        else:
            ents = auth.get_entities(type)

        ent_type = DBSession.query(EntityType).filter(EntityType.name == type).first()
        display = type
        if ent_type is not None:
            display = ent_type.display_name
        if len(ents) > 0:
            for ent in ents:
                type = ent.type.name
                if type in [constants.DATA_CENTER, constants.IMAGE_STORE, constants.IMAGE_GROUP, constants.SERVER_POOL, constants.VDC_FOLDER, constants.CLOUD_PROVIDER_FOLDER]:
                    (grnd_parent_name, parent_name) = ('', '')
                elif type in [constants.IMAGE, constants.MANAGED_NODE]:
                    parentent = ent.parents[0]
                    parent_name = parentent.name
                elif type in [constants.DOMAIN]:
                    parentent = ent.parents[0]
                    grnd_parent = parentent.parents[0]
                    parent_name = parentent.name
                    grnd_parent_name = grnd_parent.name
                elif type in [constants.VDC]:
                    parentent = ent.parents[0]
                    parent_name = parentent.name
                elif type in [constants.CLOUD_VM]:
                    parentent = ent.parents[0]
                    parent_name = parentent.name
                elif type in [constants.TMP_LIB]:
                    parentent = ent.parents[0]
                    parent_name = parentent.name
                    grnd_parent = parentent.parents[0]
                    grnd_parent_name = grnd_parent.name
                elif type in [constants.CLOUD_TMPGRP]:
                    parentent = ent.parents[0]
                    parent_name = parentent.name
                    grnd_parent = parentent.parents[0]
                    grnd_parent_name = grnd_parent.name
                elif type in [constants.CLOUD_TEMP]:
                    parentent = ent.parents[0]
                    parent_name = parentent.name
                    grnd_parent = parentent.parents[0]
                    grnd_parent_name = grnd_parent.name
                elif type in [constants.CLOUD_PROVIDER]:
                    parentent = ent.parents[0]
                    parent_name = parentent.name
                result.append(dict(id=ent.entity_id, name=ent.name, parent=parent_name, grnd_parent=grnd_parent_name))
            return dict(success=True, rows=result)
        return dict(success=False, msg='There are no entities of type ' + display)


    def get_privilege(self, privilegename):
        prvlge = None
        prvlge = DBSession.query(Privilege).filter(Privilege.name == privilegename).first()
        return prvlge

    def assign_entity_privilege(self, rolename, entity_names, privilegename):
        try:
            role = self.get_role(rolename)
            privilege = self.get_privilege(privilegename)
            if role == None:
                return dict(success=False, msg='The role ' + rolename + ' does not exists')
            if privilege == None:
                return dict(success=False, msg='The privilege ' + privilegename + ' does not exists')
            is_granular = tg.config.get(constants.GRANULAR_USER_MODEL)
            unknown = []
            not_allowed = []
            for ent_name in entity_names:
                ent = self.get_entity(ent_name)
                if ent!=None:
                    if is_granular!='True':
                        if ent.type.name in [constants.DATA_CENTER,constants.IMAGE_STORE,constants.IMAGE_GROUP,constants.SERVER_POOL]:
                            DBHelper().delete_all(RoleEntityPrivilege, [], [RoleEntityPrivilege.role_id == role.id, RoleEntityPrivilege.entity_id == ent.entity_id])
                            rep = RoleEntityPrivilege()
                            rep.role = role
                            rep.entity = ent
                            rep.privilege = privilege
                            DBHelper().add(rep)

                            if ent.type.name in [constants.IMAGE_GROUP,constants.SERVER_POOL]:
                                self.add_rep(role, ent.children, privilege)
                        else:
                            not_allowed.append(ent_name)

                    else:
                        DBHelper().delete_all(RoleEntityPrivilege, [], [RoleEntityPrivilege.role_id == role.id, RoleEntityPrivilege.entity_id == ent.entity_id])
                        rep = RoleEntityPrivilege()
                        rep.role = role
                        rep.entity = ent
                        rep.privilege = privilege
                        DBHelper().add(rep)
                else:
                    unknown.append(ent_name)

            msg = 'Privilege assigned Successfully.'
            if len(unknown) > 0:
                msg += ' Following entities does not exist :' + to_str(unknown)
            if len(not_allowed) > 0:
                msg += ' Can not assign privilege to following entities :' + to_str(not_allowed)
            return dict(success=True, msg=msg)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex))

        return None


    def remove_entity_privilege(self, rolename, entity_names):
        try:
            role = self.get_role(rolename)
            if role == None:
                return dict(success=False, msg='The role ' + rolename + ' does not exists')
            is_granular = tg.config.get(constants.GRANULAR_USER_MODEL)
            unknown = []
            not_allowed = []
            for ent_name in entity_names:
                ent = self.get_entity(ent_name)
                
                if ent!=None:
                    if is_granular!='True':
                        if ent.type.name in [constants.DATA_CENTER,constants.IMAGE_STORE,constants.IMAGE_GROUP,constants.SERVER_POOL]:
                            DBHelper().delete_all(RoleEntityPrivilege, [], [RoleEntityPrivilege.role_id == role.id, RoleEntityPrivilege.entity_id == ent.entity_id])
                            if ent.type.name in [constants.IMAGE_GROUP,constants.SERVER_POOL]:
                                self.remove_rep(role, ent.children)
                        else:
                            not_allowed.append(ent_name)
                    else:
                        DBHelper().delete_all(RoleEntityPrivilege, [], [RoleEntityPrivilege.role_id == role.id, RoleEntityPrivilege.entity_id == ent.entity_id])

                else:
                    unknown.append(ent_name)

            msg = 'Privilege removed Successfully.'
            if len(unknown) > 0:
                msg += ' Following entities does not exist :' + to_str(unknown)
            if len(not_allowed) > 0:
                msg += ' Can not remove privilege of following entities :' + to_str(not_allowed)
            return dict(success=True, msg=msg)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex))

        return None


    def get_entity(self, ent_name):
        return DBSession.query(Entity).filter(Entity.name == ent_name).first()

    def add_rep(self, role, entities, privilege):
        for entity in entities:
            DBHelper().delete_all(RoleEntityPrivilege, [], [RoleEntityPrivilege.role_id == role.id, RoleEntityPrivilege.entity_id == entity.entity_id])
            rep = RoleEntityPrivilege()
            rep.role = role
            rep.entity = entity
            rep.privilege = privilege
            DBHelper().add(rep)
            if len(entity.children) > 0:
                self.add_rep(role, entity.children, privilege)
                continue

    def remove_rep(self, role, entities):
        for entity in entities:
            DBHelper().delete_all(RoleEntityPrivilege, [], [RoleEntityPrivilege.role_id == role.id, RoleEntityPrivilege.entity_id == entity.entity_id])
            if len(entity.children) > 0:
                self.remove_rep(role, entity.children)
                continue

    def get_operations(self, like=None):
        result = []
        filters = []
        if like != '' and like != None:
            filters.append(Operation.name.like(like))
        operations = DBHelper().filterby(Operation, [], filters)
        for op in operations:
            strname = ''
            opname = op.name
            desc = op.description
            ctxdisp = op.display
            opid = op.id
            for e in op.entityType:
                disp_name = ''
                if e.display_name is not None:
                    disp_name = e.display_name
                    strname += disp_name + ' ,'
                else:
                    strname += disp_name + ' ,'
            strname = strname[0:-1]
            result.append(dict(opname=opname, description=desc, cd=ctxdisp, enttype=strname, opid=opid))
        return result

    def save_oper_det(self, login, opname, descr, context_disp, entityid, dispname, icon):
        result = []
        dupOp = None
        operation = Operation()
        db = DBHelper()
        session = DBHelper().get_session()
        dupOp = session.query(Operation).filter(Operation.name == opname).first()
        if dupOp is None:
            operation.name = opname
            operation.description = descr
            operation.display_name = dispname
            operation.icon = icon
            operation.created_by = login
            operation.modified_by = login
            operation.created_date = datetime.now()
            if context_disp == 'true':
                operation.display = True
            else:
                operation.display = False
            L = entityid.split(',')
            for i in L:
                ent = session.query(EntityType).filter(EntityType.id == int(i)).first()
                operation.entityType.append(ent)
            db.add(operation)
            return result
        result = 'False'
        return result

    def edit_op_det(self, opid, enttype):
        result = []
        op = Operation()
        session = DBHelper().get_session()
        op = session.query(Operation).filter(Operation.id == opid).first()
        entitytype = enttype
        result.append(dict(opid=op.id, opname=op.name, desc=op.description, contextdisplay=op.display, enttype=entitytype, createdby=op.created_by, modifiedby=op.modified_by, createddate=op.created_date, modifieddate=op.modified_date, dispname=op.display_name, icon=op.icon))
        return result

    def updatesave_op_det(self, login, opid, opname, desc, entid, context_disp, dispname, icon):
        result = []
        op = Operation()
        db = DBHelper()
        session = DBHelper().get_session()
        op = session.query(Operation).filter(Operation.id == opid).first()
        op.name = opname
        op.description = desc
        op.modified_date = datetime.now()
        op.modified_by = login
        op.display_name = dispname
        op.icon = icon
        if context_disp == 'true':
            op.display = True
        else:
            op.display = False
        for i in op.entityType:
            op.entityType.remove(i)
        L = entid.split(',')
        if entid != '':
            for i in L:
                ent = session.query(EntityType).filter(EntityType.id == int(i)).first()
                op.entityType.append(ent)
        db.update(op)
        return result

    def get_operation(self, name):
        operation = None
        operation = DBSession.query(Operation).filter(Operation.name == name).first()
        return operation

    def delete_operation(self, opid):
        opid = int(opid)
        DBHelper().delete_all(Operation, [], [Operation.id == opid])

    def get_entitytype_map(self, opid=None):
        result = []
        session = DBHelper().get_session()
        enty = DBHelper().get_all(EntityType)
        operation = session.query(Operation).filter(Operation.id == opid).first()
        for e in enty:
            eid = e.id
            ename = e.display_name
            result.append(dict(entid=eid, entname=ename))
        if opid is None:
            return result
        for ent in operation.entityType:
            i = 0
            for enttype in result:
                if ent.id == enttype['entid']:
                    del result[i]
                    break
                i += 1
        return result

    def get_toentitytype_map(self, opid):
        result = []
        op = DBSession.query(Operation).filter(Operation.id == opid).first()
        ents = op.entityType
        for e in ents:
            oid = e.id
            oname = e.display_name
            result.append(dict(entid=oid, entname=oname))
        return result

    def get_enttype(self):
        result = []
        enttype = DBHelper().get_all(EntityType)
        for e in enttype:
            ent_id = e.id
            ent_name = e.name
            disp_name = e.display_name
            result.append(dict(entid=ent_id, entname=ent_name, dispname=disp_name))
        return result

    def get_enttype_for_chart(self, user=None):
        result = []
        enttype = DBHelper().get_all(EntityType)
        for e in enttype:
            if user.is_cloud() and user:

                if e.name in [constants.CLOUD_VM,constants.VDC]:
                    ent_id = e.id
                    ent_name = e.name
                    disp_name = e.display_name
                    result.append(dict(entid=ent_id, entname=ent_name, dispname=disp_name))

                continue

            if e.name in [constants.DATA_CENTER, constants.SERVER_POOL, constants.MANAGED_NODE, constants.DOMAIN, constants.CLOUD_VM, constants.VDC]:
                ent_id = e.id
                ent_name = e.name
                disp_name = e.display_name
                result.append(dict(entid=ent_id, entname=ent_name, dispname=disp_name))
                continue

        return result


    def save_enttype_details(self, login, enttypename, dispname):
        dupEnt = None
        db = DBHelper()
        session = DBHelper().get_session()
        dupEnt = session.query(EntityType).filter(EntityType.name == enttypename).first()
        if dupEnt is None:
            result = []
            ent = EntityType()
            ent.name = enttypename
            ent.display_name = dispname
            ent.created_by = login
            ent.created_date = datetime.now()
            ent.modified_by = login
            db.add(ent)
            return result
            result = 'False'
        return result
        return None

    def edit_enttype_details(self, enttypeid):
        result = []
        session = DBHelper().get_session()
        ent = session.query(EntityType).filter(EntityType.id == enttypeid).first()
        enttypeid = ent.id
        entname = ent.name
        entdisp = ent.display_name
        result.append(dict(enttypeid=enttypeid, entname=entname, entdisp=entdisp, createdby=ent.created_by, modifiedby=ent.modified_by, createddate=ent.created_date, modifieddate=ent.modified_date))
        return result

    def updatesave_enttype_details(self, login, enttypeid, enttypename, dispname):
        result = []
        ent = EntityType()
        db = DBHelper()
        session = DBHelper().get_session()
        ent = session.query(EntityType).filter(EntityType.id == enttypeid).first()
        ent.name = enttypename
        ent.display_name = dispname
        ent.modified_by = login
        ent.modified_date = datetime.now()
        db.update(ent)
        return result

    def delete_enttype(self, enttypeid):
        enttypeid = int(enttypeid)

    def get_child_entites(self, auth, ent):
        ent_ids = []
        children = auth.get_child_entities(ent)
        for child in children:
            ent_ids.append(child.entity_id)
            ent_ids.extend(self.get_child_entites(auth, child))
        return ent_ids

    def get_tasks(self, auth, cloud=False):
        result = []
        lim = tg.config.get(constants.TaskPaneLimit)
        ago = datetime.now() + timedelta(days=-long(lim))
        limit = 200
        try:
            limit = int(tg.config.get(constants.task_panel_row_limit, '200'))
        except Exception as e:
            print 'Exception: ',
            print e
        entity_ids = []
        if cloud:
            vdcs = auth.get_entities(constants.VDC)
            for vdc in vdcs:
                entity_ids.append(vdc.entity_id)
                entity_ids.extend(self.get_child_entites(auth, vdc))

        LOGGER.debug('get_tasks query start : ' + to_str(datetime.now()))
        tasks = DBSession.query(Task.task_id, Task.name, Task.user_name, Task.entity_name, Task.cancellable, TaskResult.timestamp, TaskResult.endtime, TaskResult.status, TaskResult.results, Task.entity_type, Task.short_desc).join(TaskResult).filter(or_(and_(Task.repeating == True, TaskResult.visible == True), and_(Task.repeating == False, Task.entity_id != None))).filter(Task.submitted_on >= ago)
        if entity_ids:
            tasks = tasks.filter(Task.entity_id.in_(entity_ids))
        tasks = tasks.order_by(TaskResult.timestamp.desc()).limit(limit).all()
        LOGGER.debug('get_tasks query end   : ' + to_str(datetime.now()))
        result = self.format_task_result_details(tasks)
        return result

    def get_task_details(self, task_ids):
        result = []
        LOGGER.debug('get_task_details query start : ' + to_str(datetime.now()))
        task = DBSession.query(Task).filter(Task.task_id.in_(task_ids)).options(eagerload('result')).all()
        LOGGER.debug('get_task_details query end   : ' + to_str(datetime.now()))
        result = self.format_task_details(task)
        return result

    def get_details_task(self, task_id):
        task = DBSession.query(Task).filter(Task.task_id == task_id).first()
        if task != None:
            tname = task.name
            status = 'Not started'
            starttime = ''
            endtime = ''
            msg = ''
            entity = task.entity_name
            username = task.user_name
            for trs in task.result:
                status = trs.status
                if task.is_finished():
                    tend = trs.endtime
                    endtime = to_str(tend)
                    endtime = endtime.split('.')
                    endtime = endtime[0]
                    msg = trs.results
                status = Task.TASK_STATUS[trs.status]
                ts = trs.timestamp
                starttime = to_str(ts)
                starttime = starttime.split('.')
                starttime = starttime[0]
            result = dict(taskname=tname, status=status, msg=msg, start=starttime, end=endtime, entity=entity, user=username)
        else:
            raise Exception('The task with taskid ' + task_id + ' doest not exists.')
        return result

    def getNotifications(self, type, ids, user, entType=None):
        date2 = datetime.now()
        date1 = date2 + timedelta(days=-1)
        tasks = []
        notify_limit = 200
        try:
            notify_limit = int(tg.config.get(constants.NOTIFICATION_ROW_LIMIT))
        except Exception as e:
            print 'Exception: ',
            print e
        x = Task
        if type == 'COUNT':
            x = func.count(Task.task_id)
        q = DBSession.query(x).join(TaskResult).filter(TaskResult.status == Task.FAILED).filter(Task.submitted_on > date1).filter(Task.submitted_on < date2)
        if not isinstance(ids, list):
            ids = ids.split(',')
        q = q.filter(Task.entity_id.in_(ids))
        if type == 'DETAILS':
            q = q.options(eagerload('result'))
        tasks = q.order_by(Task.submitted_on.desc()).limit(notify_limit).all()
        if type == 'COUNT':
            return tasks[0][0]
        if type == 'DETAILS':
            result = []
            result = self.format_task_details(tasks, format_type='Notification')
            return result
        # if entType == constants.DATA_CENTER:
            # tasks = DBSession.query(Task).join(TaskResult).filter(TaskResult.status == Task.FAILED).filter(Task.submitted_on > date1).filter(Task.submitted_on < date2).filter(Task.user_name == user).options(eagerload('result')).order_by(Task.submitted_on.desc()).limit(notify_limit).all()
        # else:
            # if not isinstance(ids, list):
                # ids = ids.split(',')
            # tasks = DBSession.query(Task).join(TaskResult).filter(TaskResult.status == Task.FAILED).filter(Task.entity_id.in_(ids)).filter(Task.submitted_on > date1).filter(Task.submitted_on < date2).filter(Task.user_name == user).options(eagerload('result')).order_by(Task.submitted_on.desc()).limit(notify_limit).all()
        # if type == 'COUNT':
            # return len(self.format_task_details(tasks, format_type='Notification'))
        # if type == 'DETAILS':
            # result = []
            # result = self.format_task_details(tasks, format_type='Notification')
            # return result

    def getSystemTasks(self, type, user):
        date2 = datetime.now()
        date1 = date2 + timedelta(days=-1)
        if type == 'COUNT':
            total = 0
            task = DBSession.query(Task).filter(Task.entity_id == None).filter(Task.submitted_on > date1).filter(Task.submitted_on < date2).all()
            for t in task:
                if t.is_failed():
                    total += 1
                    continue
            t.is_failed()
            return total
        if type == 'DETAILS':
            result = []
            task = DBSession.query(Task).filter(Task.entity_id == None).filter(Task.submitted_on > date1).filter(Task.submitted_on < date2).order_by(Task.submitted_on.desc()).all()
            for t in task:
                desc_tuple = t.get_short_desc()
                if desc_tuple is not None:
                    short_desc = desc_tuple
                    tname = _(short_desc) % short_desc_params
                else:
                    tname = t.name
                username = t.user_name
                startime = ''
                endtime = ''
                for tr in t.result:
                    status = Task.TASK_STATUS[tr.status]
                    ts = tr.timestamp
                    startime = to_str(ts)
                    startime = startime.split('.')
                    startime = startime[0]
                    if t.is_failed():
                        t.is_failed()
                        err = tr.results
                        tend = tr.endtime
                        endtime = to_str(tend)
                        endtime = endtime.split('.')
                        endtime = endtime[0]
                        result.append(dict(tname=tname, status=status, st=startime, errmsg=err, user=username))
                        continue
                t.is_failed()
            return result
        return None

    def format_task_details(self, tasks, format_type=None):
        result = []
        ent_type_txt_map = self.get_entity_type_id_text_map()
        LOGGER.debug('start format_task_details : ' + to_str(datetime.now()))
        for t in tasks:
            tid = t.task_id
            task_name = t.name
            if t.short_desc is not None:
                task_name = t.short_desc
            username = t.user_name
            entityName = t.entity_name
            entity_type = ent_type_txt_map.get(to_str(t.entity_type), '')
            startime = ''
            endtime = ''
            err = ''
            for tr in t.result:
                if t.is_finished():
                    endtime = convert_to_CMS_TZ(tr.endtime)
                    err = tr.results
                status = Task.TASK_STATUS[tr.status]
                startime = convert_to_CMS_TZ(tr.timestamp)

                if format_type in ('Notification',):
                    if tr.status==Task.FAILED:
                        result.append(dict(taskid=tid, entname=entityName, enttype=entity_type, name=task_name, username=username, status=status, errmsg=err, timestamp=startime, cancellable=t.is_cancellable(), endtime=endtime))
                    continue
                result.append(dict(taskid=tid, entname=entityName, enttype=entity_type, name=task_name, username=username, status=status, errmsg=err, timestamp=startime, cancellable=t.is_cancellable(), endtime=endtime))
        LOGGER.debug('end   format_task_details : ' + to_str(datetime.now()))
        return result


    def get_entity_type_id_text_map(self):
        map = {}
        ent_types = DBSession.query(EntityType).all()
        for type in ent_types:
            map[to_str(type.id)] = type.display_name
        return map

    def format_task_result_details(self, task_results):
        #lbz
        result = []
        ent_type_txt_map = self.get_entity_type_id_text_map()
        LOGGER.debug('start format_task_result_details : ' + to_str(datetime.now()))
        for tpl in task_results:
            tid = tpl.task_id
            task_name = tpl.name
            username = tpl.user_name
            entityName = tpl.entity_name
            cancellable = tpl.cancellable
            startime = tpl.timestamp
            endtime = ''
            stat = tpl.status
            enttype = ent_type_txt_map.get(to_str(tpl.entity_type), '')
            short_desc = tpl.short_desc
            if short_desc:
                task_name = short_desc
            err = ''
            if stat in [Task.FAILED, Task.SUCCEEDED, Task.CANCELED]:
                endtime = convert_to_CMS_TZ(tpl.endtime)
                err = tpl.results
            status = Task.TASK_STATUS[stat]
            startime = convert_to_CMS_TZ(startime)
            result.append(dict(taskid=tid, entname=entityName, enttype=enttype, name=task_name, username=username, status=status, errmsg=err, timestamp=startime, cancellable=cancellable, endtime=endtime))
        LOGGER.debug('end   format_task_result_details : ' + to_str(datetime.now()))
        return result

    def cancel_task(self, auth, task_id):
        try:
            tk = DBSession.query(Task).filter(Task.task_id == task_id).first()
            
            if tk:
                ad_role = constants.DEFAULT_ROLES[0]
                r = DBHelper().find_by_name(Role, to_unicode(ad_role))
                if auth.is_admin_role() == False and auth.user_name != tk.user_name:
                    return dict(success=False, msg='You can not cancel the task:' + tk.name + ' .')

                if tk.is_cancellable()==True:
                    if tk.get_running_instance() is None:
                        return dict(success=False, msg='Task ' + tk.name + ' is not running.')
                
                    if tk.is_cancel_requested()==False:
                        from stackone.viewModel.TaskCreator import TaskCreator
                        TaskCreator().cancel_task(auth, task_id)
                        result = dict(success=True, taskname=tk.name, msg='Cancel requested for Task ' + tk.name + ' .')
                    else:
                        result = dict(success=False, taskname=tk.name, msg='Task ' + tk.name + ' cancellation is already requested.')
                else:
                    result = dict(success=False, msg='Task ' + tk.name + ' is not cancellable.')

            else:
                result = dict(success=False, msg='Task with id :' + str(task_id) + ' does not exist.')

            return result

        except Exception as e:
            traceback.print_exc()
            return dict(success=False, msg=to_str(e))

        return None


    def cancel_backup(self, auth, policy_name):
        try:
            from stackone.model.Backup import SPBackupConfig
            configobj = DBSession.query(SPBackupConfig).filter(SPBackupConfig.name == policy_name).first()
            if configobj:
                task_id = configobj.task_id
                return self.cancel_task(auth, task_id)

            return dict(success=False, msg='Backup policy with the name ' + policy_name + ' does not exist.')

        except Exception as e:
            traceback.print_exc()
            return dict(success=False, msg=to_str(e))
            
            
    def get_deployment_info(self):
        infolist = []
        try:
            depl = DBSession.query(Deployment).first()
            if depl:
                infolist.append(dict(name='Max Vitual Machines', value=depl.max_vm))
                infolist.append(dict(name='Max Servers', value=depl.max_server))
                infolist.append(dict(name='Max Server Pools', value=depl.max_sp))
                infolist.append(dict(name='Max Templates', value=depl.max_template))
                infolist.append(dict(name='Max Template Groups', value=depl.max_tg))
                return infolist
            depl
            raise Exception('Deployment Information is not set')
        except Exception as e:
            traceback.print_exc()
            raise e

    def lisence_info(self):
        return None



