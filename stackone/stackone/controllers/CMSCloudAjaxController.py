import pylons
import simplejson as json
from stackone.viewModel.Userinfo import Userinfo
from stackone.model.Authorization import AuthorizationService
from stackone.controllers.ControllerBase import ControllerBase
from tg import expose, flash, require, url, request, redirect, response, session, config
from stackone.model.CustomPredicates import authenticate
from stackone.model import *
from stackone.viewModel.ApplianceService import ApplianceService
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.constants
constants = stackone.core.utils.constants
import logging
import tg
import os
LOGGER = logging.getLogger('stackone.controllers')
from pylons.controllers.util import forward
from pylons.controllers import XMLRPCController
from stackone.controllers.ApplianceController import ApplianceController
from stackone.controllers.XMLRPC.CMSCloudXMLRPC import CMSCloudXMLRPC
class CMSCloudAjaxController(ControllerBase):
    __doc__ = "\n        Object of this class get created in root.py { cmscloud=CMSCloudAjaxController() }.\n        When a request like 'http://127.0.0.1:8091/cmscloud/xmlrpc' come, that will get redirected to 'CMSCloudXMLRPC'.\n    "
    @expose()
    def xmlrpc(self):
        return forward(CMSCloudXMLRPC())


