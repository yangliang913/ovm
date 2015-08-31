from stackone.model import DBSession
from stackone.model.ManagedNode import ManagedNode
from stackone.model.VM import VM
from stackone.model.Entity import Entity
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.model.Groups import ServerGroup
import stackone.core.utils.constants as constants
from stackone.core.utils.utils import to_unicode, to_str, dynamic_map, copyToRemote, print_traceback
from stackone.model.VM import VM, VMStorageLinks
from stackone.model.services import Task
from sqlalchemy.orm import eagerload
from stackone.model.availability import AvailState, StateTransition, VMStateHistory
import logging
import traceback
import time
import transaction
import tg
import os
from datetime import datetime, timedelta
LOGGER = logging.getLogger('stackone.model.Maintenance')
class Maintenance():
    DO_NOTHING = 1
    SHUTDOWN_ALL_VMS = 2
    MIGRATE_VMS_TO_SERVERS = 3
    MIGRATE_VMS_TO_SERVER = 4
    PAUSE_IN_STANDBY = 50
    FENCING = 20
    FAILURE = 'Failure'
    SUCCESS = 'Success'
    PARTIAL = 'Partial Success'
    tc = TaskCreator()
    lockmode = 'update'
    RESUME_TASK = 'resume_task'
    def __init__(self):
        self.node_id = None
        self.node = None
        self.nodename = None
        self.entity_id = None
        self.auth = None
        self.status = ''
        self.msg = ''
        self.maint_task_id = None
        self.maint_task = None
        self.maint_task_context = None
        self.current_operation = None

    def initial_check(self, node_id, maintenance):
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).with_lockmode(self.lockmode).first()
        LOGGER.debug('Row locked for node: %s' % node.hostname)
        if node:
            if not node.maintenance and not maintenance:
                return {'success':False,'msg':'Server:%s was not in maintenance mode' %node.hostname}
            if maintenance:
                if node.is_maintenance():
                    transaction.commit()
                    LOGGER.debug('locked released for node: %s' % node.hostname)
                    return {'success':False,'msg':'Node %s already marked for Maintenance' %node.hostname}
                transaction.commit()
                LOGGER.debug('locked released for node: %s' % node.hostname)
                return {'success':True,'msg':''}
            transaction.commit()
            LOGGER.debug('locked released for node: %s' % node.hostname)
            return {'success':True,'msg':''}
        else:
            LOGGER.debug('Node is None')
            raise Exception('Node is None')

    def initialize(self, auth, node_id):
        self.node_id = node_id
        self.entity_id = node_id
        self.auth = auth
        self.set_node(node_id)

    def set_node(self, node_id):
        self.node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
        if self.node:
            self.nodename = self.node.hostname
        else:
            LOGGER.debug('Node is None')
            raise Exception('Node is None')

    def set_server_maintenance(self, info):
        try:
            msg = '\n----- Maintenance setting of Node: %s ------' %self.node.hostname
            LOGGER.debug('In set_server_maintenance: \ninfo\n%s' %info)
            if not info['maintenance']:
                msg += '\n Node:%s leaving Maintenance mode' %self.node.hostname
            else:
                self.node.maintenance = info['maintenance']
            if info['do_nothing']:
                msg += '\n Do not shutdown or migrate Virtual Machines'
                self.node.maintenance_operation = Maintenance.DO_NOTHING
            if info['shutdown_vms']:
                msg += '\n Shutdown all vms'
                self.node.maintenance_operation = Maintenance.SHUTDOWN_ALL_VMS
            elif info['migrate_to_other_server']:
                msg += '\n Migrate vms to other servers in the server pool'
                self.node.maintenance_operation = Maintenance.MIGRATE_VMS_TO_SERVERS
                if info['migrate_vms_back_from_servers']:
                    msg += '\n Migrate vms back from servers, when server come out of maintenance mode'
                    self.node.maintenance_migrate_back = True
                else:
                    self.node.maintenance_migrate_back = False
            elif info['migrate_to_specific_server']:
                msg += '\n Migrate vms to a specific server in the server pool'
                self.node.maintenance_operation = Maintenance.MIGRATE_VMS_TO_SERVER
                if info['migrate_vms_back_from_specific_server']:
                    msg += '\n Migrate vms back from servers, when server come out of maintenance mode'
                    self.node.maintenance_migrate_back = True
                else:
                    self.node.maintenance_migrate_back = False    
            self.node.maintenance_mig_node_id = info.get('server')
            self.node.maintenance_user = self.auth.user_name
            LOGGER.debug(msg)
            DBSession.add(self.node)
            transaction.commit()
        except Exception,ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",''))
            return {'success':False,'msg':to_str(ex).replace("'",'')}
        return {'success':True,'msg':'Successfully Saved'}
                
    def set_log_and_message(self, msg, log=True, message=True):
        if message:
            self.msg += '\n' + msg
        if log:
            LOGGER.info(msg)

    def update_maint_task_context(self):
        DBSession.query(Task).filter(Task.task_id == self.maint_task_id).update(values = dict(context = self.maint_task_context))
        transaction.commit()

    def get_maint_task_context(self, key):
        tsk = DBSession.query(Task).filter(Task.task_id == self.maint_task_id).first()
        if tsk:
            return tsk.context.get(key)

    def get_task(self, task_id):
        task = DBSession.query(Task).filter(Task.task_id == task_id).first()
        return task
