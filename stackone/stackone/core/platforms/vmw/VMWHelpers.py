from psphere import config, template
from psphere.client import Client
from psphere.errors import TemplateNotFoundError
from psphere.soap import VimFault
from psphere.errors import ObjectNotFoundError
import re
import traceback
import time
import sys
from stackone.core.utils.utils import to_unicode, to_str
from stackone.core.utils.VMWUtils import get_moid, parse_datastore_name_from_diskpath
import logging
LOGGER = logging.getLogger('stackone.core.platforms.vmw')
class VMWProvisioningHelper():
    SUCCESS = 0
    FAILED = 1
    LOG_FILE = ''
    def __init__(self, *args, **kwargs):
        pass

    def get_client(self, node):
        return node.node_proxy.client

    def cleanupQCDomain(self, managed_node, dom, auth):
        managed_node.get_vmm().delete(dom.name)

    def execute_provisioning_script(self, auth, managed_node, image_id, v_config, i_config):
        from stackone.model import DBSession
        from stackone.model.ImageStore import Image
        image = DBSession.query(Image).filter(Image.id == image_id).first()
        phelper = image.get_provisioning_helper()
        return phelper.provision_vm(auth, managed_node, image_id, v_config, i_config)

    def provision_vm(self, auth, managed_node, image_id, v_config, i_config):
        external_id = None
        client = self.get_client(managed_node)
        name = v_config.name
        compute_resource = v_config.get('compute_resource')
        disks = v_config.getDisks(i_config)
        nics = v_config.getNetworks(i_config)
        print '------nics--------',
        print nics
        memory = v_config.get('memory')
        cpus = v_config.get('vcpus')
        guest_id = v_config.get('guest_id')
        if not guest_id:
            msg = 'guest_id not specified in miscellaneous tab of selected template. Example:ubuntu64Guest'
            LOGGER.error(msg)
            raise Exception(msg)
        host = None
        if not compute_resource:
            os_info = managed_node.get_os_info()
            if os_info:
                host = os_info.get('node_name')
        print '--compute_resource---host--',
        print compute_resource,
        print host
        try:
            task_result = self.create_vm(client, name, compute_resource, nics, memory, cpus, guest_id, host, disks)
            if not task_result['success']:
                return (task_result['msg'], self.FAILED, self.LOG_FILE, external_id)
            vm_mob = task_result['result']
            if not vm_mob:
                raise Exception('Could not find VirtualMachine managedobject')
            external_id = get_moid(vm_mob)
            managed_node.node_proxy.update_vms()
            return (task_result['msg'], self.SUCCESS, self.LOG_FILE, external_id)

        except Exception as ex:
            traceback.print_stack()
            msg = str(ex)
            return (msg, self.FAILED, self.LOG_FILE, external_id)

        return None

