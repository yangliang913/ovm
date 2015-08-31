import ConfigParser
import subprocess
import platform
import sys
import os
import os.path
import socket
import types
import tempfile
import re
import glob
import shutil
import urllib
import urllib2
import urlparse
import stackone.core.utils.constants
import time
import datetime as datetime_module
from datetime import datetime, timedelta
import string
import random
import traceback
import xml.dom.minidom
from xml.dom.minidom import Node
import webbrowser
import tg
import calendar
import netaddr
from sqlalchemy import func
try:
    import hashlib
    md5_constructor = hashlib.md5
except ImportError as e:
    import md5
    md5_constructor = md5.new
import logging
LOGGER = logging.getLogger('stackone.core.utils')
constants = stackone.core.utils.constants
#
class CancelException(Exception):
    def __init__(self, errno=404, description='Cancel Requested.'):
        Exception.__init__(self, errno, description)
        self.errno = errno
        self.description = description

    def __repr__(self):
        return '[Error %s], %s' % (self.errno, self.description)

    def __str__(self):
        return self.__repr__()



import locale
#
def to_unicode(text):
    if isinstance(text, unicode):
        return text
    if hasattr(text, '__unicode__'):
        return text.__unicode__()
    text = str(text)
    try:
        return unicode(text, 'utf-8')
    except UnicodeError:
        pass
    try:
        return unicode(text, locale.getpreferredencoding())
    except UnicodeError:
        pass
    return unicode(text, 'latin1')

#
def to_str(text):
    if isinstance(text, str):
        return text
    if hasattr(text, '__unicode__'):
        text = text.__unicode__()
    if hasattr(text, '__str__'):
        return text.__str__()
    return text.encode('utf-8')

#
def wait_for_task_completion(task_id, wait_time=0):
    from stackone.model.services import Task
    from stackone.model import DBSession
    from sqlalchemy.orm import eagerload
    import transaction
    finished = False
    status = Task.STARTED
    for i in range(0, wait_time):
        time.sleep(1)
        transaction.begin()
        task = DBSession.query(Task).filter(Task.task_id == task_id).options(eagerload('result')).first()
        if task.is_finished():
            finished = True
            status = task.result[0].status
            transaction.commit()
            break
        transaction.commit()
        
    return (finished, status)
#
def get_parent_task_status_info(task):
    from stackone.model.services import Task
    stat = Task.get_status(task)
    stat += '\nExecution Context :'
    ex_context = task.context.get('execution_context')
    if ex_context:
        for key, val in ex_context.iteritems():
            stat += '\n\t %s : %s' % (key, val)
    
    return stat

#
def get_child_task_status_info(task):
    from stackone.model.services import Task
    stat = Task.get_status(task)
    stat += "\nExecution Context :"
    ex_context = task.context.get("execution_context")
    node_ids = task.get_param("node_ids")
    stat += "\n\t NodeIDs : %s" %node_ids
    now = datetime.now()
    try:
        stat += '\n\t CurrentServer : %s("%s")' %(task.current_node.hostname, task.current_node.id)
        strt = task.start_time
        durn = str((now-strt).seconds)+"."+str((now-strt).microseconds)
        stat+='\n\t StartTime: "%s", RunningFor: "%s"' % (strt, durn)
    except AttributeError:
        pass

    if ex_context:
        for key,val in ex_context.iteritems():
            stat += "\n\t %s : %s" %(key, val)
    return stat
#
def convert_to_CMS_TZ(gmt_time):
    #t = datetime.datetime.now()
    return_time = time.mktime(gmt_time.timetuple())* 1000
    #return_time = calendar.timegm(gmt_time.timetuple()) * 1000
    #return_time = calendar.timegm(gmt_time.timetuple()) * 1000
    return return_time

#
def replace_with_CMS_TZ(objList, field1, field2=None):
    is_object_dict = False
    if type(objList) == dict:
        is_object_dict = True
        objList = objList.get('rows')
    for item in objList:
        if field1:
            gmt_time = item.get(field1)
            if gmt_time:
                cms_time = convert_to_CMS_TZ(gmt_time)
                item[field1] = cms_time
        if field2:
            gmt_time = item.get(field2)
            if gmt_time:
                cms_time = convert_to_CMS_TZ(gmt_time)
                item[field2] = cms_time
                continue
                
    if is_object_dict:
        objDict = {}
        objDict['rows'] = objList
        return objDict
        
    return objList


#
def get_canonical_name(name):
    INVALID_CHARS_EXP = '( |/|,|@|#|\\$|\\*|<|>|\\||\\!|\\&|\\%|\\.|\'|"|\\^|\\\\)'
    return re.sub(INVALID_CHARS_EXP, '_', name)
#############jpass
class dynamic_map():
    def __init__(self, another_dict=None):
        if another_dict:
            self._dynamic_map__dictionary = dict(another_dict)
        else:
            self._dynamic_map__dictionary = dict()

    def __getattr__(self, name):
        if self._dynamic_map__dictionary.has_key(name):
            return self._dynamic_map__dictionary[name]
        if name.startswith('__') and name.endswith('__'):
            return self._dynamic_map__dictionary.__getattr__(name)
        return None

    def __getitem__(self, name):
        if dict.has_key(self._dynamic_map__dictionary, name):
            return dict.__getitem__(self._dynamic_map__dictionary, name)
        return None

    def __setitem__(self, name, value):
        self._dynamic_map__dictionary[name] = value

    def __setattr__(self, name, value):
        if name == '_dynamic_map__dictionary':
            self.__dict__[name] = value
        else:
            self._dynamic_map__dictionary[name] = value

    def __repr__(self):
        return to_str(self._dynamic_map__dictionary)

    def __getstate__(self):
        return self._dynamic_map__dictionary

    def __setstate__(self, dictionary):
        self._dynamic_map__dictionary = dictionary

    def __str__(self):
        return self.__repr__()

    def print_classes(self):
        for k,v in self._dynamic_map__dictionary.items():
            print v.__class__

    def has_key(self, name):
        return self._dynamic_map__dictionary.has_key(name)

    def items(self):
        return self._dynamic_map__dictionary.items()

    def iteritems(self):
        return self._dynamic_map__dictionary.iteritems()

    def iterkeys(self):
        return self._dynamic_map__dictionary.iterkeys()

    def itervalues(self):
        return self._dynamic_map__dictionary.itervalues()

    def keys(self):
        return self._dynamic_map__dictionary.keys()

    def values(self):
        return self._dynamic_map__dictionary.values()

    def clear(self):
        return self._dynamic_map__dictionary.clear()

    def pop(self, key, default=None):
        return self._dynamic_map__dictionary.pop(key, default)

    def popitem(self):
        return self._dynamic_map__dictionary.popitem()

    def get(self, key):
        return self._dynamic_map__dictionary.get(key)
#
class fv_map(dict):
    def __init__(self):
        dict.__init__(self)

    def __getitem__(self, name):
        if dict.has_key(self, name):
            value = dict.__getitem__(self, name)
            if isinstance(value, types.MethodType) or isinstance(value, types.FunctionType):
                value = value()
                return value
                
        return dict.__getitem__(self, name)


#
class XMConfig(ConfigParser.SafeConfigParser):
    DEFAULT = 'DEFAULT'
    ENV = 'ENVIRONMENT'
    PATHS = 'PATHS'
    APP_DATA = 'APPLICATION DATA'
    CLIENT_CONFIG = 'CLIENT CONFIGURATION'
    IMAGE_STORE = 'IMAGE STORE'
    DEFAULT_REMOTE_FILE = '/etc/stackone.conf'
    
    #
    def __init__(self, node, searchfiles=None, create_file=None):
        ConfigParser.SafeConfigParser.__init__(self)
        self.node = node
        self.std_sections = [self.ENV, self.PATHS, self.APP_DATA, self.CLIENT_CONFIG]
        if searchfiles is None:
            if not self.node.isRemote:
                filelist = [x for x in [os.path.join(os.getcwd(), 'stackone.conf'), os.path.expanduser('~/.stackone/stackone.conf'), '/etc/stackone.conf'] if self.node.file_exists(x)]
            else:
                if self.node.file_exists(self.DEFAULT_REMOTE_FILE):
                    filelist = [self.DEFAULT_REMOTE_FILE]
                else:
                    filelist = []
        else:
            filelist = [x for x in searchfiles if self.node.file_exists(x)]
            
        if len(filelist) < 1:
            base_dir = None
            print 'No Configuration File Found'
            if create_file is None:
                if not self.node.isRemote:
                    print 'Creating default stackone.conf in current directory'
                    self.configFile = os.path.join(os.getcwd(), 'stackone.conf')
                    base_dir = os.getcwd()
                else:
                    print 'Creating default stackone.conf at %s:%s' % (self.node.hostname, self.DEFAULT_REMOTE_FILE)
                    self.configFile = self.DEFAULT_REMOTE_FILE
            else:
                print 'Creating default stackone.conf at %s:%s' % (self.node.hostname, create_file)
                self.configFile = create_file
                
            self._XMConfig__createDefaultEntries(base_dir)
            self._XMConfig__commit()
        else:
            self.configFile = None
            for f in filelist:
                try:
                    if self.node.file_is_writable(f):
                        if self._XMConfig__validateFile(f):
                            self.configFile = f
                            print 'Valid, writable configuration found, using %s' % f
                        else:
                            self.node.rename(f, f + '.bak')
                            print 'Old configuration found. Creating backup: %s.bak' % f
                        break
                    else:
                        print 'Confguration File not writable, skipping: %s' % f
                except IOError:
                    print 'Confguration File accessable, skipping: %s' % f

            if self.configFile is None:
                print 'No writable configuration found ... '
                if not self.node.isRemote:
                    base_dir = os.path.expanduser('~/.stackone/')
                    if not os.path.exists(base_dir):
                        os.mkdir(base_dir)
                        
                    self.configFile = os.path.join(base_dir, 'stackone.conf')
                    print '\t Creating %s' % self.configFile
                    self._XMConfig__createDefaultEntries(base_dir)
                    self._XMConfig__commit()
                else:
                    raise Exception('No writable configuration found on remote host: %s' % self.node.hostname)

            fp = self.node.open(self.configFile)
            self.readfp(fp)
            fp.close()

    #
    def _XMConfig__createDefaultEntries(self, base_dir=None):
        for s in self.sections():
            self.remove_section(s)
        for s in self.std_sections:
            self.add_section(s)
        self.set(self.DEFAULT, constants.prop_default_computed_options, "['arch', 'arch_libdir', 'device_model']")
        if base_dir:
            base = base_dir
            log_dir = os.path.join(base, 'log')
        else:
            base = '/var/cache/stackone'
            log_dir = '/var/log/stackone'
            
        i_store = os.path.join(base, 'image_store')
        a_store = os.path.join(base, 'appliance_store')
        updates_file = os.path.join(base, 'updates.xml')
        self.set(self.PATHS, constants.prop_snapshots_dir, '/var/cache/stackone/vm_snapshots')
        self.set(self.PATHS, constants.prop_snapshot_file_ext, '.snapshot.xm')
        self.set(self.PATHS, constants.prop_cache_dir, '/var/cache/stackone')
        self.set(self.PATHS, constants.prop_exec_path, '$PATH:/usr/sbin')
        self.set(self.PATHS, constants.prop_image_store, i_store)
        self.set(self.PATHS, constants.prop_appliance_store, a_store)
        self.set(self.PATHS, constants.prop_updates_file, updates_file)
        self.set(self.PATHS, constants.prop_log_dir, log_dir)
        self.set(self.CLIENT_CONFIG, constants.prop_default_ssh_port, '22')
        self.set(self.CLIENT_CONFIG, constants.prop_enable_log, 'True')
        self.set(self.CLIENT_CONFIG, constants.prop_log_file, 'stackone.log')
        self.set(self.CLIENT_CONFIG, constants.prop_enable_paramiko_log, 'False')
        self.set(self.CLIENT_CONFIG, constants.prop_paramiko_log_file, 'paramiko.log')
        self.set(self.CLIENT_CONFIG, constants.prop_http_proxy, '')
        self.set(self.CLIENT_CONFIG, constants.prop_chk_updates_on_startup, 'True')
        if not self.node.isRemote:
            self.set(self.ENV, constants.prop_dom0_kernel, platform.release())
    #
    def _XMConfig__commit(self):
        outfile = self.node.open(self.configFile, 'w')
        self.write(outfile)
        outfile.close()
    #
    def _XMConfig__validateFile(self, filename):
        temp = ConfigParser.ConfigParser()
        fp = self.node.open(filename)
        temp.readfp(fp)
        fp.close()
        for s in self.std_sections:
            if not temp.has_section(s):
                print 'section ' + s + ' not found'
                return False
        return True
    #
    def getDefault(self, option):
        return self.get(self.DEFAULT, option)
    #
    def get(self, section, option):
        if option is None:
            return None
        if not self.has_option(section, option):
            return None
        retVal = ConfigParser.SafeConfigParser.get(self, section, option)
        if retVal == None:
            return retVal
        if not retVal.strip():
            return None
        return retVal
    #
    def setDefault(self, option, value):
        if option is not None:
            self.set(self.DEFAULT, option, value)
    #
    def set(self, section, option, value):
        ConfigParser.SafeConfigParser.set(self, section, option, value)
        self._XMConfig__commit()
    #
    def getHostProperty(self, option, hostname=constants.LOCALHOST):
        if not self.has_option(hostname, option):
            return None
        retVal = self.get(hostname, option)
        if retVal == None:
            return retVal
        if not retVal.strip():
            return None
        return retVal
    #
    def getHostProperties(self, hostname=constants.LOCALHOST):
        if not self.has_section(hostname):
            return None
        return dict(self.items(hostname))
    #
    def setHostProperties(self, options, hostname=constants.LOCALHOST):
        if not self.has_section(hostname):
            self.add_section(hostname)
            
        for option in options:
            self.set(hostname, option, options[option])
        self._XMConfig__commit()
    #
    def setHostProperty(self, option, value, hostname=constants.LOCALHOST):
        if not self.has_section(hostname):
            self.add_section(hostname)
            
        self.set(hostname, option, value)
        self._XMConfig__commit()
    #
    def removeHost(self, hostname):
        if self.has_section(hostname):
            self.remove_section(hostname)
            self._XMConfig__commit()
    #
    def getHosts(self):
        hosts = []
        for sec in self.sections():
            if sec in self.std_sections or sec == self.IMAGE_STORE:
                continue
            hosts.append(sec)
        return hosts
    #
    def getGroups(self):
        groups = self.get(self.APP_DATA, constants.prop_groups)
        if groups is not None:
            return eval(groups)
        return {}
    #
    def saveGroups(self, group_list):
        g_list_map = {}
        for g in group_list:
            g_map = {}
            g_map['name'] = group_list[g].name
            g_map['node_list'] = group_list[g].getNodeNames()
            g_map['settings'] = group_list[g].getGroupVars()
            g_list_map[group_list[g].name] = g_map
            
        self.set(self.APP_DATA, constants.prop_groups, to_str(g_list_map))
        self._XMConfig__commit()


        