####################not
    def resume_maintenance(self, maint_task_id, is_maintenance):
        try:
            self.msg = ''
            msg = 'Resume(Maintenance): Entered into maintenance Resume task for node:%s' % self.node.hostname
            LOGGER.info(msg)
            msg = 'Entered into maintenance Resume task for node:%s' % self.node.hostname
            self.set_log_and_message(msg, message = True)
            self.maint_task_id = maint_task_id
            self.maint_task = self.get_task(self.maint_task_id)
            self.maint_task_context = self.maint_task.context
            self.maintenance_task_status = True
            node_ent = self.auth.get_entity(self.node_id)
            grp_ent = node_ent.parents[0]
            if is_maintenance:
                msg = 'Resume(Maintenance): Node:%s Entering into maintenance mode' % self.node.hostname
                LOGGER.info(msg)
                msg = 'Node:%s Entering into maintenance mode' % self.node.hostname
                self.set_log_and_message(msg, True)
                try:
                    if self.node.maintenance_operation in [Maintenance.MIGRATE_VMS_TO_SERVERS,Maintenance.MIGRATE_VMS_TO_SERVER]:
                        dest_node_id = self.node.maintenance_mig_node_id
                        migrated_vms = self.maint_task_context.get('migrated_vms')
                        if not migrated_vms:
                            LOGGER.debug('Cant find list of migrated vms, in the context of maintenance task')
                            failed_doms = dom_ids = [child.entity_id for child in node_ent.children]
                        else:
                            migrated_vm_ids = [x[0] for x in migrated_vms]    
                            migrated_vms_task_ids = [x[1] for x in migrated_vms]
                            for tsk_id in migrated_vms_task_ids:
                                task = DBSession.query(Task).filter(Task.task_id == tsk_id).first()
                                if not task.is_finished():
                                    LOGGER.info('Resume(Maintenance): Waiting for the completion of task:%s' % tsk_id)
                                    wait_time = tg.config.get(constants.MIGRATE +'_time')
                                    while True:
                                        finished,status = self.wait_for_task_completion(tsk_id,int(wait_time))
                                        if finished:
                                            break
                                    LOGGER.info('Resume(Maintenance): task:%s finished' % tsk_id)
                            failed_doms = dom_ids = [child.entity_id  for child in node_ent.children if child.entity_id not in migrated_vm_ids ]
                    if self.node.maintenance_operation in [Maintenance.DO_NOTHING]:
                        msg = 'Resume(Maintenance): Operation : Do not shutdown or migrate Virtual Machines'
                        self.set_log_and_message(msg)
                    elif self.node.maintenance_operation == Maintenance.SHUTDOWN_ALL_VMS:
                        msg = 'Resume(Maintenance): Operation : Shutdown all vms'
                        LOGGER.info(msg)
                        msg = 'Operation : Shutdown all vms'
                        self.set_log_and_message(msg, True)
                        shutdown_info = self.maint_task_context.get('shutdown_vms_info')
                        if not shutdown_info:
                            msg = 'Resume(Maintenance):CMS failure before setting context'
                            self.set_log_and_message(msg, False)
                            msg = 'CMS failure before setting context'
                            self.set_log_and_message(msg, False)
                            LOGGER.debug("Cant find key 'shutdown_info', in the context of maintenance task")
                            return self.msg
                        for vm_id,task_id in shutdown_info:
                            wait_time = tg.config.get(constants.SHUTDOWN + '_time')
                            dom = DBSession.query(VM).filter(VM.id == vm_id).first()
                            while True:
                                msg = 'Resume(Maintenance): waiting for shutting down VM:%s' % dom.name
                                self.set_log_and_message(msg, False)
                                msg = 'waiting for shutting down VM:%s' % dom.name
                                self.set_log_and_message(msg, False)
                                finished,status = self.wait_for_task_completion(task_id, int(wait_time))
                                if finished:
                                    break
                            if finished == True and status == Task.SUCCEEDED:
                                msg = 'Resume(Maintenance):VM:%s Shutdown Success' %dom.name
                                self.set_log_and_message(msg, False)
                                msg = 'VM:%s Shutdown Success' %dom.name
                                self.set_log_and_message(msg, False)
                            else:
                                msg = 'Resume(Maintenance):VM:%s Shutdown Failed' %dom.name
                                self.set_log_and_message(msg, False)
                                msg = 'VM:%s Shutdown Failed' %dom.name
                                self.set_log_and_message(msg, False)
                        self.shutdown_all_vms(mode = self.RESUME_TASK)
                    elif self.node.maintenance_operation == Maintenance.MIGRATE_VMS_TO_SERVERS:
                        msg = 'Resume(Maintenance): Operation : Migrating vms to any server in the ServerPool'
                        self.set_log_and_message(msg, False)
                        if len(dom_ids):
                            self.migrate_to_any_server_in_the_serverpool(grp_ent, failed_doms = failed_doms, dom_ids = dom_ids)
                        else:
                            vm_info_tup = self.get_maint_task_context('migrated_vms')
                            vm_ids = [x[0] for x in vm_info_tup]
                            self.add_vm_states(vm_ids)
                            msg = 'Could not find any vms under node:%s' %self.node.hostname
                            self.set_log_and_message(msg)
                    elif self.node.maintenance_operation == Maintenance.MIGRATE_VMS_TO_SERVER:
                        msg = 'Resume(Maintenance): Operation : Migrating vms to a specific server in the ServerPool'
                        self.set_log_and_message(msg, False)
                        if len(dom_ids):
                            self.migrate_to_specific_server_in_the_serverpool(dom_ids, dest_node_id)
                        else:
                            vm_info_tup = self.get_maint_task_context('migrated_vms')
                            vm_ids = [x[0] for x in vm_info_tup]
                            self.add_vm_states(vm_ids)
                            msg = 'Could not find any vms under node:%s' %self.node.hostname
                            self.set_log_and_message(msg)
                    if not self.maintenance_task_status:
                        raise Exception(self.msg)
                except Exception as ex:
                    self.reset_maintenance_mode()
                    print_traceback()
                    LOGGER.error(to_str(ex).replace("'", ''))
                    raise ex
                msg = 'Node %s Entered into Maintenance mode' % self.node.hostname
                self.set_log_and_message(msg)
            else:
                msg = 'Resume(Maintenance): Node:%s Leaving maintenance mode' % self.node.hostname
                LOGGER.info(msg)
                self.leaving_maintenance_mode()
            return self.msg
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex


    def server_maintenance(self, maint_task_id, is_maintenance):
        LOGGER.debug('In server_maintenance')
        self.maint_task_id = maint_task_id
        self.maint_task = self.get_task(self.maint_task_id)
        self.maint_task_context = self.maint_task.context
        self.maintenance_task_status = True
        node_ent = self.auth.get_entity(self.node_id)
        grp_ent = node_ent.parents[0]
        if is_maintenance:
            try:
                msg = 'Node %s Entering into Maintenance mode' % self.node.hostname
                self.set_log_and_message(msg)
                failed_doms = dom_ids = [child.entity_id for child in node_ent.children]
                dest_node_id = self.node.maintenance_mig_node_id
                if self.node.maintenance_operation in [Maintenance.DO_NOTHING]:
                    msg = 'Operation : Do not shutdown or migrate Virtual Machines'
                    self.set_log_and_message(msg)
                elif self.node.maintenance_operation == Maintenance.SHUTDOWN_ALL_VMS:
                    self.shutdown_all_vms()
                elif self.node.maintenance_operation == Maintenance.MIGRATE_VMS_TO_SERVERS:
                    if len(dom_ids):
                        self.migrate_to_any_server_in_the_serverpool(grp_ent, failed_doms = failed_doms, dom_ids = dom_ids)
                    else:
                        msg = 'Could not find any vms under node:%s' %self.node.hostname
                        self.set_log_and_message(msg)
                elif self.node.maintenance_operation == Maintenance.MIGRATE_VMS_TO_SERVER:
                    if len(dom_ids):
                        self.migrate_to_specific_server_in_the_serverpool(dom_ids, dest_node_id)
                    else:
                        msg = 'Could not find any vms under node:%s' %self.node.hostname
                        self.set_log_and_message(msg)
                if not self.maintenance_task_status:
                    raise Exception(self.msg)
            except Exception as ex:
                self.reset_maintenance_mode()
                print_traceback()
                LOGGER.error(to_str(ex).replace("'", ''))
                raise ex

            msg = 'Node %s Entered into Maintenance mode' % self.node.hostname
            self.set_log_and_message(msg)
        else:
            self.leaving_maintenance_mode()
        return self.msg

