from stackone.core.utils.NodeProxy import Node
from stackone.core.utils.NodePool import NodePool
from stackone.core.utils.utils import LVMProxy, PyConfig, getHexID, copyToRemote
from stackone.core.utils.IPy import *
from stackone.core.utils.constants import *
from stackone.core.utils.utils import to_unicode, to_str, create_node, get_port_forward_cmd
from stackone.core.utils.phelper import HostValidationException, AuthenticationException, CommunicationException
import sys
import os
import re
import types
import platform
import traceback
import tg
import transaction
import time
import threading
import logging
LOGGER = logging.getLogger('stackone.model')
class NodeException(Exception):
    def __init__(self):
        Exception.__init__(self)



from stackone.model.NodeInformation import Category, Component, Instance
from sqlalchemy import Column, ForeignKey, PickleType
from sqlalchemy.types import *
from sqlalchemy import orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import Index
from stackone.model import DeclarativeBase, DBSession
from stackone.model.DBHelper import DBHelper
from stackone.model.Entity import Entity, EntityType
from stackone.config.ConfigSettings import NodeConfiguration
from stackone.model.Credential import Credential
from stackone.model.availability import AvailState, AvailHistory
from stackone.core.utils.NodeProxy import Node
from stackone.model.NodeCache import NodeCache
import stackone.core.utils.utils
constants = stackone.core.utils.constants
class ManagedNode(DeclarativeBase):
    UNKNOWN = -1L
    UP = 0L
    DOWN = 1L
    POWER_ON = 450L
    POWER_OFF = 460L
    PROVISION = 400L
    PROVISION_OVER = None
    FENCE = 410L
    FENCE_FAILED = None
    FENCE_SUCCEEDED = None
    UP_FAILOVER = 420L
    UP_FAILOVER_COMPLETE = None
    DOWN_FAILOVER = 430L
    DOWN_FAILOVER_COMPLETE = None
    IMPORT = 440L
    IMPORT_OVER = None
    STANDBY = u'STANDBY'
    VM_INVALID_CHARS = '(space,comma,quotes,/,\\|,<,>,!,&,%,.,^)'
    VM_INVALID_CHARS_EXP = '( |/|,|<|>|\\||\\!|\\&|\\%||\'|"|\\^|\\\\)'
    __tablename__ = 'managed_nodes'
    id = Column(Unicode(50L), primary_key=True)
    hostname = Column(Unicode(255L), nullable=False)
    socket = Column(Integer, default=1L)
    isRemote = Column(Boolean, default=False)
    isHVM = Column(Boolean, default=False)
    address = Column(Unicode(255L))
    type = Column(Unicode(50L), default=u'NONE')
    migration_port = Column(Integer, default=8002L)
    standby_status = Column(Unicode(50L), default=None)
    credential = relation(Credential, primaryjoin=id == Credential.entity_id, foreign_keys=[Credential.entity_id], uselist=False, cascade='all, delete, delete-orphan')
    instances = relation('Instance', backref='node')
    setup_config = relation('NodeConfiguration', uselist=False, cascade='all,delete, delete-orphan')
    current_state = relation(AvailState, primaryjoin=id == AvailState.entity_id, foreign_keys=[AvailState.entity_id], uselist=False, cascade='all, delete, delete-orphan')
    maintenance = Column(Boolean, default=False)
    maintenance_mig_node_id = Column(Unicode(50L))
    maintenance_operation = Column(Integer, default=0L)
    maintenance_migrate_back = Column(Boolean, default=False)
    maintenance_user = Column(Unicode(50L))
    external_manager_id = Column(Unicode(50L))
    __mapper_args__ = {'polymorphic_on': type}
    def __init__(self, hostname=None, ssh_port=22, username=Node.DEFAULT_USER, password=None, isRemote=False, helper=None, use_keys=False, address=None):
        self.hostname = hostname
        self.ssh_port = ssh_port
        self.username = username
        self.id = getHexID(hostname, [MANAGED_NODE])
        self.password = password
        self.isRemote = isRemote
        self.helper = helper
        self.use_keys = use_keys
        self.credential = Credential(self.id, u'', ssh_port=ssh_port, username=username, password=password, use_keys=use_keys)
        if not address:
            self.address = hostname
        else:
            self.address = address
        self.setup_config = None
        self._node_proxy_lock = threading.RLock()
        self._node_proxy = None
        self._lvm_proxy = None
        self._isLVMEnabled = None
        self._config = None
        self._environ = None
        self._exec_path = None
        self.metrics = None
        self.current_state = AvailState(self.id, EntityType.MANAGED_NODE, self.UP, AvailState.MONITORING, description=u'Newly created node.')
        self.push_bash_timeout_script()
        return None
    #pass
    def push_bash_timeout_script(self):
        try:
            if self.isRemote:
                bash = os.path.join(tg.config.get('common_script'), 'bash_timeout.sh')
                copyToRemote(bash, self, os.path.join(tg.config.get('stackone_cache_dir'), 'common/scripts'))
        except Exception as e:
            LOGGER.info('Could not copy bash_timeout.sh on %s. May be not a linux node' % self.hostname)
            raise e

