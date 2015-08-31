from stackone.model.services import Task, TaskResult, TaskUtil
from stackone.viewModel import Basic
from stackone.viewModel.NodeService import NodeService
from stackone.viewModel.ImageService import ImageService
from stackone.viewModel.VcenterService import VcenterService
from stackone.core.appliance import xva
from stackone.model.ImageStore import ImageUtils, Image
from stackone.model.SyncDefinition import SyncDef
import stackone.core.utils.utils
from stackone.core.utils.utils import to_unicode, to_str, p_task_timing_start, p_task_timing_end
from stackone.core.utils.constants import *
from stackone.model.Metrics import MetricsService
import logging
import traceback
import transaction
from stackone.model import DBSession
from stackone.model.VM import VM
from stackone.model.Entity import Entity, EntityTasks
from stackone.model.ManagedNode import ManagedNode
import stackone.core.utils.constants as constants
from stackone.viewModel.StorageService import StorageService
from stackone.viewModel.NetworkService import NetworkService
from stackone.viewModel.BackupService import BackupService
from stackone.viewModel.RestoreService import RestoreService
from stackone.viewModel.VLANService import VLANService
from stackone.model.UpdateManager import AppUpdateManager
from stackone.model.GridManager import *
from datetime import datetime, timedelta
import calendar
import tg
from stackone.core.utils.utils import wait_for_task_completion, get_parent_task_status_info, get_child_task_status_info, notify_task_hung
from stackone.model.LicenseManager import check_all_lic
from stackone.model.DWM import DWMManager, SPDWMPolicy
from stackone.model.AvailabilityWorker import AvailabilityWorker
from stackone.model.VMAvailabilityWorker import VMAvailabilityWorker
from stackone.model.CollectMetricsWorker import CollectMetricsWorker
from stackone.core.utils.thread_context import with_thread_context
LOGGER = logging.getLogger('stackone.viewModel')
AVL_LOGGER = logging.getLogger('AVAIL_TIMING')
MTR_LOGGER = logging.getLogger('METRICS_TIMING')
WRK_LOGGER = logging.getLogger('WORKER')
LICENSE_CHECK_TIMER = 0L
def m_(string):
    return string

class NodeTask(Task):
    def get_node_id(self):
        return self.get_param('node_id')

    def get_dom_id(self):
        return self.get_param('dom_id')

    def get_dom_name(self):
        node_id = self.get_dom_id()
        name = node_id
        if node_id is not None:
            try:
                vm = DBSession.query(VM).filter(VM.id == node_id).one()
                name = vm.name
            except Exception as e:
                LOGGER.error(e)
            return name
        return None

    def get_node_name(self):
        node_id = self.get_node_id()
        name = node_id
        if node_id is not None:
            try:
                node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).one()
                name = node.hostname
            except Exception as e:
                pass
        return name
        return None



class VMActionTask(NodeTask):
    def get_descriptions(self):
        action = self.get_param('action')
        task_exe_context = self.get_param('task_exe_context')
        dom_name = self.get_dom_name()
        node_name = self.get_node_name()
        short_desc = ''
        desc = ''
        req = self.get_param('requester')
        if req == constants.CORE:
            req = ''
        else:
            req += ' : '
        if action == constants.START:
            short_desc = m_('%sStarting %s')
            desc = m_('%sStart action on %s. Managed Node is %s')
        elif action == constants.PAUSE:
            short_desc = m_('%sPausing %s')
            desc = m_('%sPause action on %s. Managed Node is %s')
        elif action == 'unpause':
            short_desc = m_('%sResuming %s')
            desc = m_('%sResume action on %s. Managed Node is %s')
        elif action == constants.REBOOT:
            short_desc = m_('%sRebooting %s')
            desc = m_('%sReboot action on %s. Managed Node is %s')
        elif action == constants.KILL:
            short_desc = m_('%sKilling %s')
            desc = m_('%sKill action on %s. Managed Node is %s')
        elif action == constants.SHUTDOWN:
            short_desc = m_('%sShutting down %s')
            desc = m_('%sShutdown action on %s. Managed Node is %s')
        if task_exe_context in [Maintenance]:
            short_desc = 'Maintenance : %s' % short_desc
            desc = m_('Maintenance : %s' % desc)
        return (short_desc, (req, dom_name), desc, (req, dom_name, node_name))

    def exec_task(self, auth, ctx, dom_id, node_id, action, requester, task_exe_context):
        manager = Basic.getGridManager()
        return manager.do_dom_action(auth, dom_id, node_id, action, requester)

    def resume_task(self, auth, ctx, dom_id, node_id, action, requester, task_exe_context):
        try:
            node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
            if node is None:
                raise Exception('Can not find the managed node for ' + node_id)
            dom = DBSession.query(VM).filter(VM.id == dom_id).first()
            if dom is None:
                raise Exception('Can not find the virtual machine for ' + dom_id)
            dom.node = node
            values = dom.get_state_dict()[action]
            status = dom.check_state(values, 1L)
            if status == False:
                raise Exception(action + ' failed due to timeout.')
            return status
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)
        return None

    def recover_task(self, auth, ctx, dom_id, node_id, action, requester, task_exe_context):
        try:
            return self.resume_task(auth, ctx, dom_id, node_id, action, requester, task_exe_context)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)



class ServerActionTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_node_name()
        action = self.get_param('action')
        short_desc = ''
        if action == 'start_all':
            short_desc = m_('Starting all Virtual Machines on %s')
        else:
            if action == 'shutdown_all':
                short_desc = m_('Shutting down all Virtual Machines on %s')
            else:
                if action == 'kill_all':
                    short_desc = m_('Killing all VMs on %s')
        return (short_desc, (node_name), short_desc, (node_name))

    def exec_task(self, auth, ctx, node_id, action, requester=None):
        manager = Basic.getGridManager()
        managed_node = manager.getNode(auth, node_id)
        if managed_node is not None:
            if not managed_node.is_authenticated():
                managed_node.connect()
            return manager.do_node_action(auth, node_id, action, requester)
        raise Exception('Can not find the managed node')
        return None

    def resume_task(self, auth, ctx, node_id, action, requester=None):
        try:
            return self.exec_task(auth, ctx, node_id, action, requester)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)



class ServerMaintenanceTask(NodeTask):
    def get_descriptions(self):
        is_maintenance = self.get_param('is_maintenance')
        msg = 'Entering'
        if not is_maintenance:
            msg = 'Leaving'
        short_desc = m_('%s Maintenance Mode' % msg)
        return (short_desc, (), short_desc, ())

    def exec_task(self, auth, ctx, node_id, node_name, is_maintenance):
        from stackone.model.Maintenance import Maintenance
        mainte = Maintenance()
        mainte.initialize(auth, node_id)
        msg = mainte.server_maintenance(maint_task_id=self.task_id, is_maintenance=is_maintenance)
        return dict(results=msg, visible=True, status=Task.SUCCEEDED)

    def resume_task(self, auth, ctx, node_id, node_name, is_maintenance):
        try:
            from stackone.model.Maintenance import Maintenance
            mainte = Maintenance()
            mainte.initialize(auth, node_id)
            msg = mainte.resume_maintenance(maint_task_id=self.task_id, is_maintenance=is_maintenance)
            return dict(results=msg, visible=True, status=Task.SUCCEEDED)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)



class RemoveServerTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_param('node_name')
        grp_name = self.get_param('grp_name')
        short_desc = ''
        desc = ''
        short_desc = m_('Remove %s')
        desc = m_('Removing Server %s on Server Pool %s.')
        return (short_desc, node_name, desc, (node_name, grp_name))

    def exec_task(self, auth, ctx, node_id, **kw):
        manager = Basic.getGridManager()
        return manager.removeNode(auth, node_id, kw.get('force', False))

    def resume_task(self, auth, ctx, node_id, **e):
        try:
            return self.exec_task(auth, ctx, node_id, **kw)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, node_id, **e):
        try:
            return self.exec_task(auth, ctx, node_id, **kw)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)



class VMMigrateTask(NodeTask):
    def get_descriptions(self):
        source_node = self.get_param('source_node_id')
        dest_node = self.get_param('dest_node_id')
        migrate_vm = self.get_param('all')
        vmName = ''
        if migrate_vm == False:
            doms = self.get_param('dom_list')
            dom = DBSession.query(Entity).filter_by(entity_id=doms[0L]).one()
            if dom:
                vmName = dom.name
        else:
            vmName = 'All Virtual Machines'
        sname = source_node
        dname = dest_node
        sent = DBSession.query(Entity).filter_by(entity_id=source_node).one()
        if sent:
            sname = sent.name
        dent = DBSession.query(Entity).filter_by(entity_id=dest_node).one()
        if dent:
            dname = dent.name
        req = self.get_param('requester')
        if req == constants.CORE:
            req = ''
        else:
            req += ' : '
        short_desc = m_('%sMigrate %s from %s to %s')
        desc = m_('%sMigrate %s from %s to %s')
        return (short_desc, (req, vmName, sname, dname), desc, (req, vmName, sname, dname))

    def get_source_node_id(self):
        return self.get_param('source_node_id')

    def get_dest_node_id(self):
        return self.get_param('dest_node_id')

    def get_entity_ids(self):
        entity_ids = ''
        entity_ids += self.get_source_node_id()
        entity_ids += ',' + self.get_dest_node_id()
        return entity_ids

    def exec_task(self, auth, ctx, dom_list, source_node_id, dest_node_id, live, force, all, requester):
        manager = Basic.getGridManager()
        return manager.migrate_vm(auth, dom_list, source_node_id, dest_node_id, live, force, all, requester)

    def resume_task(self, auth, ctx, dom_list, source_node_id, dest_node_id, live, force, all, requester):
        try:
            manager = Basic.getGridManager()
            return manager.resume_migrate_vm(auth, dom_list, source_node_id, dest_node_id, live, force, all, requester)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, dom_list, source_node_id, dest_node_id, live, force, all, requester):
        try:
            manager = Basic.getGridManager()
            return manager.resume_migrate_vm(auth, dom_list, source_node_id, dest_node_id, live, force, all, requester, recover=True)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)



class VMConfigSettingsTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_node_name()
        vm_name = self.get_vm_name()
        mode = self.get_param('mode')
        if mode == 'PROVISION_VM':
            short_desc = m_('Provisioning %s')
            desc = m_('Provisioning %s onto %s')
        else:
            if mode == 'EDIT_VM_INFO':
                short_desc = m_('Change Settings of %s')
                desc = m_('Change In Memory Settings of %s. Managed Node is %s')
        return (short_desc, (vm_name), desc, (vm_name, node_name))

    def exec_task(self, auth, ctx, image_id, config, mode, node_id, group_id, dom_id, vm_name, cli, memory, vcpu, cloud,csep_context, network, csep_id, vdc_name):
        if cli == False:
            return NodeService().vm_config_settings(auth, image_id, config, mode, node_id, group_id, dom_id, vm_name, task_id=self.task_id)
        return NodeService().node_provision_vm(auth, group_id, node_id, image_id, vm_name, memory, vcpu,cloud, csep_context, network=network, csep_id=csep_id, vdc_name=vdc_name)

    def resume_task(self, auth, ctx, image_id, config, mode, node_id, group_id, dom_id, vm_name, cli, memory, vcpu,cloud,  csep_context, network, csep_id, vdc_name):
        if mode != 'PROVISION_VM':
            raise Exception(constants.INCOMPLETE_TASK)
        vm = DBSession.query(VM).filter(VM.name == vm_name).first()
        if vm is None:
            raise Exception(constants.INCOMPLETE_TASK)
        return None

    def recover_task(self, auth, ctx, image_id, config, mode, node_id, group_id, dom_id, vm_name, cli, memory, vcpu,cloud,  csep_context, network, csep_id, vdc_name):
        self.resume_task(auth, ctx, image_id, config, mode, node_id, group_id, dom_id, vm_name, cli, memory, vcpu, cloud, csep_context, network, csep_id, vdc_name)

    def get_vm_name(self):
        return self.get_param('vm_name')



class RefreshNodeInfoTask(Task):
    def get_descriptions(self):
        short_desc = m_('Refresh Task for All Nodes')
        return (short_desc, (), short_desc, ())

    def exec_task(self, auth, ctx):
        manager = Basic.getGridManager()
        groups = manager.getGroupList(auth)
        for group in groups:
            grp_ent = auth.get_entity(group.id)
            node_ids = [x.entity_id for x in grp_ent.children]
            for id in node_ids:
                try:
                    transaction.begin()
                    node = DBSession.query(ManagedNode).filter(ManagedNode.id == id).one()
                    node.refresh_environ()
                    node.get_running_vms()
                    node.socket = node.get_socket_info()
                    DBSession.add(node)
                    transaction.commit()
                except Exception as e:
                    LOGGER.error(to_str(e))
                    DBSession.rollback()
        ungrouped_nodes = manager.getNodeList(auth)
        node_ids = []
        for n in ungrouped_nodes:
            node_ids.append(n.id)
        for id in node_ids:
            try:
                transaction.begin()
                node = DBSession.query(ManagedNode).filter(ManagedNode.id == id).one()
                node.refresh_environ()
                node.get_running_vms()
                node.socket = node.get_socket_info()
                DBSession.add(node)
                transaction.commit()
            except Exception as e:
                LOGGER.error(to_str(e))
                DBSession.rollback()




class PopulateNodeInfoTask(NodeTask):
    def get_descriptions(self):
        short_desc = m_('Populate Information Task for Node')
        return (short_desc, (), short_desc, ())

    def exec_task(self, auth, ctx, node_id):
        manager = Basic.getGridManager()
        m_node = manager.getNode(auth, node_id)
        m_node._init_environ()



