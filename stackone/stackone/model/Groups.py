from stackone.model.ManagedNode import ManagedNode
import stackone.core.utils.utils
from stackone.core.utils.utils import to_unicode, to_str, dynamic_map
from stackone.core.utils.utils import getHexID
constants = stackone.core.utils.constants
from stackone.model.DBHelper import DBHelper
from sqlalchemy import Column, PickleType
from sqlalchemy.types import *
from sqlalchemy import orm
from sqlalchemy.orm import relation
from sqlalchemy.schema import Index
from stackone.model import DeclarativeBase, DBSession
from stackone.model.Entity import Entity, EntityType, EntityRelation
from stackone.model.availability import AvailState
import logging
import tg
LOGGER = logging.getLogger('stackone.model')
###
class ServerGroup(DeclarativeBase):
    __tablename__ = 'server_groups'
    
    id = Column(Unicode(50), primary_key=True)
    name = Column(Unicode(255), nullable=False)
    groupVars = Column(PickleType)
    migrate_back = Column(Boolean, default=False)
    use_standby = Column(Boolean, default=True)
    failover = Column(Integer, default=constants.VM_FAILOVER)
    dwm_enabled = Column(Boolean, default=False)
    current_state = relation(AvailState, primaryjoin=id == AvailState.entity_id, foreign_keys=[AvailState.entity_id], uselist=False, cascade='all, delete, delete-orphan')
    type = Column(Unicode(50), default=None)
    __mapper_args__ = {'polymorphic_on': type}
    ###
    def __init__(self, name, node_list=None, group_vars=None):
        self.name = name
        self.id = getHexID(name, [constants.SERVER_POOL])
        self.n_list = {}
        self.groupVars = {}
        self.alloc_policy = SimpleAllocationPolicy(self)
        if node_list is not None:
            self.n_list = node_list
        if group_vars is not None:
            self.groupVars = group_vars
        self.current_state = AvailState(self.id, EntityType.SERVER_POOL, None, AvailState.MONITORING, description=u'New ServerPool')

    ###
    @orm.reconstructor
    def init_on_load(self):
        self.n_list = {}  
        self.alloc_policy = SimpleAllocationPolicy(self)
    
    ###
    def getName(self):
        return self.name
                
    ###
    def getNodeNames(self,auth):
        ent=auth.get_entity(self.id)
        nodes=auth.get_entity_names(to_unicode(constants.MANAGED_NODE),parent=ent)
        return nodes
    
    ###
    def getNodeList(self,auth):
        ent=auth.get_entity(self.id)
        nodelist={}
        if ent is not None:
            child_ents=auth.get_entities(to_unicode(constants.MANAGED_NODE),parent=ent)
            ids = [child_ent.entity_id for child_ent in child_ents]
            nodes= DBHelper().filterby(ManagedNode,[],[ManagedNode.id.in_(ids)])
            for node in nodes:
                nodelist[node.id]=node
        return nodelist

    ###
    def getNode(self,name):
        return self.n_list.get(name)
    ###
    def getGroupVars(self):
        return self.groupVars
    ###
    def is_dwm_enabled(self):
        return self.dwm_enabled
    ###
    def getGroupVarValue(self, var):
        return self.groupVars.get(var)

    ###
    def getAllocationCandidate(self,auth, ctx):
        return self.alloc_policy.getNext(auth,ctx) 
    
    ###
    def get_enabled_policy(self):
        if self.dwm_enabled:
            from stackone.model.DWM import DWM
            return DBSession.query(DWM).filter(DWM.sp_id == self.id).filter(DWM.enabled == True).first()

    ###
    def setGroupVars(self, vars):
        self.groupVars = vars        
        
    ###
    def _addNode(self, node):
        if self.n_list.get(node.hostname) is None:
            self.n_list[node.hostname] = node
        else:
            raise Exception("Node %s already exists." % (node.hostname))


    ###
    def _removeNode(self, name):
        if name in self.getNodeNames():
            del self.n_list[name]
                    
    ###
    def __str__(self):
        return  self.name + "||" + to_str(self.n_list.keys()) + "||" + to_str(self.groupVars.keys())
    
    ###
    def getAllocationCandidateData(self, auth, ctx):
        return self.alloc_policy.getCandidateData(auth,ctx)
    
    ###
    def getAttributeValue(self, name, default):
        ent = DBSession.query(Entity).filter(Entity.entity_id == self.id).first()
        value = default
        for attr in ent.attributes:
            if attr.name == name:
                value = attr.value
        return value
    
    ###
    def getDomAllocationCandidate(self, auth, ctx):
        return self.alloc_policy.getNext(auth,ctx,False)
    
    ###
    def getStandByNode(self, auth, ctx):
        return self.alloc_policy.getNext(auth,ctx,True)
    
    ###
    def get_allocation_candidate(self, auth, dom, node=None, exclude_ids=[]):
        ex_ids = [id for id in exclude_ids]
        policy_ctx = dynamic_map()
        policy_ctx.dom = dom
        policy_ctx.exclude_ids = ex_ids
        if node is not None:
            policy_ctx.node_id = node.id
        new_node = self.getDomAllocationCandidate(auth, policy_ctx)
        return new_node
    
    ###
    def get_peer_node(self, exclude_ids=[]):
        grp_ent = DBSession.query(Entity).filter(Entity.entity_id == self.id).first()
        node_ids = [x.entity_id for x in grp_ent.children]
        from stackone.model.ManagedNode import ManagedNode
        nodes = DBSession.query(ManagedNode).filter(ManagedNode.id.in_(node_ids)).all()
        up_nodes = []
        for node in nodes:
            if node.current_state.avail_state == ManagedNode.UP and node.id not in exclude_ids:
                up_nodes.append(node)
        if len(up_nodes) == 0:
            return None
        return up_nodes[0]
    #pass
    def get_platform(self):
        platform = self.type
        if platform:
            return platform
        return constants.GENERIC
    
    ###
    def get_standby_nodes(self):
        standby_nodes = []
        try:
            grp_ent = DBSession.query(Entity).filter(Entity.entity_id == self.id).first()
            node_ids = [x.entity_id for x in grp_ent.children]
            from stackone.model.ManagedNode import ManagedNode
            standby_nodes = DBSession.query(ManagedNode).filter(ManagedNode.id.in_(node_ids)).filter(ManagedNode.standby_status == ManagedNode.STANDBY).all()
        except Exception,e:
            import traceback
            traceback.print_exc()
        return standby_nodes
    
    ###
    def is_migrate_back(self):
        return self.migrate_back
    #tianfeng
    @classmethod
    def get_server_pool(cls,id):
        server_pool = None
        server_pool = DBSession.query(cls).filter(cls.id == id).first()
        return server_pool
    @classmethod
    def get_spl_pltfrms_sp(cls):
        spl_ltfrms = [constants.VMWARE,constants.VCENTER]
        try:
            spl_ltfrms = eval(tg.config.get('SPECIAL_PLATFORMS'))
        except Exception,ex:
            print ex
        vmw_node_idts = DBSession.query(ManagedNode.id).filter(ManagedNode.type.in_(spl_ltfrms)).all()
        vmw_node_ids = [x[0] for x in vmw_node_idts]
        vmw_sp_idts = DBSession.query(EntityRelation.src_id).filter(EntityRelation.dest_id.in_(vmw_node_ids)).filter(EntityRelation.relation == 'Children').all()
        vmw_sp_ids = [x[0] for x in vmw_sp_idts]
        return vmw_sp_ids
