from sqlalchemy.schema import Index, Sequence
from stackone.model import DeclarativeBase, DBSession, Entity
from stackone.model.events import Event
from stackone.core.utils.utils import to_unicode, to_str, getHexID, notify_node_down, p_task_timing_start, p_task_timing_end
from sqlalchemy.schema import Index
from sqlalchemy import Column, Integer, String, Table, func
from sqlalchemy import DateTime, PickleType, Boolean, Unicode, Text
from datetime import datetime
import logging
import transaction
import time
import traceback
import stackone.core.utils.constants
constants = stackone.core.utils.constants
logger = logging.getLogger('stackone.availability.model')
ImmutablePickleType = PickleType(mutable=False)
availability_event_type = u'Availability'

###
def update_avail(node, new_state, monit_state, timestamp, reason, logger, update=True, auth=None):
    sv_point = transaction.savepoint()
    try:
        strt = p_task_timing_start(logger, "UpdateAvailability", node.id, log_level="DEBUG")
        node.current_state.avail_state = new_state
        node.current_state.timestamp = timestamp
        node.current_state.description = reason
        avh=DBSession.query(AvailHistory).filter(AvailHistory.entity_id==node.id).\
            order_by(AvailHistory.timestamp.desc()).first()
        if avh is not None:
            avh.endtime=timestamp
            time_diff=timestamp-avh.timestamp
            avh.period=time_diff.days*24*60+time_diff.seconds/60
            DBSession.add(avh)
        #insert availability history
        ah = AvailHistory(node.id, new_state, monit_state, timestamp, reason)
        DBSession.add(ah)
        DBSession.add(node)
        if update==True:
            487
            ev_contents = {'state':new_state}
            ev = AvailabilityEvent(node.id, ev_contents, timestamp)
            DBSession.add(ev)
            ent = DBSession.query(Entity).filter(Entity.entity_id==node.id).first()
            from stackone.model.ManagedNode import ManagedNode
            if ent.type.name == constants.MANAGED_NODE and new_state == ManagedNode.DOWN:
                if node.is_maintenance():
                    logger.info('Node:%s is in Maintenance mode' %node.hostname)
                else:
                    notify_node_down(ent,reason)
    except Exception, e:
        import traceback
        traceback.print_exc()
        logger.error(e)
        sv_point.rollback()

    p_task_timing_end(logger, strt)   

###
class AvailState(DeclarativeBase):
    MONITORING = 1
    NOT_MONITORING = 0
    __tablename__ = 'avail_current'
    
    entity_id = Column(Unicode(50), primary_key=True)
    entity_type = Column(Integer)
    avail_state = Column(Integer)
    monit_state = Column(Integer)
    transient_state = Column(Integer)
    transient_state_time = Column(DateTime)
    owner = Column(Unicode(255))
    timestamp = Column(DateTime)
    description = Column(Unicode(256))
    cloud_entity_id = Column(Unicode(50))
    used_count = Column(Integer, default=0)
    ###
    def __init__(self, entity_id, type_id, avail_state, monit_state, timestamp=None, description=None):
        self.entity_id = entity_id
        self.entity_type = type_id
        self.avail_state = avail_state
        self.monit_state = monit_state
        if timestamp is None:
            timestamp = datetime.now()
        self.timestamp = timestamp
        self.description = description
        self.transient_state = None
        self.owner = constants.CORE

    ###
    def __repr__(self):
        return 'Current availability State of %s is %s since %s' % (self.entity_id, self.avail_state, self.timestamp)
    
    ###
    @classmethod
    def get_status(cls, entity_ids):
        result = DBSession.query(cls.avail_state, func.count(cls.entity_id)).filter(cls.entity_id.in_(entity_ids)).group_by(cls.avail_state).all()
        return result


###
class AvailHistory(DeclarativeBase):
    __tablename__ = 'avail_history'
    
    id = Column(Unicode(50), primary_key=True)
    entity_id = Column(Unicode(50))
    state = Column(Integer)
    timestamp = Column(DateTime)
    monit_state = Column(Integer)
    endtime = Column(DateTime)
    period = Column(Integer)
    description = Column(Unicode(256))
    
    ###
    def __init__(self, entity_id, state, monit_state, timestamp, description, endtime=None, period=None):
        self.id = getHexID()
        self.entity_id = entity_id
        self.state = state
        self.timestamp = timestamp
        self.description = description
        self.monit_state = monit_state
        self.endtime = endtime
        self.period = period

    ###
    def __repr__(self):
        return 'Availability State of %s at time %s was %s' % (self.entity_id, self.timestamp, self.state)



