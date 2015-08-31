from stackone.model import DeclarativeBase, metadata, DBSession
from sqlalchemy import Column, Integer, String, Table
from sqlalchemy.types import Text
from sqlalchemy import ForeignKey, DateTime, PickleType, Boolean, Unicode
from sqlalchemy.orm import relation, backref, eagerload
from sqlalchemy.ext.declarative import DeclarativeMeta
from sqlalchemy.schema import Index, Sequence
try:
    import sqlalchemy
    MSBigInteger = eval('sqlalchemy.types.BigInteger')
except Exception as e:
    from sqlalchemy.databases.mysql import MSBigInteger
from datetime import datetime, timedelta
from stackone.model.Authorization import AuthorizationService
from stackone.model.Entity import Entity
from stackone.model.auth import User, Group
from stackone.model.UpdateManager import UIUpdateManager
from stackone.model.notification import Notification
from stackone.model.LDAPManager import LDAPManager
import transaction
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.utils
constants = stackone.core.utils.constants
import logging
logger = logging.getLogger('stackone.services.model')
ImmutablePickleType = PickleType(mutable=False)
from sqlalchemy.databases.mysql import MSMediumBlob
class MediumPickle(PickleType):
    impl = MSMediumBlob


class PolymorphicSetter(DeclarativeMeta):
    def __new__(cls, name, bases, dictionary):
        if '__mapper_args__' in dictionary.keys():
            dictionary['__mapper_args__']['polymorphic_identity'] = to_unicode(name)
        else:
            dictionary['__mapper_args__'] = dict(polymorphic_identity=to_unicode(name))
        return DeclarativeMeta.__new__(cls, name, bases, dictionary)



class Processor():
    def process_output(self, results):
        pass



