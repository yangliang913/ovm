from stackone.config.app_cfg import base_config
from stackone.model.services import ServiceItem
from stackone.core.services.tasks import *
from stackone.model.services import TaskInterval
from datetime import datetime
from stackone.model import DBSession
import Basic
import logging
from stackone.model.Backup import BackupManager
from stackone.model.VM import VM
from stackone.model.SPRelations import ServerDefLink, CSEPDefLink
from stackone.model.LicenseManager import check_platform_expire_date
from stackone.core.utils.utils import getDateTime
from stackone.core.utils.utils import to_unicode, to_str
from stackone.model.services import TaskInterval, Task, TaskCalendar
logger = logging.getLogger('stackone.viewModel')

class TaskCreator():
    #PASSED
    def __init__(self):
        s = DBSession.query(ServiceItem).filter(ServiceItem.name == to_unicode('Task Manager Service')).one()
        self.task_service_id = s.id
        self.svc_central = base_config.stackone_service_central

    #PASSED
    def get_running_task_info(self):
        task_service = self.svc_central.get_service(self.task_service_id)
        return task_service.get_running_task_info()

    #PASSED
    def delete_task(self, task_ids):
        task_service = self.svc_central.get_service(self.task_service_id)
        task_service.delete_task(task_ids)

    #PASSED
    def _get_username(self, auth):
        if auth.user:
            return auth.user.user_name
            
        if auth.user_name:
            return auth.user_name
    def clone_template_task(self, auth, image_id, image_name, group_id, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = CloneTemplateTask(u'Clone Template',{},[],dict(image_id = image_id,image_name = image_name,group_id = group_id),None,user_name)
        t.set_entity_details(group_id)
        execution_time = getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t,execution_time)
        logger.debug('Clone Template Task Submitted')
        return t.task_id
    def ha_vm_availability(self, auth, node_id):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = HAVMAvailability(u'Update VM Availability : HA',{},[],dict(node_ids = [node_id]),None,user_name)
        t.set_entity_details(node_id)
        execution_time = getDateTime(dateval,timeval)
        task_service.submit_sync(t)
        logger.debug('HAVMAvailability Task Submitted')
        return t.task_id
    
    #add 0901       
    def send_deployment_stats(self):
        t = SendDeploymentStatsTask(u'Send Deployment Stats', {'quiet': True}, [], dict(), None, u'admin')
        dc_ent = DBSession.query(Entity).filter(Entity.type_id == 1L).first()
        t.set_entity_info(dc_ent)
        t.set_interval(TaskInterval( interval = None,  next_execution = datetime.now()))
        DBSession.add(t)
        import transaction
        transaction.commit()
        logger.debug('SendDeploymentStatsTask Submitted')
        return t.task_id

    #PASSED
    def vm_action(self, auth, dom_id, node_id, action, dateval=None, timeval=None, requester=constants.CORE, task_exe_context=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = VMActionTask(action, {}, [], dict(dom_id=dom_id, node_id=node_id, action=action, requester=requester, task_exe_context=task_exe_context), None, user_name)
        t.set_entity_details(dom_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('VM Action Task Submitted')
        return t.task_id

    #PASSED
    def server_action(self, auth, node_id, action, requester=None, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = ServerActionTask(action, {}, [], dict(node_id=node_id, action=action, requester=requester), None, user_name)
        t.set_entity_details(node_id)
        t.cancellable = True
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Server Action Task Submitted')
        return t.task_id

    #PASSED
    def remove_node(self, auth, node_id, node_name, grp_id, grp_name, force, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RemoveServerTask(u'Remove ' + node_name, {}, [], dict(node_id=node_id, node_name=node_name, grp_id=grp_id, grp_name=grp_name, force=force), None, user_name)
        t.set_entity_details(node_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Remove Server Task Submitted')
        return t.task_id

    #PASSED
    def migrate_vm(self, auth, dom_list, source_node_id, dest_node_id, live, force, all, dateval=None, timeval=None, requester=constants.CORE):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        isLive = False
        isForce = False
        migrate_all = False
        if live == 'true':
            isLive = True
        if force == 'true':
            isForce = True
        if all == 'true':
            migrate_all = True
        t = VMMigrateTask(u'Migrate', {}, [], dict(dom_list=dom_list, source_node_id=source_node_id, dest_node_id=dest_node_id, live=isLive, force=isForce, all=migrate_all, requester=requester), None, user_name)
        if all == 'true':
            t.set_entity_details(dest_node_id)
            t.cancellable = True
        else:
            t.set_entity_details(dom_list[0])
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Migrate Task Submitted')
        return t.task_id

    #PASSED
    def config_settings(self, auth, image_id, config, mode, node_id, group_id, dom_id, vm_name, dateval=None, timeval=None, cli=False, memory=None, vcpu=None, cloud=None, csep_context=None, network={}, csep_id=None, vdc_name=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = VMConfigSettingsTask(u'Provision', {}, [], dict(image_id=image_id, config=config, mode=mode, node_id=node_id, group_id=group_id, dom_id=dom_id, vm_name=vm_name, cli=cli, memory=memory, vcpu=vcpu, cloud=cloud, csep_context=csep_context, network=network, csep_id=csep_id, vdc_name=vdc_name), None, user_name)
        if mode == 'PROVISION_VM':
            t.set_entity_details(node_id)
        else:
            if mode == 'EDIT_VM_INFO':
                manager = Basic.getGridManager()
                managed_node = manager.getNode(auth, node_id)
                if managed_node is not None:
                    dom = managed_node.get_dom(dom_id)
                    t.set_entity_details(dom.id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Configuration Task Submitted')
        return t.task_id

    #PASSED
    def save_vm(self, auth, dom_id, node_id,  directory, file, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = VMSnapshotTask(u'HIBERNATE_VM', {}, [], dict(dom_id=dom_id, node_id=node_id, file=file, directory=directory), None, user_name)
        t.set_entity_details(dom_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Snapshot Task Submitted')
        return t.task_id

    #PASSED
    def restore_vm(self, auth, node_id, file, dateval=None, timeval=None):
        managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
        #managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == nodeId).first()
        ret,msg = check_platform_expire_date(managed_node.get_platform())
        if ret == False:
            raise Exception(msg)
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = VMRestoreTask(u'Restore', {}, [], dict(node_id=node_id, file=file), None, user_name)
        t.set_entity_details(node_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Restore Task Submitted')
        return t.task_id
    #def restore_vm(self, auth, node_id, file, dateval=None, timeval=None):
    #   user_name = self._get_username(auth)
    #    t.set_entity_details(node_id)
     #   execution_time = getDateTime(dateval, timeval)
    #    if execution_time is None:
     #       task_service.submit_sync(t)
     #   else:
     #       task_service.submit_schedule(t, execution_time)
     #   logger.debug('Restore Task Submitted')
     #   return t.task_id

    #PASSED
    def import_appliance(self, auth, appliance_entry, image_store, group_id, image_name, platform, force, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = ImportApplianceTask(u'Import Appliance', {}, [], dict(appliance_entry=appliance_entry, image_store=image_store, group_id=group_id, image_name=image_name, platform=platform, force=force), None, user_name)
        t.set_entity_details(group_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Import appliance task submitted')
        return t.task_id

    #PASSED
    def refresh_node_metrics(self):
        task_service = self.svc_central.get_service(self.task_service_id)
        t = DBSession.query(Task).filter(Task.name == u'Refresh Node Metrics').one()
        task_service.submit_task(t, 2)
        logger.debug('Refresh Node Metrics task submitted')

    #PASSED
    def sync_all_task(self, auth, site_id, group_id, def_type):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = SyncAllOp(u'Sync All', {}, [], dict(site_id=site_id, group_id=group_id, def_type=def_type), None, user_name)
        t.set_entity_details(group_id)
        task_service.submit_sync(t)
        logger.debug('Sync All task submitted')
        return None

    #PASSED
    def sync_server_task(self, auth, node_id):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = SyncServerOp(to_unicode('Sync Server'), {}, [], dict(node_id=node_id), None, user_name)
        t.set_entity_details(node_id)
        task_service.submit_sync(t)
        logger.debug('Sync Server task submitted')
        return t.task_id

    #PASSED
    def server_sync_task(self, auth, node_id, def_type, sync_forcefully):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        entity_name = Entity.getEntityName(node_id)
        name = to_unicode('Sync Task for Server : ' + entity_name)
        if def_type == constants.STORAGE:
            name = to_unicode('Storage Sync')
        else:
            if def_type == constants.NETWORK:
                name = to_unicode('Network Sync')
        t = ServerSyncOp(name, {}, [], dict(node_id=node_id, def_type=def_type, sync_forcefully=sync_forcefully), None, user_name)
        t.set_entity_details(node_id)
        task_service.submit_sync(t)
        logger.debug('Server Sync task submitted')
        return t.task_id

    #PASSED
    def sync_defn_task(self, auth, server_ids, def_id, site_id, group_id, defType):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        name = ''
        if defType == constants.STORAGE:
            name = to_unicode('Storage Sync')
        else:
            if defType == constants.NETWORK:
                name = to_unicode('Network Sync')
        t = SyncDefnOp(name, {}, [], dict(server_ids=server_ids, def_id=def_id, site_id=site_id, group_id=group_id, defType=defType), None, user_name)
        if defType == constants.STORAGE:
            if group_id:
                t.set_entity_details(group_id)
            else:
                t.set_entity_details(site_id)
        else:
            if defType == constants.NETWORK:
                t.set_entity_details(server_ids.split(',')[0])
        task_service.submit_sync(t)
        logger.debug('Sync definition task submitted')
        return None

    #PASSED
    def vm_remove_action(self, auth, dom_id, node_id, force=False, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        domname = Entity.getEntityName(dom_id)
        t = VMRemoveTask(u'Remove ' + domname, {}, [], dict(dom_id=dom_id, node_id=node_id, force=force), None, user_name)
        t.set_entity_details(dom_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Remove VM Task Submitted')
        return t.task_id

    #PASSED
    def populate_node_info(self, auth, node_id, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = PopulateNodeInfoTask(u'Populate Node Information', {}, [], dict(node_id=node_id), None, user_name)
        t.set_entity_details(node_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Populate Node Information Task Submitted')
        return t.task_id

    #PASSED
    def backup_vm_task(self, auth, vm_id, config_id):
        vm_name = ''
        backup_config = BackupManager().get_sp_backup_config(config_id)
        if vm_id:
            vm = DBSession.query(VM).filter_by(id=vm_id).first()
            vm_name = vm.name
            
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        if backup_config:
            t = BackupVMTask(u'Backup ' + to_str(vm_name), {}, [], dict(dom_id=vm_id, backup_config=backup_config), None, user_name)
            t.set_entity_details(vm_id)
            t.cancellable = True
            task_service.submit_sync(t)
            logger.debug('backup vm task submitted')
            return t.task_id
            
        raise Exception('Can not find Backup Policy for the Vitual Machine ' + to_str(vm_name))

    #PASSED
    def set_calendar(self, tsk, backup_occurance, days_list, hour_list, min_list):
        cal = None
        if days_list:
            for each_day in days_list:
                day_list = []
                day_list.append(each_day)
                if backup_occurance == 'Weekly':
                    cal = TaskCalendar(day_list, [], [], hour_list, min_list)
                else:
                    if backup_occurance == 'Monthly':
                        cal = TaskCalendar([], [], day_list, hour_list, min_list)
                tsk.set_calendar(cal)
        else:
            if backup_occurance == 'Hourly':
                cal = TaskCalendar([], [], [], [], min_list)
            else:
                if backup_occurance == 'Daily':
                    cal = TaskCalendar([], [], [], hour_list, min_list)
            tsk.set_calendar(cal)
        return tsk

    #PASSED
    def update_sp_backup_task_calendar(self, auth, group_id, backup_config, backup_occurance, days_list, hour_list, min_list):
        t = DBSession.query(Task).filter_by(task_id=backup_config.task_id).first()
        if t:
            logger.info('Updating backup policy task calender...')
            DBSession.query(TaskCalendar).filter_by(task_id=t.task_id).delete()
            self.set_calendar(t, backup_occurance, days_list, hour_list, min_list)
        else:
            logger.info('Creating and submitting backup policy task...')
            task_id = self.sp_backup_task(auth, group_id, backup_config, backup_occurance, days_list, hour_list, min_list)
            backup_config.task_id = task_id

    #PASSED
    def sp_backup_task(self, auth, group_id, backup_config, backup_occurance, days_list, hour_list, min_list):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = BackupTask('Backup ' + backup_config.name, {}, [], dict(group_id=group_id, backup_config=backup_config), None, user_name)
        t = self.set_calendar(t, backup_occurance, days_list, hour_list, min_list)
        t.cancellable = True
        t.set_entity_details(group_id)
        task_service.submit_calendertask(t)
        logger.debug('SP backup task submitted')
        return t.task_id

    #PASSED
    def restore_vm_task(self, auth, server_id, vm_id, result_id, config_id, ref_disk):
        backup_config = None
        vm_name = None
        if config_id:
            backup_config = BackupManager().get_sp_backup_config(config_id)
        if vm_id:
            vm = DBSession.query(VM).filter_by(id=vm_id).first()
            if vm:
                vm_name = vm.name
                
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RestoreVMTask(u'Restore ' + to_str(vm_name), {}, [], dict(server_id=server_id, vm_id=vm_id, backup_config=backup_config, result_id=result_id, ref_disk=ref_disk), None, user_name)
        t.set_entity_details(vm_id)
        t.cancellable = True
        task_service.submit_sync(t)
        logger.debug('Restore vm task submitted')
        return t.task_id

    #PASSED
    def ha_action(self, auth, group_id, group_name):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = HATask(u'HA Task', {}, [], dict(group_id=group_id, group_name=group_name), None, user_name)
        t.set_entity_details(group_id)
        task_service.submit_sync(t)
        logger.debug('HA Action Task Submitted')
        return t.task_id

    #PASSED
    def ha_recovery_action(self, auth, group_id, group_name):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = HARecoveryTask(u'HARecovery Task', {}, [], dict(group_id=group_id, group_name=group_name), None, user_name)
        t.set_entity_details(group_id)
        task_service.submit_sync(t)
        logger.debug('HA Recovery Action Task Submitted')
        return t.task_id

    #PASSED add 0901
    def import_vm_action(self, auth, node_id, action, paths, dateval=None, timeval=None, external_manager_id=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        task_name = 'Import Virtual Machine'
        if action == 'import_vms':
            task_name += 's'
        t = VMImportTask(task_name, {}, [], dict(node_id=node_id, action=action, paths=paths, external_manager_id = external_manager_id), None, user_name)
        t.set_entity_details(node_id)
        t.cancellable = True
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Import VM Task Submitted')
        return t.task_id

    #PASSED
    def cancel_task(self, auth, task_id):
        tk = DBSession.query(Task).filter(Task.task_id == task_id).first()
        if tk:
            if tk.is_cancellable() == True:
                if tk.is_cancel_requested() == False:
                    if tk.result:
                        task_service = self.svc_central.get_service(self.task_service_id)
                        user_name = self._get_username(auth)
                        t = CancelTask(u'Cancel Task', {}, [], dict(task_id=task_id), None, user_name)
                        dc_ent = DBSession.query(Entity).filter_by(name=u'Data Center').first()
                        t.set_entity_info(dc_ent)
                        t.repeating = True
                        task_service.submit_sync(t)
                        logger.debug('Cancel Task Submitted')
                        return t.task_id
                    else:
                        raise Exception('Task :' + tk.name + ' is not running. Can not cancel the task.')
                else:
                    raise Exception('Task :' + tk.name + ' is already submitted for cancellation.')
            else:
                raise Exception('Task :' + tk.name + ' is not cancellable.')
        else:
            raise Exception('Task with id :' + str(task_id) + ' does not exist.')
          
    #PASSED
    def associate_defns_task(self, auth, site_id, group_id, def_type, def_ids, op_level):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = AssociateDefnsTask(u'Associate Definitions', {}, [], dict(site_id=site_id, group_id=group_id, def_type=def_type, def_ids=def_ids, op_level=op_level), None, user_name)
        t.set_entity_details(group_id)
        task_service.submit_sync(t)
        logger.debug('Associate Definitions task submitted')
        return t.task_id

    #PASSED
    def purge_backup_task(self, auth, group_id, backup_config_id):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = PurgeBackup(u'Purge Backup', {}, [], dict(group_id=group_id, backup_config_id=backup_config_id), None, user_name)
        t.set_entity_details(group_id)
        task_service.submit_sync(t)
        logger.debug('Purge Backup task submitted')
        return t.task_id

    #PASSED
    def add_nw_defn_task(self, auth, nw_name, nw_desc, nw_type, nw_bridge, nw_address_space, nw_dhcp_range, nat_radio, nw_nat_fwding, site_id, group_id, node_id, op_level, nw_gateway, nw_ip_address, nw_use_vlan, nw_vlan_id, nw_isbonded, nw_slaves, interface, vlan_id_pool_id, sp_ids=None, csep_context_id=None, csep_id=None, nw_id=None, cp_id=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = AddNetworkDefinition(u'Add Network Definition', {}, [], dict(nw_name=nw_name, nw_desc=nw_desc, nw_type=nw_type, nw_bridge=nw_bridge, nw_address_space=nw_address_space, nw_dhcp_range=nw_dhcp_range, nat_radio=nat_radio, nw_nat_fwding=nw_nat_fwding, site_id=site_id, group_id=group_id, node_id=node_id, op_level=op_level, nw_gateway=nw_gateway, nw_ip_address=nw_ip_address, nw_use_vlan=nw_use_vlan, nw_vlan_id=nw_vlan_id, nw_isbonded=nw_isbonded, nw_slaves=nw_slaves, interface=interface, vlan_id_pool_id=vlan_id_pool_id, sp_ids=sp_ids, csep_context_id=csep_context_id, csep_id=csep_id, nw_id=nw_id), None, user_name)
        if op_level == constants.SCOPE_DC:
            t.set_entity_details(site_id)
        elif op_level == constants.SCOPE_SP:
            t.set_entity_details(group_id)
        elif op_level == constants.SCOPE_S:
            t.set_entity_details(node_id)
        elif op_level == constants.SCOPE_CP:
            t.set_entity_details(cp_id)
        task_service.submit_sync(t)
        logger.debug('Add Network Definition task submitted')
        return t.task_id

    #PASSED
    def remove_nw_defn_task(self, auth, def_id, site_id, group_id, node_id, op_level, csep_id=None, cp_id=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RemoveNetworkDefinition(u'Remove Network Definition', {}, [], dict(def_id=def_id, site_id=site_id, group_id=group_id, node_id=node_id, op_level=op_level, csep_id=csep_id), None, user_name)
        if op_level == constants.SCOPE_DC:
            def_link = DBSession.query(DCDefLink).filter_by(def_id=def_id).first()
            if def_link:
                t.set_entity_details(def_link.site_id)
        else:
            if op_level == constants.SCOPE_SP:
                def_link = DBSession.query(SPDefLink).filter_by(def_id=def_id).first()
                if def_link:
                    t.set_entity_details(def_link.group_id)
            else:
                if op_level == constants.SCOPE_CP:
                    t.set_entity_details(cp_id)
                else:
                    node_defn = DBSession.query(ServerDefLink).filter_by(def_id=def_id).first()
                    if node_defn:
                        t.set_entity_details(node_defn.server_id)

        task_service.submit_sync(t)
        logger.debug('Remove Network Definition task submitted')
        return t.task_id

    #PASSED
    def add_storage_def_task(self, auth, site_id, group_id, node_id, type, opts, op_level, sp_ids, added_manually):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        scan_result = session.get(constants.SCAN_RESULT)
        t = AddStorageDefTask(u'Add Storage Definition', {}, [], dict(site_id=site_id, group_id=group_id, node_id=node_id, type=type, opts=opts, op_level=op_level, sp_ids=sp_ids, added_manually=added_manually, scan_result=scan_result), None, user_name)
        t.set_entity_details(site_id)
        task_service.submit_sync(t)
        logger.debug('Add Storage Definition task submitted')
        session[constants.SCAN_RESULT] = None
        session.save()
        return t.task_id

    #PASSED
    def remove_storage_def_task(self, auth, storage_id, site_id, group_id, op_level):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RemoveStorageDefTask(u'Remove Storage Definition', {}, [], dict(storage_id=storage_id, site_id=site_id, group_id=group_id, op_level=op_level), None, user_name)
        if group_id:
            t.set_entity_details(group_id)
        else:
            if site_id:
                t.set_entity_details(site_id)
                
        task_service.submit_sync(t)
        logger.debug('Remove Storage Definition task submitted')
        return t.task_id

    #PASSED
    def purge_single_backup_task(self, auth, result_id, node_id):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = PurgeSingleBackup(u'Purge Single Backup', {}, [], dict(result_id=result_id), None, user_name)
        t.set_entity_details(node_id)
        task_service.submit_sync(t)
        logger.debug('Purge Single Backup task submitted')
        return t.task_id

    #PASSED
    def submit_task(self, task, dateval=None, timeval=None):
        result = None
        try:
            task_service = self.svc_central.get_service(self.task_service_id)
            execution_time = getDateTime(dateval, timeval)
            if execution_time is None:
                task_service.submit_sync(task)
            else:
                task_service.submit_schedule(task, execution_time)
            logger.debug('Task : ' + task.name + ' Submitted')
            result = task.task_id
        except Exception as ex:
            traceback.print_exc()
            raise ex
        return result

    #PASSED
    def dwm_task(self, auth, sp_id, interval, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        entity_name = Entity.getEntityName(sp_id)
        t = SPDWMTask(to_unicode(entity_name + ' DWM Task'), {'quiet': False}, [], dict(sp_id=sp_id), None, user_name)
        t.set_entity_details(sp_id)
        t.cancellable = True
        t.set_interval(TaskInterval(interval))
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('DWM Task Submitted')
        return t.task_id

    #PASSED
    def dwm_calendar_task(self, auth, sp_id, policy, mode, schedule_list):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        entity_name = Entity.getEntityName(sp_id)
        t = SPDWMCalendarTask(to_unicode(entity_name + ' DWM Calendar Task'), {'quiet': False}, [], dict(sp_id=sp_id, policy=policy, mode=mode), None, user_name)
        t.set_entity_details(sp_id)
        from stackone.model.DWM import DWMPolicySchedule
        for schedule in schedule_list:
            occurance = schedule.get('occurance')
            dow = None
            if schedule.get('dow', None) != None:
                dow = [schedule.get('dow')]
            self.set_calendar(t, occurance, dow, [schedule.get('hour')], [schedule.get('minute')])
            print 'Calendar Details: dow=',
            print str(dow),
            print ' hour=',
            print str(schedule.get('hour')),
            print ' minute=',
            print str(schedule.get('minute'))
            
        task_service.submit_calendertask(t)
        logger.debug('DWM Calendar Task Submitted')
        return t.task_id

    #PASSED
    def server_maintenance(self, auth, node_id, node_name, is_maintenance, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = ServerMaintenanceTask('Server Maintenance', {}, [], dict(node_id=node_id, node_name=node_name, is_maintenance=is_maintenance), None, user_name)
        t.set_entity_details(node_id)
        t.cancellable = True
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Server Maintenance Task Submitted')
        return t.task_id

    #PASSED
    def save_imported_items_from_cloud_task(self, auth, items, vdc_id, module):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        if module == 'KEY_PAIR':
            task_name = to_unicode('Refresh Key Pairs')
        else:
            if module == 'SECURITY_GROUP':
                task_name = to_unicode('Refresh Security Groups')
            else:
                if module == 'STORAGE':
                    task_name = to_unicode('Refresh Storage')
                else:
                    if module == 'PUBLIC_IP':
                        task_name = to_unicode('Refresh Public IPs')
                    else:
                        if module == 'SNAPSHOT':
                            task_name = to_unicode('Refresh Snapshot')
        t = SaveImportedItemsFromCloudTask(task_name, {}, [], dict(items=items, vdc_id=vdc_id, module=module), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Refresh List task submitted')
        return t.task_id

    #PASSED
    def add_key_task(self, auth, vdc_id, acc_id, region_id, key_name, desc):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = AddKeyTask(u'Add Key', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, key_name=key_name, desc=desc), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Add Key task submitted')
        return t.task_id

    #PASSED
    def edit_key_task(self, auth, vdc_id, acc_id, region_id, key_name, desc):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = EditKeyTask(u'Edit Key', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, key_name=key_name, desc=desc), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Edit Key task submitted')
        return t.task_id

    #PASSED
    def delete_key_task(self, auth, vdc_id, acc_id, region_id, key_name):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = DeleteKeyTask(u'Remove Key', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, key_name=key_name), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Remove Key task submitted')
        return t.task_id

    #PASSED
    def remove_security_group_task(self, auth, vdc_id, acc_id, region_id, sg_deleted_data):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RemoveSecurityGroupTask(u'Remove Security Group', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, sg_deleted_data=sg_deleted_data), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Remove Security Group task submitted')
        return t.task_id

    #PASSED
    def manage_security_group_task(self, auth, vdc_id, acc_id, region_id, sg_data, sg_deleted_data, rule_data, rule_deleted_data, mode):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        if mode == 'NEW' or mode == 'PROVISION':
            task_label = to_unicode('Add Security Group')
        else:
            if mode == 'EDIT':
                task_label = to_unicode('Edit Security Group')
            else:
                task_label = to_unicode('Manage Security Group')
        t = ManageSecurityGroupTask(task_label, {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, sg_data=sg_data, sg_deleted_data=sg_deleted_data, rule_data=rule_data, rule_deleted_data=rule_deleted_data), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Manage Security Group task submitted')
        return t.task_id

    #PASSED
    def add_volume_task(self, auth, vdc_id, acc_id, region_id, name, desc, size, size_unit, zone, zone_id, snapshot):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = AddVolumeTask(u'Add volume', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, name=name, desc=desc, size=size, size_unit=size_unit, zone=zone, zone_id=zone_id, snapshot=snapshot), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Add Volume task submitted')
        return t.task_id

    #PASSED
    def edit_volume_task(self, auth, vdc_id, acc_id, region_id, volume_id, name, desc):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = EditVolumeTask(u'Edit volume', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, volume_id=volume_id, name=name, desc=desc), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Edit Volume task submitted')
        return t.task_id

    #PASSED
    def remove_volume_task(self, auth, vdc_id, acc_id, region_id, volume_id):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RemoveVolumeTask(u'Remove volume', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, volume_id=volume_id), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Remove Volume task submitted')
        return t.task_id

    #PASSED
    def attach_volume_task(self, auth, vdc_id, acc_id, region_id, volume_id, instance_id, device, storage_name):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = AttachVolumeTask(u'Attach volume', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, volume_id=volume_id, instance_id=instance_id, device=device, storage_name=storage_name), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Attach Volume task submitted')
        return t.task_id

    #PASSED
    def detach_volume_task(self, auth, vdc_id, acc_id, region_id, volume_id, instance_id, device, force):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = DetachVolumeTask(u'Detach volume', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, volume_id=volume_id, instance_id=instance_id, device=device, force=force), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Detach Volume task submitted')
        return t.task_id

    #PASSED
    def add_snapshot_task(self, auth, vdc_id, acc_id, region_id, volume_id, name, desc):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = AddSnapshotTask(u'Add snapshot', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, volume_id=volume_id, name=name, desc=desc), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Add Snapshot task submitted')
        return t.task_id

    #PASSED
    def remove_snapshot_task(self, auth, vdc_id, acc_id, region_id, snapshot_id):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RemoveSnapshotTask(u'Remove snapshot', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, snapshot_id=snapshot_id), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Remove Snapshot task submitted')
        return t.task_id

    #PASSED
    def create_public_ip_task(self, auth, vdc_id, acc_id, region_id, name, description):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = CreatePublicIPTask(u'Request Public IP', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, name=name, description=description), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Request Public IP task submitted')
        return t.task_id

    #PASSED
    def edit_public_ip_task(self, auth, vdc_id, acc_id, region_id, public_ip_id, name, description):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = EditPublicIPTask(u'Edit Public IP', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, public_ip_id=public_ip_id, name=name, description=description), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Edit Public IP task submitted')
        return t.task_id

    #PASSED
    def delete_public_ip_task(self, auth, vdc_id, acc_id, region_id, public_ip, public_ip_id, detach=False, delete_from_cloud=True):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RemovePublicIPTask(u'Release Public IP', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, public_ip=public_ip, public_ip_id=public_ip_id, detach=detach, delete_from_cloud=delete_from_cloud), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Release Public IP task submitted')
        return t.task_id

    #PASSED
    def attach_public_ip_task(self, auth, vdc_id, acc_id, region_id, public_ip, public_ip_id, instance_name):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = AttachPublicIPTask(u'Attach Public IP', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, public_ip=public_ip, public_ip_id=public_ip_id, instance_name=instance_name), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Attach Public IP task submitted')
        return t.task_id

    #PASSED
    def detach_public_ip_task(self, auth, vdc_id, acc_id, region_id, public_ip, public_ip_id):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = DetachPublicIPTask(u'Detach Public IP', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, region_id=region_id, public_ip=public_ip, public_ip_id=public_ip_id), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Detach Public IP task submitted')
        return t.task_id

    #PASSED
    def cloud_vm_action(self, auth, dom_id, action, region_id, acc_id, vdc_id, delete_from_cloud=True, dateval=None, timeval=None, requester=constants.CORE):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = CloudVMActionTask(action, {}, [], dict(dom_id=dom_id, action=action, region_id=region_id, acc_id=acc_id, vdc_id=vdc_id, delete_from_cloud=delete_from_cloud), None, user_name)
        t.set_entity_details(dom_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('VM Action Task Submitted')
        return t.task_id

    #PASSED
    def provision_cloud_vm(self, auth, vdc_id, vmfolder_id, acc_id, region_id, tmpl_id, instance_type_id, name, cli, zone_id, kernel_id, ramdisk_id, data, memory_value, cpu_value, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = ProvisionCloudVMTask(u'Provision Cloud VM', {}, [], dict(vdc_id=vdc_id, vmfolder_id=vmfolder_id, instance_type_id=instance_type_id, region_id=region_id, acc_id=acc_id, tmpl_id=tmpl_id, name=name, kernel_id=kernel_id, ramdisk_id=ramdisk_id, zone_id=zone_id, data=data, cli=cli, memory_value=memory_value, cpu_value=cpu_value), None, user_name)
        t.set_entity_details(vdc_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('VM Action Task Submitted')
        return t.task_id

    #PASSED
    def edit_cloud_vm(self, auth, vdc_id, vmfolder_id, vm_id, acc_id, region_id, name, data):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = EditCloudVMTask(u'Edit Cloud VM', {}, [], dict(vdc_id=vdc_id, vmfolder_id=vmfolder_id, vm_id=vm_id, region_id=region_id, acc_id=acc_id, name=name, data=data), None, user_name)
        t.set_entity_details(vm_id)
        task_service.submit_sync(t)
        logger.debug('VM Action Task Submitted')
        return t.task_id

    #PASSED
    def create_template_vm(self, auth, vm_id, name, instance_id, vdc_id, image_name, description, region_id, account_id, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = CreateCloudVMTemplate(u'Create Template', {}, [], dict(vdc_id=vdc_id, account_id=account_id, region_id=region_id, vm_id=vm_id, instance_id=instance_id, image_name=image_name, description=description), None, user_name)
        t.set_entity_details(vm_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('VM Action Task Submitted')
        return t.task_id

    #PASSED
    def create_AMI(self, auth, image_id, name, provider_id, account_id, region_id, volume_id, dateval=None, timeval=None):
        description = ''
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = CreateImage('Create AMI', {}, [], dict(image_id=image_id, name=name, provider_id=provider_id, account_id=account_id, region_id=region_id, volume_id=volume_id), None, user_name)
        t.set_entity_details(image_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Create AMI Task Submitted')
        return t.task_id

    #PASSED
    #tianfeng
    def remove_vdc(self, auth, vdc_id, delete_from_cloud, vdc, children, force=False, dateval=None, timeval=None, delete_user=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RemoveVDCTask(u'Remove ' + vdc.name, {}, [], dict(vdc_id=vdc_id, delete_from_cloud=delete_from_cloud, vdc=vdc, force=force, children=children,delete_user=delete_user), None, user_name)
        t.set_entity_details(vdc_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Remove VDC:%s Task Submitted' % vdc.name)
        return t.task_id

    #PASSED
    def add_annotation(self, auth, node_id, text, user, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = AddAnnotationTask(u'Add Annotation ', {}, [], dict(node_id=node_id, text=text, user=user), None, user_name)
        t.set_entity_details(node_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Add Annotation Task Submitted')
        return t.task_id

    #PASSED
    def edit_annotation(self, auth, node_id, text, user, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = EditAnnotationTask(u'Edit Annotation', {}, [], dict(node_id=node_id, text=text, user=user), None, user_name)
        t.set_entity_details(node_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Edit Annotation  Task Submitted')
        return t.task_id

    #PASSED
    def clear_annotation(self, auth, node_id, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = ClearAnnotationTask(u'Remove Annotation ', {}, [], dict(node_id=node_id), None, user_name)
        t.set_entity_details(node_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Clear Annotation Task Submitted')
        return t.task_id

    #PASSED
    def add_vlan_id_pool_task(self, auth, site_id, name, desc, range, interface, sp_ids, cidr, num_hosts):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = AddVLANIDPoolTask(u'Create VLAN ID Pool', {}, [], dict(site_id=site_id, name=name, desc=desc, range=range, interface=interface, sp_ids=sp_ids, cidr=cidr, num_hosts=num_hosts), None, user_name)
        entity_id = site_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Create VLAN ID task submitted')
        return t.task_id

    #PASSED
    def edit_vlan_id_pool_task(self, auth, site_id, vlan_id_pool_id, desc, range, sp_ids, name):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = EditVLANIDPoolTask(u'Update VLAN ID Pool', {}, [], dict(site_id=site_id, vlan_id_pool_id=vlan_id_pool_id, desc=desc, range=range, sp_ids=sp_ids, name=name), None, user_name)
        entity_id = site_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Update VLAN ID task submitted')
        return t.task_id

    #PASSED
    def remove_vlan_id_pool_task(self, auth, site_id, vlan_id_pool_id):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RemoveVLANIDPoolTask(u'Remove VLAN ID Pool', {}, [], dict(vlan_id_pool_id=vlan_id_pool_id), None, user_name)
        entity_id = site_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Remove VLAN ID Pool task submitted')
        return t.task_id

    #PASSED
    def create_network_task(self, auth, vdc_id, nw_name, nw_desc, nw_address_space, nw_dhcp_range, nw_nat_fwding, acc_id, vlan_pool_id=None):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = CreateNetworkTask(u'Create Network', {}, [], dict(vdc_id=vdc_id, nw_name=nw_name, nw_desc=nw_desc, nw_address_space=nw_address_space, nw_dhcp_range=nw_dhcp_range, nw_nat_fwding=nw_nat_fwding, acc_id=acc_id, vlan_pool_id=vlan_pool_id), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        return t.task_id

    #PASSED
    def remove_network_task(self, auth, nw_id, nw_def_id, vdc_id):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RemoveNetworkTask(u'Remove Network', {}, [], dict(nw_id=nw_id, nw_def_id=nw_def_id, vdc_id=vdc_id), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        return t.task_id

    #PASSED
    def edit_network_task(self, auth, vdc_id, acc_id, nw_id, nw_def_id, nw_name, desc):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = EditNetworkTask(u'Edit Network', {}, [], dict(vdc_id=vdc_id, acc_id=acc_id, nw_id=nw_id, nw_def_id=nw_def_id, nw_name=nw_name, desc=desc), None, user_name)
        entity_id = vdc_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        return t.task_id

    #PASSED
    def create_disk_task(self, auth, context, node_id):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = CreateDiskTask(u'Add volume', {}, [], dict(context=context, managed_node=None), None, user_name)
        vdc_id = context.get('vdc_id')
        entity_id = node_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Create Disk task submitted')
        return t.task_id

    #PASSED
    def remove_disk_task(self, auth, context, node_id):
        from tg import session
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = RemoveDiskTask(u'Remove volume', {}, [], dict(context=context, managed_node=None), None, user_name)
        vdc_id = context.get('vdc_id')
        entity_id = node_id
        t.set_entity_details(entity_id)
        task_service.submit_sync(t)
        logger.debug('Remove Disk task submitted')
        return t.task_id
    ##tianfeng
    def delete_image_task(self, auth, image_id, group_id, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = DeleteImageTask(u'Delete Template ',{},[],dict(image_id = image_id,group_id = group_id),None,user_name)
        t.set_entity_details(image_id)
        execution_time = getDateTime(dateval,timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t.execution_time)
        logger.debug('Delete Template Task Submitted')
        return t.task_id
        
    #from vm to image
    def create_image_from_vm_task(self, auth, node_id, image_name, image_group_id, context, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = CreateImageFromVMTask(u'Create Template', {}, [], dict(node_id=node_id, image_name=image_name, image_group_id=image_group_id, context=context), None, user_name)
        t.set_entity_details(node_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Create Template from vm task Task Submitted')
        return t.task_id
    def import_vcenter_task(self, auth, site_id, vcenter_id, context, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = ImportVcenterTask(u'Import vCenter', {}, [], dict( site_id =site_id, vcenter_id = vcenter_id, context_dict = context), None, user_name)
        t.set_entity_details(site_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Import vCenter Task Submitted')
        return t.task_id

    def import_vcenter_templates_task(self, auth, node_id, dc_id, vcenter_id, dc, dateval=None, timeval=None):
        task_service = self.svc_central.get_service(self.task_service_id)
        user_name = self._get_username(auth)
        t = ImportVcenterTemplatesTask(u'Import vCenter Templates', {}, [], dict( node_id = node_id, dc_id = dc_id, vcenter_id = vcenter_id, dc = dc), None, user_name)
        t.set_entity_details(node_id)
        execution_time = getDateTime(dateval, timeval)
        if execution_time is None:
            task_service.submit_sync(t)
        else:
            task_service.submit_schedule(t, execution_time)
        logger.debug('Import vCenter Templates Task Submitted')
        return t.task_id


