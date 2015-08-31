import sys
import os
import re
import types
import traceback
import urllib2
import suds
import pprint
from stackone.core.utils.utils import constants, search_tree, Poller
from stackone.core.utils.utils import to_unicode, to_str, dynamic_map, convert_byte_to
from stackone.model.ManagedNode import ManagedNode
from stackone.model.vCenter import VCenter
from stackone.model.VM import VM
from stackone.model.VNode import VNode
from VMWDomain import *
from VMWVMM import VMWVMM
from VMWConstants import *
from exception import VCenterDownError
from stackone.core.utils.phelper import PHelper
from stackone.core.utils.phelper import HostValidationException, AuthenticationException, CommunicationException
from sqlalchemy import Column
from sqlalchemy.types import *
from sqlalchemy import orm
from stackone.model.DBHelper import DBHelper
from stackone.model.NodeInformation import Category, Component, Instance
from stackone.core.utils.constants import *
import suds
import suds.sax.text
from suds.sax.text import Text
import logging
LOGGER = logging.getLogger('stackone.core.platforms.vmw')
class VMWNode(VNode):
    STATE_MAP = {constants.VMW_UP: [VNode.UP, u'Host UP.'], constants.VMW_DOWN: [VNode.DOWN, u'Host Down.']}
    VM_INVALID_CHARS = '(comma,quotes,/,\\|,<,>,!,&,%,.,^)'
    VM_INVALID_CHARS_EXP = '(|/|,|<|>|\\||\\!|\\&|\\%||\'|"|\\^|\\\\)'
    __mapper_args__ = {'polymorphic_identity': u'vmw'}
    def __init__(self, hostname=None, username=Node.DEFAULT_USER, password=None, isRemote=False, ssh_port=22, migration_port=8002, helper=None, use_keys=False, address=None, external_manager_id=None):
        VNode.__init__(self, to_unicode('vmw'), hostname, username, password, isRemote, ssh_port, helper, use_keys, address)
        self.external_manager_id = external_manager_id
        self.migration_port = migration_port

    def push_bash_timeout_script(self):
        pass
    @orm.reconstructor
    def init_on_load(self):
        VNode.init_on_load(self)
    def get_auto_config_dir(self):
        return '/etc/vmw/auto'

    def is_HVM(self):
        return True

    def is_image_compatible(self, image):
        if image:
            return image.is_hvm()
        return False

    def is_dom_compatible(self, dom):
        if dom:
            return self.get_platform() == dom.get_platform()
        return False

    def new_config(self, filename, config=None):
        return VMWConfig(self, filename)

    def new_vm_from_config(self, config):
        return VMWDomain(self, config=config)

    def new_vm_from_info(self, info):
        return VMWDomain(self, vm_info=info)

    def get_running_vms(self):
        current_dict = {}
        vm_info_list = self.get_vmm().get_vms()
        for k,vm_info in vm_info_list.iteritems():
            vm = self.new_vm_from_info(vm_info)
            current_dict[k] = vm
        return current_dict

    def _init_vmm(self):
        return VMWVMM(self)

    def translate_state(self, vm_mo_state):
        if vm_mo_state == 'poweredOn':
            return VM.RUNNING
        if vm_mo_state == 'poweredOff':
            return VM.SHUTDOWN
        if vm_mo_state == 'suspended':
            return VM.PAUSED
        raise Exception('FIXME: TBI : Not translating VM state %s' % vm_mo_state)

    def get_metric_snapshot(self, filter=False):
        frame = {}
        frame['RUNNING_VMs'] = 0
        frame['PAUSED_VMs'] = 0
        frame['CRASHED_VMs'] = 0
        frame['TOTAL_VMs'] = 0
        frame['VM_TOTAL_CPU'] = 0.0
        frame['VM_TOTAL_MEM'] = 0.0
        frame['VM_TOTAL_CPU(%)'] = 0.0
        frame['VM_TOTAL_MEM(%)'] = 0.0
        dom_names,vm_dict = self.get_all_dom_names()
        frame['TOTAL_VMs'] = len(dom_names)
        mem_info = self.get_memory_info()
        total_mem = int(mem_info.get('total_memory', 0))
        cpu_info = self.get_cpu_info()
        num_cpu_cores = self.get_cores()
        nr_cpus = int(cpu_info.get(key_cpu_count, 1))
        cpu_mhz = int(cpu_info.get(key_cpu_mhz, 0))
        quick_stats_summary = self.node_proxy.get_quick_stats_summary()
        try:
            overall_cpu_usage = int(quick_stats_summary.overallCpuUsage)
            overall_memory_usage = int(quick_stats_summary.overallMemoryUsage)
        except AttributeError as ex:
            overall_cpu_usage = 0
            overall_memory_usage = 0
            msg = 'ERROR: %s' % ex
            print msg
            LOGGER.error(msg)
        total_cpu = overall_cpu_usage / float(num_cpu_cores * cpu_mhz) * 100
        host_mem = overall_memory_usage / float(total_mem) * 100
        outside_vms = []
        for v in self.node_proxy.get_vm_list():
            d_frame = {}
            vm_info = self.get_vmm().refresh(v)
            state = self.translate_state(vm_info.state)
            if vm_info.name not in dom_names:
                outside_vms.append(dict(name=vm_info.name, status=state))
                continue
            vm_overall_cpu_usage = int(vm_info.overall_cpu_usage)
            vm_overall_memory_usage = int(vm_info.guest_memory_usage)
            vm_memory = int(vm_info.memory)
            vm_num_vcpus = int(vm_info.vcpus)
            cpu_pct = vm_info.overall_cpu_usage / vm_num_vcpus * 100
            mem_pct = vm_overall_memory_usage / vm_memory * 100
            d_frame['CPU(%)'] = cpu_pct
            d_frame['MEM(%)'] = mem_pct
            d_frame['NAME'] = vm_info.name
            d_frame['STATE'] = state
            dom = vm_dict[d_frame['NAME']]
            d_frame['CLOUD_VM_ID'] = dom.cloud_vm_id
            if dom.status == constants.PAUSED:
                d_frame['STATE'] = VM.PAUSED
                frame['PAUSED_VMs'] += 1
            else:
                frame['RUNNING_VMs'] += 1
            vcpus = float(dom.getVCPUs())
            d_frame['VM_CPU(%)'] = d_frame['CPU(%)']
            if vcpus > 1:
                d_frame['VM_CPU(%)'] = to_str(float(d_frame['CPU(%)']) / vcpus)
            if nr_cpus > 1:
                d_frame['CPU(%)'] = to_str(float(d_frame['CPU(%)']) / nr_cpus)
            d_frame['NETRX(k)'] = 0
            d_frame['NETS'] = 0
            d_frame['NETTX(k)'] = 0
            d_frame['VBDS'] = 0
            d_frame['VBD_OO'] = 0
            d_frame['VBD_RD'] = 0
            d_frame['VBD_WR'] = 0
            frame['VM_TOTAL_CPU'] += cpu_pct
            frame['VM_TOTAL_MEM'] += mem_pct * total_mem / 100
            frame['VM_TOTAL_CPU(%)'] += float(d_frame['CPU(%)'])
            frame['VM_TOTAL_MEM(%)'] += mem_pct
            frame[d_frame['NAME']] = d_frame
        if filter:
            self.insert_outside_vms(outside_vms)
        cpu_str = to_str(cpu_info.get(key_cpu_count, 1)) + ' @ ' + to_str(cpu_info.get(key_cpu_mhz, 0)) + 'MHz'
        frame['SERVER_CPUs'] = cpu_str
        frame['SERVER_MEM'] = to_str(self.get_memory_info().get(key_memory_total, 0)) + 'M'
        frame['HOST_MEM(%)'] = host_mem
        frame['HOST_CPU(%)'] = total_cpu
        info = self.get_platform_info()
        if info and info.get(key_version):
            frame['VER'] = info[key_version]
        return frame

    def get_platform_info_display_names(self):
        return {key_version: display_version}

    def migrate_dom(self, name, dest_node, live):
        raise Exception('Not implemented')

    def getEnvHelper(self):
        print 'AAA about to initialize node helper',
        print self.hostname
        n_h = VMWNodeEnvHelper(self.id, self.node_proxy)
        print 'AAA Initialized initialize node helper',
        print self.hostname
        return n_h

    def get_os_info_display_names(self):
        display_dict = {key_os_release: display_os_release, key_os_machine: display_os_machine, key_os_distro_string: display_os_distro}
        return display_dict

    def get_network_info_display_names(self):
        if True:
            return {}
        display_dict = {key_network_interface_name: display_network_interface_name, key_network_ip: display_network_ip}
        return display_dict

    def get_cpu_info_display_names(self):
        display_dict = {key_cpu_count: display_cpu_count, key_cpu_vendor_id: display_cpu_vendor_id, key_cpu_model_name: display_cpu_model_name, key_cpu_mhz: display_cpu_mhz}
        return display_dict

    def get_memory_info_display_names(self):
        display_dict = {key_memory_total: display_memory_total, key_memory_free: display_memory_free}
        return display_dict

    def get_disk_info_display_names(self):
        if True:
            return {}
        display_dict = {key_disk_file_system: display_disk_file_system, key_disk_size: display_disk_size, key_disk_mounted: display_disk_mounted}
        return display_dict

    def get_virtual_networks_info(self):
        try:
            virt_nw_info = self.environ['virt_nw_info']
            if virt_nw_info is None:
                return {}
            return virt_nw_info
        except Exception as e:
            LOGGER.error('Exception : ' + to_str(e) + ' on ' + self.hostname)
            print 'Exception : ' + to_str(e) + ' on ' + self.hostname
            traceback.print_exc()
        return {}

    def get_storage_resources_info(self):
        try:
            storage_info = self.environ['storage_info']
            if storage_info is None:
                return {}
            return storage_info
        except Exception as e:
            LOGGER.error('Exception : ' + to_str(e) + ' on ' + self.hostname)
            print 'Exception : ' + to_str(e) + ' on ' + self.hostname
            traceback.print_exc()
        return {}

    def get_cores(self):
        cores = self.node_proxy.get_hardware_summary().numCpuCores
        print 'ESXi : get cores ',
        print cores,
        print self.hostname
        return cores

    def get_node_proxy_class(self):
        from stackone.core.platforms.vmw.ESXiProxy import ESXiNode, vESXiNode
        credentials = self.get_credentials()
        if credentials['use_keys']:
            return vESXiNode
        return ESXiNode

    def process_paths(self, paths):
        vm_list = self.node_proxy.get_vm_list()
        paths = []
        for vm_name in vm_list:
            paths.append('%s/%s.vmx' % (vm_name, vm_name))
        return paths

    def get_config_contents(self, filename):
        config_options = self.node_proxy.get_config_info(filename)
        content = ''
        for name,value in config_options.iteritems():
            if isinstance(value, suds.sax.text.Text):
                content = content + "%s='%s'\n" % (name, repr(value))
            else:
                content = content + '%s=%s\n' % (name, repr(value))
        return content

    def get_external_manager(self):
        if self.external_manager_id:
            vcenter = DBSession.query(VCenter).filter(VCenter.id == self.external_manager_id).first()
            if vcenter:
                credential = vcenter.credential
                vc_cred = dynamic_map()
                vc_cred.hostname = vcenter.host
                vc_cred.username = credential.cred_details['username']
                vc_cred.password = credential.cred_details['password']
                return vc_cred

    def is_script_execution_supported(self):
        return False

    def heartbeat(self):
        if self.isRemote == False:
            return [self.UP, u'Localhost is always up']

        try:
            state = self.node_proxy.get_power_state()
        except VCenterDownError as ex:
            print '===ex1============',
            print ex
            return [self.current_state.avail_state, u'vCenter Down. ' + to_unicode(ex)]
        except urllib2.URLError as ex:
            print '===ex2============',
            print ex
            return [self.DOWN, u'Host not found. ' + to_unicode(ex)]
        except suds.WebFault as ex:
            print '===ex3============',
            print ex
            return [self.DOWN, u'Host not found. ' + to_unicode(ex)]
        except Exception as ex:
            print '===ex5=========',
            print ex
            return [self.DOWN, u'Host not found. ' + to_unicode(ex)]
        return self.get_power_state(state)


    def get_power_state(self, state):
        return self.STATE_MAP.get(state)

    def get_console_local_viewers(self):
        local_viewers = {'vmware-vmrc': constants.VMWARE_VMRC_VIEWER}
        return local_viewers

    def get_console_local_viewer_param_dict(self, cmd, info):
        value_map = {}
        if cmd in [constants.VMWARE_VMRC_VIEWER]:
            value_map[constants.APPLET_IP] = info['hostname']
            value_map[constants.PORT] = info['port']
            value_map[constants.TICKET] = info['ticket']
            value_map[constants.VM_ID] = info['vm_id']
        return value_map

    def _get_vnc_info(self, dom, cmd):
        from stackone.core.utils.VMWUtils import get_external_id
        domm = self.get_dom(dom.id)
        if not domm.is_resident():
            raise Exception('Virtual Machine is not Running.')
        result = {}
        result['hostname'] = self.get_view_console_ip()
        result['port'] = '443'
        result['ticket'] = self.node_proxy.acquire_clone_ticket()
        external_id = get_external_id(dom.id)
        if not external_id:
            raise Exception('Could not find external_id of VM:%s' % dom.name)
        result['vm_id'] = external_id
        result['server'] = ''
        result['vnc_display'] = ''
        result['temp_file'] = ''
        return result

    def get_external_id(self):
        from stackone.core.utils.VMWUtils import get_moid
        hs = self.node_proxy.get_hs()
        return get_moid(hs)

    def get_view_console_ip(self):
        if not self.external_manager_id:
            return self.hostname
        cred = self.get_external_manager()
        if not cred:
            msg = 'could not find vCenter credentials'
            LOGGER.info(msg)
            raise Exception(msg)
        return cred.hostname



