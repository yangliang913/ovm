import pylons
import simplejson as json
from stackone.controllers.ControllerBase import ControllerBase
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.NodeService import NodeService
from stackone.viewModel.VMService import VMService
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
from stackone.model.Authorization import AuthorizationService
from pylons.controllers.util import forward
from pylons.controllers import XMLRPCController
LOGGER = logging.getLogger('stackone.controllers')
from stackone.controllers.DWMController import DWMController
class DWMAjaxController(ControllerBase):
    __doc__ = '\n\n    '
    dwm_controller = DWMController()
    @expose(template='json')
    def save_dwm_details(self,group_id,policy_object,enabled,offset):
        result=self.dwm_controller.save_dwm_details(group_id,policy_object,enabled,offset)
        return result
    @expose(template='json')
    def get_dwm_details(self,group_id):
        result=self.dwm_controller.get_dwm_details(group_id)
        return result
    @expose(template='json')
    def get_dwm_schedule_details(self):
        result=self.dwm_controller.get_dwm_schedule_details(group_id,policy_id)
        return result
    @expose(template='json')
    def get_policy_forall(self):
        result=self.dwm_controller.get_policy_forall()
        return result
    @expose(template='json')
    def store_dwm_policy_schedule(self,group_id,schedule):
        result=self.dwm_controller.store_dwm_policy_schedule(group_id,schedule)
        return result
    @expose(template='json')
    def update_dwm_policy_schedule(self):
        result=self.dwm_controller.update_dwm_policy_schedule()
        return result


