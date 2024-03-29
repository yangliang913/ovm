import os

from stackone.core.utils.utils import get_platform_defaults, PyConfig
from stackone.core.utils.utils import to_unicode,to_str
from VM import VMConfig

class Platform:

    defaults = None
    @classmethod
    def get_defaults(cls):
        if cls.defaults == None:
            cls.defaults = get_platform_defaults(cls.get_default_location())
        return cls.defaults

    # return directory where platform specific "defaults" file would be found
    @classmethod
    def get_default_location(cls):
        return None


    def __init__(self, platform, client_config):
        self.client_config = client_config
        self.my_platform = platform

    
    def init(self):
        pass

    # Note
    # - Keep the code to minimum. 
    # -- Currently called only for local node
    # -- Assume instance of ManagedNode class. (not platform specific node)
    def detectPlatform(self, managed_node):
        pass
    
    # return if the other necessary elements are in place
    # for managing Xen environment
    # if yes, return (True, []) else (False, [list of prereq missing])
    def runPrereqs(self, managed_node):
        pass

    # return an instance for creating nodes of this type
    def get_node_factory(self):
        return None

    # return a new vm config. VMConfig might be a good starting point.
    def create_vm_config(self,node=None, filename=None,config=None):
        return VMConfig(node, filename,config)

    # return a new image config. PyConfig should work
    def create_image_config(self,node=None, filename=None,config=None):        
        return PyConfig(node, filename,signature = None,config=config)


    # return the template file to be used for importing a particular
    # appliance
    # default implementation has slight xen flavor but should work for
    # most cases.
    def select_vm_template(self, appliance_base, platform,
                           appliance_entry, cfg):
        if appliance_entry.get("is_hvm") and \
            to_str(appliance_entry["is_hvm"]).lower() == "true" :
            f = 'appliance_hvm_conf.template'
        else:
            f = 'appliance_vm_conf.template'

        return os.path.join(appliance_base, platform, f)

    def select_image_conf_template(self, appliance_base, platform,
                                   appliance_entry):
        return os.path.join(appliance_base, platform,
                            'appliance_image_conf.template')

    def select_provisioning_script(self, appliance_base, platform,
                                   appliance_entry):
        return os.path.join(appliance_base, platform,
                            'provision.sh')


    def select_desc_template(self, appliance_base, platform,
                             appliance_entry):
        return os.path.join(appliance_base,platform, 
                            "appliance_desc.template")

    def select_html_desc_template(self, appliance_base, platform,
                             appliance_entry):
        return os.path.join(appliance_base,platform,
                            "appliance_html_desc.template")
    #pass
    def is_auto_discover(self):
        dis = self.get_default('auto_discover')
        if dis:
            return True
        return False
    #pass
    def get_default(self, key):
        dflts = self.get_defaults()
        if dflts:
            dflt = dflts.get('defaults', {})
            return dflt.get(key, None)
        return None
    def get_provisioning_helper(self, op_context=None):
        return None 
    
