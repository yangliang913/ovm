import pylons
import simplejson as json
from stackone.lib.base import BaseController
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.ApplianceService import ApplianceService
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
LOGGER = logging.getLogger('stackone.controllers')
from stackone.controllers.ControllerBase import ControllerBase
class ApplianceController(ControllerBase):
    __doc__ = '\n\n    '
    appliance_service = ApplianceService()
    def get_appliance_providers(self, **kw):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.get_appliance_providers()

        except Exception as ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'", '')}
        return dict(success='true', rows=result)


    def get_appliance_packages(self, **kw):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.get_appliance_packages()

        except Exception as ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'", '')}

        return dict(success='true', rows=result)


    def get_appliance_archs(self, **kw):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.get_appliance_archs()

        except Exception as ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'", '')}

        return dict(success='true', rows=result)


    def get_appliance_list(self, **kw):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.get_appliance_list()

        except Exception as ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'", '')}

        return dict(success='true', rows=result)


    def refresh_appliances_catalog(self, **kw):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.refresh_appliances_catalog()

        except Exception as ex:
            print_traceback()
            return {'success':'false','msg':to_str(ex).replace("'", '')}

        return dict(success='true', rows=result)

    def import_appliance(self, href, type, arch, pae, hvm, size, provider_id, platform, description, link, image_name, group_id, is_manual, date=None, time=None, **kw):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.import_appliance(session['auth'], href, type, arch, pae, hvm, size, provider_id, platform, description, link, image_name, group_id, is_manual, date, time)

        except Exception as ex:
            print_traceback()
            return {'success':False,'msg':to_str(ex).replace("'", '')}

        return dict(success=True, rows=result)


    def import_appliance_cli(self, href, type, arch, pae, hvm, size, provider_id, platform, description, link, image_name, group_id, is_manual, date=None, time=None, **result):
        try:
            self.authenticate()
            result = self.appliance_service.import_disk_image(session['auth'], href, type, arch, pae, hvm, size, provider_id, platform, description, link, image_name, group_id, is_manual, date, time)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

        return dict(success=True, taskid=result)


    def get_appliance_menu_items(self, dom_id, node_id):
        try:
            result = None
            self.authenticate()
            result = self.appliance_service.get_appliance_menu_items(session['auth'], dom_id, node_id)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

        return dict(success=True, rows=result)


    def get_appliance_info(self, dom_id, node_id, action=None):
        try:
            self.authenticate()
            result = self.appliance_service.get_appliance_info(session['auth'], dom_id, node_id, action)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

        return dict(success=True, appliance=result)


    def save_appliance_info(self, dom_id, node_id, action=None, **kw):
        try:
            self.authenticate()
            result = self.appliance_service.save_appliance_info(session['auth'], dom_id, node_id, action, kw)

        except Exception as ex:
            print_traceback()
            return dict(success=False, msg=to_str(ex).replace("'", ''))

        return dict(success=True, appliance=result)




