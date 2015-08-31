from stackone.core.utils.utils import to_unicode, to_str, constants, getHexID, copyToRemote, mkdir2, wait_for_task_completion, convert_to_CMS_TZ, replace_with_CMS_TZ, CancelException
from stackone.model import DBSession
from datetime import datetime
import time
from stackone.model.VM import VMDisks, VM
from stackone.model.availability import AvailState, StateTransition
from stackone.model.Backup import BackupManager, SPBackupConfig, SPbackup_VM_list, VMBackupResult
from stackone.model.Restore import RestoreManager
from stackone.model.ManagedNode import ManagedNode
from stackone.model.Groups import ServerGroup
from stackone.model.Credential import Credential
import logging
import Basic
import traceback
import os
import tg
from tg import session
import calendar
import transaction
from stackone.model.services import Task, TaskUtil
LOGGER = logging.getLogger('stackone.model')
class BackupService():
	def __init__(self):
		self.manager = Basic.getGridManager()
		self.backup_manager = BackupManager()
		self.restore_manager = RestoreManager()
		self.temp_path = '/var/cache/stackone/tmp'
		self.custom_path = '/var/cache/stackone/custom'
		self.script_path = '/var/cache/stackone/default/backup'
		self.custom_script_path = os.path.join(self.custom_path, 'backup')

	def getBackupManager(self):
		return self.backup_manager

	def InitateBackupTask(self, name, group_id):
		self.backup_manager.add_sp_backup_config(name, group_id, setting_id, schedule_id)

	def get_backup_settings(self, policy_config, node):
		objSettings = {}
		sp_bkp_settings = self.backup_manager.get_sp_backup_setting(policy_config.sp_backup_setting_id)
		objSettings['policy_id'] = policy_config.id
		objSettings['backup_type'] = sp_bkp_settings.backup_type
		objSettings['transferMethod'] = sp_bkp_settings.transferMethod
		objSettings['backup_content'] = sp_bkp_settings.backup_content
		objSettings['backup_destination'] = sp_bkp_settings.backup_destination
		objSettings['use_tar'] = sp_bkp_settings.use_tar
		objSettings['compression_type'] = sp_bkp_settings.compression_type
		objSettings['is_remote'] = sp_bkp_settings.is_remote
		objSettings['full_backup'] = sp_bkp_settings.full_backup
		objSettings['transferMethod_options'] = sp_bkp_settings.transferMethod_options
		objSettings['server'] = None
		objSettings['user_name'] = None
		objSettings['password'] = None
		objSettings['ssh_port'] = None
		objSettings['use_key'] = None
		if objSettings['is_remote'] == True:
			serverobj = self.backup_manager.get_server(sp_bkp_settings.server_id)
			if serverobj:
				objSettings['server'] = serverobj.name
				objSettings['user_name'] = serverobj.credential.cred_details['username']
				objSettings['password'] = serverobj.credential.cred_details['password']
				objSettings['ssh_port'] = serverobj.ssh_port
				objSettings['use_key'] = serverobj.use_key
		else:
			objSettings['server'] = node.hostname

		return objSettings


	def get_vm_state(self, vm_id):
		vm_state = None
		try:
			avail_state = DBSession.query(AvailState).filter_by(entity_id = vm_id).first()
			if avail_state:
				vm_state = self.get_vm_state_string(avail_state.avail_state)
		except Exception as ex:
			LOGGER.error('Error: ' + to_str(ex).replace("'", ''))
			raise Exception(to_str(ex))
		LOGGER.info('VM state is ' + to_str(vm_state))
		return vm_state