class Task(DeclarativeBase):
    __tablename__ = 'tasks'
    __metaclass__ = PolymorphicSetter
    SHORT_DESC_KEY = 'shortDesc'
    DESC_KEY = 'description'
    SHORT_DESC_PARAMS_KEY = 'shortDescParams'
    DESC_PARAMS_KEY = 'descParams'
    IDLE = 0L
    STARTED = 1L
    FAILED = 2L
    SUCCEEDED = 3L
    CANCELED = 4L
    TASK_STATUS = {IDLE: 'Not Started', STARTED: 'Started', FAILED: 'Failed', SUCCEEDED: 'Succeeded', CANCELED: 'Canceled'}
    task_id = Column(Integer, Sequence('task_id_seq'), primary_key=True)
    task_type = Column(Unicode(50L), default=to_unicode('Task'))
    name = Column(Unicode(256L))
    entity_id = Column(Unicode(50L))
    entity_name = Column(Unicode(255L))
    entity_type = Column(Integer)
    short_desc = Column(Text)
    long_desc = Column(Text)
    context = Column(PickleType)
    params = Column(PickleType)
    kw_params = Column(PickleType)
    processors = Column(ImmutablePickleType)
    user_name = Column(Unicode(255L))
    submitted_on = Column(DateTime)
    repeating = Column(Boolean)
    cancellable = Column(Boolean, default=False)
    parent_task_id = Column(Integer)
    __mapper_args__ = {'polymorphic_on': task_type}
    def __init__(self, name, context, params, kw_params, processors, user_name):
        self.name = name
        self.context = context
        self.params = params
        self.kw_params = kw_params
        self.processors = processors
        self.user_name = user_name
        self.submitted_on = datetime.now()
        descriptions = self.get_descriptions()
        if descriptions is not None:
            (short_desc,short_desc_params,desc,desc_params) = descriptions
            self.set_short_desc(short_desc, short_desc_params)
            self.set_desc(desc, desc_params)
        self.repeating = False

    def __repr__(self):
        return '<Task: name=%s>' % self.name

    def get_param(self, name):
        if self.kw_params is not None and name in self.kw_params:
            return self.kw_params[name]
        return None

    def get_context_param(self, name):
        if self.context is not None and name in self.context:
            return self.context[name]
        return None

    def set_short_desc(self, desc, desc_params):
        self.context[self.SHORT_DESC_KEY] = desc
        self.context[self.SHORT_DESC_PARAMS_KEY] = desc_params
        self.short_desc = desc % desc_params

    def set_desc(self, desc, desc_params):
        self.context[self.DESC_KEY] = desc
        self.context[self.DESC_PARAMS_KEY] = desc_params
        self.long_desc = desc % desc_params

    def get_short_desc(self):
        if self.context is not None and self.SHORT_DESC_KEY in self.context:
            return (self.context[self.SHORT_DESC_KEY], self.context[self.SHORT_DESC_PARAMS_KEY])
        return None

    def is_cancellable(self):
        return self.cancellable

    def is_finished(self):
        results = self.result
        if results:
            res = results[0L]
            if res.status in [self.FAILED, self.SUCCEEDED, self.CANCELED]:
                return True
        return False

    def is_failed(self):
        results = self.result
        if results:
            res = results[0L]
            if res.status in [self.FAILED, self.CANCELED]:
                return True
        return False

    def is_cancel_requested(self):
        result = self.get_running_instance()
        if result:
            return result.cancel_requested
        return False

    def request_cancel(self):
        result = self.get_running_instance()
        if result:
            result.cancel_requested = True
            return True
        raise Exception('Task is not running. Can not cancel the task.')

    def get_running_instance(self):
        result = DBSession.query(TaskResult).filter(TaskResult.status == self.STARTED).filter(TaskResult.task_id == self.task_id).first()
        return result

    def set_entity_details(self, ent_id):
        ent = DBSession.query(Entity).filter(Entity.entity_id == ent_id).first()
        if ent is not None:
            self.entity_id = ent.entity_id
            self.entity_type = ent.type_id
            self.entity_name = ent.name
        return None

    def set_entity_info(self, ent):
        if ent is not None:
            self.entity_id = ent.entity_id
            self.entity_type = ent.type_id
            self.entity_name = ent.name
        return None

    def get_task_result_instance(self):
        return DBSession.query(TaskResult).filter(TaskResult.task_id == self.task_id).first()

    @classmethod
    def get_task(cls,task_id):
        task=None
        try:
            transaction.begin()
            # Bug : 993 : high cpu : removing eager load
            #task=DBSession.query(cls).filter(cls.task_id==task_id).\
            #        options(eagerload("result")).first()
            task=DBSession.query(cls).filter(cls.task_id==task_id).first()
        except Exception,ex:
            logger.error(to_str(ex).replace("'",""))
            traceback.print_exc()
            transaction.abort()
        else:
            transaction.commit()
        return task
    
    def get_desc(self):
        if self.context is not None and self.DESC_KEY in self.context:
            return (self.context[self.DESC_KEY], self.context[self.DESC_PARAMS_KEY])
        return None

    def cancel(self):
        pass

    def exec_task(self, auth, context, *args, **kw):
        raise Exception('exec_task needs to be implemented')

    def resume_task(self, auth, context, *args, **kw):
        raise Exception(constants.INCOMPLETE_TASK + 'resume not implemented.' + str(self.name) + ':' + str(self.task_id))

    def recover_task(self, auth, context, *args, **kw):
        raise Exception(constants.INCOMPLETE_TASK + 'recover not implemented.' + str(self.name) + ':' + str(self.task_id))

    def get_descriptions(self):
        raise Exception('get_descriptions needs to be implemented')

    def get_entity_ids(self):
        return self.entity_id

    def do_work(self, runtime_context, args=None, kw=None):
        self.task_manager = runtime_context.pop()
        self.curr_instance = datetime.now()
        args = self.params
        (recover, resume) = (False, False)
        visible = False
        if kw:
            resume = kw.get('resume', False)
            recover = kw.get('recover', False)
        kw = self.kw_params
        self.quiet = self.get_context_param('quiet') == True
        if not self.quiet and resume == False and recover == False:
            self.task_started()
