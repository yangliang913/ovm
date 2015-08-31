from stackone.model import DeclarativeBase, Entity, EntityType, DBSession
from stackone.model.DBHelper import DBHelper
from stackone.model.availability import AvailState
from stackone.model.ManagedNode import ManagedNode
from stackone.model.Metrics import MetricsService
from stackone.model.VM import VM
from stackone.model.Groups import ServerGroup
from stackone.core.ha.ha_register import HAEvent
from stackone.core.ha.ha_fence import HAEntityResource
from sqlalchemy.types import Integer, Unicode, String, DateTime, Float, Boolean, Numeric
from sqlalchemy.orm import mapper, relation, sessionmaker, column_property
from sqlalchemy.schema import Index, Sequence
from sqlalchemy.sql.expression import or_, not_
from decimal import Decimal
from sqlalchemy import Table, ForeignKey, Column, PickleType
import stackone.core.utils.utils
utils = stackone.core.utils.utils
constants = stackone.core.utils.constants
from datetime import datetime, timedelta
import transaction
import traceback
import tg
import time
import os
from stackone.core.utils.utils import to_unicode, to_str, get_minute_string, copyToRemote
from stackone.model.services import Task
from stackone.core.utils.utils import getHexID
from stackone.model.availability import StateTransition
import copy
import pprint
import logging
LOGGER = logging.getLogger('stackone.model.DWM')
class DWM(DeclarativeBase):
    __tablename__ = 'dwm_policies'
    id = Column(Unicode(50), primary_key=True)
    sp_id = Column(Unicode(255))
    policy = Column(Unicode(255))
    threshold = Column(Integer)
    upper_threshold = Column(Integer)
    frequency = Column(Integer)
    data_period = Column(Integer)
    interval_task_id = Column(Integer)
    calendar_task_ids = Column(PickleType)
    enabled = Column(Boolean)
    def __init__(self, sp_id, policy, threshold, frequency, data_period):
        self.id = getHexID()
        self.sp_id = sp_id
        self.policy = policy
        self.threshold = threshold
        self.frequency = frequency
        self.data_period = data_period

    def get_dwm_task(self):
        interval_task = DBSession.query(Task).filter(Task.task_id == self.interval_task_id).first()
        return interval_task

    def is_active(self):
        spdwm = DBSession.query(SPDWMPolicy).filter(SPDWMPolicy.sp_id == self.sp_id).filter(SPDWMPolicy.policy_name == self.policy).first()
        if spdwm:
            return True
        return False


    def is_enabled(self):
        return self.enabled
    
    @classmethod
    def set_dwm_task_frequency(cls, sp_id, policy):
        dwm = DBSession.query(DWM).filter(DWM.sp_id == sp_id).filter(DWM.policy == policy).first()
        if dwm:
            interval_task = dwm.get_dwm_task()
            if interval_task:
                interval_task.set_frequency(dwm.frequency)
                DBSession.add(interval_task)
    
    @classmethod
    def find_current_policy(cls,sp_id):
        now = datetime.now()
        dwm,sch = cls.find_policy_schedule_for_time(sp_id, now)
        return dwm
    ################not
    @classmethod
    def find_policy_schedule_for_time(cls,sp_id, now=datetime.now()):
        time = float(str(now.hour) + '.' + str(now.minute))
        schedules = DBSession.query(DWM,DWMPolicySchedule).filter(DWM.sp_id == sp_id)\
                    .join((DWMPolicySchedule,DWMPolicySchedule.policy_id == DWM.id))\
                    .filter(or_(DWMPolicySchedule.start <= time,DWMPolicySchedule.end >= time)).all()
        for dwm,sch in schedules:
            if cls.check_schedule_for_time(sch, now.hour, now.minute, [now.weekday()]) == True:
                if dwm.is_enabled():
                    return (dwm,sch)
        return (None,None)
            
    
        
    @classmethod
    def check_schedules_for_time(cls, schedules, now=datetime.now()):
        valid_sch = []
        for sch in schedules:
            if cls.check_schedule_for_time(sch, now.hour, now.minute, [now.weekday()]) == True:
                valid_sch.append(sch)
        return valid_sch
                
    @classmethod
    def check_schedule_for_time(cls, schedule, hour, minute, dows=[], start=False, end=False):
        time = float(str(hour) + '.' + get_minute_string(minute))
        check_time = Decimal(str(time))
        start_time = Decimal(str(schedule.start))
        end_time = Decimal(str(schedule.end))
        print '=======================================',schedule.type
        if schedule.type == DWMPolicySchedule.DAILY:
            if start_time < check_time or start == True or start_time == check_time:
                if end_time > check_time or end == True or end_time == check_time:
                    return True
                else:
                    if end_time < start_time:
                        return True
            elif end_time > check_time or end == True or end_time == check_time:
                if end_time < start_time:
                    return True
        else:
            if start_time < check_time or start == True or start_time == check_time:
                if end_time > check_time or end == True or end_time == check_time:
                    for day in dows:
                        if day in schedule.utc_days_list:
                            return True
                else:
                    if cls.is_night_schedule(schedule) == True:
                        for day in dows:
                            if day in schedule.utc_days_list:
                                return True
            elif end_time > check_time or end == True or end_time == check_time:
                if cls.is_night_schedule(schedule) == True:
                    for day in dows:
                        if start == False and end == False:
                            day = cls.get_previous_dow(day)
                        if day in schedule.utc_days_list:
                            return True
            return False
        
        
    @classmethod
    def is_night_schedule(cls, schedule):
        now = datetime.now()
        sch_start = datetime(now.year,now.month,now.day,schedule.hour,schedule.minute)
        sch_end = sch_start + timedelta(hours = int(schedule.duration))
        if sch_start.weekday() != sch_end.weekday():
            return True
        return False
        
        
        
    @classmethod
    def get_previous_dow(cls, dow):
        dow = int(dow)
        dow = dow -1
        if dow < 0:
            dow = 6
        return dow
    @classmethod
    def check_overlapping_policies(cls, sp_id, new_policy, new_schedules, start=False, end=False):
        ex_schedules = DBSession.query(DWMPolicySchedule)\
                        .filter(DWMPolicySchedule.policy_id\
                        .in_(DBSession.query(DWM.id).filter(DWM.sp_id == sp_id)\
                            .filter(DWM.policy != new_policy))).all()
        print ex_schedules
        for new_sch in new_schedules:
            start_days = new_sch.get('start_day',[0,1,2,3,4,5,6])
            for ex_sch in ex_schedules:
                if cls.check_schedule_for_time(ex_sch, new_sch.get('hour'),new_sch.get('minute'),start_days,start = start,end = end) == True:
                    return True
        return False
                    
    @classmethod
    def check_overlapping_schedules(cls, schedule_list, schedule_objs, start=False, end=False):
        for sch in schedule_list:
            start_days = sch.get('start_day',[0,1,2,3,4,5,6])
            for sch_obj in schedule_objs:
                if cls.check_schedule_for_time(sch_obj, sch.get('hour'),sch.get('minute'),start_days,start = start,end = end) == True:
                    return True
        return False
                
    @classmethod
    def is_dwm_enabled(cls, sp_id):
        dwm = DBSession.query(DWM).filter(DWM.sp_id == sp_id).filter(DWM.enabled == True).first()
        if dwm:
            return True