#    init_on_load = orm.reconstructor()
#    node_proxy = property()
#    lvm_proxy = property()
#    isLVMEnabled = property()
#    config = property()
#    environ = property()
#    exec_path = property()
    @orm.reconstructor
    def init_on_load(self):
        self.ssh_port = None
        self.username = None
        self.password = None
        self.use_keys = None
        self.helper   = None
        self._node_proxy_lock = threading.RLock()

        self._node_proxy = None    # lazy-init self.node_proxy
        self._lvm_proxy = None     # lazy-init self.lvm_proxy
        self._isLVMEnabled = None  # lazy-init self.isLVMEnabled
        self._config = None        # lazy-init self.config
        self._environ = None       # lazy-init self.environ
        self._exec_path = None     # lazy init self.exec_path

        self.metrics = None
        
    @classmethod
    def get_status(cls, ids):
        status_dict = {to_str(cls.UP):0,to_str(cls.DOWN):0}
        result = AvailState.get_status(ids)
        for av in result:
            status_dict.update({to_str(av[0]):av[1]})
        return status_dict
        
        
    @classmethod
    def get_up_nodes(cls, node_ent_ids):
        up_nodes = DBSession.query(ManagedNode).join((AvailState,AvailState.entity_id == ManagedNode.id))\
                                                    .filter(AvailState.avail_state == ManagedNode.UP).filter(ManagedNode.standby_status == None)\
                                                    .filter(ManagedNode.id.in_(node_ent_ids)).all()
        return up_nodes
    @property
    def node_proxy(self):
        if self._node_proxy is None:
            self._node_proxy = self._init_node_proxy()
        return self._node_proxy
    @property
    def lvm_proxy(self):
        if self._lvm_proxy is None:
            self._lvm_proxy = self._init_lvm_proxy()
        return self._lvm_proxy
    @property
    def isLVMEnabled(self):
        if self._isLVMEnabled is None:
            self._isLVMEnabled = self._init_isLVMEnabled()
        return self._isLVMEnabled
    @property
    def config(self):
        if self._config is None:
            self._config = self._init_config()
        return self._config
    @property
    def environ(self):
        if self._environ is None:
            self._environ = self._init_environ()
        return self._environ
    @property
    def exec_path(self):
        if self._exec_path is None:
            self._exec_path = self._init_exec_path()
        return self._exec_path
    def stop_monitoring(self):
        self.current_state.monit_state = AvailState.NOT_MONITORING

    def start_monitoring(self):
        self.current_state.monit_state = AvailState.MONITORING

    def is_in_error(self):
        if self.is_authenticated():
            return self._node_proxy.get_last_error() is not None
        return True

    def disconnect(self):
        if self._node_proxy is not None:
            self._node_proxy.disconnect()
            self._node_proxy = None
        return None

    def connect(self):
        credentials = self.get_credentials()
        if self._node_proxy is not None:
            self._node_proxy.connect()
        else:
            self._init_node_proxy()
        return None

    def is_authenticated(self):
        if self._node_proxy is not None:
            return self._node_proxy.n_p is not None
        return self._node_proxy

    def is_up(self):
        up = False
        if self.current_state.avail_state == self.UP:
            up = True
        return up

    def is_standby(self):
        return self.standby_status == self.STANDBY

    def set_standby(self, standby=False):
        if standby == False or standby == None:
            self.standby_status = None
        else:
            if standby == True:
                self.standby_status = to_unicode(self.STANDBY)
        return None

    def set_credentials(self, username, password):
        self.username = username
        self.password = password

    def get_credentials(self):
        return self.credential.cred_details

    def set_node_credentials(self, type, **cred_details):
        self.credential.cred_type = type
        self.credential.cred_details = cred_details

    def is_remote(self):
        return self.isRemote

    def get_address(self):
        return self.address

    def set_address(self, address):
        self.address = address

    def get_metrics(self, refresh=False, filter=False):
        if not refresh:
            return self.metrics

    def get_VM_count(self):
        pass

    def get_console(self):
        pass

    def get_terminal(self, username, password):
        pass

    def get_vnc(self):
        pass
    #pass
    def get_node_proxy_class(self):
        return Node

    def get_os_info(self):
        try:
            os_info = self.environ['os_info']
            if os_info is None:
                return {}
            return os_info
        except Exception as e:
            LOGGER.error('Exception : ' + to_str(e) + ' on ' + self.hostname)
            print 'Exception : ' + to_str(e) + ' on ' + self.hostname
            traceback.print_exc()
        return {}

    def get_network_info(self):
        try:
            network_info = self.environ['network_info']
            if network_info is None:
                return []
            return network_info
        except Exception as e:
            LOGGER.error('Exception : ' + to_str(e) + ' on ' + self.hostname)
            print 'Exception : ' + to_str(e) + ' on ' + self.hostname
            traceback.print_exc()
        return []

    def get_nic_info(self):
        try:
            nic_info = self.environ['nic_info']
            if nic_info is None:
                return {}
            return nic_info
        except Exception as e:
            LOGGER.error('Exception : ' + to_str(e) + ' on ' + self.hostname)
            print 'Exception : ' + to_str(e) + ' on ' + self.hostname
            traceback.print_exc()
        return {}

    def get_bridge_info(self):
        try:
            bridge_info = self.environ['bridge_info']
            if bridge_info is None:
                return {}
            return bridge_info
        except Exception as e:
            LOGGER.error('Exception : ' + to_str(e) + ' on ' + self.hostname)
            print 'Exception : ' + to_str(e) + ' on ' + self.hostname
            traceback.print_exc()
        return {}

    def get_default_bridge(self):
        try:
            default_bridge = self.environ['default_bridge']
            return default_bridge
        except Exception as e:
            LOGGER.error('Exception : ' + to_str(e) + ' on ' + self.hostname)
            print 'Exception : ' + to_str(e) + ' on ' + self.hostname
            traceback.print_exc()
        return None

    def get_cpu_info(self):
        try:
            cpu_info = self.environ['cpu_info']
            if cpu_info is None:
                return {}
            return cpu_info
            print '\n\n\n\ncpu_info======',
            print cpu_info
        except Exception as e:
            LOGGER.error('Exception : ' + to_str(e) + ' on ' + self.hostname)
            print 'Exception : ' + to_str(e) + ' on ' + self.hostname
            traceback.print_exc()
        return {}

    def get_cores(self):
        try:
            import stackone.core.utils.utils
            constants = stackone.core.utils.constants
            sockets = self.socket
            cpu_info = self.get_cpu_info()
            cpus = int(cpu_info.get(constants.key_cpu_count, 1L))
            print 'CPUSSSS,  SOCKETSSS',
            print cpus,
            print sockets
            return cpus * sockets
        except Exception as ex:
            LOGGER.error(to_str(ex))
            traceback.print_exc()

    def get_disk_info(self):
        try:
            disk_info = self.environ['disk_info']
            if disk_info is None:
                return []
            return disk_info
        except Exception as e:
            LOGGER.error('Exception : ' + to_str(e) + ' on ' + self.hostname)
            print 'Exception : ' + to_str(e) + ' on ' + self.hostname
            traceback.print_exc()
        return []

    def get_free_mem(self, memory_total=None):
        free_mem = None
        from stackone.model.Metrics import MetricServerCurr
        currMetricsData = DBSession.query(MetricServerCurr).filter(MetricServerCurr.entity_id == self.id).filter(MetricServerCurr.metric_type == SERVER_CURR).first()
        if currMetricsData is not None:
            if memory_total is None:
                memory_total = currMetricsData.server_mem
            if memory_total is None:
                return 0L
            memory_total = int(memory_total)
            used_mem = currMetricsData.host_mem * memory_total / 100L
            free_mem = round(memory_total - used_mem)
            free_mem = '%d' % free_mem
        return free_mem

    def get_memory_info(self):
        try:
            memory_info = self.environ['memory_info']
            if memory_info is None:
                return {}
            free_mem = self.get_free_mem(memory_info[key_memory_total])
            if free_mem is not None:
                memory_info[key_memory_free] = free_mem
            return memory_info
        except Exception as e:
            LOGGER.error('Exception : ' + to_str(e) + ' on ' + self.hostname)
            print 'Exception : ' + to_str(e) + ' on ' + self.hostname
            traceback.print_exc()
        return {}

    def get_os_info_display_names(self):
        display_dict = {key_os_release: display_os_release, key_os_machine: display_os_machine, key_os_distro_string: display_os_distro}
        return display_dict

    def get_network_info_display_names(self):
        display_dict = {key_network_interface_name: display_network_interface_name, key_network_ip: display_network_ip}
        return display_dict

    def get_cpu_info_display_names(self):
        display_dict = {key_cpu_count: display_cpu_count, key_cpu_vendor_id: display_cpu_vendor_id, key_cpu_model_name: display_cpu_model_name, key_cpu_mhz: display_cpu_mhz}
        return display_dict

    def get_memory_info_display_names(self):
        display_dict = {key_memory_total: display_memory_total, key_memory_free: display_memory_free}
        return display_dict

    def get_disk_info_display_names(self):
        display_dict = {key_disk_file_system: display_disk_file_system, key_disk_size: display_disk_size, key_disk_mounted: display_disk_mounted}
        return display_dict
    #pass
    def get_cpu_db(self):
        try:
            instance = DBSession.query(Instance).filter(Instance.node_id == self.id).filter(Instance.name == constants.key_cpu_count).first()
            if instance:
                return int(instance.value)
        except Exception as e:
            print 'Exception: ',
            print e
        return 1L
    #pass
    def get_mem_db(self):
        try:
            instance = DBSession.query(Instance).filter(Instance.node_id == self.id).filter(Instance.name == constants.key_memory_total).first()
            if instance:
                return int(instance.value)
        except Exception as e:
            print 'Exception: ',
            print e
        return 0L
