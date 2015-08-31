from stackone.model import *
import stackone.core.utils.constants
constants = stackone.core.utils.constants
#from stackone.cloud.viewModel.CMSVMCloudService import CMSVMCloudService
#from stackone.cloud.viewModel.CMSTemplateCloudService import CMSTemplateCloudService
#from stackone.cloud.viewModel.CSEPService import CSEPService
#from stackone.cloud.core.model.CSEPManager import CSEPManager
from stackone.controllers.XMLRPC.stackoneXMLRPC import stackoneXMLRPC
from stackone.core.utils.utils import to_unicode, to_str, convert_to_CMS_TZ, print_traceback
from tg import session
import traceback
import logging
LOGGER = logging.getLogger('stackone.controllers.XMLRPC')
class CMSCloudXMLRPC(stackoneXMLRPC):
    cms_cloud_service = CMSVMCloudService()
    csep_service = CSEPService()
    csep_manager = CSEPManager()
    cms_template_service = CMSTemplateCloudService()
    def server_pool_provision(self, region_name, zone_name, image_id, vmname, memory, cpu, storage, csep_context, network, csep_id):
        return self.cms_cloud_service.server_pool_provision(session['auth'], session.get('servicepoint_id'), region_name, zone_name, image_id, vmname, memory, cpu, storage, csep_context, network, csep_id)

    def vm_action(self, vm_id, operation):
        return self.cms_cloud_service.vm_action(vm_id, operation)

    def remove_vm(self, vm_id):
        return self.cms_cloud_service.remove_vm(vm_id)

    def edit_vm(self):
        self.cms_cloud_service.edit_vm()

    def get_state(self, vm_id):
        return self.cms_cloud_service.get_state(vm_id)

    def get_vnc_details(self, vm_id, address):
        return self.cms_cloud_service.get_vnc_details(session['auth'], vm_id, address)

    def add_template_group(self, tmpgrp_name, csep_context=None):
        try:
            id = self.cms_template_service.add_template_group(tmpgrp_name, csep_context)
            return id
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def create_new_AMI(self, vdc_id, account_id, template_name, region_id, image_id, group_id):
        try:
            return self.cms_template_service.create_new_AMI(vdc_id, account_id, template_name, region_id, image_id, group_id)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def remove_template_group(self, groupid):
        try:
            self.cms_template_service.remove_template_group(groupid)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def getVmDetails(self, vmid):
        try:
            return self.cms_cloud_service.getVmDetails(vmid)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def get_all_regions(self):
        try:
            return self.csep_service.get_all_regions_db(session.get('servicepoint_id'))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def get_all_instance_categories(self):
        try:
            return self.csep_service.get_all_instance_categories_db(session.get('servicepoint_id'))
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def get_all_zones(self, region_id):
        try:
            return self.csep_service.get_all_zones_db(region_id)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def get_all_server_pools(self, zone_id):
        try:
            return self.csep_service.get_all_server_pools_db(zone_id)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def get_all_storage(self, server_pool_id):
        try:
            return self.csep_service.get_all_storage_db(server_pool_id)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def get_all_templates(self, region_id):
        try:
            return self.csep_service.get_all_templates_db(region_id)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def get_all_template_groups(self, region_id):
        try:
            return self.csep_service.get_all_template_groups_db(region_id)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def get_all_instance_types(self, category_id):
        try:
            return self.csep_service.get_all_instance_types_db(category_id)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def create_volume(self, name, size, zone, snapshot, vdc_name):
        try:
            csep_id = session.get('servicepoint_id')
            return self.csep_service.create_volume(name, size, zone, snapshot, csep_id, vdc_name)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def delete_volume(self, name, storage_id):
        try:
            return self.csep_service.delete_volume(name, storage_id)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def attach_volume(self, context, disk_list):
        try:
            self.csep_service.attach_volume(context, disk_list)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def detach_volume(self, context, disk_list):
        try:
            self.csep_service.detach_volume(context, disk_list)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def delete_storage_vdc_folders(self, vdc_name):
        try:
            self.csep_service.delete_storage_vdc_folders(vdc_name)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def create_network(self, acc_id, region_id, vdc_id, cp_id, nw_name, nw_desc, nw_address_space, nw_dhcp_range, nw_nat_fwding, csep_name, vlan_pool_id=None):
        try:
            nw_id = self.csep_service.create_network(acc_id, region_id, vdc_id, cp_id, nw_name, nw_desc, nw_address_space, nw_dhcp_range, nw_nat_fwding, csep_name, vlan_pool_id)
            return nw_id
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def remove_network(self, nw_def_id, csep_name, cp_id):
        try:
            result = self.csep_service.remove_network(nw_def_id, csep_name, cp_id)
            return result
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def edit_network(self, nw_def_id, nw_name, desc, csep_name):
        try:
            result = self.csep_service.edit_network(nw_def_id, nw_name, desc, csep_name)
            return result
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def create_template_context_relation(self, image_ids, context):
        try:
            result = self.cms_template_service.create_template_context_relation(session['auth'], image_ids, context)
            return result
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def delete_template_context_relation(self, image_ids=None, context=None):
        try:
            result = self.cms_template_service.delete_template_context_relation(session['auth'], image_ids, context)
            return result
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            raise ex

    def remove_csep_context(self, context):
        try:
            result = self.csep_service.remove_csep_context(session['auth'],context)
            return {'success':True,'result':result,'msg':'','error_msg':''}
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex))
            return {'success':False,'result':None,'msg':'','error_msg':to_str(ex)}
    def get_vnc_info_for_cloudcmsvm(self, node_id, dom_instance_id, address):
        try:
            result = self.cms_cloud_service.get_vnc_info_for_cloudcmsvm(session['auth'], node_id, dom_instance_id, address)
            return result
        except Exception as ex:
            print_traceback()