class SPDWMPolicy(DeclarativeBase):
    ON = 1
    OFF = 0
    __tablename__ = 'sp_dwm_policies'
    sp_id = Column(Unicode(255), primary_key=True)
    policy_name = Column(Unicode(255))
    time = Column(DateTime)
    def __init__(self, sp_id, policy, time=datetime.now()):
        self.sp_id = sp_id
        self.policy_name = policy
        self.time = time
        self.msg = ''

    @classmethod
    def get_sp_current_policy(cls, sp_id):
        obj = DBSession.query(SPDWMPolicy).filter(SPDWMPolicy.sp_id == sp_id).first()
        if obj:
            return obj.get_current_policy()

    @classmethod
    def set_sp_current_policy(cls, sp_id, policy, mode):
        obj = DBSession.query(SPDWMPolicy).filter(SPDWMPolicy.sp_id == sp_id).first()
        msg = ''
        if obj:
            LOGGER.debug('Set current Policy to :%s, Mode :%s' % (policy,mode))
            msg = obj.set_current_policy(policy,mode)
            DBSession.add(obj)
        return msg

    @classmethod
    def set_sp_none_policy(cls, sp_id):
        obj = DBSession.query(SPDWMPolicy).filter(SPDWMPolicy.sp_id == sp_id).first()
        if obj:
            obj.set_policy(None)
            DBSession.add(obj)

    @classmethod
    def ps_check_down_nodes(cls, auth, sp_id, policy, mode):
        msg = ''
        if policy in [DWMManager.POWER_SAVING] and mode in [SPDWMPolicy.OFF]:
            msg = 'Trying to start the Servers that were shutdown during Power Save. \n'
            ids,msg1 = SPDWMPolicy.ps_start_down_nodes(auth, sp_id)
            msg += msg1
        return msg
    
    @classmethod
    def ps_start_down_nodes(cls, auth, sp_id, server_limit=None):
        msg = ''
        started_server_ids = []
        limit_count = 0
        down_nodes = DBSession.query(PSDownServers).filter(PSDownServers.sp_id == sp_id).all()
        if down_nodes:
            sp = DBSession.query(ServerGroup).filter(ServerGroup.id == sp_id).first()
            sp_ent = DBSession.query(Entity).filter(Entity.entity_id == sp_id).first()
            child_ids = []
            if sp_ent:
                child_ids = [x.entity_id for x in sp_ent.children]
                DBSession.query(PSDownServers).filter(not_(PSDownServers.node_id.in_(child_ids))).filter(PSDownServers.sp_id == sp_id).delete()
            down_node_ids = [x.node_id for x in down_nodes if x.node_id in child_ids]
            peer_node = sp.get_peer_node('exclude_ids',[down_node_ids])
            if peer_node is None:
                msg = 'No up nodes found in Server Pool :%s. Can not Power ON the down servers.' % sp.name
                LOGGER.info(msg)
                return msg
            dwm = DWMManager()
            for down_node_id in down_node_ids:
                down_node = DBSession.query(ManagedNode).filter(ManagedNode.id == down_node_id).first()
                if down_node.is_maintenance():
                    LOGGER.info('Server %s is marked for maintenance' % down_node.hostname)
                msg += 'Trying to start the Server : '+ down_node.hostname
                success = dwm.start_node(auth, down_node, peer_node)
                if success:
                    msg += 'Server : ' + down_node.hostname + ' successfully started.'
                    started_server_ids.append(down_node.id)
                    if server_limit:
                        limit_count += 1
                        if limit_count == server_limit:
                            break
                    DBSession.query(PSDownServers).filter(PSDownServers.node_id == down_node.id).delete()
                    LOGGER.debug('down node :%s deleted from table ps_down_servers' %down_node.hostname)
                    LOGGER.info('%s: down node :%s started in Server Pool :%s' %(DWMManager.POWER_SAVING,down_node.hostname,sp.name))
                    continue
                msg1 = '%s: Error in starting down node :%s in Server Pool :%s' %(DWMManager.POWER_SAVING,down_node.hostname,sp.name)
                msg += msg1
                LOGGER.error(msg1)
        return (started_server_ids,msg)
            
            
            
            
            

    def get_current_policy(self):
        return self.policy_name

    def set_policy(self, policy):
        self.policy_name = policy
        self.time = datetime.now()

    def set_current_policy(self, policy, mode):
        msg = ''
        try:
            if mode == SPDWMPolicy.ON:
                msg = 'Activating ' + str(policy) + ' policy.'
                LOGGER.info(msg)
                self.set_policy(policy)
                DWM.set_dwm_task_frequency(self.sp_id, policy)
            else:
                if self.get_current_policy() == policy:
                    self.set_policy(None)
                msg = 'Deactivating ' + str(policy) + ' policy.'
                LOGGER.info(msg)
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
        return msg



class DWMPolicySchedule(DeclarativeBase):
    __tablename__ = 'dwm_policy_schedule'
    id = Column(Unicode(50), primary_key=True)
    policy_id = Column(Unicode(50), ForeignKey('dwm_policies.id'))
    sp_id = Column(Unicode(50), ForeignKey('server_groups.id'))
    type = Column(Unicode(50))
    weekdays_list = Column(PickleType)
    dows = Column(PickleType)
    utc_days_list = Column(PickleType)
    hour = Column(Integer)
    minute = Column(Integer)
    start_time = Column(Unicode(50))
    duration = Column(Integer)
    start = Column('utc_start', Numeric)
    end = Column('utc_end', Numeric)
    WEEKLY = u'Weekly'
    DAILY = u'Daily'
    def __init__(self):
        self.id = getHexID()



class DWMHistory(DeclarativeBase):
    __tablename__ = 'dwm_history'
    id = Column(Integer, Sequence('dwm_history_id_seq'), primary_key=True)
    sp_id = Column(Unicode(255), nullable=False)
    policy_name = Column(Unicode(255), nullable=False)
    vm_ent_id = Column(Unicode(255), nullable=False)
    source_ent_id = Column(Unicode(255), nullable=False)
    dest_ent_id = Column(Unicode(255), nullable=False)
    status = Column(Boolean, default=False)
    time = Column(DateTime)


class PSDownServers(DeclarativeBase):
    __tablename__ = 'ps_down_servers'
    id = Column(Integer, Sequence('ps_down_id_seq'), primary_key=True)
    sp_id = Column(Unicode(255), nullable=False)
    node_id = Column(Unicode(255), nullable=False)
    time = Column(DateTime)
    def __init__(self, sp_id, node_id):
        self.sp_id = sp_id
        self.node_id = node_id
        self.time = datetime.now()



