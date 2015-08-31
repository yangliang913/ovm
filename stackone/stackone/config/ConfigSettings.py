import tg
import os
import platform
from stackone.core.utils import constants
from stackone.core.utils.utils import getHexID
from sqlalchemy.schema import Index, Sequence
class ClientConfiguration():
    __doc__ = "\n    Client Configuration info and default values\n\n    check_updates_on_startup = True\n    paramiko_log_file = paramiko.log\n    gnome_vfs_enabled = False\n    html_browser = /usr/bin/yelp\n    log_file = stackone.log\n    enable_log = True\n    enable_paramiko_log = False\n    http_proxy =\n    default_ssh_port = 22\n\n    default_computed_options = ['arch', 'arch_libdir', 'device_model']\n    use_3_0_api = True\n    "
    def __init__(self):
        pass

    def get(self, key):
        value = None
        if key==constants.prop_chk_updates_on_startup:
            value=eval(tg.config.get(key,'True'))

        elif key==constants.prop_enable_paramiko_log:
            value=eval(tg.config.get(key,'False'))

        elif key==constants.prop_paramiko_log_file:
            value=tg.config.get(key,'paramiko.log')

        elif key==constants.prop_gnome_vfs_enabled:
            value=eval(tg.config.get(key,'False'))

        elif key==constants.prop_enable_log:
            value=eval(tg.config.get(key,'True'))
        elif key == constants.prop_log_file:
            value = tg.config.get(key, 'stackone.log')
        elif key == 'html_browser':
            value = tg.config.get(key, '/usr/bin/yelp')
        elif key == constants.prop_default_computed_options:
            value = tg.config.get(key, "['arch', 'arch_libdir', 'device_model']")
        elif key == 'use_3_0_api':
            value = tg.config.get(key, '/usr/bin/yelp')
        elif key == constants.prop_http_proxy:
            value = tg.config.get(key, '')
        elif key == constants.prop_default_ssh_port:
            value = tg.config.get(key, 22)
        elif key == constants.prop_appliance_store:
            value = tg.config.get(key, '/var/cache/stackone/appliance_store/')
            value = os.path.abspath(value)
        elif key == constants.prop_image_store:
            value = '/var/cache/stackone/image_store/'
            value = os.path.abspath(value)
        elif key == constants.prop_log_dir:
            value = '/var/log/stackone/'
            value = os.path.abspath(value)
        elif key == constants.prop_snapshots_dir:
            value = '/var/cache/stackone/vm_snapshots/'
            value = os.path.abspath(value)
        elif key == constants.prop_snapshot_file_ext:
            value = tg.config.get(key, '.snapshot.xm')
        elif key == constants.prop_cache_dir:
            value = '/var/cache/stackone/'
            value = os.path.abspath(value)
        elif key == constants.prop_exec_path:
            value = tg.config.get(key, '$PATH:/usr/sbin')
        elif key == constants.prop_updates_file:
            value = tg.config.get(key, '/var/cache/stackone/updates.xml')
            value = os.path.abspath(value)
        elif key == constants.prop_vnc_host:
            value = tg.config.get(key)
        elif key == constants.prop_vnc_port:
            value = tg.config.get(key)
        elif key == constants.prop_vnc_user:
            value = tg.config.get(key)
        elif key == constants.prop_vnc_password:
            value = tg.config.get(key)
        elif key in (constants.prop_ssh_log_level, constants.ssh_file, constants.prop_ssh_forward_host, constants.prop_ssh_forward_port, constants.prop_ssh_forward_user, constants.prop_ssh_forward_password):
            value = tg.config.get(key)
        elif key in (constants.prop_ssh_tunnel_setup, constants.prop_ssh_forward_key):
            value = eval(tg.config.get(key, 'False'))

        return value




from sqlalchemy import Column, ForeignKey, PickleType
from sqlalchemy.types import *
from sqlalchemy import orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import Index
from stackone.model import DeclarativeBase
from stackone.model.DBHelper import DBHelper
class NodeConfiguration(DeclarativeBase):
    __doc__ = '\n    Class that stores the configuration details for a ManagedServer.\n    '
    __tablename__ = 'node_config'
    id = Column(Unicode(50), primary_key=True)
    node_id = Column(Unicode(50), ForeignKey('managed_nodes.id', ondelete='CASCADE'))
    config = Column(PickleType)
    def __init__(self, node):
        self.id = getHexID()
        self.node_id = node.id
        self.node = node
        self.config = {}
        self._NodeConfiguration__populateDefaultEntries()

    def set(self, key, value=None):
        self.config[key] = value

    def get(self, key):
        return self.config.get(key)

    def _NodeConfiguration__populateDefaultEntries(self):
        base_dir = None
        if not self.node.isRemote:
            base_dir = os.path.expanduser('~/.stackone/')
            if not os.path.exists(base_dir):
                os.mkdir(base_dir)

        client_config = ClientConfiguration()
        if base_dir is not None:
            base = base_dir
            log_dir = os.path.join(base, 'log')
            i_store = os.path.join(base, 'image_store')
            a_store = os.path.join(base, 'appliance_store')
            updates_file = os.path.join(base, 'updates.xml')
        else:
            base = '/var/cache/stackone'
            log_dir = client_config.get(constants.prop_log_dir)
            i_store = client_config.get(constants.prop_image_store)
            a_store = client_config.get(constants.prop_appliance_store)
            updates_file = client_config.get(constants.prop_updates_file)

        self.set(constants.prop_snapshots_dir, client_config.get(constants.prop_snapshots_dir))
        self.set(constants.prop_snapshot_file_ext, client_config.get(constants.prop_snapshot_file_ext))
        self.set(constants.prop_cache_dir, client_config.get(constants.prop_cache_dir))
        self.set(constants.prop_exec_path, client_config.get(constants.prop_exec_path))
        self.set(constants.prop_image_store, i_store)
        self.set(constants.prop_appliance_store, a_store)
        self.set(constants.prop_updates_file, updates_file)
        self.set(constants.prop_log_dir, log_dir)
        if not self.node.isRemote:
            self.set(constants.prop_dom0_kernel, platform.release())


Index('config_nid', NodeConfiguration.node_id)