Index('ah_eid_st_time', AvailHistory.entity_id, AvailHistory.state, AvailHistory.timestamp)
###
class StateTransition(DeclarativeBase):
    __tablename__ = 'state_transitions'
    
    id = Column(Integer, Sequence('st_trs_id_seq'), primary_key=True)
    entity_type = Column(Integer)
    current_owner = Column(Unicode(50))
    current_state = Column(Integer)
    request_entity_type = Column(Integer)
    requested_state = Column(Integer)
    requester = Column(Unicode(50))
    result = Column(Boolean)
    desc = Column('description', Text)
    lockmode = 'update'
    ###
    def __init__(self, type, current_state, requested_state, result, current_owner, requester, request_entity_type, desc=None):
        self.entity_type = type
        self.current_owner = current_owner
        self.current_state = current_state
        self.requester = requester
        self.requested_state = requested_state
        self.request_entity_type = request_entity_type
        self.result = result
        self.desc = desc

    ###
    @classmethod
    def is_allowed(cls, entity_id, requested_state, requester, entity_ids=[], wait_time=0, change=True):
        if requested_state is None and change == True:
            return cls.set_none_state(entity_id, requester)
        input_entityids = []
        input_entityids.append(entity_id)
        input_entityids.extend(entity_ids)
        transaction.begin()
        try:
            allowed = False
            state_dict = {}
            state_dict['msg'] = ''
            state_dict['requested_state'] = requested_state
            state_dict['requester'] = requester
            entity = DBSession.query(Entity).filter(Entity.entity_id == entity_id).first()
            if entity is None:
                msg = 'Entity can not be found for ' + entity_id
                logger.error(msg)
                state_dict['msg'] = msg
                return (False, state_dict)
            avail_states = DBSession.query(AvailState).with_lockmode(cls.lockmode).filter(AvailState.entity_id.in_(input_entityids)).order_by(AvailState.entity_type.asc()).order_by(AvailState.entity_id.asc()).order_by(AvailState.owner.asc()).all()
            avail = None
            for avail_state in avail_states:
                if avail_state.entity_id == entity_id:
                    avail = avail_state
                state_dict[avail_state.entity_id + '_avail_state'] = avail_state.avail_state
                state_dict[avail_state.entity_id + '_transient_state'] = avail_state.transient_state
                state_dict[avail_state.entity_id + '_owner'] = avail_state.owner
                state_dict[avail_state.entity_id + '_entity_type'] = str(avail_state.entity_type)
                transition = DBSession.query(cls).filter(cls.entity_type == avail_state.entity_type).filter(cls.current_state == avail_state.avail_state).filter(cls.requester == to_unicode(requester)).filter(cls.requested_state == to_unicode(requested_state)).filter(cls.request_entity_type == entity.type_id).first()
                ent_name = Entity.getEntityName(avail_state.entity_id)
                if transition is None:
                    state = to_str(avail_state.entity_type) + '_' + to_str(avail_state.avail_state)
                    msg = 'Current state of ' + ent_name + ' is ' + constants.ENTITY_STATES[state] + '. Can not perform ' + constants.ENTITY_STATES[to_str(requested_state)] + ' on ' + entity.name + '.'
                    state_dict['msg'] = msg
                    allowed = False
                else:
                    allowed = transition.result
                    state_dict['msg'] = transition.desc
                
                if allowed == False:
                    break
                    
                if avail_state.transient_state is None or avail_state.transient_state == '':
                    allowed = True
                    continue
                    
                transition = DBSession.query(cls).filter(cls.entity_type == avail_state.entity_type).filter(cls.current_state == avail_state.transient_state).filter(cls.current_owner == avail_state.owner).filter(cls.requester == to_unicode(requester)).filter(cls.requested_state == to_unicode(requested_state)).filter(cls.request_entity_type == entity.type_id).first()
                if transition is None:
                    msg = constants.ENTITY_STATES[to_str(avail_state.transient_state)] + ' operation is in progress on ' + ent_name + '. Can not perform ' + constants.ENTITY_STATES[to_str(requested_state)] + ' on ' + entity.name + '.'
                    state_dict['msg'] = msg
                    allowed = False
                else:
                    allowed = transition.result
                    state_dict['msg'] = transition.desc
                
                if allowed == False:
                    break
                    
            if allowed == True and change == True:
                cls.set_transient_state(avail, requested_state, requester)
        except Exception as e:
            traceback.print_exc()
            logger.error(to_str(e))
            state_dict['msg'] = to_str(e)
            transaction.commit()
            return (False, state_dict)
        transaction.commit()
        if allowed == False and wait_time > 0:
            allowed,state_dict = cls.wait_check(entity_id, requested_state, requester, input_entityids, state_dict, wait_time, change)
        return (allowed, state_dict)
    
    ###
    @classmethod
    def set_none_state(cls, entity_id, requester):
        transaction.begin()
        result = False
        state_dict = {}
        state_dict['msg'] = ''
        try:
            avails = DBSession.query(AvailState).with_lockmode(cls.lockmode).filter(AvailState.entity_id == entity_id).all()
            if avails:
                avail = avails[0]
                state_dict['avail_state'] = avail.avail_state
                state_dict['transient_state'] = avail.transient_state
                state_dict['owner'] = avail.owner
                if avail.owner == requester:
                    avail.transient_state = None
                    avail.transient_state_time = datetime.now()
                    result = True
        except Exception as e:
            traceback.print_exc()
            logger.error(to_str(e))
            state_dict['msg'] = to_str(e)
        transaction.commit()
        return (result, state_dict)
    
    ###
    @classmethod
    def set_transient_state(cls, avail_state, transient_state, owner):
        avail_state.transient_state = transient_state
        avail_state.owner = to_unicode(owner)
        avail_state.transient_state_time = datetime.now()
    
    ###
    @classmethod
    def wait_check(cls, entity_id, requested_state, requester, entity_ids, state_dict, wait_time, change):
        for t in range(0, wait_time):
            time.sleep(1)
            allowed,state_dict = cls.is_allowed(entity_id, requested_state, requester, entity_ids, wait_time=0, change =change)
            if allowed == True:
                return (allowed, state_dict)
        return (allowed, state_dict)

    
