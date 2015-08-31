import pylons
import simplejson as json
from stackone.lib.base import BaseController
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.NodeService import NodeService
from stackone.viewModel.VMService import VMService
from stackone.viewModel.TaskCreator import TaskCreator
from stackone.controllers.ControllerImpl import ControllerImpl
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
from stackone.model import DBSession
from stackone.viewModel.DWMService import DWMService
from stackone.model.services import Task
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
LOGGER = logging.getLogger('stackone.controllers')
from pylons.controllers import XMLRPCController
import os
import pprint
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.controllers.ControllerBase import ControllerBase
class DWMController(ControllerBase):
    dwm_service = DWMService()
    def save_dwm_details(self, group_id, policy_object, enabled, offset):
        try:
            self.authenticate()
            info = []
            info = self.dwm_service.save_dwm_details(session['auth'],group_id,policy_object,enabled,offset)
            return dict({'success':True,'msg':info})
        except Exception as ex:
            traceback.print_exc()
            return dict({'success':False,'msg':to_str(ex).replace("'",' ')})
    def get_dwm_details(self, group_id):
        try:
            self.authenticate()
            info = []
            info = self.dwm_service.get_dwm_details(session['auth'],group_id)
            return dict({'success':True,'msg':info})
        except Exception as ex:
            traceback.print_exc()
            return dict({'success':False,'msg':to_str(ex).replace("'",' ')})
    def get_dwm_schedule_details(self, group_id, policy_id):
        try:
            self.authenticate()
            info = []
            result = self.dwm_service.get_dwm_schedule_details(group_id,policy_id)
            return dict({'success':True,'info':result})
        except Exception as ex:
            traceback.print_exc()
            return dict({'success':False,'msg':to_str(ex).replace("'",' ')})

    def get_policy_forall(self):
        try:
            self.authenticate()
            info = []
            info.append(dict({'id':'1','policy':'LB'}))
            info.append(dict({'id':'2','policy':'PS'}))
            return dict({'success':True,'info':info})
        except Exception as ex:
            traceback.print_exc()
            return dict({'success':False,'msg':to_str(ex).replace("'",' ')})

    def store_dwm_policy_schedule(self, group_id, sch_object):
        json.loads(sch_object)
        try:
            self.authenticate()
            info = []
            info = self.dwm_service.store_spdwm_schedule(group_id,sch_object)
            return dict({'success':True,'info':info})
        except Exception as ex:
            traceback.print_exc()
            return dict({'success':False,'msg':to_str(ex).replace("'",' ')})

    def update_dwm_policy_schedule(self):
        try:
            self.authenticate()
            info = []
            info = self.dwm_service.update_spdwm_schedule()
            return dict({'success':True,'info':info})
        except Exception as ex:
            traceback.print_exc()
            return dict({'success':False,'msg':to_str(ex).replace("'",' ')})


