from stackone.core.utils.utils import Poller
from stackone.core.utils.utils import to_unicode, to_str, p_task_timing_start, p_task_timing_end
import stackone.core.utils.constants
from ManagedNode import ManagedNode
from stackone.model.DBHelper import DBHelper
from stackone.model.Entity import Entity, EntityType
from stackone.model.VM import VM, OutsideVM
from stackone.model.Metrics import MetricsService
from stackone.model.NodeInformation import Category, Component, Instance
constants = stackone.core.utils.constants
import traceback
import pprint
import socket
import logging
from datetime import datetime
from stackone.model.availability import AvailState, update_avail
from stackone.model import DBSession
from stackone.model.LockManager import LockManager
from sqlalchemy import func,orm
LOGGER = logging.getLogger('stackone.model.VNode')
AVL_LOGGER = logging.getLogger('AVAIL_TIMING')
import tg
import os
class VNode(ManagedNode):
	def __init__(self, platform, hostname=None, username='root', password=None, isRemote=False, ssh_port=22L, helper=None, use_keys=False, address=None):
		ManagedNode.__init__(self, hostname, ssh_port, username, password, isRemote, helper, use_keys, address)
		self.platform = platform
		self._managed_domfiles = None
		self._vmm = None
		self._node_info = None
		self.dom_list = None
		self.dom_list = self.get_dom_list()
		self.metrics_poller = None
		self.POLLING_INTERVAL = 5.0
		self.MAX_POLLS = 4L
		return None
	@orm.reconstructor
	def init_on_load(self):
		ManagedNode.init_on_load(self)
		self.platform = self.type
		self._managed_domfiles = None
		self._vmm = None
		self._node_info = None
		self.dom_list = None
		self.dom_list = self.get_dom_list()
		self.metrics_poller = None
		self.POLLING_INTERVAL = 5.0
		self.MAX_POLLS = 4L
		return None
	def _init_environ(self):
		if self._environ is None:
			self._environ = self.getEnvHelper()
		return self._environ
	def get_auto_config_dir(self):
		return ''

	def get_config_dir(self):
		return '/var/cache/stackone/vm_configs'

	def get_platform(self):
		return self.platform

	def get_dom_list(self):
		if self.dom_list is None:
			self.dom_list = DomListHelper(self)
		return self.dom_list

	def get_vmm_info(self):
		return self.get_vmm().info()

	def get_managed_domfiles(self):
		if self._managed_domfiles is None:
			self._managed_domfiles = []
			nodes = DBHelper().filterby(Entity, [], [Entity.entity_id == self.id])
			if len(nodes) > 0L:
				n = nodes[0L]
				for v in n.children:
					self._managed_domfiles.append(self.get_config_dir() + v.name)
		return self._managed_domfiles

	def _init_vmm(self):
		return None

	def get_vmm(self):
		if self._vmm is None:
			self._vmm = self._init_vmm()
		return self._vmm

	def get_running_vms(self):
		return {}

	@property
	def managed_domfiles(self):
		if self._managed_domfiles is None:
			self._managed_domfiles = self.get_managed_domfiles()
		return self._managed_domfiles
		
	###
	@property
	def node_info(self):
		if self._node_info is None:
			self._node_info = self.get_vmm_info()
		return self._node_info
	def __getitem__(self, param):
		vmm_info = self.get_vmm_info()
		if vmm_info is not None:
			if vmm_info.has_key(param):
				return vmm_info[param]
		return None

	def is_server_in_error(self):
		return ManagedNode.is_in_error(self)

	def is_vmm_in_error(self):
		return self.get_vmm().is_in_error()

	def connect(self):
		ManagedNode.connect(self)
		self.get_vmm().connect()
		self.refresh()

	def disconnect(self):
		if self._vmm is not None:
			self.get_vmm().disconnect()
			self._vmm = None
		ManagedNode.disconnect(self)
		return None

	def new_config(self, filename):
		return None

	def new_vm_from_config(self, config):
		return None

	def new_vm_from_info(self, info):
		return None

	def get_VM_count(self):
		node_ent = DBSession.query(Entity).filter(Entity.entity_id == self.id).first()
		return len(node_ent.children)

	def get_Managed_VM_count(self):
		node_ent = DBSession.query(Entity).filter(Entity.entity_id == self.id).first()
		return len(node_ent.children)

	def get_platform_info_display_names(self):
		return None
	#tianfeng
	def get_virtual_networks_info(self):
		return []
	#tianfeng
	def get_storage_resources_info(self):
		return []
	#pass
	def populate_platform_info(self):
		platform_dict = self.get_vmm_info()
		return platform_dict
	#pass
	def get_platform_info(self):
		try:
			platform_info = self.environ['platform_info']
			if platform_info is None:
				return {}
			return platform_info
		except Exception as e:
			LOGGER.error('Exception : ' + to_str(e) + ' on ' + self.hostname)
			print 'Exception : ' + to_str(e) + ' on ' + self.hostname
			traceback.print_exc()
		return {}

	def get_dom_ids(self):
		return self.dom_list.iterkeys()

	def get_dom_names(self):
		names = []
		for k in self.dom_list.iterkeys():
			names.append(self.get_dom(k).name)
		return names

	def get_all_dom_names(self):
		"""
		return list containing names of doms under this node from database.
		"""
		names = []
		vm_dict={}
		nodes=DBHelper().filterby(Entity,[],[Entity.entity_id==self.id])
		if len(nodes)>0:
			n=nodes[0]
			ids = [v.entity_id for v in n.children]
			vms = DBHelper().filterby(VM,[],[VM.id.in_(ids)])

			for v in vms:
				names.append(v.name)
				vm_dict[v.name]=v
		return (names,vm_dict)


	def get_doms(self):
		return self.dom_list

	def get_dom(self, name):
		if self.dom_list[name] is None:
			for dom in self.dom_list:
				if dom.name == name:
					return dom
		return self.dom_list[name]
	#pass
	def get_dom_from_config(self, path):
		dom = None
		dom = self.add_dom_config(path)
		if dom:
			config_from_file = dom.get_config()
			config_from_file.set_id(dom.id)
			filename = os.path.basename(path)
			file = '$VM_CONF_DIR/' + filename
			config_from_file['config_filename'] = file
		return dom
	#tianfeng
	def process_paths(self, paths):
		return paths

	def isDom0(self, name):
		if self.get_dom(name):
			return self.get_dom(name).isDom0()
		return False

	def isDomU(self, name):
		if self.get_dom(name):
			return self.get_dom(name).isDomU()
		return False

	def get_state(self, name):
		if self.get_dom(name):
			return self.get_dom(name).get_state()
		return None

	def is_resident(self, name):
		if self.get_dom(name):
			return self.get_dom(name).is_resident()
		return False

	def create_dom(self, config):
		if config.filename is None:
			raise Exception('filename must be set in the config.')
		new_vm = self.new_vm_from_config(config)
		new_vm._start(config)
		self.refresh()
		return config.name

	def create_dom_from_file(self, filename):
		config = self.new_config(filename)
		new_vm = self.new_vm_from_config(config)
		new_vm._start(config)
		self.refresh()
		return config.dom_name

	def refresh(self):
		self.dom_list.refresh()

	def add_dom_config(self, filename):
		return self.dom_list.add_dom_config(filename)

	def remove_dom_config(self, filename):
		return self.dom_list.remove_dom_config(filename)

	def get_metrics(self, refresh=False, filter=False):
		self.metrics = self.get_metric_snapshot(filter=filter)
		return self.metrics

	def get_metric_snapshot(self):
		return None

	def get_raw_metrics(self, hrs=None):
		return MetricsService().getServerMetrics(self.id, hrs)

	def get_vcpu_count(self):
		ent=DBHelper().filterby(Entity,[],[Entity.entity_id==self.id])[0]
		vmids=[x.entity_id for x in ent.children]
		vms=DBHelper().filterby(VM,[],[VM.id.in_(vmids)])
		vcpus=0
		for vm in vms:
			vcpus+=int(vm.get_config()['vcpus'])

		return vcpus


	def start_dom(self, name):
		self.get_dom(name)._start()

	def pause_dom(self, name):
		self.get_dom(name)._pause()

	def resume_dom(self, name):
		self.get_dom(name)._resume()

	def shutdown_dom(self, name):
		self.get_dom(name)._shutdown()

	def destroy_dom(self, name):
		self.get_dom(name)._destroy()
		self.refresh()

	def reboot_dom(self, name):
		self.get_dom(name)._reboot()

	def restore_dom(self, filename):
		vmm = self.get_vmm()
		if vmm:
			vmm.restore(filename)
		self.refresh()

	def migrate_dom(self, name, dest_node, live):
		dom = self.get_dom(name)
		if dom.isDom0():
			return Exception(name + ' can not be migrated.')
		self.get_dom(name)._migrate(dest_node, live, port=dest_node.migration_port)
		self.refresh()

	def migration_checks(self, vm_list, dest_node, live):
		err_list = []
		warn_list = []
		e_list,w_list = self.maintenance_check(dest_node)
		if len(e_list):
			err_list.extend(e_list)
		if len(w_list):
			warn_list.extend(w_list)
		op_e_list,op_w_list = self.migration_op_checks(vm_list, dest_node, live)
		if op_e_list is not None:
			err_list = err_list + op_e_list
		if op_w_list is not None:
			warn_list = warn_list + op_w_list
		for vm in vm_list:
			vm_e_list,vm_w_list = self.migration_vm_checks(vm.name, dest_node, live)
			if vm_e_list is not None:
				err_list = err_list + vm_e_list
			if vm_w_list is not None:
				warn_list = warn_list + vm_w_list
				
		return (err_list, warn_list)

	def maintenance_check(self, dest_node):
		e_list = []
		w_list = []
		if dest_node.is_maintenance():
			w_list.append(('Maintenance', 'Destination node %s is marked for maintenance' % dest_node.hostname))
		return (e_list, w_list)

	def augment_storage_stats(self, dom_name, dom_frame, dom=None):
		if dom is None:
			dom = self.get_dom(dom_name)
		if dom:
			cfg = dom.get_config()
			if cfg is not None:
				ss = cfg.get_storage_stats()
				if ss:
					total_shared = ss.get_shared_total()
					total_local = ss.get_local_total()
					dom_frame[constants.VM_SHARED_STORAGE] = total_shared
					dom_frame[constants.VM_LOCAL_STORAGE] = total_local
					dom_frame[constants.VM_TOTAL_STORAGE] = total_local + total_shared


	def update_storage_totals(self, frame):
		total_shared = 0.0
		total_local = 0.0
		for dom in self.get_doms():
			cfg = dom.get_config()
			if cfg:
				ss = cfg.get_storage_stats()
				if ss:
					total_shared += ss.get_shared_total()
					total_local += ss.get_local_total()
		frame[constants.VM_SHARED_STORAGE] = total_shared
		frame[constants.VM_LOCAL_STORAGE] = total_local
		frame[constants.VM_TOTAL_STORAGE] = total_shared + total_local

	def migration_op_checks(self, vm_list, dest_node, live):
		err_list = []
		warn_list = []
		for vm in vm_list:
			if vm.is_running() and not dest_node.is_up():
				err_list.append(('Status', 'Running VM %s cannot be migrated to a down node ' % (vm.name)))
				continue
		return (err_list, warn_list)

	def migration_vm_checks(self, vm_name, dest_node, live):
		"""
		Implements a series of compatiblity checks required for successful
		migration.
		"""
		err_list = []
		warn_list = []
		if self.is_up():
			vm = self.get_dom(vm_name)
		else:
			vm = DBHelper().find_by_name(VM, vm_name)
		
		if vm == None:
			err_list.append(('VM', 'VM %s not found.' % vm_name))
			return (err_list, warn_list)
			
		node_platform = dest_node.get_platform()
		vm_platform = vm.get_platform()
		if vm_platform != node_platform:
			err_list.append(('Platform', 'The destination node does not support required platform (%s)' % (vm_platform)))
		
		vm_conf = vm.get_config()
		if vm_conf is not None and dest_node.is_up():
			des = vm_conf.getDisks()
			if des:
				for de in des:
					if not dest_node.node_proxy.file_exists(de.filename):
						err_list.append(('Disk ', 'VM Disk %s not found on the destination node %s' % (de.filename, dest_node.hostname)))
						
		return (err_list, warn_list)

	def is_hvm(self):
		return self.isHVM

	def is_image_compatible(self, image):
		raise Exception('is_image_compatible not implemented : ', self.__class__)

	def is_dom_compatible(self, dom):
		raise Exception('is_dom_compatible not implemented : ', self.__class__)

	def get_unused_display(self):
		port = self.get_unused_port(5920L, 6000L)
		last_vnc = port - 5900L
		return last_vnc

	def heartbeat(self):
		if self.isRemote == False:
			return [self.UP, u'Localhost is always up']
		else:
			creds = self.get_credentials()
			ssh_port = creds["ssh_port"]
			if ssh_port is None:
				ssh_port = 22
			hostname = self.hostname
			sock=None
			try:
				try:
					try:
						ping_timeout = int(tg.config.get(constants.ping_timeout))
					except Exception,e:
						print e
						ping_timeout = 5
					sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
					#FIXME: Make timeout configurable
					sock.settimeout(ping_timeout)
					sock.connect((hostname, ssh_port))
				except socket.timeout:
					return [self.DOWN, u'Ping timed out. Host unreachable.']
				except socket.gaierror, e:
					return [self.DOWN, u'Hostname not found. ' + to_unicode(e)]
				except Exception, ex:
					return [self.DOWN, to_unicode(ex)]
			finally:
				if sock is not None:
					sock.close()
			return [self.UP, u'Ping succeeded']
	def vm_heartbeat(self):
		mtr = self.get_metrics(refresh=True)
		ret_val = {}
		vm_names = self.get_all_dom_names()[0]
		for vm in vm_names:
			try:
				state = mtr[vm]['STATE']
			except KeyError:
				state = VM.SHUTDOWN
			ret_val[vm] = [state, None]
		return ret_val


	def refresh_vm_avail(self):
		from stackone.model.Entity import EntityRelation
		from sqlalchemy import and_
		from sqlalchemy.orm import eagerload
		is_up = self.heartbeat()[0] == self.UP
		if is_up != True:
			return None
		strt = p_task_timing_start(AVL_LOGGER, 'VMHeartBeat', self.id, log_level='DEBUG')
		vm_states = self.vm_heartbeat()
		p_task_timing_end(AVL_LOGGER, strt)
		if is_up != self.is_up():
			return None
		strt = p_task_timing_start(AVL_LOGGER, 'ProcessVMHeartBeat', self.id, log_level='DEBUG')
		timestamp = datetime.now()
		for vm in DBSession.query(VM).filter(and_(and_(VM.id == EntityRelation.dest_id, EntityRelation.src_id == self.id), EntityRelation.relation == u'Children')).options(eagerload('current_state')):
			if vm.status == constants.MIGRATING:
				continue
			try:
				new_state,reason = vm_states[vm.name]
			except KeyError:
				continue
			if vm.current_state is None:
				vm.current_state = AvailState(vm.id, EntityType.DOMAIN, None, None, None, None)
			if vm.current_state.avail_state != new_state:
				if new_state in [VM.RUNNING,VM.PAUSED,VM.UNKNOWN]:
					vm.current_state.monit_state = AvailState.MONITORING
				from stackone.model.UpdateManager import UIUpdateManager
				if vm.current_state.avail_state != VM.NOT_STARTED:
					UIUpdateManager().set_updated_entities(vm.id)
				try:
					LockManager().get_lock(constants.AVAIL_STATE,self.id, constants.DOMAIN, constants.Table_avail_current)
					update_avail(vm, new_state, vm.current_state.monit_state, \
								timestamp, reason, LOGGER, is_up)
				finally:
					LockManager().release_lock()
		p_task_timing_end(AVL_LOGGER, strt)


	def refresh_avail(self):
		node_id = self.id
		strt = p_task_timing_start(AVL_LOGGER, 'HeartBeat', node_id, log_level='DEBUG')
		new_state,reason = self.heartbeat()
		p_task_timing_end(AVL_LOGGER, strt)
		timestamp = datetime.now()
		strt = p_task_timing_start(AVL_LOGGER, 'ProcessHeartBeat', node_id, log_level='DEBUG')
		if self.current_state is None:
			self.current_state = AvailState(node_id, EntityType.MANAGED_NODE, None, None, None, None)
		if self.current_state.avail_state != new_state:
			from stackone.model.UpdateManager import UIUpdateManager
			UIUpdateManager().set_updated_entities(node_id)
			try:
				LockManager().get_lock(constants.AVAIL_STATE, node_id, constants.MANAGED_NODE, constants.Table_avail_current)
				update_avail(self, new_state, self.current_state.monit_state, timestamp, reason, LOGGER)
			finally:
				LockManager().release_lock()
		p_task_timing_end(AVL_LOGGER, strt)
		return None

	def insert_outside_vms(self, vm_names):
		try:
			vm_count = DBSession.query(func.count(OutsideVM.name)).filter(OutsideVM.node_id == self.id).all()
			DBSession.query(OutsideVM).filter(OutsideVM.node_id == self.id).delete()
			for vm in vm_names:
				outside_vm = OutsideVM(to_unicode(vm.get('name')), self.id, vm.get('status'))
				DBSession.add(outside_vm)
			if len(vm_names) != vm_count[0][0]:
				from stackone.model.UpdateManager import UIUpdateManager
				UIUpdateManager().set_updated_entities(self.id)
		except Exception as e:
			LOGGER.error('Error in set_remote(): ' + str(e))