class Purging(Task):
    def get_descriptions(self):
        short_desc = m_('Purge Historical Data')
        return (short_desc, (), short_desc, ())

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec_task for Purging task')
        MetricsService().purging_for_all_nodes(auth)
        import tg
        from datetime import datetime, timedelta
        purge_interval = tg.config.get('task_results_purge_interval')
        cutoff_date = datetime.now() + timedelta(days=-int(purge_interval))
        DBSession.query(TaskResult).filter(TaskResult.timestamp <= cutoff_date).delete()
        limit = 5000
        offset = 0
        while True:
            tasks = DBSession.query(Task).filter(Task.submitted_on <= cutoff_date).filter(Task.interval == None).filter(Task.calendar == None).order_by(Task.submitted_on.asc()).limit(limit).offset(offset).all()
            if len(tasks) == 0:
                break
            offset += limit
            for task in tasks:
                DBSession.delete(task)
            transaction.commit()
        rept_purge_interval = tg.config.get('repeating_tasks_purge_interval')
        cutoff_date = datetime.now() + timedelta(days=-int(rept_purge_interval))
        rpt_tasks = ['TimeBasisRollupForNodes', 'SPDWMTask', 'EmailNotificationTask', 'EmailTask']
        rpt_prvnt_tasks = ['CollectMetricsForNodes', 'NodeAvailTask', 'VMAvailTask']
        rpt_task = DBSession.query(Task.task_id).filter(Task.task_type.in_(rpt_tasks)).all()
        rpt_prvnt_task = DBSession.query(Task.task_id).filter(Task.task_type.in_(rpt_prvnt_tasks)).all()

        rpt_task_ids = [x.task_id for x in rpt_task]
        rpt_prvnt_task_ids = [x.task_id for x in rpt_prvnt_task]
        print rpt_task_ids,'=========XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX=========',
        print rpt_prvnt_task_ids
        task_ids = rpt_task_ids + rpt_prvnt_task_ids
        DBSession.query(TaskResult).filter(TaskResult.task_id.in_(task_ids)).filter(TaskResult.timestamp <= cutoff_date).delete()
        transaction.commit()
        DBSession.query(TaskResult).filter(TaskResult.task_id.in_(DBSession.query(Task.task_id).filter(Task.parent_task_id.in_(rpt_prvnt_task_ids)).filter(Task.submitted_on <= cutoff_date))).delete()
        transaction.commit()
        DBSession.query(Task).filter(Task.parent_task_id.in_(rpt_prvnt_task_ids)).filter(Task.submitted_on <= cutoff_date).delete()




class CollectMetricsForNodes(Task):
    def get_descriptions(self):
        short_desc = m_('Collect data for all entities and update CURR and RAW tables')
        return (short_desc, (), short_desc, ())

    def get_status(self):
        return get_parent_task_status_info(self)

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec task for CollectMetricsForNodes task')
        strt = p_task_timing_start(MTR_LOGGER, 'CollectMetricsForNodes', [])
        CollectMetricsWorker(auth).do_work()
        p_task_timing_end(MTR_LOGGER, strt)

    def resume_task(self, auth, ctx):
        try:
            CollectMetricsWorker(auth).resume_work(ctx)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx):
        try:
            self.resume_task(auth, ctx)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)



class WorkerTask(Task):
    def get_next_node_id(self, index):
        try:
            try:
                return self.exc_node_ids[index]
            except IndexError as e:
                return None
        finally:
            pass
    def get_running_status(self):
        max_wait_time = self.get_max_wait_time()
        WRK_LOGGER.debug('get_running_status : ' + self.name)
        try:
            if (datetime.now() - self.start_time).seconds > max_wait_time:
                WRK_LOGGER.error('Task, ' + str(self.name) + ':' + str(self.task_id) + ' is hung on ' + self.current_node.hostname)
                self.exc_node_ids = [self.current_node.id]
                self.mark_hung = True
                notify_task_hung(self, self.current_node)
                return (True, self.completed_nodes, self.pending_nodes)
        finally:
            pass
        return (False, [], [])

    def check_if_hung(self):
        WRK_LOGGER.debug('Check if Task, ' + self.name + ' is hung? ')
        marked_hung = False
        try:
            marked_hung = self.mark_hung
            if marked_hung:
                WRK_LOGGER.debug('Task, ' + self.name + '(' + str(self.task_id) + ') was marked hung. updating entity_tasks')
                DBSession.query(EntityTasks).filter(EntityTasks.worker_id == to_unicode(self.task_id)).update(dict(worker_id=None, finished=True, end_time=datetime.now()))
        except AttributeError as e:
            pass
        return None

    def get_pending_node_ids(self, node_ids):
        ets = DBSession.query(EntityTasks.entity_id).filter(EntityTasks.worker_id == to_unicode(self.task_id)).filter(EntityTasks.entity_id.in_(node_ids)).all()
        node_ids = [et[0] for et in ets]
        WRK_LOGGER.debug('RESUMING CHILD WORKER . NodeIDS : ' + str(node_ids))
        return node_ids


    def do_cleanup(self):
        WRK_LOGGER.debug('Cleaning Up entity_tasks . task_id: ' + str(self.task_id))
        r = DBSession.query(EntityTasks.entity_id).filter(EntityTasks.worker_id == to_unicode(self.task_id)).update(values=dict(worker_id=None, finished=True, end_time=datetime.now()))
        WRK_LOGGER.debug('Cleaned Up entity_tasks . task_id:rows : ' + str(self.task_id) + ':' + str(r))
        return None



class CollectMetrics(WorkerTask):
    def get_descriptions(self):
        short_desc = m_('Collect data for all entities and update CURR and RAW tables')
        return (short_desc, (), short_desc, ())

    def get_status(self):
        return get_child_task_status_info(self)

    def exec_task(self, auth, ctx, node_ids, sp_id):
        LOGGER.debug('entered in excec task for CollectMetricsForNodes task')
        strt = p_task_timing_start(MTR_LOGGER, 'CollectMetrics', node_ids)

        try:
            manager = Basic.getGridManager()
            self.completed_nodes = []
            self.pending_nodes = [node_id for node_id in node_ids]
            self.exc_node_ids = [node_id for node_id in node_ids]
            index = 0
            node_id = self.get_next_node_id(index)
            while node_id is not None:
                self.pending_nodes.remove(node_id)
                m_node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).one()
                index += 1
                node_id = self.get_next_node_id(index)
                if m_node is None:
                    continue
                self.current_node = m_node
                self.start_time = datetime.now()
                try:
                    try:
                        strt1 = p_task_timing_start(MTR_LOGGER,'NodeGetMterics',m_node.id)
                        node_snapshot = manager.collectServerMetrics(auth,m_node,filter=True)
                        manager.collectVMMetrics(auth, m_node.id, node_snapshot)
                        manager.collectServerPoolMetrics(auth, sp_id)
                        DBSession.flush()
                        transaction.commit()
                        p_task_timing_end(MTR_LOGGER, strt1)
                    except Exception as e:
                        LOGGER.error('Error updating metrics . Server :' + m_node.hostname)
                        traceback.print_exc()
                finally:
                    self.completed_nodes.append(m_node.id)
        finally:
            self.check_if_hung()
            p_task_timing_end(MTR_LOGGER, strt)
        
    def resume_task(self, auth, ctx, node_ids, sp_id):
        try:
            self.do_cleanup()
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, node_ids, sp_id):
        try:
            self.resume_task(auth, ctx, node_ids, sp_id)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)

    def get_max_wait_time(self):
        try:
            max_node_metrics_wait_time = int(tg.config.get('max_node_metrics_wait_time'))
        except Exception as e:
            LOGGER.error('Exception: ' + str(e))
            max_node_metrics_wait_time = 90L
        return max_node_metrics_wait_time