Index('sp_id',ServerGroup.id)
###
#class SimpleAllocationPolicy:
#    """
#    Policy for determining the best provisioning candidate
#    amongst a group's members. A candidate is selected if
#    it has the minimum:
#        1. VM CPU utilisation
#        2. VM Mem allocation
#        3. number of VM's configured        
#    in that order.
#    """
#    ###
#    def __init__(self, group = None):
#        self._group = group
#    ###
#    def setGroup(self, group):
#        self._group = group
#
#    ###
#    def filter_node(self, node, ctx):
#        try:
#            node.connect()
#        except Exception,e:
#            pass
#        result = node.is_authenticated()
#        if ctx is not None and result and ctx.image:
#            result=False
#            if node.is_image_compatible(ctx.image):
#                free_mem=0
#                try:
#                    free_mem=int(node.get_memory_info().get(constants.key_memory_free,0))
#                except Exception, e:
#                    err=to_str(e).replace("'", " ")
#                    LOGGER.error(err)
#                mem=0
#                try:
#                    vm_config,image_config=ctx.image.get_configs()
#                    mem=int(vm_config['memory'])
#                except Exception, e:
#                    err=to_str(e).replace("'", " ")
#                    LOGGER.error(err)
#                LOGGER.error("Memory required is "+str(mem))
#                LOGGER.error("Available memory in "+node.hostname+" is "+str(free_mem))
#                result = (mem<free_mem)
#        if ctx is not None and result and ctx.dom:
#            result = False
#            if node.is_dom_compatible(ctx.dom):
#                free_mem = 0 
#                try:
#                    free_mem=int(node.get_memory_info().get(constants.key_memory_free,0))
#                except Exception, e:
#                    err=to_str(e).replace("'", " ")
#                    LOGGER.error(err)
#                mem = 0
#                try:
#                    vm_config = ctx.dom.get_config()
#                    mem=int(vm_config['memory'])
#                except Exception, e:
#                    err=to_str(e).replace("'", " ")
#                    LOGGER.error(err)
#                LOGGER.error("Memory required is "+str(mem))
#                LOGGER.error("Available memory in "+node.hostname+" is "+str(free_mem))
#                result = (mem<free_mem)
#        return result
#    ###
#    def getNext(self, auth,ctx,standby=False):
#        server_list = self.getCandidateData(auth, ctx, standby)
#        if server_list:
#            return server_list[5]
#    ###
#    def getCandidateData(self, auth, ctx, standby=False):
#        sp=auth.get_entity(self._group.id)
#        child_ents=auth.get_entities(to_unicode(constants.MANAGED_NODE),parent=sp)
#        if ctx.exclude_ids is not None:
#            ctx.exclude_ids.append(ctx.node_id)
#        else:
#            ctx.exclude_ids = []
#            ctx.exclude_ids.append(ctx.node_id)
#        LOGGER.error('exclude_ids======' + str(ctx.exclude_ids))
#        ids = [child_ent.entity_id for child_ent in child_ents if child_ent.entity_id not in ctx.exclude_ids]
#        nodelist= DBHelper().filterby(ManagedNode,[],[ManagedNode.id.in_(ids)])
#        load_time=self._group.getGroupVarValue("SERVER_LOAD_TIME")
#        try:
#            load_time=int(load_time)
#        except Exception, e:
#            load_time=0
#        list = []
#
#        LOGGER.error("Begining initial placement on "+self._group.name)
#        for n in nodelist:
#            if n.is_maintenance():
#                LOGGER.info('Node %s in Maintenance mode' %n.hostname)
#            LOGGER.info(n.current_state.avail_state,'@@@@@@@@@@@@@@@@@@@@@@@@@@@', n.is_standby(),self.filter_node(n, ctx))
#            LOGGER.info(n.is_maintenance(),'@@@@@@@@@@@@@')
#            if n.is_standby() == standby and self.filter_node(n, ctx):
#                if n.current_state.avail_state == ManagedNode.UP:
#                    if not n.is_maintenance():
#                        metrics=n.get_raw_metrics(load_time)
#                        cpu_info = n.get_cpu_info()
#                        nr_cpus = int(cpu_info.get(constants.key_cpu_count,1))
#                        vcpus=n.get_vcpu_count()
#                        free_mem=int(n.get_memory_info().get(constants.key_memory_free,0))
#                        list.append((metrics['VM_TOTAL_CPU(%)'],
#                            metrics['VM_TOTAL_MEM(%)'],
#                            (vcpus/nr_cpus),
#                            n.get_VM_count(),
#                            -free_mem,
#                            n,
#                            n.hostname))
#        LOGGER.error("Capable nodes:\n "+to_str(list))
#        LOGGER.error("Finishing initial placement on "+self._group.name)
#
#        if len(list) == 0:
#            return None
#        else:
#            return min(list)
#    
class VMWServerGroup(ServerGroup):
    __mapper_args__ = {'polymorphic_identity': u'vcenter'}
    def __init__(self, name):
        ServerGroup.__init__(self, name)

