from stackone.core.utils import utils
from stackone.core.utils.utils import to_unicode, to_str
from stackone.core.utils.constants import *
class NodeInfoVO():
    def __init__(self, node, auto_disc=False):
        self.node = node
        self.auto_disc = auto_disc

    def toXml(self, xml):
        node_info_xml = xml.createElement('NodeInfo')
        credentials = self.node.get_credentials()
        node_info_xml.setAttribute('hostname', self.node.hostname)
        node_info_xml.setAttribute('platform', self.node.platform)
        node_info_xml.setAttribute('username', credentials['username'])
        node_info_xml.setAttribute('configdir', self.node.get_config_dir())
        node_info_xml.setAttribute('isRemote', to_str(self.node.is_remote()))
        node_info_xml.setAttribute('snapshotdir', self.node.config.get(prop_snapshots_dir))
        if self.node.platform == 'xen':
            node_info_xml.setAttribute('xen_port', to_str(self.node.tcp_port))
            node_info_xml.setAttribute('protocol', self.node.protocol)
        node_info_xml.setAttribute('migration_port', to_str(self.node.migration_port))
        node_info_xml.setAttribute('use_keys', to_str(credentials['use_keys']))
        node_info_xml.setAttribute('ssh_port', to_str(credentials['ssh_port']))
        node_info_xml.setAttribute('address', self.node.address)
        node_info_xml.setAttribute('auto_discover', to_str(self.auto_disc))
        return node_info_xml

    def toJson(self):
        if self.node is None:
            return {}
        node_info = {}
        credentials = self.node.get_credentials()
        node_info['hostname'] = self.node.hostname
        node_info['platform'] = self.node.platform
        node_info['username'] = credentials['username']
        node_info['configdir'] = self.node.get_config_dir()
        node_info['isRemote'] = to_str(self.node.is_remote())
        node_info['snapshotdir'] = self.node.config.get(prop_snapshots_dir)
        if self.node.platform == 'xen':
            node_info['xen_port'] = to_str(self.node.tcp_port)
            node_info['protocol'] = self.node.protocol
        node_info['migration_port'] = to_str(self.node.migration_port)
        node_info['use_keys'] = to_str(credentials['use_keys'])
        node_info['ssh_port'] = to_str(credentials['ssh_port'])
        node_info['address'] = self.node.address
        node_info['is_standby'] = self.node.is_standby()
        node_info['auto_discover'] = self.auto_disc
        return node_info