class DWMManager():
    POWER_SAVING = u'POWER_SAVING'
    LOAD_BALANCING = u'LOAD_BALANCING'
    LB_SERVER_MATRIX_ORDER = [['core_normalized_cpu', 'cpu_util', 'mem_util', 'cpu_util_variance'], ['cpu_util_plus_sigma', 'cpu_util_minus_sigma', 'sticky_vms'], ['cores', 'sp_ent', 'node']]
    LB_VM_MATRIX_ORDER = [['-sticky', '-priority', 'gain', 'cost', 'cpu_util_variance', 'cpu_util_plus_sigma', 'cpu_util_minus_sigma'], ['cpu_util', 'mem_util', 'max_mem_req', 'band_width'], ['source_node_ent', 'dom']]
    PS_SERVER_MATRIX_ORDER = [['core_normalized_cpu', 'cpu_util', 'mem_util', 'cpu_util_variance'], ['cpu_util_plus_sigma', 'cpu_util_minus_sigma', 'sticky_vms'], ['cores', 'sp_ent', 'node']]
    PS_VM_MATRIX_ORDER = [['-sticky', '-priority', 'gain', 'cost', 'cpu_util_variance', 'cpu_util_plus_sigma', 'cpu_util_minus_sigma'], ['cpu_util', 'mem_util', 'max_mem_req', 'band_width'], ['source_node_ent', 'dom']]
    def __init__(self):
        DWMManager.PS_SERVER_MATRIX_INDEX = self.get_matrix_index(DWMManager.PS_SERVER_MATRIX_ORDER)
        DWMManager.PS_VM_MATRIX_INDEX = self.get_matrix_index(DWMManager.PS_VM_MATRIX_ORDER)
        DWMManager.LB_SERVER_MATRIX_INDEX = self.get_matrix_index(DWMManager.LB_SERVER_MATRIX_ORDER)
        DWMManager.LB_VM_MATRIX_INDEX = self.get_matrix_index(DWMManager.LB_VM_MATRIX_ORDER)
        self.NEED_TO_START_SERVER = []
        self.sp_ent = None
        self.sp = None
        self.data_period = None
        self.fence_action = None
        self.variance_fetch_interval = 30
        self.powersave_servers = []
        self.msg = ''
        self.policy_active = False
        self.auth = None
        self.mig_down_vms = None

    def dwm(self, auth, sp_id):
        try:
            self.sp_ent = DBSession.query(Entity).filter(Entity.entity_id == sp_id).first()
            self.sp = DBSession.query(ServerGroup).filter(ServerGroup.id == sp_id).first()
            self.auth = auth
            if self.sp_ent is None:
                raise Exception('Entity can not be found for the id:%s ' % sp_id)
            policy = SPDWMPolicy.get_sp_current_policy(sp_id)
            if policy:
                dwm_obj = DBSession.query(DWM).filter(DWM.sp_id == sp_id).filter(DWM.policy == policy).first()
                if dwm_obj:
                    self.data_period = dwm_obj.data_period
                    if policy == DWMManager.POWER_SAVING:
                        self.run_power_saving(dwm_obj.threshold, dwm_obj.upper_threshold)
                    elif policy == DWMManager.LOAD_BALANCING:
                        self.run_load_balancing(dwm_obj.threshold)
                    else:
                        msg = 'DWM Policy is not enabled.'
                        self.msg += '\n' + msg
                        LOGGER.info('DWM Policy is not enabled for ServerPool:%s' % self.sp_ent.name)
                else:
                    msg = 'DWM Policy is not enabled.'
                    self.msg += '\n' + msg
                    LOGGER.info('DWM Policy is not enabled for ServerPool:%s' % self.sp_ent.name)
            else:
                msg = 'DWM Policy is not enabled.'
                self.msg += '\n' + msg
                LOGGER.info('DWM Policy is not enabled for ServerPool:%s' % self.sp_ent.name)
            return (self.msg, self.policy_active)
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
            raise ex


    def run_power_saving(self, threshold, upper_threshold):
        LOGGER.debug('---- run_power_saving ------ Start')
        self.msg += '\nPolicy : Power Saving \n-----------------------------'
        self.msg += '\nLower Threshold : %s%%' % threshold
        self.msg += '\nUpper Threshold : %s%%' % upper_threshold
        LOGGER.info('%s: Server Pool:%s, Lower Threshold:%s, Upper Threshold:%s' % (DWMManager.POWER_SAVING, self.sp_ent.name, threshold, upper_threshold))
        powersave_servers,server_matrix = self.get_server_matrix(threshold, DWMManager.POWER_SAVING)
        print powersave_servers,'##########powersave_servers###########################'
        print server_matrix,'#########server_matrix###########'
        if powersave_servers:
            self.policy_active = True
            self.powersave_servers = powersave_servers
            try:
                move_down_vms = int(tg.config.get('dwm_ps_migrate_down_vms'))
            except Exception as ex:
                move_down_vms = 0
                LOGGER.error(to_str(ex))
            self.mig_down_vms = Entity.get_attribute_value(self.sp_ent.entity_id, 'dwm_ps_migrate_down_vms', move_down_vms)
            if self.mig_down_vms:
                msg = 'Down vms migration : Enabled'
                self.msg += '\n' + msg
                LOGGER.info('%s: Migrate down VMs Enabled (Migrate both running and down VMs before shutdown the Node)' % DWMManager.POWER_SAVING)
            else:
                msg = 'Down vms migration : Disabled'
                self.msg += '\n' + msg
                LOGGER.info('%s: Migrate down VMs Disabled (Migrate only running VMs before shutdown the Node)' % DWMManager.POWER_SAVING)
            migrate_instructions = self.powersave_migrate_instructions(powersave_servers, server_matrix, threshold, upper_threshold)
            print '====migrate_instructions======='
            pprint.pprint(migrate_instructions)
            if not migrate_instructions:
                LOGGER.info('%s: No Migrate instructions for ServerPool:%s' % (DWMManager.POWER_SAVING, self.sp_ent.name))
            else:
                for node_id,mig_instructions in migrate_instructions.items():
                    node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
                    if not mig_instructions:
                        msg = 'No Migrate instructions.'
                        self.msg += '\n' + msg
                        LOGGER.info('%s: No Migrate instructions for Node:%s' % (DWMManager.POWER_SAVING, node.hostname))
                        if self.check_ha_event(self.sp_ent.entity_id) == False:
                            self.powersave_shutdown_node(node)
                        else:
                            msg = 'HA is active on ServerPool:%s.' % self.sp_ent.name
                            self.msg += '\n' + msg
                            LOGGER.info('%s: HA is active on ServerPool:%s ' % (DWMManager.POWER_SAVING, self.sp_ent.name))
                            continue
                    else:
                        LOGGER.debug('%s: Start excecuting Migrate instructions for Node:%s' % (DWMManager.POWER_SAVING, node.hostname))
                        result = self.execute_migrate_instructions(mig_instructions, self.sp_ent.entity_id, DWMManager.POWER_SAVING)
                        if result.get('success'):
                            LOGGER.info('%s: All the Vms of Node:%s has successfully migrated, Shutting down the Node' % (DWMManager.POWER_SAVING, node.hostname))
                            if self.check_ha_event(self.sp_ent.entity_id) == False:
                                self.powersave_shutdown_node(node)
                            else:
                                msg = 'HA is active on ServerPool:%s.' % self.sp_ent.name
                                self.msg += '\n' + msg
                                LOGGER.info('%s: HA is active on ServerPool:%s ' % (DWMManager.POWER_SAVING, self.sp_ent.name))
                                continue
                        else:
                            LOGGER.info('%s: Some migrations failed, can not shutdown Node:%s' % (DWMManager.POWER_SAVING, node.hostname))
                self.run_load_balancing(upper_threshold)
                self.lb_start_down_node_execute_mig_insts()
        else:
            msg = 'No Node with utilization below or equal to PowerSave lower threshold.'
            self.msg += '\n' + msg
            LOGGER.info('%s: No Nodes with utilization below or equal to PowerSave lower threshold:%s in ServerPool:%s' % (DWMManager.POWER_SAVING, threshold, self.sp_ent.name))
        LOGGER.debug('---- run_power_saving ------ End')


    def run_load_balancing(self, threshold):
        LOGGER.debug('---- run_load_balancing ------ Start')
        msg = '\nLoad Balancing \n---------------------'
        self.msg += '\n' + msg
        loaded_servers,server_matrix = self.get_server_matrix(threshold, DWMManager.LOAD_BALANCING)
        if loaded_servers:
            self.policy_active = True
            migrate_instructions = self.loadbalancing_migrate_instructions(loaded_servers, server_matrix, threshold)
            if migrate_instructions:
                LOGGER.info('%s: Executing Migrate instructions for ServerPool:%s' % (DWMManager.LOAD_BALANCING, self.sp_ent.name))
                self.execute_migrate_instructions(migrate_instructions, self.sp_ent.entity_id, DWMManager.LOAD_BALANCING)
            else:
                msg = 'No Migrate instructions for Load balancing.'
                self.msg += '\n' + msg
                LOGGER.info('%s: No Migrate instructions for ServerPool:%s' % (DWMManager.LOAD_BALANCING, self.sp_ent.name))
        else:
            msg = 'No loaded Nodes.'
            self.msg += '\n' + msg
            LOGGER.info('%s: No loaded Nodes in ServerPool:%s' % (DWMManager.LOAD_BALANCING, self.sp_ent.name))
        LOGGER.debug('---- run_load_balancing ------ End')