class SimpleAllocationPolicy():
    __doc__ = "\n    Policy for determining the best provisioning candidate\n    amongst a group's members. A candidate is selected if\n    it has the minimum:\n        1. VM CPU utilisation\n        2. VM Mem allocation\n        3. number of VM's configured        \n    in that order.\n    "
    def __init__(self, group=None):
        self._group = group

    def setGroup(self, group):
        self._group = group

    def filter_node(self, node, ctx):
        try:
            node.connect()
        except Exception as e:
            print e
        result = node.is_authenticated()
        if ctx is not None and result and ctx.image:
            result = False
            if node.is_image_compatible(ctx.image):
                free_mem = 0
                try:
                    free_mem = int(node.get_memory_info().get(constants.key_memory_free, 0L))
                except Exception as e:
                    err = to_str(e).replace("'", ' ')
                    LOGGER.error(err)
                mem = 0
                try:
                    vm_config,image_config = ctx.image.get_configs(node.get_platform())
                    mem = int(vm_config['memory'])
                except Exception as e:
                    err = to_str(e).replace("'", ' ')
                    LOGGER.error(err)
                LOGGER.error('Memory required is ' + str(mem))
                LOGGER.error('Available memory in ' + node.hostname + ' is ' + str(free_mem))
                result = mem < free_mem
        if ctx is not None and result and ctx.dom:
            result = False
            if node.is_dom_compatible(ctx.dom):
                free_mem = 0
                try:
                    free_mem = int(node.get_memory_info().get(constants.key_memory_free, 0L))
                except Exception as e:
                    err = to_str(e).replace("'", ' ')
                    LOGGER.error(err)
                mem = 0
                try:
                    vm_config = ctx.dom.get_config()
                    mem = int(vm_config['memory'])
                except Exception as e:
                    err = to_str(e).replace("'", ' ')
                    LOGGER.error(err)
                LOGGER.error('Memory required is ' + str(mem))
                LOGGER.error('Available memory in ' + node.hostname + ' is ' + str(free_mem))
                result = mem < free_mem
        return result

    def getNext(self, auth, ctx, standby=False):
        server_list = self.getCandidateData(auth, ctx, standby)
        if server_list:
            return server_list[5]
        return None
    #tianfeng
    def checkVmLimit(self, node_id, group):
        if node_id:
            concurrent_provision_count = Entity.get_attribute_value(node_id, 'concurrent_provision_count', None)
            if not concurrent_provision_count:
                concurrent_provision_count = self._group.getGroupVarValue('CONCURRENT_PROVISION_COUNT')
                if not concurrent_provision_count:
                    concurrent_provision_count = tg.config.get(constants.CONCURRENT_PROVISION_COUNT)
            avails = DBSession.query(AvailState).filter(AvailState.entity_id == node_id).first()
            used_count = int(avails.used_count)
            ccpc = 3
            try:
                ccpc = int(concurrent_provision_count)
            except Exception as e:
                print 'Exception:',
                print e
            if ccpc <= used_count:
                return False
            return True


    def getCandidateData(self, auth, ctx, standby=False):
        sp = auth.get_entity(self._group.id)
        child_ents = auth.get_entities(to_unicode(constants.MANAGED_NODE), parent=sp)
        if ctx.exclude_ids is not None:
            ctx.exclude_ids.append(ctx.node_id)
        else:
            ctx.exclude_ids = []
            ctx.exclude_ids.append(ctx.node_id)
        LOGGER.error('exclude_ids======' + str(ctx.exclude_ids))
        ids = [child_ent.entity_id for child_ent in child_ents if child_ent.entity_id not in ctx.exclude_ids]
        nodelist = DBHelper().filterby(ManagedNode,[], [ManagedNode.id.in_(ids)])
        load_time = self._group.getGroupVarValue('SERVER_LOAD_TIME')
        try:
            load_time = int(load_time)
        except Exception as e:
            load_time = 0
        list = []
        LOGGER.error('Begining initial placement on ' + self._group.name)
        for n in nodelist:
            if n.is_maintenance():
                LOGGER.info('Node %s in Maintenance mode' % n.hostname)
            count_check = self.checkVmLimit(n.id, self._group)
            if count_check == True:
                if n.is_standby() == standby and self.filter_node(n,ctx) and n.current_state.avail_state == ManagedNode.UP and not n.is_maintenance():
                    metrics = n.get_raw_metrics(load_time)
                    cpu_info = n.get_cpu_info()
                    nr_cpus = int(cpu_info.get(constants.key_cpu_count , 1))
                    vcpus = n.get_vcpu_count()
                    free_mem = int(n.get_memory_info().get(constants.key_memory_free,0))
                    list.append((metrics['VM_TOTAL_CPU(%)'], metrics['VM_TOTAL_MEM(%)'], vcpus / nr_cpus, n.get_VM_count(), -free_mem, n, n.hostname))
        LOGGER.error('Capable nodes:\n ' + to_str(list))
        LOGGER.error('Finishing initial placement on ' + self._group.name)
        if len(list) == 0:
            return None
        return min(list)
