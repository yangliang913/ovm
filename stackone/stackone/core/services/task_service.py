#!/usr/bin/env python
#
#   stackone   -  Copyright (c) 2009 stackone Corp.
#   ======
#
# stackone is a Virtualization management tool with a graphical user
# interface that allows for performing the standard set of VM operations
# (start, stop, pause, kill, shutdown, reboot, snapshot, etc...). It
# also attempts to simplify various aspects of VM lifecycle management.
#
#
# This software is subject to the GNU General Public License, Version 2 (GPLv2)
# and for details, please consult it at
#
#    http://www.gnu.org/licenses/old-licenses/gpl-2.0.txt
#
#
# author : gizli
#

from stackone.core.services.tasks import *
from stackone.core.services.core import Service, ServiceException
from stackone.core.services.execution_service import ThreadLimitException
from stackone.model.services import Task, TaskInterval, TaskResult, TaskCalendar, TaskUtil
from stackone.model.deployment import Deployment
from datetime import datetime, timedelta
import time
from stackone.core.utils.utils import get_dbtype
import tg
import traceback
from sqlalchemy.orm import eagerload
import logging
logger = logging.getLogger('stackone.services.task_service')
import sys
import traceback
from pygments import highlight
from pygments.lexers import PythonLexer
from pygments.formatters import HtmlFormatter
class TaskManager(Service):

    def check_prior_execution(self, conn, t):
        #async submission requires us to check whether this task has been
        #executed before and whether that execution is still going on
        #We do not submit new executions of repeating tasks unless the prior
        #has completed
        res = conn.query(TaskResult).\
                filter(TaskResult.task_id == t.task_id).\
                filter(TaskResult.status == Task.STARTED).\
                count()
        return (res == 0)


    def check_interval_tasks(self, conn):
        now = datetime.now()
        try:
            for it in conn.query(TaskInterval).options(eagerload('task')).\
                      filter(TaskInterval.next_execution <= now):
                task = it.task
                if self.check_prior_execution(conn, task):
                    self.submit_async(task)
                    if it.interval and it.interval > 0:
                        it.next_execution = datetime.now() + \
                                timedelta(minutes=it.interval)
                    else:
                        #if there is no interval, this is supposed to execute
                        #only once, so delete the interval entry
                        conn.delete(it)
                else:
                    logger.info("The prior execution of task %s has not completed. Delaying the current execution..." % task.name)
        finally:
            conn.commit()

    def check_calendar_tasks(self, conn):
        now = list(time.gmtime())
        tasks = []
        db_type = get_dbtype()
        if db_type == constants.MYSQL:
            tasks = conn.query(TaskCalendar).options(eagerload('task')).filter((TaskCalendar.dow == 0) | TaskCalendar.dow.op('&')(1 << now[6]) > 0).filter((TaskCalendar.month == 0) | TaskCalendar.month.op('&')(1 << now[1]) > 0).filter((TaskCalendar.day == 0) | TaskCalendar.day.op('&')(1 << now[2]) > 0).filter((TaskCalendar.hour == 0) | TaskCalendar.hour.op('&')(1 << now[3]) > 0).filter((TaskCalendar.minute == 0) | TaskCalendar.minute.op('&')(1 << now[4]) > 0)
        if db_type == constants.ORACLE:
            tasks = conn.query(TaskCalendar).options(eagerload('task')).filter((TaskCalendar.dow == 0) | (func.BITAND(TaskCalendar.dow, 1 << now[6]) > 0)).filter((TaskCalendar.month == 0) | (func.BITAND(TaskCalendar.month, 1 << now[1]) > 0)).filter((TaskCalendar.day == 0) | (func.BITAND(TaskCalendar.day, 1 << now[2]) > 0)).filter((TaskCalendar.hour == 0) | (func.BITAND(TaskCalendar.hour, 1 << now[3]) > 0)).filter((TaskCalendar.minute == 0) | (func.BITAND(TaskCalendar.minute, 1 << now[4]) > 0))
        for cal in tasks:
            task = cal.task
            if self.check_prior_execution(conn, task):
                self.submit_async(task)
            else:
                logger.warning('The prior execution of task %s has not completed. Delaying the current execution...' % task.name)

    def update_cms_end_time(self, conn):
        try:
            dep = conn.query(Deployment).first()
            if dep:
                dep.cms_end = datetime.now()
                conn.add(dep)
                conn.commit()
        except Exception as e:
            traceback.print_exc()
            logger.error('Error in updating cms end time: %s' % str(e))
    
    def init(self):
        self.loop_first = True
        try:
            from stackone.core.utils.utils import set_sp_dwm_policies
            set_sp_dwm_policies()
        except Exception as e:
            print 'Error while finding and setting Current DWM policies ',
            print e
        conn = self.get_database_conn()

        try:
            try:
                now = datetime.now()
                crsh_time = None
                recover = False
                for incomplete_task,task_result in conn.query(Task, TaskResult).join(TaskResult).filter(TaskResult.status == Task.STARTED).order_by(TaskResult.timestamp.asc()).all():
                    if crsh_time is None:
                        crsh_time = task_result.timestamp
                        td = now - crsh_time
                        down_time = td.days * 24 * 60 * 60 + td.seconds
                        try:
                            recover_sec = int(tg.config.get(constants.RECOVER_TIME, 1440)) * 60
                        except Exception as e:
                            logger.error('Exception: ' + str(e))
                            recover_sec = 86400
                        if down_time > recover_sec:
                            recover = True
                    self.resume_task(incomplete_task, recover=recover)
            except Exception as e:
                traceback.print_exc()
                logger.error('Error in cleaning up incomplete tasks: %s' % str(e))
        finally:
            conn.close()



    def loop(self):
        #starter
        conn = self.get_database_conn()
        try:
            self.check_interval_tasks(conn)
            self.check_calendar_tasks(conn)
        finally:
            if self.loop_first:
                self.loop_first = False
            else:
                self.update_cms_end_time(conn)
            conn.close()

    def submit_schedule(self, t, execution_time):
        conn = self.get_database_conn()
        try:
            self.set_parent_task(t)
            t.set_interval(TaskInterval(interval=None,
                                       next_execution=execution_time))
            conn.add(t)
            conn.commit()
        finally:
            conn.close()

    def submit_sync(self, t):
        conn = self.get_database_conn()
        try:
            try:
                self.set_parent_task(t)
                conn.add(t)
                conn.commit()
                if not self.submit_task(t, 2):
                    #in case of a failure we submit task asychronously
                    t.set_interval(TaskInterval(interval=None,
                                                next_execution=datetime.now()))
                    conn.commit()
                    raise ServiceException("All worker threads are busy. \
                                        Delaying task submission...")
            except Exception, ex:
                traceback.print_exc()
        finally:
            conn.close()
    def submit_calendertask(self, t):
        conn = self.get_database_conn()
        try:
            try:
                self.set_parent_task(t)
                conn.add(t)
                conn.commit()
            except Exception as ex:
                traceback.print_exc()
        finally:
            conn.close()
    def set_parent_task(self, t):
        prnt_task = TaskUtil.get_task_context()
        if prnt_task is not None:
            t.parent_task_id = prnt_task
        return t

    def submit_async(self, t):
        if not self.submit_task(t):
            conn = self.get_database_conn()
            try:
                t.task_fail_start("Task submission failed because all worker \
                                  threads are occupied. Please increase the \
                                  number of threads.", conn)
                conn.commit()
            finally:
                conn.close()

    def submit_task(self, t, max_sleep_time=\
                int(tg.config.get('services.task.max_sleep', 20))):
        (this_service, target_service) = self.get_bridge("Execution Service")
        runtime_context = [this_service, ]
        sleep_time = 0
        while sleep_time < max_sleep_time:
            try:
                target_service.new_work(t, ctx=runtime_context)
                return True
            except ThreadLimitException:
                traceback.print_exc()
                #self.stacktraces()
                # We try again
                time.sleep(0.5)
                sleep_time = sleep_time + 0.5
        return False    

    def delete_task(self, task_ids):
        conn = self.get_database_conn()
        try:
            conn.query(TaskInterval).filter(TaskInterval.task_id.in_(task_ids)).delete()
            conn.query(TaskResult).filter(TaskResult.task_id.in_(task_ids)).delete()
            conn.query(TaskCalendar).filter(TaskCalendar.task_id.in_(task_ids)).delete()
            conn.query(Task).filter(Task.task_id.in_(task_ids)).delete()
            conn.commit()
        finally:
            conn.close()

    def resume_task(self, t, recover=False, max_sleep_time=\
                int(tg.config.get('services.task.max_sleep', 20))):
        (this_service, target_service) = self.get_bridge("Execution Service")
        runtime_context = [this_service, ]
        sleep_time = 0
        while sleep_time < max_sleep_time:
            try:
                kw = dict(resume=True)
                if recover == True:
                    kw = dict(recover=True)
                target_service.new_work(t, ctx=runtime_context, kw=kw)
                return True
            except ThreadLimitException:
                traceback.print_exc()
                #self.stacktraces()
                # We try again
                time.sleep(0.5)
                sleep_time = sleep_time + 0.5
        return False
    def stacktraces(self):
        code = []
        for threadId,stack in sys._current_frames().items():
            code.append('\n# ThreadID: %s' % threadId)
            for filename,lineno,name,line in traceback.extract_stack(stack):
                code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
                if line:
                    code.append('  %s' % line.strip())
        return highlight('\n'.join(code), PythonLexer(), HtmlFormatter(full=False, noclasses=True))

    def get_running_task_info(self):
        (this_service,target_service) = self.get_bridge('Execution Service')
        active_tasks = target_service.get_running_tasks()
        code = []
        for task in active_tasks:
            code.append(task.get_status())
        return highlight('\n'.join(code), PythonLexer(), HtmlFormatter(full=False, noclasses=True))

    def get_running_task_obj(self, task_id):
        (this_service,target_service) = self.get_bridge('Execution Service')
        return target_service.get_running_task_obj(task_id)

    def clear_running_task_obj(self, task_id):
        (this_service,target_service) = self.get_bridge('Execution Service')
        return target_service.clear_running_task_obj(task_id)

