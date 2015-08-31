from stackone.model import DeclarativeBase, Entity, EntityType, DBSession
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.model.DWM import DWMPolicySchedule, DWM, SPDWMPolicy
from stackone.model.Groups import ServerGroup
import simplejson as json
import stackone.core.utils.utils
utils = stackone.core.utils.utils
constants = stackone.core.utils.constants
from datetime import datetime, timedelta
import transaction
import traceback
import tg
from stackone.core.utils.utils import to_unicode, to_str, get_minute_string

class DWMService():
    #PASSED
    def __init__(self):
        self.tc = None
        self.utcoffset = None

    #PASSED
    def get_group(self, auth, group_id):
        return DBSession.query(ServerGroup).filter(ServerGroup.id == group_id).first()

    #PASSED
    def get_dwm_details(self, auth, group_id):
        info = []
        group = self.get_group(auth, group_id)
        if group:
            dwm_enabled = group.dwm_enabled
            dwms = DBSession.query(DWM).filter(DWM.sp_id == group_id).all()
            for dwm in dwms:
                schedule = self.get_dwm_schedule_details(group_id, dwm.id)
                info.append(dict(policy_id=dwm.id, policy=dwm.policy, frequency=dwm.frequency, data_period=dwm.data_period, threshold=dwm.threshold, scobject=schedule, enabled=dwm.enabled, up_threshold=dwm.upper_threshold, dwm_enabled=dwm_enabled))

        return info


    #PASSED
    def get_dwm_schedule_details(self, group_id, policy_id):
        info = []
        schedules = self.get_dwm_schedule(group_id, policy_id)
        for schedule in schedules:
            sch = {}
            sch['type'] = schedule.type
            sch['starttime'] = schedule.start_time
            sch['duration'] = schedule.duration
            if schedule.type == 'Daily':
                day = 'Daily'
            elif schedule.type == 'Weekly':
                day = schedule.weekdays_list
                sch['dows'] = schedule.dows
                sch['weekdays_list'] = day

            sch['day'] = day
            info.append(sch)
            
        return info


    #PASSED
    def get_dwm_schedule(self, group_id, policy_id):
        schedules = DBSession.query(DWMPolicySchedule).filter(DWMPolicySchedule.policy_id == policy_id).filter(DWMPolicySchedule.sp_id == group_id).all()
        return schedules

    #PASSED
    def save_dwm_details(self, auth, group_id, policy_object, enabled, offset):
        try:
            self.tc = TaskCreator()
            self.utcoffset = timedelta(milliseconds=long(offset))
            group = self.get_group(auth, group_id)
            
            if enabled == 'true':
                dwm_list = DBSession.query(DWM).filter(DWM.sp_id == group_id).all()
                task_ids = []
                interval_task_ids = []
                dwmelems = {}
                
                for dwmelem in dwm_list:
                    interval_task_ids.append(dwmelem.interval_task_id)
                    if dwmelem.calendar_task_ids:
                        task_ids.extend(dwmelem.calendar_task_ids)
                
                    dwmelem.enabled = False
                    dwmelems[dwmelem.policy] = dwmelem
                
                if task_ids:
                    self.tc.delete_task(task_ids)
                
                policy_obj = json.loads(policy_object)
                policies = policy_obj['policy_object']['policies']
                freq = 5
                dwms = []
                schedules = []
                
                for policy in policies:
                    dwmelem = dwmelems.get(policy['policy_name'])
                    if dwmelem != None:
                        dwmelem.enabled = True
                
                    (dwm, policy_schedules) = self.save_dwm_policy(auth, group_id, policy['threshold'], policy['frequency'], policy['data_period'], policy['upper_threshold'], policy['policy_name'], policy['schedule_object'])
                    freq = policy['frequency']
                    dwms.append(dwm)
                    schedules.extend(policy_schedules)
                    
                sp_dwm = SPDWMPolicy(group_id, None)
                DBSession.merge(sp_dwm)
                if interval_task_ids:
                    self.tc.delete_task(interval_task_ids)
                
                interval_task_id = self.tc.dwm_task(auth, group_id, freq)
                
                for d in dwms:
                    d.interval_task_id = interval_task_id
                    DBSession.add(d)
                    
                group.dwm_enabled = True
                DBSession.add(group)
                transaction.commit()
                DBSession.add_all(schedules)
                transaction.commit()
                DBSession.query(DWM).filter(DWM.sp_id == group_id).update(dict(interval_task_id=interval_task_id))
                pol = DWM.find_current_policy(group_id)
                if pol and pol.is_enabled():
                    sp_dwm = SPDWMPolicy.set_sp_current_policy(group_id, pol.policy, SPDWMPolicy.ON)
                
                return True
            
            result = self.delete_dwm_tasks(auth, group_id)
            DBSession.query(DWM).filter(DWM.sp_id == group_id).update(dict(interval_task_id=None, calendar_task_ids=None))
            group.dwm_enabled = False
            DBSession.add(group)
            sp_dwm = SPDWMPolicy(group_id, None)
            DBSession.merge(sp_dwm)
            return result
        
        except Exception as ex:
            traceback.print_exc()
            raise ex
 
 
    #PASSED
    def save_dwm_policy(self, auth, group_id, threshold, frequency, data_period, upper_threshold, policyname, schedule_object):
        try:
            dwm = DBSession.query(DWM).filter(DWM.sp_id == group_id).filter(DWM.policy == policyname).first()
            if dwm:
                dwm.threshold = threshold
                dwm.frequency = frequency
                dwm.data_perod = data_period
                dwm.upper_threshold = upper_threshold
            else:
                dwm = DWM(group_id, policyname, threshold, frequency, data_period)

            (calendar_task_ids, policy_schedules) = self.add_dwm_policy_schedule(auth, group_id, dwm.id, policyname, schedule_object)
            dwm.calendar_task_ids = calendar_task_ids
            dwm.upper_threshold = upper_threshold
            dwm.enabled = True
            return (dwm, policy_schedules)  

        except Exception as ex:
            traceback.print_exc()
            raise ex


    #PASSED
    def add_dwm_policy_schedule(self, auth, sp_id, policy_id, policy_name, schedules):
        try:
            start_schedule_list = []
            end_schedule_list = []
            calendar_task_ids = []
            tot_shedules = []
            policy_schedules = []
            for schedule in schedules:
                policy_schedule = DWMPolicySchedule()
                policy_schedule.policy_id = policy_id
                policy_schedule.sp_id = sp_id
                policy_schedule.type = schedule['type']
                policy_schedule.start_time = schedule['starttime']
                policy_schedule.duration = schedule['duration']
                timeparts = schedule['starttime'].split(':')
                hr = int(timeparts[0])
                min = int(timeparts[1])
                durn = int(schedule['duration'])
                start = float(timeparts[0] + '.' + timeparts[1])
                end = start
                today = datetime.now()
                start_day = datetime(today.year, today.month, today.day, hr, min)
                start_day = start_day + self.utcoffset
                occurance = schedule['type']
                if occurance == DWMPolicySchedule.WEEKLY:
                    weekday_string = schedule['weekdays_list']
                    policy_schedule.weekdays_list = weekday_string
                    dows_list = schedule['dows']
                    dows = dows_list
                    policy_schedule.dows = dows
                    utc_dows = []
                    for dow in dows:
                        dow = int(dow)
                        while start_day.weekday() != dow:
                            start_day += timedelta(days=1)
                        
                        utc_dows.append(start_day.weekday())
                        end_day = start_day + timedelta(hours=durn)
                        start_schedule_elem = dict(occurance=occurance, dow=dow, start_day=[dow], hour=start_day.hour, minute=start_day.minute)
                        end_schedule_elem = dict(occurance=occurance, dow=end_day.weekday(), start_day=[dow], hour=end_day.hour, minute=end_day.minute)
                        start_schedule_list.append(start_schedule_elem)
                        end_schedule_list.append(end_schedule_elem)
                    
                    policy_schedule.utc_days_list = utc_dows
                
                if occurance == DWMPolicySchedule.DAILY:
                    end_day = start_day + timedelta(hours=durn)
                    start_schedule_elem = dict(occurance=occurance, hour=start_day.hour, minute=start_day.minute)
                    end_schedule_elem = dict(occurance=occurance, hour=end_day.hour, minute=end_day.minute)
                    start_schedule_list.append(start_schedule_elem)
                    end_schedule_list.append(end_schedule_elem)
                
                end = float(str(end_day.hour) + '.' + get_minute_string(end_day.minute))
                start = float(str(start_day.hour) + '.' + get_minute_string(start_day.minute))
                policy_schedule.start = start
                policy_schedule.end = end
                policy_schedule.hour = start_day.hour
                policy_schedule.minute = start_day.minute
                policy_schedules.append(policy_schedule)
                tot_shedules.append(dict(policy_schedule=policy_schedule, start=start_schedule_elem, end=end_schedule_elem))
            
            for policy_sch in policy_schedules:
                for sch in tot_shedules:
                    if sch.get('policy_schedule') != policy_sch:
                        print '\n\n++++++++++++++++++++++++++++++++++++check_overlapping_schedules'
                        if DWM.check_overlapping_schedules([sch.get('start')], [policy_sch], 'start', True) == True:
                            if DWM.check_overlapping_schedules([sch.get('end')], [policy_sch], 'end', True) == True:
                                raise Exception('Overlapping schedules within a Policy is not allowed.')
                                
            self.delete_dwm_schedule_details(policy_id, sp_id)
            calendar_task_ids.append(self.tc.dwm_calendar_task(auth, sp_id, policy_name, SPDWMPolicy.ON, start_schedule_list))
            calendar_task_ids.append(self.tc.dwm_calendar_task(auth, sp_id, policy_name, SPDWMPolicy.OFF, end_schedule_list))
            return (calendar_task_ids, policy_schedules)
            
        except Exception as ex:
            traceback.print_exc()
            raise ex
            
    #PASSED
    def delete_dwm_tasks(self, auth, group_id):
        try:
            task_ids = []
            dwms = DBSession.query(DWM).filter(DWM.sp_id == group_id).all()
            for dwm in dwms:
                task_ids.append(dwm.interval_task_id)
                if isinstance(dwm.calendar_task_ids, list):
                    task_ids.extend(dwm.calendar_task_ids)

            if task_ids:
                self.tc.delete_task(task_ids)

            return True
        except Exception as ex:
            traceback.print_exc()
            raise ex


    #PASSED
    def delete_dwm_schedule_details(self, policy_id, group_id):
        try:
            dwm_schedules = DBSession.query(DWMPolicySchedule).filter(DWMPolicySchedule.sp_id == group_id).filter(DWMPolicySchedule.policy_id == policy_id).delete()
            return True
        except Exception as ex:
            traceback.print_exc()
            raise ex
    @classmethod
    def delete_dwm_details(cls, group_id):
        try:
            task_ids = []
            policy_ids = []
            dwms = DBSession.query(DWM).filter(DWM.sp_id == group_id).all()
            for dwm in dwms:
                task_ids.append(dwm.interval_task_id)
                if isinstance(dwm.calendar_task_ids,list):
                    task_ids.extend(dwm.calendar_task_ids)
                policy_ids.append(dwm.id)
            if policy_ids:
                tc = TaskCreator()
                DBSession.query(DWMPolicySchedule).filter(DWMPolicySchedule.policy_id.in_(policy_ids)).delete()
                DBSession.query(SPDWMPolicy).filter(SPDWMPolicy.sp_id == group_id).delete()
                DBSession.query(DWM).filter(DWM.id.in_(policy_ids)).delete()
                tc.delete_task(task_ids)
            return True
        except Exception,ex:
            traceback.print_exc()




