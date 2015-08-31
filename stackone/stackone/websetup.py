# -*- coding: utf-8 -*-
import logging
import transaction
from tg import config
from datetime import datetime
from stackone.config.environment import load_environment
__all__ = ['setup_app']
log = logging.getLogger(__name__)
from stackone.core.utils.utils import PyConfig, getHexID, populate_custom_fence_resources
from stackone.core.utils.utils import to_unicode, to_str
from stackone.model.ManagedNode import ManagedNode
from stackone.model.PlatformRegistry import PlatformRegistry
from stackone.model.ImageStore import ImageStore, ImageGroup, Image
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from stackone import model
from sqlalchemy.exc import IntegrityError
import os
import MySQLdb
from stackone.model.AuthInit import initialise_auth, initialise_lookup_data, op_platform_type
from stackone.config.ConfigSettings import ClientConfiguration
from stackone.core.utils import constants
from stackone.model.Metrics import MetricsService
import tg
from stackone.model.EmailSetup import EmailSetup
from stackone.model.Backup import SPBackupSetting, SPBackupSchedule, SPBackupConfig, VMBackupResult, VMBackupDetailResult
from stackone.model.Restore import VMRestoreResult, VMRestoreDetailResult
##from stackone.cloud.DbModel.CloudProvider import CloudProviderNode
##from stackone.cloud.DbModel.TemplateProvider import TemplateProvider, TemplateGroupType
from stackone.model.VLANManager import VLANIDPool, VLANIDPoolSPRelation, VLANID
from stackone.model.PrivateIP import PrivateIPPoolSPRelation, DHCPServer
##from stackone.cloud.DbModel.platforms.cms.CMSPrivateIPManager import CMSPrivateIPPool, CMSPrivateIPPoolRegionRelation, CMSPrivateIP, CMSDHCPServer
##from stackone.cloud.DbModel.platforms.cms.CMSNetwork import CMSNetwork, CMSNetworkRegionRelation, CMSNetworkVMRelation
from stackone.model.network import NetworkVMRelation
def setup_app(command, conf, vars):
    load_environment(conf.global_conf, conf.local_conf)
    engin = config['pylons.app_globals'].sa_engine
    print 'Creating tables'
    dburl = tg.config.get('sqlalchemy.url')
    pcs = dburl.split('/')
    flag = False
    update_from_version = tg.config.get('update_from_version')

    if update_from_version == None:
        if pcs[0] == 'mysql:':
            cred,con = pcs[2].split('@')
            creds = cred.split(':')
            user = creds[0]
            passwd = None
            if len(creds) > 1:
                passwd = creds[1]
            cons = con.split(':')
            host = cons[0]
            port = None
            if len(cons)>1 and cons[1] != '':
                port = int(cons[1])
            rest = pcs[3].split('?')
            db = rest[0]
            params = dict(host=host, user=user)
            if passwd is not None:
                params['passwd'] = passwd
            if port is not None:
                params['port'] = port
            conn = MySQLdb.connect(**params)
        
            try:
                cursor = conn.cursor()
                print 'check if database exists'
                cursor.execute("select count(*) from information_schema.schemata where schema_name='" + db + "'")
                reslt = cursor.fetchone()
                if reslt[0] == 0:
                    print 'create database'
                    cursor.execute('create database ' + db + ' CHARACTER SET utf8;')
                else:
                    print 'database exists, check if tables exist'
                    cursor.execute("select count(*) from information_schema.tables where table_schema='" + db + "'")
                    reslt = cursor.fetchone()
                    if reslt[0] != 0:
                        raise Exception("Schema '" + db + "' already esists.")
                    else:
                        print 'continue with setup'
                cursor.close()
                flag = True
            except Exception as e:
                print 'Exception: ',
                print e
                print 'Drop stackone database and run setup again.'
                import sys
                sys.exit(1)
                return None
            engin.execute("set storage_engine='InnoDB'")
            model.metadata.create_all(bind=engin)
    if flag:
        conn = MySQLdb.connect(user=user, passwd=passwd, db=db)
        cursor = conn.cursor()
        cursor.execute('show table status from ' + db + " where Engine = 'MyISAM'")
        rows = cursor.fetchall()
        for row in rows:
            tname = row[0]
            cursor.execute('alter table ' + tname + " ENGINE ='InnoDB'")
        cursor.close()
        conn.close()
#    if update_from_version is not None:
#        update_changes(update_from_version)
#        return None
#    if update_from_version is not None:
#        update_changes('2.0.2')
#        update_changes('3.1')
#        update_changes('3.1.x')
    groups,entity_types,privileges,privileges_dict,cp_types_dict = initialise_auth()
    initialise_lookup_data()
    local_node = ManagedNode(hostname='localhost')
    registry = PlatformRegistry(local_node.config, {})
    tot_entities = []
    hl_entities = []
    cld_entities = []
    si = dict(id=1,name = 'Data Center',type = 'DATA_CENTER')
    site = model.Site(si['name'])
    s = model.Entity()
    s.name = si['name']
    s.id = si['id']
    s.entity_id = site.id
    s.type = entity_types[si['type']]
    ex_sites = model.DBSession.query(model.Site).filter(model.Site.name == si['name']).all()
    if len(ex_sites) == 0:
        model.DBSession.add(s)
        model.DBSession.add(site)
    else:
        site = ex_sites[0]
        s.entity_id = site.id
    hl_entities.append(s)
    # ci = dict(id = 3,name = u'Iaas',type = 'CLOUD_PROVIDER_FOLDER')    
    # cloud = CloudProviderNode(ci['name'])
    # c = model.Entity()
    # c.name = ci['name']
    # c.id = ci['id']
    # c.entity_id = cloud.id
    # c.type = entity_types[ci['type']]
    # ex_clouds = model.DBSession.query(CloudProviderNode).filter(CloudProviderNode.name == ci['name']).all()
    # if len(ex_clouds) == 0:
    #     model.DBSession.add(c)
    #     model.DBSession.add(cloud)
    # else:
    #     cloud = ex_sites[0]
    #     c.entity_id = cloud.id
    # cld_entities.append(c)
    ###############################
    locn = tg.config.get(constants.prop_image_store)
    image_store_location = to_unicode(os.path.abspath(locn))
    img_str = dict(id= 2,name = u'Template Library',type = 'IMAGE_STORE')
    image_store = ImageStore(registry)
    image_store.name = img_str['name']
    image_store.location = image_store_location
    image_store._store_location = image_store_location
    image_store.id = getHexID()
    iss = model.Entity()
    iss.name = img_str['name']
    iss.id = img_str['id']
    iss.entity_id = image_store.id
    iss.type = entity_types[img_str['type']]
    model.DBSession.add(model.EntityRelation(s.entity_id, iss.entity_id, u'Children'))
    ex_iss = model.DBSession.query(model.ImageStore).filter(model.ImageStore.name == img_str['name']).all()
    
    if len(ex_iss) == 0:
        model.DBSession.add(image_store)
        model.DBSession.add(iss)
    else:
        image_store = ex_iss[0]
        iss.entity_id = image_store.id
    hl_entities.append(iss)
    # vdcs_str = dict(id=4,name = 'Virtual Data Centers',type = 'VDC_FOLDER')
    # vdc_store = model.VDCStore(vdcs_str['name'])
    # vdc_store.name = vdcs_str['name']
    # vdc_store.id = getHexID()
    # vdcs = model.Entity()
    # vdcs.name = vdcs_str['name']
    # vdcs.id = vdcs_str['id']
    # vdcs.entity_id = vdc_store.id
    # vdcs.type = entity_types[vdcs_str['type']]
    # ex_iss = model.DBSession.query(model.VDCStore).filter(model.VDCStore.name == vdcs_str['name']).all()
    
    # if len(ex_iss) == 0:
    #     model.DBSession.add(vdc_store)
    #     model.DBSession.add(vdcs)
    # else:
    #     image_store = ex_iss[0]
    #     vdcs.entity_id = VDCStore.id
    # cld_entities.append(vdcs)
    tot_entities.extend(hl_entities)
    
    
    server_pools_dict = {}
    #server_pools = [{'id':5,'name':u'Desktops','type':'SERVER_POOL'},{'id':6,'name':u'Servers','type':'SERVER_POOL'},{'id':7,'name':u'stackone','type':'SERVER_POOL'}]
    server_pools = [{'id':7,'name':'stackone','type':'SERVER_POOL'}]
    sp_entities = []
    for sp in server_pools:
        grp = model.ServerGroup(sp['name'])
        e = model.Entity()
        e.name = sp['name']
        e.id = sp['id']
        e.entity_id = grp.id
        e.type = entity_types[sp['type']]
        
        populate_sp_adv_options(e)
        model.DBSession.add(model.EntityRelation(s.entity_id, grp.id, u'Children'))
        server_pools_dict[sp['name']] = e
        grps = model.DBSession.query(model.ServerGroup).filter(model.ServerGroup.name == sp['name']).all()
        if len(grps) == 0:
            model.DBSession.add(grp)
            model.DBSession.add(e)
        else:
            grp = grps[0]
            e.entity_id = grp.id
        sp_entities.append(e)

    tot_entities.extend(sp_entities)
    img_entities = image_store._init_from_dirs()
    tot_entities.extend(img_entities)
    grp_dict = {}
    test_groups = [{'id':5,'name':u'Stackone管理','display_name':u'Stackone管理','description':u'Stackone服务器池的操作','createdby':u'admin','modifiedby':u'','type':constants.StackOne}]
    
    test_users = [{'id':5,'user_name':u'Sam','display_name':u'Sam','email':u'sam@stackone.com.cn','password':u'Sam','firstname':u'Sam'\
                ,'lastname':u'Yang','status':u'True','createdby':u'admin','modifiedby':u'','group':u'Stackone管理','type':constants.StackOne}]
    
    test_roles = [{'id':5,'name':u'Stackone管理员','sp':'stackone','group':u'Stackone管理','desc':u'Stackone服务器池的全部权限','type':constants.StackOne}]
