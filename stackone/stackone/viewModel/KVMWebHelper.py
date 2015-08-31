#from stackone.viewModel.helpers.WebVMInfoHelper import WebVMInfoHelper
#class KVMWebHelper():
#	def __init__(self, platform_config):
#		self.platform_config = platform_config
#
#	def get_vm_info_helper(self):
#		return WebVMInfoHelper()
#
#
from stackone.viewModel.helpers.WebVMInfoHelper import WebVMInfoHelper
from stackone.viewModel.helpers.WebNodeInfoHelper import WebNodeInfoHelper
class KVMWebHelper():
	def __init__(self, platform_config):
		self.platform_config = platform_config

	def get_vm_info_helper(self):
		return KVMVMInfoHelper()

	def get_node_info_helper(self):
		return KVMNodeInfoHelper()



class KVMVMInfoHelper(WebVMInfoHelper):
	def __init__(self):
		WebVMInfoHelper.__init__(self)



class KVMNodeInfoHelper(WebNodeInfoHelper):
	def __init__(self):
		WebNodeInfoHelper.__init__(self)