##################
    def _init_node_proxy(self):
        self._node_proxy_lock.acquire()
        try:
            if self._node_proxy is None:
                while True:
                    creds = None
                    try:
                        credentials=self.get_credentials()
                        proxy_class = self.get_node_proxy_class()
                        ssh_port = 22
                        if credentials['ssh_port']:
                            ssh_port=int(credentials['ssh_port'])
                            
                        self._node_proxy = NodePool.get_node(external_manager=self.get_external_manager(), proxy_class=proxy_class, hostname=self.hostname, ssh_port=ssh_port, username=credentials['username'], password=credentials['password'], isRemote=self.isRemote, use_keys=credentials['use_keys'])
                        
                    except AuthenticationException, e:
                        creds = None
                        if self.helper and not use_keys:
                            creds = self.helper.get_credentials(self.hostname,
                                                                self.username)
                            if creds is None:
                                raise Exception("Server not Authenticated")
                            else:
                                self.username = creds.username
                                self.password = creds.password
                        else:
                            raise e
                    else:
                        break
        finally:
            self._node_proxy_lock.release()
        return self._node_proxy


    def clear_node_proxy(self):
        try:
            credentials = self.get_credentials()
            self._node_proxy = NodePool.clear_node(hostname=self.hostname, ssh_port=credentials['ssh_port'], username=credentials['username'], password=credentials['password'], isRemote=self.isRemote, use_keys=credentials['use_keys'])
        except Exception as e:
            print e

    def _init_config(self):
        if self.setup_config is None:
            self.setup_config = NodeConfiguration(self)
        return self.setup_config

    def _init_lvm_proxy(self):
        if self._lvm_proxy is None and self.isLVMEnabled:
            self._lvm_proxy = LVMProxy(self.node_proxy, self.exec_path)
        return self._lvm_proxy

    def _init_isLVMEnabled(self):
        if self._isLVMEnabled is None:
            conf_val = self.config.get(prop_lvm)
            if conf_val is None:
                self._isLVMEnabled = LVMProxy.isLVMEnabled(self.node_proxy, self.exec_path)
                self.config.set(prop_lvm, self._isLVMEnabled)
            else:
                self._isLVMEnabled = eval(to_str(conf_val))
        return self._isLVMEnabled

    def _init_environ(self):
        if self._environ is None:
            self._environ = self.getEnvHelper()
        return self._environ

    def getEnvHelper(self):
        return NodeEnvHelper(self.id, None)

    def refresh_environ(self):
        try:
            DBHelper().delete_all(Instance, [], [Instance.node_id == self.id])
            self._init_environ()
        except Exception as e:
            traceback.print_exc()
            raise e

    def remove_environ(self):
        DBHelper().delete_all(Instance, [], [Instance.node_id == self.id])

    def _init_exec_path(self):
        if self._exec_path is None:
            self._exec_path = self.config.get(prop_exec_path)
        return self._exec_path

    def get_boot_time(self):
        import tg
        boot_time = tg.config.get('server_boot_time')
        if boot_time is None:
            boot_time = 120L
        else:
            boot_time = int(boot_time)
        return boot_time

    #get_status = classmethod()
    def get_socket_info(self):
        self.socket = self.environ.get_socket_info()
        return self.socket

    #get_up_nodes = classmethod()
    def is_power_fencing_device_configured(self):
        from stackone.core.ha.ha_fence import HAEntityResource, HAFenceResource, HAFenceResourceType
        try:
            print '\n -----is_power_fencing_device_configured------'
            resources = DBSession.query(HAEntityResource).join(HAFenceResource).join(HAFenceResourceType).filter(HAEntityResource.entity_id == self.id).filter(HAFenceResourceType.classification == u'Power Fencing Device').all()
            print '\n resources----------',
            print resources
            if resources:
                return True
            return False
        except Exception as ex:
            LOGGER.error(to_str(ex))
            traceback.print_exc()
            raise ex

    def wait_for_nw_str_sync(self, auth):
        result = self.network_sync(auth)
        result = self.storage_sync(auth)
        return result

    def network_sync(self, auth, logger=None):
        return self.sync_task(auth, constants.NETWORK, logger)

    def storage_sync(self, auth, logger=None):
        return self.sync_task(auth, constants.STORAGE, logger)