#        test_roles = [{'id':4,'name':u'Desktops Admins','sp':u'Desktops','group':u'Desktop Managers','desc':u'Full privilege on Desktops server pool','type':constants.StackOne},\
#                {'id':5,'name':u'Servers Admins','sp':u'Servers','group':u'Server Managers','desc':u'Full privilege on Servers server pool','type':constants.StackOne}]

    for grp in test_groups:
        g1 = model.Group()
        g1.group_name = grp['name']
        g1.display_name = grp['display_name']
        g1.description = grp['description']
        g1.createdby = grp['createdby']
        g1.modified_by = grp['modifiedby']
        g1.created_date = datetime.now()
        g1.modified_date = datetime.now()
        g1.type = grp['type']
        grp_dict[grp['name']] = g1
        model.DBSession.add(g1)

    for user in test_users:
        u = model.User()
        u.user_name = user['user_name']
        u.display_name = user['display_name']
        u.email_address = user['email']
        u.password = user['password']
        u.firstname = user['firstname']
        u.lastname = user['lastname']
        u.status = user['status']
        u.created_by = user['createdby']
        u.modified_by = user['modifiedby']
        u.created_date = datetime.now()
        u.modified_date = datetime.now()
        u.type = user['type']
        u.groups.append(grp_dict[user['group']])
        model.DBSession.add(u)
    from stackone.core.services.task_service import TaskManager
    from stackone.core.services.execution_service import ExecutionService
    from stackone.core.services.dispatcher import DispatcherService
    from stackone.core.services.executors import ThreadExecutor
    from stackone.core.services.tasks import RefreshNodeInfoTask, RefreshNodeMetricsTask, Purging, CollectMetricsForNodes, TimeBasisRollupForNodes, UpdateDeploymentStatusTask, CheckForUpdateTask, EmailTask, UpdateDiskSize, NodeAvailTask, VMAvailTask, EmailNotificationTask,SendDeploymentStatsRptTask
    from stackone.core.ha.ha_main import HA
    from stackone.core.ha.ha_service import HAManager
    tasksvc = model.ServiceItem(u'Task Manager Service', \
                            TaskManager, \
                            ThreadExecutor,\
                            True)
    tasksvc.id=1
    model.DBSession.add(tasksvc)
    execsvc = model.ServiceItem(u'Execution Service', \
                            ExecutionService, \
                            ThreadExecutor, \
                            True)
    execsvc.id=2
    execsvc.dependents = [tasksvc]
    model.DBSession.add(execsvc)
    dispsvc = model.ServiceItem(u'Dispatcher Service', \
                            DispatcherService, \
                            ThreadExecutor, \
                            True)    
    dispsvc.id = 3
    model.DBSession.add(dispsvc)
    hasvc = model.ServiceItem(u'High Availability Service', \
                            HAManager, \
                            ThreadExecutor, \
                            True)    
    dispsvc.id = 4
    
    model.DBSession.add(hasvc)
    tasksvc.dependents = [hasvc]
    model.DBSession.add(tasksvc)
    dc_ent = s
    refresh_task = RefreshNodeInfoTask(u'Refresh Node Information',\
                        {'quiet':False}, [], {}, None, u'admin')
    refresh_task.id = 1    
    refresh_task.set_interval(model.TaskInterval(720))
    set_entity_details(refresh_task, dc_ent)
    model.DBSession.add(refresh_task)

    purge_task = Purging(u'Purging',\
                 {'quiet':False}, [], {}, None, u'admin')
    purge_task.id = 2
    purge_task.set_interval(model.TaskInterval(1440))
    set_entity_details(purge_task, dc_ent)
    model.DBSession.add(purge_task)
    
    timebasis_rollup_task= TimeBasisRollupForNodes(u'TimeBasisRollupForNodes', {'quiet':False}, [],{}, None, u'admin')
    timebasis_rollup_task.id = 4
    timebasis_rollup_task.set_interval(model.TaskInterval(15))
    set_entity_details(timebasis_rollup_task, dc_ent)
    model.DBSession.add(timebasis_rollup_task)
    
    collect_metrics_task= CollectMetricsForNodes(u'CollectMetricsForNodes', {'quiet':False}, [],\
                    {}, None, u'admin')
    collect_metrics_task.id = 3
    collect_metrics_task.set_interval(model.TaskInterval(3))
    set_entity_details(collect_metrics_task, dc_ent)
    model.DBSession.add(collect_metrics_task)
    
    upd_dep_task = UpdateDeploymentStatusTask(u'Update Deployment Status',\
                        {'quiet':False}, [], {}, None, u'admin')
    upd_dep_task.id = 4    
    upd_dep_task.set_interval(model.TaskInterval(1440))
    set_entity_details(upd_dep_task, dc_ent)
    model.DBSession.add(upd_dep_task)

    chk_upd_task = CheckForUpdateTask(u'Check For Update',\
                        {'quiet':False}, [], {}, None, u'admin')
    chk_upd_task.id = 5    
    chk_upd_task.set_interval(model.TaskInterval(1440, datetime.now()))
    set_entity_details(chk_upd_task, dc_ent)
    model.DBSession.add(chk_upd_task)
    
    send_mail_task= EmailTask(u'EmailTask', {'quiet':False}, [],\
                    {}, None, u'admin')
    send_mail_task.id = 6    
    send_mail_task.set_interval(model.TaskInterval(2))
    set_entity_details(send_mail_task, dc_ent)
    model.DBSession.add(send_mail_task)
    
    update_disk_task = UpdateDiskSize(u'Updating the disk size',\
                 {'quiet':False}, [], {}, None, u'admin')
    update_disk_task.id = 7    
    update_disk_interval = tg.config.get(constants.UPDATE_DISK_SIZE_INTERVAL)
    update_disk_task.set_interval(model.TaskInterval(int(update_disk_interval)))
    set_entity_details(update_disk_task, dc_ent)
    model.DBSession.add(update_disk_task)
    
    node_avail_task = NodeAvailTask(u'Update node availability',\
                                    {'quiet':False}, [], {}, None, u'admin')
    node_avail_task.id = 8    
    node_avail_task.set_interval(model.TaskInterval(1))
    set_entity_details(node_avail_task, dc_ent)
    model.DBSession.add(node_avail_task)
    
    vm_avail_task = VMAvailTask(u'Update VM availability',\
                                {'quiet':False}, [], {}, None, u'admin')
    vm_avail_task.id = 9    
    vm_avail_task.set_interval(model.TaskInterval(1))
    set_entity_details(vm_avail_task, dc_ent)
    model.DBSession.add(vm_avail_task)
########    
    ######################
    ha_subscriber = model.Subscriber(u'HA Subscriber',model.availability_event_type,HA)
    ha_subscriber.id = 1
    model.DBSession.add(ha_subscriber)
    
    send_mail_notification = EmailNotificationTask(u'EmailNotificationTask',\
                                {'quiet':False}, [], {}, None, u'admin')
    send_mail_notification.id = 10
    send_mail_notification.set_interval(model.TaskInterval(1))
    set_entity_details(send_mail_notification, dc_ent)
    
    model.DBSession.add(send_mail_notification)
    #add 0830
    snd_dep_task = SendDeploymentStatsRptTask(u'Send Deployment Stats',\
              {'quiet':True}, [], {}, None, u'admin')
    snd_dep_task.id = 10
    snd_dep_task.interval = [model.TaskInterval(10080)]
    set_entity_details(snd_dep_task,dc_ent)
    model.DBSession.merge(snd_dep_task)
    model.DBSession.flush()
    transaction.commit()

    roles = [{'id':1,'name':u'admin','desc':u'实体的全部权限.','type':constants.StackOne},\
            {'id':2,'name':u'operator','desc':u'实体的操作权限.','type':constants.StackOne},\
            {'id':3,'name':u'user','desc':u'实体的查看权限.','type':constants.StackOne}]
    i = 0
    ex_reps = []
    exs = model.DBSession.query(model.RoleEntityPrivilege).all()
    for ex in exs:
        ex_reps.append(ex)
    for op in roles:
        r = model.Role()
        r.name = op['name']
        r.description = op['desc']
        r.type = op['type']
        r.groups.append(groups[i])
        model.DBSession.add(r)
        for ent in tot_entities:
            rep = model.RoleEntityPrivilege()
            rep.role = r
            rep.privilege = privileges[i]
            rep.entity = ent
            #add 0830
            if ent.name == 'Data Center' and op['name'] != 'admin':
                rep.propagate = False    
            model.DBSession.add(rep)
        if op['name'] == 'admin':
            for ent in cld_entities:
                rep = model.RoleEntityPrivilege()
                rep.role = r
                rep.privilege = privileges[i]
                rep.entity = ent
                model.DBSession.add(rep)
        i += 1

    for role in test_roles:
        r = model.Role()
        r.name = role['name']
        r.description = role['desc']
        r.type = role['type']
        r.groups.append(grp_dict[role['group']])
        model.DBSession.add(r)
        for ent in img_entities:
            rep = model.RoleEntityPrivilege()
            rep.role = r
            rep.privilege = privileges_dict['OPERATOR']
            rep.entity = ent
            model.DBSession.add(rep)
    
        for ent in hl_entities:
            rep = model.RoleEntityPrivilege()
            rep.role = r
            rep.privilege = privileges_dict['VIEW']
            rep.entity = ent
            #add 0830
            if ent.name == 'Data Center' and role['name'] != 'admin':
                rep.propagate = False
            model.DBSession.add(rep)
    
        rep = model.RoleEntityPrivilege()
        rep.role = r
        rep.privilege = privileges_dict['FULL']
        rep.entity = server_pools_dict[role['sp']]
        model.DBSession.add(rep)

    populate_fence_resources()
    resources = populate_custom_fence_resources(local_node)
    model.DBSession.add_all(resources)
    #populate_cloud_datas()
    populate_state_transitions()
    populate_quota_catergories(cp_types_dict)
    model.DBSession.flush()
    transaction.commit()
    print 'Successfully setup'
    return None


def update_changes(update_from_version):
    #add 0830
    if update_from_version == '3.1.x':
        op_platform_type(update_from_version)
    if update_from_version == '2.0.2':
        update_from_version_ee2_0_2(update_from_version)
        model.DBSession.flush()
        transaction.commit()
        print 'Successfully updated to ee 3.0.1'
    #add 0830
    if update_from_version == '3.1':
        #289
        print 'update to 3.1.1'
        dc_ent = model.DBSession.query(model.Entity).filter(model.Entity.type_id == 1).first()
        from stackone.core.services.tasks import SendDeploymentStatsRptTask
        snd_dep_task = SendDeploymentStatsRptTask(u'Send Deployment Stats',\
              {'quiet':True}, [], {}, None, u'admin')
        snd_dep_task.id = 10
        snd_dep_task.interval = [model.TaskInterval(10080)]
        set_entity_details(snd_dep_task,dc_ent)
        model.DBSession.merge(snd_dep_task)
        model.DBSession.flush()
        transaction.commit()
        print 'Successfully updated to 3.1.1'
        return None
    if update_from_version == '3.1.x':
        #432
        print 'update to 3.2'
        mgd_nodes = model.DBSession.query(model.ManagedNode).all()
        for node in mgd_nodes:
            #399
            if node.is_up():
                node.isHVM = node.is_HVM()
                model.DBSession.add(node)
                continue
            model.DBSession.flush()
            transaction.commit()
            print 'Successfully updated to 3.2'
            return None
        return None
        
        