#        cancelled = False
#        results = None
        try:
            #1487
            try:
                #1359
                task_result_running_instance = True
                if not args:
                    args = []
                if not kw:
                    kw = {}
                auth = AuthorizationService()
                auth.email_address = ''
                user = User.by_user_name(self.user_name)
                auth.user = user
                if user is None:
                    #564
                    u = User.by_user_name(u'admin')
                    auth.email_address = u.email_address
                    logger.info('User: ' + str(self.user_name) + ' does not exist in CMS.')
                    result = LDAPManager().validate_user(self.user_name)
                    if result['success'] == True:
                        #523
                        group_names = result['group']
                        groups = Group.by_group_names(group_names)
                        if not groups:
                            #465
                            msg = 'Groups: ' + str(group_names) + ' does not exist in CMS.'
                            logger.info(msg)
                            raise Exception(msg)
                        #561--598
                        else:
                            auth.user_name = self.user_name
                            auth.groups = groups
                            if result.get('email_address'):
                                auth.email_address = result['email_address']
                        #598
                    else:
                        logger.info(result['msg'])
                        raise Exception('Error in LDAP chcek: ' + result['msg'])
                    #598
                else:
                    auth.user = user
                    auth.user_name = user.user_name
                    auth.email_address = user.email_address
                #598
                TaskUtil.set_task_context(self.task_id)
                if recover != True and resume != True:
                    raw_result = self.exec_task(auth, self.context, *args, **kw)
                    #884
                else:
                    #884
                    runn = self.get_running_instance()
                    if runn:
                        self.curr_instance = runn.timestamp
                        #785
                    else:
                        #785
                        task_result = self.get_task_result_instance()
                        if isinstance(task_result.results, str):
                            task_result.results += 'can not resume task. No running instance'
                            #779
                        else:
                            #779
                            if not task_result.results:
                                task_result.results = 'can not resume task. No running instance'
                        task_result_running_instance = False
                    if task_result_running_instance:
                        #883
                        if recover == True:
                            raw_result = self.recover_task(auth, self.context, *args, **kw)
                            #884
                        else:
                            if resume == True:
                                raw_result = self.resume_task(auth, self.context, *args, **kw)
                if task_result_running_instance:
                    #1354
                    cancelled = False
                    results = raw_result
                    if isinstance(raw_result, dict):
                        #1152
                        if raw_result.get('status') == constants.TASK_CANCELED:
                            #1031
                            e = raw_result.get('msg') + '\n' + raw_result.get('results')
                            transaction.abort()
                            cancelled = True
                            if not self.quiet:
                                self.task_fail(e, auth, cancelled=True)
                            #1094
                        else:
                            if raw_result.get('status') == Task.SUCCEEDED:
                                results = raw_result.get('results')
                                visible = raw_result.get('visible', False)

                        if type(results)==dict:
                            #1148
                            if results.get('success')==True:
                                results = 'Task Completed Successfully.'

                    else:
                        #1355
                        if raw_result is not None and self.processors is not None:
                            #1250
                                #isinstance(raw_result, dict)
                            results = [raw_result]
                            for p in self.processors:
                                #1246
                                if issubclass(p, Processor):
                                    p().process_output(results)
                        else:
                            results = raw_result
                        if results is None:
                            #1340
                            desc_tuple = self.get_short_desc()
                            if desc_tuple is None:
                                results = 'Task Completed Successfully.'
                            else:
                                short_desc,short_desc_params = desc_tuple
                                desc = short_desc % short_desc_params
                                results = desc + ' Completed Successfully.'
                        transaction.commit()
            except Exception as e:
                logger.exception(to_str(e))
                transaction.abort()
                if not self.quiet:
                    self.task_fail(e, auth)
            else:
                if not self.quiet and cancelled == False:
                    self.task_success(results, visible)
        finally:
            DBSession.remove()
        return None
        


    def task_started(self):
        conn = self.task_manager.get_database_conn()
        try:
            res = TaskResult(self.task_id, self.curr_instance, self.STARTED, None)
            conn.add(res)
            conn.commit()
            if not self.repeating and self.entity_id != None:
                UIUpdateManager().set_updated_tasks(self.task_id, self.user_name, self.entity_id)
        finally:
            conn.close()
        return None

    def task_fail_start(self, exception, conn):
        results = to_str(exception)
        self.curr_instance = datetime.now()
        res = TaskResult(self.task_id, self.curr_instance, self.FAILED, results)
        u = User.by_user_name(self.user_name)
        if u is None:
            u = User.by_user_name(u'admin')
        email = u.email_address
        notification = Notification(to_unicode(self.task_id), self.name, self.curr_instance, results, self.user_name, email)
        conn.merge(res)
        conn.add(notification)
        if not self.repeating and self.entity_id != None:
            UIUpdateManager().set_updated_tasks(self.task_id, self.user_name, self.entity_id)
        return None

    def task_fail(self, exception, auth, cancelled=False):
        conn = self.task_manager.get_database_conn()
        try:
            fail_status = self.FAILED
            if cancelled == True:
                fail_status = self.CANCELED
            results = to_str(exception)
            res = TaskResult(self.task_id, self.curr_instance, fail_status, results, cancel_requested=cancelled)
            email = auth.email_address
            if email:
                notification = Notification(to_unicode(self.task_id), self.name, self.curr_instance, results, self.user_name, email)
                conn.add(notification)
            conn.merge(res)
            conn.commit()
            if not self.repeating and self.entity_id != None:
                UIUpdateManager().set_updated_tasks(self.task_id, self.user_name, self.entity_id)
        finally:
            self.clear_running_task_obj()
            conn.close()
        return None

    def task_success(self, results, visible):
        conn = self.task_manager.get_database_conn()
        try:
            res = TaskResult(self.task_id, self.curr_instance, self.SUCCEEDED, results, visible=visible)
            conn.merge(res)
            conn.commit()
            if not self.repeating and self.entity_id != None or visible == True:
                UIUpdateManager().set_updated_entities(self.get_entity_ids())
                UIUpdateManager().set_updated_tasks(self.task_id, self.user_name, self.entity_id)
        finally:
            self.clear_running_task_obj()
            conn.close()
        return None

    def update_exec_context(self, key, context):
        conn = self.task_manager.get_database_conn()
        try:
            res = conn.query(TaskResult).filter(TaskResult.task_id == self.task_id).filter(TaskResult.timestamp == self.curr_instance).one()
            if res.exec_context is None:
                res.exec_context = {}
            res.exec_context[key] = context
            conn.commit()
        finally:
            conn.close()
        return None

    def set_interval(self, interval):
        if self.interval is None:
            self.interval = []
        self.interval.append(interval)
        self.repeating = (interval.interval is not None and interval.interval > 0)
        return None

    def set_calendar(self, calendar):
        if self.calendar is None:
            self.calendar = []
        self.calendar.append(calendar)
        self.repeating = True
        return None

    def set_frequency(self, frequency):
        if self.interval:
            self.interval[0L].interval = frequency

    def get_status(self):
        stat = ''
        stat += '\n# TaskName: %s' % self.name
        now = datetime.now()
        res = self.get_running_instance()
        stat += '\nID: "%s", ParentTask: "%s" SubmittedTime: "%s"' % (self.task_id, self.parent_task_id, self.submitted_on)
        if res:
            durn = str((now - res.timestamp).seconds) + '.' + str((now - res.timestamp).microseconds)
            stat += '\nStartTime: "%s", RunningFor: "%s"' % (res.timestamp, durn)
        return stat

    def clear_running_task_obj(self):
        try:
            self.task_manager.clear_running_task_obj(self.task_id)
        except Exception as e:
            logger.error('Error clearing task obj from memory. ' + str(e))