#
class LVMProxy():
    __doc__ = "A thin, (os-dependent) wrapper around the shell's LVM\n    (Logical Volume Management) verbs"
    
    #
    @classmethod
    def isLVMEnabled(cls, node_proxy, exec_path=''):
        retVal = True
        if node_proxy.exec_cmd('vgs 2> /dev/null',exec_path)[1]:
            retVal = False
        return retVal
    #
    def __init__(self, node_proxy, exec_path=''):
        self.node = node_proxy
        self.exec_path = exec_path
        if node_proxy.exec_cmd('vgs 2> /dev/null', exec_path)[1]:
            raise OSError('LVM facilities not found')
    #
    def listVolumeGroups(self):
        try:
            vglist = self.node.exec_cmd('vgs -o vg_name --noheadings', self.exec_path)[0]
            return [s.strip() for s in vglist.splitlines()]
        except OSError, err:
            print err
    #
    def listLogicalVolumes(self, vgname):
        try:            
            lvlist = self.node.exec_cmd('lvs -o lv_name --noheadings '+ vgname,
                                        self.exec_path)[0]
            return [s.strip() for s in lvlist.splitlines()]
        except OSError, err:
            print err
            return None

    #
    def createLogicalVolume(self, lvname, lvsize, vgname):
        error,retcode = self.node.exec_cmd('lvcreate %s -L %sM -n %s'%(vgname,lvsize,lvname),
                                           self.exec_path)
        if retcode:
            raise OSError(error.strip('\n'))
        else:
            return True

    #
    def removeLogicalVolume(self, lvname, vgname=None):
        if vgname:
            lvpath = vgname + '/' + lvname
        else:
            lvpath = lvname
        error, retcode = self.node.exec_cmd('lvremove -f %s' % lvpath, self.exec_path)
        if retcode:
            raise OSError(error.strip('\n'))
        else:
            return True



from threading import Thread
#
class Poller(Thread):
    __doc__ = ' A simple poller class representing a thread that wakes\n    up at a specified interval and invokes a callback function'
    def __init__(self, freq, callback, args=[], kwargs={}, max_polls=None):
        Thread.__init__(self)
        self.setDaemon(True)
        self.frequency = freq
        self.callback = callback
        self.args = args
        self.kwargs = kwargs
        self.done = False
        self.remainder = max_polls

    def run(self):
        while not self.done:
            self.callback(*self.args,**self.kwargs)
            time.sleep(self.frequency)
            if self.remainder is not None:
                self.remainder -= 1
                if self.remainder < 0:
                    self.done = True

    def stop(self):
        self.done = True


#
class PyConfig():
    default_computed_options = []
    COMPUTED_OPTIONS = 'computed_options'
    CUSTOMIZABLE_OPTIONS = 'customizable_options'
    def __init__(self, managed_node=None, filename=None, signature=None, config=None):
        if managed_node is not None and type(managed_node) in [types.StringType, types.UnicodeType]:
            raise Exception('Wrong param to PyConfig.')
        self.filename = filename
        self.managed_node = managed_node
        self.lines = []
        self.options = {}
        self.signature = signature
        self.config = config
        if self.filename is not None or self.config is not None:
            self.lines,self.options = self.read_conf()
        return None

    @classmethod        
    def set_computed_options(cls, computed):
        cls.default_computed_options = computed
    
    def get_computed_options(self):
        c = []
        if self.default_computed_options is not None:
            c = self.default_computed_options
            
        if self.options.has_key(self.COMPUTED_OPTIONS):
            specific_computed_options = self[self.COMPUTED_OPTIONS]
        else:
            specific_computed_options = None
            
        if specific_computed_options is not None and \
               type(specific_computed_options) == types.ListType:
            for o in specific_computed_options:
                c.append(o)

        if self.COMPUTED_OPTIONS not in c :
            c.append(self.COMPUTED_OPTIONS)
        return c        
        

    def get_customizable_options(self):
        customizable_options = None
        if self.options.has_key(self.CUSTOMIZABLE_OPTIONS):
            customizable_options = self[self.CUSTOMIZABLE_OPTIONS]
        else:
            customizable_options = self.options.keys()

        if customizable_options is not None and \
               self.CUSTOMIZABLE_OPTIONS in customizable_options :
            customizable_options.remove(self.CUSTOMIZABLE_OPTIONS)
            
        return (customizable_options)

    def set_filename(self, filename):
        self.filename = filename

    def set_managed_node(self, node):
        self.managed_node = node

    def read_config(self, init_glob=None, init_locs=None):
        if init_glob is not None:
            globs = init_glob
        else:
            globs = {}

        if init_locs is not None:
            locs = init_locs
        else:
            locs  = {}

        lines = []
        lines=self.config.split('\n')
        options = {}
        try:
            if len(lines) > 0:
                cmd = '\n'.join(lines)
                cmd = cmd.replace('\r\n', '\n')
                exec (cmd,globs, locs)
        except:
            raise
        # Extract the values set by the script and set the corresponding
        # options, if not set on the command line.
        vtypes = [ types.StringType,
                   types.UnicodeType,
                   types.ListType,
                   types.IntType,
                   types.FloatType,
                   types.DictType
                   ]
        for (k, v) in locs.items():
            if (type(v) not in vtypes): continue
            options[k]=v
        return (lines,options)
    #pass
    def get_config_using_external_source(self):
        cmd = ''
        try:
            f = open(self.filename)
            lines = f.readlines()
            if len(lines) > 0:
                cmd = '\n'.join(lines)
            f.close()
            return (lines, cmd)
        except Exception as ex:
            raise ex
#        finally:
#            f.close()
    def read_conf(self, init_glob=None, init_locs=None):
        if self.config is not None:
            return self.read_config(init_glob, init_locs)
        if init_glob is not None:
            globs = init_glob
        else:
            globs = {}
        if init_locs is not None:
            locs = init_locs
        else:
            locs = {}
        lines = []
        options = {}
        cmd = None
        if self.managed_node is None:
            lines,cmd = self.get_config_using_external_source()
        else:
            cmd = self.get_config_using_node()
        options = self.parse_config(cmd, globs, locs)
        return (lines, options)
    #pass
    def parse_config(self, cmd, init_glob=None, init_locs=None):
        options = {}
        if init_glob is not None:
            globs = init_glob
        else:
            globs = {}
        if init_locs is not None:
            locs = init_locs
        else:
            locs = {}
        if cmd:
            cmd = cmd.replace('\r\n', '\n')
            exec (cmd,globs,locs)
        vtypes = [types.StringType, types.UnicodeType, types.ListType, types.IntType, types.FloatType, types.DictType]
        for k,v in locs.items():
            if (type(v) not in vtypes): continue
            options[k] = v
        return options



    def write(self, full_edit=False):
        """Writes the settings out to the filename specified during
        initialization"""

        dir = os.path.dirname(self.filename)
        if self.managed_node is None:
            if not os.path.exists(dir):
                os.makedirs(dir)
            outfile = open(self.filename, 'w')
        else:
            if not self.managed_node.node_proxy.file_exists(dir):
                mkdir2(self.managed_node, dir)
            outfile = self.managed_node.node_proxy.open(self.filename, 'w')
            
        if self.signature is not None:
            outfile.write(self.signature)
        
        # Simple write
        if self.lines is None or len(self.lines) == 0:
            for name, value in self.options.iteritems():
                outfile.write("%s = %s\n" % (name, repr(value)))
        else:
            # drive the writing through lines read.
            updated = []
            for line in self.lines:
                if self.signature is not None and \
                       line.find(self.signature) >= 0:
                    continue
                if line == '':
                    continue
                if  line[0] == '#' or  line[0] == '\n' or \
                        line[0].isspace() or line.strip().endswith(':'):
                    outfile.write(line)
                else:
                    ndx = line.find("=")
                    if ndx > -1:
                        token = line[0:ndx]
                        token = token.strip()
                        if self.options.has_key(token):
                            if token not in self.get_computed_options() and \
                               (token != self.CUSTOMIZABLE_OPTIONS or full_edit) :
                                value = self.options[token]
                                outfile.write("%s=%s\n" % (token, repr(value)))
                                updated.append(token)
                            else:
                                #print "writing computed Token X:" , line
                                if token != self.COMPUTED_OPTIONS:
                                    outfile.write(line)
                        else:
                            if token in self.get_computed_options():
                                outfile.write(line)
                            else:
                                #print "Valid token but removed" , line
                                pass
                    else:
                        #print "writing default Y:" , line
                        outfile.write(line)

            # Add new tokens added
            for name, value in self.options.iteritems():
                if name not in updated and \
                       name not in self.get_computed_options():
                    outfile.write("%s=%s\n" % (name, repr(value)))

        outfile.close()


    def instantiate_config(self, value_map):
        
        # do this so that substitution happens properly
        # we may have to revisit, map interface of PyConfig
        if isinstance(value_map, PyConfig):
            value_map = value_map.options
        
        # instantiate the filename
        if self.filename is not None:
            fname = string.Template(self.filename)
            new_val = fname.safe_substitute(value_map)
            self.set_filename(new_val)
        
        for key in self.options.keys():
            value = self.options[key]
            if value is not None:                
                if type(value) in [types.StringType,types.UnicodeType]:
                    template_str = string.Template(value)
                    self.options[key] = to_str(template_str.safe_substitute(value_map))
                elif type(value) is types.ListType:
                    new_list = []
                    for v in value:
                        if type(v) is types.StringType:
                            template_str = string.Template(v)
                            new_list.append(template_str.safe_substitute(value_map))
                                                
                        else:
                            new_list.append(v)
                    self.options[key] = new_list
                    #print "old %s, new %s", (value, self.options[key])
                    



    def save(self, filename):
        self.filename = filename
        self.write()

    def get(self, name):
        return self[name]

    def __getitem__(self, name):
        if self.options.has_key(name):
            return self.options[name]
        else:
            attrib = getattr(self,name, None)
            if attrib is not None:
                return attrib
            else:
                return None

    def __setitem__(self, name, item):
        self.options[name] = item

    def __iter__(self):
        return self.options.iterkeys()

    def iteritems(self):
        return self.options.iteritems()

    def has_key(self, key):
        return self.options.has_key(key)

    def keys(self):
        return self.options.keys()

    def dump(self):
        if self.filename is not None:
            print self.filename
        for name,value in self.options.iteritems():
            print '%s = %s' % (name, repr(value))
        return None

    def __delitem__(self, key):
        if self.has_key(key):
            del self.options[key]

    #pass
    def get_config_using_node(self):
        cmd = self.managed_node.get_config_contents(self.filename)
        return cmd

import threading
from threading import Thread
#
class Worker(Thread):
    def __init__(self, fn, succ, fail,progress=None):
        Thread.__init__(self)
        self.setDaemon(True)
        self.fn = fn
        self.succ = succ
        self.progress = progress
        self.fail = fail
        
    def run(self):
        try:
            ret = self.fn()
        except Exception, ex:
            traceback.print_exc()
            if self.fail:
                gobject.idle_add(self.fail,ex)
        else:
            if self.succ:
                gobject.idle_add(self.succ, ret)

#
class UpdatesMgr():
    update_url = "http://www.stackone.com.cn/updates/updates.xml"
    updates_file = "/var/cache/stackone/updates.xml"
    
    def __init__(self, config):
        self.config = config
        self.url = self.config.get(XMConfig.PATHS, constants.prop_updates_url)
        if not self.url:
            self.url = UpdatesMgr.update_url
            
            
        self.updates_loc = self.config.get(XMConfig.PATHS,
                                       constants.prop_updates_file)
        if not self.updates_file:
            self.updates_file = UpdatesMgr.updates_file


    def fetch_updates(self):
        update_items = []

        try:
            # file is not writable..lets create a tmp file
            if not os.access(self.updates_file,os.W_OK):
                (t_handle, t_name) = tempfile.mkstemp(prefix="updates.xml")
                self.updates_file = t_name
                os.close(t_handle) # Use the name, close the handle.
                
            fetch_isp(self.url, self.updates_file, "/xml")
        except Exception, ex:
            print "Error fetching updates ", ex
            try:
                if os.path.exists(self.updates_file):
                    os.remove(self.updates_file)
            except:
                pass
            return update_items


        if os.path.exists(self.updates_file):
            updates_dom = xml.dom.minidom.parse(self.updates_file)
            for entry in updates_dom.getElementsByTagName("entry"):
                info = {}
                for text in ("title","link","description", "pubDate",
                             "product_id", "product_version","platform"):
                    info[text] = getText(entry, text)
                populate_node(info,entry,"link",
                          { "link" : "href"})

                update_items.append(info)

        # cleanup the file
        try:
            if os.path.exists(self.updates_file):
                os.remove(self.updates_file)
        except:
            pass
        
        return update_items


    # every time it is called it gets new updates from last time
    # it was called.
    def get_new_updates(self):
        new_updates = []
        updates = self.fetch_updates()
        str_r_date = self.config.get(XMConfig.APP_DATA,
                                   constants.prop_ref_update_time)
        if str_r_date:
            p_r_date = time.strptime(str_r_date, "%Y-%m-%d %H:%M:%S")
            r_date = datetime(*p_r_date[0:5])
        else:
            r_date = datetime(2000, 1, 1)

        max_dt = r_date
        for update in updates:
            str_p_dt = to_str(update["pubDate"])
            if str_p_dt:
                p_dt = time.strptime(str_p_dt, "%Y-%m-%d %H:%M:%S")
                dt = datetime(*p_dt[0:5])
                if dt > r_date :
                    new_updates.append(update)
                    if dt > max_dt:
                        max_dt = dt
                        

        if max_dt > r_date:
            str_max_dt = max_dt.strftime("%Y-%m-%d %H:%M:%S")
            self.config.set(XMConfig.APP_DATA,
                            constants.prop_ref_update_time,
                            str_max_dt)
        return new_updates


#write 0906
def copyToRemote(src, dest_node, dest_dir, dest_name=None, hashexcludes=[], timeout=None):
    from stackone.viewModel import Basic
    import stackone.core.utils.commands as commands
    if not timeout:
        timeout = int(tg.config.get('default_timeout', 300))
    srcFileName = os.path.basename(src)
    if srcFileName and srcFileName[0L] == '.':
        print 'skipping hidden file ',
        print src
        return None
    if not os.path.exists(src):
        raise Exception('%s does not exist.' % src)
    hashFile = src + '.hash'

    if os.path.isfile(src) and not src.endswith('.hash'):
        #1183
        mkdir2(dest_node, dest_dir)
        dest_hashFile = os.path.join(dest_dir, os.path.basename(hashFile))
        if dest_name is not None:
            dest = os.path.join(dest_dir, dest_name)
        else:
            dest = os.path.join(dest_dir, os.path.basename(src))
        copyFile = False
        if srcFileName not in hashexcludes:
            if not os.path.exists(hashFile):
                generateHashFile(src)
            else:
                updateHashFile(src)
            localhashVal = None
            remotehashVal = None
            if os.path.exists(hashFile):
                lhf = None
                try:
                    lhf = open(hashFile)
                    localhashVal = lhf.read()
                finally:
                    if lhf:
                        lhf.close()
                if dest_node.node_proxy.file_exists(dest_hashFile):
                    rhf = None
                    try:
                        rhf = dest_node.node_proxy.open(dest_hashFile)
                        remotehashVal = rhf.read()
                    finally:
                        if rhf:
                            rhf.close()
            else:
                raise Exception('Hash file not found.' + hashFile)
            if not compareHash(remotehashVal, localhashVal) or not dest_node.node_proxy.file_exists(dest):
                copyFile = True
        else:
            copyFile = True
        if copyFile:
            print 'copying '
            print src
            mode = os.lstat(src).st_mode
            f_size = os.path.getsize(src)
            if f_size > 65536L:
                msg = 'CopyToRemote: Copying sparse file: %s to %s' % (src, dest_dir)
                print msg
                LOGGER.info(msg)
                local = Basic.getManagedNode()
                node_username = dest_node.get_credentials().get('username')
                src_filename = src.split('/')[-1L]
                src_dir = src[0L:-len(src_filename)]
                cmd = commands.get_cmd_copy_spares_file_to_remote(node_username, dest_node.hostname, src_filename, dest_dir)
                output,exit_code = local.node_proxy.exec_cmd(cmd, exec_path=src_dir, cd=True, timeout=timeout)
                if exit_code:
                    msg = 'CopyToRemote: Can not copy spares file %s to %s, %s' % (src, dest_dir, output)
                    print msg
                    LOGGER.error(msg)
                    raise Exception(msg)
                msg = 'CopyToRemote: Copied sparse file: %s to %s' % (src, dest_dir)
                print msg
                LOGGER.info(msg)
            else:
                msg = 'CopyToRemote: Copying file: %s to %s' % (src, dest_dir)
                print msg
                LOGGER.info(msg)
                dest_node.node_proxy.put(src, dest)
                dest_node.node_proxy.chmod(dest, mode)
                msg = 'CopyToRemote: Copied file: %s to %s' % (src, dest_dir)
                print msg
                LOGGER.info(msg)

            if srcFileName not in hashexcludes:
                print 'copying hash too',
                print hashFile
                mode = os.lstat(hashFile).st_mode
                dest_node.node_proxy.put(hashFile, dest_hashFile)
                dest_node.node_proxy.chmod(dest_hashFile, mode)
    else:
        if os.path.isdir(src):
            mkdir2(dest_node, dest_dir)
            if dest_name is not None:
                dest = os.path.join(dest_dir, dest_name)
            else:
                dirname,basename = os.path.split(src)
                dest = os.path.join(dest_dir, basename)
                mkdir2(dest_node, dest)
            for entry in os.listdir(src):
                s = os.path.join(src, entry)
                copyToRemote(s, dest_node, dest, hashexcludes=hashexcludes)
    return None
# def copyToRemote(src, dest_node, dest_dir, dest_name=None, hashexcludes=[]):
    # srcFileName = os.path.basename(src)
    # if srcFileName and srcFileName[0] == '.':
        # print 'skipping hidden file ',
        # print src
        # return None
        
    # if not os.path.exists(src):
        # raise Exception('%s does not exist.' % src)

    # hashFile = src + '.hash'
    # if os.path.isfile(src) and not src.endswith('.hash'):
        # mkdir2(dest_node, dest_dir)
        # dest_hashFile = os.path.join(dest_dir, os.path.basename(hashFile))
        # if dest_name is not None:
            # dest = os.path.join(dest_dir, dest_name)
        # else:
            # dest = os.path.join(dest_dir, os.path.basename(src))
        # copyFile = False
        # if srcFileName not in hashexcludes:
            # if not os.path.exists(hashFile):
                # generateHashFile(src)
            # else:
                # updateHashFile(src)
            # localhashVal = None
            # remotehashVal = None
            # if os.path.exists(hashFile):
                # lhf = None
                # try:
                    # lhf = open(hashFile)
                    # localhashVal = lhf.read()
                # finally:
                    # if lhf:
                        # lhf.close()
                        
                # if dest_node.node_proxy.file_exists(dest_hashFile):
                    # rhf = None
                    # try:
                        # rhf = dest_node.node_proxy.open(dest_hashFile)
                        # remotehashVal = rhf.read()
                    # finally:
                        # if rhf:
                            # rhf.close()
            # else:
                # raise Exception('Hash file not found.' + hashFile)
            # if not compareHash(remotehashVal, localhashVal) or not dest_node.node_proxy.file_exists(dest):
                # copyFile = True
        # else:
            # copyFile = True

        # if copyFile:
            # print 'copying ',
            # print src
            # mode = os.lstat(src).st_mode
            # dest_node.node_proxy.put(src, dest)
            # dest_node.node_proxy.chmod(dest, mode)
            
            # if srcFileName not in hashexcludes:
                # print 'copying hash too',
                # print hashFile
                # mode = os.lstat(hashFile).st_mode
                # dest_node.node_proxy.put(hashFile, dest_hashFile)
                # dest_node.node_proxy.chmod(dest_hashFile, mode)
    # else:
        # if os.path.isdir(src):
            # mkdir2(dest_node, dest_dir)
            # if dest_name is not None:
                # dest = os.path.join(dest_dir, dest_name)
            # else:
                # dirname, basename = os.path.split(src)
                # dest = os.path.join(dest_dir, basename)
                # mkdir2(dest_node, dest)
            # for entry in os.listdir(src):
                # s = os.path.join(src, entry)
                # copyToRemote(s, dest_node, dest, hashexcludes=hashexcludes)

#
def generateHashFile(filename):
    f = file(filename, 'rb')
    fw = file(filename + '.hash', 'wb')
    m = md5_constructor()
    readBytes = 1024
    try:
        while readBytes:
            readString = f.read(readBytes)
            m.update(readString)
            readBytes = len(readString)
    finally:
        f.close()
        
    try:
        fw.write(to_str(os.stat(filename).st_mtime))
        fw.write('|')
        fw.write(m.hexdigest())
    finally:
        fw.close()

#
def updateHashFile(filename):
    fhash = file(filename + '.hash', 'rb')
    m = md5_constructor()
    try:
        readHash = fhash.read()
    finally:
        fhash.close()
    hashline = readHash.split('|')
    hashVal = m.hexdigest()
    hashTime = os.stat(filename).st_mtime
    generate = False
    if hashline[0] == to_str(hashTime) and hashline[1] == hashVal:
        return None
 
    f = file(filename, 'rb')
    readBytes = 1024
    try:
        while readBytes:
            readString = f.read(readBytes)
            m.update(readString)
            readBytes = len(readString)
    finally:
        f.close()

    try:
        fhash = file(filename + '.hash', 'wb')
        fhash.write(to_str(hashTime))
        fhash.write('|')
        fhash.write(hashVal)
    finally:
        fhash.close()

#
def compareHash(remoteHash, localHash):
    return remoteHash == localHash

#
def mkdir2(dest_node, dir):
    root = dir
    list = []
    while root and not dest_node.node_proxy.file_exists(root) and root is not '/':
        list.insert(0, root)
        root, subdir = os.path.split(root)
        
    for d in list:
        dest_node.node_proxy.mkdir(d)

#
def mktempfile(node, prefix=None, suffix=None):
    if node is None:
        fd,filename = tempfile.mkstemp(suffix, prefix)
    else:
        fname = prefix + '.XXXXX'
        temp_file,code = node.node_proxy.exec_cmd('mktemp -t ' + fname)
        filename = temp_file.strip()
    return filename

#
def fetchImage(src, dest):
    print 'Fetching: ' + src
    if src.startswith('http://') or src.startswith('ftp://'):
        urllib.urlretrieve(src, dest)
    else:
        shutil.copyfile(src, dest)

#
def search_tree(tree, key):
    if tree == None or key == None or len(tree) < 1:
        return None
    if type(tree[0]) is str:
        if key == tree[0]:
            if len(tree) > 2:
                return tree[1:]
            return tree[1]
        l = tree[1:]
    else:
        l = tree
        
    for elem in l:
        if type(elem) is list:
            if len(elem) > 0 and elem[0] == key:
                if len(elem) > 2:
                    return elem[1:]
                return elem[1]
            
            if len(elem) >= 2 and type(elem[1]) is list:
                if len(elem) == 2:
                    v = search_tree(elem[1], key)
                    if v is not None:
                        return v
                else:
                    v = search_tree(elem[1:], key)
                    if v is not None:
                        return v


#
def is_host_remote(host):
    host_names = []
    try:
        host_name, host_aliases, host_addrs = socket.gethostbyaddr(host)
        host_names.append(host_name)
        host_names = host_aliases + host_addrs
    except:
        host_names.append(host)
    return len(set(l_names).intersection(set(host_names))) == 0

#
def read_python_conf(conf_file):
    glob = {}
    loc = {}
    if not os.path.exists(conf_file):
        print 'conf file not found :' + conf_file
        return None
    execfile(conf_file, glob, loc)
    vtypes = [types.StringType, types.UnicodeType, types.ListType, types.IntType, types.FloatType, types.DictType]
    for k, v in loc.items():
        if type(v) not in vtypes:
            del loc[k]
            continue
    return loc

#
def guess_value(value):
    # check if it is a number
    if value is None or value == '':
        return value

    if value.isdigit():
        return int(value)

    # check if float
    parts = value.split('.')
    if len(parts) == 2:
        if parts[0].isdigit() and parts[1].isdigit():
            return float(value)

    # check if it is a list
    if value[0] in  ['[' ,'{']:
        g = {}
        l = {}
        cmd = "x = " + value
        exec cmd in g, l
        return l['x']

    # assume it is a string
    return value

#
def fetch_url(url, dest, proxies=None, reporthook=None, data=None, chunk=2048):
    if reporthook:
        raise Exception("reporthook not supported yet")
    
    resp = None
    df = None
    ret = (None, None)
    try:
        if proxies:
            proxy_support = urllib2.ProxyHandler(proxies)
            opener = urllib2.build_opener(proxy_support)
        else:
            opener = urllib2.build_opener()

        req = urllib2.Request(url)
        req.add_header("User-Agent", constants.fox_header)
                       
        if data:
            resp = opener.open(req, data)
        else:
            resp = opener.open(req)

        ret = resp.geturl(),resp.info()
        df = open(dest, "wb")
        data = resp.read(chunk)
        while data:
            try:
                df.write(data)
                data = resp.read(chunk)
            except socket.error, e:
                if (type(e.args) is tuple) and (len(e.args) > 0) and \
                       ((e.args[0] == errno.EAGAIN or e.args[0] == 4)):
                    continue
                else:
                    raise
    finally:
        if df:
            df.close()
        if resp:
            resp.close()

    return ret

#
def fetch_isp(url, dest, content_type):
    retries = 2
    while retries > 0:
        (u, headers) = fetch_url(url, dest)
        retries = retries - 1;
        type =  headers.get("Content-Type")
        if type and type.lower().find(content_type) < 0  :
            print "Retrying ..", type
            continue
        else:
            break

    if type is None:
        raise Exception("Could not fetch %s. Content-Type is None", u)

    if type.lower().find(content_type) < 0 :
        raise Exception("Could not fetch %s. Wrong content type: "+ type )
        
#
def guess_proxy_setup():
    moz_pref_path = os.path.expanduser("~/.mozilla/firefox")
    files = glob.glob(moz_pref_path  + "/*/prefs.js")
    if len(files) > 0:
        pref_file = files[0]
        print pref_file
    else:
        return (None, None)

    prefs = open(pref_file, "r").read().split("\n")

    # get all user_pref lines
    #prefs = re.findall('user_pref("network\.proxy\.(.*)",(.*));', prefs )
    proxy_prefs = {}
    for pref_line in prefs:
        pref = re.findall('user_pref\("network.proxy.(.*)", ?(.*)\);', pref_line )
        if len(pref) > 0 and len(pref[0]) > 1:
            k = pref[0][0]
            v = pref[0][1]
            if v[0] == '"':
                v = v[1:]
            if v[-1] == '"':
                v = v[0:-1]
            proxy_prefs[k] = v

    if proxy_prefs.has_key("type"):
        if proxy_prefs["type"] != "1": # 1 means manual setup of of proxy
            print "type is ", type , " other than manual proxy. None, None"
            return (None, None)
    else:
        print "type is missing. Direct connection. None, None"
        return (None, None)


    http_proxy = None
    if proxy_prefs.has_key("http") and proxy_prefs["http"]:
        http_proxy = "http://"+proxy_prefs["http"]
        if proxy_prefs.has_key("http_port") and proxy_prefs["http_port"]:
            http_proxy += ":" + proxy_prefs["http_port"]
        else:
            http_proxy += ":" + '80'

    ftp_proxy =None
    if proxy_prefs.has_key("ftp") and proxy_prefs["ftp"]:
        ftp_proxy = "http://"+proxy_prefs["ftp"]
        if proxy_prefs.has_key("ftp_port") and proxy_prefs["ftp_port"]:
            ftp_proxy += ":" + proxy_prefs["ftp_port"]
        else:
            ftp_proxy += ":" + '80'

    return http_proxy, ftp_proxy
