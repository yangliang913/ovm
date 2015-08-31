import pylons
import simplejson as json
from stackone.controllers.ControllerBase import ControllerBase
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.ImageService import ImageService
from stackone.viewModel.VMService import VMService
from stackone.viewModel.NodeService import NodeService
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
LOGGER = logging.getLogger('stackone.controllers')
from stackone.model.Authorization import AuthorizationService
from stackone.controllers.TemplateController import TemplateController
from stackone.controllers.XMLRPC.TemplateXMLRPCController import TemplateXMLRPCController
from pylons.controllers.util import forward
from pylons.controllers import XMLRPCController
class TemplateAjaxController(ControllerBase):
    template_controller = TemplateController()
    @expose()
    def xmlrpc(self):
        return forward(TemplateXMLRPCController())
        
    @expose(template='json')
    def get_image_groups(self,store_id=None,_dc=None):
        result = self.template_controller.get_image_groups(store_id)
        return result

    @expose(template='json')
    def get_images(self, group_id):
        result = self.template_controller.get_images(group_id)
        return result

    @expose(template='json')
    def check_image_exists(self,image_name):
        result = None
        result=self.template_controller.check_image_exists(image_name)
        return result
        
    @expose(template='json')
    def get_image_target_nodes(self, image_id):
        result = None
        result=self.template_controller.get_image_target_nodes(image_id=image_id)
        return result
    @expose(template='json')
    def get_target_doms(self):
        result =  self.template_controller.get_target_doms()
        return result 
    @expose(template='json')
    def add_image_group(self, group_name,store_id):
        try:
            result = self.template_controller.add_image_group(group_name,store_id)
        except Exception,ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",''))
            return "{success: false,msg: '" + to_str(ex).replace("'",'') +"'}"
        return "{success: true,msg: 'Success'}"
    @expose()
    def remove_image_group(self, group_id):
        result = self.template_controller.remove_image_group(group_id)
        return result
    @expose()
    def rename_image_group(self, group_id, group_name):
        result = None
        result = self.template_controller.rename_image_group(group_id, group_name)
        return result

    @expose()
    def remove_image(self, image_id, group_id):
        try:
            result = None
            result = self.template_controller.remove_image(image_id, group_id)
        except Exception as ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",''))
            return "{success: false,msg:'"+ to_str(ex).replace("'",'') + "'}"
        return "{success: true,msg: 'Task Submitted'}"

    @expose()
    def rename_image(self, image_id, image_name, group_id):
        result = None
        #image_name=to_str(image_name)
        result = self.template_controller.rename_image(image_id, image_name, group_id)
        return result

    @expose()
    def clone_image(self, image_id, image_name, group_id,group_name):
        try:
            result = None
            result = self.template_controller.clone_image(image_id, image_name, group_id, group_name)
        except Exception, ex:
            print_traceback()
            LOGGER.error(to_str(ex).replace("'",""))
            return "{success: false,msg: '",to_str(ex).replace("'",""),"'}"
        return "{success: true,msg: 'Success'}"

    @expose(template='json')
    def get_image_info(self, node_id, level):
        result = self.template_controller.get_image_info(node_id,level)
        return result

    @expose()
    def save_image_desc(self, image_id, content):
        result = None
        result =self.template_controller.save_image_desc(image_id, content)
        return result

    @expose(template='json')
    def get_image_script(self, image_id):
        result =self.template_controller.get_image_script(image_id)
        return result

    @expose()
    def save_image_script(self, image_id, content):
        result = None
        result = self.template_controller.save_image_script(image_id, content)
        return result

    @expose(template='json')
    def get_imagestore_details(self, imagestore_id, _dc=None):
        result = self.template_controller.get_imagestore_details(imagestore_id)
        return result

    @expose(template='json')
    def scan_image_store(self,imagestore_id):
        result = self.template_controller.scan_image_store(imagestore_id)
        return result

    @expose(template='json')
    def get_imagestore_count(self,imagestore_id):
        result = self.template_controller.get_imagestore_count(imagestore_id)
        return result

    @expose(template='json')
    def get_imagegroup_count(self,imagegroup_id ):
        result = self.template_controller.get_imagegroup_count(imagegroup_id)
        return result

    @expose(template='json')
    def get_imagegroup_details(self,imagegroup_id, _dc=None ):
        print  "get_imagegroup_details", imagegroup_id
        result = self.template_controller.get_imagegroup_details(imagegroup_id)
        return result

    @expose(template='json')
    def get_piechart_data(self,image_id,  _dc=None ):
        result= None
        result = self.template_controller.get_piechart_data(image_id)
        return result

    @expose(template='json')
    def get_boot_info(self,image_id,_dc=None):
        result = self.template_controller.get_boot_info(image_id)
        return result

    @expose(template='json')
    def get_template_grid_info(self,image_id,type,_dc=None):
        result = self.template_controller.get_template_grid_info(image_id,type)
        return result

    @expose(template='json')
    def transfer_image(self,image_id,source_group_id,dest_group_id):
        result = None
        result=self.template_controller.transfer_image(image_id,source_group_id,dest_group_id)
        return result

    @expose(template='json')
    def get_target_images(self, node_id,image_group_id=None,**kw):
        result = None
        result=self.template_controller.get_target_images(node_id,image_group_id,**kw)
        return result

    @expose(template='json')
    def get_target_image_groups(self, node_id,**kw):
        result = None
        result=self.template_controller.get_target_image_groups(node_id,**kw)
        return result

    @expose(template='json')
    def get_image_vm_info(self,image_id, _dc=None):
        result =self.template_controller.get_image_vm_info(image_id)
        return result

    @expose(template='json')
    def get_template_version_info(self,image_id, _dc=None):
        result = self.template_controller.get_template_version_info(image_id)
        return result

    @expose(template='json')
    def get_template_details(self,image_id, _dc=None):
        result = self.template_controller.get_template_details(image_id)
        return result

    @expose(template='json')
    def get_imagestore_summary_info(self,imagestore_id, _dc=None):
        result = self.template_controller.get_imagestore_summary_info(imagestore_id)
        return result

    @expose(template='json')
    def get_imagegrp_summary_info(self,grp_id, _dc=None):
        result = self.template_controller.get_imagegrp_summary_info(grp_id)
        return result
    @expose(template='json')
    def get_vm_status(self,image_id, _dc=None):
        result = self.template_controller.get_vm_status(image_id)
        return result
        

    @expose(template='json')
    def create_image_from_vm(self, node_id, image_name, image_group_id, context):
        result = self.template_controller.create_image_from_vm(node_id, image_name, image_group_id, context)
        return result


    #from vm to image 
    @expose(template='json')
    def get_all_image_groups(self, imagestore_id, _dc=None):
        result = self.template_controller.get_all_image_groups(imagestore_id)
        return result
    #sam 1025
    @expose(template='json')
    def get_all_images(self, group_id, _dc=None):
        result = self.template_controller.get_all_images(group_id)
        return result

