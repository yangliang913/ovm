import pylons
from stackone.model import DBSession
from stackone.model import *
from stackone.model.DBHelper import DBHelper
from stackone.model.Authorization import AuthorizationService
from stackone.model.UpdateManager import UIUpdateManager, AppUpdateManager
from tg import url, request, session
from stackone.model.NodeCache import NodeCache
from stackone.model.PlatformType import PlatformType
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
from stackone.viewModel.NodeService import NodeService
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.viewModel.Userinfo import Userinfo
from stackone.viewModel.EmailService import EmailService
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
from stackone.model.LicenseManager import get_edition, rem_days_to_exp, get_version, get_edition_string, get_sub_edition_string
from stackone.model.TopCache import TopCache
##from stackone.cloud.core.model.CloudProviderManager import CloudProviderManager
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
LOGGER = logging.getLogger('stackone.controllers')
from stackone.controllers.ControllerBase import ControllerBase
class ControllerImpl(ControllerBase):
    node_service = NodeService()
    user_info = Userinfo()
    tc = TaskCreator()
    email_service = EmailService()
    def login(self, came_from=url('/')):
        if session.get('userid') is None and request.identity is not None:
            self.redirect_to(url('/user_logout'))
        return dict(page='login', version=constants._version, came_from=came_from)


    def user_login(self, args):
        try:
            username = args.get('login')
            password = args.get('password')

            try:
                ldap_user = args.get('ldap_user', 'False')
                if ldap_user == 'on':
                    ldap_user = 'True'
                ldap_user = eval(ldap_user)

            except Exception as e:
                print 'Exception: ',e
                ldap_user = False

            if ldap_user:
                from stackone.controllers.stackoneLDAPAuthenticator import stackoneLDAPAuthenticator
                ldap_auth = stackoneLDAPAuthenticator()
                ldap_sts = ldap_auth.validate_password(username, password)
                if ldap_sts['success'] == False:
                    msg = ldap_sts['msg']
                    LOGGER.info(msg)
                    return dict(success=False, user=None, msg=msg)

                return dict(success=True, user=username, group=ldap_sts['group'], ldap_user=ldap_user, user_details=ldap_sts['user_details'])

            user = DBSession.query(User).filter(User.user_name == username).first()

            if user:
                if user.status != True:
                    msg = 'User: ' + username + ' is not Active.'
                    LOGGER.info(msg)
                    return dict(success=False, user=None, msg=msg)

                username = user.user_name
                sqa_sts = user.validate_password(password)
                if not sqa_sts:
                    msg = 'Invalid password provided for CMS authentication.'
                    LOGGER.info(msg)
                    return dict(success=False, user=None, msg=msg)

            else:
                msg = 'Invalid username provided for CMS authentication.'
                LOGGER.info(msg)
                return dict(success=False, user=None, msg=msg)

            return dict(success=True, user=username)

        except Exception as e:
            print 'Exception',e
            LOGGER.error(e)
            return dict(success=False, user=None, msg=str(e))


    #sam 1024
    def post_login(self, userid, group, ldap_user, user_details, came_from=url('/')):
        result = ''
        if not userid:
            result = "{success:false,msg:'session expired'}"
            return result

        auth = AuthorizationService()
        auth.user_name = userid
        r = DBHelper().find_by_name(Role, to_unicode('admin'))
        session['cloud_only'] = False

        if ldap_user:
            if not len(group):
                result = "{success:false,msg:'User does not belong to any group in LDAP'}"
                return result

            #len(group)
            grps=Group.by_group_names(group)
            if not grps:
                result = "{success:false,msg:'None of the LDAP group (s) " + str(group).replace("'", '') + " defined in stackone'}"
                return result

            auth.groups = grps
            session['user_firstname'] = userid
            session['group_names'] = group
            session['is_cloud_admin'] = auth.is_admin_role()
            is_admin = auth.is_admin_role()
            from stackone.model.LDAPManager import LDAPManager
            auth.email_address = LDAPManager().get_email_address(user_details)

        else:
            u = User.by_user_name(to_unicode(userid))
            auth.user = u
            auth.groups = u.groups
            session['user_firstname'] = u.firstname

            session['group_names']=[g.group_name for g in u.groups]

            is_admin=u.has_role(r)
            auth.email_address=u.email_address
            session['is_cloud_admin']=u.has_cloudadmin_role()
            dcs=auth.get_entities(constants.DATA_CENTER)
            if len(dcs) == 0L:
                session['cloud_only']=True

        session['username']=userid
        session['has_adv_priv']=tg.config.get(constants.ADVANCED_PRIVILEGES)
        session['granular_ui']=self.user_info.is_granular_ui()
        session['PAGEREFRESHINTERVAL']=tg.config.get(constants.PAGEREFRESHINTERVAL)
        session['TASKPANEREFRESH']=tg.config.get(constants.TASKPANEREFRESH)
        session['userid']=userid
        session['auth']=auth
        session['rem_days']=''
        try:
            session['rem_days']=rem_days_to_exp()
        except Exception as e:
            print 'Exception: ',e

        session['is_admin']=is_admin
        session['version']=constants._version
        #session['edition']=get_edition()+'_'+constants._version
        session['edition']='3.2.1.5'+'_'+constants._version
        #session['has_cloud']=stackone.model.LicenseManager.has_cloud_license()
        session['has_cloud'] = 0 
        #session['edition_string']= get_edition_string
        session['edition_string']= 'stackone Enterprise'
        #session['sub_edition_string']=get_sub_edition_string
        session['sub_edition_string']='Trial Edition'
        session.save()
        TopCache().delete_usercache(auth)
        result='{success:true}'
        return result


    def post_logout(self, came_from=url('/')):
        try:
            if session.get('username'):
                UIUpdateManager().del_user_updated_entities(session['username'], session['group_names'])
                UIUpdateManager().del_user_updated_tasks(session['username'])
                TopCache().delete_usercache(session.get('auth'))

        except Exception as e:
            print_traceback()
            LOGGER.error(to_str(e))

        session.delete()

    #sam 1024
    def index(self):
        try:
            self.authenticate()

        except Exception as e:
            self.redirect_to(url('/login'))

        return dict(pag='index', user_name=session['username'], has_adv_priv=session['has_adv_priv'], granular_ui=session['granular_ui'], is_admin=session['is_admin'], is_cloud_admin=session['is_cloud_admin'], user_firstname=session['user_firstname'], version=session['version'], edition=session['edition'], has_cloud=session['has_cloud'], rem_days=session['rem_days'], edition_string=session['edition_string'], sub_edition_string=session['sub_edition_string'], TASKPANEREFRESH=session[constants.TASKPANEREFRESH], page_refresh_interval=session[constants.PAGEREFRESHINTERVAL])


    def has_admin_role(self):
        try:
            self.authenticate()
            return dict(success=True, result=session['is_admin'])

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))


    def get_app_updates(self):
        self.authenticate()
        try:

            updates = []
            userid = session['userid']
            if session['is_admin'] == True:
                updates = AppUpdateManager().check_user_updates(userid)
            return dict(success=True, updates=updates)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))


    def get_nav_nodes(self):
        result = []

        try:
            nav_nodes = self.node_service.get_nav_nodes(session['auth'])
            cloudnav_nodes = self.node_service.get_cloudnav_nodes(session['auth'])
            result.extend(nav_nodes)
            result.extend(cloudnav_nodes)
            return dict(success=True, nodes=result)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))


    def get_cloudnav_nodes(self):
        result = []

        try:
            if stackone.model.LicenseManager.is_cloud_license_violated():
                return []

            result = self.node_service.get_cloudnav_nodes(session['auth'])
            return dict(success=True, nodes=result)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))


    def get_used_ports_info(self):
        try:
            nc = NodeCache().get_cache()
            print nc
            result = []

            for n,c in nc.iteritems():
                res = "\n\n Server : '%s'" % n

                for p,d in c['ports'].iteritems():
                    res += "\n\t Port : '%s' , Time : '%s'" % (p, d)

                result.append(res)

            return highlight('\n'.join(result), PythonLexer(), HtmlFormatter(full=False, noclasses=True))

        except Exception as ex:
            print_traceback()
            return '<html>Error getting Ports information.</html>'


    def get_vnc_info(self, node_id, dom_id):
        try:
            self.authenticate()
            host = pylons.request.headers['Host']
            if host.find(':') != -1L:
                address, port = host.split(':')
            else:
                address = host

            result = self.node_service.get_vnc_info(session['auth'], node_id, dom_id, address)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        return dict(success=True, vnc=result)


    def get_ssh_info(self, node_id, client_platform):
        result = []
        try:
            self.authenticate()
            host = pylons.request.headers['Host']
            if host.find(':') != -1L:
                address = host.split(':')
            else:
                address = host
            result = self.node_service.get_ssh_info(session['auth'], node_id, address, client_platform)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))

        return dict(success=True, vnc=result)


    def get_platforms(self, **result):
        try:
            self.authenticate()
            result = self.node_service.get_platforms()

        except Exception as ex:
            print_traceback()
            raise ex

        return result


    def get_provider_types(self, _dc=None):
        try:
            self.authenticate()
            result = self.node_service.get_provider_types()
        except Exception as ex:
            print_traceback()
            raise ex

        return result


    def get_cp(self, _dc=None):
        try:
            self.authenticate()
            result = self.node_service.get_cp()

        except Exception as ex:
            print_traceback()
            raise ex

        return result


    def get_context_menu_items(self, node_id, node_type, _dc=None, menu_combo=None):
        try:
            self.authenticate()
            result = self.getUserOps(node_id, node_type, menu_combo)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        return dict(success=True, rows=result)


    def getUserOps(self, ent_id, nodeType=None, menu_combo=None, cp_type=None):
        result = []
        ent = session['auth'].get_entity(ent_id, nodeType)
        vcenter_type = False
        if ent.type.name == 'DOMAIN':
            externel_manager_id = ent.get_external_manager_id()
            if externel_manager_id:
                vcenter_type = True
        if ent is None:
            return result
        ops = session['auth'].get_ops(ent)
        if cp_type and cp_type != 'ALL' and cp_type != 'undefined':
            if stackone.model.LicenseManager.is_cloud_license_violated():
                raise Exception(stackone.model.LicenseManager.LICENSE_VIOLATED_MSG)
            ops = CloudProviderManager().filter_cp_ops(cp_type, ops)
        platform = self.node_service.get_platform(session['auth'], ent_id, nodeType)
        if ent.type.name == constants.SERVER_POOL:
            spl_ltfrms = [constants.VMWARE, constants.VCENTER]
            try:
                spl_ltfrms = eval(tg.config.get('SPECIAL_PLATFORMS'))
            except Exception as e:
                print 'Exception: ',
                print e
            if platform not in spl_ltfrms:
                vmw_sp_ids = ServerGroup.get_spl_pltfrms_sp()
                if ent_id in vmw_sp_ids:
                    platform = constants.VMWARE
        if platform:
            ops = PlatformType.filter_ops(platform, ops)
        for o in ops:
            if o.display == True:
                result.append(dict(value=o.display_id, text=o.display_name, id=o.id, icon=o.icon))
                if vcenter_type == True:
                    op = DBSession.query(Operation).filter(Operation.name == 'CREATE_IMAGE_FROM_VM').first()
                    result.append(dict(value=op.display_id, text=op.display_name, id=op.id, icon=op.icon))
            if menu_combo != 'True' and o.has_separator == True:
                result.append(dict(name='--'))
        return result
        



    def get_tasks(self, _dc=None):
        try:
            self.authenticate()
            result = None
            result = self.user_info.get_tasks(session['auth'], session['cloud_only'])

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        return dict(success=True, rows=result)


    def getNotifications(self, type, list, user, entType=None, _dc=None):
        try:
            self.authenticate()
            result = None
            result = self.user_info.getNotifications(type, list, user, entType)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))
        return dict(success=True, rows=result)


    def getSystemTasks(self, type, user, _dc=None):
        try:
            self.authenticate()
            result = None
            result = self.user_info.getSystemTasks(type, user)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

        return dict(success=True, rows=result)


    def get_failed_tasks(self, _dc=None):
        try:
            self.authenticate()
            result = None
            result=self.user_info.get_failed_tasks(session['userid'])
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))
        return dict(success=True,rows=result)


    def save_email_setup_details(self, desc, servername, port, useremail, password, secure, ** kw):
        try:
            result = None
            self.authenticate()
            result = self.email_service.save_email_setup_details( desc, servername, port, useremail, password, secure )
            return  result
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))


    def update_email_setup_details(self, desc, servername, port, useremail, password, secure, ** kw):
        result = None
        self.authenticate()
        result = self.email_service.update_email_setup_details( desc, servername, port, useremail, password, secure)
        return  result

    def send_test_email(self, desc, servername, port, useremail, password, secure, ** kw):   
        try:
            self.authenticate()
            msgreceived = self.email_service.send_test_email(desc, servername, port, useremail, password, secure)
            return msgreceived
        except Exception, ex:
            print_traceback()
            raise ex