##########################
	def get_disk_list(self, vm, result_id, execution_context):
		disk_info = []
		disk_list = []
		lvm_disk_list = []
		vm_disks = DBSession.query(VMDisks).filter_by(vm_id = vm.id)
		for each_disk in vm_disks:
			if each_disk.read_write == 'r' or each_disk.skip_backup:
				continue
			else:
				disk_list.append(each_disk)
				if each_disk.disk_type == 'lvm':
					lvm_disk_list.append(each_disk)
				each_disk_info = {}
				each_disk_info['DISK_PATH'] = each_disk.disk_name
				each_disk_info['DISK_TYPE'] = each_disk.disk_type
				each_disk_info['READ_WRITE'] = each_disk.read_write
				disk_info.append(each_disk_info)
		execution_context['DISK_LIST'] = disk_info
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		LOGGER.info('The disk list is ' + to_str(disk_list))
		LOGGER.info('The LVM disk list is ' + to_str(lvm_disk_list))
		LOGGER.info('The disk info is ' + to_str(disk_info))
		return (disk_list, lvm_disk_list, execution_context)



	def wait_for_task(self, dom, task_id, action):
		returnVal = False
		wait_time = dom.get_wait_time(action)
		print '\n\nwait_time=======' + str(wait_time)
		wait_time = int(wait_time) + 3
		finished,status = wait_for_task_completion(task_id, wait_time)
		if finished == True and status == Task.SUCCEEDED:
			returnVal = True
		return returnVal


	def shutdown_vm(self, seq, auth, node, vm, policy_config, result_id, vm_state):
		tc = self.get_task_creator()
		wait_result = True
		try:
			if vm_state == VM.RUNNING:
				LOGGER.info('Shutting down VM...')
				details = 'Shutting down Virtual Machine...'
				seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				task_id = tc.vm_action(auth, vm.id, node.id, constants.SHUTDOWN, requester=constants.BACKUP)
				wait_result = self.wait_for_task(vm, task_id, constants.SHUTDOWN)
				if wait_result:
					LOGGER.info('VM is shutdown successfully')
					details = 'Virtual Machine is shutdown successfully'
					seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				else:
					LOGGER.info('Killing VM...')
					details = 'Killing Virtual Machine...'
					seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
					task_id = tc.vm_action(auth, vm.id, node.id, constants.KILL, requester=constants.BACKUP)
					if self.wait_for_task(vm, task_id, constants.KILL):
						LOGGER.info('VM is killed successfully')
						details = 'Virtual Machine is killed successfully'
						seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
					else:
						if vm_state == VM.PAUSED:
							LOGGER.info('Unpausing VM...')
							details = 'Resuming Virtual Machine...'
							seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
							task_id = tc.vm_action(auth, vm.id, node.id, 'unpause', requester=constants.BACKUP)
							wait_result = self.wait_for_task(vm, task_id, 'unpause')
							if wait_result:
								LOGGER.info('VM is unpaused successfully')
								LOGGER.info('Shutting down VM...')
								details = 'Virtual Machine is resumed successfully. Shutting down Virtual Machine...'
								seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
								task_id = tc.vm_action(auth, vm.id, node.id, constants.SHUTDOWN, requester=constants.BACKUP)
								wait_result = self.wait_for_task(vm, task_id, constants.SHUTDOWN)
								if not wait_result:
									LOGGER.info('Killing VM...')
									details = 'Killing Virtual Machine...'
									seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
									task_id = tc.vm_action(auth, vm.id, node.id, constants.KILL, requester=constants.BACKUP)
									self.wait_for_task(vm, task_id, constants.KILL)
									LOGGER.info('VM is killed successfully')
									details = 'Virtual Machine is killed successfully'
									seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
								else:
									LOGGER.info('VM is shutdown successfully')
									details = 'Virtual Machine is shutdown successfully'
									seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
							StateTransition.is_allowed(vm.id, constants.BACKING_UP, constants.BACKUP)
		except Exception as ex:
			raise Exception(to_str(ex))
		return seq


	def reset_vm(self, seq, auth, node, vm, policy_config, result_id, vm_state):
		LOGGER.info('Resetting VM...')
		if not vm:
			return None
		tc = self.get_task_creator()
		curr_vm_state = self.get_vm_state(vm.id)
		wait_result = True
		if vm_state == VM.RUNNING:
			if curr_vm_state == VM.SHUTDOWN:
				LOGGER.info('Starting VM...')
				details = 'Starting Virtual Machine...'
				seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				task_id = tc.vm_action(auth, vm.id, node.id, constants.START, requester=constants.BACKUP)
				wait_result = self.wait_for_task(vm, task_id, constants.START)
				if wait_result:
					LOGGER.info('VM is started successfully')
					details = 'Virtual Machine is started successfully'
					seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				StateTransition.is_allowed(vm.id, constants.BACKING_UP, constants.BACKUP)
			elif curr_vm_state == VM.PAUSED:
				LOGGER.info('Unpausing VM...')
				details = 'Resuming Virtual Machine...'
				seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				task_id = tc.vm_action(auth, vm.id, node.id, 'unpause', requester=constants.BACKUP)
				wait_result = self.wait_for_task(vm, task_id, 'unpause')
				if wait_result:
					LOGGER.info('VM is unpaused successfully')
					details = 'Virtual Machine is resumed successfully'
					seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				StateTransition.is_allowed(vm.id, constants.BACKING_UP, constants.BACKUP)

		elif vm_state == VM.PAUSED:
			if curr_vm_state == VM.RUNNING:
				LOGGER.info('Pausing VM...')
				details = 'Pausing Virtual Machine...'
				seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				task_id = tc.vm_action(auth, vm.id, node.id, constants.PAUSE, requester=constants.BACKUP)
				wait_result = self.wait_for_task(vm, task_id, constants.PAUSE)
				if wait_result:
					LOGGER.info('VM is paused successfully')
					details = 'Virtual Machine is paused successfully'
					seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				StateTransition.is_allowed(vm.id, constants.BACKING_UP, constants.BACKUP)
			elif curr_vm_state == VM.SHUTDOWN:
				LOGGER.info('Starting VM...')
				details = 'Starting Virtual Machine...'
				seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				task_id = tc.vm_action(auth, vm.id, node.id, constants.START, requester=constants.BACKUP)
				wait_result = self.wait_for_task(vm, task_id, constants.START)
				if wait_result:
					LOGGER.info('VM is started successfully')
					details = 'Virtual Machine is started successfully'
					seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				task_id = tc.vm_action(auth, vm.id, node.id, constants.PAUSE, requester=constants.BACKUP)
				wait_result = self.wait_for_task(vm, task_id, constants.PAUSE)
				if wait_result:
					LOGGER.info('VM is paused successfully')
					details = 'Virtual Machine is paused successfully'
					seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				StateTransition.is_allowed(vm.id, constants.BACKING_UP, constants.BACKUP)
		return seq


	def check_privileges(self, auth, vm_id):
		ent = auth.get_entity(vm_id)
		if not auth.has_privilege('EXEC_BACKUP_POLICY', ent):
			LOGGER.error(to_str(constants.NO_PRIVILEGE))
			raise Exception(constants.NO_PRIVILEGE)


	def perform_validation(self, vm_id):
		error_desc = ''
		if self.backup_manager.is_backing_up(vm_id):
			error_desc = 'Backup operation is going on this entity so this backup operation is not allowed.'
		else:
			if self.restore_manager.is_restoring(vm_id):
				error_desc = 'Restore operation is going on this entity so this backup operation is not allowed.'

		if error_desc:
			LOGGER.error('Error: ' + error_desc)
			raise Exception(error_desc)

		#record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
	def record_phase_details(self, seq, node, vm, policy_config, result_id, status, details, add_phase_details, add_vm_result=False, update_vm_result=False):
		if add_vm_result:
			print 'Adding VM backup result status...'
			temp_backup_destination = '/var/cache/stackone/backup'
			start_time = datetime.now()
			end_time = None
			details = 'Backup of ' + to_str(vm.name) + ' has started at time ' + to_str(datetime.now())
			print 'NUMBER OF RUN ',
			print policy_config.num_runs
			result_id = self.backup_manager.add_vm_backup_result(policy_config.id, vm.id, temp_backup_destination, start_time, end_time, 'Started', details, policy_config.num_runs, None, None, None, vm.name, node.id, node.hostname, execution_context=None)
			if not result_id:
				error_desc = 'Error: ' + to_str(result_id).replace("'", '')
				LOGGER.error(error_desc)
				raise Exception(error_desc)
		else:
			if update_vm_result:
				print 'Updating VM backup result status...'
				end_time = datetime.now()
				if not status:
					status = 'Running'
				LOGGER.info('Updating VM backup result status as ' + to_str(status) + '...')
				self.backup_manager.update_vm_backup_result(result_id, end_time, status, details, backup_destination=None, backup_size=None, zip_location=None, zip_name=None, zip_structure=None, local_vm_path=None, execution_context=None)
		if add_phase_details:
			print 'Adding VM backup phase result status...'
			if not status:
				status = 'Success'
			seq = self.backup_manager.add_backup_detail_result(result_id, None, status, details, seq)
		return (seq, result_id)


	def get_backup_size_final(self, seq, node, vm, policy_config, result_id, temp_dir_dic, backup_dest_dir_dic, objSettings, file_path=None):
		backup_size = 0
		if objSettings['is_remote'] == True:
			seq,backup_size = self.get_remote_backup_size(seq, node, vm, policy_config, result_id, temp_dir_dic, backup_dest_dir_dic, objSettings, file_path=None)
		else:
			seq,backup_size = self.get_backup_size(seq, node, vm, policy_config, result_id, temp_dir_dic, backup_dest_dir_dic, objSettings, file_path=None)
		return (seq, backup_size)


	def is_policy_exists(self, policy_config):
		returnVal = True
		config_obj = DBSession.query(SPBackupConfig).filter_by(id=policy_config.id).first()
		if not config_obj:
			error_desc = to_str('Backup policy with the name ' + policy_config.name + ' does not exist')
			LOGGER.error(error_desc)
			returnVal = False
			raise Exception(error_desc)
		return returnVal


	def get_value_from_vm_config(self, vm_config, key):
		value = ''
		params = to_str(vm_config).split('\n')
		for each_param in params:
			if each_param.find(key) >= 0:
				param_list_temp = to_str(each_param).split(' = ')
				value = param_list_temp[1]
				break
		return value


	def set_local_path(self):
		if tg.config.get('temp_path'):
			self.temp_path = tg.config.get('temp_path')
		if tg.config.get('custom_path'):
			self.custom_path = tg.config.get('custom_path')
		if tg.config.get('script_path_backup'):
			self.script_path = tg.config.get('script_path_backup')
		if tg.config.get('custom_script_path_backup'):
			self.custom_script_path = tg.config.get('custom_script_path_backup')


	def parse_content(self, each_content):
		LOGGER.info('Parsing content...')
		LOGGER.info('Input of each content is ' + each_content)
		if each_content:
			each_content = to_str(each_content).strip()
			if each_content == '/':
				return each_content
			if each_content.find('/') == 0:
				each_content = 'P1' + each_content
			else:
				each_content = each_content.replace(':', '', 1)
			last_index = each_content.find('/', len(each_content) - 1)
			if last_index >= 0:
				each_content = each_content[0:last_index]
		LOGGER.info('Output of each content is ' + each_content)
		return each_content


	def VMBackup(self, auth, vm_id, policy_config):
		LOGGER.info('Starting VMBackup...')
		result_id = None
		seq = 0
		node = None
		vm = None
		result_id = None
		objSettings = {}
		temp_dir_dic = None
		backup_dest_dir_dic = None
		snapshot_file_list = []
		part_details_list = {}
		disk_list = []
		lvm_disk_list = []
		vm_state = None
		execution_context = {}
		#import pdb; pdb.set_trace()
		try:
			vm = self.manager.get_dom(auth, vm_id)
			node_id,node = self.backup_manager.get_managed_node(auth, vm.id)
			self.set_local_path()
			self.check_privileges(auth, vm_id)
			self.perform_validation(vm_id)
			self.is_policy_exists(policy_config)
			self.change_defn_transient_state(auth, vm_id, constants.BACKING_UP, constants.BACKUP, StateTransition)
			result_id = None
			details = 'Starting backup of ' + to_str(vm.name) + ' at time ' + to_str(datetime.now())
			seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=True, update_vm_result=False)
			vm_state = self.get_vm_state(vm.id)
			objSettings = self.get_backup_settings(policy_config, node)
			execution_context['VM_ID'] = to_str(vm.id)
			execution_context['VM_NAME'] = to_str(vm.name)
			execution_context['NODE_ID'] = to_str(node.id)
			execution_context['BACKUP_RESULT_ID'] = to_str(result_id)
			execution_context['BACKUP_TYPE'] = objSettings.get('backup_type')
			execution_context['BACKUP_CONTENT'] = objSettings.get('backup_content')
			execution_context['IS_REMOTE'] = objSettings.get('is_remote')
			execution_context['USE_TAR'] = objSettings.get('use_tar')
			execution_context['COMPRESSION_TYPE'] = objSettings.get('compression_type')
			execution_context['TRANSFER_METHOD'] = objSettings.get('transferMethod')
			execution_context['BACKUP_DESTINATION'] = objSettings.get('backup_destination')
			execution_context['FULL_BACKUP'] = objSettings.get('full_backup')
			execution_context['TRANSFER_METHOD_OPTIONS'] = objSettings.get('transferMethod_options')
			execution_context['SERVER'] = objSettings.get('server')
			execution_context['USE_KEY'] = objSettings.get('use_key')
			execution_context['SSH_PORT'] = objSettings.get('ssh_port')
			self.backup_manager.update_vm_backup_result(result_id, None, None, None, None, None, None, None, None, None, execution_context)
			remote_node = None
			if objSettings['is_remote'] == True:
				remote_node = self.backup_manager.get_remote_node(objSettings)
			disk_list,lvm_disk_list,execution_context = self.get_disk_list(vm, result_id, execution_context)
			seq,temp_dir_dic,backup_dest_dir_dic,execution_context = self.prepare_backup(seq, auth, node, remote_node, vm, policy_config, result_id, objSettings, disk_list, execution_context)
			if TaskUtil.is_cancel_requested() == True:
				raise CancelException()
	
			if objSettings['backup_type'] == constants.HOT:
				seq,execution_context = self.quiescent_application(seq, node, vm, policy_config, result_id, objSettings, execution_context)
				if TaskUtil.is_cancel_requested() == True:
					raise CancelException()
	
				seq,snapshot_file_list,execution_context = self.get_snapshot(seq, auth, node, remote_node, vm, policy_config, result_id, objSettings, temp_dir_dic, backup_dest_dir_dic, lvm_disk_list, disk_list, execution_context)
				if TaskUtil.is_cancel_requested() == True:
					raise CancelException()
				seq,execution_context = self.resume_application(seq, node, vm, policy_config, result_id, objSettings, execution_context)
				if TaskUtil.is_cancel_requested() == True:
					raise CancelException()
			if objSettings['backup_type'] == constants.COLD:
				seq = self.shutdown_vm(seq, auth, node, vm, policy_config, result_id, vm_state)
				if TaskUtil.is_cancel_requested() == True:
					raise CancelException()
	
			if objSettings['backup_content'] == constants.BKP_CONTENT:
				seq,part_details_list,execution_context = self.mount(seq, auth, node, vm, policy_config, result_id, objSettings, temp_dir_dic, backup_dest_dir_dic, snapshot_file_list, disk_list, part_details_list, remote_node, execution_context)
				if TaskUtil.is_cancel_requested() == True:
					raise CancelException()
			seq,execution_context = self.transfer(seq, auth, node, vm, remote_node, policy_config, result_id, objSettings, temp_dir_dic, backup_dest_dir_dic, snapshot_file_list, disk_list, part_details_list, execution_context)
			if TaskUtil.is_cancel_requested() == True:
				raise CancelException()
			if objSettings['backup_type'] == constants.COLD:
				seq = self.reset_vm(seq, auth, node, vm, policy_config, result_id, vm_state)
				if TaskUtil.is_cancel_requested() == True:
					raise CancelException()
	
			##############################
