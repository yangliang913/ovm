from stackone.model import DBSession
from stackone.model.ManagedNode import ManagedNode
from stackone.model.VM import VM
import stackone.core.utils.constants
constants = stackone.core.utils.constants
class PrivilegeOps():
    op_map = {'ADD_STORAGE_DEF': 'ADD_STORAGE_DEF', 'STORAGE_POOL': 'ADD_STORAGE_DEF', 'ADD_NETWORK_DEF': 'ADD_NETWORK_DEF', 'REMOVE_SERVER': 'REMOVE_VM_CONFIG', 'REMOVE_STORAGE_DEF': 'REMOVE_STORAGE_DEF', 'REMOVE_SERVER_POOL': 'REMOVE_SERVER', 'MANAGE_VIRTUAL_NETWORKS': 'ADD_NETWORK_DEF', 'REMOVE_NETWORK_DEF': 'REMOVE_NETWORK_DEF'}
    def __init__(self):
        pass
    @classmethod
    def check_child_privileges(cls, auth, op, ent):
        children = ent.children
        if len(children) == 0:
            return True
        action = cls.op_map[op]
        if not auth.check_privilege(action, children):
            return False
        if op == 'REMOVE_SERVER_POOL':
            for child in children:
                if cls.check_child_privileges(auth, action, child) == False:
                    return False
        return True
    @classmethod
    def get_server_ids(cls, grp_ent):
        node_ents = grp_ent.children
        node_ids = [n.entity_id for n in node_ents]
        return node_ids
    @classmethod
    def get_servers(cls, grp_ent):
        node_ents = grp_ent.children
        node_ids = [n.entity_id for n in node_ents]
        nodes = DBSession.query(ManagedNode).filter(ManagedNode.id.in_(node_ids)).filter(ManagedNode.maintenance == False).all()
        return nodes
    @classmethod
    def get_vm_ids(cls, node_ent):
        dom_ents = node_ent.children
        dom_ids = [n.entity_id for n in dom_ents]
        return dom_ids
    @classmethod
    def get_vms(cls, node_ent):
        dom_ents = node_ent.children
        dom_ids = [n.entity_id for n in dom_ents]
        doms  = DBSession.query(VM).filter(VM.id.in_(dom_ids)).all()
        return doms



