from stackone.model import DBSession
from stackone.model.ManagedNode import ManagedNode
from stackone.model.Entity import Entity, EntityTasks, EntityRelation, EntityType
from stackone.model.WorkManager import WorkManager
from stackone.model.availability import AvailState
from sqlalchemy.sql.expression import not_, or_
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from datetime import datetime
import traceback
import transaction
import tg
import logging
logger = logging.getLogger('stackone.model')
WRK_LOGGER = logging.getLogger('WORKER')

class AvailabilityWorker(WorkManager):
    ###
    def __init__(self, auth):
        WorkManager.__init__(self, auth)
        self.worker = constants.AVAILABILITY
        self.sp_list = []
        try:
            self.max_workers = int(tg.config.get('max_ping_workers'))
        except Exception as e:
            print 'Exception: ',e
            self.max_workers = 5
        try:
            self.node_limit = int(tg.config.get('max_ping_servers'))
        except Exception as e:
            print 'Exception: ',e
            self.node_limit = 10

    ###
    def get_work(self):
        try:
            WRK_LOGGER.debug('in get_work : ' + self.worker)
            sp_id,node_id_list = self.get_sp_node_ids()
            logger.debug('Node NodesAvailability GET WORK')
            if len(node_id_list) > 0:
                node_ids=[m_node_id[0] for m_node_id in node_id_list]
                new_work = self.get_task(self.auth,node_ids)
                WRK_LOGGER.debug('in get_work : ' + self.worker + ' : Got Work : ' + str(node_ids))
                return (new_work,node_ids)
            else:
                WRK_LOGGER.debug('in get_work : ' + self.worker + ' : No Work')
                return (None,None)
        except Exception as e:
            traceback.print_exc()
            raise e

    ###
    def get_task(self, auth, node_ids):
        try:
            from stackone.core.services.tasks import NodesAvailability
            user_name = auth.user.user_name
            t = NodesAvailability(u'Update node availability', {}, [], dict(node_ids=node_ids), None, user_name)
            dc_ent = DBSession.query(Entity).filter(Entity.type_id == EntityType.DATA_CENTER).first()
            t.set_entity_info(dc_ent)
            t.repeating = True
            logger.debug('Node NodesAvailability Task Created nodeids===' + str(node_ids))
            return t
        except Exception as e:
            traceback.print_exc()
            raise e


    ###
    def get_sp_node_ids(self):
        """
        getting sp and its node ids that were pinged before ping_task_start_time limited to max_ping_servers
        """
        sp_id=None
        node_list=[]
        try:
            self.execution_context["sp_list"]=self.sp_list
            while len(node_list)==0:
                ent=DBSession.query(Entity).filter(Entity.type_id==EntityType.SERVER_POOL).\
                    filter(not_(Entity.entity_id.in_(self.sp_list))).\
                    order_by(Entity.name.asc()).first()
                if ent is None:
                    pending_node_id_list = DBSession.query(ManagedNode.id).filter(not_(ManagedNode.id.in_(\
                        DBSession.query(EntityTasks.entity_id).filter(or_(EntityTasks.start_time>=self.start_time,EntityTasks.worker_id!=None)).\
                            filter(EntityTasks.worker==self.worker)
                    ))).limit(self.node_limit).all()

                    if len(pending_node_id_list)>0:
                        self.sp_list=[]
                    else:
                        break
                else:
                    self.sp_list.append(ent.entity_id)
                    if len(ent.children)>0:
                        sp_id=ent.entity_id
#                        children=[x.entity_id for x in ent.children]
                        node_list=DBSession.query(EntityRelation.dest_id).\
                            join((AvailState,AvailState.entity_id==EntityRelation.dest_id)).\
                            filter(EntityRelation.src_id==sp_id).\
                            filter(not_(EntityRelation.dest_id.in_(DBSession.query(EntityTasks.entity_id).\
                                filter(or_(EntityTasks.start_time>=self.start_time,EntityTasks.worker_id!=None)).\
                                    filter(EntityTasks.worker==self.worker)
                        ))).order_by(AvailState.avail_state.asc()).limit(self.node_limit).all()
        except Exception, e:
            traceback.print_exc()
        logger.debug("Node NodesAvailability pend_nodeids==="+str(node_list))
        return (sp_id,node_list)
    
    ###
    # def get_sp_node_ids(self):
        # """
        # getting sp and its node ids that were pinged before ping_task_start_time limited to max_ping_servers
        # """

        # sp_id=None
        # node_list=[]
        # try:
            # self.execution_context["sp_list"]=self.sp_list
            # while len(node_list)==0:
                # ent=DBSession.query(Entity).filter(Entity.type_id==EntityType.SERVER_POOL).\
                    # filter(not_(Entity.entity_id.in_(self.sp_list))).\
                    # order_by(Entity.name.asc()).first()
                # if ent is None:
                    # pending_node_id_list = DBSession.query(ManagedNode.id).filter(not_(ManagedNode.id.in_(\
                        # DBSession.query(EntityTasks.entity_id).filter(or_(EntityTasks.start_time>=self.start_time,EntityTasks.worker_id!=None)).\
                            # filter(EntityTasks.worker==self.worker)
                    # ))).limit(self.node_limit).all()

                    # if len(pending_node_id_list)>0:
                        # self.sp_list=[]
                    # else:
                        # break
                # else:
                    # self.sp_list.append(ent.entity_id)
                    # if len(ent.children)>0:
                        # sp_id=ent.entity_id
                       # children=[x.entity_id for x in ent.children]
                        # node_list=DBSession.query(EntityRelation.dest_id).\
                            # join((AvailState,AvailState.entity_id==EntityRelation.dest_id)).\
                            # filter(EntityRelation.src_id==sp_id).\
                            # filter(not_(EntityRelation.dest_id.in_(DBSession.query(EntityTasks.entity_id).\
                                # filter(or_(EntityTasks.start_time>=self.start_time,EntityTasks.worker_id!=None)).\
                                    # filter(EntityTasks.worker==self.worker)
                        # ))).order_by(AvailState.avail_state.asc()).limit(self.node_limit).all()
        # except Exception, e:
            # traceback.print_exc()
        # logger.debug("Node NodesAvailability pend_nodeids==="+str(node_list))
        # return (sp_id,node_list)
    

   