from stackone.core.ha.ha_register import HARegister
from stackone.model import *
from stackone.model.DBHelper import DBHelper
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
from stackone.model.GenericCache import GenericCache
from stackone.model.Entity import EntityContext
constants = stackone.core.utils.constants
import transaction
from sqlalchemy.sql.expression import or_
import traceback
import logging
LOGGER = logging.getLogger('stackone.model')
class AuthorizationService():
    def __init__(self, user=None, groups=None, user_name=None):
        self.user = user
        self.groups = groups
        self.user_name = user_name

    def has_privilege(self, opname, entity=None):
        op = DBHelper().find_by_name(Operation, to_unicode(opname))
        if op is None or entity is None:
            return False
        ops = self.get_ops(entity, op)
        if len(ops) > 0:
            return True
        return False


    def check_privilege(self, opname, entities):
        op = DBHelper().find_by_name(Operation, to_unicode(opname))
        if op is None:
            return False
        for ent in entities:
            ops = self.get_ops(ent, op)
            if len(ops) == 0:
                return False
        return True


    def get_user_roles(self):
        if self.user:
            return self.user.get_roles()
        if self.groups:
            rol_lst = []
            for g in self.groups:
                g = DBSession.query(Group).filter(Group.group_id == g.group_id).first()
                if g:
                    rol_lst.append(g.role)
            return rol_lst
        return []


    def is_admin_role(self):
        r = DBHelper().find_by_name(Role, to_unicode(constants.DEFAULT_ROLES[0]))
        if self.user:
            if self.user.is_cloud():
                return self.user.has_cloudadmin_role()
            return self.user.has_role(r)
        if self.groups:
            for g in self.groups:
                g = DBSession.query(Group).filter(Group.group_id == g.group_id).first()
                if g and r.id ==g.role.id:
                    return True
            return False

    def has_servicepoint_role(self, servicepoint):
        role = DBSession.query(Role).filter(Role.id == servicepoint.role_id).first()
        if self.user:
            return role in self.user.get_roles()
        return False


    def get_group_filter(self):
        if self.groups:
            return Group.group_id.in_([g.group_id for g in self.groups])

        if self.user:
            return Group.users.contains(self.user)


    def get_privilege(self, entity):
        privs = DBHelper().filterby(Privilege, [Privilege.priv_rep, Entity, Role, Role.groups], [self.get_group_filter(), Entity.entity_id == entity.entity_id], [Privilege.id])
        return privs

    def get_role(self, privilege):
        roles = DBHelper().filterby(Role, [Role.role_rep, Privilege, Role.groups], [self.get_group_filter(), Privilege.id == privilege.id])
        role = None
        if len(roles) > 0:
            role = roles[0]
        return role


    def get_ops(self, entity, op=None):
        privs = self.get_privilege(entity)
        if len(privs) == 0:
            return []

        filters = [self.get_group_filter(), Entity.entity_id == entity.entity_id]

        priv_ids = [priv.id for priv in privs]
        filters.append(Privilege.id.in_(priv_ids))
        if op is not None:
            filters.append(Operation.id == op.id)
        ops = DBHelper().filterby(Operation,[Operation.entityType,Operation.opsGroup,OperationGroup.privilege,Entity,Entity.ent_rep],
            filters,[Operation.display_seq])
        return ops


    def get_entities(self, entityType, parent=None, parentid=None, privilege=None):
        ents = []
        type = DBHelper().find_by_name(EntityType, entityType)
        filters = [self.get_group_filter(), Entity.type_id == type.id]
        if privilege is not None:
            priv=DBHelper().find_by_name(Privilege, privilege)
            if priv is not None:
                filters.append(Privilege.id == priv.id)
            else:
                return ents
        else:
            filters.append(Privilege.id != None)

        if parent is not None:
            ids = [x.entity_id for x in parent.children]
            filters.append(Entity.entity_id.in_(ids))

        orderby = [Entity.name.asc()]
        ents = DBHelper().filterby(Entity, [Entity.ent_rep, Privilege, Role, Role.groups], filters, orderby)
        return ents


    def get_entity_names(self, entityType, parent=None, privilege=None):
        ents = []
        if entityType is  None or parent is None:
            return []

        type = DBHelper().find_by_name(EntityType, entityType)
        filters = [self.get_group_filter(), Entity.type_id == type.id]

        ids = [x.entity_id for x in parent.children]

        filters.append(Entity.entity_id.in_(ids))
        if privilege is not None:
            priv=DBHelper().find_by_name(Privilege, privilege)
            if priv is not None:
                filters.append(Privilege.id == priv.id)
            else:
                return ents
        else:
            filters.append(Privilege.id != None)
        ents = DBHelper().filterby(Entity, [Entity.ent_rep, Privilege, Role, Role.groups], filters)
        ent_names=[]
        for ent in ents:
            ent_names.append(ent.name)

        return ent_names


    def get_entity_ids(self, entityType, parent=None):
        etype = DBHelper().find_by_name(EntityType, entityType)
        filters = [Privilege.id != None, self.get_group_filter(), Entity.type_id == etype.id]

        if parent is not None:
            ids=[x.entity_id for x in parent.children]
            filters.append(Entity.entity_id.in_(ids))

        ents = DBHelper().filterby(Entity, [Entity.ent_rep, Privilege, Role, Role.groups], filters)
        ent_ids = []

        for ent in ents:
            ent_ids.append(ent.entity_id)

        return ent_ids


    def get_entity(self, entityId, entityType=None, parent=None):
        filters = [Privilege.id != None, self.get_group_filter(), Entity.entity_id == entityId]
        if entityType is not None:
            type=DBHelper().find_by_name(EntityType, entityType)
            filters.append(Entity.type_id == type.id)
        #import pdb; pdb.set_trace()
        if parent is not None: 
            ids=[x.entity_id for x in parent.children]

            filters.append(Entity.entity_id.in_(ids))

        ents = DBHelper().filterby(Entity, [Entity.ent_rep, Privilege, Role, Role.groups], filters)
        ent = None
        if len(ents) > 0:
            ent = ents[0]

        return ent


    def get_entity_by_name(self, name, entityType=None, parent=None):
        filters = [Privilege.id != None, self.get_group_filter(), Entity.name == name]
        if entityType is not None:
            type=DBHelper().find_by_name(EntityType, entityType)
            filters.append(Entity.type_id == type.id)

        if parent is not None: 
            ids=[x.entity_id for x in parent.children]
            filters.append(Entity.entity_id.in_(ids))

        ents = DBHelper().filterby(Entity, [Entity.ent_rep, Privilege, Role, Role.groups], filters)
        ent = None
        if len(ents) > 0:
            ent = ents[0]
        return ent


    def get_child_entities(self, entity):
        filters = [Privilege.id != None, self.get_group_filter()]

        ids = [x.entity_id for x in entity.children]
        filters.append(Entity.entity_id.in_(ids))
        ents = DBHelper().filterby(Entity, [Entity.ent_rep, Privilege, Role, Role.groups], filters)
        return ents


    def get_child_entities_by_type(self, entity, child_type):
        filters = [Privilege.id != None, self.get_group_filter()]
        ids=[x.entity_id for x in entity.children]
        filters.append(Entity.entity_id.in_(ids))
        filters.append(EntityType.name == child_type)
        ents = DBHelper().filterby(Entity, [Entity.ent_rep, EntityType,Privilege, Role, Role.groups], filters)
        return ents


    def get_all_entities(self):
        ents = DBHelper().filterby(Entity, [Entity.ent_rep, Privilege, Role, Role.groups], [Privilege.id != None, self.get_group_filter()])
        return ents

    #pass
    def get_all_rep(self, entity, role_ids=None, is_granular=None):
        filters = []
        filters.append(RoleEntityPrivilege.entity_id == entity.entity_id)
        if is_granular == True:
            if role_ids is not None:
                filters.append(or_(RoleEntityPrivilege.role_id.in_(role_ids)))
                RoleEntityPrivilege.propagate == True
            else:
                filters.append(RoleEntityPrivilege.propagate == True)
        elif is_granular == False:
            filters.append(RoleEntityPrivilege.propagate == True)
        reps = DBHelper().filterby(RoleEntityPrivilege, [], filters)
        return reps


    def remove_roles(self, role_ids):
        if not isinstance(role_ids, list):
            role_ids = [role_ids]

        reps = DBSession.query(RoleEntityPrivilege).filter(RoleEntityPrivilege.role_id.in_(role_ids)).delete()
        DBSession.query(Role).filter(Role.id.in_(role_ids)).delete()
        return reps


    #get_all_groups = classmethod()
    #get_all_users = classmethod()
    @classmethod
    def get_all_groups(cls, role_ids):
        if not isinstance(role_ids,list):
            role_ids = [role_ids]
        groups = DBSession.query(Group).filter(Group.role_id.in_(role_ids)).all()
        return groups
        
    @classmethod
    def get_all_users(cls, entity):
        filters = []
        filters.append(RoleEntityPrivilege.entity == entity)
        usrs = DBHelper().filterby(User, [User.groups, Role, RoleEntityPrivilege], filters)
        return usrs
    def add_entity(self, name, entity_id, entityType, parent, context=None, csep_context=None):
        try:
            etype = DBHelper().find_by_name(EntityType, entityType)
            (context_id, csep_context_id) = (None, None)
            if context:
                context_id = self.add_context(context)
            if csep_context:
                csep_context_id = self.add_csep_context(csep_context)

            e = Entity()
            e.name = name
            e.type = etype
            e.entity_id = entity_id
            e.context_id = context_id
            e.csep_context_id = csep_context_id
            if entityType in [constants.SERVER_POOL, constants.MANAGED_NODE, constants.DOMAIN]:
                e.set_ha(parent.ha_registered())
            DBHelper().add(e)
            DBHelper().add(EntityRelation(parent.entity_id, entity_id, u'Children'))
            self.add_rep(e, parent)
            DBSession.flush()
            gc = GenericCache()
            gc.on_add_entity(e.type.name)

        except Exception as ex:
            raise ex
        return e