class TimeBasisRollupForNodes(Task):
    def get_descriptions(self):
        short_desc = m_('Metric Rollup')
        return (short_desc, (), short_desc, ())

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec task for TimeBasisRollupForNodes task')
        MetricsService().timebasis_rollup_for_all_nodes(auth)



class VMSnapshotTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_node_name()
        short_desc = m_('Snapshot vm %s')
        return (short_desc, (node_name), short_desc, node_name)

    def exec_task(self, auth, ctx, dom_id, node_id, file, directory):
        manager = Basic.getGridManager()
        return manager.save_dom(auth, dom_id, node_id, file, directory)



class VMRestoreTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_node_name()
        short_desc = m_('Restoring vm to %s')
        return (short_desc, (node_name), short_desc, node_name)

    def exec_task(self, auth, ctx, node_id, file):
        manager = Basic.getGridManager()
        return manager.restore_dom(auth, node_id, file)



class ImportApplianceTask(Task):
    def get_descriptions(self):
        pass

    def get_group_id(self):
        return self.get_param('group_id')

    def exec_task(self, auth, ctx, appliance_entry, image_store, group_id, image_name, platform, force):
        local_node = Basic.local_node
        if appliance_entry['type'].lower() == 'xva':
            return xva.import_appliance(auth, local_node, appliance_entry, image_store, group_id, image_name, platform, force, None)
        return ImageUtils.import_fs(auth, local_node, appliance_entry, image_store, group_id, image_name, platform, force, None)
        return None

    def resume_task(self, auth, ctx, appliance_entry, image_store, group_id, image_name, platform, force):
        img = DBSession.query(Image).filter(Image.name == image_name).first()
        if img is None:
            raise Exception(constants.INCOMPLETE_TASK)
        return None

    def recover_task(self, auth, ctx, appliance_entry, image_store, group_id, image_name, platform, force):
        self.resume_task(auth, ctx, appliance_entry, image_store, group_id, image_name, platform, force)



class RefreshNodeMetricsTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx):
        manager = Basic.getGridManager()
        groups = manager.getGroupList(auth)
        for group in groups:
            nodes = manager.getNodeList(auth, group.id)
        for n in nodes:
            manager.refreshNodeMetrics(auth, n)
        ungrouped_nodes = manager.getNodeList(auth)
        for n in ungrouped_nodes:
            manager.refreshNodeMetrics(auth, n)



class SyncAllOp(NodeTask):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, site_id, group_id, def_type):
        manager = Basic.getGridManager()
        if def_type == constants.STORAGE:
            def_manager = Basic.getStorageManager()
        else:
            if def_type == constants.NETWORK:
                def_manager = Basic.getNetworkManager()
        manager.SyncAll(auth, site_id, group_id, def_type, def_manager)

    def resume_task(self, auth, ctx, site_id, group_id, def_type):
        try:
            return self.exec_task(auth, ctx, site_id, group_id, def_type)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, site_id, group_id, def_type):
        try:
            return self.exec_task(auth, ctx, site_id, group_id, def_type)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)



class SyncServerOp(NodeTask):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, node_id):
        node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
        msg = 'Submitting Storage and Network syncing tasks for ' + node.hostname + '. '
        LOGGER.info(msg)
        node.wait_for_nw_str_sync(auth)



class ServerSyncOp(NodeTask):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, node_id, def_type, sync_forcefully):
        manager = Basic.getGridManager()
        if def_type == constants.STORAGE:
            def_manager = Basic.getStorageManager()
        else:
            if def_type == constants.NETWORK:
                def_manager = Basic.getNetworkManager()
        manager.SyncServer(auth, node_id, def_type, def_manager, sync_forcefully)

    def resume_task(self, auth, ctx, node_id, def_type, sync_forcefully):
        try:
            return self.exec_task(auth, ctx, node_id, def_type, sync_forcefully)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, node_id, def_type, sync_forcefully):
        try:
            return self.exec_task(auth, ctx, node_id, def_type, sync_forcefully)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)



class SyncDefnOp(NodeTask):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, server_ids, def_id, site_id, group_id, defType):
        if defType == constants.STORAGE:
            StorageService().sync_defn(auth, server_ids, def_id, site_id, group_id)
        else:
            if defType == constants.NETWORK:
                NetworkService().sync_defn(auth, server_ids, def_id, site_id, group_id)

    def resume_task(self, auth, ctx, server_ids, def_id, site_id, group_id, defType):
        try:
            return self.exec_task(auth, ctx, server_ids, def_id, site_id, group_id, defType)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, server_ids, def_id, site_id, group_id, defType):
        try:
            return self.exec_task(auth, ctx, server_ids, def_id, site_id, group_id, defType)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)



class UpdateDeploymentStatusTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec_task for UpdateDeploymentStatus Task')
        from stackone.core.utils.utils import update_deployment_status
        update_deployment_status()



class SendDeploymentStatsTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec_task for SendDeploymentStats Task')
        from stackone.core.utils.utils import send_deployment_stats
        send_deployment_stats(True)



class SendDeploymentStatsRptTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec_task for SendDeploymentStatsRptTask Task')
        from stackone.core.utils.utils import send_deployment_stats
        send_deployment_stats(False)



class CheckForUpdateTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec_task for CheckForUpdate Task')
        AppUpdateManager().check_for_updates(True)



class NodeAvailTask(Task):
    def get_descriptions(self):
        pass

    def get_status(self):
        return get_parent_task_status_info(self)

    def exec_task(self, auth, ctx):
        try:
            stackone.model.LicenseManager.LICENSE_CHECK_TIMER += 1
            if stackone.model.LicenseManager.LICENSE_CHECK_TIMER > 1000:
                stackone.model.LicenseManager.LICENSE_CHECK_TIMER = 0
                ret,msg = check_all_lic(auth)
                if ret == False:
                    stackone.model.LicenseManager.set_violated()
                    stackone.model.LicenseManager.LICENSE_VIOLATED_MSG = msg
                    LOGGER.debug('License violation.' + msg)
                transaction.commit()
        except Exception as e:
            LOGGER.debug('error while checking license.\n' + to_str(e))
        LOGGER.debug('node availability task is running')
        strt = p_task_timing_start(AVL_LOGGER, 'NodeAvailTask', [])
        AvailabilityWorker(auth).do_work()
        p_task_timing_end(AVL_LOGGER, strt)

    def resume_task(self, auth, ctx):
        try:
            AvailabilityWorker(auth).resume_work(ctx)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx):
        try:
            self.resume_task(auth, ctx)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)



class NodesAvailability(WorkerTask):
    def get_descriptions(self):
        pass

    def get_status(self):
        return get_child_task_status_info(self)

    def exec_task(self, auth, ctx, node_ids):
        LOGGER.debug('entered in exec task for NodesAvailability task')
        strt = p_task_timing_start(AVL_LOGGER, 'NodesAvailability', node_ids)
        try:
            self.completed_nodes = []
            self.pending_nodes = [node_id for node_id in node_ids]
            self.exc_node_ids = [node_id for node_id in node_ids]
            index=0
            node_id = self.get_next_node_id(index)
            while node_id is not None:
                self.pending_nodes.remove(node_id)
                node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
                index +=1
                node_id = self.get_next_node_id(index)
                if node:
                    self.current_node = node
                    self.start_time = datetime.now()
                    try:
                        try:
                            strt1 = p_task_timing_start(AVL_LOGGER,'NodeRefreshAvail',node.id)
                            node.refresh_avail()
                            p_task_timing_end(AVL_LOGGER,strt1)
                        except Exception as e:
                            LOGGER.error('Error updating Node availability . Server :' + node.hostname)
                            traceback.print_exc()
                    finally:
                        self.completed_nodes.append(node.id)
        finally:
            self.check_if_hung()
            p_task_timing_end(AVL_LOGGER, strt)

    def resume_task(self, auth, ctx, node_ids):
        try:
            self.do_cleanup()
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, node_ids):
        try:
            self.resume_task(auth, ctx, node_ids)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)

    def get_max_wait_time(self):
        try:
            max_node_avail_wait_time = int(tg.config.get('max_node_avail_wait_time'))
        except Exception as e:
            LOGGER.error('Exception: ' + str(e))
            max_node_avail_wait_time = 45L
        return max_node_avail_wait_time



class VMAvailTask(Task):
    def get_descriptions(self):
        pass

    def get_status(self):
        return get_parent_task_status_info(self)

    def exec_task(self, auth, ctx):
        LOGGER.debug('vm availability task is running')
        strt = p_task_timing_start(AVL_LOGGER, 'VMAvailTask', [])
        VMAvailabilityWorker(auth).do_work()
        p_task_timing_end(AVL_LOGGER, strt)

    def resume_task(self, auth, ctx):
        try:
            VMAvailabilityWorker(auth).resume_work(ctx)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx):
        try:
            self.resume_task(auth, ctx)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)



class VMAvailability(WorkerTask):
    def get_descriptions(self):
        pass

    def get_status(self):
        return get_child_task_status_info(self)

    def exec_task(self, auth, ctx, node_ids):
        LOGGER.debug('entered in exec task for VMAvailability task')
        strt = p_task_timing_start(AVL_LOGGER, 'VMAvailability', node_ids)
        try:
            self.completed_nodes = []
            self.pending_nodes = [node_id for node_id in node_ids]
            self.exc_node_ids = [node_id for node_id in node_ids]
            index = 0
            node_id = self.get_next_node_id(index)
            while node_id is not None:
                self.pending_nodes.remove(node_id)
                node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
                index +=1
                node_id = self.get_next_node_id(index)
                if node and node.is_up():
                    self.current_node = node
                    self.start_time = datetime.now()
                    try:
                        try:
                            strt1 = p_task_timing_start(AVL_LOGGER,'RefreshVMAvail',node.id)
                            node.refresh_vm_avail()
                            p_task_timing_end(AVL_LOGGER, strt1)
                        except Exception as e:
                            LOGGER.error('Error updating VM availability . Server :' + node.hostname)
                            traceback.print_exc()
                    finally:
                        self.completed_nodes.append(node.id)
        finally:
            self.check_if_hung()
            p_task_timing_end(AVL_LOGGER, strt)
    
    def resume_task(self, auth, ctx, node_ids):
        try:
            self.do_cleanup()
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, node_ids):
        try:
            self.resume_task(auth, ctx, node_ids)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)

    def get_max_wait_time(self):
        try:
            max_vm_avail_wait_time = int(tg.config.get('max_vm_avail_wait_time'))
        except Exception as e:
            LOGGER.error('Exception: ' + str(e))
            max_vm_avail_wait_time = 60L
        return max_vm_avail_wait_time



class HAVMAvailability(VMAvailability):
    __doc__ = '\n    task for running vm availability as soon as a node is detected up\n    '
    def get_descriptions(self):
        node_ids = self.get_param('node_ids')
        if node_ids:
            node_id = node_ids[0L]
            name = node_id
            try:
                node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
                name = node.hostname
            except Exception as e:
                pass
        short_desc = m_('HAVMAvailability %s')
        desc = m_('VMAvailability on %s started by HA ')
        return (short_desc, (name), desc, name)




class VMRemoveTask(NodeTask):
    def get_descriptions(self):
        dom_name = self.get_dom_name()
        node_name = self.get_node_name()
        short_desc = ''
        desc = ''
        short_desc = m_('Deleting %s')
        desc = m_('Remove action on %s. Managed Node is %s')
        return (short_desc, (dom_name), desc, (dom_name, node_name))

    def exec_task(self, auth, ctx, dom_id, node_id, force):
        manager = Basic.getGridManager()
        return manager.remove_vm(auth, dom_id, node_id, force)

    def resume_task(self, auth, ctx, dom_id, node_id, force):
        try:
            vm = DBSession.query(VM).filter(VM.id == dom_id).first()
            LOGGER.debug('resuming remove vm')
            if vm is None:
                LOGGER.debug('vm is already removed')
                from stackone.model.availability import VMStateHistory
                VMStateHistory.remove_vm_states(node_id, dom_id, all=True)
            else:
                manager = Basic.getGridManager()
                return manager.remove_vm(auth, dom_id, node_id, force)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)
        return None

    def recover_task(self, auth, ctx, dom_id, node_id, force):
        try:
            self.resume_task(auth, ctx, dom_id, node_id, force)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)



class VMImportTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_node_name()
        action = self.get_param('action')
        short_desc = ''
        if action == 'import_vm':
            short_desc = m_('Importing Virtual Machine on %s')
        else:
            if action == 'import_vms':
                short_desc = m_('Importing Virtual Machines on %s')
        return (short_desc, (node_name), short_desc, (node_name))

    def exec_task(self, auth, ctx, node_id, action, paths, external_manager_id):
        manager = Basic.getGridManager()
        managed_node = manager.getNode(auth, node_id)
        if managed_node is not None:
            if not managed_node.is_authenticated():
                managed_node.connect()
                return manager.import_dom_configs(auth, node_id, paths, external_manager_id)
        else:
            raise Exception('Can not find the managed node')
        return None

    def resume_task(self, auth, ctx, node_id, action, paths, external_manager_id):
        try:
            return self.exec_task(auth, ctx, node_id, action, paths, external_manager_id)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)

    def recover_task(self, auth, ctx, node_id, action, paths, external_manager_id):
        try:
            return self.exec_task(auth, ctx, node_id, action, paths, external_manager_id)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)



class EmailTask(Task):
    def get_descriptions(self):
        short_desc = m_('Sending E-mail for failed task')
        return (short_desc, (), short_desc, ())

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec task E-mail sending task')
        manager = Basic.getGridManager()
        manager.send_notifications(auth)



class UpdateDiskSize(Task):
    def get_descriptions(self):
        short_desc = m_('Updating the actual size of the disk')
        return (short_desc, (), short_desc, ())

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in excec_task for Updating the size task')
        StorageService().update_disks_size(auth)



