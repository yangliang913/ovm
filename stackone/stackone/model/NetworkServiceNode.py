from stackone.model.ManagedNode import ManagedNode
from stackone.core.utils.utils import get_prop
class NetworkServiceNode(ManagedNode):
    __mapper_args__ = {'polymorphic_identity': u'network_service'}
    def update_node(self, **props):
        hostname = get_prop(props, 'hostname')
        username = get_prop(props, 'username', 'root')
        password = get_prop(props, 'password')
        address = get_prop(props, 'address')
        ssh_port = get_prop(props, 'ssh_port', 22)

        use_keys = password == None
        if password == None:
            use_keys = hostname != 'localhost'
        else:
            use_keys = password == None
        is_remote = hostname != 'localhost'
        self.hostname = hostname
        self.username = username
        self.password = password
        self.use_keys = use_keys
        self.address = address
        self.is_remote = is_remote
        self.ssh_port = ssh_port
        self.set_node_credentials('', ssh_port = ssh_port, username = username, password = password, use_keys = use_keys)
        return None



class CMSNetworkServiceNode(NetworkServiceNode):
    __mapper_args__ = {'polymorphic_identity': u'cms_network_service'}

__author__ = 'root'
__date__ = '$24 Sep, 2011 4:42:40 PM$'
if __name__ == '__main__':
    print 'Hello'
