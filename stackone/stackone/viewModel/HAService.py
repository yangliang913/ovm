import stat
import time
import os
from stackone.core.utils import utils
from stackone.core.utils.utils import *
from stackone.core.utils.utils import constants, is_host_remote
from stackone.core.utils.utils import populate_node_filter, dynamic_map
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
from stackone.model.Groups import ServerGroup
from stackone.viewModel.NodeInfoVO import NodeInfoVO
from stackone.core.utils.NodeProxy import Node
from stackone.viewModel.ResponseInfo import ResponseInfo
from stackone.core.utils.phelper import AuthenticationException
import Basic
import simplejson as json
from stackone.model.VM import vifEntry
from stackone.model.VM import ImageDiskEntry
from stackone.model.VM import VM
from stackone.model.ManagedNode import ManagedNode
from stackone.core.ha.ha_register import HARegister
from stackone.core.ha.ha_fence import *
from stackone.model import DBSession
from stackone.model.Entity import Entity, EntityAttribute, EntityRelation
import logging
from sqlalchemy.orm import eagerload
LOGGER = logging.getLogger('stackone.viewModel')
import traceback
from stackone.model.LicenseManager import  check_platform_expire_date
class HAService():
    #PASSED
    def __init__(self):
        self.manager = Basic.getGridManager()

    #PASSED
    def get_ha_details(self, node_type, node_id):
        result = {}
        try:
            if node_type == constants.DATA_CENTER:
                pass
            elif node_type == constants.SERVER_POOL:
                ha_reg = DBSession.query(HARegister).filter(HARegister.entity_id == node_id).all()
                registered = False
                if len(ha_reg) > 0:
                    registered = ha_reg[0].registered
                result['enable_ha'] = registered
                sg = DBSession.query(ServerGroup).filter(ServerGroup.id == node_id).one()
                result['migrate_back'] = sg.migrate_back
                result['use_standby'] = sg.use_standby
                result['failover'] = sg.failover
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            raise ex
        return result

    #PASSED
    def process_ha(self, auth, node_id, node_type, ha_data):
        try:
            ha_data = json.loads(ha_data)
            if node_type == constants.SERVER_POOL:
                self.process_ha_sp(auth, node_id, node_type, ha_data)
        except Exception as ex:
            print_traceback()
            err = to_str(ex).replace("'", ' ')
            LOGGER.error(err)
            raise ex


    #PASSED
    def process_ha_sp(self, auth, node_id, node_type, ha_data):
        general = ha_data.get('general_object')
        pre_serve_list = general.get('preferred_servers_list')
        grp_ent = auth.get_entity(node_id)
        if grp_ent is None:
            return None
        grp_ent.set_ha(general.get('enable_ha'))
        mnids = []
        standby_servers = []
        for server in pre_serve_list:
            mnids.append(server.get('server_id'))
            if server.get('is_standby'):
                standby_servers.append(server.get('server_id'))

        sg = DBSession.query(ServerGroup).filter(ServerGroup.id == node_id).one()
        sg.migrate_back = general.get('migrate_back')
        sg.use_standby = general.get('use_standby')
        sg.failover = general.get('failover')
        DBSession.add(sg)
        mnodes = DBSession.query(ManagedNode).filter(ManagedNode.id.in_(mnids)).all()
        for mnode in mnodes:
            if mnode.id in standby_servers:
                mnode.set_standby(True)
            else:
                mnode.set_standby(False)
            DBSession.add(mnode)
            
        vm_priority = ha_data.get('vm_priority_object')
        vm_priority_list = vm_priority.get('vm_priority_list')
        vmids = []
        for val in vm_priority_list:
            vmids.append(val.get('vm_id'))
        
        vms = DBSession.query(VM).filter(VM.id.in_(vmids)).all()
        ha_priorities = constants.HA_PRIORITIES
        for vm in vms:
            for val in vm_priority_list:
                if vm.id == val.get('vm_id'):
                    vm.ha_priority = ha_priorities.get(val.get('ha_priority'))
                    DBSession.add(vm)
                    break
        fence_object = ha_data.get('fence_object')
        fencing_det = fence_object.get('fence_details')
        servers = []
        for val in fencing_det:
            servers.append(val.get('server_id'))
        
        ha_entity_res = DBSession.query(HAEntityResource).filter(HAEntityResource.entity_id.in_(servers)).all()
        if len(ha_entity_res) != 0:
            for ha_entity_r in ha_entity_res:
                DBSession.delete(ha_entity_r)
        try:
            for fen in fencing_det:
                entity_id = fen.get('server_id')
                for key in fen.get('fencing_data'):
                    resource_id = key.get('id')
                    order = 1
                    haer = HAEntityResource(entity_id, resource_id, order)
                    param_list = key.get('params')
                    for param in param_list:
                        name = param.get('attribute')
                        value = param.get('value')
                        type = param.get('type')
                        field = param.get('field')
                        field_datatype = param.get('field_datatype')
                        sequence = param.get('sequence')
                        is_environ = eval(param.get('is_environ'))
                        haerp = HAEntityResourceParam(name, value, type, field, field_datatype, sequence, is_environ)
                        haer.params.append(haerp)
                    DBSession.add(haer)
        except Exception as e:
            traceback.extract_stack()
            #print e
            
        adv_object = ha_data.get('advance_object')
        entity = DBSession.query(Entity).filter(Entity.entity_id == node_id).one()
        attributes = []
        for ea in entity.attributes:
            attributes.append(ea)
            
        for i in range(len(attributes)):
            entity.attributes.remove(attributes[i])
            
        for name in adv_object:
            value = adv_object[name]
            ea = EntityAttribute(name, value)
            entity.attributes.append(ea)
            
        DBSession.add(entity)
        

    #PASSED
    def get_advanced_params(self, auth, node_id):
        result = []
        try:
            adv_opt_info = constants.ADV_OPTIONS_INFO
            entity = auth.get_entity(node_id)
            entity_attributes = entity.attributes
            if len(entity_attributes) > 0:
                for ea in entity_attributes:
                    info = adv_opt_info.get(ea.name, '').replace(' ', '%20')
                    info = '<center><img width=16 height=16 src=../icons/information.png onClick=show_desc("' + info + '") /></center>'
                    result.append(dict(attribute=ea.name, value=ea.value, information=info))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return dict(success=False, msg=to_str(ex))

        return dict(success=True, adv_params=result)


    #PASSED
    def get_dc_fence_resources(self):
        result = []
        try:
            ha_fenr = DBSession.query(HAFenceResource).all()
            if len(ha_fenr) > 0:
                for ha in ha_fenr:
                    fenc_param = []
                    for params in ha.params:
                        fenc_param.append(dict(id=to_str(params.id), attribute=to_str(params.name), value=to_str(params.value), type=to_str(params.type), field=to_str(params.field), field_datatype=to_str(params.field_datatype), sequence=int(params.sequence)))
                        
                    result.append(dict(id=ha.id, fencing_name=ha.name, fencing_type=ha.type.display_name, fencing_clasn=ha.type.classification, fencing_params=to_str(fenc_param)))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', fencing_details=result)


    #PASSED
    def ha_fence_resource_types(self, category, _dc=None):
        result = []
        try:
            ha_res_types = DBSession.query(HAFenceResourceType).filter(HAFenceResourceType.classification == category).all()
            for ha_res_type in ha_res_types:
                result.append(dict(id=ha_res_type.id, value=ha_res_type.display_name, name=ha_res_type.name, description=ha_res_type.description))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', fence_resources=result)


    #PASSED
    def ha_fence_resource_types_classification(self):
        result = []
        try:
            ha_res_types = DBSession.query(HAFenceResourceType.classification.distinct()).all()
            for ha_res_type in ha_res_types:
                result.append(dict(classification=ha_res_type[0]))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', fence_resources=result)


    #PASSED
    def ha_fence_resource_type_meta(self, fence_id):
        ha_res_type = DBSession.query(HAFenceResourceType).filter(HAFenceResourceType.id == fence_id).first()
        result = []
        try:
            for hrm in ha_res_type.meta:
                if hrm.is_resource == True:
                    result.append(dict(id=hrm.id, attribute=hrm.display_name, value='', field=hrm.field, type=hrm.field_type, field_datatype=hrm.field_datatype, sequence=int(hrm.sequence), values=hrm.field_values))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', rows=result)


    #PASSED
    def save_dc_params(self, fencing_name, fencing_id, params):
        try:
            params = json.loads(params).get('param_obj')
            har = HAFenceResource(fencing_name, fencing_id)
            for param in params:
                name = param.get('attribute')
                value = param.get('value')
                type = param.get('type')
                field = param.get('field')
                field_datatype = param.get('field_datatype')
                sequence = param.get('sequence')
                harp = HAFenceResourceParam(name, value, type, field, field_datatype, sequence)
                har.params.append(harp)
                
            DBSession.add(har)

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success=True)


    #PASSED
    def update_dc_params(self, res_id, fencing_name, fencing_id, params):
        try:
            params = json.loads(params).get('param_obj')
            hafr = DBSession.query(HAFenceResource).filter(HAFenceResource.id == res_id).one()
            hafr.name = fencing_name
            params_list = []
            for hp in hafr.params:
                params_list.append(hp)
            for i in range(len(params_list)):
                hafr.params.remove(params_list[i])
            for param in params:
                name = param.get('attribute')
                value = param.get('value')
                type = param.get('type')
                field = param.get('field')
                field_datatype = param.get('field_datatype')
                sequence = param.get('sequence')
                harp = HAFenceResourceParam(name, value, type, field, field_datatype, sequence)
                hafr.params.append(harp)
                
            DBSession.add(hafr)

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success=True)


    #PASSED
    def remove_fencing_device(self, res_id):
        try:
            hafr = DBSession.query(HAFenceResource).filter(HAFenceResource.id == res_id).one()
            if len(hafr.entity_resources) == 0:
                DBSession.delete(hafr)
            else:
                return ("{success: false,msg: '", 'This fencing device is used by some of the servers', "'}")

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success=True)


    #PASSED
    def get_sp_fencing_devices(self):
        result = []
        try:
            hafrs = DBSession.query(HAFenceResource).all()
            for hafr in hafrs:
                result.append(dict(id=hafr.id, value=hafr.name, fence_id=hafr.fence_id, device_type=hafr.type.display_name, description=hafr.type.description))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return {'success': False, 'msg': to_str(ex).replace("'", '')}

        return dict(success=True, fencing_devices=result)


    #PASSED
    def get_sp_fencingdevice_params(self, fence_id):
        result = []
        try:
            ha_res_type = DBSession.query(HAFenceResourceType).filter(HAFenceResourceType.id == fence_id).first()
            for hatm in ha_res_type.meta:
                if hatm.is_instance == True or hatm.is_environ == True:
                    result.append(dict(attribute=hatm.display_name, value='', type=hatm.field_type, field_datatype=hatm.field_datatype, field=hatm.field, is_environ=to_str(hatm.is_environ), sequence=int(hatm.sequence), values=hatm.field_values))
        
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', rows=result)
        
    
    #PASSED
    def get_sp_fencing_data(self, auth, node_id, node_type):
        info_list = []
        
        if node_type == constants.MANAGED_NODE:
            total_list = self.get_ha_fence_resources(node_id)
            node = auth.get_entity(node_id)
            info_list.append(dict(id=node_id, server=node.name, fence_details=total_list))
        elif node_type == constants.SERVER_POOL:
            node_list = self.manager.getNodeList(auth, node_id)
            for node in node_list:
                total_list = self.get_ha_fence_resources(node.id)
                fd_count = len(total_list)
                if fd_count == 1:
                    fd_count = total_list[0].get('name')
                info_list.append(dict(id=node.id, server=node.hostname, fencing_devices=fd_count, fence_details=to_str(total_list)))
            
        return info_list


    #PASSED
    def get_vm_priority(self):
        result = []
        try:
            ha_priorities = constants.HA_PRIORITIES
            for key in ha_priorities.keys():
                result.append(dict(id=ha_priorities[key], value=key))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return dict(success=False, msg=to_str(ex).replace("'", ''))

        return dict(success=True, vm_priority=result)


    #PASSED
    def ha_vm_priority(self, auth, node_id):
        infolist = {}
        dom = self.manager.get_dom(auth, node_id)
        ha_priorities = constants.HA_PRIORITIES
        ha_priority = None
        for vp in ha_priorities:
            if ha_priorities[vp] == dom.ha_priority:
                ha_priority = vp
                break

        infolist['Vmname'] = dom.name
        infolist['Priority'] = ha_priority
        return infolist


    #PASSED
    def get_preferred_servers(self, auth, grp_id):
        result = []
        try:
            node_list = self.manager.getNodeList(auth, grp_id)
            for node in node_list:
                result.append(dict(id=node.id, value=node.hostname))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return dict(success=False, msg=to_str(ex))

        return dict(success=True, prefer_servers=result)


    #PASSED
    def get_cluster_adapters(self):
        result = []
        try:
            dic = {'None': '', 'RHEL cluster suite': 'rhel', 'SUSE/SLES OpenAIS suite': 'suse'}
            for key in dic.keys():
                result.append(dict(id=dic[key], value=key))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', clusters=result)


    #PASSED
    def get_servers(self, auth, node_id):
        result = []
        try:
            group = self.manager.getGroup(auth, node_id)
            node_list = self.manager.getNodeList(auth, group.id)
            for mnode in node_list:
                result.append(dict(node_id=mnode.id, name=mnode.hostname, platform=get_platform_name(mnode.type), cpu=mnode.get_cpu_info().get(constants.key_cpu_count, 0), memory=mnode.get_memory_info().get(constants.key_memory_total, 0), is_standby=mnode.is_standby()))

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return ("{success: false,msg: '", to_str(ex).replace("'", ''), "'}")

        return dict(success='true', servers=result)


    #PASSED
    def get_servers_cli(self, auth, node_id):
        try:
            result = []
            fail = []
            group = self.manager.getGroup(auth, node_id)
            node_list = self.manager.getNodeList(auth, group.id)
            for mnode in node_list:
                if mnode.is_standby() == True:
                    result.append(mnode.hostname)
                else:
                    fail.append(mnode.hostname)

        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return dict(success=False, msg=to_str(ex))

        return dict(success=True, servers=result)

    
    #PASSED
    def enable_ha_cli(self, auth, group_id, enable):
        try:
            group = auth.get_entity(group_id)
            if enable == 'True':
                group.set_ha(True)
            else:
                group.set_ha()
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return dict(success=False, msg=to_str(ex))
        
        return dict(success=True, result='success')


    #PASSED
    def get_ha_fence_resources(self, node_id):
        try:
            hafrs = DBSession.query(HAEntityResource).filter(HAEntityResource.entity_id == node_id).all()
            total_list = []
            for hasfr in hafrs:
                list = []
                for hp in hasfr.params:
                    list.append(dict(attribute=to_str(hp.name), value=to_str(hp.value), type=to_str(hp.type), field=to_str(hp.field), field_datatype=to_str(hp.field_datatype), is_environ=to_str(hp.is_environ), sequence=int(hp.sequence)))
                
                total_list.append(dict(id=to_str(hasfr.resource_id), name=to_str(hasfr.resource.name), params=list, device_type=to_str(hasfr.resource.type.display_name)))
            
            return total_list

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex))
        return dict(success = True,result = 'success')

    #PASSED
    def save_fencing_details_fordwm(self, node_id, fence_det):
        #from stackone.model.LicenseManager import  check_platform_expire_date
        try:
            managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == node_id).first()
            ret,msg = check_platform_expire_date(managed_node.get_platform())
            if ret == False:
                raise Exception(msg)
            
            fence_det = json.loads(fence_det)
            fence_details = fence_det.get('fence_details')
            entity_id = node_id
            fence_details = eval(fence_details)
            hare_det = DBSession.query(HAEntityResource).filter(HAEntityResource.entity_id == entity_id).all()
            resids = [hare.id for hare in hare_det]
            for fen in fence_details:
                resource_id = fen.get('id')
                order = 1
                haer = HAEntityResource(entity_id, resource_id, order)
                param_list = fen.get('params')
                for param in param_list:
                    name = param.get('attribute')
                    value = param.get('value')
                    type1 = param.get('type')
                    field = param.get('field')
                    field_datatype = param.get('field_datatype')
                    sequence = param.get('sequence')
                    is_environ = eval(param.get('is_environ'))
                    haerp = HAEntityResourceParam(name, value, type1, field, field_datatype, sequence, is_environ)
                    haer.params.append(haerp)
                    
                DBSession.add(haer)
            
            DBSession.query(HAEntityResource).filter(HAEntityResource.id.in_(resids)).delete()
            DBSession.query(HAEntityResourceParam).filter(HAEntityResourceParam.entity_resource_id.in_(resids)).delete()

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex))

        return dict(success=True, result='success')