#    def create_vm(self, name, compute_resource, datastore, disksize, nics,
#                  memory, num_cpus, guest_id, host=None):
    def create_vm(self, client, name, compute_resource, nics, memory, num_cpus, guest_id, host=None, disks=None):
        print 'Creating VM %s' % name
        print '########compute_resource#########',compute_resource
        if host is None:
            try:
                target = client.find_entity_view('ComputeResource', filter={'name': compute_resource})
            except ObjectNotFoundError as ex:
                raise ObjectNotFoundError('Could not find ComputeResource:%s. %s' % (compute_resource, to_str(ex)))
            resource_pool = target.resourcePool
            print '=====resource_pool========',
            print resource_pool
        else:
            try:
                target = client.find_entity_view('HostSystem', filter={'name': host})
            except ObjectNotFoundError as ex:
                raise ObjectNotFoundError('Could not find HostSystem:%s. %s' % (host, to_str(ex)))
            resource_pool = target.parent.resourcePool
        print '======memory======',
        print memory
        vm_devices = []
        virtual_controller = VirtualController()
        lsi_logic_controller = self.create_lsi_logic_controller(client, virtual_controller.get_key())
        vm_devices.append(lsi_logic_controller)
        lsi_logic_controller_index = lsi_logic_controller.device.key
        print '=======lsi_logic_controller_index========',
        print lsi_logic_controller_index
        target_datastore_dict = self.get_datastores(target)
        default_datastore = None
        for disk in disks:
            #716
            if disk.type in ('file',):
                #625
                ds_name = parse_datastore_name_from_diskpath(disk.filename)
                ds = self.get_datastore_by_name(ds_name, target_datastore_dict)
                if not default_datastore:
                    #405
                    default_datastore = ds
                if disk.type in ('file',) and  not disk.is_iso():
                    disk_spec = self.create_disk(client, ds, disk.get_size(), virtual_controller.get_key(), virtual_controller.get_virtual_disk_unit_number_count(), controller_index=lsi_logic_controller_index)    
                    vm_devices.append(disk_spec)
                #713
                elif disk.type in ('file',) and  disk.is_iso():
                    #621
                    iso_path = self.parse_filename_get_path(disk.filename)
                    controller_key, unit_number = virtual_controller.get_virtual_ide_controller_key()
                    iso_disk_spec = self.add_iso_disk(client, ds, iso_path, virtual_controller.get_key(), unit_number, controller_key)
                    vm_devices.append(iso_disk_spec)

            elif disk.type in ('phy',):
                #712
                unit_number,controller_key = virtual_controller.get_virtual_ide_controller_key()
                cdrom_spec = self.add_virtual_cd_rom(client, disk.filename, virtual_controller.get_key(), unit_number, controller_key)
                vm_devices.append(cdrom_spec)
        for nic in nics:
            #820
            nic_spec = self.create_nic(client, target, nic, virtual_controller.get_key(), virtual_controller.get_virtual_network_unit_number_count())
            if nic_spec is None:
                msg = 'Could not create spec for NIC'
                raise Exception(msg)
            vm_devices.append(nic_spec)
        vm_path_name = default_datastore.name
        print vm_path_name,'##########vm_path_name########'
        vmfi = self.create_virtual_machine_file_info(client, vm_path_name)
        print '######vmfi########',vmfi
        print '******************************************'
        vm_config_spec = self.create_virtual_machine_config_spec(client, name, num_cpus, memory, guest_id, vmfi, vm_devices)
        print vm_config_spec,'#######vm_config_spec######'
        datacenter = self.get_datacenter(target)
        try:
            task = datacenter.vmFolder.CreateVM_Task(config=vm_config_spec, pool=resource_pool)
        except VimFault as e:
            msg = 'Failed to create %s: ' % e
            raise Exception(msg)
        task_result = self.wait_for_task(task)
        print '====task_result====',
        print task_result
        return task_result


    def create_virtual_machine_config_spec(self, client, name, num_cpus, memory_mb, guest_id, vmfi, vm_devices):
        vm_config_spec = client.create('VirtualMachineConfigSpec')
        vm_config_spec.name = name
        vm_config_spec.memoryMB = memory_mb
        vm_config_spec.files = vmfi
        vm_config_spec.annotation = 'Auto-provisioned by psphere'
        vm_config_spec.numCPUs = num_cpus
        vm_config_spec.guestId = guest_id
        vm_config_spec.deviceChange = vm_devices
        return vm_config_spec

    def create_virtual_machine_file_info(self, client, vm_path_name):
        vmfi = client.create('VirtualMachineFileInfo')
        vmfi.vmPathName = '[%s]' % vm_path_name
        return vmfi

    def get_datacenter(self, target):
        datacenter = None
        parent = target.parent
        while parent:
            if parent.__class__.__name__ == 'Datacenter':
                datacenter = parent
                break
            parent = parent.parent
        if not datacenter:
            raise Exception("No datacenter found for '%s' compute resource." % target.name)
        return datacenter

    def get_datastores(self, target):
        target_datastore_dict = {}
        for ds in target.datastore:
            target_datastore_dict[ds.name] = ds
        return target_datastore_dict

    def get_datastore_by_name(self, dsname, target_datastore_dict, target=None):
        ds = None
        if not target_datastore_dict:
            target_datastore_dict = {}
        if target:
            target_datastore_dict = self.get_datastores(target)
        try:
            ds = target_datastore_dict[dsname]
            accessible = self.is_datastore_accessible(ds)
            if not accessible:
                msg = 'Datastore (%s) exists, but is not accessible' % ds.summary.name
                raise Exception(msg)
        except KeyError as ex:
            msg = 'Could not find datastore with name %s, available datastores=%s' % (dsname, target_datastore_dict.keys())
            raise Exception(msg)
        return ds

    def is_datastore_accessible(self, ds):
        return ds.summary.accessible

    def parse_filename_get_datastore(self, filename):
        parts = filename.split('/')
        if not len(parts) > 1:
            msg = 'ERROR: Invalid filename:%s. filename should be like /datastore1/test/test1.vmdk' % filename
            raise Exception(msg)
        return parts[1]

    def parse_filename_get_path(self, filename):
        parts = filename.split('/')
        if not len(parts) > 1:
            msg = 'ERROR: Invalid filename:%s. filename should be like /datastore1/test/test1.vmdk' % filename
            raise Exception(msg)
        iso_path = filename[len(parts[1]) + 2:]
        print '======iso_path=======',
        print iso_path
        return iso_path

    def get_nw_port_group(self, bridge):
        parts = bridge.split(':')
        if len(parts) != 2:
            msg = "Invalid entry bridge (expected 'vswitch0:VM Nettwork' but got '%s')" % bridge
            raise Exception(msg)
        return parts[1]

    def create_nic(self, client, target, nic, key, unit_number):
        default_nw_port_group = 'VM Network'
        net = None
        model = nic.get_item('model')
        address_type = 'generated'
        mac = nic.get_mac()
        bridge = nic.get_bridge()
        nw_port_group = self.get_nw_port_group(bridge)
        if not nw_port_group:
            nw_port_group = default_nw_port_group
        if mac:
            address_type = 'manual'
        msg = '\nCreating Network:%s of Type:%s, MAC:%s, Bridge:%s' % (nw_port_group, model, mac, bridge)
        print msg
        for network in target.network:
            if network.name == nw_port_group:
                net = network
                break
        if not net:
            msg = 'Could not find Network:%s on HostSystem:%s' % (nw_port_group, target.name)
            raise Exception(msg)
        backing = client.create('VirtualEthernetCardNetworkBackingInfo')
        backing.deviceName = nw_port_group
        backing.network = net
        backing.useAutoDetect = False
        connect_info = client.create('VirtualDeviceConnectInfo')
        connect_info.allowGuestControl = True
        connect_info.connected = False
        connect_info.startConnected = True
        new_nic = client.create(model)
        new_nic.backing = backing
        new_nic.key = key
        new_nic.unitNumber = unit_number
        new_nic.addressType = address_type
        new_nic.macAddress = mac
        new_nic.connectable = connect_info
        nic_spec = client.create('VirtualDeviceConfigSpec')
        nic_spec.device = new_nic
        nic_spec.fileOperation = None
        operation = client.create('VirtualDeviceConfigSpecOperation')
        nic_spec.operation = operation.add
        return nic_spec

    def create_lsi_logic_controller(self, client, key):
        controller = client.create('VirtualLsiLogicController')
        controller.key = key
        controller.device = []
        controller.busNumber = (key)
        controller.sharedBus = client.create('VirtualSCSISharing').noSharing
        spec = client.create('VirtualDeviceConfigSpec')
        spec.device = controller
        spec.fileOperation = None
        spec.operation = client.create('VirtualDeviceConfigSpecOperation').add
        return spec

    def create_ide_controller(self, client, key, unit_number):
        print '====key====unit_number=====',
        print key,
        print unit_number
        controller = client.create('VirtualIDEController')
        controller.key = key
        controller.device = []
        controller.unitNumber = unit_number
        spec = client.create('VirtualDeviceConfigSpec')
        spec.device = controller
        spec.fileOperation = None
        spec.operation = client.create('VirtualDeviceConfigSpecOperation').add
        return spec

    def create_disk(self, client, datastore, disksize_mb, key, unit_number, controller_index=0):
        disksize_kb = disksize_mb * 1024
        print '==create_disk===key==unit_number==controller_index==',
        print key,
        print unit_number,
        print controller_index
        backing = client.create('VirtualDiskFlatVer2BackingInfo')
        backing.datastore = None
        backing.diskMode = 'persistent'
        backing.fileName = '[%s]' % datastore.summary.name
        backing.thinProvisioned = True
        backing.split = False
        disk = client.create('VirtualDisk')
        disk.backing = backing
        disk.controllerKey = controller_index
        disk.key = key
        disk.unitNumber = unit_number
        disk.capacityInKB = disksize_kb
        disk_spec = client.create('VirtualDeviceConfigSpec')
        disk_spec.device = disk
        file_op = client.create('VirtualDeviceConfigSpecFileOperation')
        disk_spec.fileOperation = file_op.create
        operation = client.create('VirtualDeviceConfigSpecOperation')
        disk_spec.operation = operation.add
        print '\nDisk added'
        return disk_spec

    def add_virtual_cd_rom(self, client, device_name, key, unit_number, controller_index):
        print '==add_virtual_cd_rom==key==unit_number==controller_index==',
        print key,
        print unit_number,
        print controller_index
        backing = client.create('VirtualCdromAtapiBackingInfo')
        backing.deviceName = device_name
        backing.useAutoDetect = False
        connect_info = client.create('VirtualDeviceConnectInfo')
        connect_info.allowGuestControl = True
        connect_info.connected = False
        connect_info.startConnected = True
        disk = client.create('VirtualCdrom')
        disk.backing = backing
        disk.controllerKey = controller_index
        disk.key = key
        disk.unitNumber = unit_number
        disk.connectable = connect_info
        disk_spec = client.create('VirtualDeviceConfigSpec')
        disk_spec.device = disk
        disk_spec.fileOperation = None
        operation = client.create('VirtualDeviceConfigSpecOperation')
        disk_spec.operation = operation.add
        print '\nVirtual CD ROM added'
        return disk_spec

    def add_iso_disk(self, client, datastore, path2iso, key, unit_number, controller_index):
        print '==add_iso_disk===key==unit_number==controller_index==',
        print key,
        print unit_number,
        print controller_index
        backing = client.create('VirtualCdromIsoBackingInfo')
        backing.datastore = datastore
        backing.fileName = '[%s] %s' % (datastore.summary.name, path2iso)
        connect_info = client.create('VirtualDeviceConnectInfo')
        connect_info.allowGuestControl = True
        connect_info.connected = False
        connect_info.startConnected = True
        disk = client.create('VirtualCdrom')
        disk.backing = backing
        disk.controllerKey = controller_index
        disk.key = key
        disk.unitNumber = unit_number
        disk.connectable = connect_info
        disk_spec = client.create('VirtualDeviceConfigSpec')
        disk_spec.device = disk
        disk_spec.fileOperation = None
        operation = client.create('VirtualDeviceConfigSpecOperation')
        disk_spec.operation = operation.add
        print '\nISO Disk added'
        return disk_spec

    def clone_to(self, client, v_config):
        pass

    def wait_for_task(self, task):
        msg = ''
        import time
        print task.info.state,'#######task.info.state###########'
        while task.info.state in ('queued', 'running'):
            #140
            time.sleep(5)
            task.update()
            print 'Waiting 5 more seconds for the Task: %s' % task.info.key
            try:
                print 'Status: %s' % task.info.description.message
                print 'Progress: %s' % task.info.progress
            except AttributeError:
                continue
        if task.info.state == 'success':
            elapsed_time = task.info.completeTime - task.info.startTime
            msg += 'Task Successfully Completed. Server took %s seconds.' % elapsed_time.seconds
            return {'success': True, 'msg': msg, 'result': task.info.result}

        if task.info.state == 'error':
            #462
            try:
                msg = 'ERROR: %s, Entity:%s, LocalizedMessage:%s ' % (task.info.name, task.info.entityName, task.info.error.localizedMessage)
                fault_message = ''
                try:
                    for fmsg in task.info.error.fault.faultMessage:
                        fault_message += fmsg.message
                except AttributeError as ex:
                    print 'AttributeError:',
                    print ex
                if fault_message:
                    msg = '%s, FaultMessage:%s' % (msg, fault_message)
                return {'success': False, 'msg': msg, 'result': None}
            except AttributeError:
                print 'ERROR: There is no error message available.'
        else:
            msg += 'UNKNOWN: The task reports an unknown state %s' % task.info.state
        return {'success': False, 'msg': msg, 'result': None}