####################
    def sync_task(self, auth, type, logger=None):
        from sqlalchemy.orm import eagerload
        from stackone.model.services import Task
        from stackone.viewModel.TaskCreator import TaskCreator
        tc = TaskCreator()
        boot_time = self.get_boot_time()
        msg = {Task.STARTED:' is not completed in '+str(boot_time)+ 'seconds',\
            Task.FAILED:' failed.',Task.CANCELED:' canceled.',Task.SUCCEEDED:' succeeded.',\
            }
        if not logger:
            logger = LOGGER

        result_flags = {}
        logger.info('Submitting ' + str(type) + ' Sync task for ' + self.hostname)
        nw_task = tc.server_sync_task(auth,self.id,type,True)
        task_ids = [nw_task]
        result_flags['flag'+str(nw_task)] = Task.STARTED
        
        result = False
        for i in range(0, boot_time):
            time.sleep(3)
            transaction.begin()
            tasks = DBSession.query(Task).filter(Task.task_id.in_(task_ids)).options(eagerload('result')).all()
            for task in tasks:
                if task.is_finished():
                    result_flags['flag'+str(task.task_id)] = task.result[0].status
                    if task.result[0].status == Task.SUCCEEDED:
                        result = True
                    task_ids.remove(task.task_id)
            if len(task_ids) == 0:
                transaction.commit()
                break
            transaction.commit()
        nw_msg = str(type) + ' syncing task(id:' + str(nw_task) + ') for ' + self.hostname + msg[result_flags['flag'+ str(nw_task)]]
        logger.info(nw_msg)
        return result
    def get_unused_port(self, start, end):
        used_ports = self.get_used_ports()
        nc = NodeCache()
        selected_port = nc.get_port(self.hostname, constants.PORTS, used_ports, start, end)
        return selected_port

    def get_used_ports(self):
        used_ports = []
        ports = self.netstat_local_ports()
        if ports:
            used_ports = ports
        return used_ports