####################@@@@@@@@@@
    def leaving_maintenance_mode(self):
        try:
            msg = 'Node %s Leaving Maintenance mode' % self.node.hostname
            self.set_log_and_message(msg)
            msg = 'Waiting for network and storage sync of server :%s' % self.node.hostname
            self.set_log_and_message(msg)
            self.node.wait_for_nw_str_sync(self.auth)
            migrate_back = False
            if self.node.maintenance_operation in [Maintenance.MIGRATE_VMS_TO_SERVERS, Maintenance.MIGRATE_VMS_TO_SERVER]:
                msg = 'Operation : Migrating VMs back'
                self.set_log_and_message(msg)
                if not self.node.maintenance_migrate_back:
                    msg = 'Migrate vms back is disabled for Node %s' % self.node.hostname
                    self.set_log_and_message(msg)
                    self.reset_maintenance_mode()
                else:
                    msg = 'Migrate vms back is Enabled for Node %s' % self.node.hostname
                    self.set_log_and_message(msg)
                    self.set_context_key('migrated_vms', [])
                    self.migrate_back_and_start_vms()
                    migrate_back = True
            else:
                if self.node.maintenance_operation in [Maintenance.SHUTDOWN_ALL_VMS]:
                    msg = 'Operation : Starting VMs'
                    self.set_log_and_message(msg)
                    msg = 'Starting vms in the Node %s' % self.node.hostname
                    self.set_log_and_message(msg)
                    self.migrate_back_and_start_vms()
                    migrate_back = True
                else:
                    if self.node.maintenance_operation in [Maintenance.DO_NOTHING]:
                        msg = 'Operation : Do not shutdown or migrate Virtual Machines'
                        self.set_log_and_message(msg)
                        self.reset_maintenance_mode()
            if migrate_back:
                if self.status not in [self.SUCCESS, self.PARTIAL]:
                    msg = 'All migrations(back) failed'
                    self.set_log_and_message(msg)
                    self.set_maintenance_mode()
                    raise Exception(self.msg)
                else:
                    self.reset_maintenance_mode()
            msg = 'Node %s Left Maintenance mode' % self.node.hostname
            self.set_log_and_message(msg)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex

    def shutdown_all_vms(self, mode=None):
        try:
            msg = 'Operation : Shutdown All VMs'
            self.set_log_and_message(msg)
            self.set_context_key('running_vms_info', [])
            self.set_context_key('shutdown_vms_info', [])
            task_status = self.maintenance_shutdown(mode)
            if not task_status:
                msg = 'All shutdown failed, can not put the server in to maintenance mode.'
                self.set_log_and_message(msg)
                self.maintenance_task_status = False
                self.reset_maintenance_mode()
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex

    def migrate_to_any_server_in_the_serverpool(self, grp_ent, failed_doms, dom_ids):
        try:
            msg = 'Operation : Migrate VMs to other Servers in the Server Pool'
            self.set_log_and_message(msg)
            self.set_context_key('migrated_vms', [])
            self.migrate_to_servers(grp_ent.entity_id, [], failed_doms, dom_ids)
            if self.status not in [self.SUCCESS, self.PARTIAL]:
                msg = 'All migration failed, Could not put the server in to maintenance mode.'
                self.set_log_and_message(msg)
                self.maintenance_task_status = False
                self.reset_maintenance_mode()
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex

    def set_context_key(self, key, value=None):
        if not self.maint_task_context.has_key(key):
            self.maint_task_context[key] = value

    def migrate_to_specific_server_in_the_serverpool(self, dom_ids, dest_node_id):
        try:
            msg = 'Operation : Migrate VMs to a Specific Server in the Server Pool'
            self.set_log_and_message(msg)
            self.set_context_key(key='migrated_vms', value=[])
            task_status = self.migrate_to_specific_server(dom_ids, dest_node_id)
            if not task_status:
                msg = 'All migration failed, Could not put the server in to maintenance mode.'
                self.set_log_and_message(msg)
                self.maintenance_task_status = False
                self.reset_maintenance_mode()
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex

    def get_vm_ids(self):
        node_ent = DBSession.query(Entity).filter(Entity.entity_id == self.node_id).first()
        if node_ent is None:
            msg = 'Entity can not be found for ' + self.node_id
            LOGGER.error(msg)
            raise Exception(msg)
        vm_ents = node_ent.children
        vm_ids = [vm.entity_id for vm in vm_ents]
        return vm_ids


    def add_vm_states(self, vm_ids):
        try:
            transaction.begin()
            avail_states = DBSession.query(AvailState).filter(AvailState.entity_id.in_(vm_ids)).all()
            from stackone.model.VM import VM
            (vshs, avails) = ([], [])
            for avail in avail_states:
                vsh = DBSession.query(VMStateHistory).filter(VMStateHistory.node_id == self.node_id).filter(VMStateHistory.vm_id == avail.entity_id).first()
                if vsh is None:
                    vsh = VMStateHistory(self.node_id, avail.entity_id, avail.avail_state, avail.monit_state, avail.transient_state, avail.transient_state_time, avail.owner)
                else:
                    vsh.avail_state = avail.avail_state
                    vsh.monit_state = avail.monit_state
                    vsh.transient_state = avail.transient_state
                    vsh.transient_state_time = avail.transient_state_time
                    vsh.owner = avail.owner
                    vsh.timestamp = datetime.now()
                vshs.append(vsh)
                avails.append(avail)
            DBSession.add_all(vshs)
            DBSession.add_all(avails)
            transaction.commit()
        except Exception as e:
            LOGGER.error(to_str(e))
            DBSession.rollback()
            transaction.begin()
            traceback.print_exc()
            raise e

    def migrate_to_specific_server(self, dom_list, dest_node_id):
        failed_migrations = []
        dest_node = DBSession.query(ManagedNode).filter(ManagedNode.id == dest_node_id).first()
        for vm_id in dom_list:
            dom = DBSession.query(VM).filter(VM.id == vm_id).first()
            sts = self.dom_migrate(self.auth, dom, self.node, dest_node)
            if sts:
                msg = 'Virtual Machine:%s successfully migrated from node:%s to node:%s' % (dom.name, self.node.hostname, dest_node.hostname)
                self.set_log_and_message(msg)
            else:
                failed_migrations.append(vm_id)
                msg = 'Migration of Virtual Machine:%s from node:%s to node:%s falied' % (dom.name, self.node.hostname, dest_node.hostname)
                self.set_log_and_message(msg)
        if len(dom_list) == len(failed_migrations):
            return False
        vm_info_tup = self.get_maint_task_context(key = 'migrated_vms')
        vm_ids = [x[0] for x in vm_info_tup]
        self.add_vm_states(vm_ids)
        return True


    def migrate_to_servers(self, grpid, tried_sb_nodes=[], failed_doms=[], dom_ids=[]):
        msg = 'Starting Maintenance migration on Node ' + self.nodename + '. Checking for VMs.'
        self.msg += '\n' + msg
        LOGGER.info(msg)
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.entity_id).first()
        grp = DBSession.query(ServerGroup).filter(ServerGroup.id == grpid).first()
        gretry_count = grp.getAttributeValue(constants.retry_count, 3)
        gwait_interval = grp.getAttributeValue(constants.wait_interval, 3)
        if grp.use_standby == True:
            while len(failed_doms) > 0:
                msg = 'Finding standby node.'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                new_node = self.find_standby_node(self.auth, None, node, exclude_ids=tried_sb_nodes)
                if new_node is None:
                    msg = 'All standby nodes are exhausted.'
                    self.msg += '\n' + msg
                    LOGGER.info(msg)
                    break
                failed_doms = self.dom_fail_over(failed_doms, node, new_node, gretry_count, gwait_interval, self.FENCING)
                tried_sb_nodes.append(new_node.id)
        tot_failed = failed_doms

        tmp_failed_doms = [d for d in failed_doms]
        if len(failed_doms) > 0:
            tot_failed = []
            for domid in tmp_failed_doms:
                self.step = self.PAUSE_IN_STANDBY
                dom = DBSession.query(VM).filter(VM.id == domid).first()
                domname = dom.name
                msg = 'Starting initial placement for ' + domname
                self.msg += '\n' + msg
                LOGGER.info(msg)
                new_node = self.get_allocation_candidate(self.auth,dom,node)
                failed = self.dom_fail_over(domid, node, new_node, gretry_count, gwait_interval, self.PAUSE_IN_STANDBY)
                if len(failed) == 1:
                    tot_failed.append(failed[0])

        if len(tot_failed)>0:
            doms = DBSession.query(VM).filter(VM.id.in_(tot_failed)).all()
            domnames = [d.name for d in doms]
            msg = 'Failed to migrate following VMs' + to_str(domnames)
            self.msg += '\n' + msg
            LOGGER.info(msg)
        else:
            self.status = self.SUCCESS
            msg = 'Successfully migrated all VMs'
            self.msg += '\n' + msg
            LOGGER.info(msg)

        if len(tot_failed) != 0 and len(tot_failed) < len(dom_ids):
            self.status = self.PARTIAL
        vm_info_tup = self.get_maint_task_context(key='migrated_vms')
        vm_ids = [x[0] for x in vm_info_tup]
        self.add_vm_states(vm_ids)
        return True
    def maintenance_shutdown(self, mode=None):
        LOGGER.debug('In maintenance_shutdown')
        failed_shutdowns = []
        vm_ids = self.get_vm_ids()
        running_vms = VM.get_running_vms(vm_ids)
        if not len(running_vms):
            msg = 'Could not find any running vms under the node:%s' % self.node.hostname
            self.set_log_and_message(msg)
            return True
        if mode not in [self.RESUME_TASK]:
            self.maint_task_context['running_vms_info'].extend(running_vms)
            self.update_maint_task_context()
            self.add_vm_states(vm_ids)
        for dom in running_vms:
            task_id = self.tc.vm_action(self.auth, dom.id, self.node_id, constants.SHUTDOWN, constants.Maintenance)
            self.maint_task_context['shutdown_vms_info'].append((dom.id, task_id))
            self.update_maint_task_context()
            wait_time = tg.config.get(constants.SHUTDOWN + '_time')
            while True:
                finished,status = self.wait_for_task_completion(task_id, int(wait_time))
                if finished:
                    break
            if finished == True and status == Task.SUCCEEDED:
                msg = 'VM:%s Shutdown Success' % dom.name
                self.set_log_and_message(msg)
            else:
                failed_shutdowns.append(dom.id)
                msg = 'VM:%s Shutdown Failed' % dom.name
                self.set_log_and_message(msg)
                if len(failed_shutdowns) == len(self.maint_task_context['running_vms_info']):
                    return False
        return True

    def migrate_back_and_start_vms(self):
        LOGGER.debug('In migrate_back')
        vshs = VMStateHistory.get_vm_states(self.node_id)
        (s_flag, f_flag) = (False, False)
        for vsh in vshs:
            try:
                vm = DBSession.query(VM).filter(VM.id == vsh.vm_id).options(eagerload('current_state')).first()
                domname = vm.name
                if vm is None:
                    msg = 'Removing entries for VM ' + domname + ' from VM State History'
                    LOGGER.info(msg)
                    VMStateHistory.remove_vm_states(self.entity_id, vsh.vm_id, True)
                msg = 'Processing VM ' + domname + ' for the Node ' + self.nodename + '. '
                self.msg += '\n\n' + msg + '\n'
                self.msg += '==============================\n'
                LOGGER.info(msg)
                vm_ent = DBSession.query(Entity).filter(Entity.entity_id == vm.id).one()
                src_node = DBSession.query(ManagedNode).filter(ManagedNode.id == vm_ent.parents[0].entity_id).options(eagerload('current_state')).one()
        
                msg = 'VM ' + domname + ' is already under the Node ' + self.nodename
                self.msg += '\n' + msg
                LOGGER.info(msg)
                (was_running, was_paused) = (False, False)
                if vsh.monit_state == AvailState.MONITORING:
                    was_running = True
                    if vsh.avail_state == VM.PAUSED:
                        was_paused = True
                if was_running == False:
                    config = vm.get_config()
                    if config and config.get('auto_start_vm') == 1:
                        was_running = True
        
                if was_running == True:
                    retry_count = vm.get_attribute_value(constants.retry_count, 3)
                    wait_interval = vm.get_attribute_value(constants.wait_interval, 3)
                    msg = 'Trying to start the VM ' + domname
                    self.msg += '\n' + msg
                    LOGGER.info(msg)
                    if self.dom_start(self.auth, vm, self.node, retry_count, wait_interval):
                        msg = 'Successfully started VM ' + domname
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                        s_flag = True
                        if was_paused:
                            msg = 'Trying to pause VM ' + domname
                            self.msg += '\n' + msg
                            LOGGER.info(msg)
                            if self.dom_pause(self.auth,vm,self.node) == True:
                                s_flag = True
                                msg = 'Successfully paused VM ' + domname
                                self.msg += '\n' + msg
                                LOGGER.info(msg)
                            else:
                                f_flag = True
                                msg = 'Failed to pause VM ' + domname
                                self.msg += '\n' + msg
                                LOGGER.info(msg)
                    else:
                        f_flag = True
                        msg = 'Failed to start VM ' + domname
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                else:
                    s_flag = True
                msg = 'Removing entries for VM ' + domname + ' from VM State History'
                LOGGER.info(msg)
                VMStateHistory.remove_vm_states(self.entity_id, vsh.vm_id)
                #CONTINUE_LOOP
                if self.is_down(vm):
                    msg = 'Cold Mirgation of VM ' + domname + ' to the Node ' + self.nodename + '. '
                    self.msg += '\n' + msg
                    LOGGER.info(msg)
                    if self.dom_migrate(self.auth, vm, src_node, self.node):
                        f_flag = True
                        msg = 'Migrating VM ' + domname + ' back to the node ' + self.nodename + ' failed.'
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                        config = vm.get_config()
                        if config and config.get('auto_start_vm') == 1:
                            LOGGER.info('auto_start_vm is 1 for Down VM %s' % domname)
                            retry_count = vm.get_attribute_value(constants.retry_count, 3)
                            wait_interval = vm.get_attribute_value(constants.wait_interval, 3)
                            if self.dom_start(self.auth, vm, self.node, retry_count, wait_interval):
                                msg = 'Successfully started Down VM ' + domname
                                s_flag = True
                                self.msg += '\n' + msg
                                LOGGER.info(msg)
                            else:
                                f_flag = True
                                msg = 'Failed to start Down VM ' + domname
                                self.msg += '\n' + msg
                                LOGGER.info(msg)
                    else:
                        f_flag = True
                        self.dom_migrate(self.auth, vm, src_node, self.node)
                        f_flag = True
                        msg = 'Migrating VM ' + domname + ' back to the node ' + self.nodename + ' failed.'
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                else:
                    msg = 'Live Mirgation of VM ' + domname + ' to the Node ' + self.nodename + '. '
                    self.msg += '\n' + msg
                    LOGGER.info(msg)
                    if self.dom_migrate(self.auth, vm, src_node, self.node, 'true'):
                        s_flag = True
                        msg = 'Migrating VM ' + domname + ' back to the node ' + self.nodename + ' Complete.'
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                    else:
                        f_flag = True
                        msg = 'Migrating VM ' + domname + ' back to the node ' + self.nodename + ' Failed.'
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                msg = 'Removing entries for VM ' + domname + ' from VM State History'
                LOGGER.info(msg)
            except Exception as e:
                f_flag = True
                traceback.print_exc()

            self.msg += '\n\nFinished processing VM\n'
            self.msg += '==============================\n'
        if s_flag == True:
            self.status = self.SUCCESS
        if f_flag == True:
            self.status = self.FAILURE
        if s_flag == True and f_flag == True:
            self.status = self.PARTIAL
        if len(vshs) == 0:
            self.status = self.SUCCESS
        msg = 'Finished processing VMs with the Node ' + self.nodename + '. '
        self.msg += '\n' + msg
        LOGGER.info(msg)
        return True


    def dom_fail_over(self, dom_ids, node, new_node, gretry_count, gwait_interval, step, migrated=False, started=False):
        #LOGGER.debug('In dom_fail_over:\ndom_ids, node, new_node, gretry_count, gwait_interval, step, migrated, started  \n%s, %s, %s, %s, %s, %s, %s, %s,' %(ndom_ids, node, new_node, gretry_count, gwait_interval, step, migrated, started))                                     \n%s, %s, %s, %s, %s, %s, %s, %s,' % (dom_ids, node, new_node, gretry_count, gwait_interval, step, migrated, started))
        if new_node is None:
            msg = 'No suitable server. None'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            return dom_ids
        failed_doms = []
        doms = DBSession.query(VM).filter(VM.id.in_(dom_ids)).order_by(VM.ha_priority.desc()).all()
        for dom in doms:
            try:
                dom = DBSession.query(VM).filter(VM.id == dom.id).first()
                domname = dom.name
                msg = 'Maintenance on Node ' + self.nodename + '. ' + 'Processing VM ' + domname
                self.msg += '\n\n' + msg + '.\n'
                self.msg += '==============================\n'
                LOGGER.info(msg)
                new_nodename = new_node.hostname
                new_node = DBSession.query(ManagedNode).filter(ManagedNode.id == new_node.id).first()
                if self.has_local_storage(dom.id, new_node) == True:
                    msg = 'VM ' + domname + ' has local storage. ' + 'Can not migrate to ' + new_nodename
                    self.msg += '\n' + msg
                    LOGGER.info(msg)
                    failed_doms.append(dom.id)
                    migrated = False
                else:
                    msg = 'Migrating VM ' + domname + ' to the node ' + new_nodename
                    self.msg += '\n' + msg
                    LOGGER.info(msg)
                    migrated = False
                    if self.dom_migrate(self.auth, dom, node, new_node):
                        migrated = True
                        msg = 'Migrating VM ' + domname + ' to the node ' + new_nodename + ' successful.'
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                    else:
                        failed_doms.append(dom.id)
                        msg = 'Migrating VM ' + domname + ' to the node ' + new_nodename + ' failed.'
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
            except Exception as e:
                traceback.print_exc()
                msg = 'Failover of VM ' + domname + ' to the node ' + new_nodename + ' failed.' + '\n' + to_str(e)
                self.msg += '\n' + msg
                LOGGER.info(msg)

            self.msg += '\n\nFinished processing VM.\n'
            self.msg += '==============================\n'
        return failed_doms


    def get_group(self, dom=None, node=None, grp=None):
        LOGGER.debug('In get_group')
        group = None
        if grp is None:
            node_ent = None
            if node is None:
                dom_ent = DBSession.query(Entity).filter(Entity.entity_id == dom.id).first()
                node_ent = dom_ent.parents[0]
            else:
                node_ent = DBSession.query(Entity).filter(Entity.entity_id == node.id).first()
            grp_ent = node_ent.parents[0]
            group = DBSession.query(ServerGroup).filter(ServerGroup.id == grp_ent.entity_id).first()
        else:
            group = grp
        return group

    def find_standby_node(self, auth, dom, node=None, grp=None, exclude_ids=[]):
        LOGGER.debug('In find_standby_node: \ndom, node, grp, exclude_ids\n%s, %s, %s, %s' % (dom, node, grp, exclude_ids))
        group = self.get_group(dom, node, grp)
        policy_ctx = dynamic_map()
        policy_ctx.dom = dom
        policy_ctx.exclude_ids = exclude_ids
        if node is not None:
            policy_ctx.node_id = node.id
        new_node = group.getStandByNode(auth, policy_ctx)
        return new_node

    def get_allocation_candidate(self, auth, dom, node=None, grp=None, exclude_ids=[]):
        LOGGER.debug('In get_allocation_candidate: \ndom, node, grp, exclude_ids\n%s, %s, %s, %s' % (dom, node, grp, exclude_ids))

        ex_ids = [ ids for ids in exclude_ids]
        group = self.get_group(dom,node,grp)
        policy_ctx = dynamic_map()
        policy_ctx.dom = dom
        policy_ctx.exclude_ids = ex_ids
        if node is not None:
            policy_ctx.node_id = node.id
        new_node = group.getDomAllocationCandidate(auth,policy_ctx)
        return new_node


    def has_local_storage(self, dom_id, dest_node=None):
        LOGGER.debug('In has_local_storage: \ndom_id, dest_node\n%s, %s' % (dom_id, dest_node))
        has_local_storage = False
        vm = DBSession.query(VM).filter(VM.id == dom_id).first()
        vm_disks = vm.VMDisks
        for disk in vm_disks:
            vm_storage_link = DBSession.query(VMStorageLinks).filter(VMStorageLinks.vm_disk_id == disk.id).first()
            if not vm_storage_link:
                has_local_storage = True
                break
        if has_local_storage ==True and dest_node  is not None:
            vm_conf = vm.get_config()
            if vm_conf is not None:
                des = vm_conf.getDisks()
                if des:
                    for de in des:
                        has_local_storage = False
                        if not dest_node.node_proxy.file_exists(de.filename):
                            msg = 'Disk ' + de.filename + ' of VM ' + vm.name + ' does not exist on ' + dest_node.hostname
                            LOGGER.info(msg)
                            has_local_storage = True
                            break
        return has_local_storage


    def dom_migrate(self, auth, dom, src_node, dest_node, live=None):
        LOGGER.debug('In dom_migrate: \ndom, src_node, dest_node, live\n%s, %s, %s, %s' % (dom, src_node, dest_node, live))
        try:
            tc = TaskCreator()
            dom_ent = DBSession.query(Entity).filter(Entity.entity_id == dom.id).first()
            node_ent = dom_ent.parents[0]
            task_id = tc.migrate_vm(auth, [dom.id], node_ent.entity_id, dest_node.id, live, None, None, constants.Maintenance)
            self.maint_task_context['migrated_vms'].append((dom.id, task_id))
            self.update_maint_task_context()
            wait_time = dom.get_wait_time(constants.MIGRATE)
            wait_time = int(wait_time) + 3
            finished,status = self.wait_for_task_completion(task_id, wait_time)
            if finished == True and status == Task.SUCCEEDED:
                return True
        except Exception as e:
            traceback.print_exc()
            LOGGER.info('Error trying to migrate Virtual Machine,' + dom.name + '. ' + to_str(e))
        return False

    def wait_for_task_completion(self, task_id, wait_time=0):
        LOGGER.debug('In wait_for_task_completion')
        finished = False
        status = Task.STARTED
        for i in range(0, wait_time):
            time.sleep(1)
            transaction.begin()
            task = DBSession.query(Task).filter(Task.task_id == task_id).options(eagerload('result')).first()
            if task.is_finished():
                finished = True
                status = task.result[0].status
                transaction.commit()
                break
            transaction.commit()
        return (finished, status)

    def set_maintenance_mode(self):
        LOGGER.debug('In set_maintenance_mode')
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.node.id).first()
        node.maintenance = True
        DBSession.add(node)
        transaction.commit()

    def reset_maintenance_mode(self):
        LOGGER.debug('In reset_maintenance_mode')
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.node.id).first()
        node.maintenance = False
        node.maintenance_mig_node_id = None
        node.maintenance_operation = 0
        node.maintenance_migrate_back = False
        node.maintenance_user = None
        DBSession.add(node)
        transaction.commit()

    def is_down(self, dom):
        LOGGER.debug('In is_down')
        if dom.is_running():
            return False
        return True

    def dom_start(self, auth, dom, node, retry_count=1, wait_interval=3):
        retry = 0
        dom.node = node
        try:
            wait_interval = float(wait_interval)
        except Exception as e:
            traceback.print_exc()
            LOGGER.info('Error converting wait_interval(' + str(wait_interval) + ') to float ' + 'default to 3')
            wait_interval = 3
        try:
            retry_count = int(retry_count)
        except Exception as e:
            traceback.print_exc()
            LOGGER.info('Error converting retry_count(' + str(retry_count) + ') to int ' + 'default to 3')
            retry_count = 3
        if retry < retry_count:
            try:
                tc = TaskCreator()
                task_id = tc.vm_action(auth, dom.id, node.id, constants.START, constants.CORE, constants.Maintenance)
                LOGGER.info('Trying to start the Virtual Machine:' + dom.name + '. Try:' + str(retry + 1) + '. Task:' + str(task_id))
                wait_time = dom.get_wait_time(constants.START)
                wait_time = int(wait_time) + 3
                finished,status = self.wait_for_task_completion(task_id, wait_time)
                # as status
                if finished == True and status == Task.SUCCEEDED:
                    return True
            except Exception as e:
                traceback.print_exc()
                LOGGER.info('Error trying to start Virtual Machine,' + dom.name + '. ' + to_str(e))
            if retry != retry_count - 1:
                time.sleep(wait_interval)
            retry += 1
        return False

    def dom_pause(self, auth, dom, node):
        dom.node = node
        try:
            tc = TaskCreator()
            task_id = tc.vm_action(auth, dom.id, node.id, constants.PAUSE, constants.CORE)
            LOGGER.info('Trying to pause the Virtual Machine:' + dom.name + '. Task:' + str(task_id))
            wait_time = dom.get_wait_time(constants.PAUSE)
            wait_time = int(wait_time) + 3
            finished,status = self.wait_for_task_completion(task_id, wait_time)
            if finished == True and status == Task.SUCCEEDED:
                return True
        except Exception as e:
            traceback.print_exc()
            LOGGER.info('Error trying to pause Virtual Machine,' + dom.name + '. ' + to_str(e))
        return False
    
    @classmethod
    def getNodeList(self, auth, groupId=None):
        LOGGER.debug('In getNodeList')
        if groupId is None:
            return []
        ent = auth.get_entity(groupId)
        nodelist = []
        if ent is not None:
            child_ents = auth.get_entities(to_unicode(constants.MANAGED_NODE),parent = ent)
            node_ids = [child_ent.entity_id for child_ent in child_ents]
            nodelist = DBSession.query(ManagedNode)\
                        .filter(ManagedNode.id.in_(node_ids)).order_by(ManagedNode.standby_status.desc())\
                        .order_by(ManagedNode.hostname.asc()).all()
            return nodelist
        return []
    @classmethod
    def get_task_result(cls, taskid):
        from stackone.model.services import TaskResult
        return DBSession.query(TaskResult).filter(TaskResult.task_id == taskid).first()



