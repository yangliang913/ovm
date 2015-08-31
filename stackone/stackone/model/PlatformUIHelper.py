class PlatformUIHelper():
    def __init__(self, ui_context, platform_config):
        self.ui_context = ui_context
        self.platform_config = platform_config
        self.manager = self.ui_context['manager']
        self.client_config = self.ui_context['client_config']
        self.left_nav = self.ui_context['left_nav']

    def show_add_server_dialog(self, mode, group_name, platform, existing_node=None, parentwin=None):
        raise Exception('show_add_node_dialog Not implemted for %s', platform)

    def get_vm_settings_dialog(self, mode, ctx, mainwin):
        raise Exception('get_vm_settings_dialog Not implemted.')

    def get_vm_info_helper(self):
        return None