###############
    def lb_start_down_node_execute_mig_insts(self):
        LOGGER.debug('---- lb_start_down_node_execute_mig_insts ------ Start')
        if self.NEED_TO_START_SERVER:
            LOGGER.info('%s: Starting Node which were shutdown during PowerSave in ServerPool:%s' %(DWMManager.LOAD_BALANCING,self.sp_ent.name))
            started_server_ids,msg = SPDWMPolicy.ps_start_down_nodes(self.auth, self.sp_ent.entity_id, server_limit=1)
            if started_server_ids:
                new_migrate_instructions = self.create_new_migrate_instructions(self,self.NEED_TO_START_SERVER[:],started_server_ids[0])
                LOGGER.info('%s: Executing Migrate instructions for ServerPool:%s for Load balancing during PowerSave' %(DWMManager.LOAD_BALANCING,self.sp_ent.name))
                self.execute_migrate_instructions(new_migrate_instructions, self.sp_ent.entity_id, DWMManager.LOAD_BALANCING)
            else:
                msg = 'Load balancing, Can not start Node which were shutdown during PowerSave.'
                self.msg += '\n' + msg
                LOGGER.info('%s: Load balancing, Can not start Node which were shutdown during PowerSave in ServerPool:%s' %(DWMManager.LOAD_BALANCING,self.sp_ent.name))
        else:
            msg = 'No need to start Node which were shutdown during PowerSave.'
            self.msg += '\n' + msg
            LOGGER.info('%s: No need to start Node which were shutdown during PowerSave in ServerPool:%s' %(DWMManager.LOAD_BALANCING,self.sp_ent.name))
        LOGGER.debug('---- lb_start_down_node_execute_mig_insts ------ End')
        
            
            
            
                    
    def get_server_matrix(self, threshold, mode):
        server_matrix = []
        loaded_servers = []
        try:
            #1217
            fetch_interval = self.data_period
            try:
                self.variance_fetch_interval = int(tg.config.get('dwm_variance_fetch_interval'))
            except Exception as ex:
                LOGGER.error(to_str(ex))
            variance_from_date = datetime.now() - timedelta(minutes=self.variance_fetch_interval)
            from_date = datetime.now() - timedelta(minutes=fetch_interval)
            to_date = datetime.now()
            #[NODE: 209]
            node_ent_ids = [node_ent.entity_id for node_ent in self.sp_ent.children]
            for node in ManagedNode.get_up_nodes(node_ent_ids):
                #1212
                if node.is_maintenance():
                    LOGGER.info('Server %s is marked for maintenance' % node.hostname)
                else:
                    ms = MetricsService()
                    cores = node.get_cores()
                    matrix_dict = {}
                    print '--##hostname##-',node.hostname,'--##from_date##-',from_date,'--##to_date##-',to_date
                    node_data = ms.getRawCpuAndMemData(node.id,constants.SERVER_RAW,from_date,to_date,variance_from_date)
                    pprint.pprint(node_data)
                    print node_data,'#55555555555555555'
                    if node_data:
                        #1208
                        matrix_dict['cpu_util'] = DWMManager.bucketing(node_data.get('cpu_util_avg',0))
                        
                        matrix_dict['mem_util'] = node_data.get('mem_util_avg',0)
                        matrix_dict['cpu_util_variance'] = node_data.get('cpu_util_var',0)
                        matrix_dict['core_normalized_cpu'] = DWMManager.bucketing(cores*node_data.get('cpu_util_avg',0))
                        matrix_dict['cpu_util_plus_sigma'] = node_data.get('cpu_util_avg',0) + node_data.get('cpu_util_sum',0)
                        matrix_dict['cpu_util_minus_sigma'] = node_data.get('cpu_util_avg',0) - node_data.get('cpu_util_sum',0)
                        matrix_dict['sticky_vms'] = VM.get_sticky_vms_count(node.id)
                        matrix_dict['cores'] = cores
                        matrix_dict['sp_ent'] = self.sp_ent
                        matrix_dict['node'] = node
                        if mode in [DWMManager.LOAD_BALANCING]:
                            #823
                            LOGGER.debug('%s: Server:%s has %s Sticky VMs' % (mode, node.hostname, matrix_dict['sticky_vms']))
                            LOGGER.debug('%s: Node:%s , CPU Utilization:%s , Memory Utilization:%s , CPU Variance:%s , core_normalized_cpu:%s , Mean+Sigma:%s , Mean-Sigma:%s , Sticky VMS:%s , Threshold:%s ' % (DWMManager.LOAD_BALANCING, node.hostname, matrix_dict['cpu_util'], matrix_dict['mem_util'], matrix_dict['cpu_util_variance'], matrix_dict['core_normalized_cpu'], matrix_dict['cpu_util_plus_sigma'], matrix_dict['cpu_util_minus_sigma'], matrix_dict['sticky_vms'], threshold))
                            server_matrix_item_list = self.get_ordered_matrix(DWMManager.LB_SERVER_MATRIX_ORDER, matrix_dict)
                            print '###########matrix_dict[cpu_util]#####threshold##########',matrix_dict['cpu_util'] , threshold
                            ##tianfeng
                            #matrix_dict['cpu_util'] = 30
                            ###tianfeng
                            if matrix_dict['cpu_util'] >= threshold:
                                #819
                                loaded_servers.append((matrix_dict['cpu_util'], cores, node))
                        elif mode in [DWMManager.POWER_SAVING]:
                            #1146
                            if matrix_dict['sticky_vms']:
                                mesg = 'Num of sticky VMs > 0, this node Can not selected for PowerSave'
                            else:
                                mesg = 'Num of sticky VMs == 0, this node selected for PowerSave'
                            LOGGER.debug('%s: Node:%s has %s Sticky VMs (%s)' % (mode, node.hostname, matrix_dict['sticky_vms'], mesg))
                            LOGGER.debug('%s: Node:%s , CPU Utilization:%s , Memory Utilization:%s , CPU Variance:%s , core_normalized_cpu:%s , Mean+Sigma:%s , Mean-Sigma:%s , Sticky VMS:%s, threshold:%s ' % (DWMManager.POWER_SAVING, node.hostname, matrix_dict['cpu_util'], matrix_dict['mem_util'], matrix_dict['cpu_util_variance'], matrix_dict['core_normalized_cpu'], matrix_dict['cpu_util_plus_sigma'], matrix_dict['cpu_util_minus_sigma'], matrix_dict['sticky_vms'], threshold))
                            power_fencing_dev_conf = node.is_power_fencing_device_configured()
                            if power_fencing_dev_conf:
                                #1015
                                mesg = 'Power fencing device configured.This node can be shutdown, so selected for PowerSave.'
                            else:
                                mesg = 'Power fencing device not configured.This node can not be shutdown, so can not selected for PowerSave.'
                            LOGGER.debug('%s: Node:%s, %s' %(mode,node.hostname,mesg))
                            server_matrix_item_list= self.get_ordered_matrix(DWMManager.PS_SERVER_MATRIX_ORDER, matrix_dict)
                            print matrix_dict['cpu_util'] ,'@@@@@@@@', threshold and matrix_dict['sticky_vms'] ,'@@@@@@@@', power_fencing_dev_conf,'@@@@@@@@@@@@@@@@@@@@@@@@@'
                            if matrix_dict['cpu_util'] <= threshold and matrix_dict['sticky_vms'] == 0 and power_fencing_dev_conf:
                                #1142
                                loaded_servers.append((matrix_dict['cpu_util'], cores, node))
                        server_matrix_item_tuple = tuple([tuple(x) for x in server_matrix_item_list])
                        server_matrix.append(server_matrix_item_tuple)
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
            raise ex
        return (loaded_servers, server_matrix)


    def loadbalancing_migrate_instructions(self, loaded_servers, server_matrix, loadbalancing_threshold):
        print '\n ====== loadbalancing_migrate_instructions START ======'
        self.NEED_TO_START_SERVER = []
        migrate_instructions = []
        try:
            #1884
            loaded_servers.sort(reverse=True)
            server_matrix.sort()
            print '\n-------Loaded_server---------'
            pprint.pprint(loaded_servers)
            print '\n-------Server_matrix----------'
            pprint.pprint(server_matrix)
            for loaded_server in loaded_servers:
                #1879
                instruction_gen_status = False
                source_node_cpu_util_avg = loaded_server[0]
                source_node_cores = loaded_server[1]
                source_node = loaded_server[2]
                source_node_ent = DBSession.query(Entity).filter(Entity.entity_id == source_node.id).first()
                #print source_node_ent,'###########source_node_ent#####'
                #[NODE: 193]
                vm_ent_ids = [vm_ent.entity_id for vm_ent in source_node_ent.children]
                #print vm_ent_ids,'###########vm_ent_ids#####'
                doms = [dom for dom in VM.get_running_vms(vm_ent_ids) if dom.preferred_nodeid != source_node.id]
                #doms = [dom for dom in VM.get_running_vms(vm_ent_ids) if dom.preferred_nodeid == source_node.id]
                print '-----------ignore sticky vms--------'
                pprint.pprint(doms)
                loaded_vm_matrix = self.get_vm_matrix(source_node_ent, doms)
                if loaded_vm_matrix:
                    #1875
                    print '\n-------loaded_vm_matrix-------'
                    pprint.pprint(loaded_vm_matrix)
                    for vm_mat in loaded_vm_matrix:
                        #1871
                        is_dest_node_available = False
                        x,y = DWMManager.LB_VM_MATRIX_INDEX.get('cpu_util')
                        vm_cpu_util_avg = vm_mat[x][y]
                        x,y = DWMManager.LB_VM_MATRIX_INDEX.get('cpu_util_plus_sigma')
                        vm_cpu_util_sum = vm_mat[x][y] - vm_cpu_util_avg
                        x,y = DWMManager.LB_VM_MATRIX_INDEX.get('mem_util')
                        vm_mem_util_avg = vm_mat[x][y]
                        x,y = DWMManager.LB_VM_MATRIX_INDEX.get('dom')
                        mig_vm = vm_mat[x][y]
                        for index,server_mat in enumerate(server_matrix):
                            #1734
                            server_matrix_dict = {}
                            x,y = DWMManager.LB_SERVER_MATRIX_INDEX.get('cpu_util')
                            dest_node_cpu_util_avg = server_mat[x][y]
                            x,y = DWMManager.LB_SERVER_MATRIX_INDEX.get('mem_util')
                            dest_node_mem_util_avg = server_mat[x][y]
                            x,y = DWMManager.LB_SERVER_MATRIX_INDEX.get('cores')
                            dest_node_cores = server_mat[x][y]
                            x,y = DWMManager.LB_SERVER_MATRIX_INDEX.get('sp_ent')
                            dest_node_sp_ent = server_mat[x][y]
                            x,y = DWMManager.LB_SERVER_MATRIX_INDEX.get('node')
                            dest_node = server_mat[x][y]
                
                            if source_node.id != dest_node.id:
                                #1695
                                dest_node_updated_cpu_util_avg = DWMManager.bucketing(self.get_updated_dest_cpu_util(source_node_cores, dest_node_cores, vm_cpu_util_avg, dest_node_cpu_util_avg))
                                if dest_node_updated_cpu_util_avg < loadbalancing_threshold:
                                    #1621
                                    result = utils.check_constraints(mig_vm, dest_node)
                                    if result:
                                        #1529
                                        migrate_instructions.append((mig_vm, source_node, dest_node, DWMManager.LOAD_BALANCING))
                                        is_dest_node_available = True
                                        x,y = DWMManager.LB_SERVER_MATRIX_INDEX.get('cpu_util_plus_sigma')
                                        dest_node_cpu_util_sum = server_mat[x][y] - dest_node_cpu_util_avg
                                        dest_node_updated_cpu_util_sum = dest_node_cpu_util_sum + vm_cpu_util_sum
                                        server_matrix_dict['cpu_util'] = dest_node_updated_cpu_util_avg
                                        server_matrix_dict['mem_util'] = dest_node_mem_util_avg + vm_mem_util_avg
                                        x,y = DWMManager.LB_SERVER_MATRIX_INDEX.get('cpu_util_variance')
                                        server_matrix_dict['cpu_util_variance'] = server_mat[x][y]
                                        server_matrix_dict['core_normalized_cpu'] = dest_node_updated_cpu_util_avg * dest_node_cores
                                        server_matrix_dict['cpu_util_plus_sigma'] = dest_node_updated_cpu_util_avg + dest_node_updated_cpu_util_sum
                                        server_matrix_dict['cpu_util_minus_sigma'] = dest_node_updated_cpu_util_avg - dest_node_updated_cpu_util_sum
                                        x,y = DWMManager.LB_SERVER_MATRIX_INDEX.get('sticky_vms')
                                        server_matrix_dict['sticky'] = server_mat[x][y]
                                        x,y = DWMManager.LB_SERVER_MATRIX_INDEX.get('cores')
                                        server_matrix_dict['cores'] = server_mat[x][y]
                                        x,y = DWMManager.LB_SERVER_MATRIX_INDEX.get('sp_ent')
                                        server_matrix_dict['sp_ent'] = server_mat[x][y]
                                        x,y = DWMManager.LB_SERVER_MATRIX_INDEX.get('node')
                                        server_matrix_dict['node'] = server_mat[x][y]
                                        server_matrix_item_list = self.get_ordered_matrix(DWMManager.LB_SERVER_MATRIX_ORDER, server_matrix_dict)
                                
                                        server_matrix_item_tuple = tuple([tuple(x) for x in server_matrix_item_list])
                                        del server_matrix[index]
                                
                                        flag = True
                                        for i,v in enumerate(server_matrix):
                                            if v >= server_matrix_item_tuple:
                                                server_matrix.insert(i, server_matrix_item_tuple)
                                                flag = False
                                                break
                                        if flag:
                                            #1360
                                            server_matrix.append(server_matrix_item_tuple)
                                
                                        #[NODE: 1361]
                                        instruction_gen_status = True
                                        msg = '%s: Migrate instruction generated Source Node:%s , vm:%s , Destination Node:%s' % (DWMManager.LOAD_BALANCING, source_node.hostname, mig_vm.name, dest_node.hostname)
                                        self.msg += '\n' + msg
                                        LOGGER.debug('%s: Migrate instruction generated Source Node:%s , vm:%s , Destination Node:%s' % (DWMManager.LOAD_BALANCING, source_node.hostname, mig_vm.name, dest_node.hostname))
                                        LOGGER.debug('%s: CPU Utilizaion of VM:%s to be migrated is :%s ' % (DWMManager.LOAD_BALANCING, mig_vm.name, vm_cpu_util_avg))
                                        LOGGER.debug('%s: Selected destination Node:%s  Current CPU utilization:%s  Estimated CPU Utilization:%s is less than load balancing threshold:%s' % (DWMManager.LOAD_BALANCING, dest_node.hostname, dest_node_cpu_util_avg, dest_node_updated_cpu_util_avg, loadbalancing_threshold))
                                        break
                            
                                    #1692
                                    else:
                                        msg = 'Can not generate migrate instruction: Constraints Check failed for VM:%s, Source Node:%s, Destination Node:%s.' % (mig_vm.name, source_node.hostname, dest_node.hostname)
                                        self.msg += '\n' + msg
                                        LOGGER.info('%s: Can not generate migrate instruction: Constraints Check failed for VM:%s , Source Node:%s, Destination Node:%s' % (DWMManager.LOAD_BALANCING, mig_vm.name, source_node.hostname, dest_node.hostname))
                                    #1731--529
                                else:
                                    LOGGER.debug('%s: CPU Utilizaion of VM :%s to be migrated is :%s ' % (DWMManager.LOAD_BALANCING, mig_vm.name, vm_cpu_util_avg))
                                    LOGGER.debug('%s: Can not generate migrate instruction: Selected destination Node:%s  Current CPU utilization:%s  Estimated CPU Utilization:%s is grater than or equal to load balancing threshold:%s' % (DWMManager.LOAD_BALANCING, dest_node.hostname, dest_node_cpu_util_avg, dest_node_updated_cpu_util_avg, loadbalancing_threshold))
                                    continue
                        
                            else:    #[NODE: 1695]
                                LOGGER.debug('%s: Can not generate migrate instruction: Source:%s  and Destination:%s  Nodes are same' % (DWMManager.LOAD_BALANCING, source_node.hostname, dest_node.hostname))
                        
                        #[NODE: 1735]
                        if instruction_gen_status:
                            #1834
                            instruction_gen_status = False
                            updated_source_node_cpu_util_avg = DWMManager.bucketing(self.get_updated_source_cpu_util(source_node_cores, vm_cpu_util_avg, source_node_cpu_util_avg))
                            if updated_source_node_cpu_util_avg <= loadbalancing_threshold:
                                LOGGER.debug('%s: Source Node:%s now not loaded, CPU utilization:%s  Loadbalancing Threshold:%s' % (DWMManager.LOAD_BALANCING, source_node.hostname, updated_source_node_cpu_util_avg, loadbalancing_threshold))
                                break
                        #[NODE: 1835]
                        if not is_dest_node_available:
                            #1867
                            self.NEED_TO_START_SERVER.append([mig_vm, source_node])
                            continue
                else:
                    continue
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
            raise ex
        print '\n ====== loadbalancing_migrate_instructions END ======'
        return migrate_instructions


    def powersave_migrate_instructions(self, powersave_servers, server_matrix, powersave_threshold, upper_threshold):
        print '\n ====== powersave_migrate_instructions START ====== \n'
        print '\n-------DWMManager.PS_VM_MATRIX_INDEX-------'
        pprint.pprint(DWMManager.PS_VM_MATRIX_INDEX)
        migrate_instructions = {}

        try:
            #2097
            powersave_servers.sort()
            server_matrix.sort()
            print '\n-------powersave_server-------'
            pprint.pprint(powersave_servers)
            print '\n-------server_matrix-------'
            pprint.pprint(server_matrix)
            processed_nodes_ids = []
            server_matrix_copy = [x for x in server_matrix]
            for powersave_server in powersave_servers:
                #2092
                running_vms_migrate_instructions_of_node = []
                inst_gen_for_all_running_vms = True
                source_node_cores = powersave_server[1]
                source_node = powersave_server[2]
                source_node_ent = DBSession.query(Entity).filter(Entity.entity_id == source_node.id).first()
                vm_ent_ids = [vm_ent.entity_id for vm_ent in source_node_ent.children]
                doms = VM.get_running_vms(vm_ent_ids)
                loaded_vm_matrix = self.get_vm_matrix(source_node_ent, doms)
                if loaded_vm_matrix:
                    #1877
                    #[NODE: 302]
                    if inst_gen_for_all_running_vms:
                        #339
                        server_matrix_copy = [x for x in server_matrix]
                    else:
                        server_matrix = loaded_vm_matrix
            
                    loaded_vm_matrix.reverse()
                    print '\n-------loaded_vm_matrix-------'
                    pprint.pprint(loaded_vm_matrix)
                    vm_mig_status = False
                    for vm_mat in loaded_vm_matrix:
                        #1873
                        #(_[1], running_vms_migrate_instructions_of_node, inst_gen_for_all_running_vms, source_node_cores, source_node, source_node_ent, _[2], doms, loaded_vm_matrix, migrate_instructions[source_node.id], res, migrate_instructions[source_node.id], server_matrix, vm_mig_status, x, y, vm_cpu_util_avg, x, y) = ([], [], True, powersave_server[1], powersave_server[2], DBSession.query(Entity).filter(Entity.entity_id == source_node.id).first(), [], VM.get_running_vms(vm_ent_ids), self.get_vm_matrix(source_node_ent, doms), [], self.powersave_down_vms_migrate_instructions(source_node_ent, processed_nodes_ids), [], server_matrix_copy, False, DWMManager.PS_VM_MATRIX_INDEX.get('cpu_util'), [], vm_mat[x][y], DWMManager.PS_VM_MATRIX_INDEX.get('cpu_util_plus_sigma'), [])
                        x,y = DWMManager.PS_VM_MATRIX_INDEX.get('cpu_util')
                        vm_cpu_util_avg = vm_mat[x][y]
                        x,y = DWMManager.PS_VM_MATRIX_INDEX.get('cpu_util_plus_sigma')
                        vm_cpu_util_sum = vm_mat[x][y] - vm_cpu_util_avg
                        x,y = DWMManager.PS_VM_MATRIX_INDEX.get('mem_util')
                        vm_mem_util_avg = vm_mat[x][y]
                        x,y = DWMManager.PS_VM_MATRIX_INDEX.get('dom')
                        mig_vm = vm_mat[x][y]
                        for index,server_mat in enumerate(server_matrix):
                            #1804
                            server_matrix_dict = {}
                            x,y = DWMManager.PS_SERVER_MATRIX_INDEX.get('cpu_util')
                            dest_node_cpu_util_avg = server_mat[x][y]
                            x,y = DWMManager.PS_SERVER_MATRIX_INDEX.get('mem_util')
                            dest_node_mem_util_avg = server_mat[x][y]
                            x,y = DWMManager.PS_SERVER_MATRIX_INDEX.get('cores')
                            dest_node_cores = server_mat[x][y]
                            x,y = DWMManager.PS_SERVER_MATRIX_INDEX.get('sp_ent')
                            dest_node_sp_ent = server_mat[x][y]
                            x,y = DWMManager.PS_SERVER_MATRIX_INDEX.get('node')
                            dest_node = server_mat[x][y]
                
                            if source_node.id != dest_node.id:
                                #1765
                                if dest_node.id not in processed_nodes_ids:
                                    #1732
                                    dest_node_updated_cpu_util_avg = DWMManager.bucketing(self.get_updated_dest_cpu_util(source_node_cores, dest_node_cores, vm_cpu_util_avg, dest_node_cpu_util_avg))
                            
                                    if dest_node_updated_cpu_util_avg < upper_threshold:
                                        #1658
                                        result = utils.check_constraints(mig_vm, dest_node)
                                        if result:
                                            #1572
                                            running_vms_migrate_instructions_of_node.append((mig_vm, source_node, dest_node, DWMManager.POWER_SAVING))
                                            vm_mig_status = True
                                            x,y = DWMManager.PS_SERVER_MATRIX_INDEX.get('cpu_util_plus_sigma')
                                            dest_node_cpu_util_sum = server_mat[x][y] - dest_node_cpu_util_avg
                                            dest_node_updated_cpu_util_sum = dest_node_cpu_util_sum + vm_cpu_util_sum
                                            server_matrix_dict['cpu_util'] = dest_node_updated_cpu_util_avg
                                            server_matrix_dict['mem_util'] = dest_node_mem_util_avg + vm_mem_util_avg
                                            x,y = DWMManager.PS_SERVER_MATRIX_INDEX.get('cpu_util_variance')
                                            server_matrix_dict['cpu_util_variance'] = server_mat[x][y]
                                            server_matrix_dict['core_normalized_cpu'] = dest_node_updated_cpu_util_avg * dest_node_cores
                                            server_matrix_dict['cpu_util_plus_sigma'] = dest_node_updated_cpu_util_avg + dest_node_updated_cpu_util_sum
                                            server_matrix_dict['cpu_util_minus_sigma'] = dest_node_updated_cpu_util_avg - dest_node_updated_cpu_util_sum
                                            x,y = DWMManager.PS_SERVER_MATRIX_INDEX.get('sticky_vms')
                                            server_matrix_dict['sticky'] = server_mat[x][y]
                                            x,y = DWMManager.PS_SERVER_MATRIX_INDEX.get('cores')
                                            server_matrix_dict['cores'] = server_mat[x][y]
                                            x,y = DWMManager.PS_SERVER_MATRIX_INDEX.get('sp_ent')
                                            server_matrix_dict['sp_ent'] = server_mat[x][y]
                                            x,y = DWMManager.PS_SERVER_MATRIX_INDEX.get('node')
                                            server_matrix_dict['node'] = server_mat[x][y]
                                            server_matrix_item_list = self.get_ordered_matrix(DWMManager.PS_SERVER_MATRIX_ORDER, server_matrix_dict)
                                    
                                            ###################not
                                            server_matrix_item_tuple = tuple([tuple(x) for x in server_matrix_item_list])
                                            del server_matrix[index]
                                    
                                            flag = True
                                            for i,v in enumerate(server_matrix):
                                                if v >= server_matrix_item_tuple:
                                                    server_matrix.insert(i, server_matrix_item_tuple)
                                                    flag = False
                                                    break
                                            if flag:
                                                server_matrix.append(server_matrix_item_tuple)
                                            msg = '%s: Migrate instruction generated Source Node:%s , vm:%s , Destination Node:%s' % (DWMManager.POWER_SAVING, source_node.hostname, mig_vm.name, dest_node.hostname)
                                            self.msg += '\n' + msg
                                            LOGGER.debug('%s: Migrate instruction generated Source Node:%s , vm:%s , Destination Node:%s' % (DWMManager.POWER_SAVING, source_node.hostname, mig_vm.name, dest_node.hostname))
                                            LOGGER.debug('%s: CPU Utilizaion of VM:%s to be migrated is :%s ' % (DWMManager.POWER_SAVING, mig_vm.name, vm_cpu_util_avg))
                                            LOGGER.debug('%s: Selected destination Node:%s  Current CPU utilization:%s  Estimated CPU Utilization:%s is less than powersave upper threshold:%s ' % (DWMManager.POWER_SAVING, dest_node.hostname, dest_node_cpu_util_avg, dest_node_updated_cpu_util_avg, upper_threshold))
                                            break
                                    
                                        #1729--1801--562
                                        else:
                                            msg = 'Can not generate migrate instruction: Constraints Check failed for VM:%s, Source Node:%s, Destination Node:%s.' % (mig_vm.name, source_node.hostname, dest_node.hostname)
                                            self.msg += '\n' + msg
                                            LOGGER.info('%s: Can not generate migrate instruction: Constraints Check failed for VM:%s , Destination Node:%s' % (DWMManager.POWER_SAVING, mig_vm.name, dest_node.hostname))
                                        #1762--562
                                    else:
                                        LOGGER.debug('%s: CPU Utilizaion of VM :%s to be migrated is :%s ' % (DWMManager.POWER_SAVING, mig_vm.name, vm_cpu_util_avg))
                                        LOGGER.debug('%s: Can not generate migrate instruction: Selected destination Node:%s  Current CPU utilization:%s  Estimated CPU Utilization:%s is grater than or equal to powersave upper threshold:%s ' % (DWMManager.POWER_SAVING, dest_node.hostname, dest_node_cpu_util_avg, dest_node_updated_cpu_util_avg, upper_threshold))
                                        #1801--562
                                else:
                                    LOGGER.debug('%s: Can not generate migrate instruction: Destination node :%s  already processed and marked for powersave shutdown' % (DWMManager.POWER_SAVING, dest_node.hostname))
                                    continue
                        
                            else:
                                LOGGER.debug('%s: Can not generate migrate instruction: Source:%s  and Destination:%s  Nodes are same' % (DWMManager.POWER_SAVING, source_node.hostname, dest_node.hostname))
                    
                        #[NODE: 1805]
                        if not vm_mig_status:
                            #1857
                            inst_gen_for_all_running_vms = False
                            LOGGER.debug('%s: Can not generate migrate instruction for VM:%s. So node:%s can not shutdown' % (DWMManager.POWER_SAVING, mig_vm.name, source_node.hostname))
                            break
                
                        else:
                            inst_gen_for_all_running_vms = True
                            vm_mig_status = False
                print 'YYYYYYYYYYYY'
        
                #[NODE: 1889]
                if inst_gen_for_all_running_vms:
                    #2088
                    print 'HHHHHHHHHHH',
                    print source_node.id,
                    print running_vms_migrate_instructions_of_node
            
                    #[NODE: 1915]
                    if self.mig_down_vms:
                        #2035
                        res = self.powersave_down_vms_migrate_instructions(source_node_ent,processed_nodes_ids)
                        if res.get('can_shutdown'):
                            #2031
                            migrate_instructions[source_node.id] = []
                            migrate_instructions[source_node.id].extend(running_vms_migrate_instructions_of_node)
                            migrate_instructions[source_node.id].extend(res.get('down_vms_mig_instructions'))
                            processed_nodes_ids.append(source_node.id)
                    else:
                        migrate_instructions[source_node.id] = []
                        migrate_instructions[source_node.id].extend(running_vms_migrate_instructions_of_node)
                        processed_nodes_ids.append(source_node.id)
                    continue
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
            raise ex
        print '\n ====== powersave_migrate_instructions END ====== \n'
        return migrate_instructions

