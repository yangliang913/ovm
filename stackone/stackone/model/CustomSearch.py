from sqlalchemy import Column, DateTime
import logging
from stackone.model import DeclarativeBase, DBSession
from sqlalchemy import func
from sqlalchemy.types import Integer, Unicode, Boolean, String, Text
from sqlalchemy.schema import Sequence
from stackone.model import DBSession, Entity, EntityRelation
from stackone.model.ManagedNode import ManagedNode
from stackone.model.availability import AvailState
from stackone.model.VM import VM
from stackone.model.ImageStore import Image
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from stackone.core.utils.utils import get_dbtype
LOGGER = logging.getLogger('stackone.model')
class CustomSearch(DeclarativeBase):
    __tablename__ = 'custom_search'
    id = Column(Integer, Sequence('csid_seq'), primary_key=True)
    name = Column(Unicode(255L))
    user_name = Column(Unicode(255L))
    created_date = Column(DateTime)
    modified_date = Column(DateTime)
    description = Column(Text)
    condition = Column(Text)
    node_level = Column(Unicode(50L))
    lists_level = Column(Unicode(50L))
    max_count = Column(Unicode(50L))
    def __init__(self):
        pass

    def make_query(self, class_name, DEC, property, lists_level):
        if lists_level==constants.VMS:
            conditions=self.make_vmsearch_query(class_name,DEC,property)
        elif lists_level==constants.SERVERS:
            conditions=self.make_serversearch_query(class_name,DEC,property)
        return conditions


    def make_serversearch_query(self, class_name, DEC, property):
        condition=""

        joins=[]
        filters=[]     

        dec_val=""
        lists=DEC[2:]
        i=0
        for x in lists:
            if i > 0 :
                dec_val+=" "
            dec_val+=x
            i+=1

        if property == constants.MEMUTIL_VALUE:
            
            condition = self.get_custom_condition('class_name.host_mem', DEC[1] , dec_val)
            filters.append(eval(condition))

        elif property == constants.CPUUTIL_VALUE:

            condition = self.get_custom_condition('class_name.host_cpu', DEC[1] , dec_val)
            filters.append(eval(condition))

        elif property == constants.STRGUTIL_VALUE:
            condition = self.get_custom_condition('class_name.gb_poolused', DEC[1] , dec_val)
            filters.append(eval(condition))
        
        elif property ==constants.SP_VALUE:            
            condition = self.get_custom_condition('Entity.name', DEC[1] , dec_val)
            
            filters.append(class_name.entity_id.in_(
                DBSession.query(EntityRelation.dest_id).filter(EntityRelation.src_id.in_(
                    DBSession.query(Entity.entity_id).filter(eval(condition))
                ))
            ))          
            
        elif property ==constants.PLTFM_VALUE:

            joins.append((ManagedNode,ManagedNode.id==class_name.entity_id))
            condition = self.get_custom_condition('ManagedNode.type', DEC[1] , dec_val)
            filters.append(eval(condition))

        elif property == constants.SRVR_STATUS_VALUE:

            joins.append((AvailState,AvailState.entity_id==class_name.entity_id))
            if DEC[2] == "down":
                filters.append(AvailState.avail_state == ManagedNode.DOWN)
            else:
                filters.append(AvailState.avail_state == ManagedNode.UP)

        elif property ==constants.SRVR_NAME_VALUE:

            joins.append((ManagedNode,ManagedNode.id==class_name.entity_id))
            condition = self.get_custom_condition('ManagedNode.hostname', DEC[1] , dec_val)
            filters.append(eval(condition))

        elif property ==constants.SB_VALUE:

            joins.append((ManagedNode,ManagedNode.id==class_name.entity_id))
            if DEC[2] == "yes":
                filters.append(ManagedNode.standby_status == ManagedNode.STANDBY)              
            else:
                filters.append(ManagedNode.standby_status == None)
                
        return dict(filters=filters,joins=joins)


    def make_vmsearch_query(self, class_name, DEC, property):
        condition=""
        dec_val=""
        lists=DEC[2:]
        i=0
        for x in lists:
            if i > 0 :
                dec_val+=" "
            dec_val+=x
            i+=1
        joins=[]
        filters=[]
        if property == constants.MEMUTIL_VALUE:
            condition = self.get_custom_condition('class_name.mem_util', DEC[1] , dec_val)
            filters.append(eval(condition))
        elif property == constants.CPUUTIL_VALUE:
            condition = self.get_custom_condition('class_name.cpu_util', DEC[1] , dec_val)
            filters.append(eval(condition))
        elif property == constants.STRGUTIL_VALUE:
            condition = self.get_custom_condition('class_name.gb_poolused', DEC[1] , dec_val)
            filters.append(eval(condition))
        elif property ==constants.SP_VALUE:
            condition = self.get_custom_condition('Entity.name', DEC[1] , dec_val)
            filters.append(class_name.entity_id.in_(
                    DBSession.query(EntityRelation.dest_id).filter(EntityRelation.src_id.in_(
                        DBSession.query(EntityRelation.dest_id).filter(EntityRelation.src_id.in_(
                            DBSession.query(Entity.entity_id).filter(eval(condition))
                            ))
                        ))
                    ))            
        elif property ==constants.TEMPLATE_VALUE:
            condition = self.get_custom_condition('Image.name', DEC[1] , dec_val)
            filters.append(class_name.entity_id.in_(
                                DBSession.query(VM.id).filter(VM.image_id.in_(\
                                        DBSession.query(Image.id).filter(eval(condition))
                                ))
                            ))           
        elif property ==constants.OS_VALUE:
            joins.append((VM,VM.id==class_name.entity_id))
            db_type=get_dbtype()
            if db_type==constants.ORACLE:
                condition = self.get_custom_condition('func.concat(func.concat(VM.os_name," "),VM.os_version)', DEC[1] , dec_val)
            else:
                condition = self.get_custom_condition('func.concat(VM.os_name," ",VM.os_version)', DEC[1] , dec_val)
            filters.append(eval(condition))
        elif property ==constants.SRVR_NAME_VALUE:
            condition = self.get_custom_condition('Entity.name', DEC[1] , dec_val)
            filters.append(class_name.entity_id.in_(
                                DBSession.query(EntityRelation.dest_id).filter(EntityRelation.src_id.in_(
                                    DBSession.query(Entity.entity_id).filter(eval(condition))
                                    ))
                                ))          

        elif property ==constants.VM_STATUS_VALUE:
            joins.append((VM,VM.id==class_name.entity_id))
            joins.append((AvailState,AvailState.entity_id==class_name.entity_id))

            if DEC[2] == "down":
               filters.append(AvailState.avail_state == VM.SHUTDOWN)
            else:
               filters.append(AvailState.avail_state != VM.SHUTDOWN)
        elif property ==constants.VM_NAME_VALUE:
            joins.append((VM,VM.id==class_name.entity_id))
            condition = self.get_custom_condition('VM.name', DEC[1] , dec_val)
            filters.append(eval(condition))
        return dict(filters=filters,joins=joins)



    def get_custom_condition(self, class_col, op, value):

        condn = ""
        if op == 'like':
            condn = class_col+".like('%"+value+"%')"
        else:
            condn = class_col + " " + op + " '"+ value +"'"
        return condn