Index('task_eid_time_uname', Task.entity_id, Task.submitted_on, Task.user_name)
class TaskResult(DeclarativeBase):
    __tablename__ = 'task_results'
    task_id = Column(Integer, ForeignKey('tasks.task_id'), primary_key=True)
    timestamp = Column(DateTime, primary_key=True)
    endtime = Column(DateTime)
    status = Column(Integer)
    results = Column(MediumPickle)
    exec_context = Column(PickleType)
    cancel_requested = Column(Boolean, default=False)
    visible = Column(Boolean, default=False)
    task = relation(Task, backref=backref('result'))
    def __init__(self, task_id, timestamp, status, results, exec_context={}, cancel_requested=False, visible=False):
        self.task_id = task_id
        self.timestamp = timestamp
        self.endtime = datetime.now()
        self.status = status
        self.results = results
        self.exec_context = exec_context
        self.cancel_requested = cancel_requested
        self.visible = visible

    def is_finished(self):
        if self.status in [Task.FAILED, Task.SUCCEEDED, Task.CANCELED]:
            return True
        return False

    @classmethod
    def get_task_result_instance(cls, task_id):
        return DBSession.query(cls).filter(cls.task_id == task_id).first()
        
    def __repr__(self):
        return '<Task with id %s and timestamp %s returned %s>' % (self.task_id, self.timestamp, self.status)



