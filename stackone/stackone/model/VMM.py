class VMM():
    __doc__ = ' info about the vmm capabilities and node info as seen by vmm '
    def info(self):
        return {}

    def is_in_error(self):
        return False

    def connect(self):
        pass

    def disconnect(self):
        pass

    def get_vms(self):
        pass

    def save(self, id, filename):
        pass

    def restore(self, filename):
        pass

    def reboot(self, id):
        pass

    def shutdown(self, id):
        pass

    def destroy(self, id):
        pass

    def pause(self, id):
        pass

    def unpause(self, id):
        pass

    def suspend(self, id):
        pass

    def resume(self, id):
        pass

    def migrate(self, id, dst, live, port):
        pass

    def start(self, id):
        pass

    def refresh(self, id):
        pass

    def setVCPUs(self, id, value):
        pass

    def setMem(self, id, value):
        pass
    
    #add 0904
    def setDownVCPUs(self, id, value):
        pass

    def setDownMem(self, id, value):
        pass
        
    def attachDisks(self, id, attach_disk_list):
        pass

    def detachDisks(self, id, detach_disk_list):
        pass



