from stackone.model import DBSession, Deployment, Group
from stackone.model.EmailManager import EmailManager
from stackone.model.VM import VM
from stackone.core.utils.utils import fetch_isp, getText, populate_node, to_str, to_unicode, get_product_edition
import tg
from stackone.core.utils.utils import PyConfig
import stackone.core.utils.constants as constants
import xml.dom.minidom
import os
import tempfile
import datetime
import time
import traceback
from datetime import datetime
import logging
LOGGER = logging.getLogger('stackone.model')
class AppUpdateManager():
    def __init__(self):
        self.update_url = 'http://www.stackone.com.cn/updates/updates.xml'
        self.updates_file = '/var/cache/stackone/updates.xml'

    def check_for_updates(self, send_mail=False):
        update_items = []
        dep = None
        try:
            deps = DBSession.query(Deployment).all()
            if len(deps) > 0:
                dep = deps[0]
                edition = get_product_edition()
                new_updates,max_dt = self.get_new_updates(dep.deployment_id, dep.update_checked_date, edition)
                if send_mail and new_updates:
                    self.send_update_mails(new_updates)
            else:
                LOGGER.error('Deployment table is not set. Update can not proceed.')
                return None
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error('Error fetching updates:' + to_str(ex))
            return None

        try:
            dep.update_checked_date = datetime.now()
            DBSession.add(dep)
        except:
            pass

        return update_items


    def get_new_updates(self, guid, update_checked_date, edition=None):
        new_updates = []
        updates = self.retrieve_updates(guid)
        r_date = update_checked_date
        max_dt = r_date

        for update in updates:
            str_p_dt = to_str(update['pubDate'])
            if str_p_dt:
                p_dt = time.strptime(str_p_dt, '%Y-%m-%d %H:%M:%S')
                dt = datetime(*p_dt[0:5])
                if dt>r_date:
                    if edition:
                        pltfom = to_str(update['platform'])
                        platforms = pltfom.split(',')
                        if (edition in platforms) or ('ALL' in platforms):
                            new_updates.append(update)
                            if dt>max_dt:
                                max_dt = dt

        str_max_dt = r_date.strftime('%Y-%m-%d %H:%M:%S')
        if max_dt > r_date:
            str_max_dt = max_dt.strftime('%Y-%m-%d %H:%M:%S')
        return (new_updates, str_max_dt)


    def retrieve_updates(self, guid):
        return []
        update_items = []
        try:
            if not os.access(self.updates_file, os.W_OK):
                (t_handle, t_name)= tempfile.mkstemp(prefix='updates.xml')
                self.updates_file = t_name
                os.close(t_handle)
            self.update_url += '?guid=' + guid
            fetch_isp(self.update_url, self.updates_file, '/xml')

        except Exception, ex:
            traceback.print_exc()
            LOGGER.error('Error fetching updates:' + to_str(ex))
            try:
                if os.path.exists(self.updates_file):
                    os.remove(self.updates_file)
            except:
                pass
            return update_items
        if os.path.exists(self.updates_file):
            updates_dom = xml.dom.minidom.parse(self.updates_file)
            for entry in updates_dom.getElementsByTagName('entry'):
                info = {}
                for text in ('title', 'link', 'description', 'pubDate', 'product_id', 'product_version', 'platform'):
                    info[text] = getText(entry, text)
                populate_node(info,entry,"link",{ "link" : "href"})
                update_items.append(info)

        try:
            if os.path.exists(self.updates_file):
                os.remove(self.updates_file)
        except:
            pass
        return update_items


    def send_update_mails(self, updates):
        grp = Group.by_group_name(to_unicode('adminGroup'))
        emailer = EmailManager()
        for usr in grp.users:
            for update in updates:
                sent = True
                try:
                    sent = emailer.send_email(usr.email_address, to_str(update.get('description', '')), subject=to_str(update.get('title', '')), mimetype='html')
                except Exception as e:
                    traceback.print_exc()
                    LOGGER.error('Error sending update mail:' + to_str(update.get('title', '')))
                    return None
                if sent == False:
                    LOGGER.error('Error sending update mail:' + to_str(update.get('title', '')))
                    return None

    def check_user_updates(self, username):
        update_items = []
        dep = None
        try:
            deps = DBSession.query(Deployment).all()
            if len(deps) > 0:
                dep = deps[0]
                user_config_filename = os.path.abspath(tg.config.get('user_config'))
                if not os.path.exists(user_config_filename):
                    user_config_file = open(user_config_filename, 'w')
                    user_config_file.close()
                user_config = PyConfig(filename=user_config_filename)
                date = user_config.get(username)
                if date != None:
                    p_r_date = time.strptime(date, '%Y-%m-%d %H:%M:%S')
                    r_date = datetime(*p_r_date[0:5])
                else:
                    r_date = datetime.now()
                edition = get_product_edition()
                update_items,max_dt = self.get_new_updates(dep.deployment_id, r_date, edition)
                user_config[username] = max_dt
                user_config.write()
            else:
                LOGGER.error('Deployment table is not set.Update can not proceed.')
                return None
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error('Error fetching updates:' + to_str(ex))
            return None
        return update_items