###################
    def add_context(self, context):
        try:
            if not isinstance(context, dict):
                LOGGER.debug('Entity context should be a dictionary')
                raise Exception('Entity context should be a dictionary')

            cntxt = self.get_context(context)
            if cntxt:
                LOGGER.debug('Entity Context: %s already exist' % context)
                return cntxt.id
            cntxt = EntityContext(context)
            DBHelper().add(cntxt)
            LOGGER.debug('Entity context: %s Added' % context)
            return cntxt.id

        except Exception as e:
            traceback.print_exc()
            raise e


    def add_csep_context(self, context):
        try:
            LOGGER.debug('In add_csep_context')
            #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEPContext
            if not isinstance(context, dict):
                LOGGER.debug('CSEP Context should be a dictionary')
                raise Exception('CSEP Context should be a dictionary')

            cntxt = self.get_csep_context(context)
            if cntxt:
                LOGGER.debug('CSEP Context: %s already exist' % context)
                return cntxt.id
            cntxt = CSEPContext()
            cntxt.save_context(context)
            DBSession.add(cntxt)
            LOGGER.debug('CSEP Context: %s Added' % context)
            return cntxt.id

        except Exception as e:
            traceback.print_exc()
            raise e


    def get_csep_context(self, context):
        try:
            LOGGER.debug('In get_csep_context')
            #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEPContext
            result = CSEPContext.get_context(context)
            if result:
                return result
        except Exception as e:
            traceback.print_exc()
            raise e


    def get_context(self, context):
        try:
            result = EntityContext.get_entity_context(context)
            if result:
                return result
        except Exception as e:
            traceback.print_exc()
            raise e


    def remove_context(self, context_id):
        try:
            EntityContext.remove_context(context_id)

        except Exception as e:
            traceback.print_exc()
            raise e


    def remove_entity_by_id(self, entityId, entityType=None, parent=None):
        try:
            entity = self.get_entity(entityId, entityType, parent)
            self.remove_rep(entity)
            self.delete_relations(entity)
            gc = GenericCache()
            gc.on_delete_entity(entityId, entity.type.name)
            DBHelper().delete(entity)

        except Exception as e:
            traceback.print_exc()
            raise e


    def remove_entity(self, entity):
        try:
            self.remove_rep(entity)
            self.delete_relations(entity)
            gc = GenericCache()
            gc.on_delete_entity(entity.entity_id, entity.type.name)
            DBHelper().delete(entity)
            
        except Exception as e:
            traceback.print_exc()
            raise e


    def update_entity_by_id(self, entityId, name=None, parent=None, new_entityId=None):
        try:
            entity = self.get_entity(entityId)
            self.update_entity(entity, name=name, parent=parent, new_entityId=new_entityId)
            gc = GenericCache()
            gc.on_add_entity(entity.type.name)
        except Exception as e:
            raise e


    def update_entity(self, entity, name=None, parent=None, new_entityId=None):
        try:
            update_rep = False
            if name is not None:
                entity.name = name
            if parent is not None:
                old_prnt = entity.parents[0]
                if parent not in entity.parents:
                    update_rep = True
                self.delete_entity_relation(old_prnt.entity_id, entity.entity_id, u'Children')
                DBHelper().add(EntityRelation(parent.entity_id, entity.entity_id, u'Children'))
                entity.set_ha(parent.ha_registered())
            if new_entityId is not None:
                entity.entity_id = new_entityId
            DBHelper().add(entity)
            if update_rep:
                self.update_rep(entity, parent)
            gc = GenericCache()
            gc.on_add_entity(entity.type.name)
        except Exception as e:
            traceback.print_exc()
            raise e

    def add_rep(self, entity, parent):
        propagate = True
        import tg
        is_granular = tg.config.get(constants.GRANULAR_USER_MODEL)

        if is_granular!='True':
            propagate = False
        else:
            is_granular = True
        role_ids = []
        if propagate  and (self.user is not None or self.groups is not None):
            roles = self.get_user_roles()
            r = DBHelper().find_by_name(Role, to_unicode(constants.DEFAULT_ROLES[0]))
            if r not in roles:
                roles.append(r)

            role_ids=[role.id for role in roles]
        reps = self.get_all_rep(parent, role_ids,is_granular)
        for rep in reps:
            new_rep = RoleEntityPrivilege()
            new_rep.privilege = rep.privilege
            prop = True
            if is_granular and rep.role.id not in role_ids:
                prop = rep.propagate
            new_rep.propagate = prop
            new_rep.role = rep.role
            new_rep.entity = entity
            DBHelper().add(new_rep)

    def get_admin_role(self):
        r = DBHelper().find_by_name(Role,to_unicode(constants.DEFAULT_ROLES[0]))
        return r
    def remove_rep(self, entity):
        reps = self.get_all_rep(entity)
        for rep in reps:
            DBHelper().delete(rep)

    def update_rep(self, entity, parent):
        self.remove_rep(entity)
        self.add_rep(entity, parent)

        for child in entity.children:
            self.update_rep(child, entity)


    def get_entity_relation(self, src, dest, reln):
        er = DBHelper().filterby(EntityRelation, [], [EntityRelation.src_id == src, EntityRelation.dest_id == dest, EntityRelation.relation == reln])
        return er

    def delete_entity_relation(self, src, dest, reln):
        DBHelper().delete_all(EntityRelation, [], [EntityRelation.src_id == src, EntityRelation.dest_id == dest, EntityRelation.relation == reln])

    def delete_relations(self, entity):
        ers1 = DBSession.query(EntityRelation).filter(EntityRelation.src_id == entity.entity_id).filter(EntityRelation.relation == u'Children').all()
        for er in ers1:
            DBSession.delete(er)
        ers2 = DBSession.query(EntityRelation).filter(EntityRelation.dest_id == entity.entity_id).filter(EntityRelation.relation == u'Children').all()
        for er in ers2:
            DBSession.delete(er)


    def is_csep_user(self):
        #from stackone.cloud.DbModel.platforms.cms.CSEP import CSEP
        cseps = DBSession.query(CSEP.group_id).all()
        csep_group_ids=[csep.group_id for csep in cseps]
        current_user_grp_ids=[grp.group_id for grp in self.user.groups]
        if len(set(current_user_grp_ids) & set(csep_group_ids)):
            return True
        return False
    def get_entity_by_entity_attributes(self, attributes_dict=None, entityType=None, parent=None):
        filters = [Privilege.id != None, self.get_group_filter()]
        if entityType is not None:
            type = DBHelper().find_by_name(EntityType,entityType)
            filters.append(Entity.type_id == type.id)
        if parent is not None:
            ids = [x.entity_id for x in parent.children]
            filters.append(Entity.entity_id.in_(ids))
        if attributes_dict:
            for k,v in attributes_dict.items():
                ids = DBHelper().filterby(EntityAttribute.entity_id,[],[EntityAttribute.name == k,EntityAttribute.value == v])
                ids = [id[0] for id in ids]
                print 'EntityAttribute, entity_ids: ',ids
                filters.append(EntityAttribute.entity_id.in_(ids))
                
        ents = DBHelper().filterby(Entity,[Entity.ent_rep,Privilege,Role,Role.groups,EntityAttribute],filters)
        print 'Entities: ',ents
        ent = None

        if len(ents) > 0L:
            ent = ents[0L]
        return ent

    def make_rep_entry(self, role_db, ent, priv=u'FULL'):
        try:
            reps = DBSession.query(RoleEntityPrivilege).filter(RoleEntityPrivilege.role_id == role_db.id).filter(RoleEntityPrivilege.entity_id == ent.entity_id).all()
            if not len(reps):
                rep = RoleEntityPrivilege()
                rep.role = role_db
                rep.entity = ent
                privilege = DBSession().query(Privilege).filter(Privilege.name == priv).first()
                rep.privilege = privilege
                DBSession.add(rep)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex





