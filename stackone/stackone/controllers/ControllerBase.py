import pylons
import logging
import tg
import os
from tg import expose, flash, require, url, request, redirect, response, session, config
import stackone.core.utils.constants
constants = stackone.core.utils.constants
LOGGER = logging.getLogger('stackone.controllers')
class ControllerBase():
    def authenticate(self, came_from=url('/')):
        if session.get('userid') is None:
            try:                
                self.redirect_to(url('login', came_from=came_from, __logins=0))
            except Exception, e:
                raise Exception("SessionExpired.")



    def redirect_to(self, url):
        try:
            protocol = tg.config.get(constants.SERVER_PROTOCOL,"http")
            host=pylons.request.headers['Host']            
            redirect(url, host=host, protocol=protocol)
        except Exception, e:
            raise e