#################
    def netstat_local_ports(self):
        """Run netstat to get a list of the local ports in use.
        """
        netstat_cmd = "netstat -nat"
        out, exit_code = self.node_proxy.exec_cmd(netstat_cmd, timeout=60)
        if exit_code != 0:
            raise Exception("Error finding the used ports. "+out)

        lines = out.split('\n')
        port_list = []
        for x in lines[2:]:
            if not x:
                continue
            y = x.split()[3]
            y = y.split(':')[-1]
            port_list.append(int(y))
        return port_list


    def is_maintenance(self):
        return self.maintenance
    #pass
    def get_external_manager(self):
        pass
    #pass
    def get_config_contents(self, filename):
        f = self.node_proxy.open(filename)
        lines = f.readlines()
        contents = '\n'.join(lines)
        f.close()
        return contents
    #pass
    def is_script_execution_supported(self):
        return True

    def get_vm_invalid_chars(self):
        return self.VM_INVALID_CHARS
    #pass
    def get_vm_invalid_chars_exp(self):
        return self.VM_INVALID_CHARS_EXP
    #pass
    def get_vnc_info(self, dom, address):
        from stackone.model.LicenseManager import check_platform_expire_date
        ret,msg = check_platform_expire_date(self.get_platform())
        if ret == False:
            raise Exception(msg)
        return self._get_vnc_info(dom, address)

    def _get_vnc_info(self, dom, address):
        from stackone.config.ConfigSettings import ClientConfiguration
        credentials = self.get_credentials()
        result = {}
        hostname = self.address
        host_ssh_port = credentials['ssh_port']
        vnc_node = None
        if hostname is None:
            hostname = self.hostname
        client_config = ClientConfiguration()
        vnchost = client_config.get(constants.prop_vnc_host)
        vncport = client_config.get(constants.prop_vnc_port)
        vncuser = client_config.get(constants.prop_vnc_user)
        vncpwd = client_config.get(constants.prop_vnc_password)
        if not vnchost or not vncport or not vncuser or vncport.find(':') == -1L:
            raise Exception('VNC Host,Port & User should be configured properly.')
        start,end = vncport.split(':')
        if not start or not end:
            raise Exception('VNC Port should be configured properly.' + '(start:end)')
        result['hostname'] = address
        result['port'] = '00'
        result['server'] = self.hostname
        result['server_ssh_port'] = self.ssh_port
        result['vnc_display'] = '00'
        result['height'] = dom.get_attribute_value(constants.VNC_APPLET_HEIGHT, tg.config.get(constants.VNC_APPLET_HEIGHT))
        result['width'] = dom.get_attribute_value(constants.VNC_APPLET_WIDTH, tg.config.get(constants.VNC_APPLET_WIDTH))
        result['new_window'] = dom.get_attribute_value(constants.VNC_APPLET_PARAM_OPEN_NEW_WINDOW, tg.config.get(constants.VNC_APPLET_PARAM_OPEN_NEW_WINDOW))
        result['show_control'] = dom.get_attribute_value(constants.VNC_APPLET_PARAM_SHOW_CONTROL, tg.config.get(constants.VNC_APPLET_PARAM_SHOW_CONTROL))
        result['encoding'] = dom.get_attribute_value(constants.VNC_APPLET_PARAM_ENCODING, tg.config.get(constants.VNC_APPLET_PARAM_ENCODING))
        result['restricted_colours'] = dom.get_attribute_value(constants.VNC_APPLET_PARAM_RESTRICTED_COLOURS, tg.config.get(constants.VNC_APPLET_PARAM_RESTRICTED_COLOURS))
        result['offer_relogin'] = dom.get_attribute_value(constants.VNC_APPLET_PARAM_OFFER_RELOGIN, tg.config.get(constants.VNC_APPLET_PARAM_OFFER_RELOGIN))
        domm = self.get_dom(dom.id)
        if not domm.is_resident():
            return result
        if dom.is_graphical_console():
            vnc_port = dom.get_vnc_port()
            if vnc_port:
                vnc_display = 5900L + int(vnc_port)
                list = []
                if len(list) > 0L:
                    vnc_node = list[0L]
                else:
                    vnc_node = create_node(vnchost, vncuser, vncpwd)
                if vnc_node is None:
                    raise Exception('Can not connect to VNC Host, ' + vnchost + '.')
                try:
                    start = int(start)
                    end = int(end)
                except Exception as e:
                    print 'Exception: ',
                    print e
                    raise Exception('Port Numbers should be valid numbers.')
                try:
                    forward_port = vnc_node.get_unused_port(start, end)
                except Exception as e:
                    LOGGER.error(to_str(e))
                    traceback.print_exc()
                    raise e
                if forward_port is None:
                    raise Exception('No ports are free in the given range.' + '(' + str(start) + ':' + str(end) + ')')
                cmd,temp_file = get_port_forward_cmd(forward_port, vncuser, hostname, host_ssh_port, vnc_display, dom)
                # as temp_file
                print forward_port,
                print vncuser,
                print hostname,
                print vnc_display
                print cmd
                print '--Managednode----_get_vnc_info----forward_cmd--',
                print cmd
                output,exit_code = vnc_node.node_proxy.exec_cmd(cmd, timeout=None)
                # as exit_code
                if exit_code == 1L:
                    raise Exception('Error forwarding the vnc display to VNC Host. ' + output)
                if vnchost == 'localhost':
                    vnchost = address
                result['hostname'] = vnchost
                result['port'] = forward_port
                result['server'] = self.hostname
                result['vnc_display'] = vnc_display
                result['temp_file'] = temp_file
            else:
                raise Exception('VNC is not enabled for this VM.')
        else:
            raise Exception('VNC is not enabled for this VM.')
        return result
    #pass
    def get_console_local_viewers(self):
        local_viewers = {'tightvnc': constants.TIGHTVNC, 'vncviewer': constants.VNC}
        return local_viewers
    #pass
    def get_console_local_viewer_param_dict(self, cmd, info):
        value_map = {}
        if cmd in [constants.VNC, constants.TIGHTVNC]:
            value_map[constants.APPLET_IP] = info['hostname']
            value_map[constants.PORT] = info['port']
        return value_map
    #pass
    def get_external_id(self):
        return None
    #pass
    def get_view_console_ip(self):
        return None