class DomListHelper():
	__doc__ = '\n    Class represent list of dom being tracked by this managed\n    node. \n    '
	def __init__(self, node):
		self._dom_dict = None
		self.node = node
		return None

	def _init_dom_list(self):
		if self._dom_dict is None:
			self.refresh()
		return self._dom_dict

	def __getattr__(self, name):
		if name == 'dom_dict':
			return self._init_dom_list()

	def refresh(self):
		vmm = self.node.get_vmm()
		current_dict = self.node.get_running_vms()		
		nodes=DBHelper().filterby(Entity,[],[Entity.entity_id==self.node.id])
		if len(nodes)>0:
			n=nodes[0]
			for v in n.children:
				vm=DBHelper().find_by_id(VM, v.entity_id)
				if vm is not None:
					vm.node=self.node
					vm._config.managed_node=self.node
					if current_dict.get(vm.name,None) is not None:						
						vm.set_vm_info(current_dict.get(vm.name)._vm_info)
						del current_dict[vm.name]
					current_dict[vm.id] = vm

		self._dom_dict = current_dict

	def __getitem__(self, item):
		if not item: return None
		if type(item) is int:
			for name, dom in self.dom_dict.iteritems():
				if dom.is_resident() and dom.id == item:
					return dom
		else:
			if self.dom_dict.has_key(item):
				return self.dom_dict[item]
			else:
				return None
	

	def __len__(self):
		return len(self.dom_dict)

	def __iter__(self):
		return self.dom_dict.itervalues()

	def iterkeys(self):
		return self.dom_dict.keys()

	def itervalues(self):
		return self.dom_dict.itervalues()

	def add_dom_config(self, filename):
		config = self.node.new_config(filename)
		config.update_storage_stats()
		new_dom = self.node.new_vm_from_config(config)
		self.dom_dict[new_dom.name] = new_dom
		return new_dom

	def remove_dom_config(self, filename):
		if filename in self.node.managed_domfiles:
			self.node.managed_domfiles.remove(filename)
			for d in self.dom_dict.itervalues():
				if d.get_config() is not None and d.get_config().filename == filename:
					del self.dom_dict[d.name]
					return True
		return False