#
def show_url(url):
    if webbrowser.__dict__.has_key('open_new_tab'):
        webbrowser.open_new_tab(url)
    else:
        webbrowser.open_new(url)

l_names = []
try:
    (local_name, local_aliases,local_addrs) = \
                 socket.gethostbyaddr(constants.LOCALHOST)

    l_names.append(local_name)
    l_names = local_aliases + local_addrs
except socket.herror:
    print "ERROR : can not resolve localhost"
    pass

#
def randomMAC():
    mac = [0, 22, 62, random.randint(0, 127), random.randint(0, 255), random.randint(0, 255)]
    return ':'.join(map((lambda x: '%02x' % x), mac))
#
def randomUUID():
    return [random.randint(0, 255) for _ in range(0, 16)]



#
def uuidToString(u):
    return '-'.join(['%02x%02x%02x%02x', '%02x%02x', '%02x%02x', '%02x%02x', '%02x' * 6]) % tuple(u)

#
def uuidFromString(s):
    s = s.replace('-', '')
    return [ int(s[i : i + 2], 16) for i in range(0, 32, 2) ]

#
def populate_node(info, parent_node, tag, attributes):
    nodes = parent_node.getElementsByTagName(tag)
    if nodes:
        node = nodes[0]
        populate_attrs(info, node, attributes)

#
def populate_attrs(info, node, attributes):
    for key,attr in attributes.iteritems():
        info[key] = node.getAttribute(attr)
#
def getText(parent_node, tag_name):
    nodeist = []
    elems = parent_node.getElementsByTagName(tag_name)
    if elems.length > 0:
        first = elems[0]
        nodeist = first.childNodes
    rc = ''
    for node in nodeist:
        if node.nodeType == node.TEXT_NODE or node.nodeType == node.CDATA_SECTION_NODE:
            rc = rc + node.data
            continue
    return rc
#
def get_path(filename, name_spaces=None):
    for path in (os.path.dirname(sys.argv[0]),'.', '/usr/share/stackone'):
        if name_spaces:
            for ns in name_spaces:
                p = os.path.join(path, ns)
                f = os.path.join(p, filename)
                if os.path.exists(f):
                    return (p, f)
        else:
            f = os.path.join(path, filename)
            if os.path.exists(f):
                return (path,f)
    return (None,None)
#    
def get_platform_defaults(location):
    dir_name = os.path.dirname(location)
    file_name = os.path.join(dir_name, 'defaults')
    return read_python_conf(file_name)
#
def get_prop(map, key, default=None):
    if map.has_key(key):
        return map[key]
    return default
#
def get_config(config):
    globs={}
    locs={}
    lines = []
    lines=config.split('\n')
    options = {}
    try:
        if len(lines) > 0:
            cmd = '\n'.join(lines)
            exec cmd in globs, locs
    except:
        raise
    # Extract the values set by the script and set the corresponding
    # options, if not set on the command line.
    vtypes = [ types.StringType,
               types.UnicodeType,
               types.ListType,
               types.IntType,
               types.FloatType,
               types.DictType
               ]
    for (k, v) in locs.items():
        if not(type(v) in vtypes): continue
        options[k]=v
    return options
    
#
def get_minute_string(minute):
    str_minute = str(minute)
    if minute < 10:
        str_minute = str('0' + str(minute))
    return str_minute
#
def getHexID(name=None, params=None):
    return to_unicode(uuidToString(randomUUID()))
#
def getDateTime(dateval,timeval):
    if dateval is None or timeval is None:
        return None
    print dateval,"==============",timeval
    months={
        'Jan':1,
        'Feb':2,
        'Mar':3,
        'Apr':4,
        'May':5,
        'Jun':6,
        'Jul':7,
        'Aug':8,
        'Sep':9,
        'Oct':10,
        'Nov':11,
        'Dec':12,
    }
    dateparts=dateval.split(" ")
    timeparts=timeval.split(":")
    print dateparts[1],"--",dateparts[2],"---",dateparts[3],"----"
    utcnow=datetime.now()
    now=datetime.now()
    diff=utcnow-now

    sel=datetime(int(dateparts[3]),months[dateparts[1]],int(dateparts[2]),\
            int(timeparts[0]),int(timeparts[1]))
    return sel+diff
    
    
#
def print_traceback():
    traceback.print_exc()

#
def populate_node_filter(managed_node, platform, image):
    if managed_node is not None:
        if platform:
            if managed_node.get_platform() != platform or not managed_node.is_authenticated():
                return False

        if image:
            if not managed_node.is_authenticated() or not managed_node.is_image_compatible(image):
                return False
                
    return True

def vm_config_write(auth, context, image_id, v_config, i_config, img_name):
    try:
        is_remote_list = []
        s_stats = v_config.get_storage_stats()
        for de in v_config.getDisks():
            r = s_stats.get_remote(de.filename)
            is_remote_list.append(r)
        img_location = context.image_store.get_image(auth, image_id).location
        if img_location:
            img_location = os.path.basename(img_location)
        instantiate_configs(context.managed_node, context.image_store, img_name, img_location, v_config, i_config)
        store = context.image_store
#        managed_node = DBSession.query(ManagedNode).filter(ManagedNode.id == context.managed_node.id).first()
        managed_node = context.managed_node    
        vm_config_file = v_config.filename
        v_config['image_name'] = img_name
        v_config['image_id'] = image_id
        v_config['config_filename'] = v_config.filename
        v_config['platform'] = managed_node.get_platform()
        v_config.set_managed_node(managed_node)
        change_file_2_tap = False
        is_hvm_image = context.image_store.get_image(auth, image_id).is_hvm()
        if v_config['platform'] == 'xen' and not is_hvm_image:
            change_file_2_tap = True
        changed = False
        changed_disks = []
        ndx = 0
        ll = len(is_remote_list)
        s_stats = v_config.get_storage_stats()
        for de in v_config.getDisks():
            if de and de.type == 'file' and change_file_2_tap:
                pv_driver = v_config.get(constants.default_xen_pv_driver)
                if pv_driver is None:
                    pv_driver = 'tap:aio'
                de.type = pv_driver
                changed = True
            changed_disks.append(repr(de))
            r = None
            if ndx < ll:
                r = is_remote_list[ndx]
            s_stats.set_remote(de.filename, r)
            ndx += 1
        if changed:
            print 'Updating disk to new value : for tap:aio',
            print changed_disks
            v_config['disk'] = changed_disks
        v_config.write()
        return (store, managed_node, vm_config_file, v_config)
    except Exception as e:
        raise e

#
def instantiate_configs(managed_node, image_store, image_name, image_location, vm_config, image_config):
    try:
        template_map = fv_map()
        store_location = image_store.get_remote_location(managed_node)
        template_map['IMAGE_STORE'] = store_location
        template_map['IMAGE_NAME'] = image_name
        template_map['IMAGE_LOCATION'] = image_location
        template_map['VM_NAME'] = vm_config['name']
        template_map['SERVER_NAME'] = managed_node.hostname
        def_bridge = 'xenbr0'
        if managed_node.platform == 'kvm':
            def_bridge = 'br0'
        bridge = managed_node.get_default_bridge()
        if bridge:
            print 'setting default bridge from discoverd information',
            print bridge
            def_bridge = bridge
        else:
            if image_config['DEFAULT_BRIDGE']:
                def_bridge = image_config['DEFAULT_BRIDGE']
        template_map['DEFAULT_BRIDGE'] = def_bridge
        template_map['AUTOGEN_MAC'] = randomMAC
        image_config.instantiate_config(template_map)
        vm_config.instantiate_config(template_map)
        if image_config is not None:
            vm_config.instantiate_config(image_config)
    except Exception as e:
        import traceback
        traceback.print_exc()
        raise e
    return None

#
def merge_pool_settings(vm_config, image_config, pool_settings, append_missing=False):
    gconfig = {}
    for key in pool_settings:
        gconfig[key] = pool_settings[key]
    for key in vm_config:
        if key in gconfig:
            vm_config[key] = gconfig[key]
            del gconfig[key]
            continue
            
    for key in image_config:
        if key in gconfig:
            image_config[key] = gconfig[key]
            del gconfig[key]
            continue
            
    if append_missing is True:
        for key in gconfig:
            image_config[key] = gconfig[key]

#pass
def validateVMSettings(mode,managed_node,image_store,vm_name,memory,vcpus):
    errmsgs = []
    value = memory
    try:
        if memory is not None:
            value = int(value)
    except:
        errmsgs.append("Specify a proper integer value for the Memory.")
    value = vcpus
    try:
        if vcpus is not None:
            value = int(value)
    except:
        errmsgs.append("Specify a proper integer value for the VirtualCPUs.")
    if mode != "EDIT_IMAGE":
        if mode == "PROVISION_VM" and managed_node.is_resident(vm_name):
            errmsgs.append("Running VM with the same name exists.")

        if vm_name:
            x = vm_name
            if re.sub(managed_node.get_vm_invalid_chars_exp(),"", x) != x:
                errmsgs.append("VM name can not contain special chars %s" % managed_node.get_vm_invalid_chars())

    return errmsgs
#
def get_platform_count(ids=None):
    from stackone.model import DBSession, ManagedNode
    query = DBSession.query(ManagedNode.type, func.count(ManagedNode.id)).group_by(ManagedNode.type)
    if ids is not None:
        query = query.filter(ManagedNode.id.in_(ids))
    result = query.all()
    return result

#
def get_host_os_info(ids=None):
    from stackone.model import DBSession, Instance
    query = DBSession.query(Instance.value, func.count(Instance.name)).filter(Instance.name.in_([u'distro_string'])).filter(Instance.node_id != None).group_by(Instance.value)
    if ids is not None:
        query = query.filter(Instance.node_id.in_(ids))
    result = query.all()
    return result

#
def get_guest_os_info(ids=None):
    from stackone.model import DBSession
    from stackone.model.VM import VM
    query = DBSession.query(VM.os_name, VM.os_version, func.count(VM.os_version)).group_by(VM.os_name, VM.os_version)
    if ids is not None:
        query = query.filter(VM.id.in_(ids))
    result = query.all()
    x = 0
    os_list = []
    for item in result:
        if item[0] == None or item[0] == 'None' or item[0] == '' or item[1] == None or item[1] == 'None' or item[1] == '':
            x += 1
            continue
            
        os_list.append((item[0] + ' ' + item[1], item[2]))
    
    if x > 0:
        os_list.append(('Unknown', x))
    return os_list

#
def get_string_status(value):
    ret_val = ''
    if value in [0L, False, str(False)]:
        ret_val = 'no'
    else:
        if value in [1L, True, str(True)]:
            ret_val = 'yes'
        else:
            ret_val = 'n/a'
    return ret_val
#
def update_vm_status():
    from stackone.model import DBSession
    from stackone.model.VM import VM
    import transaction
    doms = DBSession.query(VM).all()
    for dom in doms:
        if dom.status == constants.MIGRATING:
            print 'changing status of VM ',
            print dom.name,
            print ' from ',
            print constants.MIGRATING,
            print " to ''"
            dom.status = ''
            continue
            
    transaction.commit()
#
def get_template_versions(image_id):
    from stackone.model import DBSession
    from stackone.model.ImageStore import Image
    result = []
    if image_id is not None:
        query = DBSession.query(Image.version).filter(Image.prev_version_imgid == image_id).order_by(Image.version.asc())
        result = query.all()
    return result

#
def notify_node_down(node_ent, reason):
    try:
        LOGGER.info('Sending Node down notification...')
        now = datetime.now()
        subject = u'stackone : Server ' + node_ent.name + ' not reachable'
        message = '\n<br/>CMS detected a server down. '
        message += '\n<br/>Server Name    : ' + node_ent.name
        message += '\n<br/>Detected At    : ' + to_str(now)
        message += '\n<br/>Reason         : ' + to_str(reason)
        send_user_notification(subject, message, node_ent)
        LOGGER.info('Sending Node Down Notification to LDAP Users...')
        notify_ldap_users(node_ent, subject, message)
        LOGGER.info('Sent Node Down Notifications.')
    except Exception as e:
        traceback.print_exc()
        LOGGER.error(e)
#
def notify_task_hung(task, node):
    try:
        LOGGER.info('Sending Task hung notification...')
        now = datetime.now()
        subject = u'stackone : Task' + str(task.name) + ' is hung'
        message = '\n<br/>Task ' + str(task.name) + '(' + str(task.task_id) + ') is hung'
        message += '\n<br/>Host Name    : ' + node.hostname
        message += '\n<br/>Time         : ' + str(now)
        from stackone.model import DBSession
        from stackone.model.Entity import Entity
        node_ent = DBSession.query(Entity).filter(Entity.entity_id == node.id).first()
        send_user_notification(subject, message, node_ent)
        LOGGER.info('Sending Task hung notification to LDAP Users...')
        notify_ldap_users(node_ent, subject, message)
        LOGGER.info('Sending Task hung notification.')
    except Exception as e:
        traceback.print_exc()
        LOGGER.error(e)
#
def send_user_notification(subject, message, node_ent):
    try:
        from stackone.model import DeclarativeBase, DBSession, Group
        from stackone.model.notification import Notification
        from stackone.model.Authorization import AuthorizationService
        now = datetime.now()
        grp = Group.by_group_name(to_unicode('adminGroup'))
        for user in grp.users:
            notifcn = Notification(None, None, now, to_unicode(message), user.user_name, user.email_address, subject)
            DBSession.add(notifcn)
        users = AuthorizationService.get_all_users(node_ent)
        for user in users:
            if user not in grp.users:
                notifcn = Notification(None, None, now, to_unicode(message), user.user_name, user.email_address, subject)
                DBSession.add(notifcn)
                continue
    except Exception as e:
        traceback.print_exc()
        LOGGER.error(e)
    return None

#
def notify_annotation(node_ent, message):
    try:
        LOGGER.info('Sending Annotation notification...')
        from stackone.model import DeclarativeBase, DBSession, Group
        from stackone.model.notification import Notification
        from stackone.model.Authorization import AuthorizationService
        users = AuthorizationService.get_all_users(node_ent)
        subject = u'stackone :Annotation Status- ' + node_ent.type.display_name + ' : ' + node_ent.name
        now = datetime.now()
        entity_details = node_ent.type.display_name + ' : ' + node_ent.name + '\n\n'
        message = entity_details + message
        message = message.replace('\n', '<br/>').replace(' ', '&nbsp;')
        for user in users:
            notifcn = Notification(None, None, now, to_unicode(message), user.user_name, user.email_address, subject)
            DBSession.add(notifcn)
        LOGGER.info('Sending Annotation Notification to LDAP Users...')
        notify_ldap_users(node_ent, subject, message)
        LOGGER.info('Sent Annotation Notification.')
    except Exception as e:
        traceback.print_exc()
        LOGGER.error(e)
    return None

#
def notify_ldap_users(node_ent, subject, message):
    try:
        from stackone.model import DeclarativeBase, DBSession, Group
        from stackone.model.notification import Notification
        from stackone.model.Authorization import AuthorizationService
        from stackone.model.LDAPManager import LDAPManager
        enabled = eval(tg.config.get('ldap_enabled', 'False'))
        now = datetime.now()
        if not enabled:
            LOGGER.info('LDAP is not Enabled')
        else:
            LOGGER.info('LDAP is Enabled')
            LOGGER.info('Finding LDAP users for send Notification......')
            reps = AuthorizationService().get_all_rep(node_ent)
            role_ids = [rep.role_id for rep in reps]
            groups = AuthorizationService.get_all_groups(role_ids)
            group_names = [group.group_name for group in groups]
            LOGGER.info('LDAP User Notification: Groups of entity:%s, %s' % (node_ent.name, group_names))
            group_key = tg.config.get('group_key', 'groups')
            email_key = tg.config.get('email_key', 'email')
            if not len(group_names):
                LOGGER.info('Roles of entity:%s did not attached to any groups.' % node_ent.name)
            else:
                for group in group_names:
                    users = LDAPManager().get_all_user(group)
                    for user in users:
                        LOGGER.info('Sending Notification to User:%s Email Ids:%s' % (user[user_key], user[email_key]))
                for email_address in user[email_key]:
                    notifcn = Notification(None, None, now, to_unicode(message), user[user_key], email_address, subject)
                    DBSession.add(notifcn)
            LOGGER.info('Sent Notification to LDAP Users.')
    except Exception as e:
        traceback.print_exc()
        LOGGER.error(e)
    return None

#add 0901
##########pass
def update_deployment_status():
    from stackone.model import DBSession, Deployment
    deps = DBSession.query(Deployment).all()
    if len(deps) > 0:
        try:
            from stackone.viewModel import Basic
            src_script_dir = os.path.abspath(tg.config.get('common_script'))
            dist_script_fie = 'deltect_distro.sh'
            src_script_fie = os.path.join(src_script_dir, dist_script_fie)
            loc_node = Basic.getManagedNode()
            output,exit_code = loc_node.node_proxy.exec_cmd(src_script_fie)
            # as exit_code
            if exit_code == 0:
                distro_info = output.split(';version=')
                distro_name = distro_info[0].replace('name=', '')
                distro_ver = distro_info[1].replace('\n', '')
            memory_values = get_mem_info(loc_node)
            cpu_values = get_cpu_info(loc_node)
            mem = float(memory_values.get(constants.key_memory_total))
            cpu = int(cpu_values.get(constants.key_cpu_count, 1))
            soc = loc_node.get_socket_info()
            cor = cpu
            if soc:
                cor = cpu * soc
            ent_type_count = {}
            ent_types = [to_unicode(constants.SERVER_POOL), to_unicode(constants.MANAGED_NODE), to_unicode(constants.DOMAIN), to_unicode(constants.IMAGE_GROUP), to_unicode(constants.IMAGE)]
            from stackone.model import Entity, EntityType
            from stackone.model.auth import User
            from stackone.model.network import Nwdef
#            from stackone.model.storage import Storagedef
            from stackone.core.platforms.xen.XenNode import XenNode
            from stackone.core.platforms.kvm.KVMNode import KVMNode
            from stackone.model.ManagedNode import ManagedNode
            from stackone.model.VM import VM
            result = DBSession.query(EntityType.name, func.count(Entity.name)).join(Entity).group_by(EntityType.name).fiter(EntityType.name.in_(ent_types)).all()
            dep = deps[0]
            ent_type_count = dict(result)
            if dep.max_sp < ent_type_count.get(constants.SERVER_POOL, 0L):
                dep.max_sp = ent_type_count.get(constants.SERVER_POOL)
            if dep.max_server < ent_type_count.get(constants.MANAGED_NODE, 0L):
                dep.max_server = ent_type_count.get(constants.MANAGED_NODE)
            if dep.max_vm < ent_type_count.get(constants.DOMAIN, 0L):
                dep.max_vm = ent_type_count.get(constants.DOMAIN)
            if dep.max_tg < ent_type_count.get(constants.IMAGE_GROUP, 0L):
                dep.max_tg = ent_type_count.get(constants.IMAGE_GROUP)
            if dep.max_template < ent_type_count.get(constants.IMAGE, 0L):
                dep.max_template = ent_type_count.get(constants.IMAGE)
            dep.sps = ent_type_count.get(constants.SERVER_POOL, 0L)
            dep.templates = ent_type_count.get(constants.IMAGE, 0L)
            x = DBSession.query(func.count(User.user_id)).all()
            dep.users = x[0L][0L]
            x = DBSession.query(func.count(NwDef.id)).all()
            dep.networks = x[0L][0L]
            x = DBSession.query(func.count(StorageDef.id)).all()
            dep.storages = x[0L][0L]
#            x = DBSession.query(func.count(XenNode.id)).all()
#            dep.xen_server = x[0L][0L]
            x = DBSession.query(func.count(KVMNode.id)).all()
            dep.kvm_server = x[0L][0L]
            x = DBSession.query(func.count(VM.id)).all()
            dep.vms = x[0L][0L]
            nodes = DBSession.query(ManagedNode).all()
            tot_sockets = 0L
            tot_cores = 0L
            tot_mem = 0L
            for n in nodes:
                cpu = 1
                mem = 0
                tot_sockets += n.socket
    
                try:
                    cpu = n.get_cpu_db()
                    mem = n.get_mem_db()
                except Exception as e:
                    print 'Error getting cpu/mem info for node ' + n.hostname
                    import traceback
                    traceback.print_exc()
                tot_cores += cpu * n.socket
                tot_mem += mem
            dep.tot_sockets = tot_sockets
            dep.tot_cores = tot_cores
            dep.tot_mem = tot_mem
            dep.distro_name = to_unicode(distro_name)
            dep.distro_ver = to_unicode(distro_ver)
            dep.host_mem = mem
            dep.host_cores = cor
            dep.host_sockets = soc
            DBSession.add(dep)
        except Exception as e:
            import traceback
            traceback.print_exc()

#def update_deployment_status():
#    from stackone.model import DBSession, Deployment
#    deps = DBSession.query(Deployment).all()
#    if len(deps) > 0:
#        ent_type_count = {}
#        ent_types = [to_unicode(constants.SERVER_POOLL), to_unicode(constants.MANAGED_NODE), to_unicode(constants.DOMAIN), to_unicode(constants.IMAGE_GROUP), to_unicode(constants.IMAGE)]
#        from stackone.model import Entity, EntityType
#        result = DBSession.query(EntityType.name, func.count(Entity.name)).join(Entity).group_by(EntityType.name).filter(EntityType.name.in_(ent_types)).all()
#        dep = deps[0]
#        ent_type_count = dict(result)
#        if dep.max_sp < ent_type_count.get(constants.SERVER_POOLL, 0):
#            dep.max_sp = ent_type_count.get(constants.SERVER_POOLL)
#        if dep.max_server < ent_type_count.get(constants.MANAGED_NODE, 0):
#            dep.max_server = ent_type_count.get(constants.MANAGED_NODE)
#        if dep.max_vm < ent_type_count.get(constants.DOMAIN, 0):
#            dep.max_vm = ent_type_count.get(constants.DOMAIN)
#        if dep.max_tg < ent_type_count.get(constants.IMAGE_GROUP, 0):
#            dep.max_tg = ent_type_count.get(constants.IMAGE_GROUP)
#        if dep.max_template < ent_type_count.get(constants.IMAGE, 0):
#            dep.max_template = ent_type_count.get(constants.IMAGE)
#        DBSession.add(dep)
#
#add 0907

#####tianfeng
def get_cpu_info(mgd_node):
    cpu_attributes = [constants.key_cpu_count, constants.key_cpu_vendor_id, constants.key_cpu_model_name, constants.key_cpu_mhz]
    cpu_values = mgd_node.node_proxy.exec_cmd('cat /proc/cpuinfo | grep "processor" | wc -l;' + 'cat /proc/cpuinfo | grep "vendor*" | head -1 | cut -d\':\' -f2;' + 'cat /proc/cpuinfo | grep "model na*" | head -1 | cut -d\':\' -f2;' + 'cat /proc/cpuinfo | grep "cpu MHz*" | head -1 | cut -d\':\' -f2;')[0L].split('\n')[:-1L]
    cpu_dict = {}
    for x in range(len(cpu_attributes)):
        cpu_dict[cpu_attributes[x]] = cpu_values[x]
    return cpu_dict
#tianfeng
def get_mem_info(mgd_node):
    memory_attributes = [constants.key_memory_total, constants.key_memory_free]
    memory_values = []
    memory_values = mgd_node.node_proxy.exec_cmd('cat /proc/meminfo | grep "Mem*" | cut -d\':\' -f2')[0L].split('\n')[:-1L]
    memory_values = [int(re.search('(\\d+)(\\s+)(\\S+)',v.strip()).group(1))/1000 for v in memory_values]
    memory_dict = {}
    for x in range(len(memory_attributes)):
        memory_dict[memory_attributes[x]] = memory_values[x]
    return memory_dict

    # def get_mem_info(mgd_node):
    # memory_attributes = [constants.key_memory_total, constants.key_memory_free]
    # memory_values = []
    # memory_values = mgd_node.node_proxy.exec_cmd('cat /proc/meminfo | grep "Mem*" | cut -d\':\' -f2')[0L].split('\n')[:-1L]
    # memory_values = [int(re.search('(\\d+)(\\s+)(\\S+)',v.strip()).group(1))/1000 for v in memory_values]
    # memory_dict) = <genexpr>(range(len(memory_attributes)))
    # return memory_dict
def get_cms_network_service_node():
    try:
        from stackone.model import DBSession
        from stackone.model.Entity import Entity, EntityType
        from stackone.model.ManagedNode import ManagedNode
        from stackone.model.NetworkServiceNode import CMSNetworkServiceNode
        hostname = tg.config.get('nw_service_host', '')
        username = 'root'
        password = tg.config.get('nw_service_root_password', '')
        sshport = tg.config.get('nw_service_ssh_port', '')
        if not hostname:
            print 'CMS Network Service Host is not configured .'
            return None
        node = DBSession.query(ManagedNode).filter(ManagedNode.hostname == hostname).first()
        if node:
            print 'CMS Network Service Host is Managed Server :' + hostname + ', ' + node.type
            return node
            
        cms_node = DBSession.query(CMSNetworkServiceNode).first()
        if cms_node:
            cms_node.update_node(hostname=hostname, ssh_port=sshport, username=username, password=password, address=hostname)
            DBSession.query(Entity).filter(Entity.entity_id == cms_node.id).update(values=dict(name=hostname))
            print 'CMS Network Service Host updated :' + hostname
        else:
            if password == None:
                use_keys = hostname != 'localhost'
            else:
                use_keys = password == None
            is_remote = hostname != 'localhost'
            if sshport:
                sshport = int(sshport)
                
            cms_node = CMSNetworkServiceNode(hostname=hostname, ssh_port=sshport, username=username, password=password, isRemote=is_remote, helper=None, use_keys=use_keys, address=hostname)
            type = DBSession.query(EntityType).filter(EntityType.name == constants.MANAGED_NODE).first()
            e = Entity()
            e.name = hostname
            e.type = type
            e.entity_id = cms_node.id
            DBSession.add(e)
            print 'CMS Network Service Host added :' + hostname
        
        import transaction
        DBSession.add(cms_node)
        transaction.commit()
        return DBSession.query(CMSNetworkServiceNode).first()
    except Exception as ex:
        import traceback
        traceback.print_exc()
        raise ex
    return None

#
def populate_custom_fence_resources(local_node, commit=False):
    resources = []
    try:
        from stackone.core.ha.ha_fence import HAFenceResourceTypeMeta, HAFenceResourceType
        from stackone.model import DBSession
        fence_loc = os.path.abspath(tg.config.get('custom_fencing_scripts'))
        metadata_loc = os.path.join(fence_loc, 'metadata')
        scripts_loc = os.path.join(fence_loc, 'scripts')
        custom_entries = local_node.node_proxy.get_dir_entries(metadata_loc)
        ex_resources = DBSession.query(HAFenceResourceType).filter(HAFenceResourceType.meta_source != None).all()
        meta_sources = [r.meta_source for r in ex_resources]
        for entry in custom_entries:
            meta_source = entry['path']
            if entry['isdir'] != True and meta_source not in meta_sources:
                fence_config = PyConfig(filename = meta_source)
                opts = fence_config.options
                filename = opts['filename']
                cls = opts.get('classification')
                desc = opts.get('description')
                file = os.path.join(scripts_loc, filename)
                resource = HAFenceResourceType(to_unicode(opts['name']), to_unicode(opts['display_name']), to_unicode(opts['cmd']), to_unicode(file), to_unicode(meta_source), to_unicode(cls), to_unicode(desc))
                i = 1
                device_attrs = opts.get('device_attrs')
                if device_attrs:
                    for dev in device_attrs:
                        meta = HAFenceResourceTypeMeta(
                            to_unicode(dev['name']),
                            to_unicode(dev['display_name']),
                            to_unicode(dev['componenttype']),
                            to_unicode(dev['datatype']),
                            'sequence',
                            i,
                            values = dev.get('values')
                        )
                        i += 1
                        meta.is_resource = True
                        resource.meta.append(meta)
                
                i = 1
                instance_attrs = opts.get('instance_attrs')
                if instance_attrs:
                    for inst in instance_attrs:
                        meta = HAFenceResourceTypeMeta(
                            to_unicode(inst['name']),
                            to_unicode(inst['display_name']),
                            to_unicode(inst['componenttype']),
                            to_unicode(inst['datatype']),
                            'sequence',
                            i, 
                            values = inst.get('values')
                        )
                        i += 1
                        meta.is_instance = True
                        resource.meta.append(meta)
                
                meta = HAFenceResourceTypeMeta(
                    to_unicode('action'),
                    to_unicode('Action'),
                    to_unicode('combobox'),
                    to_unicode('text'),
                    'sequence',
                    i,
                    values = to_unicode("[['on', 'On'],['off','Off'],['reboot','Reboot']]")
                )
                
                i += 1
                meta.is_instance = True
                resource.meta.append(meta)
                
                environ_attrs = opts.get('environ_attrs')
                if environ_attrs:
                    for inst in environ_attrs:
                        meta = HAFenceResourceTypeMeta(
                            to_unicode(inst['name']),
                            to_unicode(inst['display_name']),
                            to_unicode(inst['componenttype']),
                            to_unicode(inst['datatype']),
                            'sequence',
                            i,
                            values = inst.get('values')
                        )
                        i += 1
                        meta.is_environ = True
                        resource.meta.append(meta)
                resources.append(resource)
            continue
        if commit == True:
            import transaction
            DBSession.add_all(resources)
            transaction.commit()
    except Exception as ex:
        import traceback
        traceback.print_exc()

    return resources