class VMWNodeEnvHelper():
    def __init__(self, node_id, node_proxy):
        self.node_proxy = node_proxy
        self.node_id = node_id
        self._VMWNodeEnvHelper__dict = {}
        self._VMWNodeEnvHelper__populateInformation()

    def __iter__(self):
        return self._VMWNodeEnvHelper__dict.iterkeys()

    def keys(self):
        return self._VMWNodeEnvHelper__dict.keys()

    def __getitem__(self, item):
        if not item:
            return None
        if self._VMWNodeEnvHelper__dict.has_key(item):
            return self._VMWNodeEnvHelper__dict[item]
        return None

    def __setitem__(self, item, value):
        self._VMWNodeEnvHelper__dict[item] = value

    def refresh(self):
        DBHelper().delete_all(Instance, [], [Instance.node_id == self.node_id])
        self._VMWNodeEnvHelper__dict = None
        self._VMWNodeEnvHelper__populateDictionary()
        return None

    def get_socket_info(self):
        return self.node_proxy.get_hardware_summary().numCpuPkgs

    def _VMWNodeEnvHelper__populateInformation(self):
        instances = DBHelper().filterby(Instance, [], [Instance.node_id == self.node_id])
        if len(instances) == 0:
            self._VMWNodeEnvHelper__populateDictionary()
        else:
            for instance in instances:
                comp = instance.component
                if comp.type in ('cpu_info', 'memory_info', 'os_info', 'nic_info', 'bridge_info', 'platform_info'):
                    if not self._VMWNodeEnvHelper__dict.has_key(comp.type):
                        self._VMWNodeEnvHelper__dict[comp.type] = {}
                    val = instance.value
                    if val[0] in ('{', '['):
                        val = eval(instance.value)
                    self._VMWNodeEnvHelper__dict[comp.type][instance.name] = val
                    continue
                if comp.type in ('disk_info', 'virt_nw_info', 'storage_info'):
                    self._VMWNodeEnvHelper__dict[comp.type] = eval(instance.value)
                    continue
                if comp.type in ('network_info',):
                    if not self._VMWNodeEnvHelper__dict.has_key(comp.type):
                        self._VMWNodeEnvHelper__dict[comp.type] = []
                    self._VMWNodeEnvHelper__dict[comp.type].append(dict(interface_name=instance.name, ip_address=instance.value))
                    continue
                if comp.type in ('default_bridge',):
                    self._VMWNodeEnvHelper__dict[comp.type] = instance.value
                    continue

    def _VMWNodeEnvHelper__populateDictionary(self):
        if self._VMWNodeEnvHelper__dict is not None:
            self._VMWNodeEnvHelper__dict = None
            #(comp_dict[component.type], device_name, device_type, device_size, mount_path, device_block, device_blocksize, device_size, device_size, datastore_name, datastore_summary, datastore_type, datastore_size, datastore_description, datastore_status, status, status, spec, nw_name, nw_description, nw_type, nw_details, vswitch_key, vswitch_name, nw_type, vnic, spec, ip, vnic, nw_type, vswitch_name, vlan_id, vswitch, pnics, pnics_name, pnics_key, pnics_key, vswitch, self._VMWNodeEnvHelper__dict) = (component, storage_device.displayName, storage_device.deviceType, 0, storage_device.deviceName, storage_device.capacity.block, storage_device.capacity.blockSize, device_block * device_blocksize, convert_byte_to(device_size, convert_to='G', humansize=True), datastore.name, datastore.summary, datastore_summary.type, convert_byte_to(datastore_summary.capacity, convert_to='GB', humansize=False), datastore.name, datastore.overallStatus, 'OUT_OF_SYNC', 'IN_SYNC', portgroup.spec, portgroup.spec.name, nw_name, '', '', portgroup.vswitch, '', 'VMKernel', None, vnic.spec, spec.ip, virtual_nic, 'Virtual Machine', spec.vswitchName, spec.vlanId, None, [], [], [], vswitch.pnic, virtual_switch, None)
        cpu_attributes = [key_cpu_count, key_cpu_vendor_id, key_cpu_model_name, key_cpu_mhz]
        memory_attributes = [key_memory_total, key_memory_free]
        disk_attributes = [key_disk_file_system, key_disk_size, key_disk_mounted]
        print 'BBB Just before node_proxy ',
        print self.node_proxy is None
        host_mob = self.node_proxy.get_hs()
        print 'DEBUG======self.node_proxy.client.server======',
        print self.node_proxy.client.server
        print 'DEBUG======host_mob======',
        print host_mob
        print 'DEBUG=====host_mob.name====',
        print host_mob.name
        hw_summary = host_mob.summary.hardware
        v_idx = hw_summary.cpuModel.find(' ')
        cpu_vendor = hw_summary.cpuModel[0:v_idx]
        cpu_model = hw_summary.cpuModel[v_idx + 1:]
        cpu_dict = {key_cpu_count: hw_summary.numCpuPkgs, key_cpu_vendor_id: cpu_vendor, key_cpu_model_name: cpu_model, key_cpu_mhz: hw_summary.cpuMhz}
        memory_dict = {key_memory_total: str(hw_summary.memorySize / 1048576), key_memory_free: 0}
        network_list = []
        network = host_mob.config.network
        host_virtual_nics = network.vnic
        for vnic in host_virtual_nics:
            network_list.append({key_network_interface_name: vnic.device, key_network_ip: vnic.spec.ip.ipAddress})
        nics = {}
        bridges = {}
        host_portgroups = network.portgroup
        host_physical_nics = network.pnic
        host_virtual_switches = network.vswitch
        host_networks = host_mob.network
        host_networks_name = [hnw.name for hnw in host_networks]
        port_groups_list = []
        for portgroup in host_portgroups:
            spec = portgroup.spec
            nw_name = portgroup.spec.name
            nw_description = nw_name
            nw_type = ''
            nw_details = ''
            vswitch_key = portgroup.vswitch
            vswitch_name = ''
            if spec:
                vswitch_name = spec.vswitchName
                vlan_id = spec.vlanId
                vswitch = None
                pnics = []
                nw_details += 'Switch:%s, VlanId:%s' % (vswitch_name, vlan_id)
                for virtual_switch in host_virtual_switches:
                    if vswitch_key == virtual_switch.key:
                        vswitch = virtual_switch
                        break
                if vswitch:
                    try:
                        pnics_key = vswitch.pnic
                    except AttributeError as ex:
                        pnics_key = []
                    for pnic_key in pnics_key:
                        for physical_nic in host_physical_nics:
                            if pnic_key == physical_nic.key:
                                pnics.append(physical_nic)
                                break
                    if pnics:
                        pnics_name = []
                        for pnic in pnics:
                            pnics_name.append(pnic.device)
                        nw_details += ', Physical adapters:%s' % ','.join(pnics_name)
            if nw_name in host_networks_name:
                nw_type = 'Virtual Machine'
            else:
                nw_type = 'VMKernel'
                vnic = None
                for virtual_nic in host_virtual_nics:
                    if nw_name == virtual_nic.portgroup:
                        break
                if vnic:
                    spec = vnic.spec
                    ip = spec.ip
                    nw_details += ', Virtual Adapter:%s, IP:%s' % (vnic.device, ip.ipAddress)
            port_groups_list.append({key_virtual_network_name: to_str(nw_name), key_virtual_network_type: to_str(nw_type), key_virtual_network_details: to_str(nw_details), key_virtual_network_description: to_str(nw_description), key_virtual_network_switch: to_str(vswitch_name)})
        storage_resource_list = []
        datastores = host_mob.datastore
        for datastore in datastores:
            datastore_name = datastore.name
            datastore_summary = datastore.summary
            datastore_type = datastore_summary.type
            
            ################
            datastore_size = convert_byte_to(datastore_summary.capacity,convert_to = 'GB',humansize = False)
            datastore_description = datastore.name
            datastore_status = datastore.overallStatus
            status = 'OUT_OF_SYNC'
            if datastore_status in ('green',):
                status = 'IN_SYNC'
            storage_resource_list.append({key_storage_resource_name: to_str(datastore_name), key_storage_resource_type: to_str(datastore_type), key_storage_resource_size: to_str(datastore_size), key_storage_resource_description: to_str(datastore_description), key_storage_resource_status: to_str(status)})
        disk_list = []
        storage_devices = host_mob.configManager.storageSystem.storageDeviceInfo.scsiLun
        for storage_device in storage_devices:
            device_name = storage_device.displayName
            device_type = storage_device.deviceType
            device_size = 0
            if device_type in ('disk',):
                device_block = storage_device.capacity.block
                device_blocksize = storage_device.capacity.blockSize
                device_size = device_block * device_blocksize
                ###########
                device_size = convert_byte_to(device_size,convert_to = 'G',humansize = True)
            mount_path = storage_device.deviceName
            disk_list.append({key_disk_file_system: to_str(device_name), key_disk_size: to_str(device_size), key_disk_mounted: to_str(mount_path)})
        summary = host_mob.summary
        product = summary.config.product
        os_dict = {key_os_release:product.version + 'build-' + product.build,key_os_system:product.name,key_os_machine:product.osType,key_os_distro:product.name,key_os_distro_ver:product.version,key_os_distro_string:product.fullName,'node_name':summary.config.name}
        def_bridge = ''
        platform_dict = {'version':product.version}
        if platform_dict is None:
            raise Exception('Cannot get server platform')
        self._VMWNodeEnvHelper__dict = dict([('cpu_info',cpu_dict),('memory_info',memory_dict),('disk_info',disk_list),('network_info',network_list),('nic_info',nics),('bridge_info',bridges),('os_info',os_dict),('default_bridge',def_bridge),('platform_info',platform_dict),('virt_nw_info',port_groups_list),('storage_info',storage_resource_list)])
        
        comp_dict = {}
        components = DBHelper().get_all(Component)
        for component in components:
            comp_dict[component.type] = component
        instances = []
        for key,val in self._VMWNodeEnvHelper__dict.iteritems():
            print key,'-----------------',val
            if key in ('cpu_info', 'memory_info', 'os_info', 'nic_info', 'bridge_info', 'platform_info'):
                for k1,v1 in val.iteritems():
                    inst = Instance(to_unicode(k1))
                    inst.value = to_unicode(v1)
                    inst.display_name = to_unicode('')
                    inst.component = comp_dict[key]
                    inst.node_id = self.node_id
                    instances.append(inst)
                continue
            if key in ('disk_info', 'storage_info'):
                inst = Instance(to_unicode('disks'))
                inst.value = to_unicode(val)
                inst.display_name = to_unicode('')
                inst.component = comp_dict[key]
                inst.node_id = self.node_id
                instances.append(inst)
                continue
            if key in ('network_info',):
                for i in range(len(val)):
                    k1,v1 = val[i]
                    inst = Instance(to_unicode(val[i][k1]))
                    inst.value = to_unicode(val[i][v1])
                    inst.display_name = to_unicode('')
                    inst.component = comp_dict[key]
                    inst.node_id = self.node_id
                    instances.append(inst)
                continue
            if key in ('virt_nw_info',):
                inst = Instance(to_unicode('networks'))
                inst.value = to_unicode(val)
                inst.display_name = to_unicode('')
                inst.component = comp_dict[key]
                inst.node_id = self.node_id
                instances.append(inst)
                continue
            if key in ('default_bridge',):
                inst = Instance(to_unicode(key))
                inst.value = to_unicode(val)
                inst.display_name = to_unicode('')
                inst.component = comp_dict[key]
                inst.node_id = self.node_id
                instances.append(inst)
                continue
        DBHelper().add_all(instances)


    def populate_platform_info(self):
        m_node = DBSession.query(ManagedNode).filter(ManagedNode.id == self.node_id).one()
        platform_dict = m_node.get_vmm_info()
        return platform_dict


#
#if __name__ == '__main__':
#    test_domu = 'test'
#    host = 'localhost'
#    dom_file = '/etc/vmw/test'
#    dom_2b_started = 'test'
#    dom_2b_shutdown = 'test'
#    username = 'root'
#    print 'Enter password '
#    passwd = sys.stdin.readline().strip()
#    remote = True
#    if not remote:
#        not remote
#        host = 'localhost'
#    else:
#        not remote
#        host = '192.168.12.101'
#        test_domu = 'test'
#        dom_file = '/etc/vmw/test'
#        dom_2b_started = 'test'
#        dom_2b_shutdown = 'test'
#    managed_node = VMWNode(hostname=host, username=username, password=passwd, isRemote=remote)
#    names = managed_node.get_dom_names()
#    for dom_name in names:
#        print dom_name,
#        print managed_node.get_state(dom_name)
#    for dom_name in names:
#        print dom_name,
#        print managed_node.get_state(dom_name)
