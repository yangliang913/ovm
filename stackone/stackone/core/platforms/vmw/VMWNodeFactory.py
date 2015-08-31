from stackone.model.VNodeFactory import VNodeFactory
from stackone.core.utils.utils import get_prop
from stackone.core.utils.utils import to_unicode, to_str
from stackone.core.utils.constants import *
from VMWNode import VMWNode
class VMWNodeFactory(VNodeFactory):
    def __init__(self):
        VNodeFactory.__init__(self)

    def create_node(self, **props):
        keys = props.keys()
        missing = []
        for k in ('hostname',):
            if k not in keys:
                missing.append(k)
        if len(missing) > 0:
            raise Exception('Missing properties ' + to_str(missing))
        platform = props['platform']
        if platform != 'vmw':
            raise Exception('Wrong platform %s found, while expecting %s' % (platform, 'vmw'))
#        if self.config:
#            self.config
        external_manager_id = get_prop(props, 'external_manager_id')
        hostname = get_prop(props, 'hostname')
        username = get_prop(props, 'username', 'root')
        password = get_prop(props, 'password')
        use_keys = get_prop(props, 'use_keys')
        address = get_prop(props, 'address')
        is_remote = get_prop(props, 'is_remote', True)
        ssh_port = get_prop(props, 'ssh_port', 22)
        migration_port = get_prop(props, 'migration_port', 8002)
        node = VMWNode(hostname=hostname, username=username, password=password, isRemote=is_remote, ssh_port=ssh_port, migration_port=migration_port, helper=None, use_keys=use_keys, address=address, external_manager_id=external_manager_id)
        return node

    def create_node_from_repos(self, **props):
        key_map = {'login': 'username'}
        new_props = {}
        keys = key_map.keys()
        for prop,val in props.iteritems():
            if prop in keys:
                new_props[key_map[prop]] = props[prop]
            else:
                new_props[prop] = props[prop]
        for prop,val in new_props.iteritems():
            if prop in ('ssh_port', 'tcp_port', 'migration_port'):
                new_props[prop] = int(val)
            if prop in ('is_remote', 'use_keys'):
                new_props[prop] = eval(val)
        return self.create_node(**new_props)

    def get_props_for_repos(self, node):
        print 'Hostname %s' % node.hostname
        props = {prop_hostname: node.hostname, prop_login: node.username, prop_ssh_port: to_str(node.ssh_port), prop_migration_port: to_str(node.migration_port), prop_isRemote: to_str(node.isRemote), prop_use_keys: to_str(node.use_keys), prop_address: node.address, prop_platform: node.platform}
        if props is not None:
            props.update(VNodeFactory.get_props_for_repos(self, node))
        return props

    def update_node(self, node, **props):
        platform = props['platform']
        if platform != 'vmw':
            raise Exception('Wrong platform %s found, while expecting %s' % (platform, 'vmw'))
        hostname = get_prop(props, 'hostname')
        username = get_prop(props, 'username', 'root')
        password = get_prop(props, 'password')
        use_keys = get_prop(props, 'use_keys')
        address = get_prop(props, 'address')
        is_remote = get_prop(props, 'is_remote', True)
        ssh_port = get_prop(props, 'ssh_port', 22)
        migration_port = get_prop(props, 'migration_port', 8002)
        node.platform = platform
        node.username = username
        node.password = password
        node.use_keys = use_keys
        node.address = address
        node.is_remote = is_remote
        node.ssh_port = ssh_port
        node.migration_port = migration_port
        node.set_node_credentials('', ssh_port=ssh_port, username=username, password=password, use_keys=use_keys)
        return node



