import select
import traceback
import fcntl
import re
import time
from stackone.core.utils.utils import dynamic_map
from stackone.core.utils.utils import to_unicode, to_str
from stackone.core.utils.phelper import *
from stackone.core.utils.NodeProxy import *
from stackone.model.VMM import VMM
from VMWConstants import *
import logging
LOGGER = logging.getLogger('stackone.core.platforms.vmw')
class VMWVMM(VMM):
    def __init__(self, node):
        self.node = node
        self.node_proxy = node.node_proxy
        self.vm_list = None
        self._info = None
        self._slashes = None
        self.info()

    def set_node_proxy(self, node_proxy):
        self.node_proxy = node_proxy
        self.vm_list.clear()

    def info(self):
        if self._info is None:
            self._info = {key_version: 'version TBI'}
        return self._info

    def is_in_error(self):
        return False

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_vms(self):
        self.refresh_vm_list()
        return self.vm_list

    def get_vm_info(self, name):
        vms = self.get_vms()
        return vms.get(name)

    def _to_vmInfo(self, vm_mo):
        vm_info = dynamic_map()
        try:
            config = vm_mo.config
            vm_info.name = config.name
            vm_info.id = config.name
            vm_info.uuid = config.instanceUuid
            vm_info.memory = config.hardware.memoryMB
            vm_info.vcpus = config.hardware.numCPU
            vm_info.config_filename = config.files.vmPathName
            vm_info.external_id = vm_mo._mo_ref.value
            vm_info.platform = 'vmw'
            vm_info.state = vm_mo.runtime.powerState
            vm_info.overall_cpu_usage = 0
            vm_info.guest_memory_usage = 0
        except Exception as ex:
            msg = 'ERROR:===_to_vmInfo===VMName:%s' % vm_mo.name
            print msg
            raise ex
        return vm_info

    def refresh(self, id):
        vm_mo = self.node_proxy.get_vm(id)
        return self._to_vmInfo(vm_mo)

    def refresh_vm_list(self):
        vm_mos = self.node_proxy.get_vm_mob_list()
        vms = {}
        for v in vm_mos:
            vm_info = self._to_vmInfo(v)
            vms[vm_info.id] = vm_info
        self.vm_list = vms
        return vms

    def start(self, config, timeout=5):
        if config is None:
            raise Exception('No context provided to start the vm')
        vm_mo = self.node_proxy.get_vm(config.name)
        if vm_mo:
            t = vm_mo.PowerOnVM_Task()
            self.wait_for_task(t)
        return config.get('name')

    def shutdown(self, id):
        vm_mo = self.node_proxy.get_vm(id)
        if vm_mo:
            t = vm_mo.PowerOffVM_Task()
            return self.wait_for_task(t)
        raise Exception('VM with id %s not found.' % id)

    def reboot(self, id):
        vm_mo = self.node_proxy.get_vm(id)
        if vm_mo:
            t = vm_mo.ResetVM_Task()
            return self.wait_for_task(t)
        raise Exception('VM with id %s not found.' % id)

    def pause(self, id):
        vm_mo = self.node_proxy.get_vm(id)
        if vm_mo:
            t = vm_mo.SuspendVM_Task()
            return self.wait_for_task(t)
        raise Exception('VM with id %s not found.' % id)

    def unpause(self, id):
        vm_mo = self.node_proxy.get_vm(id)
        if vm_mo:
            t = vm_mo.PowerOnVM_Task()
            return self.wait_for_task(t)

    def save(self, id, filename, cfg):
        raise Exception('VMW : save : snapshot : TBI.')

    def restore(self, filename):
        raise Exception('VMW : resume : snapshot : TBI.')

    def destroy(self, id):
        vm_mo = self.node_proxy.get_vm(id)
        if vm_mo:
            t = vm_mo.PowerOffVM_Task()
            return self.wait_for_task(t)
        raise Exception('Destroy : VM with id %s not found.' % id)

    def migrate(self, id, dst, live, port, cfg):
        raise Exception('VMW migrate: TBI')

    def delete(self, id):
        vm_mo = None
        try:
            vm_mo = self.node_proxy.get_vm(id)
        except Exception as ex:
            msg = to_str(ex)
            LOGGER.info(msg)
        if vm_mo:
            t = vm_mo.Destroy_Task()
            self.wait_for_task(t)
            self.node_proxy.update_vms()

    def list_snapshots(self, id):
        raise Exception('VMW list snapshots: TBI')

    def setVCPUs(self, id, value):
        self.setMemoryAndVCPUs(id, value, 'vcpus')

    def setMem(self, id, value):
        self.setMemoryAndVCPUs(id, value, 'memory')

    def setDownVCPUs(self, id, value):
        self.setVCPUs(id, value)

    def setDownMem(self, id, value):
        self.setMem(id, value)

    def setMemoryAndVCPUs(self, id, value, config_set_string):
        from psphere.soap import VimFault
        from psphere.errors import ObjectNotFoundError
        vm_mo = self.node_proxy.get_vm(id)
        vm_name = vm_mo.name
        new_config = self.node_proxy.create('VirtualMachineConfigSpec')
        if config_set_string == 'memory':
            new_config.memoryMB = value
        elif config_set_string == 'vcpus':
            new_config.numCPUs = value
        else:
            desc = 'UNKNOWN: Unknown settings ' + config_set_string + ' for the VM ' + vm_name
            raise Exception(desc)
        try:
            task = vm_mo.ReconfigVM_Task(spec=new_config)
        except VimFault as e:
            desc = 'Failed to reconfigure %s: ' % e
            raise Exception(desc)
        while task.info.state in ('queued', 'running'):
            print 'Waiting 5 more seconds for VM creation'
            time.sleep(5)
            task.update()

        if task.info.state == 'success':
            elapsed_time = task.info.completeTime - task.info.startTime
            print 'Successfully reconfigured VM %s. Server took %s seconds.' % (vm_name, elapsed_time.seconds)

        elif task.info.state == 'error':
            desc = 'ERROR: The task for reconfiguring the VM has finished with an error. If an error was reported it will follow.'

            try:
                desc = 'ERROR: %s' % task.info.error.localizedMessage
            except AttributeError:
                desc = 'ERROR: There is no error message available.'
        else:
            desc = 'UNKNOWN: The task reports an unknown state %s' % task.info.state
        if task.info.state != 'success':
            raise Exception(desc)


    def attachDisks(self, id, attach_disk_list):
        raise Exception('VMW : Can not attach disks for running vm.')

    def detachDisks(self, id, detach_disk_list):
        raise Exception('VMW : Can not detach disks for running vm.')

    def set_vnc_password(self, id, password):
        return True

    def wait_for_task(self, t):
        state = t.info.state
        while state not in ('success', 'error'):
            print '##### Waiting for vmw task to finish',
            print state
            time.sleep(5)
            t.update(properties='info')
            state = t.info.state
        if state == 'error':
            desc = 'ERROR: %s, Entity:%s, LocalizedMessage:%s ' % (t.info.name, t.info.entityName, t.info.error.localizedMessage)
            fault_message = ''
            try:
                for fmsg in t.info.error.fault.faultMessage:
                    fault_message += fmsg.message
            except AttributeError as ex:
                print 'AttributeError:',
                print ex
            if fault_message:
                desc = '%s, FaultMessage:%s' % (desc, fault_message)
        else:
            desc = '%s : Success, Entity = %s' % (t.info.name, t.info.entityName)
        if state != 'success':
            raise Exception(desc)
        return True



