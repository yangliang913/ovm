from stackone.model.Entity import Entity
from stackone.core.ha.ha_main import HA
from stackone.core.ha.ha_register import HAEvent
from stackone.core.services.core import Service, ServiceException
from stackone.core.services.execution_service import ThreadLimitException
from datetime import datetime, timedelta
from stackone.model.Groups import ServerGroup
from stackone.model.Authorization import AuthorizationService
from stackone.model.auth import User
from stackone.viewModel.TaskCreator import TaskCreator
import time
import logging
LOGGER = logging.getLogger('HA')
class HAManager(Service):
    def init(self):
        pass

    def loop(self):
        conn = self.get_database_conn()
        try:
            self.process_ha_events(conn)
        except Exception as e:
            import traceback
            traceback.print_exc()
        finally:
            conn.close()

    def process_ha_events(self, conn):
        try:
            tc = TaskCreator()
            auth = AuthorizationService()
            auth.user = User.by_user_name(u'admin')
            grps = conn.query(ServerGroup).all()
            for grp in grps:
                running_ha_evts = conn.query(HAEvent).filter(HAEvent.status == HAEvent.STARTED).filter(HAEvent.sp_id == grp.id).all()
                if running_ha_evts:
                    continue
                ha_events = conn.query(HAEvent).filter(HAEvent.status == HAEvent.IDLE).filter(HAEvent.sp_id == grp.id).order_by(HAEvent.event_id.asc()).all()
                if len(ha_events) > 0:
                    tc.ha_action(auth, grp.id, grp.name)
        finally:
            conn.commit()



__author__ = 'root'
__date__ = '$Feb 9, 2010 7:21:22 PM$'
if __name__ == '__main__':
    print 'Hello'
