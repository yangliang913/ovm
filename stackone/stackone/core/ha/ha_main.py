from stackone.core.ha.ha_register import HARegister, HAHistory, HAEvent, HAEventLog, HAStatus
from stackone.core.ha.ha_fence import HAEntityResource
from stackone.core.services.dispatcher import Subscribable
from stackone.core.utils.utils import to_unicode, to_str, dynamic_map, copyToRemote
from stackone.model import DBSession
from stackone.model.Entity import Entity
from stackone.model.Groups import ServerGroup
from stackone.model.ManagedNode import ManagedNode
from stackone.model.VM import VM, VMStorageLinks
from stackone.model.availability import AvailState, StateTransition, VMStateHistory
from stackone.model.Authorization import AuthorizationService
from stackone.model.auth import User
from stackone.model.notification import Notification
from stackone.model.services import Task
from stackone.viewModel.TaskCreator import TaskCreator
from sqlalchemy.orm import eagerload
import stackone.core.utils.constants
from datetime import datetime, timedelta
import logging
import traceback
import time
import transaction
import tg
import os
LOGGER = logging.getLogger('HA')
constants = stackone.core.utils.constants
class HA(Subscribable):
    #PASSED
    conn = None
    notification = u'stackone HA Notification'
    FAILURE = HAEvent.FAILURE
    SUCCESS = HAEvent.SUCCESS
    PARTIAL = HAEvent.PARTIAL
    FAILOVER_SUCCESS = 1
    FAILOVER_FAILURE = 0
    def add_ha_event(self, ev, avail):
        ent = DBSession.query(Entity).filter(Entity.entity_id == ev.entity_id).first()
        if ent.type.name == constants.DOMAIN:
            state = None
            contents = ev.contents
            if contents:
                state = contents.get('state')
            if state not in [VM.SHUTDOWN]:
                return None
                
        sp_ent = self.get_sp_entity(ent)
        group = DBSession.query(ServerGroup).filter(ServerGroup.id == sp_ent.entity_id).first()
        if group.failover == constants.VM_FAILOVER and ent.type.name == constants.MANAGED_NODE:
            return None
            
        node_id = ev.entity_id
        if ent.type.name == constants.DOMAIN:
            parent = ent.parents[0]
            node_id = parent.entity_id
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
        if node and node.maintenance == True:
            LOGGER.info('Server :' + node.hostname + ' is in Maintenance Mode. Skipping HA.')
            return None
            
        ha_event = HAEvent(ev.entity_id, sp_ent.entity_id, avail.avail_state, ev.timestamp)
        DBSession.add(ha_event)
        transaction.commit()
        ha_event_log = HAEventLog(ha_event.event_id, ev.entity_id, to_unicode('HAEvent created.'))
        DBSession.add(ha_event_log)
        transaction.commit()
        return None
        
    #PASSED
    def add_notification(self, user, message):
        notifcn = Notification(None, None, datetime.now(), to_unicode(message), user.user_name, user.email_address, self.notification)
        DBSession.add(notifcn)
        transaction.commit()

    #PASSED
    def change_ha_state(self, ha_reg, state, msg):
        ha_reg.set_ha_state(state)
        ha_reg.set_description(to_unicode(msg))
        DBSession.add(ha_reg)
        ha_history = HAHistory(ha_reg.entity_id, state, to_unicode(msg))
        DBSession.add(ha_history)
        transaction.commit()

    #PASSED
    def change_transient_state(self, entity_id, state, owner):
        allowed,info = StateTransition.is_allowed(entity_id, state, owner)
        return (allowed, info)

    #PASSED
    def check_dom_down(self, dom, node):
        metrics = node.get_metrics()
        running_vms = metrics.keys()
        if dom.name in running_vms:
            return False
        return True

    #PASSED
    def do_fencing(self, node, peer_node):
        if peer_node is None:
            msg = 'Peer node is None. Can not proceed fencing.'
            LOGGER.info(msg)
            return (False, msg)
            
        msg = 'Trying to Fence using ' + peer_node.hostname
        LOGGER.info(msg)
        devices = DBSession.query(HAEntityResource).filter(HAEntityResource.entity_id == node.id).all()
        msg = ''
        if len(devices) == 0:
            msg = 'No Fencing devices configured.'
            print msg
            LOGGER.info(msg)
        success = True
        for device in devices:
            cmd = device.resource.type.fence_method
            locn = device.resource.type.script_location
            stdin_params = []
            env_params = {}
            for param in device.params:
                if device.resource.type.classification == u'Power Fencing Device':
                    if param.field == 'action' and param.value == 'reboot':
                        self.fence_action = 'reboot'
                if param.is_environ == False:
                    stdin_params.append(param.field + '=' + param.value)
                else:   
                    env_params[param.field] = param.value
            for param in device.resource.params:
                stdin_params.append(param.field + '=' + param.value)
            dirname = os.path.dirname(locn)
            try:
                stackone_cache_dir = os.path.join(tg.config.get('stackone_cache_dir'), 'custom/fencing/scripts')
                if not peer_node.node_proxy.file_exists(locn):
                    copyToRemote(locn, peer_node, stackone_cache_dir)
                    dirname = stackone_cache_dir
            except Exception as e:
                traceback.print_exc()
                success = False
                msg += 'Fencing failed using ' + device.resource.name + '\n' + ' Can not copy the fencing script to peer node' + peer_node.hostname + 'Exception:' + to_str(e)
                LOGGER.info(msg)
                
            (out, exit_code) = peer_node.node_proxy.exec_cmd(cmd, dirname, None, stdin_params, cd=True, env=env_params)
            if exit_code != 0:
                success = False
                msg += 'Fencing failed using ' + device.resource.name + '\n' + out
                print 'Fencing failed using ',
                print device.resource.name,
                print '\n',
                print out
                LOGGER.info('Fencing failed using ' + device.resource.name + '\n' + out)
            else:    
                msg += 'Fencing succeeded using ' + device.resource.name + '\n' + out
                print 'Fencing succeeded using ',
                print device.resource.name,
                print '\n',
                print out
                LOGGER.info('Fencing succeeded using ' + device.resource.name + '\n' + out)
            
        return (success, msg)
        
    #PASSED
    def do_peer_ping(self, node, peer):
        dest_dir = os.path.join(tg.config.get('stackone_cache_dir'), 'common/scripts')
        src_script_dir = os.path.abspath(tg.config.get('common_script'))
        ping_script_file = tg.config.get('ping_script')
        src_script_file = os.path.join(src_script_dir, ping_script_file)
        args = ' ' + node.hostname + ' 1'
        cmd = os.path.join(dest_dir, ping_script_file) + args
        out,exit_code = self.execute_script(cmd, src_script_file, dest_dir, peer)
        return (out, exit_code)

    #PASSED
    def dom_migrate(self, auth, dom, src_node, dest_node, live=None):
        try:
            tc = TaskCreator()
            dom_ent = DBSession.query(Entity).filter(Entity.entity_id == dom.id).first()
            node_ent = dom_ent.parents[0]
            task_id = tc.migrate_vm(auth, [dom.id], node_ent.entity_id, dest_node.id, live=live, force=None, all=None, requester=constants.HA)
            self.ha_status_update(self.sp_id, self.event_id, dom.id, task_id, Task.STARTED, constants.MIGRATE)
            wait_time = dom.get_wait_time(constants.MIGRATE)
            wait_time = int(wait_time) + 3
            (finished, status)= self.wait_for_task_completion(task_id, wait_time)
            self.ha_status_update(self.sp_id, self.event_id, dom.id, task_id, status)
            if finished == True and status == Task.SUCCEEDED:
                return True
        except Exception as e:
            traceback.print_exc()
            LOGGER.info('Error trying to migrate Virtual Machine,' + dom.name + '. ' + to_str(e))
            
        return False
        
    
    #PASSED
    def dom_pause(self, auth, dom, node):
        dom.node = node
        try:
            tc = TaskCreator()
            task_id = tc.vm_action(auth, dom.id, node.id, constants.PAUSE, requester=constants.HA)
            self.ha_status_update(self.sp_id, self.event_id, dom.id, task_id, Task.STARTED, constants.PAUSE)
            LOGGER.info('Trying to pause the Virtual Machine:' + dom.name + '. Task:' + str(task_id))
            wait_time = dom.get_wait_time(constants.PAUSE)
            wait_time = int(wait_time) + 3
            (finished, status) = self.wait_for_task_completion(task_id, wait_time)
            self.ha_status_update(self.sp_id, self.event_id, dom.id, task_id, status)
            if finished == True and status == Task.SUCCEEDED:
                return True
        except Exception as e:
            traceback.print_exc()
            LOGGER.info('Error trying to pause Virtual Machine,' + dom.name + '. ' + to_str(e))
        return False
    
        
    #PASSED
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
        while retry < retry_count:
            try:
                tc = TaskCreator()
                task_id = tc.vm_action(auth, dom.id, node.id, constants.START, requester=constants.HA)
                self.ha_status_update(self.sp_id, self.event_id, dom.id, task_id, Task.STARTED, constants.START)
                LOGGER.info('Trying to start the Virtual Machine:' + dom.name + '. Try:' + str(retry + 1) + '. Task:' + str(task_id))
                wait_time = dom.get_wait_time(constants.START)
                wait_time = int(wait_time) + 3
                (finished, status) = self.wait_for_task_completion(task_id, wait_time)
                self.ha_status_update(self.sp_id, self.event_id, dom.id, task_id, status)
                if finished == True and status == Task.SUCCEEDED:
                    return True
            except Exception as e:
                traceback.print_exc()
                LOGGER.info('Error trying to start Virtual Machine,' + dom.name + '. ' + to_str(e))
            if retry != retry_count - 1:
                time.sleep(wait_interval)
            retry += 1
        
        return False
        
    #PASSED
    def execute_script(self, cmd, src, dest_dir, dest_node):
        copyToRemote(src, dest_node, dest_dir)
        out,exit_code = dest_node.node_proxy.exec_cmd(cmd)
        return (out, exit_code)
        
    #PASSED    
    def find_standby_node(self, auth, dom, node=None, grp=None, exclude_ids=[]):
        group = self.get_group(dom, node, grp)
        policy_ctx = dynamic_map()
        policy_ctx.dom = dom
        policy_ctx.exclude_ids = exclude_ids
        if node is not None:
            policy_ctx.node_id = node.id
        new_node = group.getStandByNode(auth, policy_ctx)
        return new_node

    #PASSED
    def get_allocation_candidate(self, auth, dom, node=None, grp=None, exclude_ids=[]):
        ex_ids = [id for id in exclude_ids]
        group =  self.get_group(dom, node, grp)
        policy_ctx = dynamic_map()
        policy_ctx.dom = dom
        policy_ctx.exclude_ids = ex_ids
        if node is not None:
            policy_ctx.node_id = node.id
            
        new_node = group.getDomAllocationCandidate(auth, policy_ctx)
        return new_node        
        
    #PASSED
    def get_group(self, dom=None, node=None, grp=None):
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

    #PASSED
    def get_next_step(self):
        return self.steps.get(self.step, 1)


    #PASSED
    def get_preferred_node(self, dom):
        if dom.preferred_nodeid is not None:
            node = DBSession.query(ManagedNode).filter(ManagedNode.id == dom.preferred_nodeid).filter(ManagedNode.maintenance == False).first()
            if node != None and node.current_state.avail_state == ManagedNode.UP:
                return node

    #PASSED
    def get_sp_entity(self, ent):
        parent = ent.parents[0]
        if parent.type.name == constants.SERVER_POOL:
            return parent
        
        return self.get_sp_entity(parent)

    #PASSED
    def ha_status_update(self, sp_id, event_id, entity_id, task_id, task_status, action=None):
        ha_stat = HAStatus(sp_id, event_id, entity_id, task_id, task_status)
        ha_stat.step_number = self.step
        ha_stat.msg = self.msg
        ha_stat.execution_context = self.execution_context
        ha_stat.failover_status = self.FAILOVER_FAILURE
        if action != None:
            ha_stat.action = action
            
        DBSession.merge(ha_stat)
        transaction.commit()
        return ha_stat

    #PASSED
    def handle_event(self, auth, event_id, entity_id, avail_state, event_time, group_id):
        try:
            processed = False
            status = self.FAILURE
            name = entity_id
            try:
                entity = DBSession.query(Entity).filter(Entity.entity_id == entity_id).options(eagerload('ha')).first()
                name = entity.name
                msg = '\nStart processing HA Event ' + str(event_id) + ' on ' + name + ' generated at ' + str(event_time)
                tot_msg = msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(event_id, entity_id, to_unicode(msg)))
                if entity.type.name == constants.MANAGED_NODE:
                    processed = True
                    node_event = NodeHAEvent(auth, event_id, entity, group_id)
                    if avail_state == ManagedNode.UP:
                        node_event.onNodeUP()
                    else:
                        node_event.onNodeDown()
                    tot_msg += '\n.' + node_event.msg
                    status = node_event.status
                elif entity.type.name == constants.DOMAIN:
                    status = self.SUCCESS
                    if avail_state == VM.SHUTDOWN:
                        (allowed, info) = StateTransition.is_allowed(entity.entity_id, VM.HA_FAILOVER, constants.HA)
                        if allowed == False:
                            raise Exception(constants.NO_OP + '\n' + str(info['msg']))
                        processed = True
                        vm_event = VMHAEvent(auth, event_id, entity, group_id)
                        vm_event.onVMDown()
                        tot_msg += '\n.' + vm_event.msg
                        status = vm_event.status
            except Exception as e:
                status = self.FAILURE
                traceback.print_exc()
                msg = to_unicode('Error processing HA Event on (handle_event) ' + name + '.' + str(e))
                tot_msg += '\n.' + msg
                DBSession.add(HAEventLog(event_id, entity_id, msg))
                LOGGER.error(msg)
        finally:
            msg = 'Finished processing HA Event ' + str(event_id) + ' on ' + name + '.'
            tot_msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(event_id, entity_id, to_unicode(msg)))
            transaction.commit()
            StateTransition.is_allowed(entity_id, None, constants.HA)
            if processed == True:
                self.notify_user(auth, event_id)
        return (tot_msg, status)
        

    #PASSED
    def has_local_storage(self, dom_id, dest_node=None):
        has_local_storage = False
        vm = DBSession.query(VM).filter(VM.id == dom_id).first()
        vm_disks = vm.VMDisks
        for disk in vm_disks:
            vm_storage_link = DBSession.query(VMStorageLinks).filter(VMStorageLinks.vm_disk_id == disk.id).first()
            if not vm_storage_link:
                has_local_storage = True
                break
                
        if has_local_storage == True and dest_node is not None:
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
        

    #PASSED
    def is_down(self, dom):
        if dom.is_running():
            return False
        return True

    #PASSED
    def node_up_action(self, event_id, node_id):
        task_ids = []
        try:
            adm_usr = DBSession.query(User).filter(User.user_name == u'admin').first()
            auth = AuthorizationService(adm_usr)
            node_ent = DBSession.query(Entity).filter(Entity.entity_id == node_id).first()
            if node_ent: 
                sp_ent = self.get_sp_entity(node_ent)
                node_event = NodeHAEvent(auth, event_id, node_ent, sp_ent.entity_id)
                node_event.wait_for_sync()
                tc = TaskCreator()
                vm_ids = [d.entity_id for d in node_ent.children]
                doms = DBSession.query(VM).filter(VM.id.in_(vm_ids)).all()
                for dom in doms: 
                    config = dom.get_config()
                    if config and config.get('auto_start_vm') == 1:
                        start_task = DBSession.query(Task).filter(Task.task_id == dom.start_taskid).first()
                        if start_task:
                            if start_task.is_finished != True:
                                continue
                        else:
                            tid = tc.vm_action(auth, dom.id, node_id, constants.START)
                            task_ids.append(tid)
                            
        except Exception as e:
            traceback.print_exc()
            
        return task_ids
        
    #PASSED
    def notify(self, ev):
        try:
            transaction.commit()
            ha = DBSession.query(HARegister).filter(HARegister.entity_id == ev.entity_id).first()
            avail = DBSession.query(AvailState).filter(AvailState.entity_id == ev.entity_id).first()
            if ha and ha.registered == True:
                if avail and avail.monit_state == AvailState.MONITORING:
                    self.add_ha_event(ev, avail)
                else:
                    print 'Entity %s is not in Monitoring state.' % ev.entity_id
                    LOGGER.info('Entity %s is not in Monitoring state.' % ev.entity_id)
            else:
                print 'Entity %s is not registered for HA.' % ev.entity_id
                LOGGER.info('Entity %s is not registered for HA.' % ev.entity_id)
                entity = DBSession.query(Entity).filter(Entity.entity_id == ev.entity_id).first()
                if entity is None:
                    LOGGER.info('Can not find the entity for .' + ev.entity_id)
                    return 
                    
                if entity.type.name == constants.MANAGED_NODE:
                    if avail and avail.monit_state == AvailState.MONITORING:
                        if avail.avail_state == ManagedNode.DOWN:
                            LOGGER.info('Marking VMs as down and Adding VM states.')
                            VMStateHistory.add_vm_states(ev.entity_id)
                        else:
                            LOGGER.info('Removing VM states.')
                            VMStateHistory.remove_node_states(ev.entity_id)
                            self.node_up_action(ev.event_id, ev.entity_id)
        except Exception as e:
            traceback.print_exc()
            print 'Exception: ',
            print e

    #PASSED
    def notify_user(self, auth, event_id):
        logs = DBSession.query(HAEventLog).filter(HAEventLog.event_id == event_id).order_by(HAEventLog.id.asc()).all()
        message = ''
        for log in logs:
            message += str(log.timestamp) + ' : ' + log.msg + '\n'
        self.add_notification(auth.user, message)

    #PASSED
    def print_step(self, num=0):
        return None


    #PASSED
    def resume_event(self, auth, event_id, entity_id, avail_state, event_time, ha_state, group_id):
        try:
            processed = False
            status = self.FAILURE
            name = entity_id
            try:
                entity = DBSession.query(Entity).filter(Entity.entity_id == entity_id).options(eagerload('ha')).first()
                name = entity.name
                msg = '\nResume processing HA Event ' + str(event_id) + ' on ' + name + ' generated at ' + str(event_time)
                tot_msg = msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(event_id, entity_id, to_unicode(msg)))
                
                if entity.type.name == constants.MANAGED_NODE:
                    processed = True
                    node_event = NodeHAEvent(auth, event_id, entity, group_id, ha_state)
                    if avail_state == ManagedNode.UP:
                        node_event.resumeNodeUP()
                    else:
                        node_event.resumeNodeDown()
                    
                    tot_msg += '\n.' + node_event.msg
                    status = node_event.status
                    
                elif entity.type.name == constants.DOMAIN:
                    status = self.SUCCESS
                    if avail_state == VM.SHUTDOWN:
                        (allowed, info)= StateTransition.is_allowed(entity.entity_id, VM.HA_FAILOVER, constants.HA)
                        if allowed == False:
                            raise Exception(constants.NO_OP + '\n' + str(info['msg']))
                    
                    processed = True
                    vm_event = VMHAEvent(auth, event_id, entity, group_id, ha_state)
                    vm_event.resumeVMDown()
                    tot_msg += '\n.' + vm_event.msg
                    status = vm_event.status
                    
            except Exception as e:
                status = self.FAILURE
                traceback.print_exc()
                msg = 'Error processing HA Event on ' + name + '.' + str(e)
                tot_msg += '\n.' + msg
                DBSession.add(HAEventLog(event_id, entity_id, to_unicode(msg)))
                LOGGER.error(msg)
                
        finally:
            msg = 'Finished processing HA Event ' + str(event_id) + ' on ' + name + '.'
            tot_msg += '\n.' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(event_id, entity_id, to_unicode(msg)))
            transaction.commit()
            StateTransition.is_allowed(entity_id, None, constants.HA)
            if processed == True:
                self.notify_user(auth, event_id)
        
        return (tot_msg, status)

    #PASSED
    def send_nw_service_host_down_email(self, csep):
        msg = 'Network Service Host: ' + self.nodename + ' went down,' + ' network service for all Virtual Machines for the ' + constants.IAAS + ':' + csep.name + ' would be affected.'
        self.add_notification(self.auth.user, msg)

    #PASSED
    def update_execution_context(self):
        DBSession.query(HAStatus).filter(HAStatus.event_id == self.event_id).update(values=dict(execution_context=self.execution_context))
        transaction.commit()

    #PASSED
    def update_failover_status(self, entity_id, failover_status):
        DBSession.query(HAStatus).filter(HAStatus.event_id == self.event_id).filter(HAStatus.entity_id == entity_id).update(values=dict(failover_status=failover_status, execution_context=self.execution_context))
        transaction.commit()

    #PASSED
    def update_step_to_next(self):
        self.step = self.steps.get(self.step, 1)

    #PASSED
    def vm_status_check(self, dom, action, result=None):
        try:
            res = dom.check_action_status(action, result)
            return res
        except Exception as e:
            traceback.print_exc()
            return False

    #PASSED
    def wait_for_node_up(self, node):
        now = datetime.now()
        dif = timedelta(seconds=180)
        end = now + dif
        interval = 30
        msg = 'Waiting for Node ' + self.nodename + ' to come UP.'
        self.msg += '\n' + msg
        LOGGER.info(msg)
        node_id = node.id
        while datetime.now() < end:
            transaction.begin()
            avail = DBSession.query(AvailState).filter(AvailState.entity_id == node_id).first()
            if avail.avail_state == ManagedNode.UP:
                msg = 'Node :' + self.nodename + ' UP is detected. '
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                transaction.commit()
                return True
                
            transaction.commit()
            time.sleep(interval)
        
        msg = 'Node ' + self.nodename + ' did not come UP in 180 seconds.'
        self.msg += '\n' + msg
        LOGGER.info(msg)
        return False
        
    #PASSED
    def wait_for_task_completion(self, task_id, wait_time=0):
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


        
class NodeHAEvent(HA):
    CONFIRMATION = 10
    FENCING = 20
    MIGRATE_TO_STANDBY = 30
    START_IN_STANDBY = 40
    PAUSE_IN_STANDBY = 50
    MIGRATE_TO_CANDIDATE = 60
    START_IN_CANDIDATE = 70
    PAUSE_IN_CANDIDATE = 80
    def __init__(self, auth, event_id, entity, group_id, ha_state=None):
        self.auth = auth
        self.event_id = event_id
        self.entity = entity
        self.entity_id = entity.entity_id
        self.nodename = entity.name
        self.ha_state = ha_state
        self.msg = ''
        self.status = self.FAILURE
        self.sp_id = group_id
        self.step = self.CONFIRMATION
        self.execution_context = {}
        self.fence_action = None
        self.steps = {self.CONFIRMATION: self.FENCING, self.FENCING: self.MIGRATE_TO_STANDBY, self.MIGRATE_TO_STANDBY: self.START_IN_STANDBY, self.START_IN_STANDBY: self.PAUSE_IN_STANDBY, self.PAUSE_IN_STANDBY: self.MIGRATE_TO_CANDIDATE, self.MIGRATE_TO_CANDIDATE: self.START_IN_CANDIDATE, self.START_IN_CANDIDATE: self.PAUSE_IN_CANDIDATE}

    #PASSED
    def check_nw_service_host(self):
        msg = 'Checking if Node ' + self.nodename + ' is active Network Service Host for any ' + constants.IAAS
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        csep = CSEP.is_active_host(self.entity_id)
        if not csep:
            msg = 'Node ' + self.nodename + ' is not an active Network Service Host for any ' + constants.IAAS
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            return True
            
        msg = 'Node ' + self.nodename + ' is an active Network Service Host for ' + constants.IAAS + ': ' + csep.name
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        new_node = csep.get_new_nw_service_host()
        if not new_node:
            msg = 'No other Network Service Host is defined for ' + constants.IAAS + ': ' + csep.name
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            self.send_nw_service_host_down_email(csep)
            return False
            
        if new_node.id == self.entity_id:
            msg = 'Network Service Host ' + self.nodename + ' for ' + constants.IAAS + ': ' + csep.name + 'is Up.'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            self.send_nw_service_host_down_email(csep)
            return False
            
        msg = 'Set active Network Service Host as ' + new_node.hostname + ' for ' + constants.IAAS + ': ' + csep.name
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        DBSession.query(InternalNetworkService).filter(InternalNetworkService.server_id == self.entity_id).filter(InternalNetworkService.csep_id == csep.id).update(values=dict(active=False))
        DBSession.query(InternalNetworkService).filter(InternalNetworkService.server_id == new_node.id).filter(InternalNetworkService.csep_id == csep.id).update(values=dict(active=True))
        transaction.commit()
        msg = 'Submit Network Service Host Sync task for ' + constants.IAAS + ': ' + csep.name
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        result = new_node.network_sync(self.auth, LOGGER)
        msg = 'Network Service Host Sync task for ' + constants.IAAS + ': ' + csep.name + ' is over.'
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        transaction.commit()
        return result

    #PASSED
    def check_pending_task(self):
        ha_stat = DBSession.query(HAStatus).filter(HAStatus.event_id == self.event_id).filter(HAStatus.task_status == Task.STARTED).first()
        if ha_stat:
            exec_context = ha_stat.execution_context
            dom_id = exec_context.get('current_dom_id', None)
            dom = DBSession.query(VM).filter(VM.id == dom_id).first()
            status = False
            if dom is not None:
                wait_time = dom.get_wait_time(ha_stat.action)
                self.step = ha_stat.step_number
                self.msg = ha_stat.msg
                self.execution_context = ha_stat.execution_context
                (finished, status)= self.wait_for_task_completion(ha_stat.task_id, wait_time)
                self.ha_status_update(self.sp_id, self.event_id, ha_stat.entity_id, ha_stat.task_id, status)
            return (status, ha_stat.step_number, ha_stat.msg, ha_stat)
        ha_stat = DBSession.query(HAStatus).filter(HAStatus.event_id == self.event_id).order_by(HAStatus.timestamp.desc()).first()
        if ha_stat:
            self.execution_context = ha_stat.execution_context
            return (ha_stat.task_status, ha_stat.step_number, ha_stat.msg, ha_stat)
        return (False, None, '', None)
        

    #PASSED
    def dom_fail_over(self, dom_ids, node, new_node, gretry_count, gwait_interval, step, migrated=False, started=False):
        if new_node is None:
            msg = 'No suitable server. None'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            return dom_ids
        failed_doms = []
        doms = DBSession.query(VM).filter(VM.id.in_(dom_ids)).order_by(VM.ha_priority.desc()).all()
        self.print_step(1617)
        for dom in doms:
            try:
                self.step = step
                dom = DBSession.query(VM).filter(VM.id == dom.id).first()
                domname = dom.name
                msg = 'Fail-over on Node ' + self.nodename + '. ' + 'Processing VM ' + domname
                self.msg += '\n\n' + msg + '.\n'
                self.msg += '==============================\n'
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                new_nodename = new_node.hostname
                new_node = DBSession.query(ManagedNode).filter(ManagedNode.id == new_node.id).first()
                (was_running, was_paused) = (False, False)
                avail = VMStateHistory.get_vm_state(node.id, dom.id)
                if avail and avail.monit_state == AvailState.MONITORING:
                    was_running = True
                    if avail.avail_state == VM.PAUSED:
                        was_paused = True
                        
                self.execution_context['current_node_id'] = new_node.id
                self.execution_context['current_dom_id'] = dom.id
                self.execution_context['was_running'] = was_running
                self.execution_context['was_paused'] = was_paused

                if self.get_next_step() in [self.MIGRATE_TO_STANDBY, self.MIGRATE_TO_CANDIDATE]:
                    self.update_step_to_next()
                    if self.has_local_storage(dom.id, new_node) == True:
                        msg = 'VM ' + domname + ' has local storage. ' + 'Can not migrate to ' + new_nodename
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                        failed_doms.append(dom.id)
                        migrated = False
                    else:
                        msg = 'Migrating VM ' + domname + ' to the node ' + new_nodename
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                        migrated = False
                        
                        if self.dom_migrate(self.auth, dom, node, new_node):
                            migrated = True
                            msg = 'Migrating VM ' + domname + ' to the node ' + new_nodename + ' successful.'
                            self.msg += '\n' + msg
                            LOGGER.info(msg)
                            if was_running == False:
                                self.update_failed_doms(dom.id)
                        else:
                            failed_doms.append(dom.id)
                            msg = 'Migrating VM ' + domname + ' to the node ' + new_nodename + ' failed.'
                            self.msg += '\n' + msg
                            LOGGER.info(msg)
                            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                        
                self.print_step(1674)
                if self.get_next_step() in [self.START_IN_STANDBY, self.START_IN_CANDIDATE]:
                    self.update_step_to_next()
                    if migrated == True:
                        msg = ' VM ' + domname + ' was Running = ' + str(was_running)
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                        
                        if was_running:
                            msg = 'Trying to start VM ' + domname + ' on ' + new_nodename
                            self.msg += '\n' + msg
                            LOGGER.info(msg)
                            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                            retry_count = dom.get_attribute_value(constants.retry_count, gretry_count)
                            wait_interval = dom.get_attribute_value(constants.wait_interval, gwait_interval)
                            started = False
                            new_node = DBSession.query(ManagedNode).filter(ManagedNode.id == new_node.id).first()
                            
                            if self.dom_start(self.auth, dom, new_node, retry_count, wait_interval) == True:
                                msg = 'Successfully started VM ' + domname + ' on ' + new_nodename
                                self.msg += '\n' + msg
                                LOGGER.info(msg)
                                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                                started = True
                                self.update_failed_doms(dom.id)
                            else:    
                                failed_doms.append(dom.id)
                                started = False
                                msg = 'Failed starting VM ' + domname + ' on ' + new_nodename
                                self.msg += '\n' + msg
                                LOGGER.info(msg)
                                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))

                                
                self.print_step(1710)
                if self.get_next_step() in [self.PAUSE_IN_STANDBY, self.PAUSE_IN_CANDIDATE]:
                    self.update_step_to_next()
                    if started == True:
                        msg = ' VM ' + domname + ' was Paused = ' + str(was_paused)
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                        
                        if was_paused:
                            msg = 'Trying to pause VM ' + domname + ' on ' + new_nodename
                            self.msg += '\n' + msg
                            LOGGER.info(msg)
                            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                            
                            if self.dom_pause(self.auth, dom, new_node) == True:
                                msg = 'Successfully paused VM ' + domname + ' on ' + new_nodename
                                self.msg += '\n' + msg
                                LOGGER.info(msg)
                                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                                self.update_failed_doms(dom.id)
                            else:    
                                msg = 'Failed pausing VM ' + domname + ' on ' + new_nodename
                                self.msg += '\n' + msg
                                LOGGER.info(msg)
                                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                            
            except Exception as e:
                traceback.print_exc()
                msg = 'Failover of VM ' + domname + ' to the node ' + new_nodename + ' failed.' + '\n' + to_str(e)
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            
            self.msg += '\n\nFinished processing VM.\n'
            self.msg += '==============================\n'
            
        return failed_doms
        

    #PASSED
    def down_confirmation(self, node_ha, grpid, grpname):
        msg = 'Confirm the Node ' + self.nodename + ' is Down. '
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        self.change_ha_state(node_ha, HARegister.DOWN_CONFIRMATION, 'Checking if node is Down.')
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.entity_id).first()
        status = node.heartbeat()
        if status and status[0] == ManagedNode.UP:
            msg = 'Node ' + self.nodename + ' is not DOWN. Returning...'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            self.status = self.SUCCESS
            return False
            
        grp = DBSession.query(ServerGroup).filter(ServerGroup.id == grpid).first()
        msg = 'Trying to peer ping to ' + self.nodename + '. '
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        peer_node = grp.get_peer_node([node.id])
        if peer_node is None:
            VMStateHistory.add_vm_states(self.entity_id)
            msg = 'No UP nodes found in the serverpool ' + grpname + '. Returning. Can not proceed Failover.'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            return False
        
        node_shutdown_time = 180
        try:
            node_shutdown_time = int(tg.config.get(constants.node_shutdown_time))
        except Exception as e:
            print 'Exception: ',
            print e
        
        now = datetime.now()
        dif = timedelta(seconds=node_shutdown_time)
        end = now + dif
        ping_interval = 10
        try:
            ping_interval = int(tg.config.get('ping_interval', '10'))
        except Exception as e:
            print 'Exception: ',
            print e
        
        i = 0
        exit_code = 1
        while datetime.now() < end:
            i += 1
            msg = 'Peer Ping Try:' + str(i)
            LOGGER.info(msg)
            (out, exit_code) = self.do_peer_ping(node, peer_node)
            if exit_code != 0:
                break
            
            msg = 'Peer Ping Try:' + str(i) + ' is Success.'
            LOGGER.info(msg)
            time.sleep(ping_interval)
        
        if exit_code == 0:
            msg = 'Node ' + self.nodename + ' is not DOWN. Tried Peer Ping ' + str(i) + ' time(s). Returning...'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            node.current_state.avail_state = ManagedNode.UP
            DBSession.add(node)
            self.status = self.SUCCESS
            return False
        
        msg = 'Node ' + self.nodename + ' is DOWN. Peer Ping Failed.'
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        VMStateHistory.add_vm_states(self.entity_id)
        return True
        

    #PASSED
    def fail_over(self, node_ha, grpid, grpname, tried_sb_nodes=[], failed_doms=[], dom_ids=[]):
        (allowed, info) = self.change_transient_state(self.entity_id, ManagedNode.DOWN_FAILOVER, constants.HA)
        if allowed == False:
            raise Exception(constants.NO_OP + '\n' + str(info['msg']))
        self.change_ha_state(node_ha, HARegister.FAIL_OVER, 'Starting migrating vms.')
        self.check_nw_service_host()
        msg = 'Starting Fail-over on Node ' + self.nodename + '. Checking for VMs.'
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        self.print_step(1476)
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.entity_id).first()
        grp = DBSession.query(ServerGroup).filter(ServerGroup.id == grpid).first()
        gretry_count = grp.getAttributeValue(constants.retry_count, 3)
        gwait_interval = grp.getAttributeValue(constants.wait_interval, 3)
        self.execution_context['failed_doms'] = failed_doms
        self.start_one_ps_down_server(grp)
        
        if self.get_next_step() == self.MIGRATE_TO_STANDBY:
            if grp.use_standby == True:
                while len(failed_doms) > 0:
                    self.step = self.FENCING
                    msg = 'Finding standby node.'
                    self.msg += '\n' + msg
                    LOGGER.info(msg)
                    DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                    new_node = self.find_standby_node(self.auth, None, node, exclude_ids=tried_sb_nodes)
                    if new_node is None:
                        msg = 'All standby nodes are exhausted.'
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                        self.step = self.PAUSE_IN_STANDBY
                        break
                        
                    failed_doms = self.dom_fail_over(failed_doms, node, new_node, gretry_count, gwait_interval, self.FENCING)
                    tried_sb_nodes.append(new_node.id)
                    self.execution_context['tried_sb_nodes'] = tried_sb_nodes
                    self.execution_context['failed_doms'] = failed_doms
                    self.update_execution_context()
            else:
                self.step = self.PAUSE_IN_STANDBY
                
        self.print_step(1504)
        tot_failed = failed_doms
        tmp_failed_doms = [d for d in failed_doms]
        if len(failed_doms) > 0 and self.get_next_step() == self.MIGRATE_TO_CANDIDATE:
            tot_failed = []
            for domid in tmp_failed_doms:
                self.step = self.PAUSE_IN_STANDBY
                dom = DBSession.query(VM).filter(VM.id == domid).first()
                domname = dom.name
                msg = domname + 'Starting initial placement for '
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                new_node = self.get_allocation_candidate(self.auth, dom, node)
                failed = self.dom_fail_over([domid], node, new_node, gretry_count, gwait_interval, self.PAUSE_IN_STANDBY)
                if len(failed) == 1:
                    tot_failed.append(failed[0])
                
        
        if len(tot_failed) > 0:
            doms = DBSession.query(VM).filter(VM.id.in_(tot_failed)).all()
            domnames = [d.name for d in doms]
            msg = 'Failed to migrate following VMs'+to_str(domnames)
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        else:
            self.status = self.SUCCESS
            msg = 'Successfully migrated all VMs'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            
        if len(tot_failed) != 0 and len(tot_failed) < len(dom_ids):
            self.status = self.PARTIAL
            
        return True
        

    #PASSED
    def failover_complete(self, node_ha, msg, state):
        self.change_ha_state(node_ha, HARegister.FAILOVER_COMPLETE, msg)
        self.change_transient_state(self.entity_id, None, constants.HA)
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        self.msg += '\n' + msg

    #PASSED
    def onNodeDown(self):
        node_ha = self.entity.ha
        grp_ent = self.entity.parents[0]
        grpid = grp_ent.entity_id
        grpname = grp_ent.name
        LOGGER.info('======================START NODE DOWN============================ ')
        msg = 'Start processing Node Down Event on ' + self.nodename
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        self.msg += '\n\nConfirm the Node is down.\n'
        self.msg += '==============================\n'
        if self.down_confirmation(node_ha, grpid, grpname) != True:
            return self.msg
        LOGGER.info('_____________--Node Fencing____________')   
        self.msg += '\n\nStart Node Fencing.\n'
        self.msg += '==============================\n'
        if self.stonith(node_ha, grpid) != True:
            return self.msg
        LOGGER.info('_____________Start Node Failover____________')      
        self.msg += '\n\nStart Node Failover.\n'
        self.msg += '==============================\n'
        dom_ids = [child.entity_id for child in self.entity.children]
        doms = DBSession.query(VM).filter(VM.id.in_(dom_ids)).order_by(VM.ha_priority.desc()).all()
        failed_doms = [d.id for d in doms]
        dom_ids = failed_doms
        self.execution_context['total_dom_ids'] = dom_ids
        if self.fail_over(node_ha, grpid, grpname, tried_sb_nodes=[], failed_doms=failed_doms, dom_ids=dom_ids) != True:
            return self.msg
        LOGGER.info('_____________Post failover processing____________')   
        self.msg += '\n\nPost failover processing.\n'
        self.msg += '==============================\n'
        self.post_fail_over(node_ha)
        self.failover_complete(node_ha, msg, ManagedNode.DOWN_FAILOVER_COMPLETE)
        self.msg += '\n' + msg
        LOGGER.info('==================1111====END NODE DOWN============================ ')


    #PASSED
    def onNodeUP(self):
        node_ha = self.entity.ha
        grp_ent = self.entity.parents[0]
        grpid = grp_ent.entity_id
        grpname = grp_ent.name
        LOGGER.info('======================START NODE UP============================ ')
        msg = 'Start processing Node Up Event on ' + self.nodename
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        self.msg += '\n\nConfirm the Node is up.\n'
        self.msg += '==============================\n'
        if self.up_confirmation(node_ha, grpid, grpname) != True:
            return self.msg
            
        res = self.wait_for_sync()
        self.msg += '\n\nStart Node Failover.\n'
        self.msg += '==============================\n'
        self.up_fail_over(node_ha, grpid)
        self.msg += '\n\nPost failover processing.\n'
        self.msg += '==============================\n'
        self.up_post_fail_over(node_ha, grpid, grpname)
        msg = 'Node up event completed for ' + self.nodename
        self.failover_complete(node_ha, msg, ManagedNode.UP_FAILOVER_COMPLETE)
        self.msg += '\n' + msg
        LOGGER.info('======================END NODE UP============================ ')

        
    #PASSED
    def post_fail_over(self, node_ha):
        self.change_ha_state(node_ha, HARegister.POST_FAILOVER, 'Post failover phase.')
        transaction.commit()
        return True

    #PASSED
    def resumeNodeDown(self):
        node_ha = self.entity.ha
        ha_state = self.ha_state
        grp_ent = self.entity.parents[0]
        grpid = grp_ent.entity_id
        grpname = grp_ent.name
        LOGGER.info('======================START NODE DOWN============================ ')
        msg = 'Resuming Node Down Event on ' + self.nodename
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        if ha_state in [HARegister.NOT_ACTIVE, HARegister.DOWN_CONFIRMATION, HARegister.STONITH]:
            self.msg += '\n\nConfirm the Node is down.\n'
            self.msg += '==============================\n'
            if self.down_confirmation(node_ha, grpid, grpname) != True:
                return self.msg
            self.msg += '\n\nStart Node Fencing.\n'
            self.msg += '==============================\n'
            if self.stonith(node_ha, grpid) != True:
                return self.msg
            ha_state = HARegister.FAIL_OVER
        
        if ha_state == HARegister.FAIL_OVER:
            self.msg += '\n\nStart Node Failover.\n'
            self.msg += '==============================\n'
            status,self.step,self.msg,stat = self.check_pending_task()
            #self.msg = self
            self.msg += '\n' + msg
            dom_id = self.execution_context.get('current_dom_id', None)
            current_node_id = self.execution_context.get('current_node_id', None)
            was_running = self.execution_context.get('was_running', False)
            was_paused = self.execution_context.get('was_paused', False)
            (dom_fail_over, migrated, started) = (False, False, False)
            node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.entity_id).first()
            dom = DBSession.query(VM).filter(VM.id == dom_id).first()
            new_node = DBSession.query(ManagedNode).filter(ManagedNode.id == current_node_id).first()
            grp = DBSession.query(ServerGroup).filter(ServerGroup.id == self.sp_id).first()
            gretry_count = grp.getAttributeValue(constants.retry_count, 3)
            gwait_interval = grp.getAttributeValue(constants.wait_interval, 3)
            domname = ''
            if dom:
                domname = dom.name
                
            if self.step in [self.MIGRATE_TO_STANDBY, self.MIGRATE_TO_CANDIDATE] and status == Task.SUCCEEDED:
                migrated = True
                msg = 'Migrating VM ' + domname + ' successful.'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                if was_running == False:
                    self.update_failed_doms(dom.id)
                else:
                    dom_fail_over = True
            else:
                if self.step in [self.START_IN_STANDBY, self.START_IN_CANDIDATE] and status == Task.SUCCEEDED:
                    msg = 'Successfully started VM ' + domname
                    self.msg += '\n' + msg
                    LOGGER.info(msg)
                    DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                    started = True
                    self.update_failed_doms(dom.id)
                    if was_paused == True:
                        dom_fail_over = True
                else:
                    if self.step in [self.PAUSE_IN_STANDBY, self.PAUSE_IN_CANDIDATE] and status == Task.SUCCEEDED:
                        msg = 'Successfully paused VM ' + domname
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            if dom_fail_over == True:
                self.dom_fail_over([dom_id], node, new_node, gretry_count, gwait_interval, self.step, migrated=migrated, started=started)
            tried_sb_nodes = self.execution_context.get('tried_sb_nodes', [])
            failed_doms = self.execution_context.get('failed_doms', [])
            dom_ids = self.execution_context.get('total_dom_ids', [])
            
            if dom_ids == []:
                failed_doms = [child.entity_id for child in self.entity.children]
                dom_ids = failed_doms
                
            self.step = self.FENCING
            if self.fail_over(node_ha, grpid, grpname, tried_sb_nodes=tried_sb_nodes, failed_doms=failed_doms, dom_ids=dom_ids) != True:
                return self.msg
                
            ha_state = HARegister.POST_FAILOVER
            
        if ha_state == HARegister.POST_FAILOVER:
            self.msg += '\n\nPost failover processing.\n'
            self.msg += '==============================\n'
            self.post_fail_over(node_ha)
            
        msg = 'Node Down event completed for ' + self.nodename
        self.failover_complete(node_ha, msg, ManagedNode.DOWN_FAILOVER_COMPLETE)
        self.msg += '\n' + msg
        LOGGER.info('======================END NODE DOWN============================ ')
        return 

        
    ######################
    def resumeNodeUP(self):
        node_ha = self.entity.ha
        ha_state = self.ha_state
        grp_ent = self.entity.parents[0]
        grpid = grp_ent.entity_id
        grpname = grp_ent.name
        LOGGER.info('======================START NODE UP============================ ')
        msg = 'Resuming Node Up Event on ' + self.nodename
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        if ha_state in [HARegister.NOT_ACTIVE, HARegister.DOWN_CONFIRMATION]:
            self.msg += '\n\nConfirm the Node is up.\n'
            self.msg += '==============================\n'
            if self.up_confirmation(node_ha, grpid, grpname) != True:
                return self.msg
            ha_state = HARegister.FAIL_OVER
        if ha_state == HARegister.FAIL_OVER:
            status,self.step,self.msg,stat = self.check_pending_task()
            self.msg = self
            self.msg += '\n' + msg
            if stat is not None:
                dom_id = stat.entity_id
                dom = DBSession.query(VM).filter(VM.id == dom_id).first()
                msg = 'Removing entries for VM ' + dom.name + ' from VM State History'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                VMStateHistory.remove_vm_states(self.entity_id, dom_id)
                if status == Task.SUCCEEDED:
                    self.update_failover_status(dom_id, HA.FAILOVER_SUCCESS)
            self.msg += '\n\nStart Node Failover.\n'
            self.msg += '==============================\n'
            self.up_fail_over(node_ha, grpid)
            ha_state = HARegister.POST_FAILOVER
        if ha_state == HARegister.POST_FAILOVER:
            self.msg += '\n\nPost failover processing.\n'
            self.msg += '==============================\n'
            self.up_post_fail_over(node_ha, grpid, grpname)
        msg = 'Node up event completed for ' + self.nodename
        self.failover_complete(node_ha, msg, ManagedNode.UP_FAILOVER_COMPLETE)
        self.msg += '\n' + msg
        LOGGER.info('======================END NODE UP============================ ')
        return None
        

    #PASSED
    def start_one_ps_down_server(self, grp):
        from stackone.model.DWM import DWMManager, SPDWMPolicy, DWM
        adm_usr = DBSession.query(User).filter(User.user_name == u'admin').first()
        auth = AuthorizationService(adm_usr)
        standby_nodes = grp.get_standby_nodes()
        
        if not standby_nodes:
            current_policy = SPDWMPolicy.get_sp_current_policy(self.sp_id)
            if current_policy == DWMManager.POWER_SAVING:
                dwm = DBSession.query(DWM).filter(DWM.sp_id == self.sp_id).filter(DWM.policy == current_policy).first()
                server_ids = DWMManager.find_nodes_below_upper_threshold(self.sp_id, dwm.data_period, dwm.upper_threshold)
                if not server_ids:
                    (started_server_ids, msg) = SPDWMPolicy.ps_start_down_nodes(auth, self.sp_id, server_limit=1)
                    if started_server_ids:
                        dest_node = DBSession.query(ManagedNode).filter(ManagedNode.id == started_server_ids[0]).first()
                        msg = 'Server ' + dest_node.hostname + ' started to make space for HA failover. '
                        LOGGER.info(msg)
                        self.msg += '\n' + msg
                    else:
                        msg = 'Can not start Node which were shudown ' + 'during POWERSAVE OR No down Node to start.'
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                else:
                    msg = 'Nodes are available with utilization less than POWERSAVE upper threshold.\n' + 'So no need to start Node which were shudown during POWERSAVE '
                    self.msg += '\n' + msg
                    LOGGER.info(msg)
            else:
                msg = 'Current policy is not %s.So no need to start Node which were shudown during POWERSAVE' % DWMManager.POWER_SAVING
                self.msg += '\n' + msg
                LOGGER.info(msg)
        else:   
            msg = 'Standby nodes exists.So no need to start Node which were shudown during POWERSAVE'
            self.msg += '\n' + msg
            LOGGER.info(msg)
        

    #PASSED
    def stonith(self, node_ha, grpid):
        (allowed, info) = self.change_transient_state(self.entity_id, ManagedNode.FENCE, constants.HA)
        if allowed == False:
            raise Exception(constants.NO_OP + '\n' + str(info['msg']))
        self.update_step_to_next()
        msg = 'Confirmed the Node ' + self.nodename + ' is Down. Beginning STONITH '
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        self.change_ha_state(node_ha, HARegister.STONITH, 'Node is Down. Beginning STONITH')
        msg = 'Start Fencing on Node ' + self.nodename + '. '
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.entity_id).first()
        grp = DBSession.query(ServerGroup).filter(ServerGroup.id == grpid).first()
        peer_node = grp.get_peer_node([node.id])
        success = self.do_fencing(node, peer_node)
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        if success == False and peer_node is not None:
            peer_node = grp.get_peer_node([node.id, peer_node.id])
            if peer_node is not None:
                success = self.do_fencing(node, peer_node)
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            if success == False:
                self.change_transient_state(self.entity_id, ManagedNode.FENCE_FAILED, constants.HA)
                msg = 'Fencing Failed on Node ' + self.nodename + '. ' + ' Can not proceed Failover.'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                return False
        msg = 'Finished Fencing on Node ' + self.nodename + '. '
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        self.change_transient_state(self.entity_id, ManagedNode.FENCE_SUCCEEDED, constants.HA)
        ha_wait_for_node_up = False
        try:
            ha_wait_for_node_up = eval(tg.config.get('ha_wait_for_node_up'))
        except Exception as e:
            print 'Exception : ',
            print e
        if ha_wait_for_node_up == True:
            if self.fence_action == 'reboot':
                if self.wait_for_node_up(node) == True:
                    msg = 'Node ' + self.nodename + ' rebooted by fencing script. Returning...'
                    self.msg += '\n' + msg
                    LOGGER.info(msg)
                    DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                    self.status = self.SUCCESS
                    return False
        return True
        

    #PASSED
    def up_confirmation(self, node_ha, grpid, grpname):
        self.change_ha_state(node_ha, HARegister.DOWN_CONFIRMATION, 'Checking if node is UP.')
        msg = 'Confirm the Node ' + self.nodename + ' is Up '
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        grp = DBSession.query(ServerGroup).filter(ServerGroup.id == grpid).first()
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.entity_id).first()
        node.clear_node_proxy()
        peer_node = grp.get_peer_node([node.id])
        ping = True
        if peer_node is None:
            msg = 'No UP nodes found in ServerPool ' + grpname + '. Can not do peer ping. Ping from CMS Server.'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            status = node.heartbeat()
            if status and status[0] == ManagedNode.UP:
                msg = 'Node ' + self.nodename + ' is Up.'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            else:
                ping = False
        else:
            msg = 'Trying to ping from the Node ' + peer_node.hostname
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            out,exit_code = self.do_peer_ping(node, peer_node)
            if exit_code == 0:
                msg = 'Peer Ping Success. Node ' + self.nodename + ' is UP. '
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            else:
                ping = False
        if ping == False:
            msg = 'Can not reach the node. Node ' + self.nodename + ' is DOWN. Returning...'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            return False
        return True
        

    ##########################
    def up_fail_over(self, node_ha, grpid):
        self.change_ha_state(node_ha, HARegister.FAIL_OVER, 'Starting migrating vms back to the node.')
        (allowed, info) = self.change_transient_state(self.entity_id, ManagedNode.UP_FAILOVER, constants.HA)
        if allowed == False:
            raise Exception(constants.NO_OP + '\n' + str(info['msg']))
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.entity_id).options(eagerload('current_state')).first()
        grp = DBSession.query(ServerGroup).filter(ServerGroup.id == grpid).first()
        msg = 'Processing VMs that belonged to the Node ' + self.nodename + '. '
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        vshs = VMStateHistory.get_vm_states(self.entity_id)
        migrate_back = grp.is_migrate_back()
        (s_flag, f_flag) = (False, False)
        for vsh in vshs:
            try:
                self.execution_context['current_dom_id'] = vsh.vm_id
                vm = DBSession.query(VM).filter(VM.id == vsh.vm_id).options(eagerload('current_state')).first()
                domname = vm.name
                if vm is None:
                    msg = 'Removing entries for VM ' + domname + ' from VM State History'
                    LOGGER.info(msg)
                    VMStateHistory.remove_vm_states(self.entity_id, vsh.vm_id, all=True)
                else:    
                    msg = 'Processing VM ' + domname + ' for the Node ' + self.nodename + '. '
                    self.msg += '\n\n' + msg + '\n'
                    self.msg += '==============================\n'
                    LOGGER.info(msg)
                    DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                    vm_ent = DBSession.query(Entity).filter(Entity.entity_id == vm.id).one()
                    src_node = DBSession.query(ManagedNode).filter(ManagedNode.id == vm_ent.parents[0].entity_id).options(eagerload('current_state')).one()
                    
                    if self.entity_id == vm_ent.parents[0].entity_id:
                        msg = 'VM ' + domname + ' is already under the Node ' + self.nodename
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
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
                            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                            
                            if self.dom_start(self.auth, vm, node, retry_count, wait_interval):
                                msg = 'Successfully started VM ' + domname
                                self.update_failover_status(vm.id, HA.FAILOVER_SUCCESS)
                                self.msg += '\n' + msg
                                LOGGER.info(msg)
                                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                                s_flag = True
                                
                                if was_paused:
                                    msg = 'Trying to pause VM ' + domname
                                    self.msg += '\n' + msg
                                    LOGGER.info(msg)
                                    DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                                    
                                    if self.dom_pause(self.auth, vm, node) == True:
                                        s_flag = True
                                        msg = 'Successfully paused VM ' + domname
                                        self.msg += '\n' + msg
                                        LOGGER.info(msg)
                                        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                                        self.update_failover_status(vm.id, HA.FAILOVER_SUCCESS)
                                    else:
                                        f_flag = True
                                        msg = 'Failed to pause VM ' + domname
                                        self.msg += '\n' + msg
                                        LOGGER.info(msg)
                                        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                            else:
                                f_flag = True
                                msg = 'Failed to start VM ' + domname
                                self.msg += '\n' + msg
                                LOGGER.info(msg)
                                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                        else:
                            s_flag = True
                        
                        msg = 'Removing entries for VM ' + domname + ' from VM State History'
                        LOGGER.info(msg)
                        VMStateHistory.remove_vm_states(self.entity_id, vsh.vm_id)
                        continue
                    
                    if migrate_back == False:
                        s_flag = True
                        msg = 'Removing entries for VM ' + domname + ' from VM State History'
                        LOGGER.info(msg)
                        VMStateHistory.remove_vm_states(self.entity_id, vsh.vm_id)
                        continue
                    
                    if self.is_down(vm):
                        msg = 'Cold Mirgation of VM ' + domname + ' to the Node ' + self.nodename + '. '
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                        
                        if self.dom_migrate(self.auth, vm, src_node, node):
                            s_flag = True
                            msg = 'Migrating VM ' + domname + ' back to the node ' + self.nodename + ' done.'
                            self.msg += '\n' + msg
                            LOGGER.info(msg)
                            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                            self.update_failover_status(vm.id, HA.FAILOVER_SUCCESS)
                            config = vm.get_config()
                            
                            if config and config.get('auto_start_vm') == 1:
                                LOGGER.info('auto_start_vm is 1 for Down VM %s' % domname)
                                retry_count = vm.get_attribute_value(constants.retry_count, 3)
                                wait_interval = vm.get_attribute_value(constants.wait_interval, 3)
                                
                                if self.dom_start(self.auth, vm, node, retry_count, wait_interval):
                                    msg = 'Successfully started Down VM ' + domname
                                    s_flag = True
                                    self.msg += '\n' + msg
                                    LOGGER.info(msg)
                                    DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                                    self.update_failover_status(vm.id, HA.FAILOVER_SUCCESS)
                                else:
                                    f_flag = True
                                    msg = 'Failed to start Down VM ' + domname
                                    self.msg += '\n' + msg
                                    LOGGER.info(msg)
                                    DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                                    
                        else:
                            f_flag = True
                            msg = 'Migrating VM ' + domname + ' back to the node ' + self.nodename + ' failed.'
                            self.msg += '\n' + msg
                            LOGGER.info(msg)
                            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                    else:    
                        msg = 'Live Mirgation of VM ' + domname + ' to the Node ' + self.nodename + '. '
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                        if self.dom_migrate(self.auth, vm, src_node, node, live='true'):
                            s_flag = True
                            msg = 'Migrating VM ' + domname + ' back to the node ' + self.nodename + ' Complete.'
                            self.msg += '\n' + msg
                            LOGGER.info(msg)
                            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                            self.update_failover_status(vm.id, HA.FAILOVER_SUCCESS)
                        else:
                            f_flag = True
                            msg = 'Migrating VM ' + domname + ' back to the node ' + self.nodename + ' Failed.' + '\n' + to_str(e)
                            self.msg += '\n' + msg
                            LOGGER.info(msg)
                            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                        
                    msg = 'Removing entries for VM ' + domname + ' from VM State History'
                    LOGGER.info(msg)
                    VMStateHistory.remove_vm_states(self.entity_id, vsh.vm_id)
                    
            except Exception as e:
                f_flag = True
                msg = 'Can not process VM ' + domname + '.\n' + to_str(e)
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            
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
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        return True
        

    #PASSED
    def up_post_fail_over(self, node_ha, grpid, grpname):
        msg = 'Checking the Standby Node status in the ServerPool ' + grpname
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        self.change_ha_state(node_ha, HARegister.POST_FAILOVER, msg)
        grp = DBSession.query(ServerGroup).filter(ServerGroup.id == grpid).first()
        migrate_back = grp.is_migrate_back()
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.entity_id).first()
        node_ent = DBSession.query(Entity).filter(Entity.entity_id == node.id).first()
        if len(node_ent.children) == 0 and migrate_back == False:
            sb_nodes = grp.get_standby_nodes()
            for sb_node in sb_nodes:
                sbnode_ent = DBSession.query(Entity).filter(Entity.entity_id == sb_node.id).first()
                if sbnode_ent is not None and len(sbnode_ent.children) > 0:
                    sb_node.set_standby(False)
                    node.set_standby(True)
                    DBSession.add(node)
                    DBSession.add(sb_node)
                    msg = 'Marking the node ' + self.nodename + ' as a standby ' + 'and the node ' + sb_node.hostname + ' as not standby'
                    self.msg += '\n' + msg
                    LOGGER.info(msg)
                    DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                    break
                    
        transaction.commit()
        return True
        

    #PASSED
    def update_failed_doms(self, dom_id):
        failed_doms = self.execution_context['failed_doms']
        if dom_id in failed_doms:
            failed_doms.remove(dom_id)
        
        self.execution_context['failed_doms'] = failed_doms
        self.update_failover_status(dom_id, HA.FAILOVER_SUCCESS)
        

    #PASSED
    def wait_for_sync(self):
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.entity_id).first()
        msg = 'Submitting Storage and Network syncing tasks for ' + self.nodename + '. '
        LOGGER.info(msg)
        node.wait_for_nw_str_sync(self.auth)
        return True


