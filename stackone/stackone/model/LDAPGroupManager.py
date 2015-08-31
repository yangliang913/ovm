from stackone.core.utils.utils import to_unicode, to_str, get_ldap_module
import tg
import logging
LOGGER = logging.getLogger('stackone.model')
from pprint import pprint
LDAP_Groups_Dict = {}
class LDAPBaseGroup():
    def __init__(self):
        self.ldap = get_ldap_module()
        self.SCOPE_BASE = self.ldap.SCOPE_BASE
        self.user_key = tg.config.get('user_key', 'uid')
        self.group_key = tg.config.get('group_key', 'groupMembership')
        self.email_key = tg.config.get('email_key', 'email')

    def get_all_user(self, ldapcon, group_base_dn):
        return self._get_all_user(ldapcon, group_base_dn)

    def get_user_by_dn(self, ldapcon, user_dn, scope=None):
        try:
            if not scope:
                scope = self.SCOPE_BASE
            results = ldapcon.search_s(user_dn,scope)
            return results
        except Exception as e:
            pass
    def get_user_from_user_dn(self, dn):
        dn_dict = dict([item.split('=') for item in dn.split(',')])
        if dn_dict.has_key(self.user_key):
            if not dn_dict.get(self.user_key):
                LOGGER.error('%s is None in user DN: %s' % (self.user_key, dn))
            return dn_dict.get(self.user_key)
        LOGGER.error('Can not find %s in user DN: %s' % (self.user_key, dn))
        



class LDAPGroupOfNames(LDAPBaseGroup):
    MEMBER_ATTR = 'member'
    def get_user_groups(self, user_details, group_key):
        group_details = self._get_user_groups(user_details, group_key)
        group_names = self.parse_group(group_details)
        return group_names

    def parse_group(self, group_details):
        group_names = self._parse_group(group_details)
        return group_names

    def _get_user_groups(self, user_details, group_key):
        try:
            group_details = user_details.get(group_key)
            return group_details
        except Exception as e:
            print e
    def _parse_group(self, group_details):
        l = []
        try:
            for gp_name_str in group_details:
                for item in gp_name_str.split(','):
                    splt = item.split('=')
                    if len(splt) == 1:
                        l.append(splt[0])
                    if splt[0] == self.user_key:
                        l.append(splt[1])
        except Exception as ex:
            raise ex
        return l

    def _get_all_user(self, ldapcon, group_base_dn, scope=None):
        try:
            if not scope:
                scope = self.SCOPE_BASE
            result = []
            result_list = []
            result_data_dict = {}
            try:
                result = ldapcon.search_s(group_base_dn, scope)
            except Exception as e:
                import traceback
            if not len(result):
                LOGGER.info('Could not find group: %s' % group_base_dn)
            else:
                g_dn,result_data_dict = result[0]
                users = result_data_dict.get(self.MEMBER_ATTR)
                LOGGER.info('Members of Group:%s from LDAP: ===== %s \n' % (group_base_dn, users))
                for user in users:
                    user_info = self.get_user_by_dn(ldapcon, user)
                    LOGGER.info('Info of User:%s ==== %s' % (user, user_info))
                    if not user_info:
                        LOGGER.info('Could not find user: %s' % user)
                u_dn,usr_info = user_info[0]
                LOGGER.info('DN and Info of User:%s ==== DN:%s ==== Info:%s' % (user, u_dn, usr_info))
                res_dict = {self.user_key: self.get_user_from_dn(u_dn),self.group_key:usr_info.get(self.group_key),self.email_key:usr_info.get(self.email_key)}
                result_list.append(res_dict)
                LOGGER.info('Members of Group:%s after Parsing: ===== %s \n' % (group_base_dn, result_list))
                return result_list
            
        except Exception as e:
            import traceback
            traceback.print_exc()
            LOGGER.error(e)
            raise e


LDAP_Groups_Dict['groupOfNames'] = LDAPGroupOfNames