#####################not
    def get_vm_matrix(self, source_node_ent, doms):
        fetch_interval = self.data_period
        variance_from_date = datetime.now() - timedelta(minutes = self.variance_fetch_interval)
        from_date = datetime.now() - timedelta(minutes=fetch_interval)
        to_date = datetime.now()
        loaded_vm_matrix = []
        for dom in doms:
            vm_matrix_dict = {}
            ms = MetricsService()
            vm_data = ms.getRawCpuAndMemData(dom.id, constants.VM_RAW, from_date, to_date, variance_from_date)
            print '\n------getRawCpuAndMemData------'
            pprint.pprint(vm_data)
            if vm_data:
                sticky = 0
                priority = dom.get_ha_priority()
                max_mem_req = int(dom.get_memory())
                band_width = 0
                vm_matrix_dict['sticky'] = sticky
                vm_matrix_dict['priority'] = priority
                vm_matrix_dict['gain'] = vm_data.get('cpu_util_avg', 0)
                vm_matrix_dict['cost'] = vm_data.get('cpu_util_avg', 0) * vm_data.get('mem_util_avg', 0)
                vm_matrix_dict['cpu_util_variance'] = vm_data.get('cpu_util_var', 0)
                vm_matrix_dict['cpu_util_plus_sigma'] = vm_data.get('cpu_util_avg', 0) + vm_data.get('cpu_util_sum', 0)
                vm_matrix_dict['cpu_util_minus_sigma'] = vm_data.get('cpu_util_avg', 0) - vm_data.get('cpu_util_sum', 0)
                vm_matrix_dict['cpu_util'] = vm_data.get('cpu_util_avg', 0)
                vm_matrix_dict['mem_util'] = vm_data.get('mem_util_avg', 0)
                vm_matrix_dict['max_mem_req'] = max_mem_req
                vm_matrix_dict['band_width'] = band_width
                vm_matrix_dict['source_node_ent'] = source_node_ent
                vm_matrix_dict['dom'] = dom
                vm_matrix_item_list = self.get_ordered_matrix(DWMManager.PS_VM_MATRIX_ORDER, vm_matrix_dict)
                vm_matrix_item_tuple = tuple([tuple(x) for x in vm_matrix_item_list])
                flag = True
                for i,v in enumerate(loaded_vm_matrix):
                    if v <= vm_matrix_item_tuple:
                        loaded_vm_matrix.insert(i, vm_matrix_item_tuple)
                        flag = False
                        break
                if flag:
                    loaded_vm_matrix.append(vm_matrix_item_tuple)
        return loaded_vm_matrix


    def execute_migrate_instructions(self, migrate_instructions, sp_id, policy):
        print '\n========== execute_migrate_instructions START============\n'
        LOGGER.debug('==========DWM ' + policy + ' MIGRATION FUNCTION START============')
        try:
            from stackone.viewModel.TaskCreator import TaskCreator
            from stackone.core.utils.utils import wait_for_task_completion
            print '------Migrate Instructions------'
            pprint.pprint(migrate_instructions)
            instruction_limit = tg.config.get('dwm_migration_instructions_limit')
            limit = 0
            migration_failed = False
            for instruction in migrate_instructions:
                limit += 1
                if self.check_ha_event(sp_id) == False:
                    if limit > instruction_limit:
                        msg = 'DWM Migration instuctions limit %s reached.' % instruction_limit
                        self.msg += '\n' + msg
                        LOGGER.info(msg)
                        break
                    tc = TaskCreator()
                    wait_time = instruction[0].get_wait_time('migrate')
                    msg = 'Migration Task submitted and waiting.'
                    self.msg += '\n' + msg
                    LOGGER.info('%s: Migration Task submitted and waiting' % policy)
                    task_id = tc.migrate_vm(self.auth, [instruction[0].id], instruction[1].id, instruction[2].id, live=None, force=None, all=None, requester=constants.DWM)
                    finished,status = wait_for_task_completion(task_id, wait_time)
                    dwmhis = DWMHistory()
                    dwmhis.sp_id = sp_id
                    dwmhis.policy_name = policy
                    dwmhis.vm_ent_id = instruction[0].id
                    dwmhis.source_ent_id = instruction[1].id
                    dwmhis.dest_ent_id = instruction[2].id
                    dwmhis.time = datetime.now()
                    if finished == True and status == Task.SUCCEEDED:
                        dwmhis.status = True
                        msg = 'Virtual Machine %s successfully migrated from Node %s to Node %s.' % (instruction[0].name, instruction[1].hostname, instruction[2].hostname)
                        self.msg += '\n' + msg
                        LOGGER.info('%s : Virtual Machine %s successfully migrated from Node %s to Node %s' % (policy, instruction[0].name, instruction[1].hostname, instruction[2].hostname))
                    else:
                        migration_failed = True
                        dwmhis.status = False
                        msg = 'Error trying to migrate Virtual Machine %s from Node %s to Node %s.' % (instruction[0].name, instruction[1].hostname, instruction[2].hostname)
                        self.msg += '\n' + msg
                        LOGGER.info('%s : Error trying to migrate Virtual Machine %s from Node %s to Node %s' % (policy, instruction[0].name, instruction[1].hostname, instruction[2].hostname))

                    DBSession.add(dwmhis)
                    transaction.commit()
                    if policy in [DWMManager.POWER_SAVING]:
                        if migration_failed:
                            break
                else:
                    migration_failed = True
                    msg = 'HA is active on ServerPool:%s.' % self.sp_ent.name
                    self.msg += '\n' + msg
                    LOGGER.info('%s: HA is active on ServerPool:%s ' % (policy, self.sp_ent.name))
                    break
            LOGGER.debug('==========DWM ' + policy + ' MIGRATION FUNCTION END============')
            if policy in [DWMManager.POWER_SAVING]:
                if not migration_failed:
                    return dict(success=True, msg='All VMs successfully migrated')
                return dict(success=False, msg='Failed Migration of Some VMs')
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
            raise ex

        

    def powersave_down_vms_migrate_instructions(self, source_node_ent, processed_nodes_ids):
        LOGGER.debug('---- powersave_down_vms_migrate_instructions ------ Start')
        down_vms_migrate_instructions_of_node = []
        vm_ent_ids = [vm_ent.entity_id for vm_ent in source_node_ent.children]
        shutdown_vms = VM.get_shutdown_vms(vm_ent_ids)
        source_node = DBSession.query(ManagedNode).filter(ManagedNode.id == source_node_ent.entity_id).first()
        if shutdown_vms:
            LOGGER.info('%s: Start Migrating Down VMs from Node:%s ' % (DWMManager.POWER_SAVING, source_node.hostname))
            mig_failed = False
            for dom in shutdown_vms:
                dest_node = self.sp.get_allocation_candidate(self.auth,dom,node = source_node,exclude_ids = processed_nodes_ids)
                if dest_node is None:
                    mig_failed = True
                    LOGGER.info('%s:Can not find destination Node for migrate down VM:%s from Node:%s' % (DWMManager.POWER_SAVING, dom.name, source_node.hostname))
                    break
    
                result = utils.check_constraints(dom,dest_node)
                if result:
                    down_vms_migrate_instructions_of_node.append((dom, source_node, dest_node, DWMManager.POWER_SAVING))
                    continue
                mig_failed = True
                LOGGER.info('%s: Constraints Check failed for down VM:%s, Source Node:%s, Destination Node:%s' % (DWMManager.POWER_SAVING, dom.name, source_node.hostname, dest_node.hostname))
                msg = (dom.name,source_node.hostname,dest_node.hostname)
                self.msg += '\n' + msg
                LOGGER.info('%s: Constraints Check failed for down VM:%s, Source Node:%s, Destination Node:%s' % (DWMManager.POWER_SAVING, dom.name, source_node.hostname, dest_node.hostname))
                break
            LOGGER.debug('---- powersave_down_vms_migrate_instructions ------ End')
            if mig_failed:
                LOGGER.debug('%s: One of the down vm migration instruction failed, so can not shutdown Node:%s' % (DWMManager.POWER_SAVING, source_node.hostname))
                return dict(down_vms_mig_instructions=[], can_shutdown=False)
            return dict(down_vms_mig_instructions=down_vms_migrate_instructions_of_node, can_shutdown=True)

        else:
            msg = 'No Down VMs for migrate.'
            self.msg += '\n' + msg
            LOGGER.info('%s: No Down VMs in Node:%s to migrate' % (DWMManager.POWER_SAVING, source_node.hostname))
            return dict(down_vms_mig_instructions=[], can_shutdown=True)
        LOGGER.debug('---- powersave_down_vms_migrate_instructions ------ End')
        return dict(down_vms_mig_instructions=[], can_shutdown=False)


    def powersave_check_can_shutdown_node(self, source_node):
        source_node_ent = DBSession.query(Entity).filter(Entity.entity_id == source_node.id).first()
        vm_ent_ids = [vm_ent.entity_id for vm_ent in source_node_ent.children]
        if self.mig_down_vms:
            if vm_ent_ids:
                mesg = 'Found VMs in Node:%s, so can not shutdown this Node' %source_node.hostname
                LOGGER.info('%s:%s' % (DWMManager.POWER_SAVING, mesg))
                return dict(can_shutdown=False, msg=mesg)
            else:
                mesg = 'No VMs in Node:%s, so can shutdown this Node' %source_node.hostname
        else:
            run_vms = VM.get_running_vms(vm_ent_ids)
            if run_vms:
                mesg = 'Found running VMs in Node:%s, so can not shutdown this Node' % source_node_ent.name
                LOGGER.info('%s:%s' % (DWMManager.POWER_SAVING, mesg))
                return dict(can_shutdown=False, msg=mesg)
            else:
                mesg = 'No running VMs in Node:%s, so can shutdown this Node' % source_node.hostname
        if source_node.is_maintenance():
            mesg = 'Server %s is marked for maintenance' %source_node_ent.hostname
            LOGGER.info(mesg)
            return dict(can_shutdown=False, msg=mesg)
        return dict(can_shutdown=True, msg=mesg)


    def powersave_shutdown_node(self, source_node):
        LOGGER.debug('---- powersave_shutdown_node ------ Start')
        result = self.powersave_check_can_shutdown_node(source_node)
        if result.get('can_shutdown'):
            allowed,info = StateTransition.is_allowed(source_node.id, ManagedNode.POWER_OFF, constants.DWM)
            if allowed == False:
                msg = 'Node:%s can not be shutdown, not allowed' % source_node.hostname
                self.msg += '\n' + msg
                LOGGER.info('%s: Node:%s cannot be shutdown, not allowed.' % (DWMManager.POWER_SAVING, source_node.hostname))
                LOGGER.info(constants.NO_OP + '\n' + str(info['msg']))
            else:
                try:
                    peer_node = self.sp.get_peer_node(exclude_ids=[source_node.id])
                    success,msg = self.shutdown_node(source_node, peer_node)
                    if success:
                        source_node = DBSession.query(ManagedNode).filter(ManagedNode.id == source_node.id).first()
                        source_node.stop_monitoring()
                        DBSession.add(PSDownServers(self.sp_ent.entity_id, source_node.id))
                        transaction.commit()
                        msg = 'Node:%s shutdown.' % source_node.hostname
                        self.msg += '\n' + msg
                        LOGGER.info('%s: Node:%s shutdown' % (DWMManager.POWER_SAVING, source_node.hostname))
                    else:
                        msg = 'Node:%s can not be shutdown, shutdown failed.' % source_node.hostname
                        self.msg += '\n' + msg
                        LOGGER.info('%s: Node:%s cannot be shutdown, shutdown failed' % (DWMManager.POWER_SAVING, source_node.hostname))
                    StateTransition.is_allowed(source_node.id, None, constants.DWM)
                except Exception as e:
                    StateTransition.is_allowed(source_node.id, None, constants.DWM)
                    LOGGER.error(to_str(e))
                    msg = 'Node:%s can not be shutdown.' % source_node.hostname
                    self.msg += '\n' + msg
                    LOGGER.info('%s: Node:%s cannot be shutdown' % (DWMManager.POWER_SAVING, source_node.hostname))
                    raise Exception('Node:%s cannot be shutdown' % source_node.hostname)
        else:
            self.msg += '\n' + result.get('msg')
        LOGGER.debug('---- powersave_shutdown_node ------ End')


    def get_ordered_matrix(self, matrix_order, matrix_dict, l=None):
        try:
            import re
            if l is None:
                l = [[], [], []]
            for i,v in enumerate(matrix_order):
                for j,x in enumerate(v):
                    m = re.match('-', x)
                    if m:
                        res = re.sub('^-', '', x)
                        data = -matrix_dict.get(res)
                    else:
                        data = matrix_dict.get(x)
                    l[i].append(data)
            return l
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
            raise ex


    def get_matrix_index(self, matrix_order):
        try:
            import re
            d = {}
            for i,v in enumerate(matrix_order):
                for j,x in enumerate(v):
                    m = re.match('-', x)
                    if m:
                        res = re.sub('^-', '', x)
                        x = res
                    d[x] = (i, j)
            return d
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
            raise ex

    @classmethod
    def bucketing(cls,data):
        return int(data)*10/10
    
    def get_updated_dest_cpu_util(self, source_node_cores, dest_node_cores, mig_vm_util, dest_node_util):
        try:
            print 'source_node_cores dest_node_cores',
            print source_node_cores,
            print dest_node_cores
            cpu_units_on_source_node = 100 * source_node_cores
            cpu_units_on_dest_node = 100 * dest_node_cores
            cpu_units_on_mig_vm = mig_vm_util * cpu_units_on_source_node / 100
            return dest_node_util + cpu_units_on_mig_vm * 100 / cpu_units_on_dest_node
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
            raise ex


    def get_updated_source_cpu_util(self, source_node_cores, mig_vm_util, source_node_util):
        try:
            cpu_units_on_source_node = 100 * source_node_cores
            cpu_units_on_mig_vm = mig_vm_util * cpu_units_on_source_node / 100
            print 'updated_source ===> source_node_util, resul_source_node_util, cpu_units_on_mig_vm, mig_vm_util, source_node_cores',
            print source_node_util,
            print source_node_util - cpu_units_on_mig_vm * 100 / cpu_units_on_source_node,
            print cpu_units_on_mig_vm,
            print mig_vm_util,
            print source_node_cores
            return source_node_util - cpu_units_on_mig_vm * 100 / cpu_units_on_source_node
        except Exception as ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
            raise ex


    def check_ha_event(self, sp_id):
        ha = DBSession.query(HAEvent).filter(HAEvent.sp_id == sp_id).filter(HAEvent.status.in_([HAEvent.STARTED, HAEvent.IDLE])).first()
        if ha:
            return True
        return False


    def shutdown_node(self, node, peer_node):
        return self.do_fencing(node, peer_node, 'off')

    def start_node(self, auth, node, peer_node):
        LOGGER.debug('Trying to start the Server :' + node.hostname + ' using fencing device')
        success,msg = self.do_fencing(node, peer_node, 'on')
        if success:
            try:
                node_start_time = int(tg.config.get(constants.start_time))
            except Exception as e:
                node_start_time = 180
            now = datetime.now()
            dif = timedelta(seconds=node_start_time)
            end = now + dif
            LOGGER.debug('Waiting for boot server :%s' % node.hostname)
            i = 0
            ping_status = False
            while datetime.now() < end:
                i += 1
                msg = 'Ping Try:' + str(i)
                LOGGER.info(msg)
                status = node.heartbeat()
                if status and status[0] == ManagedNode.UP:
                    msg = 'Node ' + node.hostname + ' came UP.'
                    LOGGER.info(msg)
                    node.current_state.avail_state = ManagedNode.UP
                    transaction.commit()
                    ping_status = True
                    break
                time.sleep(3)
            if ping_status:
                LOGGER.debug('Waiting for network and storage sync in server :%s' % node.hostname)
                node.wait_for_nw_str_sync(auth)
                node = DBSession.query(ManagedNode).filter(ManagedNode.id == node.id).first()
                node.start_monitoring()
                DBSession.add(node)
                transaction.commit()
                return True
            msg = 'Server ' + node.hostname + 'not started .\n Ping Failed.'
            LOGGER.info(msg)
            return False
        else:
            msg = 'Can not start Node ' + node.hostname + '\n' + msg
            LOGGER.info(msg)
            return False

        


    def do_fencing(self, node, peer_node, action):
        if peer_node is None:
            msg = 'Peer node is None. Can not proceed fencing.'
            LOGGER.info(msg)
            return (False, msg)
        msg = 'Trying to Fence using ' + peer_node.hostname
        LOGGER.info(msg)
        devices = DBSession.query(HAEntityResource).filter(HAEntityResource.entity_id == node.id).all()
        msg = ''
        if len(devices) == 0:
            msg = 'No Fencing devices configured.'
            print msg
            LOGGER.info(msg)
        success = False
        for device in devices:
            if device.resource.type.classification != u'Power Fencing Device':
                continue
            fence_action = False
            cmd = device.resource.type.fence_method
            locn = device.resource.type.script_location
            stdin_params = []
            env_params = {}
    
            for param in device.params:
                if param.field == 'action' and param.value == action:
                    fence_action = True
                if param.is_environ == False:
                    stdin_params.append(param.field + '=' + param.value)
                    continue
                env_params[param.field] = param.value
            if fence_action == False:
                continue
            for param in device.resource.params:
                stdin_params.append(param.field + '=' + param.value)
            dirname = os.path.dirname(locn)
    
            try:
                stackone_cache_dir = os.path.join(tg.config.get('stackone_cache_dir'), 'custom/fencing/scripts')
                if not peer_node.node_proxy.file_exists(locn):
                    copyToRemote(locn, peer_node, stackone_cache_dir)
                    dirname = stackone_cache_dir
            except Exception as e:
                traceback.print_exc()
                success = False
                msg += 'Fencing failed using ' + device.resource.name + '\n' + ' Can not copy the fencing script to peer node' + peer_node.hostname + 'Exception:' + to_str(e)
                LOGGER.info(msg)
                continue
            print cmd,'@@@@@@@@@@@@@@@cmd@@@@@@@@@@@@@@@@@@'
            out,exit_code = peer_node.node_proxy.exec_cmd(cmd, dirname, None, stdin_params, cd=True, env=env_params)
            if exit_code != 0:
                success = False
                msg += 'Fencing failed using ' + device.resource.name + '\n' + out
                print 'Fencing failed using ',
                print device.resource.name,
                print '\n',
                print out
                LOGGER.info('Fencing failed using ' + device.resource.name + '\n' + out)
                continue
            success = True
            msg += 'Fencing succeeded using ' + device.resource.name + '\n' + out
            print 'Fencing succeeded using ',
            print device.resource.name,
            print '\n',
            print out
            LOGGER.info('Fencing succeeded using ' + device.resource.name + '\n' + out)
        return (success, msg)


    def create_new_migrate_instructions(self, vm_and_src_server_list, dest_server_id):
        dest_node = DBSession.query(ManagedNode).filter(ManagedNode.id == dest_server_id).first()
        for vm_and_src_server in vm_and_src_server_list:
            vm_and_src_server.append(dest_node)
        return vm_and_src_server_list

    @classmethod
    def find_nodes_below_upper_threshold(cls, sp_id, data_period, upper_threshold):
        try:
            server_ids = []
            sp_ent = DBSession.query(Entity).filter(Entity.entity_id == sp_id).first()
            try:
                variance_fetch_interval = int(tg.config.get('dwm_variance_fetch_interval'))
            except Exception,ex:
                variance_fetch_interval= 30
                LOGGER.error(to_str(ex))
            variance_from_date = datetime.now() - timedelta('minutes',variance_fetch_interval)
            from_date = datetime.now() - timedelta('minutes',data_period)
            to_date = datetime.now()
            node_ent_ids = [node_ent.entity_id for node_ent in sp_ent.children]
            ms = MetricsService()
            for node in ManagedNode.get_up_nodes(node_ent_ids):
                if node.is_maintenance():
                    LOGGER.info('Server %s is marked for maintenance' % node.hostname)
                node_data = ms.getRawCpuAndMemData(node.id,constants.SERVER_RAW,from_date,to_date,variance_from_date)
                if node_data:
                    cpu_util = node_data.get('cpu_util_avg',0)
                    if cpu_util < upper_threshold:
                        server_ids.append(node.id)
            return server_ids
        except Exception,ex:
            traceback.print_exc()
            LOGGER.error(to_str(ex))
            raise ex
        