#
def reset_transient_state():
    try:
        import transaction
        from stackone.model.availability import AvailState
        from stackone.model import DBSession
        from stackone.viewModel.BackupService import BackupService
        from stackone.viewModel.RestoreService import RestoreService
        DBSession.query(AvailState).update(values=dict(transient_state=None))
        transaction.commit()
    except Exception as ex:
        import traceback
        traceback.print_exc()
        raise ex
    return None

#
def init_firewall_for_all_csep():
    try:
        from stackone.model.FirewallManager import FirewallManager
        fw_manager = FirewallManager.get_manager()
        fw_manager.init_firewall_for_all_csep()
    except Exception as ex:
        import traceback
        traceback.print_exc()
        raise ex

#
def storage_stats_data_upgrade():
    try:
        from stackone.model.storage import StorageManager
        StorageManager().storage_stats_data_upgrade()
    except Exception as ex:
        import traceback
        traceback.print_exc()
        raise ex
#
def unreserve_disks_on_cms_start():
    try:
        from stackone.viewModel import Basic
        grid_manager = Basic.getGridManager()
        grid_manager.unreserve_disks_on_cms_start()
    except Exception as ex:
        import traceback
        traceback.print_exc()
        raise ex

#
def setup_ssh_keys(node,local_node):
    try:
        ssh_key_file=tg.config.get(constants.ssh_file)
        if ssh_key_file is None:
            ssh_key_file="~/.ssh/id_rsa"
        ssh_key_file=os.path.expanduser(ssh_key_file)
        key=""
        ssh_dir="/"+node.username+"/.ssh"
        ssh_file_exist=local_node.node_proxy.file_exists(ssh_key_file+".pub")
        if ssh_file_exist:
            ssh_key=None
            f = open(ssh_key_file+".pub")
            key=f.readline()
            if key and len(key) > 1:
                if key[-1] == '\n':
                    key = key[:-1]
                ssh_key=key.split(" ")
            (retbuf, retcode)=local_node.node_proxy.exec_cmd("ssh-add -L | grep \""+ssh_key[1]+"\" ")
            if retcode==0:
                LOGGER.info("key existing in ssh command")
                auth_key_file = os.path.join(ssh_dir, "authorized_keys")
                file_exist=node.node_proxy.file_exists(auth_key_file)
                retcode=None
                if file_exist:
                    cmd="grep \""+key+"\" "+auth_key_file
                    (retbuf, retcode)=node.node_proxy.exec_cmd(cmd)
                if not file_exist or retcode ==1:
                    #newcmd = "umask 077; test -d ~/.ssh || mkdir ~/.ssh ; echo \""+key+"\"  >> "+auth_key_file
                    newcmd = "umask 077; test -d ~/.ssh || mkdir ~/.ssh ; echo \""+key+"\"  >> "+auth_key_file + "; test -x /sbin/restorecon && /sbin/restorecon ~/.ssh ~/.ssh/authorized_keys"
                    (retbuf, retcode)=node.node_proxy.exec_cmd (newcmd)
                    if retcode ==0:
                        print "key added"
                        LOGGER.info("key added to the managed server")
        else:
            LOGGER.error("ssh key file "+ssh_key_file+" not found")
    except Exception ,ex:
        traceback.print_exc()
        err=to_str(ex).replace("'", " ")
        LOGGER.error(":"+err)

#
def set_sp_dwm_policies():
    try:
        import transaction
        from stackone.model import DBSession
        from stackone.model.Groups import ServerGroup
        from stackone.model.DWM import DWMManager, DWM, SPDWMPolicy
        from stackone.model.auth import User
        from stackone.model.Authorization import AuthorizationService
        adm_usr = DBSession.query(User).filter(User.user_name == u'admin').first()
        auth = AuthorizationService(adm_usr)
        groups = DBSession.query(ServerGroup).all()
        LOGGER.info('RESUME: Entered in resume operation to start nodes which are shutdown during %s or can not start at the end of %s' % (DWMManager.POWER_SAVING, DWMManager.POWER_SAVING))
        for group in groups:
            if group.is_dwm_enabled() == False:
                LOGGER.debug('RESUME: DWM is not enabled for ServerPool:%s' % group.name)
                print 'RESUME: DWM is not enabled for ServerPool:%s' % group.name
                continue
                
            dwm = DWM.find_current_policy(group.id)
            if dwm:
                LOGGER.debug('RESUME: DWM is enabled for ServerPool:%s' % group.name)
                SPDWMPolicy.set_sp_current_policy(group.id, dwm.policy, SPDWMPolicy.ON)
                policy = dwm.policy
                LOGGER.debug('RESUME: Current DWM policy of ServerPool:%s is %s' % (group.name, policy))
                if policy not in [DWMManager.POWER_SAVING]:
                    SPDWMPolicy.ps_start_down_nodes(auth, group.id)
                    LOGGER.info('RESUME %s: Started down nodes in ServerPool:%s' % (DWMManager.POWER_SAVING, group.name))

                LOGGER.debug('RESUME: Current DWM policy of ServerPool:%s is %s, So dont need to start nodes which are shutdown during %s' % (group.name, policy, policy))
                continue

            LOGGER.debug('RESUME: This time no DWM policy is active for ServerPool:%s' % group.name)
            SPDWMPolicy.set_sp_none_policy(group.id)

        transaction.commit()
    except Exception as ex:
        import traceback
        traceback.print_exc()
        raise ex


#
def process_value(value):
    if value is None or value == '':
        return value
    str_value = to_str(value)
    if str_value[0] in ('[',):
        temp = []
        for val in value:
            temp.append(to_str(val))
        return temp
    elif str_value[0] in ('{',):
        temp1 = {}
        for key in value:
            parts = to_str(value.get(key)).split('.')
            if to_str(value.get(key)).isdigit():
                temp1[to_str(key)] = int(value.get(key))
            elif len(parts) == 2 and parts[0].isdigit() and parts[1].isdigit():
                temp1[to_str(key)] = float(value.get(key))
            else:
                temp1[to_str(key)] = to_str(value.get(key))
        return temp1
        
    return value
#
def get_config_text(config):
    str_config = ''
    for name, value in config.iteritems():
        str_config += '%s = %s\n' % (name, repr(value))
    return str_config
#
class dummyStream():
    def __init__(self):
        pass

    def write(self, data):
        pass

    def read(self, data):
        pass

    def flush(self):
        pass

    def close(self):
        pass