class VcenterProvisioningHelper(VMWProvisioningHelper):
    def __init__(self, *args, **kwargs):
        VMWProvisioningHelper.__init__(self, *args, **kwargs)

    def provision_vm(self, auth, managed_node, image_id, v_config, i_config):
        from stackone.model import DBSession
        from stackone.model.ImageStore import Image
        external_id = None
        image = DBSession.query(Image).filter(Image.id == image_id).first()
        client = self.get_client(managed_node)
        config_context = {}
        config_context['dest_datastore'] = v_config.get('datastore')
        config_context['dest_host'] = managed_node.hostname
        config_context['name'] = v_config.get('name')
        config_context['vmfolder'] = v_config.get('vmfolder')
        config_context['mob_name'] = image.name
        disks = v_config.getDisks(i_config)
        config_context['disks'] = disks
        task_result = self.clone_to(client, v_config, config_context=config_context)
        if not task_result['success']:
            return (task_result['msg'], self.FAILED, self.LOG_FILE, external_id)
        vm_mob = task_result['result']
        if not vm_mob:
            raise Exception('Could not find VirtualMachine managedobject')
        external_id = get_moid(vm_mob)
        return (task_result['msg'], self.SUCCESS, self.LOG_FILE, external_id)

    def clone_image(self, vm_config, config_context=None):
        if not config_context:
            config_context = {}
        external_manager_id = config_context.get('external_manager_id')
        if not external_manager_id:
            raise Exception('Could not find external_manager_id')
        vesxi_node = self.get_vesxi_node(external_manager_id)
        client = self.get_client(vesxi_node)
        return self.clone_to(client, vm_config, to_template=True, power_on=False, config_context=config_context)

    def create_image_from_vm(self, vm_config, config_context=None):
        return self.clone_image(vm_config, config_context)

    def get_vesxi_node(self, vcenter_id):
        from stackone.model.VcenterManager import VcenterManager
        vcenter_manager = VcenterManager()
        vcenter,vcenter_cred = vcenter_manager.get_vcenter_credential_dict(vcenter_id)
        vesxi_node = vcenter_manager.get_vesxi_node(vcenter_id, hostname=vcenter_cred['hostname'])
        return vesxi_node

    def delete_image(self, vm_config):
        try:
            msg = ''
            image_name = vm_config.name
            dc_name = vm_config['datacenter']
            external_manager_id = vm_config['external_manager_id']
            vesxi_node = self.get_vesxi_node(external_manager_id)
            client = self.get_client(vesxi_node)
            try:
                dc = client.find_entity_view('Datacenter', filter={'name': dc_name})
            except ObjectNotFoundError as ex:
                raise ObjectNotFoundError('Could not find Datacenter:%s. %s' % (dc_name, to_str(ex)))
            try:
                img = client.find_entity_view('VirtualMachine', begin_entity=dc, filter={'name': image_name})
            except ObjectNotFoundError as ex:
                raise ObjectNotFoundError('Could not find VirtualMachine:%s. %s' % (image_name, to_str(ex)))
            print '======img========',
            print img,
            print img.name
            if img:
                t = img.Destroy_Task()
                msg = self.wait_for_task(t)
                print '========msg======',
                print msg
                return msg
        except ObjectNotFoundError as ex:
            msg = to_str(ex)
        except Exception as ex:
            raise ex
        return msg

    def clone_to(self, client, v_config, to_template=False, power_on=False, vm_config_spec_dict=None, config_context=None):
        if not vm_config_spec_dict:
            vm_config_spec_dict = {}
        if not config_context:
            config_context = {}
        print '======config_context==========',
        print config_context
        name = config_context.get('name')
        mob_name = config_context.get('mob_name')
        host = config_context.get('dest_host')
        if not host:
            raise Exception('Esxi Host should not be None')
        try:
            vm = client.find_entity_view('VirtualMachine', filter={'name': mob_name})
        except ObjectNotFoundError as ex:
            raise ObjectNotFoundError('Could not find VirtualMachine:%s. %s' % (mob_name, to_str(ex)))
        vmfolder_mob = None
        vmfolder = config_context.get('vmfolder')
        if not vmfolder:
            raise Exception('Location/vmFolder should not be None')
        try:
            vmfolder_mob = client.find_entity_view('Folder', filter={'name': vmfolder})
        except ObjectNotFoundError as ex:
            raise ObjectNotFoundError('Could not find Folder:%s. %s' % (vmfolder, to_str(ex)))
        try:
            host_system = client.find_entity_view('HostSystem', filter={'name': host})
        except ObjectNotFoundError as ex:
            raise ObjectNotFoundError('Could not find HostSystem:%s. %s' % (host, to_str(ex)))
        resource_pool = host_system.parent.resourcePool
        ds_to_use = None
        disks = config_context.get('disks')
        for disk in disks:
            if disk.type in ('file',) and not disk.is_iso():
                ds_name = parse_datastore_name_from_diskpath(disk.filename)
                target_datastore_dict = self.get_datastores(host_system)
                ds_to_use = self.get_datastore_by_name(ds_name, target_datastore_dict)
                break
        if not ds_to_use:
            raise Exception('Could not find datastore')
        vm_clone_spec = client.create('VirtualMachineCloneSpec')
        vm_reloc_spec = client.create('VirtualMachineRelocateSpec')
        vm_reloc_spec.datastore = ds_to_use
        vm_reloc_spec.diskMoveType = None
        vm_reloc_spec.pool = resource_pool
        vm_reloc_spec.host = host_system
        vm_reloc_spec.transform = 'sparse'
        vm_reloc_spec_disk_locr = client.create('VirtualMachineRelocateSpecDiskLocator')
        vm_reloc_spec_disk_locr.datastore = ds_to_use
        vm_reloc_spec_disk_locr.diskMoveType = None
        vm_reloc_spec.disk = None
        vm_clone_spec.location = vm_reloc_spec
        vm_clone_spec.template = to_template
        vm_clone_spec.powerOn = power_on
        vm_config_spec = client.create('VirtualMachineConfigSpec')
        vm_config_spec.alternateGuestName = None
        vm_config_spec.annotation = None
        vm_config_spec.bootOptions = None
        vm_config_spec.changeTrackingEnabled = None
        vm_config_spec.changeVersion = None
        vm_config_spec.consolePreferences = None
        vm_config_spec.cpuAffinity = None
        vm_config_spec.cpuAllocation = None
        vm_config_spec.cpuFeatureMask = None
        vm_config_spec.cpuHotAddEnabled = None
        vm_config_spec.cpuHotRemoveEnabled = None
        vm_config_spec.deviceChange = None
        vm_config_spec.extraConfig = None
        vm_config_spec.files = None
        vm_config_spec.firmware = None
        vm_config_spec.flags = None
        vm_config_spec.ftInfo = None
        vm_config_spec.guestAutoLockEnabled = None
        vm_config_spec.guestId = None
        vm_config_spec.instanceUuid = None
        vm_config_spec.locationId = None
        vm_config_spec.managedBy = None
        vm_config_spec.maxMksConnections = None
        vm_config_spec.memoryAffinity = None
        vm_config_spec.memoryAllocation = None
        vm_config_spec.memoryHotAddEnabled = None
        vm_config_spec.memoryMB = None
        vm_config_spec.memoryReservationLockedToMax = None
        vm_config_spec.name = None
        vm_config_spec.networkShaper = None
        vm_config_spec.npivDesiredNodeWwns = None
        vm_config_spec.npivDesiredPortWwns = None
        vm_config_spec.npivNodeWorldWideName = None
        vm_config_spec.npivOnNonRdmDisks = None
        vm_config_spec.npivPortWorldWideName = None
        vm_config_spec.npivTemporaryDisabled = None
        vm_config_spec.npivWorldWideNameOp = None
        vm_config_spec.npivWorldWideNameType = None
        vm_config_spec.numCoresPerSocket = None
        vm_config_spec.numCPUs = None
        vm_config_spec.powerOpInfo = None
        vm_config_spec.swapPlacement = None
        vm_config_spec.tools = None
        vm_config_spec.uuid = None
        vm_config_spec.vAppConfig = None
        vm_config_spec.vAppConfigRemoved = None
        vm_config_spec.vAssertsEnabled = None
        vm_config_spec.version = None
        vm_config_spec.virtualICH7MPresent = None
        vm_config_spec.virtualSMCPresent = None
        vm_clone_spec.config = vm_config_spec
        vm_clone_spec.snapshot = None
        vm_clone_spec.customization = None

        try:
            task = vm.CloneVM_Task(folder=vmfolder_mob, name=name, spec=vm_clone_spec)
            print '===successfully Created====',
            print name,
            print task,
            print vars(task)
        except Exception as ex:
            msg = 'Failed to clone %s: ' % ex
            raise Exception(msg)
        task_result = self.wait_for_task(task)
        print '====task_result====',
        print task_result
        return task_result




