import pylons
import logging
import tg
import os
from tg import expose, flash, require, url, request, redirect, response, session, config
import stackone.core.utils.constants
constants = stackone.core.utils.constants
LOGGER = logging.getLogger('stackone.controllers')
from pylons.controllers import XMLRPCController
class stackoneXMLRPC(XMLRPCController):
	allow_none = True


