from stackone.core.utils.utils import to_unicode, to_str, constants, getHexID, copyToRemote, mkdir2, wait_for_task_completion, CancelException, replace_with_CMS_TZ
from stackone.model import DBSession
from datetime import datetime
from stackone.model.VM import VMDisks, VM, ImageDiskEntry
from stackone.model.availability import AvailState, StateTransition
from stackone.model.ManagedNode import ManagedNode
from stackone.model.Groups import ServerGroup
from stackone.model.Credential import Credential
from stackone.viewModel.NodeService import NodeService
import logging
import Basic
import traceback
import os
import tg
from tg import session
import calendar
import transaction
import traceback
LOGGER = logging.getLogger('stackone.model')
from stackone.model.Backup import SPBackupConfig
from stackone.model.Restore import RestoreManager, VMRestoreResult
from stackone.model.Backup import BackupManager
from stackone.model.services import Task, TaskUtil
from stackone.viewModel.BackupService import BackupService
class RestoreService():
    def __init__(self):
        self.backup_service = BackupService()
        self.manager = Basic.getGridManager()
        self.backup_manager = BackupManager()
        self.restore_manager = RestoreManager()
        self.script_path = '/var/cache/stackone/default/restore'
        self.custom_path = '/var/cache/stackone/custom'
        self.custom_script_path = os.path.join(self.custom_path, 'restore')
        self.local_tmp = os.path.join('/var/cache/stackone', 'tmp')
        self.local_path = os.path.join(self.local_tmp, 'restore')
        self.mount_device = None
        self.bkp_result_id = ''
        self.seq = ''

    def getRestoreManager(self):
        return self.restore_manager

    def get_file_name(self, file_path):
        file_name = None
        if file_path:
            item_list = file_path.split('/')
            if item_list:
                file_name = item_list[len(item_list) - 1]
        return file_name

    def get_vm_state_string(self, avail_state):
        vm_state = None
        if avail_state == 0:
            vm_state = VM.RUNNING
        elif avail_state == 2:
            vm_state = VM.PAUSED
        elif avail_state == 3:
            vm_state = VM.SHUTDOWN
        elif avail_state == 4:
            vm_state = VM.CRASHED
        elif avail_state == -1:
            vm_state = VM.NOT_STARTED
        elif avail_state == -2:
            vm_state = VM.UNKNOWN
        return vm_state

    def get_vm_state(self, vm_id):
        vm_state = None
        try:
            avail_state = DBSession.query(AvailState).filter_by(entity_id=vm_id).first()
            if avail_state:
                vm_state = self.get_vm_state_string(avail_state.avail_state)
        except Exception as ex:
            LOGGER.error('Error: ' + to_str(ex).replace("'", ''))
            raise Exception(to_str(ex))
        return vm_state

    def check_privileges(self, auth, vm_id):
        ent = auth.get_entity(vm_id)
        if not auth.has_privilege('EXEC_BACKUP_POLICY', ent):
            LOGGER.error(to_str(constants.NO_PRIVILEGE))

    def perform_validation(self, vm_id):
        error_desc = ''
        if self.backup_manager.is_backing_up(vm_id):
            error_desc = 'Backup operation is going on this entity so this restore operation is not allowed.'
        else:
            if self.restore_manager.is_restoring(vm_id):
                error_desc = 'Restore operation is going on this entity so this restore operation is not allowed.'
        if error_desc:
            LOGGER.error('Error: ' + error_desc)
            raise Exception(error_desc)

    def wait_for_task(self, dom, task_id, action):
        returnVal = False
        wait_time = dom.get_wait_time(action)
        print '\n\nwait_time=======' + str(wait_time)
        wait_time = int(wait_time) + 3
        finished,status = wait_for_task_completion(task_id, wait_time)
        if finished == True and status == Task.SUCCEEDED:
            returnVal = True
        return returnVal

    def set_local_path(self):
        if tg.config.get('temp_path'):
            self.local_tmp = tg.config.get('temp_path')
        if tg.config.get('local_path_restore'):
            self.local_path = tg.config.get('local_path_restore')
        if tg.config.get('custom_path'):
            self.custom_path = tg.config.get('custom_path')
        if tg.config.get('script_path_restore'):
            self.script_path = tg.config.get('script_path_restore')
        if tg.config.get('custom_script_path_restore'):
            self.custom_script_path = tg.config.get('custom_script_path_restore')

    def restore_vm(self, auth, node_id, vm_id, bkp_result_id, backup_config=None, ref_disk=None):
        result_id = None
        disk_info = []
        backup_info = {}
        backup_vm_path = None
        execution_context = {}
        self.bkp_result_id = bkp_result_id
        vm = self.manager.get_dom(auth, vm_id)
        try:
            self.set_local_path()
            self.check_privileges(auth, vm_id)
            self.perform_validation(vm_id)
            self.change_defn_transient_state(auth, vm_id, constants.RESTORING, constants.RESTORE, StateTransition)
            vm_backup_result = self.backup_manager.get_vm_backup_result(bkp_result_id)
            if vm_backup_result:
                backup_vm_path = vm_backup_result.backup_destination
                backup_config = DBSession.query(SPBackupConfig).filter_by(id=vm_backup_result.backup_id).first()
                bkp_config_id = backup_config.id
                vm_id = vm_backup_result.vm_id
                vm_name = vm_backup_result.vm_name
                if not node_id:
                    node_id = vm_backup_result.server_id
                node = DBSession.query(ManagedNode).filter_by(id=node_id).first()
                node.connect()
                node_entity = auth.get_entity(node_id)
                group_id = node_entity.parents[0].entity_id
                execution_context = vm_backup_result.execution_context
            config_id = backup_config.id
            start_time = datetime.now()
            end_time = None
            status = 'Started'
            result = 'VM restore has started'
            result_id = self.record_phase_details(vm, backup_config, result_id, '', status, result, add_phase_details=True, add_vm_result=True, update_vm_result=False)
            vm_state = self.get_vm_state(vm_id)
            self.prepare_restore(auth, node, vm, backup_config, result_id, vm_state)
            if TaskUtil.is_cancel_requested() == True:
                raise CancelException()
            backup_info = self.get_backup_info(node.hostname, backup_config, backup_vm_path, execution_context)
            disk_info,local_dir_dic,remote_node = self.get_backup(node, vm, backup_config, result_id, bkp_result_id, backup_vm_path, backup_info)
            if TaskUtil.is_cancel_requested() == True:
                raise CancelException()
            execution_context['RESTORE_LOCAL_DIR_STRUCTURE'] = local_dir_dic
            self.backup_manager.update_vm_backup_result(bkp_result_id, None, None, None, None, None, None, None, None, None, execution_context)
            LOGGER.info('Updating database for virtual machine and vm disks...')
            vm_info = self.read_vm_config(node, auth, vm_id, vm_name)
            if self.backup_manager.vm_exists(vm_id) == False:
                vm_config = self.convert_config(vm_info, node_id, bkp_config_id)
                NodeService().vm_config_settings(auth, vm_info.get('image_id'), vm_config, 'PROVISION_VM', node_id, group_id, None, vm_name, True, vm_id)
            else:
                vm_info['name'] = vm_name
                vm_config = vm.get_config()
                vm_config.set_managed_node(node)
                self.manager.update_vm_disks(auth, vm_id, node_id, vm_config)
            LOGGER.info('Database update is complete')
            execution_context = eval(vm_info.get('execution_context'))
            self.transfer(node, vm, backup_config, result_id, bkp_result_id, disk_info, backup_info, local_dir_dic, ref_disk)
            if TaskUtil.is_cancel_requested() == True:
                raise CancelException()
            
            self.restore(node, vm, backup_config, result_id, bkp_result_id, disk_info, backup_info, local_dir_dic, ref_disk, vm_info, execution_context)
            StateTransition.set_none_state(vm_id, constants.RESTORE)
            self.cleanup(vm_id, result_id, bkp_result_id)
            end_time = datetime.now()
            result = 'Restore of ' + to_str(vm.name) + ' completed successfully at time ' + to_str(datetime.now())
            result_id = self.record_phase_details(vm, backup_config, result_id, '', 'Success', result, add_phase_details=True, add_vm_result=False, update_vm_result=True)
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex).replace("'", ''))
            StateTransition.set_none_state(vm_id, constants.RESTORE)
            self.cleanup(vm_id, result_id, bkp_result_id)
            end_time = datetime.now()
            result = to_str(ex).replace("'", '')
            result_id = self.record_phase_details(vm, backup_config, result_id, '', 'Failed', result, add_phase_details=True, add_vm_result=False, update_vm_result=True)
            if isinstance(ex, CancelException):
                return dict(status=constants.TASK_CANCELED, msg=constants.TASK_CANCEL_MSG, results=result)
            raise Exception(to_str(ex))

    def prepare_restore(self, auth, node, vm, config, result_id, vm_state):
        LOGGER.info('Preparing restore...')
        phase = 'prepare_restore'
        details = ''
        status = 'Success'
        tc = self.get_task_creator()
        try:
            if self.backup_manager.vm_exists(vm.id) == True:
                if vm_state != VM.SHUTDOWN:
                    details = 'Shutting down virtual machine...'
                    result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
                    task_id = tc.vm_action(auth, vm.id, node.id, constants.SHUTDOWN, requester=constants.RESTORE)
                    wait_result = self.wait_for_task(vm, task_id, constants.SHUTDOWN)
                    if not wait_result:
                        task_id = tc.vm_action(auth, vm.id, node.id, constants.KILL, requester=constants.RESTORE)
                        if self.wait_for_task(vm, task_id, constants.KILL):
                            LOGGER.info('VM is killed successfully')
                            details = 'Virtual machine is killed successfully.'
                            result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
                    else:
                        LOGGER.info('VM is shutdown successfully')
                        details = 'Virtual machine is shutdown successfully.'
                        result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
                    StateTransition.is_allowed(vm.id, constants.RESTORING, constants.RESTORE)
        except Exception as ex:
            details = to_str(ex).replace("'", '')
            details = 'Got exception while shutting down virtual machine.'
            result_id = self.record_phase_details(vm, config, result_id, phase, 'Failed', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
            raise Exception(to_str(ex))

    def get_backup_info(self, server_name, config, backup_vm_path, execution_context):
        LOGGER.info('Getting backup info...')
        backup_info = {}
        serverobj = None
        user_name = ''
        password = ''
        sp_bkp_settings = self.backup_manager.get_sp_backup_setting(config.sp_backup_setting_id)
        serverobj = self.backup_manager.get_server(sp_bkp_settings.server_id)
        if execution_context:
            backup_type = execution_context.get('BACKUP_TYPE')
            transferMethod = execution_context.get('TRANSFER_METHOD')
            backup_content = execution_context.get('BACKUP_CONTENT')
            is_remote = execution_context.get('IS_REMOTE')
            use_tar = execution_context.get('USE_TAR')
            compression_method = execution_context.get('COMPRESSION_TYPE')
            transferMethod_options = execution_context.get('TRANSFER_METHOD_OPTIONS')
            backup_dest_dir_structure = execution_context.get('BACKUP_DEST_DIR_STRUCTURE')
            backup_vm_path = backup_dest_dir_structure.get('backup_vm_path')
            server_name = execution_context.get('SERVER')
            use_key = execution_context.get('USE_KEY')
            ssh_port = execution_context.get('SSH_PORT')
            if serverobj:
                user_name = serverobj.credential.cred_details['username']
                password = serverobj.credential.cred_details['password']
        else:
            backup_type = sp_bkp_settings.backup_type
            transferMethod = sp_bkp_settings.transferMethod
            backup_content = sp_bkp_settings.backup_content
            is_remote = sp_bkp_settings.is_remote
            use_tar = sp_bkp_settings.use_tar
            compression_method = sp_bkp_settings.compression_type
            transferMethod_options = sp_bkp_settings.transferMethod_options
            if serverobj:
                server_name = serverobj.name
                ssh_port = serverobj.ssh_port
                use_key = serverobj.use_key
        backup_info['backup_type'] = backup_type
        backup_info['transferMethod'] = transferMethod
        backup_info['transferMethod_options'] = transferMethod_options
        backup_info['backup_content'] = backup_content
        backup_info['backup_destination'] = backup_vm_path
        backup_info['is_remote'] = is_remote
        backup_info['use_tar'] = use_tar
        backup_info['compression_method'] = compression_method
        backup_info['user_name'] = user_name
        backup_info['password'] = password
        backup_info['server_name'] = server_name
        backup_info['ssh_port'] = ssh_port
        backup_info['use_key'] = use_key
        return backup_info

    def get_backup(self, node, vm, config, result_id, bkp_result_id, backup_vm_path, backup_info):
        LOGGER.info('Get backup phase...')
        phase = 'get_backup'
        details = 'Getting disk information and creating directory structure...'
        result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
        local_dir_dic = {}
        remote_node = None
        vm_name = vm.name
        try:
            server = None
            user_name = None
            password = None
            backup_config_path = os.path.join(backup_vm_path, 'config')
            is_remote = backup_info.get('is_remote')
            if is_remote == True:
                server = backup_info.get('server_name')
                user_name = backup_info.get('user_name')
                password = backup_info.get('password')
                remote_node = self.get_remote_node(server, user_name, password, True)
            else:
                server = node.hostname
                user_name,password,ssh_port = self.get_node_creds(node)
            details = 'Getting disk information...'
            result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
            disk_info = self.get_disks(backup_config_path, vm_name, node, server, user_name, password, result_id, is_remote, backup_info)
            details = 'Creating directory structure...'
            result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
            local_dir_dic = self.create_dir_structure(node, vm_name, None, disk_info)
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error('Error: ' + to_str(ex).replace("'", ''))
            details = 'Got exception while getting disk information and creating directory structure.'
            result_id = self.record_phase_details(vm, config, result_id, phase, 'Failed', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
            raise Exception(to_str(ex))
        details = 'Getting disk information and creating directory structure are complete.'
        result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
        return (disk_info, local_dir_dic, remote_node)

    def transfer(self, node, vm, config, result_id, bkp_result_id, disk_info, backup_info, local_dir_dic, ref_disk):
        file_name_list = []
        phase = 'transfer'
        op = None
        vm_name = vm.name
        use_tar = backup_info.get('use_tar')
        backup_content = backup_info.get('backup_content')
        is_remote = backup_info.get('is_remote')
        try:
            LOGGER.info('ref_disk=' + to_str(ref_disk))
            if ref_disk and ref_disk != 'undefined' and ref_disk != 'true':
                LOGGER.info('Creating copy of reference disk...')
                for each_disk in disk_info:
                    cmd,custom_script_exists,params = self.get_script(op, node, False, None, None, None, phase, result_id, backup_info, each_disk, ref_disk, bkp_result_id, None, local_dir_dic)
                    self.exec_script(cmd, node, result_id, phase, custom_script_exists, params=params)
            if use_tar:
                LOGGER.info('Transferring zip file...')
                details = 'Transferring zip file...'
                result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
                cmd,custom_script_exists,params = self.get_script(op, node, False, None, None, None, phase, result_id, backup_info, None, None, bkp_result_id, None, local_dir_dic)
                self.exec_script(cmd, node, result_id, phase, custom_script_exists, params=params)
                details = 'Transfer of zip file is complete.'
                result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
                LOGGER.info('Transfer of zip file is complete.')
            else:
                if is_remote and backup_content == constants.BKP_RAW:
                    LOGGER.info('Transferring disks/contents...')
                    details = 'Transferring disks/contents...'
                    result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
                    for each_disk in disk_info:
                        details = 'Transferring disk ' + to_str(each_disk.get('disk_name')) + '...'
                        result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
                        file_name_list.append(each_disk.get('disk_name'))
                        if each_disk.get('block_device'):
                            cmd,custom_script_exists,params = self.get_script(op, node, False, None, vm_name, None, phase, result_id, backup_info, each_disk, None, bkp_result_id, None, local_dir_dic)
                            self.exec_script(cmd, node, result_id, phase, custom_script_exists, params=params)
                    details = 'Transfer of disks/contents is complete.'
                    result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
                    LOGGER.info('Transfer of disks/contents is complete.')
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error('Error: ' + to_str(ex).replace("'", ''))
            details = 'Got exception while transferring disks/contents.'
            result_id = self.record_phase_details(vm, config, result_id, phase, 'Failed', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
            raise Exception(to_str(ex))

    def restore(self, node, vm, config, result_id, bkp_result_id, disk_info, backup_info, local_dir_dic, ref_disk, vm_info, execution_context):
        phase = 'restore'
        details = 'Restoring disks/contents...'
        result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
        file_name_list = []
        content_op_list = []
        snap_op_list = []
        content_op_list.append('CONTENT_MOUNT')
        content_op_list.append('COPY')
        content_op_list.append('CONTENT_UMOUNT')
        snap_op_list.append('MOUNT_SNAPSHOT')
        snap_op_list.append('COPY')
        snap_op_list.append('UMOUNT_SNAPSHOT')
        use_tar = backup_info.get('use_tar')
        backup_content = backup_info.get('backup_content')
        try:
            if use_tar:
                LOGGER.info('Unzipping contents...')
                details = 'Unzipping contents...'
                result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
                op = 'UNZIP'
                cmd,custom_script_exists,params = self.get_script(op, node, False, None, None, None, phase, result_id, backup_info, None, None, bkp_result_id, None, local_dir_dic)
                self.exec_script(cmd, node, result_id, phase, custom_script_exists, params=params)
                details = 'Unzip is complete.'
                result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
            for each_disk in disk_info:
                file_name_list.append(each_disk.get('disk_name'))
                if backup_content == constants.BKP_RAW:
                    details = 'Restoring disk ' + to_str(each_disk.get('disk_name')) + '...'
                    result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
                    op = None
                    cmd,custom_script_exists,params = self.get_script(op, node, False, None, None, None, phase, result_id, backup_info, each_disk, None, bkp_result_id, None, local_dir_dic)
                    self.exec_script(cmd, node, result_id, phase, custom_script_exists, params=params)
                elif backup_content == constants.BKP_CONTENT:
                    if each_disk.get('disk_type') == 'lvm':
                        op_list = snap_op_list
                    else:
                        op_list = content_op_list
                    self.restore_disk_content(node, vm, config, result_id, bkp_result_id, backup_info, local_dir_dic, disk_info, phase, each_disk, vm_info, op_list, execution_context)
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error('Error: ' + to_str(ex).replace("'", ''))
            details = 'Got exception while restoring disks/contents.'
            result_id = self.record_phase_details(vm, config, result_id, phase, 'Failed', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
            raise Exception(to_str(ex))
        details = 'Restore is complete.'
        result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
        LOGGER.info('Disks/contents are restored successfully')

    def get_partition_details(self, node, vm, phase, each_disk, backup_info, result_id, bkp_result_id, local_dir_dic):
        op = 'PART_DETAILS'
        cmd,custom_script_exists,params = self.get_script(op, node, False, None, None, None, phase, result_id, backup_info, each_disk, None, bkp_result_id, None, local_dir_dic)
        exit_code,output = self.exec_script(cmd, node, result_id, phase, custom_script_exists, params=params)
        details = self.backup_manager.parse_details(output, op)
        disk_path = os.path.join(each_disk.get('disk_path'), each_disk.get('disk_name'))
        details['DISK_PATH'] = disk_path
        return details

    def get_backup_content(self, vm_info, disk_path):
        selective_content = ''
        template_cfg = eval(vm_info.get('template_cfg'))
        for disk_item in template_cfg:
            if disk_path == disk_item.get('FILE_NAME'):
                selective_content = disk_item.get('FILE/DIRECTORY')
        return selective_content

    def restore_disk_content(self, node, vm, config, result_id, bkp_result_id, backup_info, local_dir_dic, disk_list, phase, each_disk, vm_info, op_list, execution_context):
        LOGGER.info('Restoring contents...')
        part_details_list = {}
        context = {}
        partition_name = ''
        volume_group = ''
        logical_volume = ''
        mount_device = ''
        disk_path = os.path.join(each_disk.get('disk_path'), each_disk.get('disk_name'))
        use_tar = backup_info.get('use_tar')
        backup_content = backup_info.get('backup_content')
        part_details_list = execution_context.get('PARTITON_DETAILS')
        selective_content = self.get_backup_content(vm_info, disk_path)
        current_part_details = self.get_partition_details(node, vm, phase, each_disk, backup_info, result_id, bkp_result_id, local_dir_dic)
        part_details = part_details_list.get(disk_path)
        for partition_name in part_details:
            #if partition_name == 'DISK_PATH' or partition_name == 'VOLUME_GROUPS' or partition_name == 'P2' or :
            if partition_name != 'P1': 
                continue
            else:
                LOGGER.info('Partition name is ' + to_str(partition_name))
                each_part_details = part_details.get(partition_name)
                LOGGER.info('each_part_details= ' + to_str(each_part_details))
                cur_each_part_details = current_part_details.get(partition_name)
                LOGGER.info('cur_each_part_details= ' + to_str(cur_each_part_details))
                dev_mapper = cur_each_part_details.get('DEV_MAPPER')
                flags = each_part_details.get('FLAGS')
                vgs_details = part_details.get('VOLUME_GROUPS')
                is_lvm = True
                #if flags.find('lvm') >= 0:
                    #is_lvm = True
                fs = None
                if flags.find('ntfs') >= 0 and flags.find('boot') >= 0:
                    flags = to_str(flags).replace('boot', '')
                    fs = flags.strip()
                else:
                    if flags.find('ntfs') >= 0:
                        fs = flags.strip()
                if not vgs_details:
                    vgs_details = '/'
                else:
                    op = 'VG_SCAN'
                    cmd,custom_script_exists,params = self.get_script(op, node, False, None, None, None, phase, result_id, backup_info, each_disk, None, bkp_result_id, None, local_dir_dic)
                    exit_code,output = self.exec_script(cmd, node, result_id, phase, custom_script_exists, params=params)
                for vg_details in vgs_details:
                    LOGGER.info('vgs_details= ' + to_str(vgs_details))
                    if vgs_details == '/':
                        lvs = '/'
                    else:
                        vg_details = vgs_details.get(vg_details)
                        #if partition_name == vg_details.get('PART_NAME'):
                        if vg_details.get('PART_NAME') == 'P1' or vg_details.get('PART_NAME') == 'P2':
                            volume_group = vg_details.get('VG_NAME')
                            lvs = vg_details.get('LOGICAL_VOLUMES')
                            context = {}
                            context['VOLUME_GROUP'] = volume_group
                            op = 'VG_ACTIVATE'
                            cmd,custom_script_exists,params = self.get_script(op, node, False, None, None, None, phase, result_id, backup_info, each_disk, None, bkp_result_id, None, local_dir_dic, context)
                            exit_code,output = self.exec_script(cmd, node, result_id, phase, custom_script_exists, params=params)
                        else:
                            lvs = '/'
                    if lvs:
                        for lv in lvs:
                            if lvs == '/':
                                volume_group = ''
                                logical_volume = ''
                                mount_device = dev_mapper
                            else:
                                lv = lvs.get(lv)
                                logical_volume = lv.get('LV_NAME')
                                if logical_volume == 'lv_swap' or logical_volume == 'swap_1':
                                    continue
                            if selective_content:
                                if not self.backup_service.has_content(selective_content, partition_name, volume_group, logical_volume):
                                    continue
                                else:
                                    context = {}
                                    context['IS_LVM'] = is_lvm
                                    context['PARTITON_NAME'] = partition_name
                                    context['VOLUME_GROUP'] = volume_group
                                    context['LOGICAL_VOLUME'] = logical_volume
                                    context['MOUNT_DEVICE'] = mount_device
                                    if is_lvm:
                                        details = 'Restoring contents of logical volume ' + to_str(os.path.join(partition_name, volume_group, logical_volume)) + '...'
                                        result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
                                    else:
                                        details = 'Restoring contents of partition ' + to_str(partition_name) + '...'
                                        result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
                                    for op in op_list:
                                        cmd,custom_script_exists,params = self.get_script(op, node, False, None, None, None, phase, result_id, backup_info, each_disk, None, bkp_result_id, None, local_dir_dic, context, fs)
                                        exit_code,output = self.exec_script(cmd, node, result_id, phase, custom_script_exists, params=params)
                                        if op == 'CONTENT_MOUNT' and output.find('swapspace') != -1:
                                            LOGGER.info('Skipping mounting and restoring for swap partition.')
                                            details = 'Skipping mounting and restoring for swap partition...'
                                            result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)

    def cleanup_for_recovery(self, task_id):
        LOGGER.info('Cleanning up for recovery...')
        sp_backup_config = DBSession.query(SPBackupConfig).filter_by(task_id=task_id).first()
        if sp_backup_config:
            rec_list = DBSession.query(VMRestoreResult).filter_by(backup_id=sp_backup_config.id, status='Running')
            for rec in rec_list:
                result_id = rec.id
                vm_id = rec.vm_id
                bkp_result_id = rec.backup_result_id
                self.cleanup(vm_id, result_id, bkp_result_id)

    def cleanup(self, vm_id, result_id, bkp_result_id):
        LOGGER.info('Cleanning up...')
        phase = 'cleanup'
        execution_context = {}
        part_details_list = {}
        backup_info = {}
        local_dir_dic = {}
        config = ''
        vm = DBSession.query(VM).filter_by(id=vm_id).first()
        vm_backup_result = self.backup_manager.get_vm_backup_result(bkp_result_id)
        if vm_backup_result:
            execution_context = vm_backup_result.execution_context
            part_details_list = execution_context.get('PARTITON_DETAILS')
            disk_list = execution_context.get('DISK_LIST')
            local_dir_dic = eval(to_str(execution_context.get('RESTORE_LOCAL_DIR_STRUCTURE')))
            vm_name = execution_context.get('VM_NAME')
            node_id = execution_context.get('NODE_ID')
            zip_structure = execution_context.get('ZIP_STRUCTURE')
            use_tar = execution_context.get('USE_TAR')
            backup_vm_path = vm_backup_result.backup_destination
            config = DBSession.query(SPBackupConfig).filter_by(id=vm_backup_result.backup_id).first()
            node = DBSession.query(ManagedNode).filter_by(id=node_id).first()
            node.connect()
            backup_info = self.get_backup_info(node.hostname, config, backup_vm_path, execution_context)
        details = 'Cleaning temporary files...'
        result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
        if local_dir_dic:
            cmd = 'rm -rf ' + local_dir_dic.get('backup_vm_path')
            LOGGER.info('Command= ' + to_str(cmd))
            node.node_proxy.exec_cmd(cmd)
        backup_content = ''
        if backup_info:
            backup_content = backup_info.get('backup_content')
        try:
            local_config_file = os.path.join('/tmp', vm_name)
            if node.node_proxy.file_exists(local_config_file):
                LOGGER.info('vm config file exists')
                LOGGER.info('Removing vm config file in /tmp folder...')
                cmd = 'rm -f ' + to_str(local_config_file)
                LOGGER.info('Command= ' + to_str(cmd))
                node.node_proxy.exec_cmd(cmd)
            LOGGER.info('Local vm config file is removed as part of cleanup operation in restore')
        except Exception as ex:
            LOGGER.error(to_str(ex))
            LOGGER.error('Could not remove local vm config file as part of cleanup operation in restore')
        if disk_list and part_details_list and backup_content == constants.BKP_CONTENT:
            #1227
            dev_mapper = ''
            for each_disk in disk_list:
                disk_path = each_disk.get('DISK_PATH')
                part_details = part_details_list.get(disk_path)
                for partition_name in part_details:
                    if partition_name == 'DISK_PATH' or partition_name == 'VOLUME_GROUPS':
                        continue
                    LOGGER.info('Partition name is ' + to_str(partition_name))
                    each_part_details = part_details.get(partition_name)
                    LOGGER.info('each_part_details= ' + to_str(each_part_details))
                    dev_mapper = each_part_details.get('DEV_MAPPER')
                    vgs_details = part_details.get('VOLUME_GROUPS')
                    for vg_details in vgs_details:
                        vg_details = vgs_details.get(vg_details)
                        volume_group = vg_details.get('VG_NAME')
                        LOGGER.info('Deactivating volume group ' + to_str(volume_group) + '...')
                        context = {}
                        context['VOLUME_GROUP'] = volume_group
                        op = 'DETACH_VOL_GROUP'
                        cmd,custom_script_exists,params = self.get_script(op, node, False, None, None, None, phase, result_id, backup_info, each_disk, None, bkp_result_id, None, local_dir_dic, context)
                        self.exec_script(cmd, node, result_id, phase, custom_script_exists, params=params)
                LOGGER.info('Removing dev mappers..')
                op = 'REMOVE_MAPPER'
                cmd,custom_script_exists,params = self.get_script(op, node, False, None, None, None, phase, result_id, backup_info, each_disk, None, bkp_result_id, None, local_dir_dic)
                self.exec_script(cmd, node, result_id, phase, custom_script_exists, params=params)
        if use_tar:
            cmd = 'rm -rf ' + os.path.join(to_str(zip_structure), 'disks')
            LOGGER.info('Removing zip directory structure...')
            LOGGER.info('Command= ' + to_str(cmd))
            node.node_proxy.exec_cmd(cmd)
        LOGGER.info('Cleanup is done successfully')
        details = 'Cleanup is complete.'
        result_id = self.record_phase_details(vm, config, result_id, phase, 'Running', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)

    def prepare_scripts(self, dest_node):
        if not os.path.exists(self.script_path):
            mkdir2(dest_node, os.path.dirname(self.script_path))
        source = tg.config.get('restore_script')
        destination = self.script_path
        copyToRemote(source, dest_node, destination)

    def prepare_custom_scripts(self, dest_node):
        if self.custom_script_path:
            if not os.path.exists(self.custom_script_path):
                mkdir2(dest_node, os.path.dirname(self.custom_script_path))
        source = tg.config.get('restore_custom_script')
        destination = self.custom_script_path
        copyToRemote(source, dest_node, destination)

    def get_command(self, op, node, script_path, source, destination, user_name, password, backup_path, backup_vm_path, server, custom_script_exists, objCustomParam, vm_name, snapshot_file, phase, result_id, use_key, volume_group, fs):
        LOGGER.info('OP= ' + to_str(op))
        script_folder_path = os.path.join(self.script_path, 'scripts', phase)
        script_args = ''
        if custom_script_exists:
            for each_key in objCustomParam.keys():
                if each_key:
                    script_args += ' ' + each_key + ' ' + objCustomParam[each_key]
        if op == 'LS':
            script_args = ' -s ' + source
        elif op == 'CP':
            if source:
                script_args = ' -s ' + source
            else:
                script_args = ' -s NONE'
            if destination:
                script_args += ' -d ' + destination
            else:
                script_args += ' -d NONE'
            script_args += ' -o ' + op
        elif op == 'CONTENT_CP':
            if source:
                script_args = source
            else:
                script_args = ' -s NONE'
            if destination:
                script_args += ' ' + destination
            else:
                script_args += ' -d NONE'    
        elif op == 'DD' or op == 'DD_LOCAL' or op == 'DD_REMOTE':
            if source:
                script_args = ' -s ' + source
            else:
                script_args = ' -s NONE'
            if destination:
                script_args += ' -d ' + destination
            else:
                script_args += ' -d NONE'
            if server:
                script_args += ' -n ' + to_str(server)
            else:
                script_args += ' -n NONE'
            if user_name:
                script_args += ' -u ' + user_name
            else:
                script_args += ' -u NONE'
            script_args += ' -t ' + script_folder_path
            if use_key:
                script_args += ' -k ' + to_str(use_key)
            else:
                script_args += ' -k NONE'
            script_args += ' -o ' + op
        elif op == 'SCP' or op == 'CONTENT_SCP':
            if source:
                script_args = ' -s ' + source
            else:
                script_args = ' -s NONE'
            if destination:
                script_args += ' -d ' + destination
            else:
                script_args += ' -d NONE'
            if server:
                script_args += ' -n ' + to_str(server)
            else:
                script_args += ' -n NONE'
            if user_name:
                script_args += ' -u ' + user_name
            else:
                script_args += ' -u NONE'
            script_args += ' -t ' + script_folder_path
            if use_key:
                script_args += ' -k ' + to_str(use_key)
            else:
                script_args += ' -k NONE'
            script_args += ' -o ' + op
        elif op == 'UNTAR':
            if source:
                script_args = ' -s ' + source
            else:
                script_args = ' -s NONE'
        elif op == 'BZIP2' or op == 'GZIP':
            if source:
                script_args = ' -s ' + source
            else:
                script_args = ' -s NONE'
            script_args += ' -o ' + op
        elif op == 'MOUNT_SNAPSHOT' or op == 'UMOUNT_SNAPSHOT':
            if source:
                script_args = ' -s ' + source
            else:
                script_args = ' -s NONE'
            if destination:
                script_args += ' -d ' + destination
            else:
                script_args += ' -d NONE'
            script_args += ' -o ' + op
        elif op == 'PART_DETAILS' or op == 'VG_ACTIVATE' or op == 'VG_SCAN':
            if source:
                script_args = ' -d ' + source
            else:
                script_args = ' -d NONE'
            if volume_group:
                script_args += ' -v ' + volume_group
            else:
                script_args += ' -v NONE'
            script_args += ' -o ' + op
        elif op == 'CONTENT_MOUNT' or op == 'CONTENT_UMOUNT':
            if op == 'CONTENT_MOUNT':
                self.mount_device = None
            if source:
                script_args = ' -d ' + source
            else:
                script_args = ' -d NONE'
            if destination:
                script_args += ' -m ' + destination
            else:
                script_args += ' -m NONE'
            if self.mount_device:
                script_args += ' -v ' + self.mount_device
            else:
                script_args += ' -v NONE'
            if fs:
                script_args += ' -t ' + fs
            else:
                script_args += ' -t NONE'
            script_args += ' -o ' + op
        elif op == 'CLEAN' or op == 'DETACH_VOL_GROUP' or op == 'REMOVE_MAPPER':
            if backup_vm_path:
                script_args = ' -v ' + backup_vm_path
            else:
                script_args = ' -v NONE'
            if snapshot_file:
                script_args += ' -s ' + snapshot_file
            else:
                script_args += ' -s NONE'
            if source:
                script_args += ' -d ' + source
            else:
                script_args += ' -d NONE'
            if volume_group:
                script_args += ' -g ' + volume_group
            else:
                script_args += ' -g NONE'
            script_args += ' -o ' + op
        elif op == 'RSYNC':
            full_bk_dest = backup_path
            script_args = ' -s ' + source
            script_args += ' -d ' + destination
        elif op == 'REMOTE_RSYNC':
            full_bk_dest = backup_path
            script_args = ' -s ' + source
            script_args += ' -d ' + destination
            script_args += ' -o ' + op
            script_args += ' -t ' + script_folder_path
            script_args += ' -u ' + user_name
            script_args += ' -n ' + to_str(server)
            if use_key:
                script_args += ' -k ' + to_str(use_key)
            else:
                script_args += ' -k NONE'
        if op == 'CONTENT_CP':
            cmd = 'cp -arf ' + script_args
        else:
            cmd = script_path + script_args
        cmd_print = cmd
        params = []
        if password:
            params = [password]
            LOGGER.info('Command= ' + to_str(cmd_print.replace('-p ' + password, '-p *****')))
        else:
            LOGGER.info('Command= ' + to_str(cmd))
        return (cmd, params)

    def exec_script(self, cmd, node, result_id, phase, custom_script_exists, params):
        if custom_script_exists:
            self.prepare_custom_scripts(node)
        else:
            self.prepare_scripts(node)
        output = 'Success'
        exit_code = 0
        output,exit_code = node.node_proxy.exec_cmd(cmd, params=params, timeout=int(tg.config.get('restore_timeout')))
        LOGGER.info('Script output=' + to_str(output))
        LOGGER.info('exit_code=' + to_str(exit_code))
        if exit_code:
            if output.find('No such file or directory') != -1:
                LOGGER.error('Error: ' + to_str(output))
                exit_code = 0
            elif output.find('swapspace') != -1:
                LOGGER.error(to_str(output))
                LOGGER.info('Ignoring swapspace mounting here...')
                exit_code = 0
            elif output.find('not found') != -1:
                LOGGER.error('Error: ' + to_str(output))
                exit_code = 0
            else:
                if result_id:
                    pass
                    #self.restore_manager.add_restore_detail_result(result_id, phase, 'Failed', output, False, self.seq, self)
                    #self.restore_manager.update_vm_restore_result(result_id, None, 'Failed', output)
                    #raise Exception('Error: ' + str(output))
        return (exit_code, output)

    def record_phase_details(self, vm, policy_config, result_id, phase, status, details, add_phase_details, add_vm_result=False, update_vm_result=False):
        if add_vm_result:
            LOGGER.info('Adding VM restore result status...')
            vm_id = ''
            vm_name = ''
            policy_id = ''
            if vm:
                vm_id = vm.id
                vm_name = vm.name
            if policy_config:
                policy_id = policy_config.id
            start_time = datetime.now()
            end_time = None
            details = 'Restore of ' + to_str(vm_name) + ' has started at time ' + to_str(datetime.now())
            result_id = self.restore_manager.add_vm_restore_result(policy_id, vm_id, start_time, end_time, status, details, self.bkp_result_id)
            if not result_id:
                error_desc = 'Error: ' + to_str(result_id).replace("'", '')
                LOGGER.error(error_desc)
                raise Exception(error_desc)
        else:
            if update_vm_result:
                LOGGER.info('Updating VM restore result status...')
                end_time = datetime.now()
                if not status:
                    status = 'Running'
                LOGGER.info('Updating VM restore result status as ' + to_str(status) + '...')
                self.restore_manager.update_vm_restore_result(result_id, end_time, status, details)
        if add_phase_details:
            LOGGER.info('Adding VM restore phase result status...')
            if not status:
                status = 'Success'
            self.restore_manager.add_restore_detail_result(result_id, phase, status, details, False, self.seq, self)
        return result_id

    def read_vm_config(self, node, auth, vm_id, vm_name):
        LOGGER.info('Reading vm config...')
        vm_info = {}
        disk_info = []
        local_config_file = os.path.join('/tmp', vm_name)
        f = node.node_proxy.open(local_config_file, 'r')
        vm_config = to_str(f.read())
        vm_info['vm_config'] = vm_config
        f.close()
        f = node.node_proxy.open(local_config_file, 'r')
        lines = f.readlines()
        vm_keys = []
        vm_keys.append('kernel')
        vm_keys.append('vif')
        vm_keys.append('extra')
        vm_keys.append('ssh_port')
        vm_keys.append('password')
        vm_keys.append('uuid')
        vm_keys.append('platform')
        vm_keys.append('on_reboot')
        vm_keys.append('backup_retain_days')
        vm_keys.append('on_shutdown')
        vm_keys.append('os_version')
        vm_keys.append('use_ssh_key')
        vm_keys.append('memory')
        vm_keys.append('ramdisk')
        vm_keys.append('quiescent_script_options')
        vm_keys.append('os_name')
        vm_keys.append('vnc')
        vm_keys.append('image_name')
        vm_keys.append('on_crash')
        vm_keys.append('image_id')
        vm_keys.append('image_conf')
        vm_keys.append('bootloader')
        vm_keys.append('ip_address')
        vm_keys.append('username')
        vm_keys.append('name')
        vm_keys.append('vfb')
        vm_keys.append('allow_backup')
        vm_keys.append('vcpus')
        vm_keys.append('os_flavor')
        vm_keys.append('root')
        vm_keys.append('STORAGE_STATS')
        vm_keys.append('disk')
        vm_keys.append('template_cfg')
        vm_keys.append('execution_context')
        for each_line in lines:
            for each_key in vm_keys:
                if each_line.find(to_str(each_key + ' =')) == 0:
                    param_list = each_line.split(' = ')
                    each_value = to_str(param_list[1]).strip()
                    vm_info[each_key] = each_value
        user_name = ''
        if auth.user:
            user_name = auth.user.user_name
        vm_info['created_user'] = user_name
        f.close()
        LOGGER.info('Virtual machine config file has been read successfully')
        return vm_info

    def get_disks(self, backup_config_path, vm_name, node, server, user_name, password, result_id, is_remote, backup_info):
        LOGGER.info('Getting disks info...')
        disk_info = []
        config_file = os.path.join(backup_config_path, vm_name)
        phase = 'transfer'
        op = 'COPY_CONFIG'
        cmd,custom_script_exists,params = self.get_script(op, node, False, None, None, None, phase, result_id, backup_info, None, None, None, config_file, None)
        self.exec_script(cmd, node, result_id, phase, custom_script_exists, params=params)
        LOGGER.info('Config file is copied from remote server to managed server for reading the same')
        local_config_file = os.path.join('/tmp', vm_name)
        f = node.node_proxy.open(local_config_file, 'r')
        for line in f:
            if line.find('disk') == 0:
                disk_list = eval(to_str(line).split('=', 1)[1])
                for each_disk in disk_list:
                    de = ImageDiskEntry(to_str(each_disk), None)
                    is_block_device = False
                    if to_str(de.filename).find('/dev') == 0:
                        is_block_device = True
                    disk_dic = {}
                    disk_dic['disk_type'] = de.type
                    disk_dic['disk_name'] = os.path.basename(de.filename)
                    disk_dic['disk_path'] = os.path.dirname(de.filename)
                    disk_dic['block_device'] = is_block_device
                    disk_dic['dev_type'] = de.device
                    disk_dic['read_write'] = de.mode
                    read_write = ''
                    read_write = de.mode
                    if read_write.find('r') != -1:
                        continue
                    else:
                        if read_write.find('w!') != -1:
                            disk_dic['read_write'] = 'w!'
                        else:
                            if read_write.find('w') != -1:
                                disk_dic['read_write'] = 'w'
                    disk_info.append(disk_dic)
        f.close()
        LOGGER.info('Collected disk info from virtual machine config file successfully')
        LOGGER.info('disk_info=' + str(disk_info))
        return disk_info

    def create_dir_structure(self, node, vm_name, remote_node, disk_info):
        objReturnVal = {}
        objReturnVal['backup_vm_path'] = None
        objReturnVal['backup_disk_path'] = None
        mkdir2(node, self.local_tmp)
        mkdir2(node, self.local_path)
        backup_vm_path = os.path.join(self.local_path, vm_name)
        mkdir2(node, backup_vm_path)
        local_tmp_mount = os.path.join(backup_vm_path, 'mount')
        mkdir2(node, local_tmp_mount)
        backup_disk_path = os.path.join(backup_vm_path, 'disks')
        mkdir2(node, backup_disk_path)
        for each_disk in disk_info:
            file_name = each_disk.get('disk_name')
            folder_path = os.path.join(self.local_path, vm_name, 'disks', file_name + '_DiskContent')
            mkdir2(node, folder_path)
        LOGGER.info('Directory structure is created')
        objReturnVal['backup_vm_path'] = backup_vm_path
        objReturnVal['backup_disk_path'] = backup_disk_path
        return objReturnVal

    def get_remote_node(self, hostname, username, password, isRemote):
        remote_node = ManagedNode(hostname, ssh_port=22, username=username, password=password, isRemote=isRemote, helper=None, use_keys=False, address=None)
        return remote_node

    def get_node_creds(self, node):
        user_name = None
        password = None
        ssh_port = None
        creds = DBSession.query(Credential).filter_by(entity_id=node.id).first()
        if creds:
            cred_details = creds.cred_details
            cred_type = creds.cred_type
            user_name = cred_details.get('username')
            password = cred_details.get('password')
            ssh_port = cred_details.get('ssh_port')
        return (user_name, password, ssh_port)

    def custom_script_exists(self, backup_info, phase):
        returnVal = False
        params = None
        transferMethod = backup_info['transferMethod']
        transferMethod_options = backup_info['transferMethod_options']
        LOGGER.info('Phase is ' + to_str(phase))
        LOGGER.info('Transfer method is ' + to_str(transferMethod))
        LOGGER.info('Transfer method options are ' + to_str(transferMethod_options))
        if transferMethod == 'CUSTOM':
            if phase == 'transfer':
                params = transferMethod_options.get('transfer_script')
                if params:
                    returnVal = True
        else:
            if phase == 'snapshot':
                params = transferMethod_options.get('snapshot_create_script')
                if params:
                    returnVal = True
    
            elif phase == 'mount':
                params = transferMethod_options.get('mount_script')
                if params:
                    returnVal = True
    
            elif phase == 'cleanup':
                params = transferMethod_options.get('snapshot_create_script')
                if params:
                    params = transferMethod_options.get('snapshot_delete_script')
                    if params:
                        returnVal = True
        if returnVal:
            LOGGER.info('Custom script is present')
        else:
            LOGGER.info('Custom script does not exist')
        return returnVal


    def exec_custom_script(self, backup_info, phase):
        script_exists = True
        script_path = ''
        script_name = ''
        params = None
        objCustomParam = {}
        transferMethod = backup_info['transferMethod']
        transferMethod_options = backup_info['transferMethod_options']
        if transferMethod == 'CUSTOM':
            if phase == 'transfer':
                params = transferMethod_options.get('transfer_script')
                script_path = os.path.join(self.custom_script_path, 'scripts', phase)
        elif phase == 'snapshot':
            params = transferMethod_options.get('snapshot_create_script')
            script_path = os.path.join(self.custom_script_path, 'scripts', phase)
        elif phase == 'mount':
            params = transferMethod_options.get('mount_script')
            script_path = os.path.join(self.custom_script_path, 'scripts', phase)
        elif phase == 'cleanup':
            param_tmp = transferMethod_options.get('snapshot_create_script')
            if param_tmp:
                params = transferMethod_options.get('snapshot_delete_script')
                script_path = os.path.join(self.custom_script_path, 'scripts', phase)
        if params:
            name_value_list = params.split(',')
            script_name = name_value_list[0]
            for each_pair in name_value_list:
                param_list = each_pair.split('=')
                if len(param_list) == 2:
                    param_key = param_list[0].strip()
                    if param_key[0:1] != '-':
                        param_key = '-' + param_key
                    param_value = param_list[1].strip()
                    objCustomParam[param_key] = param_value
        script_path = os.path.join(script_path, script_name)
        return (script_path, objCustomParam)

    def convert_config(self, vm_info, node_id, bkp_config_id):
        config = {}
        general_object = {}
        boot_params_object = {}
        misc_object = {}
        provision_object = {}
        storage_status_object = {}
        backup_object = {}
        network_object = {}
        high_avail_object = {}
        general_object['filename'] = ''
        general_object['memory'] = '256'
        general_object['vcpus'] = '1'
        general_object['start_checked'] = 'no'
        general_object['template_version'] = ''
        general_object['preferred_nodeid'] = to_str(node_id)
        general_object['os_flavor'] = vm_info.get('os_flavor')
        general_object['os_name'] = vm_info.get('os_name')
        general_object['os_version'] = vm_info.get('os_version')
        general_object['allow_backup'] = vm_info.get('allow_backup')
        boot_params_object['boot_check'] = False
        boot_params_object['kernel'] = vm_info.get('kernel')
        boot_params_object['ramdisk'] = vm_info.get('ramdisk')
        boot_params_object['extra'] = vm_info.get('extra')
        boot_params_object['root'] = vm_info.get('root')
        boot_params_object['on_reboot'] = vm_info.get('on_reboot')
        boot_params_object['on_crash'] = vm_info.get('on_crash')
        boot_params_object['on_shutdown'] = vm_info.get('on_shutdown')
        misc_object['platform'] = vm_info.get('platform')
        vfb_list = []
        vfb_list.append(vm_info.get('vfb'))
        misc_object['vfb'] = vfb_list
        vif_list = []
        vif_list.append(vm_info.get('vif'))
        misc_object['vif'] = vif_list
        misc_object['vnc'] = vm_info.get('vnc')
        provision_object['xvda_disk_type'] = 'VBD'
        provision_object['xvda_disk_fs_type'] = 'ext3'
        provision_object['xvda_disk_size'] = '1'
        provision_object['xvda_disk_create'] = 'yes'
        disk_list = []
        template_cfg = eval(vm_info.get('template_cfg'))
        for each_disk in template_cfg:
            disk = {}
            disk['type'] = each_disk.get('DISK_TYPE')
            disk['filename'] = each_disk.get('FILE_NAME')
            disk['device'] = each_disk.get('DEVICE')
            disk['mode'] = each_disk.get('READ_WRITE')
            disk['backup_content'] = each_disk.get('FILE/DIRECTORY')
            disk['option'] = 'CREATE_DISK'
            disk['disk_create'] = 'yes'
            disk['size'] = 10000
            disk['disk_type'] = 'VBD'
            disk['image_src'] = ''
            disk['image_src_type'] = ''
            disk['image_src_format'] = ''
            disk['fs_type'] = each_disk.get('FILE_SYSTEM')
            disk['storage_name'] = ''
            disk['storage_disk_id'] = ''
            disk['storage_id'] = ''
            disk['shared'] = False
            disk_list.append(disk)
        storage_status_object['disk_stat'] = disk_list
        backup_object['quiescent_script_stat'] = vm_info.get('quiescent_script_stat')
        backup_object['username'] = vm_info.get('username')
        backup_object['password'] = vm_info.get('password')
        backup_object['ip_address'] = vm_info.get('ip_address')
        backup_object['ssh_port'] = vm_info.get('ssh_port')
        backup_object['use_ssh_key'] = vm_info.get('use_ssh_key')
        backup_object['backup_retain_days'] = vm_info.get('backup_retain_days')
        backup_tab_list = []
        backup_tab = {}
        backup_tab['backup_id'] = bkp_config_id
        backup_tab['backup_all'] = False
        backup_tab['allow_backup'] = vm_info.get('allow_backup')
        backup_tab_list.append(backup_tab)
        backup_object['backup_stat'] = backup_tab_list
        network_tab_list = []
        network_tab = {}
        network_tab['mac'] = 'Autogenerated'
        network_tab['bridge'] = '$DEFAULT_BRIDGE'
        network_tab_list.append(network_tab)
        network_object['network'] = network_tab_list
        high_avail_object['vm_priority'] = ''
        config['general_object'] = general_object
        config['boot_params_object'] = boot_params_object
        config['misc_object'] = misc_object
        config['provision_object'] = provision_object
        config['storage_status_object'] = storage_status_object
        config['backup_object'] = backup_object
        config['network_object'] = network_object
        config['high_avail_object'] = high_avail_object
        return config

    def change_defn_transient_state(self, auth, vm_id, transient_state, owner, state_transaction):
        allowed,info = state_transaction.is_allowed(vm_id, transient_state, owner)
        if allowed == False:
            raise Exception(constants.NO_OP + '\n' + str(info['msg']))

    def get_task_creator(self):
        from stackone.viewModel.TaskCreator import TaskCreator
        tc = TaskCreator()
        return tc

    def get_script(self, op, node, custom_script_exists, objCustomParam, vm_name, snapshot_file, phase, result_id, backup_info, each_disk, ref_disk, bkp_result_id, config_file, local_dir_dic, context=None, fs=None):
        script_name = None
        server = None
        user_name = None
        password = None
        use_key = False
        remote_node = None
        cmd = ''
        block_device = ''
        disk_name = ''
        disk_path = ''
        disk_type = ''
        source = None
        destination = None
        backup_path = ''
        backup_vm_path = ''
        zip_location = ''
        zip_name = ''
        zip_structure = ''
        file_name = ''
        local_vm_path = ''
        local_disk_path = ''
        script_path = ''
        partition_name = ''
        volume_group = ''
        logical_volume = ''
        is_lvm = ''
        mount_device = ''
        if context:
            partition_name = context.get('PARTITON_NAME')
            volume_group = context.get('VOLUME_GROUP')
            logical_volume = context.get('LOGICAL_VOLUME')
            is_lvm = context.get('IS_LVM')
            mount_device = context.get('MOUNT_DEVICE')
        if backup_info:
            is_remote = backup_info.get('is_remote')
            transferMethod = backup_info.get('transferMethod')
            use_tar = backup_info.get('use_tar')
            compression_method = backup_info.get('compression_method')
            backup_type = backup_info.get('backup_type')
            backup_content = backup_info.get('backup_content')
            if is_remote == True:
                server = backup_info.get('server_name')
                user_name = backup_info.get('user_name')
                password = backup_info.get('password')
                use_key = backup_info.get('use_key')
                remote_node = self.get_remote_node(server, user_name, password, True)
            else:
                server = node.hostname
            source = os.path.join(backup_info.get('backup_destination'), 'disks')
        if bkp_result_id:
            zip_location,zip_name,zip_structure,inter_vm_path = self.backup_manager.get_zip_location(bkp_result_id)
        if local_dir_dic:
            local_vm_path = local_dir_dic.get('backup_vm_path')
            local_disk_path = local_dir_dic.get('backup_disk_path')
        if each_disk:
            block_device = each_disk.get('block_device')
            disk_name = each_disk.get('disk_name')
            file_name = disk_name
            disk_path = each_disk.get('disk_path')
            disk_type = each_disk.get('disk_type')
            if not disk_path:
                disk_name,disk_path = self.backup_service.get_file_name(each_disk.get('DISK_PATH'))
                file_name = disk_name
                disk_type = each_disk.get('DISK_PATH')

        if phase == 'transfer':
            #1191
            if not op:
                #886
                if is_remote:
                    #829
                    if transferMethod == 'CP':
                        op = 'SCP'
                        script_name = 'scp.sh'
                    #883
                    elif transferMethod == 'RSYNC':
                        op = 'REMOTE_RSYNC'
                        script_name = 'remote_rsync_restore.sh'
                    #883
                    else:
                        op = transferMethod
                        script_name = to_str(op + '.sh').lower()
                #887
                else:
                    if transferMethod == 'RSYNC':
                        op = 'RSYNC'
                        script_name = 'rsync_restore.sh'
                    #858--887
                    else:
                        op = 'CP'
                        script_name = to_str(op + '.sh').lower()
                    #887
            if op == 'COPY_CONFIG':
                #950
                if is_remote:
                    op = 'SCP'
                    script_name = 'scp.sh'
                else:
                    op = 'CP'
                    script_name = 'cp.sh'
                source = config_file
                destination = '/tmp'
            #1135
            else:
                if ref_disk and ref_disk != 'undefined' and ref_disk != 'true':
                    #999
                    source = ref_disk
                    destination = disk_name
                #1135
                else:
                    if use_tar:
                        source = os.path.join(zip_location, zip_name)
                        destination = local_vm_path
                    else:
                        if is_remote and backup_content == constants.BKP_RAW and block_device:
                            source = os.path.join(backup_info.get('backup_destination'), 'disks', file_name)
                            destination = os.path.join(self.local_path, vm_name, 'disks', file_name)
            if self.custom_script_exists(backup_info, phase):
                script_path,objCustomParam = self.exec_custom_script(backup_info, phase)
                custom_script_exists = True
        #2652

        elif phase == 'restore':
            #2399
            if op == 'UNZIP':
                #1301
                if use_tar:
                    #1297
                    if compression_method and compression_method != 'NONE':
                        op = compression_method
                        script_name = 'unzip.sh'
                    #1273
                    else:
                        op = 'UNTAR'
                        script_name = 'untar.sh'
                    source = os.path.join(local_vm_path, zip_name)
                    #2320
            else:
                if backup_content == constants.BKP_RAW:
                    #1595
                    if block_device:
                        #1470
                        op = 'DD_LOCAL'
                        script_name = 'dd.sh'
                        if use_tar:
                            source = os.path.join(zip_structure, 'disks', file_name)
                        #1446
                        else:
                            if is_remote:
                                source = os.path.join(local_dir_dic.get('backup_disk_path'), file_name)
                            else:
                                source = os.path.join(backup_info.get('backup_destination'), 'disks', file_name)
                        destination = os.path.join(disk_path, file_name)
                    else:
                        if is_remote:
                            #1493
                            op = 'SCP'
                            script_name = 'scp.sh'
                        else:
                            op = 'CP'
                            script_name = 'cp.sh'
                        if use_tar:
                            op = 'CP'
                            script_name = 'cp.sh'
                            source = os.path.join(zip_structure, 'disks', file_name)
                        else:
                            source = os.path.join(backup_info.get('backup_destination'), 'disks', file_name)
                        destination = disk_path
                        #2320
                elif backup_content == constants.BKP_CONTENT:
                    #2319
                    if op == 'PART_DETAILS' or op == 'VG_ACTIVATE' or op == 'VG_SCAN':
                        script_name = 'partition_details.sh'
                        source = os.path.join(disk_path, disk_name)
                    #2320
                    elif op == 'CONTENT_MOUNT':
                        #1807
                        script_name = 'content_copy.sh'
                        source = os.path.join(disk_path, file_name)
                        destination = os.path.join(local_dir_dic.get('backup_vm_path'), 'mount')
                        if not is_lvm:
                            #1768
                            source = mount_device
                            #2316
                        elif is_lvm:
                            source = os.path.join('/dev', volume_group, logical_volume)
                        #2316
                    elif op == 'COPY':
                        #2122
                        if is_remote:
                            op = 'CONTENT_SCP'
                            script_name = 'scp.sh'
                        else:
                            op = 'CONTENT_CP'
                            script_name = 'cp.sh'
                        if use_tar:
                            #1974
                            op = 'CONTENT_CP'
                            script_name = 'cp.sh'
                            if not is_lvm:
                                source = os.path.join(zip_structure, 'disks', file_name + '_DiskContent', partition_name, '*')
                            #2089
                            elif is_lvm:
                                source = os.path.join(zip_structure, 'disks', file_name + '_DiskContent', partition_name, volume_group, logical_volume, '*')
                                #2089
                        else:
                            if not is_lvm:
                                source = os.path.join(backup_info.get('backup_destination'), 'disks', file_name + '_DiskContent', partition_name, '*')
                            elif is_lvm:
                                source = os.path.join(backup_info.get('backup_destination'), 'disks', file_name + '_DiskContent', partition_name, '*')
                                #source = os.path.join(backup_info.get('backup_destination'), 'disks', file_name + '_DiskContent', partition_name, volume_group, logical_volume, '*')
                        destination = os.path.join(local_dir_dic.get('backup_vm_path'), 'mount')
                    #2320
                    elif op == 'CONTENT_UMOUNT':
                        script_name = 'content_copy.sh'
                        source = os.path.join(local_dir_dic.get('backup_vm_path'), 'mount')
                        #2320
                    elif disk_type == 'lvm' and op == 'MOUNT_SNAPSHOT':
                        script_name = 'snapshot.sh'
                        source = os.path.join(disk_path, file_name)
                        destination = os.path.join(local_dir_dic.get('backup_vm_path'), 'mount')
                    elif op == 'UMOUNT_SNAPSHOT':
                        script_name = 'snapshot.sh'
                        source = os.path.join(local_dir_dic.get('backup_vm_path'), 'mount')
            if op != 'UNZIP':
                #2389
                if self.custom_script_exists(backup_info, phase):
                    script_path,objCustomParam = self.exec_custom_script(backup_info, phase)
                    custom_script_exists = True
                #2390
                #2652
        elif phase == 'cleanup':
            #2651
            script_name = 'cleanup.sh'
            if op == 'REMOVE_VM_DIR':
                op = 'CLEAN'
                backup_vm_path = local_dir_dic.get('backup_vm_path')
            elif op == 'REMOVE_MAPPER':
                source = os.path.join(disk_path, disk_name)
            elif op == 'DETACH_VOL_GROUP':
                volume_group = os.path.join('/dev', volume_group)
            elif op == 'UNMOUNT_SNAP':
                if self.custom_script_exists(backup_info, phase):
                    #2592
                    script_path,objCustomParam = self.exec_custom_script(backup_info, phase)
                    custom_script_exists = True
                else:
                    op = 'CLEAN'
                    backup_vm_path = local_dir_dic.get('backup_vm_path')
                    snapshot_file = os.path.join(local_dir_dic.get('backup_vm_path'), 'mount')
        if not script_path:
            script_path = os.path.join(self.script_path, 'scripts', phase, script_name)
        cmd,params = self.get_command(op, node, script_path, source, destination, user_name, password, backup_path, backup_vm_path, server, custom_script_exists, objCustomParam, vm_name, snapshot_file, phase, result_id, use_key, volume_group, fs)
        return (cmd, custom_script_exists, params)


    def get_mount_device(self, node, result_id, phase):
        device = None
        script_path = os.path.join(self.script_path, 'scripts', phase, 'device.sh')
        cmd = script_path
        params = None
        exit_code,output = self.exec_script(cmd, node, result_id, phase, custom_script_exists=False, params=params)
        for i in range(0,7):
            device = '/dev/loop' + to_str(i)
            x = output.find(device)
            if x == -1:
                break
            continue
        LOGGER.info('free device for mounting is ' + to_str(device))
        return device

    def update_restore_status(self, restore_result_rec):
        self.restore_manager.update_restore_status(restore_result_rec)

    def get_sp_vm_restore_history(self, auth, node_id, node_type, search_text):
        result = self.restore_manager.get_sp_vm_restore_history(auth, node_id, node_type, search_text)
        result = replace_with_CMS_TZ(result, 'starttime', 'endtime')
        return result

    def get_vm_restore_task_result(self, auth, vm_id):
        result = self.restore_manager.get_vm_restore_task_result(auth, vm_id)
        result = replace_with_CMS_TZ(result, 'starttime', 'endtime')
        return result