def update_from_version_ee2_0_2(update_from_version):
    print 'Updating from ee2.0.2 to ee3.0.1 .......'
    #from stackone.cloud.DbModel.CloudProvider import CloudProviderNode
    #from stackone.cloud.DbModel.TemplateProvider import TemplateProvider, TemplateGroupType
    from stackone.model.VLANManager import VLANIDPool, VLANIDPoolSPRelation, VLANID
    from stackone.model.PrivateIP import PrivateIPPoolSPRelation, DHCPServer
    #from stackone.cloud.DbModel.platforms.cms.CMSPrivateIPManager import CMSPrivateIPPool, CMSPrivateIPPoolRegionRelation, CMSPrivateIP, CMSDHCPServer
    #from stackone.cloud.DbModel.platforms.cms.CMSNetwork import CMSNetwork, CMSNetworkRegionRelation, CMSNetworkVMRelation
    from stackone.model.network import NetworkVMRelation
    from stackone.core.services.tasks import Purging
    dc_ent = model.DBSession.query(model.Entity).join(model.EntityType).filter(model.EntityType.name == constants.DATA_CENTER).first()
    is_ent = model.DBSession.query(model.Entity).join(model.EntityType).filter(model.EntityType.name == constants.IMAGE_STORE).first()
    model.DBSession.add(model.EntityRelation(dc_ent.entity_id, is_ent.entity_id, u'Children'))
    groups,entity_types,privileges,privileges_dict,cp_types_dict = authinit_update()
    cld_entities = []
    ci = {'id':3,'name':u'IaaS','type':'CLOUD_PROVIDER_FOLDER'}
    cloud = CloudProviderNode(ci['name'])
    c = model.Entity()
    c.name = ci['name']
    c.id = ci['id']
    c.entity_id = cloud.id
    c.type = entity_types[ci['type']]
    ex_clouds = model.DBSession.query(CloudProviderNode).filter(CloudProviderNode.name == ci['name']).all()
    if len(ex_clouds) == 0:
        model.DBSession.add(c)
        model.DBSession.add(cloud)

    else:
        cloud = ex_clouds[0]
        c.entity_id = cloud.id
    cld_entities.append(c)
    
    vdcs_str = {'id':4,'name':u'Virtual Data Centers','type':'VDC_FOLDER'}
    vdc_store = model.VDCStore(vdcs_str['name'])
    vdc_store.name = vdcs_str['name']
    vdc_store.id = getHexID()
    vdcs = model.Entity()
    vdcs.name = vdcs_str['name']
    vdcs.id = vdcs_str['id']
    vdcs.entity_id = vdc_store.id
    vdcs.type = entity_types[vdcs_str['type']]
    ex_iss = model.DBSession.query(model.VDCStore).filter(model.VDCStore.name == vdcs_str['name']).all()
    
    if len(ex_iss) == 0:
        model.DBSession.add(vdc_store)
        model.DBSession.add(vdcs)
    else:
        ex_store = ex_iss[0]
        vdcs.entity_id = ex_store.id
    cld_entities.append(vdcs)
    group_names = ['Desktop Managers','Server Managers']
    groups = model.DBSession.query(model.Group).filter(model.Group.group_name.in_(group_names)).all()
    for grp in groups:
        grp.type = constants.StackOne
        model.DBSession.add(grp)

    user_names = ['Joe','Sam']
    users = model.DBSession.query(model.User).filter(model.User.user_name.in_(user_names)).all()
    for usr in users:
        usr.type = constants.StackOne
        model.DBSession.add(usr)
##################
    
   #########################
    role_names = ['admin','operator','user']
    roles = model.DBSession.query(Role).filter(model.Role.name.in_(role_names)).all()
    i = 0
    for rol in roles:
        rol.type = constants.StackOne
        model.DBSession.add(rol)
        if rol.name == 'admin':
            for ent in cld_entities:
                rep = model.RoleEntityPrivilege()
                rep.role = rol
                rep.privilege = privileges[i]
                rep.entity = ent
                model.DBSession.add(rep)
        i += 1
    roles_test = ['Desktops Admins','Servers Admins']
    test_roles = model.DBSession.query(model.Role).filter(model.Role.name.in_(roles_test)).all()
    for t_rol in test_roles:
        t_rol.type = constants.StackOne
        model.DBSession.add(t_rol)
    populate_cloud_datas()
    populate_quota_catergories(cp_types_dict)
    return None


def authinit_update():
    #from stackone.cloud.DbModel.CPTypes import CPType
    user_names = ['admin', 'operator', 'user']
    users = model.DBSession.query(model.User).filter(model.User.user_name.in_(user_names)).all()

    for user in users:
        user.type = constants.StackOne
        model.DBSession.add(user)

    group_names = ['adminGroup', 'operatorGroup', 'usersGroup']
    groups = model.DBSession.query(model.Group).filter(model.Group.group_name.in_(group_names)).all()

    for grp in groups:
        grp.type = constants.StackOne
        model.DBSession.add(grp)
#        ent_types = [\
#                    {'id':10,'name':'CLOUD_VM','disp':'Cloud VM'},\
#                    {'id':11,'name':'CLOUD_TEMPLATE','disp':'Cloud Template'},\
#                    {'id':12,'name':'CLOUD_OUT_OF_BOX_TEMPLATE','disp':'Cloud out of box Template'},\
#                    {'id':13,'name':'VDC_FOLDER','disp':'VDC Folder'},\
#                    {'id':14,'name':'CLOUD_PROVIDER_FOLDER','disp':'IaaS Folder'},\
#                    {'id':15,'name':'CLOUD_PROVIDER','disp':'IaaS'},\
#                    {'id':16,'name':'VDC','disp':'Virtual Data Center'},\
#                    {'id':17,'name':'TMP_LIB','disp':'Cloud Template Library'},\
#                    {'id':18,'name':'CLOUD_TMPGRP','disp':'Cloud Template Group'},\
#                    {'id':19,'name':'CMS_SERVICE_POINT','disp':'CMS Service Point'},\
#                    {'id':20,'name':'VDC_VM_FOLDER','disp':'Cloud Virtual Machines Folder'}\
#                ]
        ent_types = [{'id': 10, 'name': 'CLOUD_VM', 'disp': 'Cloud VM'},
                        {'id': 11, 'name': 'CLOUD_TEMPLATE', 'disp': 'Cloud Template'},
                        {'id': 12, 'name': 'CLOUD_OUT_OF_BOX_TEMPLATE', 'disp': 'Cloud out of box Template'}, {'id': 13, 'name': 'VDC_FOLDER', 'disp': 'VDC Folder'},
                        {'id': 14, 'name': 'CLOUD_PROVIDER_FOLDER', 'disp': 'IaaS Folder'}, 
                        {'id': 15, 'name': 'CLOUD_PROVIDER', 'disp': 'IaaS'}, 
                        {'id': 16, 'name': 'VDC', 'disp': 'Virtual Data Center'},
                        {'id': 17, 'name': 'TMP_LIB', 'disp': 'Cloud Template Library'},
                        {'id': 18, 'namse': 'CLOUD_TMPGRP', 'disp': 'Cloud Template Group'}, 
                        {'id': 19, 'name': 'CMS_SERVICE_POINT', 'disp': 'CMS Service Point'},
                        {'id': 20, 'name': 'VDC_VM_FOLDER', 'disp': 'Cloud Virtual Machines Folder'}]
    entity_types = {}
    etypes = model.DBSession.query(model.EntityType).all()
    for etype in etypes:
        entity_types[etype.name] = etype
    for ent in ent_types:
        et = model.EntityType()
        et.name = _(ent['name'])
        et.display_name = _(ent['disp'])
        et.created_by = _('')
        et.modified_by = _('')
        et.created_date = datetime.now()
        et.modified_date = datetime.now()
        model.DBSession.add(et)
        entity_types[ent['name']] = et