class BackupVMTask(NodeTask):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, dom_id, backup_config):
        LOGGER.debug('entered in excec_task for backup vm task')
        return BackupService().VMBackup(auth, dom_id, backup_config)

    def resume_task(self, auth, ctx, dom_id, backup_config):
        LOGGER.debug('entered in resume_task for backup vm task')
        from stackone.model.Backup import VMBackupResult
        bkup_rec = DBSession.query(VMBackupResult).filter(VMBackupResult.backup_id == backup_config.id).filter(VMBackupResult.vm_id == dom_id).filter(VMBackupResult.status == u'Running').first()
        if bkup_rec:
            seq = 500L
            try:
                bkup_svc = BackupService()
                seq = bkup_svc.cleanup(seq, bkup_rec.vm_id, bkup_rec.id)
                bkup_svc.update_backup_status(bkup_rec)
            except Exception as e:
                raise Exception(constants.INCOMPLETE_TASK + '\nTrying to do cleanup.\n' + to_str(e))
            raise Exception(constants.INCOMPLETE_TASK + '\nCleanup completed successfully.')
        raise Exception(constants.INCOMPLETE_TASK)

    def recover_task(self, auth, ctx, dom_id, backup_config):
        LOGGER.debug('entered in recover_task for backup vm task')
        self.resume_task(auth, ctx, dom_id, backup_config)



class BackupTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, group_id, backup_config):
        LOGGER.debug('entered in excec_task for backup task')
        return self.InitiateSPBackup(auth, group_id, backup_config)

    def InitiateSPBackup(self, auth, group_id, backup_config):
        try:
            purge_interval = None
            ent = auth.get_entity(group_id)
            if not auth.has_privilege('EXEC_BACKUP_POLICY', ent):
                raise Exception(constants.NO_PRIVILEGE)
            backup_manager = BackupService().getBackupManager()
            sp_bkp_config = backup_manager.get_sp_backup_config(backup_config.id)
            if sp_bkp_config:
                sp_bkp_config.num_runs = sp_bkp_config.num_runs + 1
                purge_interval = sp_bkp_config.rel_sch_conf.backup_purge_days
            manager = Basic.getGridManager()
            from stackone.viewModel.TaskCreator import TaskCreator
            tc = TaskCreator()
            server_list = manager.getNodeList(auth, group_id)
            err_doms = []
            if server_list:
                for server in server_list:
                    vm_list = manager.get_doms(auth, server.id)
                    if vm_list:
                        for vm in vm_list:
                            if TaskUtil.is_cancel_requested() == True:
                                err_str = 'Error in Virtual Machines:- ' + to_str(err_doms)
                                return dict(status=constants.TASK_CANCELED, msg=constants.TASK_CANCEL_MSG, results=err_str)
                            sp_bkp_config = backup_manager.get_sp_backup_config(backup_config.id)
                            p_settings = sp_bkp_config.rel_setting_conf
                            #LOGGER.info('Include All VM option is ' + to_str(p_settings.includeAll_VM))
                            #if not p_settings.includeAll_VM:
                            LOGGER.info('Checking for allow VM backup...')
                            is_allow_backup = BackupService().allow_vm_backup(backup_config.id, vm.id)
                            if is_allow_backup == False:
                                LOGGER.info(to_str(vm.name) + ' VM is not allowed for backup')
                                err_doms.append(to_str(vm.name) + ' VM is not allowed for backup')
                            else:
                                try:
                                    task_id = tc.backup_vm_task(auth, vm.id, backup_config.id)
                                    wait_time = tg.config.get('backup_time')
                                    wait_time = int(wait_time)
                                    LOGGER.info('vm backup task time is ' + to_str(wait_time))
                                    LOGGER.info('Calling wait for task for SP level VM backup task...')
                                    wait_for_task_completion(task_id, wait_time)
                                except Exception as ex:
                                    traceback.print_exc()
                                    LOGGER.error('Error in submitting task: ' + to_str(ex).replace("'", ''))
                                    err_doms.append('Error in submitting task: ' + to_str(ex))
            if purge_interval:
                tc.purge_backup_task(auth, group_id, backup_config.id)
            else:
                desc = "Retention days are not found for the backup policy '" + to_str(backup_config.name) + "'"
                LOGGER.info(desc)

        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex).replace("'", ''))




class RestoreVMTask(NodeTask):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, server_id, vm_id, backup_config, result_id, ref_disk):
        LOGGER.debug('entered in excec_task for restore vm task')
        return RestoreService().restore_vm(auth, server_id, vm_id, result_id, backup_config, ref_disk)

    def resume_task(self, auth, ctx, server_id, vm_id, backup_config, result_id, ref_disk):
        LOGGER.debug('entered in resume_task for restore vm task')
        from stackone.model.Restore import VMRestoreResult
        rstr_rec = DBSession.query(VMRestoreResult).filter(VMRestoreResult.backup_id == backup_config.id).filter(VMRestoreResult.vm_id == vm_id).filter(VMRestoreResult.status == u'Running').first()
        if rstr_rec:
            try:
                rstr_svc = RestoreService()
                rstr_svc.cleanup(rstr_rec.vm_id, rstr_rec.id, rstr_rec.backup_result_id)
                rstr_svc.update_restore_status(rstr_rec)
            except Exception as e:
                raise Exception(constants.INCOMPLETE_TASK + '\nTrying to do cleanup.\n' + to_str(e))
            raise Exception(constants.INCOMPLETE_TASK + '\nCleanup completed successfully.')
        raise Exception(constants.INCOMPLETE_TASK)

    def recover_task(self, auth, ctx, server_id, vm_id, backup_config, result_id, ref_disk):
        LOGGER.debug('entered in recover_task for restore vm task')
        self.resume_task(auth, ctx, server_id, vm_id, backup_config, result_id, ref_disk)



class HAEventTask(Task):
    def mark_started(self, event_id, task_id):
        try:
            import transaction
            transaction.begin()
            from stackone.core.ha.ha_register import HAEvent
            event = DBSession.query(HAEvent).filter(HAEvent.event_id == event_id).first()
            event.mark_started(task_id)
        finally:
            transaction.commit()

    def mark_finished(self, event_id, status):
        try:
            import transaction
            transaction.begin()
            from stackone.core.ha.ha_register import HAEvent
            event = DBSession.query(HAEvent).filter(HAEvent.event_id == event_id).first()
            event.mark_finished(status)
        finally:
            transaction.commit()



