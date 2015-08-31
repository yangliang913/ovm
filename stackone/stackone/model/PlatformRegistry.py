import os
from stackone.core.utils.utils import read_python_conf, get_path
import pprint
class PlatformRegistry():
    base_path = 'stackone/core/platforms'
    module_base = 'stackone.core.platforms.'
    def __init__(self, client_config, ui_context):
        self.platforms = {}
        self.platform_config = {}
        self.platform_objects = {}
        self.node_factories = None
        self.ui_helpers = {}
        self.web_helpers = {}
        self.ui_context = ui_context
        self.client_config = client_config
        (p, reg_file) = get_path('registry', [self.base_path])
        reg_map = read_python_conf(reg_file)
        if reg_map.has_key('platforms'):
            self.platforms = reg_map['platforms']
        else:
            msg = 'Error : Invalid registry file %s.' % reg_file
            print msg

        for plat,info in self.platforms.iteritems():
            dir = info['directory']
            name = info['name']
            r_dir = os.path.join(p, dir)
            r_file = os.path.join(r_dir, 'registry')
            r_map = read_python_conf(r_file)
            self.platform_config[plat] = r_map

        for plat, info in self.platform_config.iteritems():
            platform_class = info['config']['platform_class']
            platform_module = info['config']['platform_module']
            instantiate_code = 'from %s import %s; platform = %s(plat, self.client_config)' % (platform_module, platform_class, platform_class)
            print instantiate_code
            exec instantiate_code
            self.platform_objects[plat] = platform


    def init_platforms(self, client_config):
        for p in self.platform_objects.itervalues():
            p.init()


    def detect_platforms(self, managed_node):
        platforms = []
        for p,p_obj in self.platform_objects.iteritems():
            res = p_obj.detectPlatform(managed_node)
            if res:
                platforms.append(p)
        return platforms


    def runPrereqs(self, managed_node, plat):
        p_obj = self.platform_objects[plat]
        (res, msgs) = p_obj.runPrereqs(managed_node)
        return (res, msgs)

    def get_platforms(self):
        return self.platforms

    def get_platform_object(self, platform):
        return self.platform_objects[platform]

    def get_node_factory(self, platform):
        if self.node_factories is None:
            self.node_factories = {}

        if self.node_factories.get(platform) is None:
            p_obj = self.get_platform_object(platform)
            self.node_factories[platform] = p_obj.get_node_factory()

        return self.node_factories[platform]


    def get_ui_helper(self, platform):
        if self.ui_helpers.has_key(platform):
            return self.ui_helpers[platform]

        info = self.platform_config[platform]
        helper_module = info['ui_config']['ui_helper_module']
        helper_class = info['ui_config']['ui_helper_class']
        instantiate_code = 'import %s;from %s import %s; helper = %s(self.ui_context, info)' % (helper_module, helper_module, helper_class, helper_class)
        print instantiate_code
        exec instantiate_code
        self.ui_helpers[platform] = helper
        return helper


    def get_web_helper(self, platform):
        if self.web_helpers.has_key(platform):
            return self.web_helpers[platform]
        info = self.platform_config[platform]
        helper_module = info['web_config']['web_helper_module']
        helper_class = info['web_config']['web_helper_class']
        instantiate_code = 'import %s;from %s import %s; helper = %s(info)' % (helper_module, helper_module, helper_class, helper_class)
        print instantiate_code
        exec instantiate_code
        self.web_helpers[platform] = helper
        return helper