#        operations_group = [\
#                        {'id':22, 'name':'FULL_VDC_STORE','desc':'Full Privilege on Vdc'},\
#                        {'id':23,'name':'OP_VDC_STORE','desc':'Operator Privilege on Vdc'},\
#                        {'id':24, 'name':'VIEW_VDC_STORE','desc':'View Privilege on Vdc'},\
#                        {'desc':  'View Privilege on Vdc', 'id': '24', 'name':  'VIEW_VDC'}, \
#                        {'desc':  'Full privilege on vm operations', 'id': ' 25', 'name':  'VM_FULL_OPS'} ,\
#                        {'desc':  'Operator privilege on vm operations', 'id': ' 26', 'name':  'VM_OP_OPS'} ,\
#                        {'desc':  'Cloud Full privilege on IaaS', 'id': ' 27', 'name':  'FULL_CLOUD_PROVIDER_FOLDER'} ,\
#                        {'desc':  'Cloud Operator privilege on IaaS', 'id': ' 28', 'name':  'OP_CLOUD_PROVIDER_FOLDER'} ,\
#                        {'desc':  'Cloud View privilege on IaaS', 'id': ' 29', 'name':  'VIEW_CLOUD_PROVIDER_FOLDER'} ,\
#                        {'desc':  'Full privilege on IaaS', 'id': ' 30', 'name':  'FULL_CLOUD_PROVIDER'} ,\
#                        {'desc':  'Operator privilege on IaaS', 'id': ' 31', 'name':  'OP_CLOUD_PROVIDER'} ,\
#                        {'desc':  'View privilege on IaaS', 'id': ' 32', 'name':  'VIEW_CLOUD_PROVIDER'} ,\
#                        {'desc':  'Cloud full privilege on vdc', 'id': ' 33', 'name':  'FULL_CLOUD_VDC'} ,\
#                        {'desc':  'Cloud operator privilege on vdc', 'id': ' 34', 'name':  'OP_CLOUD_VDC'} ,\
#                        {'desc':  'Cloud view privilege on vdc', 'id': ' 35', 'name':  'VIEW_CLOUD_VDC'} ,\
#                        {'desc':  'Cloud operator privilege on vm operations', 'id': ' 36', 'name':  'CLOUD_VM_FULL_OPS'} ,\
#                        {'desc':  'Cloud operator privilege on vm operations', 'id': ' 37', 'name':  'CLOUD_VM_OP_OPS'} ,\
#                        {'desc':  'Cloud operator privilege on vm operations', 'id': ' 38', 'name':  'CLOUD_VM_VIEW_OPS'} ,\
#                        {'desc':  'Cloud full privilege on Cloud Template Provider', 'id': ' 39', 'name':  'FULL_CLOUD_TEMPLATE_LIBRARY'} ,\
#                        {'desc':  'Cloud operator privilege on Cloud Template Provider', 'id': ' 40', 'name':  'OP_CLOUD_TEMPLATE_LIBRARY'} ,\
#                        {'desc':  'Cloud view privilege on Cloud Template Provider', 'id': ' 41', 'name':  'VIEW_CLOUD_TEMPLATE_LIBRARY'} ,\
#                        {'desc':  'Cloud full privilege on Cloud Template Group', 'id': ' 42', 'name':  'FULL_CLOUD_TEMPLATE_GROUP'} ,\
#                        {'desc':  'Cloud operator privilege on Cloud Template Group', 'id': ' 43', 'name':  'OP_CLOUD_TEMPLATE_GROUP'} ,\
#                        {'desc':  'Cloud view privilege on Cloud Template Group', 'id': ' 44', 'name':  'VIEW_CLOUD_TEMPLATE_GROUP'} ,\
#                        {'desc':  'full privilege on Cloud Templates', 'id': ' 45', 'name':  'FULL_CLOUD_TEMPLATES'} ,\
#                        {'desc':  'operator privilege on Cloud Templates', 'id': ' 46', 'name':  'OP_CLOUD_TEMPLATES'} ,\
#                        {'desc':  'view privilege on Cloud Templates', 'id': ' 47', 'name':  'VIEW_CLOUD_TEMPLATES'} ,\
#                        {'desc':  'Cloud full privilege on Cloud Templates', 'id': ' 48', 'name':  'CLOUD_TEMPLATES_FULL_OPS'} ,\
#                        {'desc':  'Cloud operator privilege on Cloud Templates', 'id': ' 49', 'name':  'CLOUD_TEMPLATES_OP_OPS'} ,\
#                        {'desc':  'Cloud view privilege on Cloud Templates', 'id': ' 50', 'name':  'CLOUD_TEMPLATES_VIEW_OPS'} ,\
#                        {'desc':  'Full Privilege on Virtual Machines Folder', 'id': ' 51', 'name':  'FULL_VDC_VM_FOLDER'} ,\
#                        {'desc':  'Operator Privilege on Virtual Machines Folder', 'id': ' 52', 'name':  'OP_VDC_VM_FOLDER'} ,\
#                        {'desc':  'View Privilege on Virtual Machines Folder', 'id': ' 53', 'name':  'VIEW_VDC_VM_FOLDER'} ,\
#                        {'desc':  'Cloud full privilege on Virtual Machines Folder', 'id': ' 54', 'name':  'FULL_CLOUD_VDC_VM_FOLDER'} ,\
#                        {'desc':  'Cloud operator privilege on Virtual Machines Folder', 'id': ' 55', 'name':  'OP_CLOUD_VDC_VM_FOLDER'} ,\
#                        {'desc':  'Cloud view privilege on Virtual Machines Folder', 'id': ' 56', 'name':  'VIEW_CLOUD_VDC_VM_FOLDER'} ,\
#                        {'desc':  'Full Privilege on CSEP', 'id': ' 57', 'name':  'FULL_CSEP'},\
#                        {'id':58,'name':'OP_CSEP','desc':'Operator Privilege on CSEP'}\
#                        ]
        operations_group = [{'id': 22, 'name': 'FULL_VDC_STORE', 'desc': 'Full Privilege on Vdc'},
                         {'id': 23, 'name': 'OP_VDC_STORE', 'desc': 'Operator Privilege on Vdc'}, 
                         {'id': 24, 'name': 'VIEW_VDC_STORE', 'desc': 'View Privilege on Vdc'}, 
                         {'id': 22, 'name': 'FULL_VDC', 'desc': 'Full Privilege on Vdc'}, 
                         {'id': 23, 'name': 'OP_VDC', 'desc': 'Operator Privilege on Vdc'}, 
                         {'id': 24, 'name': 'VIEW_VDC', 'desc': 'View Privilege on Vdc'},
                         {'id': 25, 'name': 'VM_FULL_OPS', 'desc': 'Full privilege on vm operations'}, 
                         {'id': 26, 'name': 'VM_OP_OPS', 'desc': 'Operator privilege on vm operations'}, 
                         {'id': 27, 'name': 'FULL_CLOUD_PROVIDER_FOLDER', 'desc': 'Cloud Full privilege on IaaS'}, 
                         {'id': 28, 'name': 'OP_CLOUD_PROVIDER_FOLDER', 'desc': 'Cloud Operator privilege on IaaS'}, 
                         {'id': 29, 'name': 'VIEW_CLOUD_PROVIDER_FOLDER', 'desc': 'Cloud View privilege on IaaS'}, 
                         {'id': 30, 'name': 'FULL_CLOUD_PROVIDER', 'desc': 'Full privilege on IaaS'}, 
                         {'id': 31, 'name': 'OP_CLOUD_PROVIDER', 'desc': 'Operator privilege on IaaS'}, 
                         {'id': 32, 'name': 'VIEW_CLOUD_PROVIDER', 'desc': 'View privilege on IaaS'}, 
                         {'id': 33, 'name': 'FULL_CLOUD_VDC', 'desc': 'Cloud full privilege on vdc'}, 
                         {'id': 34, 'name': 'OP_CLOUD_VDC', 'desc': 'Cloud operator privilege on vdc'}, 
                         {'id': 35, 'name': 'VIEW_CLOUD_VDC', 'desc': 'Cloud view privilege on vdc'}, 
                         {'id': 36, 'name': 'CLOUD_VM_FULL_OPS', 'desc': 'Cloud operator privilege on vm operations'}, 
                         {'id': 37, 'name': 'CLOUD_VM_OP_OPS', 'desc': 'Cloud operator privilege on vm operations'}, 
                         {'id': 38, 'name': 'CLOUD_VM_VIEW_OPS', 'desc': 'Cloud operator privilege on vm operations'}, 
                         {'id': 39, 'name': 'FULL_CLOUD_TEMPLATE_LIBRARY', 'desc': 'Cloud full privilege on Cloud Template Provider'}, 
                         {'id': 40, 'name': 'OP_CLOUD_TEMPLATE_LIBRARY', 'desc': 'Cloud operator privilege on Cloud Template Provider'}, 
                         {'id': 41, 'name': 'VIEW_CLOUD_TEMPLATE_LIBRARY', 'desc': 'Cloud view privilege on Cloud Template Provider'}, 
                         {'id': 42, 'name': 'FULL_CLOUD_TEMPLATE_GROUP', 'desc': 'Cloud full privilege on Cloud Template Group'}, 
                         {'id': 43, 'name': 'OP_CLOUD_TEMPLATE_GROUP', 'desc': 'Cloud operator privilege on Cloud Template Group'}, 
                         {'id': 44, 'name': 'VIEW_CLOUD_TEMPLATE_GROUP', 'desc': 'Cloud view privilege on Cloud Template Group'}, 
                         {'id': 45, 'name': 'FULL_CLOUD_TEMPLATES', 'desc': 'full privilege on Cloud Templates'}, 
                         {'id': 46, 'name': 'OP_CLOUD_TEMPLATES', 'desc': 'operator privilege on Cloud Templates'}, 
                         {'id': 47, 'name': 'VIEW_CLOUD_TEMPLATES', 'desc': 'view privilege on Cloud Templates'}, 
                         {'id': 48, 'name': 'CLOUD_TEMPLATES_FULL_OPS', 'desc': 'Cloud full privilege on Cloud Templates'}, 
                         {'id': 49, 'name': 'CLOUD_TEMPLATES_OP_OPS', 'desc': 'Cloud operator privilege on Cloud Templates'}, 
                         {'id': 50, 'name': 'CLOUD_TEMPLATES_VIEW_OPS', 'desc': 'Cloud view privilege on Cloud Templates'}, 
                         {'id': 51, 'name': 'FULL_VDC_VM_FOLDER', 'desc': 'Full Privilege on Virtual Machines Folder'}, 
                         {'id': 52, 'name': 'OP_VDC_VM_FOLDER', 'desc': 'Operator Privilege on Virtual Machines Folder'}, 
                         {'id': 53, 'name': 'VIEW_VDC_VM_FOLDER', 'desc': 'View Privilege on Virtual Machines Folder'}, 
                         {'id': 54, 'name': 'FULL_CLOUD_VDC_VM_FOLDER', 'desc': 'Cloud full privilege on Virtual Machines Folder'}, 
                         {'id': 55, 'name': 'OP_CLOUD_VDC_VM_FOLDER', 'desc': 'Cloud operator privilege on Virtual Machines Folder'}, 
                         {'id': 56, 'name': 'VIEW_CLOUD_VDC_VM_FOLDER', 'desc': 'Cloud view privilege on Virtual Machines Folder'}, 
                         {'id': 57, 'name': 'FULL_CSEP', 'desc': 'Full Privilege on CSEP'}, 
                         {'id': 58, 'name': 'OP_CSEP', 'desc': 'Operator Privilege on CSEP'}]
    operations_group_dict = {}
    etypes = model.DBSession.query(model.OperationGroup).all()
    
    for etype in etypes:
        operations_group_dict[etype.name] = etype
    for opgrp in operations_group:
        og = model.OperationGroup()
        model.DBSession.add(og)
        og.name = _(opgrp['name'])
        og.description = _(opgrp['desc'])
        og.created_by = _('')
        og.modified_by = _('')
        og.created_date = datetime.now()
        og.modified_date = datetime.now()
        model.DBSession.add(og)
        operations_group_dict[opgrp['name']] = og
    EC2 = constants.EC2
    CMS = constants.CMS
    EUC = constants.EUC
    OST = constants.OPENSTACK
    ALLCP = [EC2,CMS,EUC,OST]
    EC2CP = [EC2,EUC,OST]
    CMSCP = [CMS]
    cp_types = [{'name':EC2,'desc':u'Amazon EC2 Cloud Provider','display':'Amazon EC2'},\
                {'name':CMS,'desc':u'stackone-Cloud Cloud Provider','display':'stackone Cloud'},\
                {'name':EUC,'desc':u'Eucalyptus Cloud Provider','display':'Eucalyptus'},\
                {'name':OST,'desc':u'OpenStack Cloud Provider','display':'OpenStack'}\
               ]
    cp_types_dict = {}
    
    for cp_type in cp_types:
        cpt = CPType(cp_type['name'],cp_type['display'],cp_type['desc'])
        model.DBSession.add(cpt)
        cp_types_dict[cp_type['name']] = cpt