class HATask(HAEventTask):
    def get_descriptions(self):
        group = self.get_param('group_name')
        short_desc = m_('High Availability Task')
        desc = m_('High Availability Task on ' + group + ' at ' + to_str(self.submitted_on))
        return (short_desc, (), desc, ())

    def exec_task(self, auth, ctx, group_id, group_name):
        LOGGER.debug('entered in exec_task of High Availability Task for' + group_name + '(' + group_id + ')')
        from stackone.core.ha.ha_main import HA
        from stackone.core.ha.ha_register import HAEvent
        ha_events = DBSession.query(HAEvent).filter(HAEvent.sp_id == group_id).filter(HAEvent.status == HAEvent.IDLE).order_by(HAEvent.event_id.asc()).all()
        ha = HA()
        msg = ''
        i = 0L
        result = []
        failure = False
        for event in ha_events:
            i += 1L
            status = HA.FAILURE
            self.mark_started(event.event_id, self.task_id)
        try:
            ev_msg,status = ha.handle_event(auth, event.event_id, event.entity_id, event.avail_state, event.event_time, group_id)
            result.append('HAEvent ' + str(event.event_id) + ':' + str(status))
            if status != HA.SUCCESS:
                failure = True
            msg += ev_msg
        finally:
            self.mark_finished(event.event_id, status)
        if i > 1L:
            msg += '\n==============================\n'
            msg += 'Summary:' + str(result) + '\n'
        if failure == True:
            raise Exception(msg)
        return msg

    def resume_task(self, auth, ctx, group_id, group_name):
        LOGGER.debug('entered in resume_task of High Availability Task for' + group_name + '(' + group_id + ')')
        from stackone.core.ha.ha_main import HA
        from stackone.core.ha.ha_register import HAEvent, HARegister
        ha_events = DBSession.query(HAEvent).filter(HAEvent.sp_id == group_id).filter(HAEvent.status == HAEvent.STARTED).order_by(HAEvent.event_id.asc()).all()
        ha = HA()
        msg = constants.RESUME_TASK
        i = 0
        result = []
        failure = False
        for event in ha_events:
            self.mark_started(event.event_id,self.task_id)
            ha_reg = DBSession.query(HARegister).filter(HARegister.entity_id == event.entity_id).first()
            if ha_reg and ha_reg.ha_state not in [HARegister.FAILOVER_COMPLETE]:
                i += 1
                ev_msg,status = ha.resume_event(auth, event.event_id, event.entity_id, event.avail_state, event.event_time, ha_reg.ha_state, group_id)
                result.append('High Availability Event ' + str(event.event_id) + ':' + str(status))
                if status != HA.SUCCESS:
                    failure = True
                msg += ev_msg
            self.mark_finished(event.event_id, status)
        if i > 1:
            msg += '\n==============================\n'
            msg += 'Summary:' + str(result) + '\n'
        if failure == True:
            raise Exception(msg)
        return msg
    def recover_task(self, auth, ctx, group_id, group_name):
        try:
            return self.resume_task(auth, ctx, group_id, group_name)
        except Exception as e:
            msg = constants.RECOVER_TASK + to_str(e)
            raise Exception(msg)


    # def recover_task(self, auth, ctx, group_id, group_name):
        # try:
            # return self.resume_task(auth, ctx, group_id, group_name)
        # except Exception as e:
            # msg = constants.RECOVER_TASK + to_str(e)
            # raise Exception(msg)



class HARecoveryTask(HAEventTask):
    def get_descriptions(self):
        group = self.get_param('group_name')
        short_desc = m_('High Availability Recovery Task')
        desc = m_('High Availability Recovery Task on ' + group + ' at ' + to_str(self.submitted_on))
        return (short_desc, (), desc, ())

    def exec_task(self, auth, ctx, group_id, group_name):
        LOGGER.debug('entered in exec_task of High Availability Recovery Task for' + group_name + '(' + group_id + ')')
        from stackone.core.ha.ha_main import HA
        from stackone.core.ha.ha_register import HAEvent, HARegister
        ha_events = DBSession.query(HAEvent).filter(HAEvent.sp_id == group_id).filter(HAEvent.status == HAEvent.STARTED).order_by(HAEvent.event_id.asc()).all()
        ha = HA()
        msg = ''
        i = 0L
        result = []
        failure = False
        for event in ha_events:
            self.mark_started(event.event_id, self.task_id)
            ha_reg = DBSession.query(HARegister).filter(HARegister.entity_id == event.entity_id).first()
        if ha_reg and ha_reg.ha_state not in [HARegister.NOT_ACTIVE, HARegister.FAILOVER_COMPLETE]:
            i += 1L
            ev_msg = ha.resume_event(auth, event.event_id, event.entity_id, event.avail_state, event.event_time, ha_reg.ha_state)
            result.append('HAEvent ' + str(event.event_id) + ':' + str(status))
            if status != HA.SUCCESS:
                failure = True
            msg += ev_msg
        else:
            ha_reg
        self.mark_finished(event.event_id, status)
        if i > 1L:
            msg += '\n==============================\n'
            msg += 'Summary:' + str(result) + '\n'
        if failure == True:
            raise Exception(msg)
        return msg



class EmailNotificationTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx):
        LOGGER.debug('entered in exec_task for notification entry task')
        NodeService().schedule_email_notification()



class CancelTask(Task):
    def get_descriptions(self):
        short_desc = 'Cancel Task'
        task_id = self.get_param('task_id')
        tname = ' Unknown '
        t = DBSession.query(Task).filter(Task.task_id == task_id).first()
        if t:
            tname = t.name
        desc = 'Cancel Task for task : ' + tname
        return (short_desc, (), desc, ())

    def exec_task(self, auth, ctx, task_id):
        LOGGER.debug('entered in exec_task for cancel task')
        t = DBSession.query(Task).filter(Task.task_id == task_id).first()
        if t and t.is_cancellable() == True:
            t.request_cancel()
            transaction.commit()
            t = DBSession.query(Task).filter(Task.task_id == task_id).first()
            t.cancel()



class AssociateDefnsTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, site_id, group_id, def_type, def_ids, op_level):
        LOGGER.debug('entered in excec_task for associate definitions task')
        if def_type == constants.STORAGE:
            StorageService().associate_defns(site_id, group_id, def_type, def_ids, auth, op_level)
        else:
            if def_type == constants.NETWORK:
                NetworkService().associate_defns(site_id, group_id, def_type, def_ids, auth, op_level)



class PurgeBackup(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, group_id, backup_config_id):
        LOGGER.debug('entered in excec_task for purge backup task')
        BackupService().purge_backup(auth, group_id, backup_config_id)



class AddNetworkDefinition(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, nw_name, nw_desc, nw_type, nw_bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id=None, group_id=None, node_id=None, op_level=None, nw_gateway=None, nw_ip_address=None, nw_use_vlan=None, nw_vlan_id=None, nw_isbonded=None, nw_slaves=None, interface=None, vlan_id_pool_id=None, sp_ids=None, csep_context_id=None, csep_id=None, nw_id=None):
        LOGGER.debug('entered in excec_task for add network definition task')
        NetworkService().add_nw_defn(auth, nw_name, nw_desc, nw_type, nw_bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id, group_id, node_id, op_level, nw_gateway, nw_ip_address, nw_use_vlan, nw_vlan_id, nw_isbonded, nw_slaves, interface, vlan_id_pool_id, sp_ids, csep_context_id, csep_id, nw_id)



class RemoveNetworkDefinition(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, def_id, site_id=None, group_id=None, node_id=None, op_level=None, csep_id=None):
        LOGGER.debug('entered in excec_task for remove network definition task')
        NetworkService().remove_nw_defn(auth, def_id, site_id, group_id, node_id, op_level, csep_id)



class AddStorageDefTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, site_id, group_id, node_id, type, opts, op_level, sp_ids, added_manually, scan_result):
        LOGGER.debug('entered in excec_task for add storage definition task')
        StorageService().add_storage_def(auth, site_id, group_id, node_id, type, opts, op_level, sp_ids, added_manually, scan_result)



class RemoveStorageDefTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, storage_id, site_id, group_id, op_level):
        LOGGER.debug('entered in excec_task for remove storage definition task')
        StorageService().remove_storage_def(auth, storage_id, site_id, group_id, op_level)



