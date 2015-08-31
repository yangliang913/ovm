import os
from stackone.model.Platform import Platform
from KVMDomain import KVMConfig
from KVMNodeFactory import KVMNodeFactory
class KVMPlatform(Platform):
	@classmethod
	def get_default_location(cls):
		return __file__
	def __init__(self, platform, client_config):
		Platform.__init__(self, platform, client_config)

	def init(self):
		Platform.init(self)

	def detectPlatform(self, managed_node):
		return managed_node.node_proxy.file_exists('/dev/kvm')

	def runPrereqs(self, managed_node):
		kvm_enabled = managed_node.node_proxy.file_exists('/dev/kvm')
		kvm_access = managed_node.node_proxy.file_is_writable('/dev/kvm')
		if not kvm_enabled:
			return (False, ['KVM not enabled. Can not find /dev/kvm'])
		if not kvm_access:
			return (False, ['You do not have permission to manage VMs via KVM. Try running as root.'])
		return (True, [])

	def get_node_factory(self):
		return KVMNodeFactory()

	def create_vm_config(self, node=None, filename=None, config=None):
		return KVMConfig(node, filename, config)