#        operations_map = [\
#                        {'display_id': 'manage_vlan_id_pool', 'separator': True, 'seq': 90, 'opr': True, 'entType': 'DATA_CENTER', 'text': 'Manage VLAN Id Pool', 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_DATA_CENTER', 'OP_DATA_CENTER'], 'id': 111, 'icon': 'manage_vlan_id_pool.png', 'op': 'MANAGE_VLAN_ID_POOL'} ,\
#                        {'display_id': 'manage_public_ip_pool', 'separator': False, 'seq': 91, 'opr': True, 'entType': 'DATA_CENTER', 'text': 'Manage Public IP Pool', 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_DATA_CENTER', 'OP_DATA_CENTER'], 'id': 111, 'icon': 'manage_public_ip_pool.png', 'op': 'MANAGE_PUBLIC_IP_POOL'} ,\
#                        {'display_id': 'edit_vdc', 'separator': False, 'groups': ['FULL_VDC', 'OP_VDC'], 'seq': 212, 'entType': 'VDC', 'text': 'Edit Virtual Data Center', 'icon': 'file_edit.png', 'id': 85, 'op': 'EDIT_VDC'} ,\
#                        {'display_id': 'delete_vdc', 'separator': False, 'groups': ['FULL_VDC', 'OP_VDC'], 'seq': 213, 'entType': 'VDC', 'text': 'Delete Virtual Data Center', 'icon': 'delete.png', 'id': 86, 'op': 'DELETE_VDC'} ,\
#                        {'display_id': 'provision_vm', 'separator': False, 'groups': ['FULL_VDC_VM_FOLDER', 'OP_VDC_VM_FOLDER', 'FULL_CLOUD_VDC_VM_FOLDER', 'OP_CLOUD_VDC_VM_FOLDER'], 'seq': 214, 'entType': 'VDC_VM_FOLDER', 'text': 'Provision Virtual Machine', 'icon': 'provision_vm.png', 'id': 87, 'op': 'CLOUD_PROVISION_VM'} ,\
#                        {'display_id': 'connect', 'separator': False, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS', 'CLOUD_VM_VIEW_OPS'], 'seq': 215, 'entType': 'CLOUD_VM', 'text': 'Connect', 'icon': 'small_connect.png', 'id': 88, 'op': 'CLOUD_CONNECT'} ,\
#                        {'display_id': 'start', 'separator': False, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS', 'CLOUD_VM_VIEW_OPS'], 'seq': 216, 'entType': 'CLOUD_VM', 'text': 'Start', 'icon': 'small_start.png', 'id': 89, 'op': 'CLOUD_START_VM'} ,\
#                        {'display_id': 'stop', 'separator': False, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS', 'CLOUD_VM_VIEW_OPS'], 'seq': 217, 'entType': 'CLOUD_VM', 'text': 'Stop', 'icon': 'small_shutdown.png', 'id': 90, 'op': 'CLOUD_STOP_VM'} ,\
#                        {'display_id': 'terminate', 'separator': False, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS'], 'seq': 218, 'entType': 'CLOUD_VM', 'text': 'Destroy', 'icon': 'delete.png', 'id': 91, 'op': 'CLOUD_DELETE_VM'} ,\
#                        {'display_id': 'edit_vm', 'separator': False, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS'], 'seq': 219, 'entType': 'CLOUD_VM', 'text': 'Edit', 'icon': 'file_edit.png', 'id': 92, 'op': 'CLOUD_EDIT_VM'} ,\
#                        {'display_id': 'reboot', 'separator': False, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS', 'CLOUD_VM_VIEW_OPS'], 'seq': 220, 'entType': 'CLOUD_VM', 'text': 'Reboot', 'icon': 'small_reboot.png', 'id': 93, 'op': 'CLOUD_REBOOT_VM'} ,\
#                        {'display_id': 'add_cloud_provider', 'separator': False, 'seq': 224, 'opr': True, 'entType': 'CLOUD_PROVIDER_FOLDER', 'text': 'Add IaaS', 'groups': ['FULL_CLOUD_PROVIDER_FOLDER'], 'id': 95, 'icon': 'add.png', 'op': 'ADD_CLOUD_PROVIDER'} ,\
#                        {'display_id': 'provision_vdc', 'separator': False, 'groups': ['FULL_VDC_STORE', 'OP_VDC_STORE'], 'seq': 225, 'entType': 'VDC_FOLDER', 'text': 'Provision Virtual Data Center', 'icon': 'provision_vm.png', 'id': 96, 'op': 'PROVISION_VDC'} ,\
#                        {'display_id': 'cloud_public_ip', 'separator': False, 'seq': 200, 'opr': True, 'entType': 'VDC', 'text': 'Manage Public IP', 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'id': 97, 'icon': 'Publicip.png', 'op': 'STORAGE_POOL'} ,\
#                        {'display_id': 'cloud_key_pair', 'separator': False, 'seq': 201, 'opr': True, 'entType': 'VDC', 'text': 'Manage Key Pair', 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'id': 98, 'icon': 'KeyPairs.png', 'op': 'STORAGE_POOL'} ,\
#                        {'display_id': 'cloud_security_group', 'separator': False, 'seq': 202, 'opr': True, 'entType': 'VDC', 'text': 'Manage Security Group', 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'id': 99, 'icon': 'Securitygroups.png', 'op': 'STORAGE_POOL'} ,\
#                        {'display_id': 'cloud_storage', 'separator': False, 'seq': 203, 'opr': True, 'entType': 'VDC', 'text': 'Manage Storage', 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'id': 100, 'icon': 'StorageManagement.png', 'op': 'STORAGE_POOL'} ,\
#                        {'display_id': 'edit_cloud_provider', 'separator': False, 'seq': 155, 'opr': True, 'entType': 'CLOUD_PROVIDER', 'text': 'Edit IaaS', 'groups': ['FULL_CLOUD_PROVIDER', 'OP_CLOUD_PROVIDER'], 'id': 101, 'icon': 'file_edit.png', 'op': 'EDIT_CLOUD_PROVIDER'} ,\
#                        {'display_id': 'create_template', 'separator': False, 'seq': 146, 'opr': True, 'entType': 'CLOUD_TEMPLATE', 'text': 'Create Like', 'groups': ['CLOUD_TEMPLATES_FULL_OPS', 'CLOUD_TEMPLATES_OP_OPS', 'FULL_CLOUD_TEMPLATES', 'OP_CLOUD_TEMPLATES'], 'id': 102, 'icon': 'provision_vm.png', 'op': 'CREATE_TEMPLATE'} ,\
#                        {'display_id': 'delete_cloud_provider', 'separator': False, 'seq': 156, 'opr': True, 'entType': 'CLOUD_PROVIDER', 'text': 'Delete IaaS', 'groups': ['FULL_CLOUD_PROVIDER', 'OP_CLOUD_PROVIDER'], 'id': 105, 'icon': 'delete.png', 'op': 'DELETE_CLOUD_PROVIDER'} ,\
#                        {'display_id': 'create_template', 'separator': False, 'seq': 221, 'opr': True, 'entType': 'CLOUD_VM', 'text': 'Create Template', 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS'], 'id': 106, 'icon': 'provision_vm.png', 'op': 'CREATE_TEMPLATE'} ,\
#                        {'display_id': 'annotate', 'separator': False, 'seq': 222, 'opr': True, 'entType': 'DOMAIN', 'text': 'Annotate', 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'id': 107, 'icon': 'rename.png', 'op': 'ANNOTATE'} ,\
#                        {'display_id': 'annotate', 'separator': False, 'seq': 223, 'opr': True, 'entType': 'MANAGED_NODE', 'text': 'Annotate', 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'id': 108, 'icon': 'rename.png', 'op': 'ANNOTATE'} ,\
#                        {'display_id': 'cloud_snapshot', 'separator': False, 'seq': 203, 'opr': True, 'entType': 'VDC', 'text': 'Manage Snapshot', 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'id': 109, 'icon': 'StorageManagement.png', 'op': 'STORAGE_POOL'} ,\
#                        {'display_id': 'cloud_network', 'separator': False, 'seq': 204, 'opr': True, 'entType': 'VDC,CMS_SERVICE_POINT', 'text': 'Manage Network', 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC', 'FULL_CSEP', 'OP_CSEP'], 'id': 110, 'icon': 'manage_virtual_networks.png', 'op': 'MANAGE_NETWORK'} \
#
#                    
#                    ]
        operations_map = [{'id': 111, 'op': 'MANAGE_VLAN_ID_POOL', 'text': 'Manage VLAN Id Pool', 'display_id': 'manage_vlan_id_pool', 'entType': 'DATA_CENTER', 'opr': True, 'separator': True, 'display': True, 'seq': 90, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_DATA_CENTER', 'OP_DATA_CENTER'], 'icon': 'manage_vlan_id_pool.png'}, 
                          {'id': 111, 'op': 'MANAGE_PUBLIC_IP_POOL', 'text': 'Manage Public IP Pool', 'display_id': 'manage_public_ip_pool', 'entType': 'DATA_CENTER', 'opr': True, 'separator': False, 'display': True, 'seq': 91, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE', 'FULL_SERVER_POOL', 'OP_SERVER_POOL', 'FULL_DATA_CENTER', 'OP_DATA_CENTER'], 'icon': 'manage_public_ip_pool.png'}, 
                          {'id': 85, 'op': 'EDIT_VDC', 'text': 'Edit Virtual Data Center', 'display_id': 'edit_vdc', 'entType': 'VDC', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 212, 'groups': ['FULL_VDC', 'OP_VDC'], 'icon': 'file_edit.png'}, 
                          {'id': 86, 'op': 'DELETE_VDC', 'text': 'Delete Virtual Data Center', 'display_id': 'delete_vdc', 'entType': 'VDC', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 213, 'groups': ['FULL_VDC', 'OP_VDC'], 'icon': 'delete.png'}, 
                          {'id': 87, 'op': 'CLOUD_PROVISION_VM', 'text': 'Provision Virtual Machine', 'display_id': 'provision_vm', 'entType': 'VDC_VM_FOLDER', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 214, 'groups': ['FULL_VDC_VM_FOLDER', 'OP_VDC_VM_FOLDER', 'FULL_CLOUD_VDC_VM_FOLDER', 'OP_CLOUD_VDC_VM_FOLDER'], 'icon': 'provision_vm.png'}, 
                          {'id': 88, 'op': 'CLOUD_CONNECT', 'text': 'Connect', 'display_id': 'connect', 'entType': 'CLOUD_VM', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 215, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS', 'CLOUD_VM_VIEW_OPS'], 'icon': 'small_connect.png'}, 
                          {'id': 89, 'op': 'CLOUD_START_VM', 'text': 'Start', 'display_id': 'start', 'entType': 'CLOUD_VM', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 216, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS', 'CLOUD_VM_VIEW_OPS'], 'icon': 'small_start.png'}, 
                          {'id': 90, 'op': 'CLOUD_STOP_VM', 'text': 'Stop', 'display_id': 'stop', 'entType': 'CLOUD_VM', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 217, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS', 'CLOUD_VM_VIEW_OPS'], 'icon': 'small_shutdown.png'}, 
                          {'id': 91, 'op': 'CLOUD_DELETE_VM', 'text': 'Destroy', 'display_id': 'terminate', 'entType': 'CLOUD_VM', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 218, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS'], 'icon': 'delete.png'}, 
                          {'id': 92, 'op': 'CLOUD_EDIT_VM', 'text': 'Edit', 'display_id': 'edit_vm', 'entType': 'CLOUD_VM', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 219, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS'], 'icon': 'file_edit.png'}, 
                          {'id': 93, 'op': 'CLOUD_REBOOT_VM', 'text': 'Reboot', 'display_id': 'reboot', 'entType': 'CLOUD_VM', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 220, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS', 'CLOUD_VM_VIEW_OPS'], 'icon': 'small_reboot.png'}, 
                          {'id': 95, 'op': 'ADD_CLOUD_PROVIDER', 'text': 'Add IaaS', 'display_id': 'add_cloud_provider', 'entType': 'CLOUD_PROVIDER_FOLDER', 'opr': True, 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 224, 'groups': ['FULL_CLOUD_PROVIDER_FOLDER'], 'icon': 'add.png'}, 
                          {'id': 96, 'op': 'PROVISION_VDC', 'text': 'Provision Virtual Data Center', 'display_id': 'provision_vdc', 'entType': 'VDC_FOLDER', 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 225, 'groups': ['FULL_VDC_STORE', 'OP_VDC_STORE'], 'icon': 'provision_vm.png'}, 
                          {'id': 97, 'op': 'STORAGE_POOL', 'text': 'Manage Public IP', 'display_id': 'cloud_public_ip', 'entType': 'VDC', 'opr': True, 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 200, 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'icon': 'Publicip.png'}, 
                          {'id': 98, 'op': 'STORAGE_POOL', 'text': 'Manage Key Pair', 'display_id': 'cloud_key_pair', 'entType': 'VDC', 'opr': True, 'CPTYPE': EC2CP, 'separator': False, 'display': True, 'seq': 201, 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'icon': 'KeyPairs.png'}, 
                          {'id': 99, 'op': 'STORAGE_POOL', 'text': 'Manage Security Group', 'display_id': 'cloud_security_group', 'entType': 'VDC', 'opr': True, 'CPTYPE': EC2CP, 'separator': False, 'display': True, 'seq': 202, 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'icon': 'Securitygroups.png'}, 
                          {'id': 100, 'op': 'STORAGE_POOL', 'text': 'Manage Storage', 'display_id': 'cloud_storage', 'entType': 'VDC', 'opr': True, 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 203, 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'icon': 'StorageManagement.png'}, 
                          {'id': 101, 'op': 'EDIT_CLOUD_PROVIDER', 'text': 'Edit IaaS', 'display_id': 'edit_cloud_provider', 'entType': 'CLOUD_PROVIDER', 'CPTYPE': ALLCP, 'opr': True, 'separator': False, 'display': True, 'seq': 155, 'groups': ['FULL_CLOUD_PROVIDER', 'OP_CLOUD_PROVIDER'], 'icon': 'file_edit.png'}, 
                          {'id': 102, 'op': 'CREATE_TEMPLATE', 'text': 'Create Like', 'display_id': 'create_template', 'entType': 'CLOUD_TEMPLATE', 'opr': True, 'CPTYPE': ALLCP, 'separator': False, 'display': True, 'seq': 146, 'groups': ['CLOUD_TEMPLATES_FULL_OPS', 'CLOUD_TEMPLATES_OP_OPS', 'FULL_CLOUD_TEMPLATES', 'OP_CLOUD_TEMPLATES'], 'icon': 'provision_vm.png'}, 
                          {'id': 105, 'op': 'DELETE_CLOUD_PROVIDER', 'text': 'Delete IaaS', 'display_id': 'delete_cloud_provider', 'entType': 'CLOUD_PROVIDER', 'CPTYPE': ALLCP, 'opr': True, 'separator': False, 'display': True, 'seq': 156, 'groups': ['FULL_CLOUD_PROVIDER', 'OP_CLOUD_PROVIDER'], 'icon': 'delete.png'}, 
                          {'id': 106, 'op': 'CREATE_TEMPLATE', 'text': 'Create Template', 'display_id': 'create_template', 'entType': 'CLOUD_VM', 'opr': True, 'CPTYPE': EC2CP, 'separator': False, 'display': True, 'seq': 221, 'groups': ['VM_FULL_OPS', 'VM_OP_OPS', 'CLOUD_VM_FULL_OPS', 'CLOUD_VM_OP_OPS'], 'icon': 'provision_vm.png'}, 
                          {'id': 107, 'op': 'ANNOTATE', 'text': 'Annotate', 'display_id': 'annotate', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 222, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'rename.png'}, 
                          {'id': 108, 'op': 'ANNOTATE', 'text': 'Annotate', 'display_id': 'annotate', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': False, 'display': True, 'seq': 223, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'rename.png'}, 
                          {'id': 109, 'op': 'STORAGE_POOL', 'text': 'Manage Snapshot', 'display_id': 'cloud_snapshot', 'entType': 'VDC', 'opr': True, 'separator': False, 'display': True, 'seq': 203, 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC'], 'icon': 'StorageManagement.png'}, 
                          {'id': 110, 'op': 'MANAGE_NETWORK', 'text': 'Manage Network', 'display_id': 'cloud_network', 'entType': 'VDC,CMS_SERVICE_POINT', 'opr': True, 'CPTYPE': CMSCP, 'separator': False, 'display': True, 'seq': 204, 'groups': ['FULL_VDC', 'OP_VDC', 'FULL_CLOUD_VDC', 'OP_CLOUD_VDC', 'FULL_CSEP', 'OP_CSEP'], 'icon': 'manage_virtual_networks.png'}]
    i = 0
    for opmap in operations_map:
        i += 1
        o = model.Operation()
        o.name = _(opmap['op'])
        o.icon = _(opmap['icon'])
        o.description = _(opmap['op'])
        o.created_by = _('')
        o.modified_by = _('')
        o.created_date = datetime.now()
        o.modified_date = datetime.now()
        
        if opmap.has_key('text'):
            o.display_name = _(opmap['text'])
    if opmap.has_key('display_id'):
        o.display_id = _(opmap['display_id'])
    for entType in opmap['entType'].split(','):
        o.entityType.append(entity_types[entType])
    if opmap.has_key('display'):
        o.display = opmap['display']
    if opmap.has_key('seq'):
        o.display_seq = opmap['seq']
    if opmap.has_key('separator'):
        o.has_separator = opmap['separator']

    grps = opmap['groups']
    for grp in grps:
        og = operations_group_dict[grp]
        o.opsGroup.append(og)
    cpts = opmap.get('CPTYPE',None)
    if cpts:
        for cp in cpts:
            og = cp_types_dict[cp]
            o.cpTypes.append(og)
    model.DBSession.add(o)
#    operations_map = [
#                    {'display_id': 'server_maintenance', 'separator': False, 'seq': 998, 'opr': True, 'entType': 'MANAGED_NODE', 'text': 'Maintenance', 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'id': 107, 'icon': 'general.gif', 'op': 'SERVER_MAINTENANACE'} ,\
#                    {'display_id': 'start_view_console', 'separator': False, 'seq': 113, 'opr': True, 'entType': 'DOMAIN', 'text': 'Start and View Console', 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'id': 109, 'icon': 'provision_vm.png', 'op': 'START_VIEW_CONSOLE'}\
#                    ]
    operations_map = [{'id': 107, 'op': 'SERVER_MAINTENANACE', 'text': 'Maintenance', 'display_id': 'server_maintenance', 'entType': 'MANAGED_NODE', 'opr': True, 'separator': False, 'display': True, 'seq': 998, 'groups': ['FULL_MANAGED_NODE', 'OP_MANAGED_NODE'], 'icon': 'general.gif'}, 
                      {'id': 109, 'op': 'START_VIEW_CONSOLE', 'text': 'Start and View Console', 'display_id': 'start_view_console', 'entType': 'DOMAIN', 'opr': True, 'separator': False, 'display': True, 'seq': 113, 'groups': ['FULL_DOMAIN', 'OP_DOMAIN'], 'icon': 'provision_vm.png'}]
    for opmap in operations_map:
        Operations = model.DBSession.query(model.Operation).filter(model.Operation.name == opmap['op']).first()
        Operations.icon = opmap['icon']
        model.DBSession.add(Operations)

#    operations_map = [\
#                    {'display_id':'add_network_def', 'groups':['FULL_CLOUD_PROVIDER', 'OP_CLOUD_PROVIDER', 'FULL_VDC', 'OP_VDC', 'FULL_CSEP', 'OP_CSEP'], 'opr':True, 'entType':'CLOUD_PROVIDER,VDC,CMS_SERVICE_POINT', 'icon':'.png', 'id':9, 'op':'ADD_NETWORK_DEF'},
#                    {'display_id':'edit_network_def', 'groups':['FULL_CSEP', 'OP_CSEP'], 'opr':True, 'entType':'CMS_SERVICE_POINT', 'icon':'.png','id':10, 'op':'UPDATE_NETWORK_DEF'},                                                                                   
#                    {'display_id':'remove_network_def', 'groups':['FULL_CSEP', 'OP_CSEP'], 'opr':True, 'entType':'CMS_SERVICE_POINT', 'icon':'.png', 'id':12, 'op':'REMOVE_NETWORK_DEF'}
#                    ]
    operations_map = [{'id': 9, 'op': 'ADD_NETWORK_DEF', 'display_id': 'add_network_def', 'entType': 'CLOUD_PROVIDER,VDC,CMS_SERVICE_POINT', 'opr': True, 'groups': ['FULL_CLOUD_PROVIDER', 'OP_CLOUD_PROVIDER', 'FULL_VDC', 'OP_VDC', 'FULL_CSEP', 'OP_CSEP'], 'icon': '.png'}, 
                      {'id': 10, 'op': 'UPDATE_NETWORK_DEF', 'display_id': 'edit_network_def', 'entType': 'CMS_SERVICE_POINT', 'opr': True, 'groups': ['FULL_CSEP', 'OP_CSEP'], 'icon': '.png'}, 
                      {'id': 12, 'op': 'REMOVE_NETWORK_DEF', 'display_id': 'remove_network_def', 'entType': 'CMS_SERVICE_POINT', 'opr': True, 'groups': ['FULL_CSEP', 'OP_CSEP'], 'icon': '.png'}]

    for opmap in operations_map:
        Oper = model.DBSession.query(Operation).filter(model.Operation.name == opmap['op']).first()
        for entType in opmap['entType'].split(','):
            Oper.entityType.append(entity_types[entType])
        grps = opmap['groups']
        for grp in grps:
            og = operations_group_dict[grp]
            Oper.opsGroup.append(og)
        model.DBSession.add(Oper)

    privileges_dict = {}
    privileges = []
#    privs = [\
#            {'type': constants.StackOne, 'id': 1, 'groups': ['FULL_CLOUD_PROVIDER_FOLDER', 'FULL_VDC_STORE', 'FULL_VDC',  'VM_FULL_OPS', 'FULL_CLOUD_PROVIDER', 'FULL_CLOUD_TEMPLATE_LIBRARY', 'FULL_CLOUD_TEMPLATE_GROUP',  'FULL_CLOUD_TEMPLATES', 'FULL_VDC_VM_FOLDER', 'FULL_CSEP'], 'name': 'FULL'} ,\
#            {'type': constants.StackOne, 'id': 2, 'groups': ['OP_VDC', 'OP_VDC_STORE', 'VM_OP_OPS', 'OP_CLOUD_PROVIDER', 'OP_CLOUD_PROVIDER_FOLDER',  'OP_CLOUD_TEMPLATE_LIBRARY', 'OP_CLOUD_TEMPLATE_GROUP', 'OP_CLOUD_TEMPLATES', 'OP_VDC_VM_FOLDER', 'OP_CSEP'], 'name': 'OPERATOR'} ,\
#            {'type': constants.StackOne, 'id': 3, 'groups': ['VIEW_VDC_STORE', 'VIEW_VDC_VM_FOLDER', 'VIEW_CLOUD_PROVIDER', 'CLOUD_TEMPLATES_VIEW_OPS', 'VIEW_VDC',  'VIEW_CLOUD_PROVIDER_FOLDER', 'VIEW_CLOUD_TEMPLATE_LIBRARY', 'VIEW_CLOUD_TEMPLATE_GROUP', 'VIEW_CLOUD_TEMPLATES'], 'name': 'VIEW'} \
#            
#            ]
    privs = [{'id': 1, 'name': 'FULL', 'groups': ['FULL_CLOUD_PROVIDER_FOLDER', 'FULL_VDC_STORE', 'FULL_VDC', 'VM_FULL_OPS', 'FULL_CLOUD_PROVIDER', 'FULL_CLOUD_TEMPLATE_LIBRARY', 'FULL_CLOUD_TEMPLATE_GROUP', 'FULL_CLOUD_TEMPLATES', 'FULL_VDC_VM_FOLDER', 'FULL_CSEP'], 'type': constants.StackOne}, 
             {'id': 2, 'name': 'OPERATOR', 'groups': ['OP_VDC', 'OP_VDC_STORE', 'VM_OP_OPS', 'OP_CLOUD_PROVIDER', 'OP_CLOUD_PROVIDER_FOLDER', 'OP_CLOUD_TEMPLATE_LIBRARY', 'OP_CLOUD_TEMPLATE_GROUP', 'OP_CLOUD_TEMPLATES', 'OP_VDC_VM_FOLDER', 'OP_CSEP'], 'type': constants.StackOne}, 
             {'id': 3, 'name': 'VIEW', 'groups': ['VIEW_VDC_STORE', 'VIEW_VDC_VM_FOLDER', 'VIEW_CLOUD_PROVIDER', 'CLOUD_TEMPLATES_VIEW_OPS', 'VIEW_VDC', 'VIEW_CLOUD_PROVIDER_FOLDER', 'VIEW_CLOUD_TEMPLATE_LIBRARY', 'VIEW_CLOUD_TEMPLATE_GROUP', 'VIEW_CLOUD_TEMPLATES'], 'type': constants.StackOne}]

    
    for priv in privs:
        Privileg = model.DBSession.query(model.Privilege).filter(model.Privilege.name == priv['name']).first()
        Privileg.type = priv['type']
        grps = priv['groups']
        for grp in grps:
            og = operations_group_dict[grp]
            Privileg.opGroups.append(og)
        model.DBSession.add(Privileg)
        privileges.append(Privileg)
        privileges_dict[priv['name']] = Privileg

    privs = [\
                {'type': constants.CLOUD, 'id': 4, 'groups': ['FULL_CLOUD_VDC', 'CLOUD_VM_FULL_OPS',  'CLOUD_TEMPLATES_FULL_OPS', 'FULL_CLOUD_VDC_VM_FOLDER'], 'name': 'FULL_CLOUD'} ,\
                {'type': constants.CLOUD, 'id': 5, 'groups': ['OP_CLOUD_VDC', 'CLOUD_VM_OP_OPS',  'CLOUD_TEMPLATES_OP_OPS', 'OP_CLOUD_VDC_VM_FOLDER'], 'name': 'OPERATOR_CLOUD'} ,\
                {'type': constants.CLOUD, 'id': 6, 'groups': ['VIEW_CLOUD_VDC', 'CLOUD_VM_VIEW_OPS', 'CLOUD_TEMPLATES_VIEW_OPS',  'VIEW_CLOUD_VDC_VM_FOLDER'], 'name': 'VIEW_CLOUD'} \
            ]
    for priv in privs:
        #6469
        #add0830
        pri = model.Privilege
        #privileges.append(pri)
        pri.name = _(priv['name'])
        grps = priv['groups']
        pri.created_by  = _('')
        pri.modified_by  = _('')
        pri.created_date  = datetime.now()
        pri.modified_date  = datetime.now()
        #pri.type  = _('')
        #pri.created_by  = _(priv['type'])
        pri.type  = _(priv['type'])
        privileges_dict[priv['name']] = pri
        privileges.append(pri)
        for grp in grps:
            og = operations_group_dict[grp]
            pri.opGroups.append(og)
        model.DBSession.add(pri)
    return (groups, entity_types, privileges, privileges_dict, cp_types_dict)


def set_entity_details(task, dc_ent):
    task.set_entity_info(dc_ent)

# def populate_cloud_datas():
#     #from stackone.cloud.DbModel.platforms.ec2.EC2CloudProvider import LookUPEC2ServiceOfferings, LookUPEC2ServiceOfferingCategories
#     #from stackone.cloud.DbModel.platforms.euc.EUCCloudProvider import LookUPEUCServiceOfferings, LookUPEUCServiceOfferingCategories
#     #from stackone.cloud.DbModel.platforms.openstack.OpenStackCloudProvider import LookUPOpenStackServiceOfferings, LookUPOpenStackServiceOfferingCategories

#     try:
#         for item in LookUPEC2ServiceOfferingCategories.CATEGORIES:
#             soc = LookUPEC2ServiceOfferingCategories(item)
#             model.DBSession.add(soc)
#         for item in LookUPEC2ServiceOfferings.INSTANCE_TYPE_DETAILS:
#             so = LookUPEC2ServiceOfferings(item.get('api_name'))
#             desc_tuple = (item.get('cpu_units'), item.get('memory'), item.get('storage'), item.get('platform'))
#             so.description = '%s EC2 Compute Unit | %s GB Memory | %s GB Storage | %s-bit Platform' % desc_tuple
#             so.memory = item.get('memory')
#             so.cpu_units = item.get('cpu_units')
#             so.storage = item.get('storage')
#             so.platform = item.get('platform')
#             so.io_performance = item.get('io_performance')
#             so.api_name = item.get('api_name')
#             so.type = item.get('type')
#             so.category_name = item.get('category_name')
#             cat = model.DBSession.query(LookUPEC2ServiceOfferingCategories).filter(LookUPEC2ServiceOfferingCategories.provider_type == u'EC2').filter(LookUPEC2ServiceOfferingCategories.name == item.get('category_name')).first()
#             if cat:
#                 so.category_id = cat.id
#             model.DBSession.add(so)
#         for item in LookUPEUCServiceOfferingCategories.CATEGORIES:
#             soc = LookUPEUCServiceOfferingCategories(item)
#             model.DBSession.add(soc)
#         for item in LookUPEUCServiceOfferings.INSTANCE_TYPE_DETAILS:
#             so = LookUPEUCServiceOfferings(item.get('api_name'))
#             desc_tuple = (item.get('cpu_units'), item.get('memory'), item.get('storage'), item.get('platform'))
#             so.description = '%s EUC Compute Unit | %s GB Memory | %s GB Storage | %s-bit Platform' % desc_tuple
#             so.memory = item.get('memory')
#             so.cpu_units = item.get('cpu_units')
#             so.storage = item.get('storage')
#             so.platform = item.get('platform')
#             so.io_performance = item.get('io_performance')
#             so.api_name = item.get('api_name')
#             so.type = item.get('type')
#             so.category_name = item.get('category_name')
#             cat = model.DBSession.query(LookUPEUCServiceOfferingCategories).filter(LookUPEUCServiceOfferingCategories.provider_type == u'EUC').filter(LookUPEUCServiceOfferingCategories.name == item.get('category_name')).first()
#             if cat:
#                 so.category_id = cat.id
#             model.DBSession.add(so)
#         for item in LookUPOpenStackServiceOfferingCategories.CATEGORIES:
#             soc = LookUPOpenStackServiceOfferingCategories(item)
#             model.DBSession.add(soc)
#         for item in LookUPOpenStackServiceOfferings.INSTANCE_TYPE_DETAILS:
#             so = LookUPOpenStackServiceOfferings(item.get('api_name'))
#             desc_tuple = (item.get('cpu_units'), item.get('memory'), item.get('storage'), item.get('platform'))
#             so.description = '%s OpenStack Compute Unit | %s GB Memory | %s GB Storage | %s-bit Platform' % desc_tuple
#             so.memory = item.get('memory')
#             so.cpu_units = item.get('cpu_units')
#             so.storage = item.get('storage')
#             so.platform = item.get('platform')
#             so.io_performance = item.get('io_performance')
#             so.api_name = item.get('api_name')
#             so.type = item.get('type')
#             so.category_name = item.get('category_name')
#             cat = model.DBSession.query(LookUPOpenStackServiceOfferingCategories).filter(LookUPOpenStackServiceOfferingCategories.provider_type == u'OPENSTACK').filter(LookUPOpenStackServiceOfferingCategories.name == item.get('category_name')).first()
#             if cat:
#                 so.category_id = cat.id
#             model.DBSession.add(so)
#     except Exception as ex:
#         import traceback
#         traceback.print_exc()


def populate_fence_resources():
    try:
        from stackone.core.ha.ha_fence import HAFenceResourceTypeMeta, HAFenceResourceType
        fence_opts = constants.FENCE_OPTS
        fence_cmd = constants.FENCE_CMD_SCRIPT
        pretty_names = constants.PRETTY_NAME_ATTRS
        instance_attrs = constants.FENCE_FI_ATTRS
        device_attrs = constants.FENCE_FD_ATTRS
        field_types = constants.FIELD_TYPES
        field_datatypes = constants.FIELD_DATATYPES
        fence_desc = constants.FENCE_DESC
        fence_cl = constants.FENCE_CL
        for opt in fence_opts.keys():
            cmd_script = fence_cmd[opt]
            resource = HAFenceResourceType(to_unicode(opt), to_unicode(fence_opts[opt]), to_unicode(cmd_script.get('cmd', opt)), to_unicode(cmd_script['loc']), None, to_unicode(fence_cl[opt]), to_unicode(fence_desc[opt]))
            i = 0
            for inst in instance_attrs[opt]:
                meta = HAFenceResourceTypeMeta(to_unicode(inst), to_unicode(pretty_names.get(inst, inst)), to_unicode(field_types.get(inst, 'textfield')), to_unicode(field_datatypes.get(inst, '')), None, instance_attrs[opt].index(inst))
                i = instance_attrs[opt].index(inst)
                meta.is_instance = True
                resource.meta.append(meta)
            i += 1
            meta = HAFenceResourceTypeMeta(to_unicode('action'), to_unicode('Action'), to_unicode('combobox'), to_unicode('text'), sequence=i, values=to_unicode("[['on', 'On'],['off','Off'],['reboot','Reboot']]"))
            meta.is_instance = True
            resource.meta.append(meta)
            for dev in device_attrs[opt]:
                meta = HAFenceResourceTypeMeta(to_unicode(dev), to_unicode(pretty_names.get(dev, dev)), to_unicode(field_types.get(dev, 'textfield')), to_unicode(field_datatypes.get(dev, '')), None, device_attrs[opt].index(dev))
                meta.is_resource = True
                resource.meta.append(meta)
            model.DBSession.add(resource)
    except Exception as ex:
        import traceback
        traceback.print_exc()


def populate_sp_adv_options(entity):
    try:
        from stackone.model.Entity import EntityAttribute
        adv_opts = constants.ADV_OPTIONS
        for name in adv_opts:
            value = adv_opts[name]
            ea = EntityAttribute(to_unicode(name), to_unicode(value))
            entity.attributes.append(ea)
        return entity
    except Exception as ex:
        import traceback
        traceback.print_exc()


def populate_state_transitions():
    try:
        from stackone.model.availability import StateTransition
        transition_dict = {model.EntityType.DOMAIN: [{'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.KILL,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.STOP,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.REBOOT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.REMOVE,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.COLLECT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.EDIT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': constants.BACKING_UP,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': constants.RESTORING,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.DWM,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.RESUME,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.KILL,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.STOP,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.REBOOT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.COLLECT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.EDIT,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.REMOVE,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.REMOVE,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': constants.BACKING_UP,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': constants.RESTORING,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.DWM,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.START,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.COLLECT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.REMOVE,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.EDIT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.DWM,
                                    'res': True},
                                   {'curr': model.VM.START,
                                    'curr_owner': constants.HA,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSE,
                                    'curr_owner': constants.HA,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSE,
                                    'curr_owner': constants.HA,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.MIGRATE,
                                    'curr_owner': constants.HA,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': constants.BACKING_UP,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.START,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.STOP,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.KILL,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.RESUME,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.STOP,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.CORE,
                                    'new': constants.RESTORING,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.STOP,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.START,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.COLLECT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.PAUSE,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.COLLECT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.RESUME,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.COLLECT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.REBOOT,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.COLLECT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.STOP,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.COLLECT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.STOP,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.KILL,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.KILL,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.COLLECT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.REMOVE,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.COLLECT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.EDIT,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.COLLECT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.HA_FAILOVER,
                                    'curr_owner': constants.HA,
                                    'new': model.VM.COLLECT,
                                    'requester': constants.CORE,
                                    'res': True},
                                   {'curr': model.VM.HA_FAILOVER,
                                    'curr_owner': constants.HA,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.HA_FAILOVER,
                                    'curr_owner': constants.HA,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.HA_FAILOVER,
                                    'curr_owner': constants.HA,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.HA_FAILOVER,
                                    'curr_owner': constants.HA,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.BACKUP,
                                    'new': constants.BACKING_UP,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.BACKUP,
                                    'new': constants.BACKING_UP,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.BACKUP,
                                    'new': constants.BACKING_UP,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.START,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.STOP,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.RESUME,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': constants.BACKING_UP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.STOP,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': constants.BACKING_UP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': constants.BACKING_UP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.RESUME,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': constants.BACKING_UP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.START,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.STOP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.KILL,
                                    'requester': constants.BACKUP,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.RESTORE,
                                    'new': constants.RESTORING,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.RESTORE,
                                    'new': constants.RESTORING,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.RESTORE,
                                    'new': constants.RESTORING,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.SHUTDOWN,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.START,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.STOP,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.RUNNING,
                                    'curr_owner': constants.CORE,
                                    'new': model.VM.KILL,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.PAUSED,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.RESUME,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': constants.RESTORING,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.STOP,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.STOP,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.KILL,
                                    'requester': constants.RESTORE,
                                    'res': True},
                                   {'curr': model.VM.MIGRATE,
                                    'curr_owner': constants.DWM,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.MIGRATE,
                                    'curr_owner': constants.DWM,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.MIGRATE,
                                    'curr_owner': constants.DWM,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': constants.BACKING_UP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': constants.BACKING_UP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': constants.BACKING_UP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': constants.BACKING_UP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.START,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.START,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.START,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.START,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.STOP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.STOP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.STOP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.STOP,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSE,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSE,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSE,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSE,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RESUME,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RESUME,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RESUME,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RESUME,
                                    'curr_owner': constants.BACKUP,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': constants.RESTORING,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': constants.RESTORING,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': constants.RESTORING,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': constants.RESTORING,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.START,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.START,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.START,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.START,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.STOP,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.STOP,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.STOP,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.STOP,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSE,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSE,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSE,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.PAUSE,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RESUME,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.HA_FAILOVER,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RESUME,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.START,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RESUME,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.PAUSE,
                                    'requester': constants.HA,
                                    'res': True},
                                   {'curr': model.VM.RESUME,
                                    'curr_owner': constants.RESTORE,
                                    'new': model.VM.MIGRATE,
                                    'requester': constants.HA,
                                    'res': True}],
         model.EntityType.MANAGED_NODE: [{'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': constants.STORAGE_SYNCING,
                                          'requester': constants.STORAGE,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': constants.NETWORK_SYNCING,
                                          'requester': constants.NETWORK,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.PROVISION,
                                          'requester': constants.CORE,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.IMPORT,
                                          'requester': constants.CORE,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.FENCE,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.UP_FAILOVER,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.DOWN_FAILOVER,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.DOWN,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.FENCE,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.DOWN,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.UP_FAILOVER,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.DOWN,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.DOWN_FAILOVER,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.DOWN_FAILOVER,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP_FAILOVER,
                                          'curr_owner': constants.HA,
                                          'new': model.ManagedNode.DOWN_FAILOVER,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.DOWN_FAILOVER,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.UP_FAILOVER,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.UP_FAILOVER,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.FENCE,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP_FAILOVER,
                                          'curr_owner': constants.HA,
                                          'new': model.ManagedNode.FENCE,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP_FAILOVER,
                                          'curr_owner': constants.HA,
                                          'new': model.ManagedNode.UP_FAILOVER,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.DOWN_FAILOVER,
                                          'curr_owner': constants.HA,
                                          'new': model.ManagedNode.DOWN_FAILOVER,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.FENCE,
                                          'curr_owner': constants.HA,
                                          'new': model.ManagedNode.FENCE,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.FENCE,
                                          'curr_owner': constants.HA,
                                          'new': model.ManagedNode.FENCE,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.FENCE,
                                          'curr_owner': constants.HA,
                                          'new': model.ManagedNode.DOWN_FAILOVER,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.FENCE,
                                          'requester': constants.HA,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.ManagedNode.POWER_OFF,
                                          'requester': constants.DWM,
                                          'res': True}]}
        for key in transition_dict.keys():
            for row in transition_dict[key]:
                st = StateTransition(key, to_unicode(row['curr']), to_unicode(row['new']), row['res'], row['curr_owner'], row['requester'], key)
                model.DBSession.add(st)


        transition_dict = {model.EntityType.MANAGED_NODE: [{'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.START,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.PAUSE,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.MIGRATE,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.MIGRATE,
                                          'requester': constants.DWM,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.START,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.STOP,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.KILL,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.REMOVE,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.REBOOT,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.PAUSE,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.RESUME,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.MIGRATE,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.STOP,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.KILL,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.PAUSE,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.START,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.RESUME,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.STOP,
                                          'requester': constants.RESTORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.KILL,
                                          'requester': constants.RESTORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.DOWN,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.MIGRATE,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.DOWN,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.MIGRATE,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.DOWN_FAILOVER,
                                          'curr_owner': constants.HA,
                                          'new': model.VM.MIGRATE,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP_FAILOVER,
                                          'curr_owner': constants.HA,
                                          'new': model.VM.MIGRATE,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP_FAILOVER,
                                          'curr_owner': constants.HA,
                                          'new': model.VM.START,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.UP_FAILOVER,
                                          'curr_owner': constants.HA,
                                          'new': model.VM.PAUSE,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.FENCE,
                                          'curr_owner': constants.HA,
                                          'new': model.VM.MIGRATE,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.START,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.PAUSE,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.RESUME,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.REBOOT,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.STOP,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.KILL,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.MIGRATE,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.COLLECT,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.REMOVE,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.EDIT,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.HA_FAILOVER,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.START,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.PAUSE,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.MIGRATE,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.START,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.PAUSE,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.RESUME,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.STOP,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.KILL,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.START,
                                          'requester': constants.RESTORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.PAUSE,
                                          'requester': constants.RESTORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.RESUME,
                                          'requester': constants.RESTORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.STOP,
                                          'requester': constants.RESTORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.PROVISION,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.KILL,
                                          'requester': constants.RESTORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.START,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.PAUSE,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.RESUME,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.REBOOT,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.STOP,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.KILL,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.MIGRATE,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.COLLECT,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.REMOVE,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.EDIT,
                                          'requester': constants.CORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.HA_FAILOVER,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.HA_FAILOVER,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.START,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.PAUSE,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.MIGRATE,
                                          'requester': constants.HA,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.START,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.PAUSE,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.RESUME,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.STOP,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.KILL,
                                          'requester': constants.BACKUP,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.START,
                                          'requester': constants.RESTORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.PAUSE,
                                          'requester': constants.RESTORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.RESUME,
                                          'requester': constants.RESTORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.STOP,
                                          'requester': constants.RESTORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True},
                                         {'curr': model.ManagedNode.IMPORT,
                                          'curr_owner': constants.CORE,
                                          'new': model.VM.KILL,
                                          'requester': constants.RESTORE,
                                          'req_ent_type': model.EntityType.DOMAIN,
                                          'res': True}]}
        for key in transition_dict.keys():
            for row in transition_dict[key]:
                st = StateTransition(key, to_unicode(row['curr']), to_unicode(row['new']), row['res'], row['curr_owner'], row['requester'], row['req_ent_type'])
                model.DBSession.add(st)


        model.DBSession.add(st)
    except Exception, e:
        import traceback
        traceback.print_exc()

def populate_quota_catergories(cp_types_dict):
    EC2 = constants.EC2
    CMS = constants.CMS
    EUC = constants.EUC
    OST = constants.OPENSTACK
    ALLCP = [EC2, CMS, EUC, OST]
    EC2CP = [EC2, EUC, OST]
    quota_categories = [constants.QUOTA_INSTANCES, constants.QUOTA_RESOURCES, constants.QUOTA_STORAGE, constants.QUOTA_NETWORK, constants.QUOTA_INSTANCE_TYPE]
    quota_items = [ {'name':constants.QUOTA_INSTANCE_RUN_VMS,'cat':constants.QUOTA_INSTANCES,'cptype':ALLCP,'unit':'','order':10},\
                    {'name':constants.QUOTA_INSTANCE_TOT_VMS,'cat':constants.QUOTA_INSTANCES,'cptype':ALLCP,'unit':'','order':20},\
                    {'name':constants.QUOTA_RESOURCE_MEM,'cat':constants.QUOTA_RESOURCES,'cptype':[CMS],'unit':constants.MB,'order':30},\
                    {'name':constants.QUOTA_RESOURCE_VCPU,'cat':constants.QUOTA_RESOURCES,'cptype':[CMS],'unit':'','order':40},\
                    {'name':constants.QUOTA_STORAGE_SIZE,'cat':constants.QUOTA_STORAGE,'cptype':ALLCP,'unit':constants.GB,'order':50},\
                    {'name':constants.QUOTA_PRIVATE_NETWORK_COUNT,'cat':constants.QUOTA_NETWORK,'cptype':[CMS],'unit':'','order':70},\
                    {'name':constants.QUOTA_NETWORK_IP_COUNT,'cat':constants.QUOTA_NETWORK,'cptype':ALLCP,'unit':'','order':80}\
                  ]
    category_dict = {}
    #i = 1
    # for category in quota_categories:
    #     qc = model.QuotaCategories(category,i)
    #     model.DBSession.add(qc)
    #     category_dict[category] = qc
    #     i += 1
    # for item in quota_items:
    #     qi = model.QuotaItems(item['name'],item['unit'],item['order'])
    #     qi.category = category_dict[item['cat']]
    #     for cp in item['cptype']:
    #         og = cp_types_dict[cp]
    #         qi.cpTypes.append(og)
    #     model.DBSession.add(qi)


def _(name):
    return to_unicode(name)