Index('mnode_hn', ManagedNode.hostname)
class NodeEnvHelper():
    def __init__(self, node_id, node_proxy):
        self.node_proxy = node_proxy
        self.node_id = node_id
        self._NodeEnvHelper__dict = {}
        self._NodeEnvHelper__populateInformation()

    def __iter__(self):
        return self._NodeEnvHelper__dict.iterkeys()

    def keys(self):
        return self._NodeEnvHelper__dict.keys()

    def __getitem__(self, item):
        if not item:
            return None
        if self._NodeEnvHelper__dict.has_key(item):
            return self._NodeEnvHelper__dict[item]
        return None

    def __setitem__(self, item, value):
        self._NodeEnvHelper__dict[item] = value

    def refresh(self):
        DBHelper().delete_all(Instance, [], [Instance.node_id == self.node_id])
        self._NodeEnvHelper__dict = None
        self._NodeEnvHelper__populateDictionary()
        return None

    def get_socket_info(self):
        try:
            cmd = 'cat /proc/cpuinfo | grep "physical id"  | sort | uniq -c | wc -l'
            output,exit_code = self.node_proxy.exec_cmd(cmd)
            # as exit_code
            if output and not exit_code:
                sock = int(output)
                if sock == 0L:
                    sock = 1L
                return sock
        except Exception as e:
            LOGGER.error(to_str(e))
            traceback.print_exc()
        LOGGER.error('Unable to get Socket info. output:' + to_str(output) + 'exit_code:' + to_str(exit_code))
        raise Exception('Unable to get Socket info. output:' + to_str(output) + 'exit_code:' + to_str(exit_code))
###################
    def populate_network(self, n):
        if n.get("ip") and n.get("netmask"):
            try:
                ip = IP(n.get('ip'))
                mask = IP(n.get('netmask'))
                net_int = ip.int() & mask.int()
                net_ip = IP(net_int)
                net_ip_mask = IP(net_ip.strNormal() + '/' + mask.strNormal())
                net_str = net_ip_mask.strNormal()
                n['network'] = net_str
            except Exception as ex:
                pass

####################
    def _NodeEnvHelper__populateInformation(self):
        instances = DBHelper().filterby(Instance, [], [Instance.node_id == self.node_id])
        if len(instances) == 0:
            self._NodeEnvHelper__populateDictionary()
        else:
            for instance in instances:
                comp = instance.component
                if comp.type in ('cpu_info', 'memory_info', 'os_info', 'nic_info', 'bridge_info', 'platform_info'):
                    if not self._NodeEnvHelper__dict.has_key(comp.type):
                        self._NodeEnvHelper__dict[comp.type] = {}
            
                    val = instance.value
                    if val[0] in ('{', '['):
                        val = eval(instance.value)
                    self._NodeEnvHelper__dict[comp.type][instance.name] = val
                    continue
                if comp.type in ('disk_info',):
                    self._NodeEnvHelper__dict[comp.type] = eval(instance.value)
                    continue
                if comp.type in ('network_info',):
                    if not self._NodeEnvHelper__dict.has_key(comp.type):
                        self._NodeEnvHelper__dict[comp.type] = []
                    self._NodeEnvHelper__dict[comp.type].append(dict(interface_name=instance.name, ip_address=instance.value))
                    continue
    
                if comp.type in ('default_bridge',):
                    self._NodeEnvHelper__dict[comp.type] = instance.value
                    continue