Index('tr_composite', TaskResult.task_id, TaskResult.timestamp, TaskResult.status, TaskResult.visible)
class TaskInterval(DeclarativeBase):
    __doc__ = ' The TaskInterval entity defines regularly scheduled\n    items which execute at intervals. It can also optionally define\n    one time execution by passing an interval value of <= 0. Such interval\n    objects will be deleted after the first execution.\n    '
    __tablename__ = 'task_intervals'
    cal_id = Column(Integer, Sequence('cal_id_seq'), primary_key=True)
    task_id = Column(Integer, ForeignKey(Task.task_id, ondelete='CASCADE'))
    interval = Column('task_interval', Integer)
    next_execution = Column(DateTime)
    task = relation(Task, backref=backref('interval'))
    def __init__(self, interval, next_execution=None):
        self.interval = interval
        if next_execution:
            self.next_execution = next_execution
        else:
            if interval is not None and interval > 0:
                self.next_execution = datetime.now() + timedelta(minutes=interval)
            else:
                raise Exception('Either define a non-zero interval or a next execution timestamp')



Index('ti_ne', TaskInterval.next_execution)
class TaskCalendar(DeclarativeBase):
    __tablename__ = 'task_calendars'
    cal_id = Column(Integer, Sequence('cal_id_seq'), primary_key=True)
    task_id = Column(Integer, ForeignKey('tasks.task_id'))
    dow = Column(Integer)
    month = Column(Integer)
    day = Column(MSBigInteger)
    hour = Column(Integer)
    minute = Column(MSBigInteger)
    task = relation(Task, backref=backref('calendar'))
    def create_bits(self, numbers):
        k = 0
        for n in numbers:
            if n > 60 or n < 0:
                continue
            k = k | 1 << n
        return k

    def reverse_bits(self, number):
        ret_val = []
        if number == 0L:
            return ret_val
        for n in range(0L, 60L):
            if number & 1L << n != 0L:
                ret_val.append(n)
                continue
        return ret_val

    def get_dow(self):
        return self.reverse_bits(self.dow)

    def get_month(self):
        return self.reverse_bits(self.month)

    def get_day(self):
        return self.reverse_bits(self.day)

    def get_hour(self):
        return self.reverse_bits(self.hour)

    def get_minute(self):
        return self.reverse_bits(self.minute)

    def __init__(self, dow, month, day, hour, minute):
        self.dow = self.create_bits(dow)
        self.month = self.create_bits(month)
        self.day = self.create_bits(day)
        self.hour = self.create_bits(hour)
        self.minute = self.create_bits(minute)



Index('tc_ne', TaskCalendar.dow, TaskCalendar.month, TaskCalendar.day, TaskCalendar.hour, TaskCalendar.minute)
Dependencies_table = Table('dependencies', metadata, Column('dependent_id', Integer, ForeignKey('services.id'), primary_key=True), Column('parent_id', Integer, ForeignKey('services.id'), primary_key=True))
class ServiceItem(DeclarativeBase):
    __tablename__ = 'services'
    id = Column(Integer, primary_key=True)
    name = Column(Unicode(255L))
    type = Column(ImmutablePickleType)
    executor = Column(ImmutablePickleType)
    enabled = Column(Boolean)
    dependents = relation('ServiceItem', secondary=Dependencies_table, primaryjoin=id == Dependencies_table.c.parent_id, secondaryjoin=Dependencies_table.c.dependent_id == id)
    parents = relation('ServiceItem', secondary=Dependencies_table, primaryjoin=id == Dependencies_table.c.dependent_id, secondaryjoin=Dependencies_table.c.parent_id == id)
    def __init__(self, name, type, executor, enabled):
        self.name = name
        self.type = type
        self.executor = executor
        self.enabled = enabled

    def __repr__(self):
        return '<Service: %s>' % self.name



Index('ser_name', ServiceItem.name)
import threading
class TaskUtil():
    local = threading.local()
    
    @classmethod
    def set_task_context(cls,task_id):
        cls.local.task_id = task_id

    @classmethod
    def get_task_context(cls):
        try:
            return cls.local.task_id
        except Exception, e:
            pass
        return None

    @classmethod
    def is_cancel_requested(cls):
        tid=cls.get_task_context()
        if tid:
            task=Task.get_task(tid)
            if task:
                return task.is_cancel_requested()
        return False


