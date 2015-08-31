from stackone.model.AvailabilityWorker import AvailabilityWorker
from stackone.model.Entity import Entity, EntityType
from stackone.model import DBSession
import traceback
import logging
import stackone.core.utils.constants
constants = stackone.core.utils.constants
logger = logging.getLogger('stackone.model')
class VMAvailabilityWorker(AvailabilityWorker):
    def __init__(self, auth):
        AvailabilityWorker.__init__(self, auth)
        self.worker = constants.VM_AVAILABILITY

    def get_task(self, auth, node_ids):
        try:
            from stackone.core.services.tasks import VMAvailability
            user_name = auth.user.user_name
            t = VMAvailability(u'Update vm availability', {}, [], dict(node_ids=node_ids), None, user_name)
            dc_ent = DBSession.query(Entity).filter(Entity.type_id == EntityType.DATA_CENTER).first()
            t.set_entity_info(dc_ent)
            t.repeating = True
            logger.debug('VM NodesAvailability Task Created')
            return t
        except Exception as e:
            traceback.print_exc()
            raise e