################
    def _NodeEnvHelper__populateDictionary(self):
        """ retrieve environment information for the
        node and store it in the local dictionary. """

        if self._NodeEnvHelper__dict is not None:
            self._NodeEnvHelper__dict = None

        m_node=DBSession.query(ManagedNode).filter(ManagedNode.id==self.node_id).one()
        self.node_proxy=m_node.node_proxy

        cpu_attributes = [key_cpu_count,key_cpu_vendor_id,key_cpu_model_name, key_cpu_mhz]
        memory_attributes = [key_memory_total,key_memory_free]
        #disk_attributes = [key_disk_file_system,key_disk_size,key_disk_mounted]
        disk_attributes = [key_disk_file_system, key_disk_size, key_disk_mounted]
        cpu_values = self.node_proxy.exec_cmd( \
                'cat /proc/cpuinfo | grep "processor" | wc -l;' +
                'cat /proc/cpuinfo | grep "vendor*" | head -1 | cut -d\':\' -f2;' +
                'cat /proc/cpuinfo | grep "model na*" | head -1 | cut -d\':\' -f2;' +
                'cat /proc/cpuinfo | grep "cpu MHz*" | head -1 | cut -d\':\' -f2;'\
                )[0].split('\n')[:-1]

        memory_values = self.populate_mem_info()
        network_values = self.node_proxy.exec_cmd( \
               'ifconfig | awk \'{print $1, $2, $3, $4}\' ;'
               )[0].split("\n   \n")

        # Process networks # TODO : rewrite this.
        raw_network_list = network_values
        network_list = []
        if raw_network_list[0].find('not found') == -1:
            for i in range(len(raw_network_list)):
                split_item = raw_network_list[i].split("UP")
                if cmp('',split_item[0]) !=0 :
                    split_item = split_item[0].split('\n')
                    interface_name = split_item[0].split()[0]
                    ip_addr = ''
                    if cmp('',split_item[1]) !=0:
                        for i in range(1, len(split_item)):
                            ip_addr += split_item[i] + '\n'
                    network_list.append(dict([(key_network_interface_name, interface_name), (key_network_ip, ip_addr)]))


        disk_values = self.node_proxy.exec_cmd( \
                'df -kh -P | grep ^/dev | awk \'{print $1, $2, $6}\''\
                )[0].split('\n')[:-1]
        #remove ''
        ################tianfeng
        disk_values = [v for v in disk_values if len(v) > 0]
        
        cpu_dict = dict((cpu_attributes[x],cpu_values[x]) \
                           for x in range(len(cpu_attributes)))
        ##################
        cpu_dict[key_cpu_count] = int(cpu_dict[key_cpu_count])
        memory_dict = dict((memory_attributes[x],memory_values[x]) \
                           for x in range(len(memory_attributes)))

        disk_list = []
        for i in range(len(disk_values)):
            disk_values_split =disk_values[i].split(" ")
            if len(disk_values_split)==len(disk_attributes):
                disk_list.append(dict((disk_attributes[x],disk_values_split[x]) \
                for x in range(len(disk_values_split))))
        print '>>>>>>>>>>',disk_list 

        # os details
        os_values = self.node_proxy.exec_cmd( \
            'uname -r;uname -s; uname -m;'\
                )[0].split('\n')[:-1]
        i = 0
        os_dict = {}
        for name in [key_os_release,key_os_system,key_os_machine]:
            try:
                os_dict[name] = os_values[i]
            except ValueError:
                pass
            i = i+1

        # Augment the information gathered from setup script.
        discovery_file = '/var/cache/stackone/server_info'
        alt_discovery_file = '/var/cache/stackone/server_info'
        if not self.node_proxy.file_exists(discovery_file):
            if self.node_proxy.file_exists(alt_discovery_file):
                discovery_file = alt_discovery_file

        discovered_info = None
        if self.node_proxy.file_exists(discovery_file):
            discovered_info = PyConfig(m_node, discovery_file)
        
        def_bridge = ""
        if discovered_info:
            os_dict[key_os_distro] = discovered_info["DISTRO"]
            os_dict[key_os_distro_ver] = discovered_info["VER"]
            os_dict[key_os_distro_string] = discovered_info["DISTRO"] + " " + \
                discovered_info["VER"]
            def_bridge = discovered_info["DEFAULT_BRIDGE"]


        # Add some more network specific info.
        cmd = "ls -ld /sys/class/net/*/device | sed -e 's/.*\/sys\/class\/net\///' -e 's/\/device.*//'"
    
        nics = {}
        (output,exit_code) = self.node_proxy.exec_cmd(cmd)
        if output and not exit_code:
            nic_list = output.split('\n')
            for nic in nic_list:
                if nic:
                    nics[nic] = { "name":nic }
        ###tianfeng
        bridges = {}
        cmd = "ls -ld /sys/class/net/*/{bridge,brif/*} | sed -e 's/.*\/sys\/class\/net\///' -e 's/\/bridge.*//' -e 's/\->.*//'"
        (output,exit_code) = self.node_proxy.exec_cmd( cmd)
        if output and not exit_code:
            base_entries = output.split('\n')
            entries=[]
            for e in base_entries:
                if e and e.find('cannot access') < 0:
                    if e and e.find('ls:') != 0:
                        entries.append(e)
            # Populate bridges
            for e in entries:
                if e and e.find("/brif/") == -1:
                    bridges[e] = { "name":e }
            # Populate interfaces for bridges.
            for e in entries:
                if e.find("/brif/") > -1:
                    (br_name,brif,ifname) = e.split("/")
                    if ifname:
                        ifname = ifname.strip()
                    if ifname and (ifname.find("vif") == 0 or \
                            ifname.find("tap")==0):
                        # ignore virtual interface conventions.
                        continue
                    try:
                        bridge = bridges[br_name]
                        if bridge :
                            interfaces = bridge.get("interfaces")
                            if interfaces is not None:
                                interfaces.append(ifname)
                            else:
                                bridge["interfaces"] = [ifname,]
                    except Exception,ex:
                        print ex
        # from the network info, get ip address and netmask and 
        # construct net details from it.
        # NOTE : There must be a better way of doing this.
        # Look in to ioctl 
        ipv4_re = re.compile("(.*):(.*) (.*):(.*)")
        ipv4_re1 = re.compile("(.*):(.*) (.*):(.*) (.*):(.*)")
        for n_info in network_list:
            ifname = n_info[key_network_interface_name]
            b = bridges.get(ifname)
            n = nics.get(ifname)
            if b or n:
                # we need to process
                ip_info = n_info[key_network_ip]
                if ip_info:
                    ip_list = ip_info.split('\n')
                    for ip_entry in ip_list:
                        m = ipv4_re.match(ip_entry)
                        if not m:
                            ipv4_re1.match(ip_entry)
                        if m :
                            l = len(m.groups())
                            if l > 0 and  m.group(1).find("inet addr") == 0:
                                if b: b["ip"] = m.group(2)
                                if n: n["ip"] = m.group(2)
                            if l > 2 and m.group(3).find("Mask") == 0:
                                if b: b["netmask"] = m.group(4)
                                if n: n["netmask"] = m.group(4)
                            if l > 4 and m.group(5).find("Mask") == 0:
                                if b: b["netmask"] = m.group(6)
                                if n: n["netmask"] = m.group(6)
                                
                                
        # find the network by using ip and netmask
        for n in nics.itervalues():
            self.populate_network(n)
        for b in bridges.itervalues():
            self.populate_network(b)

        platform_dict = self.populate_platform_info()

        if platform_dict is None:
            raise Exception("Cannot get server platform")

        #import pprint; pprint.pprint(bridges)
        self._NodeEnvHelper__dict = dict([('cpu_info',cpu_dict),
                            ('memory_info', memory_dict),
                            ('disk_info', disk_list),
                            ('network_info',network_list),
                            ('nic_info',nics),
                            ('bridge_info',bridges),
                            ('os_info', os_dict),
                            ('default_bridge', def_bridge),
                            ('platform_info', platform_dict)])
        comp_dict={}
        components=DBHelper().get_all(Component)
        for component in components:
            comp_dict[component.type]=component
        instances=[]
        for key,val in self._NodeEnvHelper__dict.iteritems():
            #val is of dictionary type
            if key in ['cpu_info','memory_info','os_info','nic_info','bridge_info','platform_info']:
                for k1,v1 in val.iteritems():
                    inst=Instance(to_unicode(k1))
                    inst.value=to_unicode(v1)
                    inst.display_name=to_unicode('')
                    inst.component=comp_dict[key]
                    inst.node_id=self.node_id
                    instances.append(inst)
            #val is of list type
            elif key in ['disk_info']:
                inst=Instance(to_unicode('disks'))
                inst.value=to_unicode(val)
                inst.display_name=to_unicode('')
                inst.component=comp_dict[key]
                inst.node_id=self.node_id
                instances.append(inst)
            elif key in ['network_info']:
                for i in range(len(val)):
                    k1,v1=val[i]
                    inst=Instance(to_unicode(val[i][k1]))
                    inst.value=to_unicode(val[i][v1])
                    inst.display_name=to_unicode('')
                    inst.component=comp_dict[key]
                    inst.node_id=self.node_id
                    instances.append(inst)
            #val is of string type
            elif key in ['default_bridge']:
                inst=Instance(to_unicode(key))
                inst.value=to_unicode(val)
                inst.display_name=to_unicode('')
                inst.component=comp_dict[key]
                inst.node_id=self.node_id
                instances.append(inst)

        DBHelper().add_all(instances)

##############
    def populate_mem_info(self):
        memory_values = self.node_proxy.exec_cmd('cat /proc/meminfo | grep "Mem*" | cut -d\':\' -f2')[0].split('\n')[:-1]
        memory_values = [ int(re.search('(\d+)(\s+)(\S+)', v.strip()).group(1))/ 1000 \
                          for v in memory_values ]
        return memory_values


    def populate_platform_info(self):
        m_node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.node_id).one()
        return m_node.populate_platform_info()