class PurgeSingleBackup(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, result_id):
        LOGGER.debug('entered in excec_task for purge single backup task')
        BackupService().purge_single_backup(auth, result_id)



class SPDWMTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, sp_id):
        print '\nDWM  task\n'
        LOGGER.debug('Entered in excec_task for SPDWMTask')
        msg,policy_active = DWMManager().dwm(auth, sp_id)
        return dict(results=msg, visible=policy_active, status=Task.SUCCEEDED)



class SPDWMCalendarTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, sp_id, policy, mode):
        print '\n\n DWM Calendar Task \n\n'
        LOGGER.debug('Entered in excec_task for SPDWMCalendarTask')
        msg = SPDWMPolicy.set_sp_current_policy(sp_id, policy, mode)
        transaction.commit()
        msg += SPDWMPolicy.ps_check_down_nodes(auth, sp_id, policy, mode)
        return dict(results=msg, visible=True, status=Task.SUCCEEDED)



class AddAnnotationTask(Task):
    def get_descriptions(self):
        short_desc = m_('Add Annotation Task')
        desc = m_('Add Annotation Task at ' + to_str(self.submitted_on))
        return (short_desc, (), desc, ())

    def exec_task(self, auth, ctx, node_id, text, user):
        LOGGER.debug('Entered in excec_task for AddAnnotationTask')
        msg = NodeService().process_annotation(auth, node_id, text, user)
        return dict(results=msg, visible=True, status=Task.SUCCEEDED)



class EditAnnotationTask(Task):
    def get_descriptions(self):
        short_desc = m_('Edit Annotation Task')
        desc = m_('Edit Annotation Task at ' + to_str(self.submitted_on))
        return (short_desc, (), desc, ())

    def exec_task(self, auth, ctx, node_id, text, user):
        LOGGER.debug('Entered in excec_task for EditAnnotationTask')
        msg = NodeService().process_annotation(auth, node_id, text, user)
        return dict(results=msg, visible=True, status=Task.SUCCEEDED)



class ClearAnnotationTask(Task):
    def get_descriptions(self):
        short_desc = m_('Clear Annotation Task')
        desc = m_('Clear Annotation Task at ' + to_str(self.submitted_on))
        return (short_desc, (), desc, ())

    def exec_task(self, auth, ctx, node_id):
        LOGGER.debug('Entered in excec_task for ClearAnnotationTask')
        msg = NodeService().clear_annotation(auth, node_id)
        return dict(results=msg, visible=True, status=Task.SUCCEEDED)



class AddVLANIDPoolTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, site_id, name, desc, range, interface, sp_ids, cidr, num_hosts):
        LOGGER.debug('entered in excec_task for add vlan id pool definition task')
        VLANService().add_vlan_id_pool(auth, site_id, name, desc, range, interface, sp_ids, cidr, num_hosts)



class EditVLANIDPoolTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, site_id, vlan_id_pool_id, desc, range, sp_ids, name):
        LOGGER.debug('entered in excec_task for add vlan id pool definition task')
        VLANService().edit_vlan_id_pool(auth, site_id, vlan_id_pool_id, desc, range, sp_ids, name)



class RemoveVLANIDPoolTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, vlan_id_pool_id):
        LOGGER.debug('entered in excec_task for remove vlan id pool definition task')
        VLANService().remove_vlan_id_pool(vlan_id_pool_id)



class CreateDiskTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, context, managed_node):
        LOGGER.debug('entered in excec_task for create disk task')
        StorageService().create_disk(context, managed_node)



class RemoveDiskTask(Task):
    def get_descriptions(self):
        pass

    def exec_task(self, auth, ctx, context, managed_node):
        LOGGER.debug('entered in excec_task for remove disk task')
        StorageService().remove_disk(context, managed_node)



class CreateImageFromVMTask(NodeTask):
    __doc__ = '\n    '
    def get_descriptions(self):
        image_name = self.get_param('image_name')
        short_desc = m_('Create Template %s')
        desc = m_('Create Template %s From Virtual Machine')
        return (short_desc, image_name, desc, image_name)

    def exec_task(self, auth, ctx, node_id, image_name, image_group_id, context):
        image_service = ImageService()
        msg = image_service.create_image_from_vm(auth, node_id, image_name, image_group_id, context, self.task_id)
        return dict(results=msg, status=Task.SUCCEEDED)

    def resume_task(self, auth, ctx, node_id, image_name, image_group_id, context):
        try:
            image_service = ImageService()
            msg = image_service.create_image_from_vm_recovery_cleaning(auth, node_id, image_name, image_group_id, context, self.task_id)
            return dict(results=msg, visible=True, status=Task.SUCCEEDED)
        except Exception as e:
            msg = constants.RESUME_TASK + to_str(e)
            raise Exception(msg)



class ImportVcenterTask(NodeTask):
    def get_descriptions(self):
        from stackone.model.vCenter import VCenter
        vcenter_id = self.get_param('vcenter_id')
        vc = DBSession.query(VCenter).filter(VCenter.id == vcenter_id).first()
        short_desc = m_('Importing vCenter %s')
        desc = m_('Importing vCenter %s')
        return (short_desc, (vc.host), desc, (vc.host))

    def exec_task(self, auth, ctx, site_id, vcenter_id, context_dict):
        vcenter_service = VcenterService()
        msg = vcenter_service.import_managed_objects_from_vcenter(auth, site_id, vcenter_id, context_dict)
        return dict(results=msg, status=Task.SUCCEEDED)



class ImportVcenterTemplatesTask(NodeTask):
    def get_descriptions(self):
        node_name = self.get_node_name()
        short_desc = m_('Importing Templates on %s')
        desc = m_('Importing Templates on %s')
        return (short_desc, (node_name), desc, (node_name))

    def exec_task(self, auth, ctx, node_id, dc_id, vcenter_id, dc):
        vcenter_service = VcenterService()
        msg = vcenter_service.import_vcenter_templates(auth, node_id, dc_id, vcenter_id, dc)
        return dict(results=msg, status=Task.SUCCEEDED)



class DeleteImageTask(NodeTask):
    __doc__ = '\n    '
    def get_descriptions(self):
        image_id = self.get_param('image_id')
        image = DBSession.query(Image).filter(Image.id == image_id).first()
        short_desc = m_('Deleteing Template %s' % image.name)
        desc = m_('Delete Template %s' % image.name)
        return (short_desc, (), desc, ())

    def exec_task(self, auth, ctx, image_id, group_id):
        image_service = ImageService()
        msg = image_service.remove_image(auth, image_id, group_id)
        return dict(results=msg, status=Task.SUCCEEDED)

    def get_entity_ids(self):
        group_id = self.get_param('group_id')
        return group_id



class CloneTemplateTask(NodeTask):
    __doc__ = '\n    '
    def get_descriptions(self):
        image_id = self.get_param('image_id')
        image = DBSession.query(Image).filter(Image.id == image_id).first()
        short_desc = m_('Cloning Template %s' % image.name)
        desc = m_('Cloning Template %s' % image.name)
        return (short_desc, (), desc, ())

    def exec_task(self, auth, ctx, image_id, image_name, group_id):
        image_service = ImageService()
        msg = image_service.clone_image(auth, image_id, image_name, group_id)
        return dict(results=msg, status=Task.SUCCEEDED)



