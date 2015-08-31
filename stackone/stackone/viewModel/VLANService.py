from stackone.core.utils.utils import to_unicode, to_str, print_traceback
from stackone.model import DBSession
from stackone.model.VLANManager import VLANManager, VLANNetworkInfo
import stackone.core.utils.utils
from stackone.core.utils.constants import *
constants = stackone.core.utils.constants
import logging
import tg
LOGGER = logging.getLogger('stackone.viewModel')

class VLANService():
    #PASSED
    def __init__(self):
        return None

    #PASSED
    def add_vlan_id_pool(self, auth, site_id, name, desc, range, interface, sp_ids, cidr, num_networks):
        VLANManager().add_vlan_id_pool(auth, site_id, name, desc, range, interface, sp_ids, cidr, num_networks)

    #PASSED
    def edit_vlan_id_pool(self, auth, site_id, vlan_id_pool_id, desc, range, sp_ids, name):
        VLANManager().edit_vlan_id_pool(auth, site_id, vlan_id_pool_id, desc, range, sp_ids, name)

    #PASSED
    def remove_vlan_id_pool(self, vlan_id_pool_id):
        VLANManager().remove_vlan_id_pool(vlan_id_pool_id)

    #PASSED
    def get_vlan_id_pool_details(self, vlan_id_pool_id):
        VLANManager().get_vlan_id_pool_details(vlan_id_pool_id)

    #PASSED
    def get_vlan_id_pools(self):
        result = VLANManager().get_vlan_id_pools()
        return result

    #PASSED
    def get_unused_id(self, pool_tag, context):
        result = VLANManager().get_unused_id(pool_tag, context)
        return result

    #PASSED
    def release_id(self, pool_tag, context):
        VLANManager().release_id(pool_tag, context)

    #PASSED
    def get_vlan_id_pool(self, vlan_id_pool_id):
        result = VLANManager().get_vlan_id_pool(vlan_id_pool_id)
        return result

    #PASSED
    @classmethod
    def get_vlan_network_info_by_vlan_id(cls, vlan_id, pool_id):
        return VLANNetworkInfo.get_vlan_network_info_by_vlan_id(vlan_id, pool_id)