Index('st_et_co_cs_req', StateTransition.entity_type, StateTransition.current_state, StateTransition.current_owner, StateTransition.requested_state, StateTransition.requester, StateTransition.request_entity_type)
###
class VMStateHistory(DeclarativeBase):
    __tablename__ = 'vm_state_history'
    
    id = Column(Unicode(255), primary_key=True)
    node_id = Column(Unicode(50))
    vm_id = Column(Unicode(50))
    avail_state = Column(Integer)
    monit_state = Column(Integer)
    transient_state = Column(Unicode(255))
    transient_state_time = Column(DateTime)
    owner = Column(Unicode(255))
    timestamp = Column(DateTime)
    
    ###
    def __init__(self, node_id, vm_id, avail_state, monit_state, transient_state, transient_state_time, owner):
        self.id = getHexID()
        self.node_id = node_id
        self.vm_id = vm_id
        self.avail_state = avail_state
        self.monit_state = monit_state
        self.transient_state = transient_state
        self.transient_state_time = transient_state_time
        self.owner = owner
        self.timestamp = datetime.now()
    
    ###
    @classmethod
    def add_vm_states(cls, node_id):
        try:
            node_ent = DBSession.query(Entity).filter(Entity.entity_id == node_id).first()
            if node_ent is None:
                msg = 'Entity can not be found for ' + node_id
                logger.error(msg)
                raise Exception(msg)
            vm_ents = node_ent.children
            vm_ids = [vm.entity_id for vm in vm_ents]
            transaction.begin()
            avail_states = DBSession.query(AvailState).filter(AvailState.entity_id.in_(vm_ids)).all()
            from stackone.model.VM import VM
            vshs,avails = [],[]
            for avail in avail_states:
                vsh = DBSession.query(cls).filter(cls.node_id == node_id).filter(cls.vm_id == avail.entity_id).first()
                if vsh is None:
                    vsh = VMStateHistory(node_id,avail.entity_id,avail.avail_state,avail.monit_state,avail.transient_state,avail.transient_state_time,avail.owner)
                else:
                    vsh.avail_state = avail.avail_state  
                    vsh.monit_state = avail.monit_state
                    vsh.transient_state = avail.transient_state
                    vsh.transient_state_time = avail.transient_state_time
                    vsh.owner = avail.owner
                    vsh.timestamp = datetime.now()
                
                avail.avail_state = VM.SHUTDOWN
                vshs.append(vsh)
                avails.append(avail)
                
            DBSession.add_all(vshs)
            DBSession.add_all(avails)
            transaction.commit()
        except Exception as e:
            logger.error(to_str(e))
            DBSession.rollback()
            transaction.begin()
            traceback.print_exc()
            raise e
    
    ###
    @classmethod
    def get_vm_state(cls, node_id, vm_id):
        vsh = DBSession.query(cls).filter(cls.node_id == node_id).filter(cls.vm_id == vm_id).first()
        return vsh
    
    ###
    @classmethod
    def get_vm_states(cls, node_id):
        from stackone.model.VM import VM
        vshs = DBSession.query(cls).join((VM, VM.id == cls.vm_id)).filter(cls.node_id == node_id).order_by(VM.ha_priority.desc()).all()
        return vshs
    
    ###
    @classmethod
    def remove_node_states(cls, node_id):
        try:
            transaction.begin()
            deleted = DBSession.query(cls).filter(cls.node_id == node_id).delete()
            transaction.commit()
            return deleted
        except Exception as e:
            logger.error(to_str(e))
            traceback.print_exc()
    
    ###
    @classmethod
    def remove_vm_states(cls, node_id, vm_id, all=False):
        try:
            transaction.begin()
            query = DBSession.query(cls).filter(cls.vm_id == vm_id)
            if all == False:
                vsh = DBSession.query(cls).filter(cls.node_id == node_id).filter(cls.vm_id == vm_id).first()
                query = query.filter(cls.timestamp >= vsh.timestamp)
            deleted = query.delete()
            transaction.commit()
            return deleted
        except Exception as e:
            logger.error(to_str(e))
            DBSession.rollback()
            transaction.begin()
            traceback.print_exc()
            raise e


Index('vsh_nid_vid', VMStateHistory.node_id, VMStateHistory.vm_id)
###
class AvailabilityEvent(Event):
    __mapper_args__ = {'polymorphic_identity': u'Availability'}

    ###
    def get_state(self):
        return self.get('state')
    
    ###
    def get_timestamp(self):
        return self.timestamp



