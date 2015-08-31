from stackone.controllers.TemplateController import TemplateController
from stackone.model import *
from stackone.model.Authorization import AuthorizationService
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from tg import session
from stackone.controllers.XMLRPC.stackoneXMLRPC import stackoneXMLRPC
import logging
LOGGER = logging.getLogger('stackone.controllers.XMLRPC')
class TemplateXMLRPCController(stackoneXMLRPC):
    template_controller = TemplateController()
    def get_template_groups(self, store_id=None, _dc=None):
        result = self.template_controller.get_image_groups(store_id)
        result = json.dumps(dict(success=True, nodes=result))
        return result

    def get_templates(self, group_id):
        result = self.template_controller.get_images(group_id)
        result = json.dumps(dict(success=True, nodes=result))
        return result

    def check_template_exists(self, template_name):
        result = None
        result = self.template_controller.check_image_exists(image_name)
        return result

    def get_template_target_nodes(self, template_id):
        result = None
        result = self.template_controller.get_target_nodes(image_id=template_id)
        return result

    def add_template_group(self, group_name, store_id):
        try:
            result = None
            result=self.template_controller.add_image_group(group_name,store_id)
        except Exception ,ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return "{success: false,msg: '"+to_str(ex).replace("'", '')+"'}"
        return "{success: true,msg: 'Success'}"
    def remove_template_group(self, group_id):
        result = None
        result = self.template_controller.remove_image_group(group_id)
        return result

    def rename_template_group(self, group_id, group_name):
        result = None
        result = self.template_controller.rename_image_group(group_id, group_name)
        return result

    def remove_template(self, template_id, group_id):
        result = None
        result = self.template_controller.remove_image(template_id, group_id)
        return result

    def rename_template(self, template_id, template_name, group_id):
        result = None
        result = self.template_controller.rename_image(template_id, template_name, group_id)
        return result

    def clone_template(self, template_id, template_name, group_id, group_name):
        try:
            result = None
            result=self.template_controller.clone_image(template_id,template_name,group_id,group_name)
        except Exception ,ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'", ''))
            return "{success: false,msg: '"+to_str(ex).replace("'", '')+"'}"
        return "{success: true,msg: 'Success'}"
        
    def get_template_info(self, node_id, level):
        result = self.template_controller.get_image_info(node_id, level)
        result = json.dumps(dict(success=True, content=result))
        return result

    def save_template_desc(self, template_id, content):
        result = None
        result = self.template_controller.save_image_desc(template_id, content)
        return result

    def get_template_script(self, template_id):
        result = self.template_controller.get_image_script(template_id)
        result = json.dumps(dict(success=True, content=result))
        return result

    def save_template_script(self, template_id, content):
        result = None
        result = self.template_controller.save_image_script(template_id, content)
        return result

    def get_template_store_details(self, imagestore_id, _dc=None):
        result = self.template_controller.get_imagestore_details(imagestore_id)
        result = json.dumps(dict(success=True, content=result))
        return result

    def scan_template_store(self, imagestore_id):
        result = self.template_controller.scan_image_store(imagestore_id)
        return result

    def get_templatestore_count(self, templatestore_id):
        result = self.template_controller.get_imagestore_count(templatestore_id)
        result = json.dumps(dict(success=True, count=result))
        return result

    def get_templategroup_count(self, imagegroup_id):
        result = self.template_controller.get_templategroup_count(imagegroup_id)
        result = json.dumps(dict(success=True, info=result))
        return result

    def get_templategroup_details(self, templategroup_id, _dc=None):
        result = self.template_controller.get_imagegroup_details(templategroup_id)
        print result

    def get_piechart_data(self, template_id, _dc=None):
        result = None
        result = self.template_controller.get_piechart_data(template_id)
        return result

    def get_boot_info(self, template_id, _dc=None):
        result = self.template_controller.get_boot_info(template_id)
        return result

    def get_template_grid_info(self, template_id, type, _dc=None):
        result = self.template_controller.get_template_grid_info(template_id, type)
        return result

    def transfer_template(self, template_id, source_group_id, dest_group_id):
        result = None
        result = self.template_controller.transfer_image(template_id, source_group_id, dest_group_id)
        return result

    def get_target_templates(self, node_id, template_group_id=None, **result):
        result = None
        result = self.template_controller.get_target_images(node_id, template_group_id)
        return result

    def get_target_template_groups(self, node_id, **result):
        result = None
        result = self.template_controller.get_target_template_groups(node_id)
        return result

    def get_template_vm_info(self, template_id, _dc=None):
        result = self.template_controller.get_image_vm_info(template_id)
        return result

    def get_template_version_info(self, template_id, _dc=None):
        result = self.template_controller.get_template_version_info(template_id)
        return result

    def get_template_details(self, template_id, _dc=None):
        result = self.template_controller.get_template_details(template_id)
        return result

    def get_templatestore_summary_info(self, templatestore_id, _dc=None):
        result = self.template_controller.get_imagestore_summary_info(templatestore_id)
        return result

    def get_templategrp_summary_info(self, grp_id, _dc=None):
        result = self.template_controller.get_imagegrp_summary_info(grp_id)
        return result

    def get_vm_status(self, template_id, _dc=None):
        result = self.template_controller.get_vm_status(template_id)
        return result

    def get_groups(self, store_id=None):
        image_groups = self.template_controller.get_groups(store_id)
        return image_groups