#if __name__ == '__main__':
#    print 'Enter password :'
#    pwd = sys.stdin.readline().strip()
#    node_proxy = Node('hostname'='192.168.12.101', 'ssh_port'=22, 'username'='root', 'password'=pwd, 'isRemote'=True)
#    vmm = VMWVMM(node_proxy)
#    config = {}
#    config['platform'] = 'vmw'
#    config['hda'] = '/vm_disks/fc-7.qcow2'
#    config['m'] = 512
#    config['name'] = 'fc-7'
#    config['vnc'] = ':5'
#    import pprint
#    print 'sys.argv',
#    print pprint.pprint(sys.argv)
#    if len(sys.argv) > 1 and sys.argv[1] == 'start':
#        vmm.start(config)
#    doms = vmm.get_vms()
#    for id in doms.keys():
#        print doms[id]
#    print 'enter pid '
#    pid = sys.stdin.readline().strip()
#    if pid.isdigit():
#        pid.isdigit()
#        pid = int(pid)
#        print 'pausing',
#        print pid
#        vmm.pause(pid)
#        print 'paused.'
#        sys.stdin.readline()
#        print 'continue',
#        print pid
#        vmm.resume(pid)
#        print 'resumed.'
#        sys.stdin.readline()
#        print 'saving snapshot x'
#        vmm.save(id, 'x')
#        print 'saved vm x'
#        sys.stdin.readline()
#        print 'restoring snapshot x'
#        vmm.load_vm(id, 'x')
#        print 'restored vm x'
#        sys.stdin.readline()
#        print 'quiting vm'
#        vmm.quit_vm(id)
#        print 'vm quit'
#    else:
#        pid.isdigit()
#        print 'Invalid PID'
#    sys.exit(0)
