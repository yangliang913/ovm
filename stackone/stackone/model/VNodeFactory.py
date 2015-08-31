from stackone.core.utils.constants import *
from stackone.core.utils.utils import to_unicode, to_str
class VNodeFactory():
    def __init__(self):
        self.config = None
        return None

    def create_node(self, **kwargs):
        pass

    def create_node_from_repos(self, **kwargs):
        pass

    def get_props_for_repos(self, node):
        props = { prop_domfiles : to_str(node.get_managed_domfiles())}
        return props