#
def get_cms_stacktrace():
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("<br/><br/>\n# ThreadID: %s<br/>" % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s<br/>' % (filename, lineno, name))
            if line:
                code.append("  %s<br/>" % (line.strip()))
    return ("\n".join(code)) 
#
def get_cms_stacktrace_fancy():
    from pygments import highlight
    from pygments.lexers import PythonLexer
    from pygments.formatters import HtmlFormatter
    code = []
    for threadId, stack in sys._current_frames().items():
        code.append("\n# ThreadID: %s" % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            code.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                code.append("  %s" % (line.strip()))
    return highlight("\n".join(code), PythonLexer(), HtmlFormatter(
      full=False,
      # style="native",
      noclasses=True,
    ))
    
#
def get_product_edition():
    from stackone.model.LicenseManager import get_db_license_info
    lise = get_db_license_info()
    return lise['pe']
#
def get_ldap_module():
    import ldap
    return ldap
#
if __name__ == '__main__':
    REMOTE_HOST = '192.168.123.155'
    REMOTE_USER = 'root'
    REMOTE_PASSWD = ''
    REMOTE = False
    local_node = Node(hostname=constants.LOCALHOST)
    if not REMOTE:
        remote_node = local_node
    else:
        remote_node = Node(hostname=REMOTE_HOST, username=REMOTE_USER, password=REMOTE_PASSWD, isRemote=True)
    lvm_local = LVMProxy(local_node)
    lvm_remote = LVMProxy(remote_node)
    lvm_remote = lvm_local
    print '\nLVMProxy interface test STARTING'
    for lvm in (lvm_local, lvm_remote):
        vgs = lvm.listVolumeGroups()
        for g in vgs:
            print g
            print lvm.listLogicalVolumes(g)
            print '\t Creating test LV'
            lvm.createLogicalVolume('selfTest', 0.10000000000000001, g)
            print '\t Deleting test LV'
            lvm.removeLogicalVolume('selfTest', g)
    print 'LVMPRoxy interface test COMPLETED\n'
    TEST_CONFIGFILE = '/foo/stackone.conf'
    print '\nXMConfig interface test STARTING\n'
    print 'LOCALHOST ...'
    config_local = XMConfig(local_node, searchfiles=[TEST_CONFIGFILE], create_file=TEST_CONFIGFILE)
    config_local.set(XMConfig.DEFAULT, 'TEST_PROP', 'TEST_VAL')
    print 'Default Property TEST_PROP:',
    print config_local.getDefault('TEST_PROP')
    print 'Default Sections:',
    print config_local.sections()
    print 'Known Hosts',
    print config_local.getHosts()
    config_local2 = XMConfig(local_node, searchfiles=[TEST_CONFIGFILE])
    print 'Default Property TEST_PROP:',
    print config_local2.getDefault('test_prop')
    local_node.remove(TEST_CONFIGFILE)
    print '\nREMOTE HOST ...'
    config_remote = XMConfig(remote_node, searchfiles=[TEST_CONFIGFILE], create_file=TEST_CONFIGFILE)
    config_remote.setDefault('TEST_PROP', 'TEST_VAL')
    print 'Default Property TEST_PROP:',
    print config_remote.get(XMConfig.DEFAULT, 'TEST_PROP')
    print 'Default Sections:',
    print config_remote.sections()
    print 'Known Hosts',
    print config_remote.getHosts()
    config_remote2 = XMConfig(remote_node, searchfiles=[TEST_CONFIGFILE])
    print 'Default Property TEST_PROP:',
    print config_remote2.getDefault('test_prop')
    remote_node.remove(TEST_CONFIGFILE)
    print '\nXMConfig interface test COMPLETED'
    print '\nImageStore interface test COMPLETED'
    sys.exit(0)
    
#pass
def util_provision_vm(auth, image_store, image, image_id, eGroup, managed_node, storage_manager, vname, memory, vcpus):
    ctx = dynamic_map()
    ctx.image_store = image_store
    ctx.image = image
    ctx.image_id = image_id
    ctx.managed_node = managed_node
    ####archer 20130205
    ctx.preferred_nodeid = managed_node.id
    ctx.vm = None
    ctx.server_pool = eGroup
    ctx.platform = managed_node.get_platform()
    ctx.storage_manager = storage_manager
    vm_config,image_config = image.get_configs(ctx.platform)
    if ctx.server_pool is not None:
        grp_settings = ctx.server_pool.getGroupVars()
        merge_pool_settings(vm_config, image_config, grp_settings, True)
        vm_config.instantiate_config(image_config)
    vm_config['name'] = vname
    if memory is not None:
        vm_config['memory'] = memory
    if vcpus is not None:
        vm_config['vcpus'] = vcpus
    vm_config_path = os.path.join('$VM_CONF_DIR', vname)
    vm_config.set_filename(vm_config_path)
    ctx.vm_config = vm_config
    ctx.image_config = image_config
    return ctx

#
def check_constraints(dom, node):
    status = False
    msg = ('Constraints of ', dom.name, ' on ', node.hostname)
    err_list = []
    err = ''
    mem_status = ''
    cpu_status = ''
    storage_status = ''
    network_status = ''
    mem_status,err = do_memory_check(dom, node)
    err_list.append(err)
    cpu_status,err = do_cpu_check(dom, node)
    err_list.append(err)
    storage_status,err = do_storage_check(dom, node)
    err_list.append(err)
    network_status,err = do_network_check(dom, node)
    err_list.append(err)
    if node.is_dom_compatible(dom) and mem_status and cpu_status and storage_status and network_status:
        status = True
        msg = ' are successful'
    else:
        msg = (' failed', to_str(err_list))
    LOGGER.info(msg)
    print 'MESSAGEEEEEE======',
    print msg
    return status

#
def do_memory_check(dom, node):
    print '\n\nMEMORYYYYYYYYYY'
    err = ''
    result = False
    free_mem = 0
    try:
        free_mem = int(node.get_memory_info().get(constants.key_memory_free, 0))
    except Exception as e:
        err = to_str(e).replace("'", ' ')
        LOGGER.error(err)
    mem = 0
    try:
        vm_config = dom.get_config()
        mem = int(vm_config['memory'])
    except Exception as e:
        err = to_str(e).replace("'", ' ')
        LOGGER.error(err)
    LOGGER.error('Memory required is ' + str(mem))
    LOGGER.error('Available memory in ' + node.hostname + ' is ' + str(free_mem))
    result = mem < free_mem
    return (result, err)

#
def do_cpu_check(dom, node):
    print '\n\\CPUUUUUUUU'
    result = False
    err = ''
    try:
        vm_config = dom.get_config()
        vcpus = int(vm_config['vcpus'])
        cpu_info = node.get_cpu_info()
        cpus = int(cpu_info.get(constants.key_cpu_count, 1))
        print '\n\n==vcpus==',
        print vcpus,
        print '==cpus==',
        print cpus
        if vcpus / cpus <= 1:
            result = True
        else:
            err = 'vcpu/cpu ratio not correct'
    except Exception as e:
        err = to_str(e).replace("'", ' ')
        LOGGER.error(err)
    return (result, err)

#
def do_storage_check(dom, node):
    print '\n\\STORAGE===='
    result = False
    msg = ''
    if has_local_storage(dom.id, node) == True:
        msg = 'VM has local storage. ' + 'Can not migrate to '
    else:
        result = True
    return (result, msg)

#
def do_network_check(dom, node):
    print '\n\\nNETWORK===='
    result = False
    msg = ''
    vifs = dom.get_config().getNetworks()
    net_det = node.get_bridge_info()
    vif_count = 0
    for vif in vifs:
        nw_bridge_name = vif.get_bridge()
        print '\n\nbri==',
        print nw_bridge_name
        if net_det.has_key(nw_bridge_name):
            vif_count = vif_count + 1
            continue
            
    if len(vifs) == vif_count:
        result = True
    else:
        msg = 'Networks are not available'
    return (result, msg)

#
def has_local_storage(dom_id, dest_node=None):
    from stackone.model import DBSession
    from stackone.model.VM import VM, VMStorageLinks
    has_local_storage = False
    vm = DBSession.query(VM).filter(VM.id == dom_id).first()
    vm_disks = vm.VMDisks
    for disk in vm_disks:
        vm_storage_link = DBSession.query(VMStorageLinks).filter(VMStorageLinks.vm_disk_id == disk.id).first()
        if not vm_storage_link:
            has_local_storage = True
            break

    if has_local_storage == True and dest_node is not None:
        vm_conf = vm.get_config()
        if vm_conf is not None:
            des = vm_conf.getDisks()
            if des:
                for de in des:
                    has_local_storage = False
                    if not dest_node.node_proxy.file_exists(de.filename):
                        msg = 'Disk ' + de.filename + ' of VM ' + vm.name + ' does not exist on ' + dest_node.hostname
                        LOGGER.info(msg)
                        has_local_storage = True
                        break

    return has_local_storage

#
def get_dbtype():
    dburl = tg.config.get('sqlalchemy.url')
    db_type = dburl.split('/')
    if db_type[0][-1] == ':':
        db_type = db_type[0][:-1]
    return db_type
#
def p_task_timing_start(logger, op, entities, log_level='INFO'):
    from stackone.model.services import TaskUtil
    tid = str(TaskUtil.get_task_context())
    now = datetime.now()
    if log_level == 'INFO':
        logger.info('T:TID:E:TIMING::START  ' + op + ':' + tid + ':' + str(entities) + ' ' + str(now))
    else:
        logger.debug('T:TID:E:TIMING::START  ' + op + ':' + tid + ':' + str(entities) + ' ' + str(now))
    return (now, op, entities, tid, log_level)

#
def p_task_timing_end(logger, start_context, log_level='INFO'):
    now = datetime.now()
    delta = ''
    start = now
    entities = []
    tid = ''
    op = 'unknown'
    if start_context:
        start = start_context[0]
        op = start_context[1]
        entities = start_context[2]
        tid = start_context[3]
        log_level = start_context[4]
        
    if start != None:
        delta = str((now - start).seconds) + '.' + str((now - start).microseconds)
    if log_level == 'INFO':
        logger.info('T:TID:E:TIMING::END  ' + op + ':' + tid + ':' + str(entities) + ' ' + str(now) + ' ' + delta)
    else:
        logger.debug('T:TID:E:TIMING::END  ' + op + ':' + tid + ':' + str(entities) + ' ' + str(now) + ' ' + delta)
    return (now, op, entities)

#
def p_timing_start(logger, op, entities=None, log_level='INFO'):
    now = datetime.now()
    t = threading.currentThread()
    tid = '?'
    if t.getName():
        tid = t.getName()
    if log_level == 'INFO':
        logger.info('TIMING::START ' + op + ':' + tid + ':' + str(entities) + ': ' + str(now))
    else:
        logger.debug('TIMING::START ' + op + ':' + tid + ':' + str(entities) + ': ' + str(now))
    return (now, op, entities, log_level)
#
def p_timing_end(logger, start_context, print_entities=True, log_level="INFO"):
    now = datetime.now()

    t = threading.currentThread()
    tid = "?"
    if t.getName():
        tid = t.getName()

    delta = ""
    op = "unknown op"
    entities = None
    start=now
    if start_context:
        start = start_context[0]
        op = start_context[1]
        entities = start_context[2]
        log_level = start_context[3]

    if start!=None:
        delta = str((now-start).seconds)+"."+str((now-start).microseconds)

    str_entities = ""
    if entities:
        str_entities = str(entities)

    msg = "TIMING::END "+op+":"+tid+":"+" "+": "+ str(now)+" "+delta
    if print_entities :
        msg = "TIMING::END "+op+":"+tid+":"+str_entities+": "+ str(now)+" "+delta

    if log_level=="INFO":
        logger.info(msg)
    else:
        logger.debug(msg)

    # return it so that it can be chained
    return (now, op, entities)

import pylons
def create_node(hostname, username, password, sshport=22):
    from stackone.model.ManagedNode import ManagedNode
    if password == None:
        use_keys = hostname != 'localhost'
        
    use_keys = password == None
    isRemote = hostname != 'localhost'
    try:
        vnc_node = ManagedNode(hostname=hostname, ssh_port=sshport, username=username, password=password, isRemote=isRemote, helper=None, use_keys=use_keys, address=hostname)
        vnc_node.connect()

    except Exception as e:
        print 'Exception: ',
        print e
        return None

    return vnc_node

#
def remove_cidr_format_from_ip(ip):
    idx = to_str(ip).find('/')
    if idx > 0:
        ip = ip[0:idx]
    return ip
#
def is_cidr(c):
    parts = str(c).split('/')
    if len(parts) > 1:
        return True
    return False
#
def get_ips_from_range(range):
    start, end = range.split('-')
    ip_addresses = list(netaddr.iter_iprange(start, end))
    ips = [to_unicode(ip) for ip in ip_addresses]
    return ips

#
def get_ips_from_cidr(cidr):
    ips = [to_unicode(ip) for ip in netaddr.IPNetwork(cidr)]
    return ips
##pass
def boto_delay_request(delay_time=None):
    if not delay_time:
        delay_time = int(tg.config.get('boto_delay_request_time', 1L))
    if not isinstance(delay_time, int):
        raise Exception('delay time should be Integer')
    def wrap(fun):
        def wrapper(*args, **kwds):
            time.sleep(delay_time)
            return fun(*args, **kwds)

        return wrapper

    return wrap
#pass
def get_task_results(task_id):
    results = ''
    from stackone.model.services import TaskResult
    task_result = TaskResult.get_task_result_instance(task_id)
    if task_result:
        results = task_result.results
    return results

####pass 
def connect_url(url, proxies=None, reporthook=None, data=None, chunk=2048L):
    if reporthook:
        raise Exception('reporthook not supported yet')
    resp = None
    result = ''
    try:
        if proxies:
            proxy_support = urllib2.ProxyHandler(proxies)
            opener = urllib2.build_opener(proxy_support)
        else:
            opener = urllib2.build_opener()
        req = urllib2.Request(url)
        req.add_header('User-Agent', constants.fox_header)
        if data:
            resp = opener.open(req, data)
        else:
            resp = opener.open(req)
        data = resp.read(chunk)
        while data:
            result = result + data
            try:
                data = resp.read(chunk)
            except socket.error,e:
                if type(e.args is tuple) and len(e.args) > 0:
                    if e.args[0] == errno.EAGAIN or e.args[0] == 4:
                        continue
                else:
                    raise
    finally:
        if resp:
            resp.close()
    return result
#pass
def is_dev_deployment():
    imgstr_dir = tg.config.get(constants.prop_image_store, '')
    if imgstr_dir:
        top_dir = os.path.abspath(os.path.join(imgstr_dir, os.path.pardir))
        return os.path.isdir(top_dir + '/.svn')
    return False
#pass
def send_deployment_stats(cms_strt):
    if is_dev_deployment():
        print 'development deployment'
        return None
    from stackone.model import DBSession, Deployment
    from datetime import datetime
    from stackone.model.LicenseManager import get_license_guid
    try:
        lguid = get_license_guid()
        url = 'http://www.stackone.com.cn/deployments/deployment_stats.php'
        dep = DBSession.query(Deployment).first()
        if dep:
            end = ''
            nw = datetime.now()
            cms_started = nw
            cms_deployed = nw
            if not dep.distro_name:
                try:
                    update_deployment_status()
                except Exception as e:
                    print 'Error updating deployment data',
                    print e
            if dep.cms_end:
                end = dep.cms_end
            if dep.cms_started:
                cms_started = dep.cms_started
            else:
                end = ''
            if dep.cms_deployed:
                cms_deployed = dep.cms_deployed
            if not cms_strt:
                end = ''
            (distro_name, distro_ver) = ('n/a', 'n/a')
            if dep.distro_name:
                distro_name = to_str(dep.distro_name)
            if dep.distro_ver:
                distro_ver = to_str(dep.distro_ver)
            data = urllib.urlencode({'sps': to_str(dep.sps), 'vms': to_str(dep.vms), 'templates': to_str(dep.templates), 'users': to_str(dep.users), 'networks': to_str(dep.networks), 'storages': to_str(dep.storages), 'xen_server': to_str(dep.xen_server), 'kvm_server': to_str(dep.kvm_server), 'cms_started': to_str(cms_started), 'cms_deployed': to_str(cms_deployed), 'cms_end': to_str(end), 'cms_current': to_str(nw), 'version': to_str(dep.version) + '_EE', 'dep_id': to_str(dep.deployment_id), 'lguid': to_str(lguid), 'distro_name': distro_name, 'distro_ver': distro_ver, 'tot_sockets': to_str(dep.tot_sockets), 'tot_cores': to_str(dep.tot_cores), 'tot_mem': to_str(dep.tot_mem), 'host_sockets': to_str(dep.host_sockets), 'host_cores': to_str(dep.host_cores), 'host_mem': to_str(dep.host_mem)})
        response = connect_url(url, data=data)
        print response
    except Exception as e:
        import traceback
        traceback.print_exc()
    try:
        dep = DBSession.query(Deployment).first()
        if dep and cms_strt:
            if not dep.cms_deployed:
                dep.cms_deployed = datetime.now()
            dep.cms_started = datetime.now()
            DBSession.add(dep)
            import transaction
            transaction.commit()
    except Exception as e:
        import traceback
        traceback.print_exc()
#pass
def convert_byte_to(size, a_kilobyte_is_1024_bytes=True, humansize=True, convert_to='GB', round_size=True, return_format='%s%s'):
    act_size_in_byte = size
    print 'act_size_in_byte: ',
    print size
    SUFFIXES = {1000: [('KB', 'K'), ('MB', 'M'), ('GB', 'G'), ('TB', 'T'), ('PB', 'P'), ('EB', 'E'), ('ZB', 'Z'), ('YB', 'Y')], 1024L: [('KB', 'K'), ('MB', 'M'), ('GB', 'G'), ('TB', 'T'), ('PB', 'P'), ('EB', 'E'), ('ZB', 'Z'), ('YB', 'Y')]}
    if size < 0:
        raise ValueError('number must be non-negative')
    if a_kilobyte_is_1024_bytes:
        multiple = 1024
    else:
        multiple = 1000
    for suffix in SUFFIXES[multiple]:
        size /= float(multiple)
        if convert_to in suffix:
            print 'act_size_in_byte:%s, new size in %s: %s' % (act_size_in_byte, convert_to, size)
            break
        if size < multiple or convert_to in suffix:
            break
    if round_size:
        size = int(size)
    if humansize:
        return return_format % (size, convert_to)
    return size
    raise ValueError('number too large')
#pass
def get_default_datacenter():
    from stackone.model.Sites import Site
    from stackone.model import DBSession
    dc = DBSession.query(Site).filter(Site.name == constants.DC).filter(Site.type == None).first()
    if not dc:
        raise Exception('Could not find default Datacenter')
    return dc
#pass
def add_deployment_stats_task():
    from stackone.viewModel.TaskCreator import TaskCreator
    TaskCreator().send_deployment_stats()
#pass
def get_platform_name(platform):
    return get_platform_data(platform, 'name')
#pass
def get_platform_data(platform, key):
    from stackone.viewModel import Basic
    registry = Basic.getPlatformRegistry()
    plt_info = registry.get_platforms().get(platform)
    if plt_info:
        return plt_info[key]
    return ''
#pass
def get_web_helper(platform):
    from stackone.viewModel import Basic
    registry = Basic.getPlatformRegistry()
    web_helper = registry.get_web_helper(platform)
    return web_helper
#pass
def get_platform_version_key(platform):
    return get_platform_data(platform, 'version_key')
PROFILING = 'profiling'
TIMING = 'timing'
DEBUG = PROFILING
DEBUG_DIR = 'debug'
PREFIX = 'CMS'
#pass
def is_debug_enabled(type, function=None, category_lst=None):
    if not session.has_key('perf_debug_context') or not session['perf_debug_context'].has_key(type):
        return {'status': False, 'mgs': ''}
    debug_type = session['perf_debug_context'][type]
    if not debug_type.get('enable'):
        return {'status': False, 'mgs': ''}
    if type == PROFILING and function:
        if category_lst:
            if isinstance(category_lst, str):
                category_lst = [category_lst]
            categories = debug_type.get('categories', [])
            if filter((lambda x: x in categories), category_lst):
                debug_functions = debug_type.get('functions')
                if debug_functions:
                    debug_func_dict = debug_functions.get(function)
                    if debug_func_dict:
                        return {'status': debug_func_dict.get('status'), 'msg': ''}
                return {'status': True, 'mgs': ''}
        if not debug_type.has_key('functions'):
            return {'status': False, 'mgs': ''}
        debug_functions = debug_type.get('functions')
        debug_func_dict = debug_functions.get(function)
        if not debug_func_dict:
            return {'status': False, 'mgs': ''}
        return {'status': debug_func_dict.get('status'), 'msg': ''}
    return {'status': debug_type.get('enable'), 'mgs': ''}
#tianfeng
def performance_debug(type=None):
    def accept_method(method):
        def customize_method(*args, **kw):
            prof_result = is_debug_enabled(PROFILING, function=method.__name__, category_lst=type)
            prof_result.get('status', False)
            import cProfile
            import pstats
            import fcntl
            prof = cProfile.Profile()
            prof.enable(subcalls=True, builtins=True)
            start_dt_time = datetime.now()
            start_tm = time.time()
            result = prof.runcall(method, *args, **kw)
            end_tm = time.time()
            totall_tm = end_tm - start_tm
            if not os.path.exists(DEBUG_DIR):
                os.path.exists(DEBUG_DIR)
                os.mkdir(DEBUG_DIR)
            else:
                os.path.exists(DEBUG_DIR)
            msg = '\n\n\n ################## %s ##################### \n\n' % start_dt_time
            msg += '\n\nURL : %s' % tg.request.url
            msg += '\n\nMethod:%s, Time Taken:%s, Start Time:%s, End Time:%s' % (method.__name__, totall_tm, start_dt_time, datetime.now())
            fname = DEBUG_DIR + '/' + PREFIX + '_' + str(method.__name__) + '.txt'
            stats = pstats.Stats(prof)
            pp = stats.strip_dirs().sort_stats(-1L)
            try:
                fp = open(fname, 'a')
                fcntl.flock(fp, fcntl.LOCK_EX)
                fp.write(msg)
                pp.stream = fp
                pp.print_stats()
                fcntl.flock(fp, fcntl.LOCK_UN)
            except Exception as ex:
                LOGGER.error(ex)
            fp.close()
            prof_result.get('status', False)
            if is_debug_enabled(TIMING).get('status', False):
                start_dt_time = datetime.now()
                start_tm = time.time()
                result = method(*args, **kw)
                end_tm = time.time()
                totall_tm = end_tm - start_tm
                msg = 'PERFDEBUG: Method:%s, Time Taken:%s, Start Time:%s, End Time:%s' % (method.__name__, totall_tm, start_dt_time, datetime.now())
                LOGGER.info(msg)
            else:
                result = method(*args, **kw)
            return result
        return customize_method
    return accept_method
import pylons
#pass
def get_base_web_url():
    protocol = tg.config.get(constants.SERVER_PROTOCOL, 'http')
    host = pylons.request.headers['Host']
    web_url = '%s://%s' % (protocol, host)
    msg = 'base_web_url : %s' % web_url
    LOGGER.info(msg)
    return web_url
from tg import session
DEBUG_TYPES = [PROFILING, TIMING]
BOOL_TYPES = {'TRUE': True, 'FALSE': False}
GET = 'get'
SET = 'set'
METHODS = [GET, SET]
#pass
def set_or_get_perf_debug(**kwargs):
    base_web_url = get_base_web_url()
    msg = ''
    if not kwargs:
        msg = '<h4> Current Status </h4>\n                    <b>Profiling:</b> %s </br>\n                    <b>Timing:</b> %s\n              ' % (is_debug_enabled(PROFILING).get('status'), is_debug_enabled(TIMING).get('status'))
        msg += '<h5>Profiling Usage</h5>\n                Parameters: </br>\n                type : Debugging type (profiling). </br>\n                enable : To enable/disable profiling (true/false). </br>\n                method : To set/get profiling at function level (set/get). </br>\n                fun_name : Name of fucnction for which profiling to be enabled/disabled. </br>\n                fun_enable : To enable/disable profiling for a perticular function (true/false). </br>\n                category : To specify profiling category (DC_dashboard/SP_dashboard/SR_dashboard/VM_dashboard). </br>\n                cat_enable : To enable category base profiling (true/false). </br> </br>\n\n                <a href="%s/perf_debug?type=profiling&enable=true"> Enable Profiling:</a> </br> %s/perf_debug?type=profiling </br></br>\n                <a href="%s/perf_debug?type=profiling&enable=false"> Disable Profiling:</a> </br>  %s/perf_debug?type=profiling&enable=false </br></br>\n                Add method to session and enable profiling:</br>  %s/perf_debug?type=profiling&method=set&fun_name=dashboard_server_info </br></br>\n                <a href="%s/perf_debug?type=profiling&category=DC_dashboard&cat_enable=true"> Enable profiling for DC dashboard:</a> </br>  %s/perf_debug?type=profiling&category=DC_dashboard&cat_enable=true </br></br>\n                <a href="%s/perf_debug?type=profiling&method=get"> Get profiling status:</a> </br>  %s/perf_debug?type=profiling&method=get </br>\n              ' % (base_web_url, base_web_url, base_web_url, base_web_url, base_web_url, base_web_url, base_web_url, base_web_url, base_web_url)
        msg += '<h5>Timing Usage</h5>\n                Parameters: </br>\n                type : Debugging type (profiling). </br>\n                enable : To enable/disable profiling (true/false). </br> </br>\n                \n                <a href="%s/perf_debug?type=timing&enable=true"> Enable Timing:</a> </br>  %s/perf_debug?type=timing </br></br>\n                <a href="%s/perf_debug?type=timing&enable=false"> Disable Timing:</a> </br>  %s/perf_debug?type=timing&enable=false </br></br>\n              ' % (base_web_url, base_web_url, base_web_url, base_web_url)
        return msg
    type = kwargs.get('type')
    enable = kwargs.get('enable')
    method = kwargs.get('method')
    fun_name = kwargs.get('fun_name')
    fun_enable = kwargs.get('fun_enable', 'True')
    category = kwargs.get('category')
    cat_enable = kwargs.get('cat_enable', 'True')
    if method:
        if method not in METHODS:
            msg = "value of 'method' should be %s" % ' or '.join(METHODS)
            return msg
    if type not in DEBUG_TYPES:
        msg = "value of 'type' should be %s" % ' or '.join(DEBUG_TYPES)
        return msg
    if fun_enable.upper() not in BOOL_TYPES:
        msg = "value of 'fun_enable' should be true or false,"
        return msg
    fun_enable = BOOL_TYPES.get(fun_enable.upper())
    if not session.has_key('perf_debug_context'):
        session['perf_debug_context'] = {}
    perf_debug_context = session['perf_debug_context']
    if not perf_debug_context.has_key(type):
        perf_debug_context[type] = {}
    debug_type = perf_debug_context[type]
    if enable:
        if enable.upper() not in BOOL_TYPES:
            msg = "value of 'enable' should be true or false"
            return msg
        enable = BOOL_TYPES.get(enable.upper())
        debug_type['enable'] = enable
        msg += '<h4> Debugging Type:%s, Enabled:%s </h4> </br>' % (type, enable)
    if category:
        if cat_enable.upper() not in BOOL_TYPES:
            msg = "value of 'cat_enable' should be true or false"
            return msg
        cat_enable = BOOL_TYPES.get(cat_enable.upper())
        if not debug_type.has_key('categories'):
            debug_type['categories'] = []
        if cat_enable:
            if category not in debug_type['categories']:
                debug_type['categories'].append(category)
            msg += '<h4> Debugging Type:%s, Enabled Category:%s </h4> </br>' % (type, category)
        try:
            debug_type['categories'].remove(category)
        except Exception as ex:
            LOGGER.error(ex)
        msg += '<h4> Debugging Type:%s, Disabled Category:%s </h4> </br>' % (type, category)
    if type == PROFILING:
        if method:
            if not debug_type.has_key('functions'):
                debug_type['functions'] = {}
            debug_functions_dict = debug_type.get('functions')
            if method == SET and fun_name:
                st = 'Enabled'
                if not fun_enable:
                    st = 'Disabled'
                debug_functions_dict.update({fun_name: {'status': fun_enable}})
                msg += 'successfuly %s profliling of method %s' % (st, fun_name)
            elif method == GET:
                if not debug_functions_dict:
                    msg += 'Please add a function to enable/disable function level profiling'
                else:
                    if fun_name:
                        debug_fun_dict = debug_functions_dict.get(fun_name)
                        if debug_fun_dict:
                            msg += 'method: %s, Status: %s' % (fun_name, debug_fun_dict.get('status'))
                        else:
                            msg += 'method: %s not in the session' % fun_name
                            msg += '<table> <tr> <td><u>Method</u></td><td><u>Profiling</u></td> <td><u>Action</u></td></tr>'
                            for f_name,fun_dict in debug_functions_dict.items():
                                fun_cur_sts = fun_dict.get('status')
                                action = 'Enable'
                                if fun_cur_sts:
                                    action = 'Disable'
                                msg += '<tr> <td> %s </td> <td> <b> %s </b></td> <td><a href="%s/perf_debug?type=profiling&method=set&fun_name=%s&fun_enable=%s"> %s </a></td></tr>\n                                   ' % (f_name, fun_cur_sts, base_web_url, f_name, not fun_cur_sts, action)
                                msg += '</table> '
                msg += '</br></br></br><b>Profiling Enabled Categories: </b> </br> %s ' % '</br>'.join(debug_type.get('categories', []))
    session.save()
    return msg
#pass
def get_port_forward_cmd(forward_port, vncuser, hostname, host_ssh_port, vnc_display, dom):
    prename = to_str(forward_port) + '_' + to_str(vnc_display) + '_'
    temp_file = mktempfile(None, prename, '.log')
    log_level = 3L
    try:
        log_level = dom.get_vnc_log_level()
    except Exception as e:
        print 'Exception: ',
        print e
    vnc_log_level = '-d ' * log_level
    cmd = 'socat ' + vnc_log_level + ' TCP-LISTEN:' + to_str(forward_port) + " EXEC:'/usr/bin/ssh -p " + str(host_ssh_port) + ' ' + vncuser + '@' + hostname + ' socat - TCP\\:127.0.0.1\\:' + to_str(vnc_display) + "' > " + temp_file + ' 2>&1 &'
    return (cmd, temp_file)
def get_stackone_cache_dir():
    res_path = tg.config.get(constants.prop_cache_dir, '')
    print 'stackone cache dir: ',
    print res_path
    return res_path  
#pass 
def get_cms_root_dir():
    cwd = os.getcwd()
    print 'CMS root dir: ',
    print cwd
    return cwd  
#pass 
def get_cms_common_script_dir():
    cms_root_dir = get_cms_root_dir()
    res_path = cms_root_dir + '/common/scripts'
    print 'CMS common script dir: ',
    print res_path
    return res_path
def get_stackone_cache_common_script_dir():
    stackone_cache_dir = get_stackone_cache_dir()
    res_path = stackone_cache_dir + '/common/scripts'
    print 'stackone cache common script dir: ',
    print res_path
    return res_path
######################20130625  archer   hotNic  HotDevice
def device_exist(device):
    path = '/home/stackone/nic_disk'
    if not os.path.exists(path):
        os.mkdir(path)
    filelist = os.listdir(path)
    for filename in filelist:
        print device,'#############device,######filename',filename
        if device == '*'.join(filename.split('*')[:-1]):
            return True
    return False
def device_tag(device):
    path = '/home/stackone/nic_disk'
    f = file(os.path.join(path,device),'w')
    f.close()
    
def get_device_solt(device_k):
    path = '/home/stackone/nic_disk'
    filelist = os.listdir(path)
    for filename in filelist:
        if device_k == '*'.join(filename.split('*')[:-1]):
            solt = filename.split('*')[-1]
            os.remove(os.path.join(path,filename))
            return solt
def get_slot_number(output):
    import re

    # common variables
    
    rawstr = r"""\s+slot\s(\d+)"""
    embedded_rawstr = r"""\s+slot\s(\d+)"""
    matchstr = """OK domain 0, bus 0, slot 3, function 0"""
    
    # method 1: using a compile object
    compile_obj = re.compile(rawstr)
    match_obj = compile_obj.search(output)
    
    # method 2: using search function (w/ external flags)
    match_obj = re.search(rawstr, output)
    
    # method 3: using search function (w/ embedded flags)
    match_obj = re.search(embedded_rawstr, output)
    
    # Retrieve group(s) from match_obj
    all_groups = match_obj.groups()
    
    # Retrieve group(s) by index
    group_1 = match_obj.group(1)
    return group_1
    
def get_virtual_size(disk_name):
    import re

    # common variables
    
    rawstr = r""".*virtual size:\s+(\d+\w).*"""
    embedded_rawstr = r""".*virtual size:\s+(\d+\w).*"""
    matchstr = """'image: /home/stackone/vpn\nfile format: qcow2\nvirtual size: 10G (10737418240 bytes)\ndisk size: 1.2G\ncluster_size: 65536\n'"""
    
    # method 1: using a compile object
    compile_obj = re.compile(rawstr)
    match_obj = compile_obj.search(disk_name)
    
    # method 2: using search function (w/ external flags)
    match_obj = re.search(rawstr, disk_name)
    
    # method 3: using search function (w/ embedded flags)
    match_obj = re.search(embedded_rawstr, disk_name)
    
    # Retrieve group(s) from match_obj
    all_groups = match_obj.groups()
    
    # Retrieve group(s) by index
    group_1 = match_obj.group(1)
    return group_1
def get_bus_addr(usb_info):
    import re
    try:
        rawstr = r"""Bus\s+(\d{3})\s+\w+\s(\d{3})"""
        embedded_rawstr = r"""Bus\s+(\d{3})\s+\w+\s(\d{3})"""
        compile_obj = re.compile(rawstr)
        match_obj = compile_obj.search(usb_info)
        match_obj = re.search(rawstr, usb_info)
        match_obj = re.search(embedded_rawstr, usb_info)
        all_groups = match_obj.groups()
        bus = match_obj.group(1)
        addr = match_obj.group(2)
        return bus,addr
    except  Exception,e:
        raise Exception('get_bus_addr'+str(e))
        return (-1,-1)
    return bus,addr
def get_device(usb_info):
    try:
        import re
        rawstr = r"""Device\s+(\d+.\d+),\s+Port\s\d+.\d+,.*[^QEMU]"""
        embedded_rawstr = r"""Device\s+(\d+.\d+),\s+Port\s\d+.\d+,.*[^QEMU]"""
        matchstr = usb_info
        compile_obj = re.compile(rawstr)
        match_obj = compile_obj.search(matchstr)
        match_obj = re.search(rawstr, matchstr)
        match_obj = re.search(embedded_rawstr, matchstr)
        if match_obj:
            #all_groups = match_obj.groups()
            device = match_obj.group(1)
            return device
        else:
            return -1
    except  Exception,e:
        raise Exception('get_device'+str(e))
        return -1



##pass
#def get_stackone_cache_common_script_dir():
#    stackone_cache_dir = get_stackone_cache_dir()
#    res_path = stackone_cache_dir + '/common/scripts'
#    return res_path
##pass
#def get_stackone_cache_dir():
#    res_path = tg.config.get(constants.prop_cache_dir,'')
#    return res_path
