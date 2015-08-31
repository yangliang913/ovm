import os
from stackone.model.Platform import Platform
class VMWPlatform(Platform):
    @classmethod
    def get_default_location(cls):
        return __file__
    def __init__(self, platform, client_config):
        Platform.__init__(self, platform, client_config)

    def init(self):
        Platform.init(self)

    def detectPlatform(self, managed_node):
        return True

    def runPrereqs(self, managed_node):
        return (True, [])

    def get_node_factory(self):
        from VMWNodeFactory import VMWNodeFactory
        return VMWNodeFactory()

    def create_vm_config(self, node=None, filename=None, config=None):
        from VMWDomain import VMWConfig
        return VMWConfig(node, filename, config)

    def get_provisioning_helper(self, op_context=None):
        from VMWHelpers import VMWProvisioningHelper
        return VMWProvisioningHelper()

    def create_vcenter_vm_config(self, node=None, filename=None, config=None):
        from VMWDomain import VcenterConfig
        return VcenterConfig(node=node, filename=filename, config=config)

    def create_vcenter_image_config(self, vm_config, filename=None, config=None):
        return vm_config.create_image_config(filename=filename, config=config)



