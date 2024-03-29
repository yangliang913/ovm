import pylons
import simplejson as json
from stackone.lib.base import BaseController
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.ImageService import ImageService
from stackone.viewModel.VMService import VMService
from stackone.viewModel.NodeService import NodeService
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
LOGGER = logging.getLogger('stackone.controllers')
from stackone.controllers.ControllerBase import ControllerBase
class TemplateController(ControllerBase):
    image_service = ImageService()
    vm_service = VMService()
    tc = TaskCreator()
    
    def get_image_groups(self, store_id=None, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_image_groups(session['auth'], store_id)
            result = json.dumps(dict(success=True, nodes=result))
            return result

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def get_images(self, group_id):
        try:
            self.authenticate()
            result = self.image_service.get_images(session['auth'], group_id)
            result = json.dumps(dict(success=True, nodes=result))
            return result

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def check_image_exists(self, image_name):
        result = None
        self.authenticate()
        result = self.image_service.check_image_exists(session['auth'], image_name)
        return result

    def get_image_target_nodes(self, image_id):
        result = None
        self.authenticate()
        
        try:
            result = NodeService().get_target_nodes(session['auth'], image_id=image_id)
        except Exception as ex:
            print_traceback()
            return dict(success='false', msg=to_str(ex).replace("'", ''))

        return dict(success='true', nodes=result)

    def get_target_doms(self):
        result = None
        self.authenticate()

        try:
            result = NodeService().get_target_doms(session['auth'])
        except Exception as ex:
            print_traceback()
            return dict(success='false', msg=to_str(ex).replace("'", ''))
        return dict(success='true', nodes=result)

    def add_image_group(self, group_name, store_id, csep_context=None):
        result = None
        self.authenticate()
        result = self.image_service.add_image_group(session['auth'], group_name, store_id, csep_context)
        return result

    def remove_image_group(self, group_id):
        try:
            self.authenticate()
            result = self.image_service.remove_image_group(session['auth'], group_id)
            return result
        except Exception as ex:
            print_traceback()
            raise ex
#    def remove_image(self, image_id, group_id):
#        self.authenticate()
#        return self.image_service.remove_image(session['auth'],image_id,group_id)
    def rename_image_group(self, group_id, group_name):
        result = None
        self.authenticate()
        result = self.image_service.rename_image_group(session['auth'], group_id, group_name)
        return result

    def rename_image(self, image_id, image_name, group_id):
        result = None
        self.authenticate()
        result = self.image_service.rename_image(session['auth'], image_id, image_name, group_id)
        return result
    #sam 1026
    def clone_image(self, image_id, image_name, group_id, group_name):
        try:
            self.authenticate()
            result = self.tc.clone_template_task(session['auth'],image_id,image_name,group_id)
            #return image_id
        except Exception as ex:
            print_traceback()
            raise ex

    def get_image_info(self, node_id, level):
        try:
            self.authenticate()
            if level == constants.IMAGE:
                result = self.image_service.get_image_info(session['auth'], node_id)
            else:
                if level == constants.IMAGE_GROUP:
                    result = self.image_service.get_image_group_info(session['auth'], node_id)
                else:
                    if level == constants.IMAGE_STORE:
                        result = self.image_service.get_image_store_info(session['auth'], node_id)
            result = json.dumps(dict(success=True, content=result))
            return result
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))


    def save_image_desc(self, image_id, content):
        result = None
        self.authenticate()
        result = self.image_service.save_image_desc(session['auth'], image_id, content)
        return result

    def get_image_script(self, image_id):
        try:
            self.authenticate()
            result = self.image_service.get_image_script(session['auth'], image_id)
            result = json.dumps(dict(success=True, content=result))
            return result
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))

    def save_image_script(self, image_id, content):
        result = None
        self.authenticate()
        result = self.image_service.save_image_script(session['auth'], image_id, content)
        return result

    def get_imagestore_details(self, imagestore_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_imagestore_details(session['auth'], imagestore_id)
            result = json.dumps(dict(success=True, content=result))
            return result
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))

    def scan_image_store(self, imagestore_id):
        try:
            self.authenticate()
            new_imgs, rej_imgs = self.image_service.scan_imagestore_details(session['auth'], imagestore_id)
            return dict(success=True, new_imgs=new_imgs, rej_imgs=rej_imgs)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))

    def get_imagestore_count(self, imagestore_id):
        try:
            result = self.image_service.get_imagestore_count(session['auth'], imagestore_id)
            result = json.dumps(dict(success=True, count=result))
            return result
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))

    def get_imagegroup_count(self, imagegroup_id):
        try:
            result = self.image_service.get_imagegroup_count(session['auth'], imagegroup_id)
            result = json.dumps(dict(success=True, info=result))
            return result
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))

    def get_imagegroup_details(self, imagegroup_id, _dc=None):
        try:
            print "get_imagegroup_details",imagegroup_id
            result = self.image_service.get_imagegroup_details(session['auth'], imagegroup_id)
            print result
            result = json.dumps(dict(success=True, info=result))
            return result
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))

    def get_piechart_data(self, image_id, _dc=None):
        try:
            result = []
            result = self.image_service.get_piechart_data(image_id)
            returnresult = json.dumps(dict(success=True, Records=result, RecordCount='2'))
            return returnresult
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))

    def get_boot_info(self, image_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_boot_info(image_id)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        return dict(success=True, rows=result)

    def get_template_grid_info(self, image_id, type, _dc=None):
        try:
            self.authenticate()
            result = self.vm_service.get_template_grid_info(session['auth'], image_id, type)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        return dict(success=True, rows=result)

    def transfer_image(self, image_id, source_group_id, dest_group_id):
        result = None
        self.authenticate()
        result = self.image_service.transfer_image(session['auth'], image_id, source_group_id, dest_group_id)
        return result

    def get_target_images(self, node_id, image_group_id=None, **result):
        result = None
        self.authenticate()
        result = self.image_service.get_target_images(session['auth'], node_id, image_group_id)
        return result

    def get_target_image_groups(self, node_id, **result):
        result = None
        self.authenticate()
        result = self.image_service.get_target_image_groups(session['auth'], node_id)
        return result

    def get_image_vm_info(self, image_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_image_vm_info(image_id)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        return dict(success=True, rows=result)

    def get_template_version_info(self, image_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_template_version_info(session['auth'], image_id)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        return dict(success=True, rows=result)

    def get_template_details(self, image_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_template_details(image_id)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))

        return dict(success=True, rows=result)

    def get_imagestore_summary_info(self, imagestore_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_imagestore_summary_info(session['auth'], imagestore_id)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        return dict(success=True, rows=result)

    def get_imagegrp_summary_info(self, grp_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_imagegrp_summary_info(session['auth'], grp_id)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        return dict(success=True, row=result)

    def get_vm_status(self, image_id, _dc=None):
        try:
            self.authenticate()
            result = self.image_service.get_vm_status(image_id)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))

        return dict(success=True, rows=result)

    def get_groups(self, store_id=None):
        try:
            self.authenticate()
            image_groups = self.image_service.get_groups(session['auth'], store_id)
            return image_groups
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))

    def create_template_context_relation(self, image_ids, context):
        result = None
        self.authenticate()
        result = self.image_service.add_image_group(session['auth'], image_ids, context)
        return result
        
    #from vm to image 
    def create_image_from_vm(self, node_id, image_name, image_group_id, context):
        try:
            self.authenticate()
            if self.image_service.is_image_exist(session['auth'], image_name):
                return dict(success=False, msg='Template %s already exists.' % image_name)
            
            result = self.tc.create_image_from_vm_task(session['auth'], node_id, image_name, image_group_id, context)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        
        return dict(success=True, rows=result, msg='Task submitted')
        
    #from vm to image sam 1026
    def remove_image(self, image_id, group_id):
        try:
            self.authenticate()
            result = self.tc.delete_image_task(session['auth'],image_id,group_id,)
        except Exception as ex:
            print_traceback()
            raise ex
        
    #from vm to image    
    def get_all_image_groups(self, imagestore_id):
        try:
            self.authenticate()
            result = self.image_service.get_all_image_groups(session['auth'], imagestore_id)
        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ' '))
        
        return dict(success=True, rows=result)
    def get_all_images(self, group_id):
        try:
            self.authenticate()
            result=self.image_service.get_all_images(session['auth'],group_id)
        except Exception as ex:
            print_traceback()
            return dict(success=False,msg=to_str(ex).replace("'", ' '))
        