#			if objSettings['backup_type'] == constants.HOT:
#				continue
			StateTransition.set_none_state(vm_id, constants.BACKUP)
			seq,execution_context = self.cleanup(seq, vm.id, result_id)
			if TaskUtil.is_cancel_requested() == True:
				raise CancelException()
			details = 'Backup of ' + to_str(vm.name) + ' completed successfully at time ' + to_str(datetime.now())
			seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, 'Success', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
			backup_size = 0
			seq,backup_size = self.get_backup_size_final(seq, node, vm, policy_config, result_id, temp_dir_dic, backup_dest_dir_dic, objSettings, file_path=None)
			self.backup_manager.update_vm_backup_result(result_id, datetime.now(), 'Success', None, None, backup_size, None, None, None, None, None)
		except Exception as ex:
			traceback.print_exc()
			LOGGER.error('Error: ' + to_str(ex).replace("'", ''))
			StateTransition.set_none_state(vm_id, constants.BACKUP)
			details = '100-' + to_str(ex).replace("'", '') + '. Time-' + to_str(datetime.now())
			seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, 'Failed', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
			seq = self.reset_vm(seq, auth, node, vm, policy_config, result_id, vm_state)
			StateTransition.set_none_state(vm_id, constants.BACKUP)
			self.cleanup(seq, vm_id, result_id)
			details = '101-' + to_str(ex).replace("'", '') + '. Time-' + to_str(datetime.now())
			seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, 'Failed', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
			if isinstance(ex, CancelException):
				return dict(status=constants.TASK_CANCELED, msg=constants.TASK_CANCEL_MSG, results=details)
			raise Exception(to_str(ex))


	def quiescent_application(self, seq, node, vm, policy_config, result_id, objSettings, execution_context):
		phase = 'quiescent_application'
		details = 'Application on virtual machine is being made quiescent'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		execution_context['PHASE'] = phase
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		vm_node = None
		cmd = None
		scripts = []
		vm_id = vm.id
		if vm:
			vm_config = vm.vm_config
			params = to_str(vm_config).split('\n')
			for each_param in params:
				if each_param.find('quiescent_script_options') != -1:
					param_list_temp = to_str(each_param).split(' = ')
					param_list = param_list_temp[1]
					param_dic = eval(param_list)
					for each_key in param_dic:
						script_name = each_key
						script_args = param_dic.get(each_key)
						cmd = script_name + ' ' + script_args
						cmd += ' -mode quiescent'
						scripts.append(cmd)
					break
		creds = DBSession.query(Credential).filter_by(entity_id=vm_id).first()
		if creds:
			cred_details = creds.cred_details
			objCreds = {}
			objCreds['user_name'] = cred_details.get('username')
			objCreds['password'] = cred_details.get('password')
			objCreds['server'] = cred_details.get('ip_address')
			objCreds['ssh_port'] = cred_details.get('ssh_port')
			if objCreds['user_name'] and objCreds['server']:
				vm_node = self.backup_manager.get_remote_node(objCreds)
				for each_script in scripts:
					cmd = each_script
					vm_node.node_proxy.exec_cmd(cmd)
		details = 'Application on virtual machine has been made quiescent'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		return (seq, execution_context)


	def quiescent_vm(self, seq, auth, node, vm, policy_config, result_id, objSettings, vm_state, execution_context):
		phase = 'quiescent_vm'
		tc = self.get_task_creator()
		wait_result = True
		execution_context['PHASE'] = phase
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		try:
			if vm_state == VM.RUNNING:
				LOGGER.info('Pausing VM...')
				details = 'Pausing virtual machine...'
				seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				task_id = tc.vm_action(auth, vm.id, node.id, constants.PAUSE, requester=constants.BACKUP)
				wait_result = self.wait_for_task(vm, task_id, constants.PAUSE)
				if wait_result:
					LOGGER.info('VM is paused successfully')
					details = 'Virtual machine is paused successfully'
					seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
				StateTransition.is_allowed(vm.id, constants.BACKING_UP, constants.BACKUP)
		except Exception as ex:
			raise Exception(to_str(ex))
		return (seq, execution_context)


	def prepare_backup(self, seq, auth, node, remote_node, vm, policy_config, result_id, objSettings, disk_list, execution_context):
		phase = 'prepare_backup'
		details = 'Preparing for the backup; creating backup directory structure and config file for virtual machine'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		execution_context['PHASE'] = phase
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		temp_dir_dic = self.create_dir_structure(seq, None, node, None, vm, self.temp_path, None, None, None, None, disk_list, objSettings, result_id, policy_config, phase)
		execution_context['BACKUP_TEMP_DIR_STRUCTURE'] = temp_dir_dic
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		backup_dest_dir_dic = self.create_dir_structure(seq, None, node, None, vm, objSettings['backup_destination'], objSettings['server'], objSettings['user_name'], objSettings['password'], remote_node, disk_list, objSettings, result_id, policy_config, phase)
		execution_context['BACKUP_DEST_DIR_STRUCTURE'] = backup_dest_dir_dic
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		details = 'Backup directories and config file for virtual machine has been created successfully'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', details, backup_dest_dir_dic.get('backup_vm_path'), None)
		return (seq, temp_dir_dic, backup_dest_dir_dic, execution_context)

	def get_snapshot(self, seq, auth, node, remote_node, vm, policy_config, result_id, objSettings, temp_dir_dic, backup_dest_dir_dic, lvm_disk_list, disk_list, execution_context):
		phase = 'snapshot'
		snapshot_taken = False
		details = 'Taking snapshot'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		execution_context['PHASE'] = phase
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		op = 'SNAPSHOT'
		use_temp_area = True
		snapshot_file_list = []
		if lvm_disk_list:
			for each_disk in lvm_disk_list:
				disk_path = each_disk.disk_name
				file_name,dir_path = self.get_file_name(disk_path)
				snapshot_file = 'snap_' + to_str(file_name)
				snapshot_file_path = os.path.join(dir_path, snapshot_file)
				snapshot_file_list.append(snapshot_file_path)
				cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, snapshot_file, mount_device=None, each_content=None, archive_file=None, make_archive=False, previous_backup=None, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
				seq,exit_code,output = self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
				snapshot_taken = True
		execution_context['SNAPSHOT_FILE_LIST'] = snapshot_file_list
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		if snapshot_taken:
			details = 'Snapshot has been taken successfully'
		else:
			details = 'LVM device is not found for taking snapshot. So skipping snapshot...'
		seq,result_id, = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		return (seq, snapshot_file_list, execution_context)


	def resume_vm(self, seq, auth, node, vm, policy_config, result_id, vm_state, execution_context):
		phase = 'resume_vm'
		wait_result = True
		execution_context['PHASE'] = phase
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		try:
			curr_vm_state = self.get_vm_state(vm.id)
			LOGGER.info('curr_vm_state=' + to_str(curr_vm_state))
			if curr_vm_state != VM.PAUSED:
				return seq
			tc = self.get_task_creator()
			LOGGER.info('vm_state=' + to_str(vm_state))
			if vm_state == VM.RUNNING:
				if curr_vm_state == VM.PAUSED:
					LOGGER.info('Unpausing the VM...')
					details = 'Resuming virtual machine'
					seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
					task_id = tc.vm_action(auth, vm.id, node.id, 'unpause', requester=constants.BACKUP)
					wait_result = self.wait_for_task(vm, task_id, 'unpause')
					if wait_result:
						LOGGER.info('VM is unpaused successfully')
						details = 'Virtual machine has been resumed successfully'
						seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
					StateTransition.is_allowed(vm.id, constants.BACKING_UP, constants.BACKUP)
		except Exception as ex:
			raise Exception(to_str(ex))
		return (seq, execution_context)


	def resume_application(self, seq, node, vm, policy_config, result_id, objSettings, execution_context):
		phase = 'resume_application'
		execution_context['PHASE'] = phase
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		details = 'Resuming application(s) in virtual machine'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		vm_node = None
		cmd = None
		scripts = []
		vm_id = vm.id
		if vm:
			vm_config = vm.vm_config
			params = to_str(vm_config).split('\n')
			for each_param in params:
				if each_param.find('quiescent_script_options') != -1:
					param_list_temp = to_str(each_param).split(' = ')
					param_list = param_list_temp[1]
					param_dic = eval(param_list)
					for each_key in param_dic:
						script_name = each_key
						script_args = param_dic.get(each_key)
						cmd = script_name + ' ' + script_args
						cmd += ' -mode resume'
						scripts.append(cmd)
					break
		creds = DBSession.query(Credential).filter_by(entity_id=vm_id).first()
		if creds:
			cred_details = creds.cred_details
			objCreds = {}
			objCreds['user_name'] = cred_details.get('username')
			objCreds['password'] = cred_details.get('password')
			objCreds['server'] = cred_details.get('ip_address')
			objCreds['ssh_port'] = cred_details.get('ssh_port')
			if objCreds['server'] and objCreds['user_name']:
				vm_node = self.backup_manager.get_remote_node(objCreds)
				for each_script in scripts:
					cmd = each_script
					vm_node.node_proxy.exec_cmd(cmd)
		details = 'Application(s) in virtual machine are resumed'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		return (seq, execution_context)

	def is_snapshot_file(self, disk_path, snapshot_file_list):
		returnVal = False
		snap_file = ''
		for snap_file in snapshot_file_list:
			snap_file_name,dir_path = self.get_file_name(snap_file)
			snap_file_name = snap_file_name[len('snap_'):len(snap_file_name)]
			disk_name,dir_path = self.get_file_name(disk_path)
			if snap_file_name == disk_name:
				returnVal = True
				break
		return (returnVal, snap_file)


	def has_lvm_partition(self, disk_part_details):
		LOGGER.info('Checking for lvm partition...')
		is_lvm = False
		for partition_name in disk_part_details:
			if partition_name  == 'DISK_PATH' or partition_name == 'VOLUME_GROUPS':
				continue
			each_part_details = disk_part_details.get(partition_name)
			flags = each_part_details.get('FLAGS')
			if to_str(flags).find('lvm') >= 0:
				is_lvm = True
				break
		return is_lvm

	def mount(self, seq, auth, node, vm, policy_config, result_id, objSettings, temp_dir_dic, backup_dest_dir_dic, snapshot_file_list, disk_list, part_details_list, remote_node, execution_context):
		phase = 'mount'
		details = 'Mounting...'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		execution_context['PHASE'] = phase
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		part_details = {}
		vg_details = {}
		use_temp_area = True
		backup_vm_path = temp_dir_dic.get('backup_vm_path')
		backup_disk_path = temp_dir_dic.get('backup_disk_path')
		backup_content = objSettings['backup_content']
		LOGGER.info('disk_list' + to_str(disk_list))
		if disk_list:
			for each_disk in disk_list:
				is_snap,snapshot_file_path = self.is_snapshot_file(each_disk.disk_name, snapshot_file_list)
				if is_snap:
					each_disk = snapshot_file_path
					disk_path = snapshot_file_path
					selective_content = self.backup_manager.get_backup_content(vm.id, backup_content, each_disk)
				else:
					disk_path = each_disk.disk_name
					selective_content = self.backup_manager.get_backup_content(vm.id, backup_content, each_disk.disk_name)
				file_name,dir_path = self.get_file_name(disk_path)
				part_details = self.get_partition_details(seq, node, vm, phase, each_disk, objSettings, result_id, policy_config, disk_path)
				is_lvm = self.has_lvm_partition(part_details)
				if is_lvm:
					LOGGER.info('Found lvm partition')
					vg_details = self.get_volume_groups(seq, node, vm, phase, each_disk, objSettings, result_id, policy_config)
				else:
					LOGGER.info('Not found lvm partition')
				for each_vg in vg_details:
					vg = vg_details.get(each_vg)
					volume_group = vg.get('VG_NAME')
					lv_details = self.get_logical_volumes(seq, node, vm, phase, each_disk, objSettings, result_id, policy_config, volume_group)
					vg['LOGICAL_VOLUMES'] = lv_details
				part_details['VOLUME_GROUPS'] = vg_details
				part_details_list[disk_path] = part_details
				execution_context['PARTITON_DETAILS'] = part_details_list
				self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
				self.create_partition_directories(node, part_details, vg_details, temp_dir_dic.get('backup_vm_path'), temp_dir_dic.get('backup_disk_path'), file_name, objSettings['is_remote'], selective_content)
				temp_node = None
				if remote_node:
					temp_node = remote_node
				else:
					temp_node = node
				self.create_partition_directories(temp_node, part_details, vg_details, backup_dest_dir_dic.get('backup_vm_path'), backup_dest_dir_dic.get('backup_disk_path'), file_name, objSettings['is_remote'], selective_content)
				self.mount_partitions(seq, node, vm, policy_config, result_id, objSettings, temp_dir_dic, backup_dest_dir_dic, snapshot_file_list, disk_list, phase, each_disk, part_details_list, selective_content, disk_path)
				#self.mount_partitions(seq, node, vm, policy_config, result_id, objSettings, temp_dir_dic, backup_dest_dir_dic, snapshot_file_list, disk_list, phase, each_disk, part_details_list, selective_content, disk_path)
		execution_context['PARTITON_DETAILS'] = part_details_list
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		if disk_list or snapshot_file_list:
			details = 'Mounting done successfully'
		else:
			if not disk_list:
				details = 'Could not find any disk for mounting.'
			else:
				if not snapshot_file_list:
					details = 'Could not find any snapshot for mounting.'

		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		return (seq, part_details_list, execution_context)



	def mount_partitions(self, seq, node, vm, policy_config, result_id, objSettings, temp_dir_dic, backup_dest_dir_dic, snapshot_file_list, disk_list, phase, each_disk, part_details_list, selective_content, disk_path):
		LOGGER.info('Mounting partitions...')
		use_temp_area = True
		mount_device = None
		op = None
		file_name,dir_path = self.get_file_name(disk_path)
		part_details = part_details_list.get(disk_path)
		LOGGER.info('part_details= ' + to_str(part_details))
		for partition_name in part_details:
			if partition_name == 'DISK_PATH' or partition_name == 'VOLUME_GROUPS' or partition_name == 'P2':
				continue
			else:
				LOGGER.info('Partition name is ' + to_str(partition_name))
				each_part_details = part_details.get(partition_name)
				LOGGER.info('each_part_details= ' + to_str(each_part_details))
				dev_mapper = each_part_details.get('DEV_MAPPER')
				flags = each_part_details.get('FLAGS')
				p_type = each_part_details.get('TYPE')
				file_system = each_part_details.get('FILE_SYSTEM')
				vgs_details = part_details.get('VOLUME_GROUPS')
				if p_type:
					if to_str(p_type).lower().find('extended') >= 0:
						LOGGER.info('We are not mounting extended partition here...')
						continue
	
				if file_system:
					if to_str(file_system).lower().find('swap') >= 0:
						LOGGER.info('We are not mounting swap partition here...')
						continue
		
				if flags:
					if to_str(flags).lower().find('swap') >= 0:
						LOGGER.info('We are not mounting swap partition here...')
						continue
				is_lvm = False
				if flags and flags.find('lvm') >= 0:
					is_lvm = True
					LOGGER.info('is_lvm=' + to_str(is_lvm))
				LOGGER.info('is_lvm=' + to_str(is_lvm))
				
				fs = None
				if flags.find('ntfs') >= 0 and flags.find('boot') >= 0:
					flags = to_str(flags).replace('boot', '')
					fs = flags.strip()
				else:
					if flags.find('ntfs') >= 0:
						fs = flags.strip()
				if not vgs_details:
					vgs_details = '/'
				volume_group = ''
				logical_volume = ''
				LOGGER.info('vgs_details=' + to_str(vgs_details))
				for vg_details in vgs_details:
					if vgs_details == '/':
						lvs = '/'
					else:
						vg_details = vgs_details.get(vg_details)
						#if partition_name == vg_details.get('PART_NAME'):
						if vg_details.get('PART_NAME'):
							volume_group = vg_details.get('VG_NAME')
							lvs = vg_details.get('LOGICAL_VOLUMES')
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
								if to_str(logical_volume) != 'lv_root' and to_str(logical_volume) != 'root':
									continue


							if selective_content:
								if not self.has_content(selective_content, partition_name, volume_group, logical_volume):
									continue

							op = 'MOUNT'
														
							cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', mount_device, None, None, False, None, partition_name, volume_group, logical_volume, is_lvm, fs)
							seq,exit_code,output = self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
		