from stackone.model.Entity import Entity
import threading
class UIUpdateManager():
    _UIUpdateManager__dict = {}
    _UIUpdateManager__dicttask = {}
    lock = threading.RLock()
    def __init__(self):
        self.updated_entities = self._UIUpdateManager__dict
        self.updated_tasks = self._UIUpdateManager__dicttask
#################gogo
    def set_updated_entities(self, entity_ids):
        node_ids = []
        up_sessions = {}
        (usrs, grps) = ([], [])
        if not entity_ids:
            LOGGER.error('Error: entity_ids are not found.')
            return None
        del_ent_usrs = []
        for entity_id in entity_ids.split(','):
            usr_grps = []
            ent = Entity.get_entity(entity_id)
            if ent and ent.type.name==constants.DOMAIN:
                if ent.csep_context_id:
                    vm = DBSession.query(VM.cloud_vm_id).filter(VM.id == entity_id).first()
                    if vm and vm[0]:
                        cloud_vm_id = vm[0]
                        node_ids.append(cloud_vm_id)
                        node_ids = self.merge_lists(node_ids, Entity.get_hierarchy(cloud_vm_id))
                        usr_grps.extend(Entity.get_users_groups(cloud_vm_id))

            hierarchy = Entity.get_hierarchy(entity_id)
            if not hierarchy:
                hierarchy = [entity_id]
                del_ent_usrs = self.updated_entities.keys()

            node_ids = self.merge_lists(node_ids, hierarchy)
            usr_grps.extend(Entity.get_users_groups(entity_id))
            (priv_usrs, priv_groups) = ([], [])

            for priv_usr,priv_group in usr_grps:
                priv_usrs.append(priv_usr)
                priv_groups.append(priv_group)

            usrs = self.merge_lists(usrs, priv_usrs)
            grps = self.merge_lists(grps, priv_groups)

        usr_names=[u.user_name for u in usrs]

        grp_names=[g.group_name for g in priv_groups]
        if del_ent_usrs:
            usr_names=del_ent_usrs
        try:
            self.lock.acquire()
            
            for key in self.updated_entities.keys():
                if key not in usr_names and key not in grp_names:
                    continue
                else:
                    up_sessions=self.updated_entities.get(key, {})
                    for session,nodes in up_sessions.iteritems():
                        if len(nodes) > 35:
                            nodes=[]
                        updated_nodes=self.merge_lists(nodes, node_ids)
                        self.updated_entities[key][session]=updated_nodes
        finally:
            self.lock.release()


    def get_updated_entities(self, user_name, group_names):
        self.lock.acquire()
        up_ents = []
        try:
            session = self.get_session()
            up_sessions = self.updated_entities.get(user_name, None)
            if up_sessions == None:
                up_sessions = {}
                self.updated_entities[user_name] = up_sessions
            up_ents = up_sessions.get(session, None)
            if up_ents==None:
                up_ents = []
                self.updated_entities[user_name][session] = up_ents

            else:
                up_ents = []
                for x in range(len(self.updated_entities[user_name][session])):
                    up_ents.append(self.updated_entities[user_name][session].pop())

            if not up_ents and group_names:
                for group_name in group_names:
                    up_sessions = self.updated_entities.get(group_name, None)
                    if up_sessions == None:
                        up_sessions = {}
                        self.updated_entities[group_name] = up_sessions
                    up_ents = up_sessions.get(session, None)
                    if up_ents == None:
                        up_ents = []
                        self.updated_entities[group_name][session] = up_ents
                        continue
                    up_ents = []
                    for x in range(len(self.updated_entities[group_name][session])):
                        up_ents.append(self.updated_entities[group_name][session].pop())

        finally:
            self.lock.release()
        return up_ents

    def clear_updated_entities(self, user_name, group_names):
        session = self.get_session()
        self.updated_entities[user_name][session] = []
        for group_name in group_names:
            self.updated_entities[group_name][session] = []


    def del_user_updated_entities(self, user_name, group_names):
        session = self.get_session()
        if self.updated_entities.get(user_name, None) is not None:
            if self.updated_entities.get(user_name).get(session) is not None:
                del self.updated_entities[user_name][session]

        for group_name in group_names:
            #if self.updated_entities.get(group_name).get(session) is not None:
            if self.updated_entities.get(group_name,None) is not None:
                if self.updated_entities.get(group_name).get(session) is not None:
                    del self.updated_entities[group_name][session]
        
    def set_updated_tasks(self, task_id, user_name, entity_id=None):
        user_names = []
        if entity_id:
            usr_grps = Entity.get_users_groups(entity_id)
            if not usr_grps:
                user_names = self.updated_tasks.keys()
            else:
                priv_usrs = []
                for priv_usr,priv_group in usr_grps:
                    priv_usrs.append(priv_usr)
                user_names=[u.user_name for u in priv_usrs]
                if user_name not in user_names:
                    user_names.append(user_name)
        else:
            user_names.append(user_name)
        self.lock.acquire()
        try:
            for user_name in user_names:
                up_sessions = self.updated_tasks.get(user_name, {})
                for session,tasks in up_sessions.iteritems():
                    if len(tasks) > 35:
                        tasks = []
                    updated_tasks = self.merge_lists(tasks, [task_id])
                    self.updated_tasks[user_name][session] = updated_tasks
        finally:
            self.lock.release()


    def get_updated_tasks(self, user_name):
        self.lock.acquire()
        up_tasks = []
        try:
            session = self.get_session()
            up_sessions = self.updated_tasks.get(user_name, None)
            if up_sessions == None:
                up_sessions = {}
                self.updated_tasks[user_name] = up_sessions
            up_tasks = up_sessions.get(session, None)
            if up_tasks==None:
                up_tasks = []
                self.updated_tasks[user_name][session] = up_tasks
            else:
                up_tasks = []
                for x in range(len(self.updated_tasks[user_name][session])):
                    up_tasks.append(self.updated_tasks[user_name][session].pop())
        finally:
            self.lock.release()
        return up_tasks

    def clear_updated_tasks(self, user_name):
        session = self.get_session()
        self.updated_tasks[user_name][session] = []

    def del_user_updated_tasks(self, user_name):
        session = self.get_session()
        if self.updated_tasks.get(user_name, None) is not None:
            if self.updated_tasks.get(user_name).get(session) is not None:
                del self.updated_tasks[user_name][session]

    def merge_lists(self, list1, list2):
        for item in list2:
            if item not in list1:
                list1.append(item)
        return list1


    def get_session(self):
        from tg import session
        return session.id




