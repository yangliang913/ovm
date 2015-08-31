import tg
import logging
from stackone.core.utils.utils import to_unicode, to_str, get_ldap_module
LOGGER = logging.getLogger('stackone.model')
from stackone.model.LDAPGroupManager import LDAP_Groups_Dict
from pprint import pprint
import traceback
class LDAPInvalidObjectClass(Exception):
    pass

class LDAPManager(object):
    _LDAPManager__instance = None
    def __new__(cls, *args, **kwargs):
        if cls._LDAPManager__instance is not None:
            return cls._LDAPManager__instance
        cls._LDAPManager__instance = object.__new__(cls, *args, **kwargs)
        return cls._LDAPManager__instance

    def __init__(self):
        self.ldap = get_ldap_module()
        get = tg.config.get
        try:
            self.trace_level = int(get(ldap_trace_level , 0))
        except Exception,ex:
            self.trace_level = 0
            
        self.tls_cacertfile = get('ldap_tls_cacertfile','/etc/ssl/certs/cacert.pem')
        try:
            self.start_tls = int(get('ldap_start_tls',0))
        except Exception,ex:
            self.start_tls = 0
        try:
            self.network_timeout = int(get('ldap_network_timeout',60))   
        except Exception,ex:
            self.network_timeout = 60   
        self.host = get('ldap_host', '127.0.0.1')
        self.port = get('ldap_port', 389)
        self.basedn = get('ldap_basedn', 'dc=localhost,dc=localdomain')
        self.filter_id = get('user_key', 'uid')
        self.ldap_user_search = get('ldap_user_search', 'ou=Users')
        self.ldap_group_search = get('ldap_group_search', 'ou=Groups')
        self.ldap_group_objectclass = get('ldap_group_objectclass', 'groupOfNames')
        self.grp_key = get('group_key', None)
        self.ldap_user_dn = '%s,%s' % (self.ldap_user_search, self.basedn)
        self.ldap_group_dn = '%s,%s' % (self.ldap_group_search, self.basedn)
        self.LDAPGroup = self.get_ldap_group_class()
        self.ldap_server_uri = self.get_ldap_server_uri()
        self.set_options()
        LOGGER.info('trace_level :: %s' % self.trace_level)
        LOGGER.info('tls_cacertfile :: %s' % self.tls_cacertfile)
        LOGGER.info('network_timeout :: %s' % self.network_timeout)
        
        LOGGER.info('host :: %s' % self.host)
        LOGGER.info('port :: %s' % self.port)
        LOGGER.info('basedn :: %s' % self.basedn)
        LOGGER.info('filter_id :: %s' % self.filter_id)
        LOGGER.info('ldap_user_search :: %s' % self.ldap_user_search)
        LOGGER.info('ldap_group_search :: %s' % self.ldap_group_search)
        LOGGER.info('ldap_group_objectclass :: %s' % self.ldap_group_objectclass)
        LOGGER.info('ldap_user_dn :: %s' % self.ldap_user_dn)
        LOGGER.info('ldap_group_dn :: %s' % self.ldap_group_dn)
        LOGGER.info('ldap_server_uri :: %s' % self.ldap_server_uri)
    def is_ldap_enabled(self):
        try:
            enabled = eval(tg.config.get('ldap_enabled','False'))
            return enabled
        except Exception as e:
            print 'Exception:',e
            return False
    def get_ldap_group_class(self):
        group_class = LDAP_Groups_Dict.get(self.ldap_group_objectclass)
        if not group_class:
            msg = 'Invalid objectclass: %s' % self.ldap_group_objectclass
            LOGGER.error(msg)
            raise LDAPInvalidObjectClass(msg)
        return group_class

    def get_all_user(self, group_name):
        ldapcon = self.get_connection()
        ldap_group_dn = 'cn=%s,%s' % (group_name, self.ldap_group_dn)
        users = self.LDAPGroup().get_all_user(ldapcon, ldap_group_dn)
        ldapcon.unbind()
        return users
    #pass
    def get_connection(self):
        try:
            msg = 'ldap_server_uri: %s' %self.ldap_server_uri
            print msg
            LOGGER.info(msg)
            ldapcon = self.ldap.initialize(self.ldap_server_uri,trace_level = self.trace_level)
            if self.start_tls and self.ldap_server_uri.startswith('ldap:'):
                msg = 'Trying to start TLS to %r.' %self.ldap_server_uri
                print msg
                LOGGER.info(msg)
                try:
                    ldapcon.start_tls_s()
                    msg = 'Using TLS to %r.' %self.ldap_server_uri
                    print msg
                    LOGGER.info(msg)
                except (self.ldap.SERVER_DOWN, self.ldap.CONNECT_ERROR) as ex:
                    LOGGER.error("Couldn't establish TLS to %r (ex: %s)." % (self.ldap_server_uri, str(ex)))
                    raise ex
            return ldapcon
        except Exception as e:
            import traceback
            traceback.print_exc()
            LOGGER.error(e)
            raise e

    def get_email_address(self, user_details):
        try:
            email_key = tg.config.get('email_key','email')
            emails = user_details.get(email_key)
            if emails:
                return emails[0]
            return ''
        except Exception as e:
            print 'Exception:',e
            return ''
    def validate_password(self, user_name, password):
        try:
            if self.is_ldap_enabled() == False:
                return dict(success=False, msg='LDAP is not Enabled.')
            ldapcon = self.get_connection()
            filter = '(%s=%s)' % (self.filter_id, user_name)
            try:
                ldap_result_id = ldapcon.search(self.ldap_user_dn, self.ldap.SCOPE_SUBTREE, filter)
            except Exception as e:
                import traceback
                traceback.print_exc()
                try:
                    exptn = to_str(e)
                    expt = eval(exptn)
                    if expt.get('desc'):
                        msg = expt['desc']
                        return dict(success=False, msg=msg)
                    raise e
                except Exception as ex:
                    print 'Exception: ',
                    print ex
                    raise e
            self.result_data = ldapcon.result(ldap_result_id)[1]
            if len(self.result_data) == 0:
                msg = 'User: %s does not exist in LDAP.' % user_name
                LOGGER.info(msg)
                return dict(success=False, msg=msg)
            if len(self.result_data) > 1:
                msg = 'Too many users: %s' % user_name
                LOGGER.error(msg)
                return dict(success=False, msg=msg)
            dn = self.result_data[0][0]
            rc = ldapcon.simple_bind(dn, password)
            ldapcon.result(rc)
            user_details = self.result_data[0][1]
            group_names = self.LDAPGroup().get_user_groups(user_details, self.grp_key)
            ldapcon.unbind()
        except self.ldap.INVALID_CREDENTIALS as e:
            import traceback
            traceback.print_exc()
            LOGGER.error(e)
            return dict(success=False, msg='LDAP authentication failed.')
        except Exception as e:
            import traceback
            traceback.print_exc()
            LOGGER.error(e)
            return dict(success=False, msg=str(e))
        return dict(success=True, user=user_name, group=group_names, user_details=user_details)

    def validate_user(self, user_name):
        try:
            if self.is_ldap_enabled() == False:
                return dict({'success':False, 'msg':'LDAP is not Enabled.'})
            ldapcon = self.get_connection()
            filter = '(%s=%s)' % (self.filter_id, user_name)
            try:
                ldap_result_id = ldapcon.search(self.ldap_user_dn, self.ldap.SCOPE_SUBTREE, filter)
            except Exception as e:
                import traceback
                traceback.print_exc()
                raise e
            self.result_data = ldapcon.result(ldap_result_id)[1]
            if len(self.result_data) == 0:
                msg = 'No such LDAP user: %s' % user_name
                LOGGER.info(msg)
                return dict({'success':False, 'msg':msg})
            if len(self.result_data) > 1:
                msg = 'Too many users: %s' % user_name
                LOGGER.error(msg)
                return dict({'success':False, 'msg':msg})
            user_details = self.result_data[0][1]
            group_names = self.LDAPGroup().get_user_groups(user_details, self.grp_key)
            email = self.get_email_address(user_details)
            return dict({'success':True, 'group':group_names, 'email_address':email})

        except Exception as e:
            import traceback
            traceback.print_exc()
            LOGGER.error(e)
            return dict({'success':False, 'msg':str(e)})
    #pass
    def get_ldap_server_uri(self):
        print 'host: ',
        print self.host
        ldap_server_uri = '%s:%s' % (self.host, self.port)
        if not self.host.startswith(self.LDAP_URI_PREFIX) and not self.host.startswith(self.LDAPS_URI_PREFIX):
            ldap_server_uri = '%s%s' % (self.LDAP_URI_PREFIX, self.host)
        return ldap_server_uri
    #pass
    def set_options(self):
        try:
            msg = 'Setting OPTIONS'
            print msg
            LOGGER.info(msg)
            OPTIONS = ((self.ldap.OPT_NETWORK_TIMEOUT, self.network_timeout))
            for option,value in OPTIONS:
                if value is not None:
                    self.ldap.set_option(option, value)
            if hasattr(self.ldap, 'TLS_AVAIL') and self.ldap.TLS_AVAIL:
                msg = 'Setting TLS_OPTIONS'
                print msg
                LOGGER.info(msg)
                TLS_OPTIONS = ((self.ldap.OPT_X_TLS_CACERTFILE, self.tls_cacertfile))
                for option,value in TLS_OPTIONS:
                    if value is not None:
                        self.ldap.set_option(option, value)
        except Exception as e:
            traceback.print_exc()
            LOGGER.error(e)
            raise e
        return None