#####################################
	def transfer_files(self, seq, node, vm, policy_config, result_id, phase, objSettings, temp_dir_dic, backup_dest_dir_dic, snapshot_file_list, disk_list, use_temp_area, part_details_list):
		LOGGER.info('Transfer files...')
		phase = 'transfer'
		details = 'Transferring backup files...'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		op = None
		device_block = False
		backup_file_list = []
		backup_content = objSettings['backup_content']
		is_remote = objSettings['is_remote']
		use_tar = objSettings['use_tar']
		previous_backup = self.get_previous_backup(policy_config)
		i = 0
		for each_disk in disk_list:
			is_snap,snapshot_file_path = self.is_snapshot_file(each_disk.disk_name, snapshot_file_list)
			if is_snap:
				each_disk = snapshot_file_path
				disk_path = snapshot_file_path
				backup_file_list.append(snapshot_file_path)
			else:
				disk_path = each_disk.disk_name
				backup_file_list.append(each_disk.disk_name)

			if disk_path.find('/dev') == 0:
				device_block = True
			else:
				device_block = False
	
			if backup_content == constants.BKP_RAW:
				if i > 0:
					previous_backup = 'NONE'
				i = i + 1
				if is_remote and device_block and not use_tar:
					make_archive = False
					use_temp_area = True
					cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', '', '', '', make_archive, previous_backup, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
					self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
					make_archive = False
					use_temp_area = False
					cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', '', '', '', make_archive, previous_backup, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
					self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
				else:
					make_archive = False
					cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', '', '', '', make_archive, previous_backup, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
					self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)

			elif  backup_content == constants.BKP_CONTENT:
				contents = self.get_selective_content(vm.id, backup_content, disk_path)
				for each_content in contents:
					LOGGER.info('Copying content ' + to_str(each_content) + ' ...')
					each_content = to_str(each_content).strip()
					make_archive = False
					partition_name = None
					#volume_group = None
					#logical_volume = None
					#is_lvm = False
					is_lvm = True
					LOGGER.info('part_details_list' + to_str(part_details_list))
					part_details = part_details_list.get(disk_path)
					vgs_details = part_details.get('VOLUME_GROUPS')
					if not vgs_details:
						vgs_details = '/'
					volume_group = ''
					logical_volume = ''

					LOGGER.info('vgs_details=' + to_str(vgs_details))
					for vg_details in vgs_details:
						if vgs_details == '/':
							lvs = '/'
						else:
							vg_details = vgs_details.get(vg_details)
							volume_group = vg_details.get('VG_NAME')
							lvs = vg_details.get('LOGICAL_VOLUMES')

						if lvs:
							for lv in lvs:
								if lvs == '/':
									volume_group = ''
									logical_volume = ''
									mount_device = dev_mapper
								else:
									lv = lvs.get(lv)
									logical_volume = lv.get('LV_NAME')
									if logical_volume.find('swap') == -1:
										break

					if i > 0:
						previous_backup = 'NONE'
					i = i + 1
					cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', '', each_content, '', make_archive, previous_backup, partition_name, volume_group, logical_volume, is_lvm)
					self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
					if TaskUtil.is_cancel_requested() == True:
						raise CancelException()
						continue
			if TaskUtil.is_cancel_requested() == True:
				raise CancelException()
				continue
		details = 'Transfer of files is complete'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		return (seq, backup_file_list)
		

	def get_selective_content(self, vm_id, backup_content, disk_path):
		returnVal = []
		selective_content = self.backup_manager.get_backup_content(vm_id, backup_content, disk_path)
		if selective_content:
			selective_content = selective_content.strip()
			contents = selective_content.split(',')
			returnVal = contents
		else:
			returnVal = '/'
		return returnVal


	def transfer_archive(self, seq, node, vm, policy_config, result_id, phase, objSettings, temp_dir_dic, backup_dest_dir_dic, archive_file):
		details = 'Transfering archive file...'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		op = None
		use_temp_area = False
		each_disk = None
		snapshot_file = None
		mount_device = None
		each_content = None
		cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, snapshot_file, mount_device, each_content, archive_file, make_archive=False, previous_backup=None, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
		self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
		if TaskUtil.is_cancel_requested() == True:
			raise CancelException()
		details = 'Transfer of archive file is complete'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		return seq


	def archive(self, seq, node, vm, policy_config, result_id, phase, objSettings, temp_dir_dic, backup_dest_dir_dic):
		details = 'Creating tar of the backup taken'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		use_temp_area = False
		archive_file = to_str(vm.name + '.tar')
		each_disk = None
		compression_type = objSettings['compression_type']
		use_tar = objSettings['use_tar']
		if compression_type == 'NONE':
			compression_type = None
		if compression_type:
			if compression_type == 'GZIP':
				archive_file = to_str(archive_file + '.gz')
			elif compression_type == 'BZIP2':
				archive_file = to_str(archive_file + '.bz2')
			op = compression_type
			cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', '', '', archive_file, make_archive=True, previous_backup=None, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
			self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
		else:
			op = 'MAKE_TAR'
			cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', '', '', archive_file, make_archive=True, previous_backup=None, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
			self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
		if TaskUtil.is_cancel_requested() == True:
			raise CancelException()
		details = 'Tarring backup is complete'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		return (seq, archive_file)


	def get_previous_backup(self, policy_config):
		full_bk_dest = None
		backup_result_obj_list = DBSession.query(VMBackupResult).filter_by(backup_id=policy_config.id).order_by(VMBackupResult.start_time).all()
		if backup_result_obj_list:
			last_index = len(backup_result_obj_list) - 2
			last_backup_result_obj = backup_result_obj_list[last_index]
			full_bk_dest = os.path.join(last_backup_result_obj.backup_destination, 'disks')
		return full_bk_dest


	def transfer(self, seq, auth, node, vm, remote_node, policy_config, result_id, objSettings, temp_dir_dic, backup_dest_dir_dic, snapshot_file_list, disk_list, part_details_list, execution_context):
		phase = 'transfer'
		archive_file = ''
		archive_file_path = ''
		archive_structure = ''
		is_remote = objSettings['is_remote']
		use_tar = objSettings['use_tar']
		execution_context['PHASE'] = phase
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, None, None, None, None, execution_context)
		if is_remote:
			if use_tar:
				use_temp_area = True
				seq,backup_file_list = self.transfer_files(seq, node, vm, policy_config, result_id, phase, objSettings, temp_dir_dic, backup_dest_dir_dic, snapshot_file_list, disk_list, use_temp_area, part_details_list)
				seq,archive_file = self.archive(seq, node, vm, policy_config, result_id, phase, objSettings, temp_dir_dic, backup_dest_dir_dic)
				seq = self.transfer_archive(seq, node, vm, policy_config, result_id, phase, objSettings, temp_dir_dic, backup_dest_dir_dic, archive_file)
				archive_file_path = backup_dest_dir_dic.get('backup_vm_path')
				archive_structure = temp_dir_dic.get('backup_vm_path')
			else:
				use_temp_area = False
				seq,backup_file_list = self.transfer_files(seq, node, vm, policy_config, result_id, phase, objSettings, temp_dir_dic, backup_dest_dir_dic, snapshot_file_list, disk_list, use_temp_area, part_details_list)
		else:
			use_temp_area = False
			seq,backup_file_list = self.transfer_files(seq, node, vm, policy_config, result_id, phase, objSettings, temp_dir_dic, backup_dest_dir_dic, snapshot_file_list, disk_list, use_temp_area, part_details_list)
			if use_tar:
				seq,archive_file = self.archive(seq, node, vm, policy_config, result_id, phase, objSettings, temp_dir_dic, backup_dest_dir_dic)
				archive_file_path = backup_dest_dir_dic.get('backup_vm_path')
				archive_structure = backup_dest_dir_dic.get('backup_vm_path')
		execution_context['ZIP_FILE'] = archive_file
		execution_context['ZIP_STRUCTURE'] = archive_structure
		self.backup_manager.update_vm_backup_result(result_id, None, None, None, None, None, None, None, None, None, execution_context)
		self.backup_manager.update_vm_backup_result(result_id, None, 'Running', None, None, None, archive_file_path, archive_file, archive_structure, temp_dir_dic.get('backup_vm_path'), None)
		backup_file_size_list = []
		file_list = ''
		for each_file in backup_file_list:
			dic_temp = {}
			file_name,dir_path = self.get_file_name(each_file)
			seq,backup_size = self.get_backup_size(seq, node, vm, policy_config, result_id, temp_dir_dic, backup_dest_dir_dic, objSettings, each_file)
			dic_temp['File Name'] = file_name
			dic_temp['File Size'] = backup_size
			dic_temp['File Location'] = dir_path
			backup_file_size_list.append(dic_temp)
			file_list += file_name + '\n'
		self.create_config_file(node, remote_node, vm, backup_dest_dir_dic.get('backup_config_path'), execution_context)
		details = ''
		if file_list:
			details = 'List of files backed up:\n' + to_str(file_list)

		if archive_file_path:
			details = details + 'Tar/ Zip file:\n' + archive_file_path
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		return (seq, execution_context)


	def cleanup_for_recovery(self, task_id):
		LOGGER.info('Cleanning up for recovery...')
		sp_backup_config = DBSession.query(SPBackupConfig).filter_by(task_id=task_id).first()
		if sp_backup_config:
			rec_list = DBSession.query(VMBackupResult).filter_by(backup_id=sp_backup_config.id, status='Running')
			seq = 500
			for rec in rec_list:
				result_id = rec.id
				vm_id = rec.vm_id
				seq = self.cleanup(seq, vm_id, result_id)


	def cleanup(self, seq, vm_id, result_id):
		LOGGER.info('Cleanning up...')
		phase = 'cleanup'
		details = 'Cleaning temporary files...'
		node = None
		temp_dir_dic = None
		backup_dest_dir_dic = None
		snapshot_file_list = []
		disk_list = {}
		part_details_list = {}
		execution_context = {}
		objSettings = {}
		policy_config = None
		vm_backup_result = self.backup_manager.get_vm_backup_result(result_id)
		
		if vm_backup_result:
			execution_context = vm_backup_result.execution_context
			part_details_list = execution_context.get('PARTITON_DETAILS')
			disk_list = execution_context.get('DISK_LIST')
			snapshot_file_list = execution_context.get('SNAPSHOT_FILE_LIST')
			backup_dest_dir_dic = execution_context.get('BACKUP_DEST_DIR_STRUCTURE')
			temp_dir_dic = execution_context.get('BACKUP_TEMP_DIR_STRUCTURE')
			node_id = execution_context.get('NODE_ID')
			node = DBSession.query(ManagedNode).filter_by(id=node_id).first()
			node.connect()
			vm_id = execution_context.get('VM_ID')
			backup_id = vm_backup_result.backup_id
			policy_config = self.backup_manager.get_sp_backup_config(backup_id)
			if policy_config:
				objSettings = self.get_backup_settings(policy_config, node)
		vm = DBSession.query(VM).filter_by(id = vm_id).first()
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		execution_context['PHASE'] = phase
		self.backup_manager.update_vm_backup_result(result_id, None, u'Running', None, None, None, None, None, None, None, execution_context)
		try:
			if not objSettings or not temp_dir_dic or not backup_dest_dir_dic:
				return seq
			use_temp_area = True
			backup_vm_path_tmp = None
			remote_node = None
			backup_content = objSettings['backup_content']
			use_tar = objSettings['use_tar']
			is_remote = objSettings['is_remote']
			if temp_dir_dic:
				backup_vm_path_tmp = temp_dir_dic.get('backup_vm_path')
	
			if snapshot_file_list and backup_content == constants.BKP_CONTENT:
				LOGGER.info('Umounting snapshot..')
				op = 'UMOUNT_SNAPSHOT'
				for each_disk in snapshot_file_list:
					cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', '', '', archive_file=None, make_archive=True, previous_backup=None, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
					self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
	
			LOGGER.info('backup_content= ' + to_str(backup_content))
			if disk_list and part_details_list and backup_content == constants.BKP_CONTENT:
				for each_disk in disk_list:
					disk_path = each_disk.get('DISK_PATH')
					each_disk = disk_path
					part_details = part_details_list.get(disk_path)
					for partition_name in part_details:
						if partition_name == 'DISK_PATH' or partition_name == 'VOLUME_GROUPS':
							continue
						else:
							LOGGER.info('Partition name is ' + to_str(partition_name))
							each_part_details = part_details.get(partition_name)
							LOGGER.info('each_part_details= ' + to_str(each_part_details))
							dev_mapper = each_part_details.get('DEV_MAPPER')
							flags = each_part_details.get('FLAGS')
							vgs_details = part_details.get('VOLUME_GROUPS')
							is_lvm = False
							if flags and flags.find('lvm') >= 0:
								is_lvm = True
							if is_lvm:
								vgs_details = part_details.get('VOLUME_GROUPS')
								for vg_details in vgs_details:
									vg_details = vgs_details.get(vg_details)
									volume_group = vg_details.get('VG_NAME')
									lvs = vg_details.get('LOGICAL_VOLUMES')
									for lv in lvs:
										lv = lvs.get(lv)
										logical_volume = lv.get('LV_NAME')
										LOGGER.info('Unmounting logical volume ' + to_str(logical_volume) + '...')
										op = 'UMOUNT_LV'
										cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', None, '', None, False, None, None, volume_group, logical_volume, is_lvm=False)
										self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
									LOGGER.info('Deactivating volume groups ' + to_str(volume_group) + '...')
									op = 'DETACH_VOL_GROUP'
									cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', None, '', None, False, None, None, volume_group, None, False)
									self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
							else:
								op = 'UMOUNT_DEVICE'
								cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', dev_mapper, '', archive_file=None, make_archive=True, previous_backup=None, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
								self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
					LOGGER.info('Removing dev mappers..')
					op = 'REMOVE_MAPPER'
					cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', None, '', archive_file=None, make_archive=True, previous_backup=None, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
					self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
			if backup_vm_path_tmp:
				LOGGER.info('Deleting main vm backup temp directory..')
				op = 'CLEAN'
				#import pdb; pdb.set_trace()
				each_disk = None
				mount_device = None
				cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, '', mount_device, '', archive_file=None, make_archive=True, previous_backup=None, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
				self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
				if backup_vm_path_tmp:
					parent_of_vm_dir = os.path.dirname(backup_vm_path_tmp)
					cmd = 'rm -rf ' + to_str(parent_of_vm_dir)
					LOGGER.info('Command=' + to_str(cmd))
					node.node_proxy.exec_cmd(cmd)
	
			LOGGER.info('Cleaning up some stuff in backup destination directory...')
			if is_remote:
				remote_node = self.backup_manager.get_remote_node(objSettings)
			else:
				remote_node = node
			if disk_list:
				for each_disk in disk_list:
					disk_path = each_disk.get('DISK_PATH')
					each_disk = disk_path
					if snapshot_file_list:
						is_snap,snapshot_file_path = self.is_snapshot_file(disk_path, snapshot_file_list)
						if is_snap:
							file_name,dir_path = self.get_disk_name(snapshot_file_path)
						else:
							file_name,dir_path = self.get_file_name(each_disk.disk_name)
					else:
						file_name,dir_path = self.get_file_name(disk_path)
	
					folder_path = os.path.join(backup_dest_dir_dic.get('backup_vm_path'), file_name + '_DiskContent')
					cmd = 'rm -rf ' + folder_path
					remote_node.node_proxy.exec_cmd(cmd)
					if not use_tar and backup_content == constants.BKP_RAW:
						folder_path = os.path.join(backup_dest_dir_dic.get('backup_disk_path'), file_name + '_DiskContent')
						cmd = 'rm -rf ' + folder_path
						LOGGER.info('Command=' + to_str(cmd))
						remote_node.node_proxy.exec_cmd(cmd)
	
			if use_tar:
				cmd = 'rm -rf ' + backup_dest_dir_dic.get('backup_disk_path')
				LOGGER.info('Command=' + to_str(cmd))
				remote_node.node_proxy.exec_cmd(cmd)
		except Exception as ex:
			traceback.print_exc()
			LOGGER.error('Error in cleanup: ' + to_str(ex).replace("'", ''))
			details = '90-' + to_str(ex).replace("'", '') + '. Time-' + to_str(datetime.now())
			seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, 'Failed', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
			raise Exception(to_str(ex))
		details = 'Cleanup is complete'
		seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, '', details, add_phase_details=True, add_vm_result=False, update_vm_result=True)
		return (seq, execution_context)


	def get_disk_name(self, snapshot_file_path):
		disk_name = ''
		dir_path = ''
		snapshot_file_name,dir_path = self.get_file_name(snapshot_file_path)
		disk_name = snapshot_file_name[len('snap_'):len(snapshot_file_name)]
		return (disk_name, dir_path)

	def get_script(self, seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, snapshot_file, mount_device, each_content, archive_file, make_archive, previous_backup, partition_name, volume_group, logical_volume, is_lvm, fs=None):
		backup_type = objSettings.get('backup_type')
		backup_content = objSettings.get('backup_content')
		backup_method = objSettings.get('transferMethod')
		backup_destination = objSettings.get('backup_destination')
		compression_type = objSettings.get('compression_type')
		is_remote = objSettings.get('is_remote')
		server = objSettings.get('server')
		user_name = objSettings.get('user_name')
		password = objSettings.get('password')
		ssh_port = objSettings.get('ssh_port')
		use_key = objSettings.get('use_key')
		use_tar = objSettings.get('use_tar')
		full_backup = objSettings.get('full_backup')
		transferMethod_options = objSettings.get('transferMethod_options')
		options = ''
		if transferMethod_options:
			if transferMethod_options.get('options'):
				options = transferMethod_options.get('options').strip()
		custom_script_exists = False
		objCustomParam = None
		vm_name = None
		file_name = ''
		dir_path = ''
		script_file = ''
		script_path = ''
		is_device_block = False
		source = ''
		destination = ''
		snapshot_size = ''
		backup_vm_path = ''
		cur_bk_path = ''
		if each_content:
			each_content = self.parse_content(each_content)
		if not previous_backup:
			previous_backup = 'NONE'
		if use_temp_area == True:
			backup_path = os.path.join(self.temp_path, 'backup')
			backup_vm_path = temp_dir_dic.get('backup_vm_path')
			backup_disk_path = temp_dir_dic.get('backup_disk_path')
		else:
			backup_path = os.path.join(self.temp_path, 'backup')
			if backup_dest_dir_dic:
				backup_vm_path = backup_dest_dir_dic.get('backup_vm_path')
				backup_disk_path = backup_dest_dir_dic.get('backup_disk_path')

		disk_path = None
		if each_disk:
			try:
				disk_path = each_disk.disk_name
				file_name,dir_path = self.get_file_name(disk_path)
			except Exception as ex:
				disk_path = each_disk
				file_name,dir_path= self.get_file_name(disk_path)
				file_name = file_name[len('snap_'):len(file_name)]
			if disk_path.find('/dev') == 0:
				is_device_block = True
		if phase == 'snapshot':
			source = disk_path
			destination = dir_path
			snapshot_size = self.get_snapshot_size(each_disk, vm.vm_config)
			vm_name = snapshot_file
			if self.custom_script_exists(objSettings, phase):
				script_path,objCustomParam = self.exec_custom_script(seq, node, objSettings, phase)
				custom_script_exists = True
			else:
				script_file = 'snapshot.sh'
		elif phase == 'mount':
			source = disk_path
			script_file = 'mount.sh'
			if op == 'PART_DETAILS' or op == 'VG_DETAILS' or op == 'LV_DETAILS':
				script_file = 'partition_details.sh'
			else:
				if each_disk.disk_type == 'lvm' and backup_type == constants.HOT:
					op = 'MOUNT'
					destination = os.path.join(backup_vm_path, file_name + '_DiskContent')
				else:
					#if not is_lvm:
					if to_str(logical_volume) != 'lv_root' and to_str(logical_volume) != 'root':
						op = 'MOUNT'
						source = mount_device
						destination = os.path.join(backup_vm_path, file_name + '_DiskContent', partition_name)
					else:
						op = 'MOUNT'
						source = os.path.join('/dev', volume_group, logical_volume)
						#destination = os.path.join(backup_vm_path, file_name + '_DiskContent', partition_name, volume_group, logical_volume)
						destination = os.path.join(backup_vm_path, file_name + '_DiskContent', partition_name)
			vm_name = mount_device
			if op == 'MOUNT' and each_disk.disk_type == 'lvm':
				if self.custom_script_exists(objSettings, phase):
					script_path,objCustomParam = self.exec_custom_script(seq, node, objSettings, phase)
					custom_script_exists = True
		elif phase == 'transfer':
			#2462
			#True GZIP False CP
			if make_archive:
				#1327
				if op == 'MAKE_TAR':
					script_file = 'tar.sh'
				else:
					script_file = 'zip.sh'
				if is_remote:
					source = temp_dir_dic.get('backup_disk_path')
					destination = os.path.join(temp_dir_dic.get('backup_vm_path'), archive_file)
				else:
					source = backup_dest_dir_dic.get('backup_disk_path')
					destination = os.path.join(backup_dest_dir_dic.get('backup_vm_path'), archive_file)
				#2400
			else:
				if backup_method == 'RSYNC':
					#1431
					LOGGER.info('Previous backup path is ' + to_str(previous_backup))
					LOGGER.info('Backup vm path is ' + to_str(backup_vm_path))
					if previous_backup != 'NONE':
						backup_path = previous_backup
						cur_bk_path = backup_vm_path
					else:
						backup_path = ''
						cur_bk_path = ''
			
				if is_remote:
					#2004
					if archive_file:
						#1491
						op = 'SCP'
						source = os.path.join(temp_dir_dic.get('backup_vm_path'), archive_file)
						destination = backup_vm_path
					#2378
					else:
						if use_temp_area:
						#1548
							if backup_method == 'RSYNC':
								if full_backup:
									op = 'FULL_RSYNC'
								else:
									op = 'RSYNC'
							else:
								op = 'CP'
						else:
							if backup_method == 'CP':
								op = 'SCP'
							elif backup_method == 'RSYNC':
								if full_backup:
									op = 'FULL_REMOTE_RSYNC'
								else:
									op = 'REMOTE_RSYNC'
							else:
								op = backup_method
						if backup_content == constants.BKP_RAW:
							#1749
							if is_device_block:
								#1733
								if use_temp_area:
									#1693
									op = 'DD'
									source = disk_path
									destination = os.path.join(temp_dir_dic.get('backup_disk_path'), file_name)
								#1746---2378
								else:
									source = os.path.join(temp_dir_dic.get('backup_disk_path'), file_name)
									destination = backup_disk_path
								#2001---2378
							else:
								source = disk_path
								destination = backup_disk_path
							#2378
						elif backup_content == constants.BKP_CONTENT:
							#2000
							if each_content and each_content != '/':
								#1943
								LOGGER.info('Copying ' + to_str(each_content) + ' content...')
								dir_path = os.path.join(backup_disk_path, file_name + '_DiskContent', each_content)
								self.create_parent_dir_struct(node, dir_path, objSettings)
								source = os.path.join(temp_dir_dic.get('backup_vm_path'), file_name + '_DiskContent', each_content)
								each_content = self.get_path_omitting_last_content(each_content)
								destination = os.path.join(backup_disk_path, file_name + '_DiskContent', each_content)
							#2001----2378
							else:
								LOGGER.info('Copying full partition...')
								source = os.path.join(temp_dir_dic.get('backup_vm_path'), file_name + '_DiskContent')
								destination = backup_disk_path
				else:
					if backup_method == 'RSYNC':
						if full_backup:
							op = 'FULL_RSYNC'
						else:
							op = 'RSYNC'
					else:
						op = 'CP'
					if backup_content == constants.BKP_RAW:
						#2126
						source = disk_path
						destination = backup_disk_path
						if is_device_block:
							op = 'DD'
							source = disk_path
							destination = os.path.join(backup_disk_path, file_name)
							#2378
					elif backup_content == constants.BKP_CONTENT:
						if each_content and each_content != '/':
							LOGGER.info('Copying ' + to_str(each_content) + ' content...')
							dir_path = os.path.join(backup_disk_path, file_name + '_DiskContent', each_content)
							self.create_parent_dir_struct(node, dir_path, objSettings)
							LOGGER.info('volume_group' + to_str(volume_group))
							LOGGER.info('logical_volume' + to_str(logical_volume))
							#source = os.path.join(temp_dir_dic.get('backup_vm_path'), file_name + '_DiskContent', each_content[:each_content.find('/')] + '/' + volume_group + '/' + logical_volume + each_content[each_content.find('/'):])
							source = os.path.join(temp_dir_dic.get('backup_vm_path'), file_name + '_DiskContent', each_content)
							each_content = self.get_path_omitting_last_content(each_content)
							destination = os.path.join(backup_disk_path, file_name + '_DiskContent', each_content)
							LOGGER.info('source=' + to_str(source))
							LOGGER.info('each_content' + to_str(each_content))
							LOGGER.info('destination' + to_str(destination))
						else:
							LOGGER.info('Copying full partition...')
							source = os.path.join(temp_dir_dic.get('backup_vm_path'), file_name + '_DiskContent')
							destination = backup_disk_path

				script_file = to_str(op).lower() + '.sh'
			if self.custom_script_exists(objSettings, phase):
				script_path,objCustomParam = self.exec_custom_script(seq, node, objSettings, phase)
				custom_script_exists = True
		elif phase == 'cleanup':
			if op == 'UMOUNT_SNAPSHOT':
				snapshot_file = disk_path
			elif op == 'UMOUNT_DEVICE':
				source = mount_device
			elif op == 'UMOUNT_LV':
				op = 'UMOUNT_DEVICE'
				source = os.path.join('/dev', volume_group, logical_volume)
			elif op == 'DETACH_VOL_GROUP':
				volume_group = os.path.join('/dev', volume_group)
			elif op == 'CLEAN':
				source = None
				destination = None
			elif op == 'REMOVE_MAPPER':
				source = disk_path
			script_file = 'cleanup.sh'
			if op == 'UMOUNT_SNAPSHOT':
				if self.custom_script_exists(objSettings, phase):
					script_path,objCustomParam = self.exec_custom_script(seq, node, objSettings, phase)
					custom_script_exists = True
		else:
			if op == 'SIZE':
				backup_path = backup_dest_dir_dic.get('backup_vm_path')
				script_path = os.path.join(self.script_path, 'scripts/backup_size.sh')
			elif op == 'REMOTESIZE':
				backup_path = backup_dest_dir_dic.get('backup_vm_path')
				script_path = os.path.join(self.script_path, 'scripts/remote_backup_size.sh')
		if not script_path:
			script_path = os.path.join(self.script_path, 'scripts', phase, script_file)
		cmd,params = self.get_command(op, script_path, source, destination, user_name, password, backup_path, backup_vm_path, server, custom_script_exists, objCustomParam, vm_name, snapshot_file, phase, result_id, options, use_key, snapshot_size, volume_group, logical_volume, cur_bk_path, ssh_port, fs)
		return (cmd, custom_script_exists, params)



	def create_parent_dir_struct(self, node, dir_path, objSettings):
		if objSettings['is_remote'] == True:
			node = self.backup_manager.get_remote_node(objSettings)
		cmd = 'mkdir -p ' + dir_path
		LOGGER.info('Command=' + to_str(cmd))
		node.node_proxy.exec_cmd(cmd)


	def get_path_omitting_last_content(self, each_content):
		path = ''
		param_list = each_content.split('/')
		list_len = len(param_list)
		i = 0
		while i < list_len - 1:
			path = os.path.join(path, param_list[i])
			i += 1
		return path


	def exec_script(self, cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=None):
		if custom_script_exists:
			self.prepare_custom_scripts(node)
		else:
			self.prepare_scripts(node)

		output = 'Success'
		exit_code = 0
		output,exit_code = node.node_proxy.exec_cmd(cmd, params=params, timeout=int(tg.config.get('backup_timeout')))
		LOGGER.info('Script output=' + to_str(output))
		LOGGER.info('exit_code=' + to_str(exit_code))
		if exit_code:
			seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, 'Failed', output, add_phase_details=True, add_vm_result=False, update_vm_result=False)
			if output.find('No such file or directory') != -1:
				LOGGER.error(to_str(output))
				LOGGER.info('Ignoring No such file or directory error...')
				exit_code = 0
			elif output.find('swapspace') != -1:
				LOGGER.error(to_str(output))
				LOGGER.info('Ignoring swapspace mounting here...')
				exit_code = 0
			elif output.find('not found') != -1:
				LOGGER.error('Error: ' + to_str(output))
				exit_code = 0
			elif exit_code == 1 and output.find('LOOP_CLR_FD: Device or resource busy') != -1:
				LOGGER.error(to_str(output))
				LOGGER.info('Ignoring LOOP_CLR_FD: Device or resource busy error...')
				exit_code = 0
			else:
				seq,result_id = self.record_phase_details(seq, node, vm, policy_config, result_id, 'Failed', output, add_phase_details=False, add_vm_result=False, update_vm_result=True)
				raise Exception('Error: ' + to_str(output))
		return (seq, exit_code, output)


	def get_script_arg(self, opt, value):
		if value:
			return opt + to_str(value)
		return opt + 'NONE'


	def get_command(self, op, script_path, source, destination, user_name, password, backup_path, backup_vm_path, server, custom_script_exists, objCustomParam, vm_name, snapshot_file, phase, result_id, options, use_key, snapshot_size, volume_group, logical_volume, cur_bk_path, ssh_port, fs):
		script_args = ''
		if custom_script_exists:
			if objCustomParam:
				for each_key in objCustomParam.keys():
					script_args += ' ' + each_key + ' ' + objCustomParam[each_key]
		if phase:
			script_folder_path = os.path.join(self.script_path, 'scripts', phase)
		else:
			script_folder_path = os.path.join(self.script_path, 'scripts')
		LOGGER.info('op= ' + to_str(op))
		if op == 'SNAPSHOT' or op == 'DD':
			script_args = self.get_script_arg(' -s ', source)
			script_args += self.get_script_arg(' -d ', destination)
			script_args += self.get_script_arg(' -v ', backup_vm_path)
			script_args += self.get_script_arg(' -m ', vm_name)
			script_args += self.get_script_arg(' -n ', server)
			script_args += self.get_script_arg(' -u ', user_name)
			script_args += ' -t ' + script_folder_path
			script_args += ' -z ' + snapshot_size
			script_args += ' -o ' + op
		elif op == 'MOUNT':
			script_args = self.get_script_arg(' -s ', source)
			script_args += self.get_script_arg(' -d ', destination)
			script_args += self.get_script_arg(' -v ', backup_vm_path)
			script_args += self.get_script_arg(' -m ', vm_name)
			script_args += self.get_script_arg(' -f ', snapshot_file)
			script_args += self.get_script_arg(' -l ', logical_volume)
			script_args += self.get_script_arg(' -t ', fs)
			script_args += ' -o ' + op
		elif op == 'PART_DETAILS' or op == 'VG_DETAILS' or op == 'LV_DETAILS':
			script_args = self.get_script_arg(' -d ', source)
			script_args += self.get_script_arg(' -v ', volume_group)
			script_args += ' -o ' + op
		elif op == 'MAKE_TAR' or op == 'GZIP' or op == 'BZIP2':
			script_args = self.get_script_arg(' -s ', source)
			script_args += self.get_script_arg(' -d ', destination)
			script_args += self.get_script_arg(' -v ', backup_vm_path)
			script_args += self.get_script_arg(' -m ', vm_name)
			script_args += self.get_script_arg(' -f ', snapshot_file)
			script_args += ' -o ' + op
		elif op == 'CP' or op == 'SCP':
			script_args = self.get_script_arg(' -s ', source)
			script_args += self.get_script_arg(' -d ', destination)
			script_args += self.get_script_arg(' -n ', server)
			script_args += self.get_script_arg(' -u ', user_name)
			script_args += ' -t ' + script_folder_path
			script_args += self.get_script_arg(' -i ', options)
			script_args += ' -o ' + op
			script_args += self.get_script_arg(' -k ', use_key)
			script_args += self.get_script_arg(' -r ', ssh_port)
		elif op == 'CLEAN' or op == 'UMOUNT_SNAPSHOT' or op == 'UMOUNT_DEVICE' or op == 'REMOVE_MAPPER' or op == 'DETACH_VOL_GROUP':
			script_args = self.get_script_arg(' -v ', backup_vm_path)
			script_args += self.get_script_arg(' -s ', snapshot_file)
			script_args += self.get_script_arg(' -m ', source)
			script_args += self.get_script_arg(' -d ', source)
			script_args += self.get_script_arg(' -g ', volume_group)
			script_args += ' -o ' + op
		elif op == 'PING':
			script_args = ' -n ' + server
		elif op == 'SIZE':
			script_args = ' -s ' + backup_path
		elif op == 'REMOTESIZE':
			script_args = ' -u ' + user_name
			script_args += ' -n ' + server
			script_args += ' -d ' + backup_path
			script_args += ' -t ' + script_folder_path
			script_args += self.get_script_arg(' -r ', ssh_port)
		elif op == 'RSYNC':
			full_bk_dest = backup_path
			script_args = ' -s ' + source
			script_args += ' -d ' + destination
			script_args += self.get_script_arg(' -f ', full_bk_dest)
			script_args += self.get_script_arg(' -i ', options)
			script_args += self.get_script_arg(' -c ', cur_bk_path)
		elif op == 'REMOTE_RSYNC':
			full_bk_dest = backup_path
			script_args = ' -s ' + source
			script_args += ' -d ' + destination
			script_args += self.get_script_arg(' -f ', full_bk_dest)
			script_args += ' -o ' + op
			script_args += ' -t ' + script_folder_path
			script_args += ' -u ' + user_name
			script_args += ' -n ' + server
			script_args += self.get_script_arg(' -i ', options)
			script_args += self.get_script_arg(' -k ', use_key)
			script_args += self.get_script_arg(' -c ', cur_bk_path)
			script_args += self.get_script_arg(' -r ', ssh_port)
		elif op == 'FULL_RSYNC':
			script_args = ' -s ' + source
			script_args += ' -d ' + destination
			script_args += self.get_script_arg(' -i ', options)
		elif op == 'FULL_REMOTE_RSYNC':
			full_bk_dest = backup_path
			script_args = ' -s ' + source
			script_args += ' -d ' + destination
			script_args += ' -t ' + script_folder_path
			script_args += ' -u ' + user_name
			script_args += ' -n ' + server
			script_args += self.get_script_arg(' -i ', options)
			script_args += self.get_script_arg(' -k ', use_key)
			script_args += self.get_script_arg(' -r ', ssh_port)

		cmd = script_path + script_args
		cmd_print = cmd
		params = []
		if password:
			params = [password]
			LOGGER.info('Command= ' + to_str(cmd_print.replace('-p ' + password, '-p *****')))
		else:
			LOGGER.info('Command= ' + to_str(cmd))
		return (cmd, params)
		
	def prepare_scripts(self, dest_node):
		if self.script_path:
			if not os.path.exists(self.script_path):
				mkdir2(dest_node, os.path.dirname(self.script_path))
		source = tg.config.get('backup_script')
		destination = self.script_path
		copyToRemote(source, dest_node, destination)


	def prepare_custom_scripts(self, dest_node):
		if self.custom_script_path:
			if not os.path.exists(self.custom_script_path):
				mkdir2(dest_node, os.path.dirname(self.custom_script_path))

		source = tg.config.get('backup_custom_script')
		destination = self.custom_script_path
		copyToRemote(source, dest_node, destination)


	def copy_custom_scripts(self, dest_node, backup_config):
		custom_backup_dir = os.path.join(self.custom_path, 'backup')
		if not os.path.exists(self.custom_path):
			mkdir2(dest_node, os.path.dirname(self.custom_path))
			mkdir2(dest_node, os.path.dirname(custom_backup_dir))
		else:
			if not os.path.exists(custom_backup_dir):
				mkdir2(dest_node, os.path.dirname(custom_backup_dir))
		sp_bkp_settings = self.backup_manager.get_sp_backup_setting(backup_config.sp_backup_setting_id)
		if not sp_bkp_settings:
			return None
		custom_script_location = None
		advance_options = sp_bkp_settings.advance_options
		if advance_options:
			custom_script_location = advance_options.get('custom_script_location')

		if custom_script_location:
			source = custom_script_location
			destination = custom_backup_dir
			copyToRemote(source, dest_node, destination)


	def custom_script_exists(self, objSettings, phase):
		returnVal = False
		params = None
		transferMethod = objSettings['transferMethod']
		transferMethod_options = objSettings['transferMethod_options']
		LOGGER.info('Phase is ' + to_str(phase))
		LOGGER.info('Transfer method is ' + to_str(transferMethod))
		LOGGER.info('Transfer method options are ' + to_str(transferMethod_options))
		if transferMethod == 'CUSTOM':
			if phase == 'transfer':
				params = transferMethod_options.get('transfer_script')
				if params.strip():
					returnVal = True
		else:
			if phase == 'snapshot':
				params = transferMethod_options.get('snapshot_create_script')
				if params.strip():
					returnVal = True
			elif phase == 'mount':
				params = transferMethod_options.get('mount_script')
				if params.strip():
					returnVal = True
			elif phase == 'cleanup':
				params = transferMethod_options.get('snapshot_create_script')
				if params.strip():
					params = transferMethod_options.get('snapshot_delete_script')
					if params.strip():
						returnVal = True
		if returnVal:
			LOGGER.info('Custom script is present')
		else:
			LOGGER.info('Custom script does not exist')
		return returnVal


	def exec_custom_script(self, seq, node, objSettings, phase):
		script_exists = True
		script_path = ''
		script_name = ''
		params = None
		objCustomParam = {}
		transferMethod = objSettings['transferMethod']
		transferMethod_options = objSettings['transferMethod_options']
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


	def get_logical_volumes(self, seq, node, vm, phase, each_disk, objSettings, result_id, policy_config, volume_group):
		op = 'LV_DETAILS'
		cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, None, None, None, result_id, '', None, None, None, False, None, None, volume_group, None, False)
		seq,exit_code,output = self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
		details = self.backup_manager.parse_details(output, op)
		return details

	def get_volume_groups(self, seq, node, vm, phase, each_disk, objSettings, result_id, policy_config):
		op = 'VG_DETAILS'
		cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, None, None, None, result_id, '', None, None, None, False, None, None, None, None, False)
		seq,exit_code,output = self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
		details = self.backup_manager.parse_details(output, op)
		return details

	def get_partition_details(self, seq, node, vm, phase, each_disk, objSettings, result_id, policy_config, disk_path):
		op = 'PART_DETAILS'
		cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, None, None, None, result_id, '', None, None, None, False, None, None, None, None, False)
		seq,exit_code,output = self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists, params=params)
		details = self.backup_manager.parse_details(output, op)
		details['DISK_PATH'] = disk_path
		return details

	def create_dir_structure(self, seq, op, node, script_path, vm, temp_path, server, user_name, password, remote_node, disk_list, objSettings, result_id, policy_config, phase):
		objReturnVal = {}
		objReturnVal['backup_date_path'] = None
		objReturnVal['backup_time_path'] = None
		objReturnVal['backup_vm_path'] = None
		objReturnVal['backup_disk_path'] = None
		objReturnVal['backup_config_path'] = None
		policy_id = objSettings['policy_id']
		backup_content = objSettings['backup_content']
		objDateTime = datetime.now()
		objDate = objDateTime.date()
		objTime = objDateTime.time()
		s_hour = objTime.hour
		s_minute = objTime.minute
		if len(to_str(s_hour)) == 1:
			s_hour = '0' + to_str(s_hour)
		if len(to_str(s_minute)) == 1:
			s_minute = '0' + to_str(s_minute)
		s_time = to_str(s_hour) + '_' + to_str(s_minute)
		temp_node = None
		if remote_node:
			temp_node = remote_node
		else:
			temp_node = node
		mkdir2(temp_node, temp_path)
		backup_path = os.path.join(temp_path, 'backup')
		mkdir2(temp_node, backup_path)
		backup_date_path = os.path.join(backup_path, policy_id, to_str(objDate))
		mkdir2(temp_node, backup_date_path)
		backup_time_path = os.path.join(backup_date_path, s_time)
		mkdir2(temp_node, backup_time_path)
		backup_vm_path = os.path.join(backup_time_path, vm.name)
		mkdir2(temp_node, backup_vm_path)
		backup_disk_path = os.path.join(backup_vm_path, 'disks')
		mkdir2(temp_node, backup_disk_path)
		backup_config_path = os.path.join(backup_vm_path, 'config')
		mkdir2(temp_node, backup_config_path)
		if backup_content == constants.BKP_CONTENT:
			for each_disk in disk_list:
				file_name,dir_path = self.get_file_name(each_disk.disk_name)
				content_path = os.path.join(backup_disk_path, file_name + '_DiskContent')
				mkdir2(temp_node, content_path)
				if not remote_node:
					content_path = os.path.join(backup_vm_path, file_name + '_DiskContent')
					mkdir2(temp_node, content_path)
		objReturnVal['backup_date_path'] = backup_date_path
		objReturnVal['backup_time_path'] = backup_time_path
		objReturnVal['backup_vm_path'] = backup_vm_path
		objReturnVal['backup_disk_path'] = backup_disk_path
		objReturnVal['backup_config_path'] = backup_config_path
		LOGGER.info('temp_dir_dic=' + to_str(objReturnVal))
		return objReturnVal


	def has_content(self, selective_content, partition_name, volume_group, logical_volume):
		returnVal = False
		LOGGER.info('selective_content=' + selective_content)
		if selective_content:
			selective_content = selective_content.strip()
			contents = selective_content.split(',')
			LOGGER.info('content list=' + to_str(contents))
			for each_content in contents:
				each_content = self.parse_content(each_content)
				each_content = each_content.strip()

				LOGGER.info('each_content= ' + to_str(each_content))
				LOGGER.info('partition_name=' + to_str(partition_name))
				LOGGER.info('volume_group=' + to_str(volume_group))
				LOGGER.info('logical_volume=' + to_str(logical_volume))

				if logical_volume:
					if each_content.find(partition_name + '/' + volume_group + '/' + logical_volume + '/') == 0:
						returnVal = True
						break
				if volume_group:
					if each_content.find(partition_name + '/' + volume_group + '/') == 0:
						returnVal = True
						break
				if partition_name:
					if each_content.find(partition_name) == 0:
						returnVal = True
						break

				if each_content == '/':
					returnVal = True
					break
		else:
			returnVal = True
		return returnVal


	def create_partition_directories(self, node, part_details, vg_details, backup_vm_path, backup_disk_path, file_name, is_remote, selective_content):
		for each_part in part_details:
			if each_part == 'DISK_PATH' or each_part == 'VOLUME_GROUPS':
				continue
			else:
				partition_name = each_part
				LOGGER.info('Partition name is ' + to_str(partition_name))
			self.create_partition_directory(part_details, partition_name, backup_vm_path, backup_disk_path, file_name, node, is_remote, selective_content)
			each_part_details = part_details.get(partition_name)
			flags = each_part_details.get('FLAGS')
			if flags:
				if flags.find('lvm')>=0:
					self.create_vg_lv_directories(partition_name, vg_details, backup_vm_path, backup_disk_path, file_name, node, is_remote, selective_content)


	def create_partition_directory(self, part_details, partition_name, backup_vm_path, backup_disk_path, file_name, node, is_remote, selective_content):
		if self.has_content(selective_content, partition_name, None, None):
			content_path = os.path.join(backup_disk_path, file_name + '_DiskContent', partition_name)
			LOGGER.info('backup disk path=' + to_str(content_path))
			mkdir2(node, content_path)
			LOGGER.info(to_str(partition_name) + ' directory is created')
			content_path = os.path.join(backup_vm_path, file_name + '_DiskContent', partition_name)
			LOGGER.info('backup vm path=' + to_str(content_path))
			mkdir2(node, content_path)


	def create_vg_lv_directories(self, partition_name, vgs_details, backup_vm_path, backup_disk_path, file_name, node, is_remote, selective_content):
		for each_vg in vgs_details:
			vg_details = vgs_details.get(each_vg)
			volume_group = vg_details.get('VG_NAME')
			if self.has_content(selective_content, partition_name, volume_group, None):
				parent_dir = os.path.join(backup_disk_path, file_name + '_DiskContent', partition_name)
				if not os.path.isdir(parent_dir):
					return None
				content_path = os.path.join(backup_disk_path, file_name + '_DiskContent', partition_name, volume_group)
				mkdir2(node, content_path)
				LOGGER.info(to_str(volume_group) + ' directory is created')
				content_path = os.path.join(backup_vm_path, file_name + '_DiskContent', partition_name, volume_group)
				mkdir2(node, content_path)
			parent_dir = os.path.join(backup_disk_path, file_name + '_DiskContent', partition_name, volume_group)
			if not os.path.isdir(parent_dir):
				return None
			lvs = vg_details.get('LOGICAL_VOLUMES')
			for each_lv in lvs:
				lv = lvs.get(each_lv)
				logical_volume = lv.get('LV_NAME')
				if self.has_content(selective_content, partition_name, volume_group, logical_volume):
					content_path = os.path.join(backup_disk_path, file_name + '_DiskContent', partition_name, volume_group, logical_volume)
					mkdir2(node, content_path)
					LOGGER.info(to_str(logical_volume) + ' directory is created')
					content_path = os.path.join(backup_vm_path, file_name + '_DiskContent', partition_name, volume_group, logical_volume)
					mkdir2(node, content_path)


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


	def ping_server(self, auth, server, username, password, ssh_port, usekey):
		result = None
		try:
			m_node = ManagedNode(hostname=server, ssh_port=int(ssh_port), username=username, password=password, isRemote=True, address=server)
			m_node.connect()
			result = 'Connection Established with ' + server
		except Exception as ex:
			result = str(ex)
		return result


	def get_file_name(self, file_path):
		file_name = ''
		dir_path = ''
		if file_path:
			dir_path = os.path.dirname(file_path)
			file_name = os.path.basename(file_path)
		return (file_name, dir_path)


	def allow_vm_backup(self, config_id, vm_id):
		returnVal = False
		sp_backup_vm_list = DBSession.query(SPbackup_VM_list).filter_by(backup_id=config_id, vm_id=vm_id).first()
		if sp_backup_vm_list:
			returnVal = sp_backup_vm_list.allow_backup
		return returnVal


	def create_config_file(self, node, remote_node, vm, backup_config_path, execution_context):
		if backup_config_path:
			if remote_node:
				temp_node = remote_node
			else:
				temp_node = node
			config_file = os.path.join(backup_config_path, vm.name)
			f = temp_node.node_proxy.open(config_file, 'w')
			f.write(to_str(vm.vm_config))
			context = 'execution_context = ' + to_str(execution_context)
			f.write(to_str(context))
			f.close()
		else:
			LOGGER.error('Error: Backup path is not available. Config file backup failed.')


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


	def get_backup_size(self, seq, node, vm, policy_config, result_id, temp_dir_dic, backup_dest_dir_dic, objSettings, file_path):
		result = None
		op = 'SIZE'
		phase = None
		if file_path:
			each_disk = file_path
		else:
			each_disk = None
		use_temp_area = True
		cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, snapshot_file=None, mount_device=None, each_content=None, archive_file=None, make_archive=False, previous_backup=None, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
		seq,exit_code,output = self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists=False, params=params)
		try:
			output = float(output)
		except Exception as ex:
			LOGGER.error('Error: ' + to_str(ex))
			output = 0
		result = str(output)
		return (seq, result)


	def get_remote_backup_size(self, seq, node, vm, policy_config, result_id, temp_dir_dic, backup_dest_dir_dic, objSettings, file_path=None):
		result = None
		op = 'REMOTESIZE'
		phase = None
		use_temp_area = False
		each_disk = None
		cmd,custom_script_exists,params = self.get_script(seq, node, vm, phase, op, each_disk, objSettings, use_temp_area, temp_dir_dic, backup_dest_dir_dic, result_id, snapshot_file=None, mount_device=None, each_content=None, archive_file=None, make_archive=False, previous_backup=None, partition_name=None, volume_group=None, logical_volume=None, is_lvm=False)
		seq,exit_code,output = self.exec_script(cmd, seq, node, vm, policy_config, result_id, phase, custom_script_exists=False, params=params)
		result = str(output)
		return (seq, result)

	def change_defn_transient_state(self, auth, vm_id, transient_state, owner, state_transaction):
		allowed,info = state_transaction.is_allowed(vm_id, transient_state, owner)
		if allowed == False:
			raise Exception(constants.NO_OP + '\n' + str(info['msg']))


	def get_task_creator(self):
		from stackone.viewModel.TaskCreator import TaskCreator
		tc = TaskCreator()
		return tc

	def get_snapshot_size(self, each_disk, vm_config):
		snapshot_size = tg.config.get(constants.prop_snapshot_file_size)
		if each_disk:
			device_type = to_str(each_disk.dev_type).strip()
			if device_type == 'hda':
				snapshot_size_temp = self.get_value_from_vm_config(vm_config, 'hda_snapshot_size')
				if snapshot_size_temp:
					snapshot_size = snapshot_size_temp
		return snapshot_size


	def skip_backup(self, each_disk, vm_config):
		skip_backup = False
		if each_disk:
			device_name = to_str(each_disk.dev_type).strip()
			if device_name == 'hda' or device_name == 'hdb' or device_name == 'hdd':
				returnVal = self.get_value_from_vm_config(vm_config, 'hda_skip_backup')
				returnVal = returnVal.lower()
				if returnVal == 'true' or returnVal == 'yes':
					skip_backup = True
					LOGGER.info('Skipping backup for this disk...')
		return skip_backup


	def get_backupsetupinfo(self, auth, node_id, node_type):
		result = self.backup_manager.get_backupsetupinfo(auth, node_id, node_type)
		result = replace_with_CMS_TZ(result, 'start_time')
		return result

	def get_backup(self, backup_name):
		result = DBSession.query(SPBackupConfig).filter(SPBackupConfig.name == backup_name).first()
		return result

	def get_recent_backupresult(self, backup_id, vm_id, date_time):
		result = DBSession.query(VMBackupResult).filter(VMBackupResult.backup_id == backup_id).filter(VMBackupResult.vm_id == vm_id).filter(VMBackupResult.status == u'Success').filter(VMBackupResult.end_time == date_time).order_by(VMBackupResult.start_time.desc()).first()
		return result

	def get_vm_backupsetupinfo(self, sp_id, vm_id):
		result = self.backup_manager.get_vm_backupsetupinfo(sp_id, vm_id)
		result = replace_with_CMS_TZ(result, 'start_time')
		return result

	def get_vm_backupsetupinfo_cli(self, sp_id, vm_id):
		results = []
		time = ''
		results = self.backup_manager.get_vm_backupsetupinfo(sp_id, vm_id, True)
		for result in results:
			time = result['Backup Start Time']
			start_time = to_str(time)
			result['Backup Start Time'] = start_time
		return results


	def list_backups(self, auth, vm_id, policyname, number, details):
		result = []
		if vm_id and policyname != None:
			config = DBSession.query(SPBackupConfig).filter(SPBackupConfig.name == policyname).first()
			backuptype_str = ''
			if config.rel_setting_conf.backup_type == constants.COLD:
				backuptype_str = 'Cold Backup'
			else:
				backuptype_str = 'Hot Backup'
			next_schedule = self.backup_manager.get_backup_schedule(config)
			backups = DBSession.query(VMBackupResult).filter_by(backup_id=config.id, vm_id=vm_id).order_by(VMBackupResult.start_time.desc())
			if details == 'yes':
				backups = backups.all()
			else:
				backups = backups.limit(number).all()
			backup_det = []
			for backup in backups:
				timestamp = to_str(backup.end_time)
				backup_det.append({'Backup Status':backup.status,'Backup timestamp':timestamp,'backup_size':backup.backup_size})
				backup.backup_size('backup_size')
			detail = dict({'Policy Name':config.name,'Backup Type':backuptype_str,'Schedule':next_schedule})
			result.append({'detail':detail,'Backup':backup_det})
			return result
		backupresults = DBSession.query(SPbackup_VM_list).filter(SPbackup_VM_list.vm_id == vm_id).all()
		for backupresult in backupresults:
			config_objs = DBSession.query(SPBackupConfig).filter(SPBackupConfig.id == backupresult.backup_id).all()
			for configs in config_objs:
				next_schedule = self.backup_manager.get_backup_schedule(configs)
				backuptype_str = ''
				if configs.rel_setting_conf.backup_type == constants.COLD:
					backuptype_str = 'Cold Backup'
				else:
					backuptype_str = 'Hot Backup'
				backups = DBSession.query(VMBackupResult).filter_by(backup_id=configs.id, vm_id=vm_id).order_by(VMBackupResult.start_time.desc())
				if details == 'yes':
					backups = backups.all()
				else:
					backups = backups.limit(number).all()
				backup_det = []
				for backup in backups:
					timestamp = to_str(backup.end_time)
					backup_det.append({'Backup Status':backup.status,'Backup timestamp':timestamp,'backup_size':backup.backup_size})
					backup.backup_size('backup_size')
				detail = dict({'Policy Name':config.name,'Backup Type':backuptype_str,'Schedule':next_schedule})
				result.append({'detail':detail,'Backup':backup_det})
				return result


	def get_sp_vm_backup_history(self, auth, node_id, node_type, search_text):
		result = self.backup_manager.get_sp_vm_backup_history(auth, node_id, node_type, search_text)
		result = replace_with_CMS_TZ(result, 'starttime', 'endtime')
		return result

	def get_sp_backup_task_result(self, auth, group_id):
		result = self.backup_manager.get_sp_backup_task_result(auth, node_id)
		result = replace_with_CMS_TZ(result, 'starttime', 'endtime')
		return result

	def get_vm_backup_task_result(self, auth, vm_id):
		result = self.backup_manager.get_vm_backup_task_result(auth, vm_id)
		result = replace_with_CMS_TZ(result, 'starttime', 'endtime')
		return result

	def get_individual_sp_backup_task_history(self, auth, backup_id):
		result = self.backup_manager.get_individual_sp_backup_task_history(auth, backup_id)
		result = replace_with_CMS_TZ(result, 'starttime', 'endtime')
		return result

	def sp_backup_failure(self, auth, node_id, node_type):
		result = self.backup_manager.sp_backup_failure(auth, node_id, node_type)
		result = replace_with_CMS_TZ(result, 'last_success')
		return result

	def get_sp_backup_config(self, config_id, group_id=None, policy_name=None):
		policy_config = self.backup_manager.get_sp_backup_config(config_id, group_id, policy_name)
		return policy_config

	def update_backup_status(self, bkup_result_rec):
		self.backup_manager.update_backup_status(bkup_result_rec)

	def update_task_id(self, config_id, task_id):
		self.backup_manager.update_task_id(config_id, task_id)

	def purge_backup(self, auth, group_id, backup_config_id):
		self.backup_manager.purge_backup(auth, group_id, backup_config_id, self.restore_manager)

	def purge_single_backup(self, auth, result_id):
		self.backup_manager.purge_single_backup(auth, result_id, self.restore_manager)

	def delete_backup_policy_task(self, policy_id, group_id):
		self.backup_manager.delete_backup_policy_task(policy_id, group_id)



