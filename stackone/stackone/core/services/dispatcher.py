import logging
logger = logging.Logger('stackone.core.services')
from stackone.core.services.core import Service
from stackone.model.events import Event
from stackone.model.events import Subscriber

#PASSED
class DispatcherService(Service):
    #PASSED
    def delete_event(self, conn, id):
        return conn.execute(Event.__table__.delete().where(Event.__table__.c.event_id == id)).rowcount

    #PASSED
    def init(self):
        conn = self.get_database_conn()
        self.subscribers = {}
        for subs in conn.query(Subscriber):
            if self.subscribers.has_key(subs.event_type):
                self.subscribers[subs.event_type].append(subs.cls)
                continue
                
            self.subscribers[subs.event_type] = [subs.cls]
    #PASSED
    def loop(self):
        conn = self.get_database_conn()
        try:
            for ev in conn.query(Event).order_by(Event.timestamp):
                try:
                    num = self.delete_event(conn, ev.event_id)
                    conn.commit()
                    if num == 1:
                        if self.subscribers.has_key(ev.event_type):
                            for cls in self.subscribers[ev.event_type]:
                                cls().notify(ev)
                except Exception as e:
                    logger.error(e)
        finally:
            conn.close()
        

#PASSED
class Subscribable:
    #PASSED
    def notify(self, ev):
        return None
        