class VMHAEvent(HA):
    CONFIRMATION = 10
    MIGRATE_TO_CANDIDATE = 70
    MIGRATE_TO_PREFERRED = 30
    MIGRATE_TO_STANDBY = 50
    RESTART = 20
    START_IN_CANDIDATE = 80
    START_IN_PREFERRED = 40
    START_IN_STANDBY = 60
    def __init__(self, auth, event_id, entity, group_id, ha_state=None):
        self.auth = auth
        self.event_id = event_id
        self.entity = entity
        self.entity_id = entity.entity_id
        self.ha_state = ha_state
        self.msg = ''
        self.status = self.FAILURE
        self.sp_id = group_id
        self.step = self.CONFIRMATION
        self.execution_context = {}
        self.steps = {self.CONFIRMATION: self.RESTART, self.RESTART: self.MIGRATE_TO_PREFERRED, self.MIGRATE_TO_PREFERRED: self.START_IN_PREFERRED, self.START_IN_PREFERRED: self.MIGRATE_TO_STANDBY, self.MIGRATE_TO_STANDBY: self.START_IN_STANDBY, self.START_IN_STANDBY: self.MIGRATE_TO_CANDIDATE, self.MIGRATE_TO_CANDIDATE: self.START_IN_CANDIDATE}

        
    #PASSED
    def check_pending_task(self, dom):
        ha_stat = DBSession.query(HAStatus).filter(HAStatus.event_id == self.event_id).filter(HAStatus.task_status == Task.STARTED).first()
        if ha_stat:
            wait_time = dom.get_wait_time(ha_stat.action)
            self.step = ha_stat.step_number
            self.msg = ha_stat.msg
            self.execution_context = ha_stat.execution_context
            (finished, status) = self.wait_for_task_completion(ha_stat.task_id, wait_time)
            self.ha_status_update(self.sp_id, self.event_id, self.entity_id, ha_stat.task_id, status)
            return (status, ha_stat.step_number, ha_stat.msg)
            
        ha_stat = DBSession.query(HAStatus).filter(HAStatus.event_id == self.event_id).order_by(HAStatus.timestamp.desc()).first()
        if ha_stat:
            return (ha_stat.task_status, ha_stat.step_number, ha_stat.msg)
            
        return (False, None, '')

       
    #PASSED
    def down_confirmation(self, dom, domname, node, nodename, dom_ha):
        if dom.status == constants.MIGRATING:
            msg = 'VM ' + domname + ' is in Migrating state. Returning..'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            self.status = self.SUCCESS
            return False
            
        ha = DBSession.query(HARegister).filter(HARegister.entity_id == node.id).first()
        if ha:
            msg = 'Checking if the parent node is going through a fail-over'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            if ha.ha_state in [HARegister.DOWN_CONFIRMATION, HARegister.STONITH, HARegister.FAIL_OVER, HARegister.POST_FAILOVER]:
                msg = 'Parent Node ' + nodename + ', of VM ' + domname + ', is going through fail-over. Cancelling VM fail-over'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                self.status = self.SUCCESS
                return False
                
        msg = 'Checking if the VM ' + domname + ' is actually down.'
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        self.change_ha_state(dom_ha, HARegister.DOWN_CONFIRMATION, msg)
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == node.id).first()
        dom_down = self.check_dom_down(dom, node)
        if dom_down is False:
            msg = 'VM ' + domname + ' is not DOWN. Returning...'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            self.change_ha_state(dom_ha, HARegister.FAILOVER_COMPLETE, msg)
            self.status = self.SUCCESS
            return False
            
        return True


    #PASSED
    def fail_over(self, dom, domname, dom_ha, node_id, fail_over=False, migrate_start=False):
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
        group = self.get_group(node=node)
        retry_count = dom.get_attribute_value(constants.retry_count, group.getAttributeValue(constants.retry_count, 3))
        wait_interval = dom.get_attribute_value(constants.wait_interval, group.getAttributeValue(constants.wait_interval, 3))
        msg = 'VM ' + dom.name + 'attributes. retry_count=' + str(retry_count) + ', wait_interval=' + str(wait_interval)
        LOGGER.info(msg)
        self.print_step(833)
        if self.get_next_step() == self.RESTART:
            time.sleep(19)
            self.update_step_to_next()
            self.print_step(838)
            msg = 'Trying to start VM ' + domname + '.'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            self.change_ha_state(dom_ha, HARegister.FAIL_OVER, 'Trying to start.')
            node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
            if self.dom_start(self.auth, dom, node, retry_count, wait_interval) == True:
                msg = 'Fail-Over success. VM ' + domname + ' started during retry.'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
                self.change_ha_state(dom_ha, HARegister.FAILOVER_COMPLETE, msg)
                self.status = self.SUCCESS
                return True
        if group.failover == constants.VM_FAILOVER:
            msg = 'VM ' + domname + ' failover failed'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            self.change_ha_state(dom_ha, HARegister.FAILOVER_COMPLETE, msg)
            return False
        self.print_step(860)
        if fail_over == False and self.get_next_step() == self.MIGRATE_TO_PREFERRED:
            self.update_step_to_next()
            msg = 'Starting VM ' + domname + ' failed. Try Starting on another node.'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            dom = DBSession.query(VM).filter(VM.id == self.entity_id).options(eagerload('current_state')).first()
            new_node = self.get_preferred_node(dom)
            if new_node is None or new_node is not None and new_node.id == node.id:
                self.update_step_to_next()
                msg = 'VM ' + domname + ' has no valid preferred node. ' + 'Looking for Standby Nodes.'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            else:
                migrate_start = False
                migrate_start = self.migrate(dom, node, new_node)
        self.print_step(891)
        if fail_over == False and migrate_start == True and self.get_next_step() == self.START_IN_PREFERRED:
            self.update_step_to_next()
            if self.start(dom, retry_count, wait_interval) == True:
                fail_over = True
                msg = 'VM ' + domname + ' failover successfully completed'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        self.print_step(902)
        if fail_over == False and self.get_next_step() == self.MIGRATE_TO_STANDBY:
            self.update_step_to_next()
            new_node = self.find_standby_node(self.auth, dom, node, group)
            if new_node is None:
                self.update_step_to_next()
                msg = 'No valid standby node for VM ' + domname + '. ' + 'Trying Initial Placement.'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            else:
                migrate_start = False
                migrate_start = self.migrate(dom, node, new_node)
        self.print_step(925)
        if fail_over == False and migrate_start == True and self.get_next_step() == self.START_IN_STANDBY:
            self.update_step_to_next()
            if self.start(dom, retry_count, wait_interval) == True:
                fail_over = True
                msg = 'VM ' + domname + ' failover successfully completed'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        self.print_step(936)
        if fail_over == False and self.get_next_step() == self.MIGRATE_TO_CANDIDATE:
            self.update_step_to_next()
            new_node = self.get_allocation_candidate(self.auth, dom, node, group)
            if new_node is None:
                self.update_step_to_next()
                msg = 'No suitable node found for migrating VM ' + domname + '. ' + 'Can not proceed.'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            else:
                migrate_start = False
                migrate_start = self.migrate(dom, node, new_node)
        self.print_step(961)
        if fail_over == False and migrate_start == True and self.get_next_step() == self.START_IN_CANDIDATE:
            self.update_step_to_next()
            if self.start(dom, retry_count, wait_interval) == True:
                fail_over = True
                msg = 'VM ' + domname + ' failover successfully completed'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        if fail_over == False:
            msg = 'VM ' + domname + ' failover failed'
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        self.change_ha_state(dom_ha, HARegister.FAILOVER_COMPLETE, msg)
        return fail_over


    #PASSED
    def migrate(self, dom, node, new_node):
        domname = dom.name
        dom_ent = DBSession.query(Entity).filter(Entity.entity_id == dom.id).first()
        node_ent = dom_ent.parents[0]
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_ent.entity_id).first()
        new_nodename = new_node.hostname
        local_storage = self.has_local_storage(dom.id, new_node)
        if local_storage == True:
            self.update_step_to_next()
            msg = 'Can not Migrate VM ' + domname + ' to the node ' + new_nodename + 'VM disks are not present in the node ' + new_nodename
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            return False
        msg = 'Migrating VM ' + domname + ' to the node ' + new_nodename
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        if self.dom_migrate(self.auth, dom, node, new_node):
            msg = 'VM ' + domname + ' migrated to the node ' + new_nodename
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            return True
        msg = 'Migrating VM ' + domname + ' to the node ' + new_nodename + ' failed'
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        return False


    #PASSED
    def onVMDown(self):
        dom = DBSession.query(VM).filter(VM.id == self.entity_id).options(eagerload('current_state')).first()
        domname = dom.name
        dom_ha = self.entity.ha
        LOGGER.info('======================START VM DOWN============================ ')
        msg = 'Start processing VM Down Event on ' + domname
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        parent = self.entity.parents[0]
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == parent.entity_id).first()
        nodename = node.hostname
        self.msg += '\n\nConfirm the VM is down.\n'
        self.msg += '==============================\n'
        failover_status = HA.FAILOVER_FAILURE
        if self.down_confirmation(dom, domname, node, nodename, dom_ha) != True:
            self.update_failover_status(self.entity_id, failover_status)
            return
            
        self.msg += '\n\nStart VM Failover.\n'
        self.msg += '==============================\n'
        if self.fail_over(dom, domname, dom_ha, parent.entity_id) == True:
            self.status = self.SUCCESS
            failover_status = HA.FAILOVER_SUCCESS
            
        self.update_failover_status(self.entity_id, failover_status)
        LOGGER.info('======================END VM DOWN============================ ')



    #PASSED
    def resumeVMDown(self):
        dom = DBSession.query(VM).filter(VM.id == self.entity_id).options(eagerload('current_state')).first()
        domname = dom.name
        dom_ha = self.entity.ha
        ha_state = self.ha_state
        LOGGER.info('======================START VM DOWN============================ ')
        msg = 'Resuming VM Down Event on ' + domname
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        parent = self.entity.parents[0]
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == parent.entity_id).first()
        nodename = node.hostname
        failover_status = HA.FAILOVER_FAILURE
        if ha_state in [HARegister.NOT_ACTIVE, HARegister.DOWN_CONFIRMATION]:
            self.msg += '\n\nConfirm the VM is down.\n'
            self.msg += '==============================\n'
            if self.down_confirmation(dom, domname, node, nodename, dom_ha) != True:
                self.update_failover_status(self.entity_id, failover_status)
                return 
            ha_state = HARegister.FAIL_OVER
        if ha_state == HARegister.FAIL_OVER:
            status,self.step,self.msg = self.check_pending_task(dom)
            #self.msg = self
            if self.step is None:
                self.step = self.CONFIRMATION
            (fail_over, migrate_start) = (False, False)
            if self.step in [self.RESTART, self.START_IN_PREFERRED, self.START_IN_STANDBY, self.START_IN_CANDIDATE] and status == Task.SUCCEEDED:
                fail_over = True
                msg = 'VM ' + domname + ' failover successfully completed'
                self.msg += '\n' + msg
                LOGGER.info(msg)
                DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            else:
                if self.step in [self.MIGRATE_TO_PREFERRED, self.MIGRATE_TO_STANDBY, self.MIGRATE_TO_CANDIDATE] and status == Task.SUCCEEDED:
                    migrate_start = True
                    msg = 'VM ' + domname + ' migrated succesfully'
                    self.msg += '\n' + msg
                    LOGGER.info(msg)
                    DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            self.msg += '\n\nResume VM Failover.\n'
            self.msg += '==============================\n'
            if self.fail_over(dom, domname, dom_ha, parent.entity_id, fail_over, migrate_start) == True:
                self.status = self.SUCCESS
                failover_status = HA.FAILOVER_SUCCESS
        self.update_failover_status(self.entity_id, failover_status)
        LOGGER.info('======================END VM DOWN============================ ')



    #PASSED
    def start(self, dom, retry_count, wait_interval):
        domname = dom.name
        dom_ent = DBSession.query(Entity).filter(Entity.entity_id == dom.id).first()
        node_ent = dom_ent.parents[0]
        new_nodename = node_ent.name
        msg = 'Trying to start  VM ' + domname + ' on the node ' + new_nodename
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_ent.entity_id).first()
        if self.dom_start(self.auth, dom, node, retry_count, wait_interval) == True:
            msg = 'VM ' + domname + ' successfully started on Node ' + new_nodename
            self.msg += '\n' + msg
            LOGGER.info(msg)
            DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
            return True
        msg = 'VM ' + domname + ' migrated to Node ' + new_nodename + '. But failed to start.'
        self.msg += '\n' + msg
        LOGGER.info(msg)
        DBSession.add(HAEventLog(self.event_id, self.entity_id, to_unicode(msg)))
        return False



