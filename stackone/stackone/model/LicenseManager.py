import os
import tg
import logging
import sys
import base64
import traceback
import datetime as datetime_module
from datetime import datetime, date
from stackone.model import DBSession, Deployment
from stackone.core.utils.utils import md5_constructor, to_str, get_platform_name
from stackone.model import DBSession
from stackone.model.Entity import Entity
from sqlalchemy.orm import *
from stackone.core.utils.utils import print_traceback, to_unicode, getHexID
import stackone.core.utils.constants
constants = stackone.core.utils.constants
from stackone.model.ManagedNode import ManagedNode
from sqlalchemy import func
from stackone.model.VM import VM
from stackone.model.notification import Notification
import transaction
LOGGER = logging.getLogger('stackone.model')
LICENSE_CHECK_TIMER = 0L
EXPIRE_NOTIFY_DAYS = 7L
LICENSE_EXPIRE_DAYS = None
LICENSE_VIOLATED = 0L
LICENSE_VIOLATED_MSG = ''
CLOUD_LICENSE = 0L

def set_violated():
    stackone.model.LicenseManager.LICENSE_VIOLATED = 1

def is_violated():
    return stackone.model.LicenseManager.LICENSE_VIOLATED == 1

def check_platform_vm_count(l_info, platform, new):
    return (True, '')
#pass
def check_vm_license(new=0L, platform=None):
    return (True, '')

#pass
def check_sbs_makeup(soc_count=None, platform=None):
    return (True, '')

def check_utc_time_lic():
    return (True, '')




def rem_days_to_exp():
    return ''

def check_license_str():
    return (True, '')


def check_license_id():
    return (True, '')

def check_license_expire_date(auth=None):
    return (True, '')

def get_edition():
    return '3.2.1.5'

#pass
def get_edition_string():
    edition_string = 'stackone Enterprise'
    return edition_string
#pass
def get_sub_edition_string():
    sub_edition_string = 'Trial Edition'
    return sub_edition_string
 
def get_version():
    return '3.2.1.5'


def check_all_lic(auth=None):
    ret,msg = check_license_str()
    if ret == False:
        return (ret, msg)
    ret,msg = check_license_id()
    if ret == False:
        return (ret, msg)
    ret,msg = check_utc_time_lic()
    if ret == False:
        return (ret, msg)
    ret,msg = check_vm_license()
    if ret == False:
        return (ret, msg)
    ret,msg = check_sbs_makeup()
    if ret == False:
        return (ret, msg)
    ret,msg = check_license_expire_date(auth)
    if ret == False:
        return (ret, msg)
    ret,msg = check_platform_license()
    if ret == False:
        return (ret, msg)
    return (True, '')

def has_cloud_license():
    return False

def check_cloud_license():
    stackone.model.LicenseManager.CLOUD_LICENSE = 0

def is_cloud_license_violated():
    return True

def is_ec2_enabled():
    return is_cloud_plugin_enabled(constants.EC2)

def is_euc_enabled():
    return is_cloud_plugin_enabled(constants.EUC)

def is_ost_enabled():
    return is_cloud_plugin_enabled(constants.OPENSTACK)

def is_cms_enabled():
    return is_cloud_plugin_enabled(constants.CMS)

def is_cloud_plugin_enabled(type):
    return True
def check_ec2_vm_count(count):
    return check_plugin_vm_count(constants.EC2, count)

def check_euc_vm_count(count):
    return check_plugin_vm_count(constants.EUC, count)

def check_ost_vm_count(count):
    return check_plugin_vm_count(constants.OPENSTACK, count)

def check_cms_vm_count(count):
    return check_plugin_vm_count(constants.CMS, count)

def check_plugin_vm_count(type, count):
    return True
        

def is_cms_allowed():
    return True
#vCenter
#pass
def get_license_guid():
    return 'e1cdea2a-7506-8195-eeef-052ff966e3b0'
#pass
def check_platform_license():
    return (True,'')     
        
#pass
def check_platform_socket_count(l_info, platform, soc_count):
    return (True, '')
#tianfeng
#pass
def check_platform_expire_date(platform, l_info=None):
    return (True, '')
#pass
def check_server_platform(l_info, platform):
    return check_platform_expire_date(platform, l_info)
#pass
def is_platform_enabled(platform, l_info=None):
    return True
