from stackone.viewModel.helpers.WebVMInfoHelper import WebVMInfoHelper
class XenWebHelper():
	def __init__(self, platform_config):
		self.platform_config = platform_config
	def get_vm_info_helper(self):
		return XenVMInfoHelper()



class XenVMInfoHelper(WebVMInfoHelper):
	def __init__(self):
		WebVMInfoHelper.__init__(self)


	def get_category_keys(self):
		cat_keys = WebVMInfoHelper.get_category_keys(self)
		boot_base_keys = cat_keys['BOOT']
		xen_boot_keys = [('kernel', 'Kernel'), ('ramdisk', 'Ramdisk'), ('bootloader', 'Bootloader')]
		for ndx in range(0, 3):
			boot_base_keys.insert(ndx, xen_boot_keys[ndx])
		return cat_keys