#            return dict(success=False,msg=to_str(ex).replace("'",""))

    def get_emailsetupinfo(self,_dc=None):
        try:
            self.authenticate()
            result = None
            result=self.email_service.get_emailsetupinfo()
        except Exception, ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'",""))            
        return dict(success=True,rows=result)


    def delete_emailrecord(self,emailsetup_id):
        try:
            self.authenticate()
            self.email_service.delete_emailrecord(emailsetup_id)
            return {'success':True, 'msg':'Email Record Deleted.'}
        except Exception, ex:
            print_traceback()
            return {'success':False, 'msg':to_str(ex).replace("'", "")}

    def get_emailsetup_details(self,emailsetup_id):
        try:
            result = None
            self.authenticate()
            result = self.email_service.get_emailsetup_details(emailsetup_id)
        except Exception, ex:
            print_traceback()
            return {'success':False, 'msg':to_str(ex).replace("'", "")}
        return {'success':True, 'emailsetup_details':result}


    def sync_defn(self, server_ids, def_id, defType, site_id=None, group_id=None):
        self.authenticate()

        try:
            self.tc.sync_defn_task(session['auth'], server_ids, def_id, site_id, group_id, defType)
        except Exception as ex:
            print_traceback()
            err_desc = to_str(ex).replace("'", '')
            err_desc = err_desc.strip()
            LOGGER.error(err_desc)
            return "{success: false,msg: '" + err_desc + "'}"
        return "{success: true,msg: 'Task submitted.'}"


    def server_sync(self, node_id, def_type, sync_forcefully=False):
        self.authenticate()

        try:
            self.tc.server_sync_task(session['auth'], node_id, def_type, sync_forcefully)

        except Exception as ex:
            print_traceback()
            return "{success: false,msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"
        return "{success: true,msg: 'Task submitted.'}"


    def sync_all(self, def_type, site_id=None, group_id=None):
        self.authenticate()

        try:
            self.tc.sync_all_task(session['auth'], site_id, group_id, def_type)

        except Exception as ex:
            print_traceback()
            return "{success: false,msg:'" + to_str(ex).replace("'", '').replace('\n', '') + "'}"

        return "{success: true,msg: 'Task submitted.'}"


    def get_entityid(self, name, type):
        try:
            ent = Entity.find_by_name(name, type)
            if ent is not None:
                result = ent.entity_id
                return result

            return {'success': False,'msg': 'The Entity '+name+' is not found'}

        except Exception as ex:
            print_traceback()
            return 'msg'

        return None


    def get_details_task(self, task_id):
        self.authenticate()
        result = self.user_info.get_details_task(task_id)
        return result

    def cancel_task(self, task_id):
        self.authenticate()
        result = self.user_info.cancel_task(session['auth'], task_id)
        return result

    def cancel_backup(self, policy_name):
        self.authenticate()
        result = self.user_info.cancel_backup(session['auth'], policy_name)
        return result

    def get_deployment_info(self):
        self.authenticate()
        result = self.user_info.get_deployment_info()
        return result

    def lisence_info(self):
        self.authenticate()
        result = self.user_info.lisence_info()
        return result

    def check_license_expire(self, mode=None):
        self.authenticate()
        if stackone.model.LicenseManager.is_violated():
            return {'success':True,'msg':stackone.model.LicenseManager.LICENSE_VIOLATED_MSG,'mode':'VIOLATION'}
        exp_days = stackone.model.LicenseManager.LICENSE_EXPIRE_DAYS

        if exp_days is not None and mode is None:
            if exp_days == 0L:
                message = 'stackone License will expire Today.'
            else:
                message = 'stackone License will expire in %s day(s).' % str(exp_days)
            return {'success':True,'msg':message,'mode':'WARNING'}

        return {'success':True,'msg':'','mode':'SUCCESS'}

        