class VirtualController(object):
    def __init__(self):
        from stackone.core.utils.ordereddict import OrderedDict
        self.DEFAULT_VIRTUAL_IDE_CONTOLLER_KEYS = OrderedDict({'200': [None, None], '201': [None, None]})
        self.virtual_ide_unit_number_count = 0
        self.key = 0
        self.virtual_disk_unit_number_count = 0
        self.virtual_network_unit_number_count = 0

    def get_virtual_ide_controller_key(self):
        for k,v in self.DEFAULT_VIRTUAL_IDE_CONTOLLER_KEYS.items():
            for index,item in enumerate(v):
                if not item:
                    v[index] = True
                    return (k, index)
        return (201, 2)

    def increment_virtual_disk_unit_number_count(self):
        self.virtual_disk_unit_number_count += 1

    def increment_virtual_network_unit_number_count(self):
        self.virtual_network_unit_number_count += 1

    def get_virtual_disk_unit_number_count(self):
        cnt = self.virtual_disk_unit_number_count
        self.increment_virtual_disk_unit_number_count()
        return cnt

    def get_virtual_network_unit_number_count(self):
        cnt = self.virtual_network_unit_number_count
        self.increment_virtual_network_unit_number_count()
        return cnt

    def get_key(self):
        key = self.key
        self.increment_key()
        return key

    def increment_key(self):
        self.key += 1



