import sys
import os
import select
import stat
import shutil
import socket
import errno
import types
import paramiko
import getpass
from paramiko import SSHException
import subprocess
from stackone.core.utils.phelper import PHelper
from stackone.core.utils.utils import to_unicode, to_str
import threading
import _threading_local
class CommandException(Exception):
    def __init__(self, errno, description):
        Exception.__init__(self, errno, description)
        self.errno = errno
        self.description = description

    def __repr__(self):
        return '[Error %d], %s' % (self.errno, self.description)

    def __str__(self):
        return self.__repr__()



class Protected():
    def __init__(self, wrapped, owner, lock, skip_lock=False):
        self._wrapped = wrapped
        self._owner = owner
        self._lock = lock
        self._fn_map = {}
        self._skip_lock = skip_lock

    def locked_access(self, fn):
        def locked(*args, **kwargs):
            try:
                #print "Locking ", fn
                if not self._skip_lock:
                    self._lock.acquire()
                #print "Locked ", fn
                try:
                    return fn(*args, **kwargs)
                except IOError,er:
                    ###not calling set_last_error to avoid nodeproxy recycling
#                    print "calling self.set_last_errror"
#                    self.set_last_error(er)
                    raise
                except Exception, ex:
                    print "Error calling method. owner.set_last_error."
                    if not self._skip_lock:
                        self._owner.set_last_error(ex)
                    raise
            finally:
                #print "unlocking ", fn
                self._lock.release()
                #print "unlocked ", fn

        return locked

    def __getattr__(self, name):
        attr = getattr(self._wrapped, name)
        if type(attr) in (types.MethodType, types.FunctionType, types.LambdaType, types.BuiltinMethodType, types.BuiltinFunctionType):
            if self._fn_map.get(attr):
                return self._fn_map.get(attr)
            locked_callable = self.locked_access(attr)
            self._fn_map[attr] = locked_callable
            return locked_callable
        return attr



class Node():
    DEFAULT_USER = 'root'
    use_bash_timeout = False
    default_bash_timeout = None
    bash_dir = None
    local_bash_dir = None
    file_functions =  {
                  # "open": "open",
                   "mkdir": "os.mkdir",
                   "listdir": "os.listdir",
                   "remove": "os.remove",
                   "rmdir": "os.rmdir",
                   "rename": "os.rename",
                   "unlink": "os.unlink",
                   "chdir": "os.chdir",
                   "chmod": "os.chmod",
                   "symlink": "os.symlink",
                  # "put": "shutil.copyfile",
                  # "get": "shutil.copyfile",
                   "lstat": "os.lstat",
                   "stat": "os.stat",
                   "readlink": "os.readlink"}
    def x_init_fptrs(self):
        if self.thread_local.__dict__.get('_fptrs') is not None:
            return self.thread_local._fptrs
        fptrs = {}
        for fn in self.file_functions.keys():
            if self.isRemote:
                fptrs[fn] = eval('self.sftp_client.' + fn)
            else:
                fptrs[fn] = eval(self.file_functions[fn])
        self.thread_local._fptrs = fptrs
        return fptrs

    def x_init_sftp(self):
        if self.thread_local.__dict__.get('sftp_client') is not None:
            return self.thread_local.sftp_client
        client = paramiko.SFTPClient.from_transport(self.ssh_transport)
        client.sock.settimeout(socket.getdefaulttimeout())
        self.thread_local.sftp_client = client
        return client

    def locked_access(self, fn, fn_name, skip_lock=False):
        def locked(*args, **kwargs):
            try:
                #print "locking for ", fn_name
                if not skip_lock:
                    self._sftp_client_lock.acquire()
                #print "locked for ", fn_name
                try:
                    return fn(*args, **kwargs)
                except IOError,er:
                    ###not calling set_last_error to avoid nodeproxy recycling
#                    print "calling self.set_last_errror"
#                    self.set_last_error(er)
                    raise
                except Exception, ex:
                    print "calling self.set_last_errror"
                    self.set_last_error(ex)
                    raise
            finally:
                #print "unlocking for ", fn_name
                if not skip_lock:
                    self._sftp_client_lock.release()
                #print "unlocked for ", fn_name
        return locked
    def _init_fptrs(self):
        if self._fptrs is not None:
            return self._fptrs
        fptrs = {}
        for fn in self.file_functions.keys():
            if self.isRemote:
                fptrs[fn] = self.locked_access(eval('self.sftp_client.' + fn), fn)
            else:
                fptrs[fn] = eval(self.file_functions[fn])
        self._fptrs = fptrs
        return fptrs

    def _init_sftp(self):
        if self._sftp_client is not None:
            return self._sftp_client
        client = None
        try:
            self._sftp_init_lock.acquire()
            client = paramiko.SFTPClient.from_transport(self.ssh_transport)
            client.sock.settimeout(socket.getdefaulttimeout())
            self._sftp_client = client
        finally:
            self._sftp_init_lock.release()
        return client

    def __getattr__(self, name):
        if name == 'sftp_client':
            return self._init_sftp()
        if name == 'fptrs':
            return self._init_fptrs()
        if name in self.file_functions:
            return self.fptrs[name]

    def __init__(self, external_manager=None, hostname=None, ssh_port=22L, username=DEFAULT_USER, password=None, isRemote=False, use_keys=False):
        self.external_manager = external_manager
        self.isRemote = isRemote
        self.hostname = hostname
        self.ssh_port = ssh_port
        self.username = username
        self.password = password
        self.use_keys = use_keys
        self.ssh_transport = None
        self._fptrs = None
        self._sftp_client = None
        self._sftp_client_lock = None
        self._sftp_init_lock = threading.RLock()
        self._sftp_client_lock = threading.RLock()
        self._last_error = None
        self._fptrs = None

        ### Uncomment the following if you want to use thread local again.
        ### self.thread_local = _threading_local.local()
        ### self.local_obj_key = object.__getattribute__(self.thread_local,
        ###                                             '_local__key')

        #print "Creating NodeProxy with  ", self.hostname, self.local_obj_key
        # pointers to functions for doing file / directory manipulations
        self._fptrs = None

        if isRemote:
            try:
                authtype = None
                pwd = self.password
                if not pwd and self.use_keys:
                    authtype = "agent"
                    
                self.ssh_transport = \
                PHelper.init_ssh_transport(self.hostname,
                                           ssh_port = self.ssh_port,
                                           username=self.username,
                                           password=pwd,
                                           authtype = authtype
                                           )
            except Exception, ex:
                print "Could not initialize ssh for %s %d" % (hostname,
                                                              ssh_port)
                raise

            
        # Wrap the local functions
        self.put = self.locked_access(self.put, "put")
        self.get = self.locked_access(self.get,  "get")
        self.file_exists = self.locked_access(self.file_exists, "file_exists")
        self.file_is_writable = self.locked_access(self.file_is_writable, "file_is_writable")
        # exec_cmd creates its own channel. No need to protect it using sftp
        # But recycling logic is also in locked function.. so get locked access wrapper but skip locking.
        self.exec_cmd = self.locked_access(self.exec_cmd, "exec_cmd", 
                                           skip_lock=True)

        self.open = self.locked_access(self.open, "open")
        self.get_dir_entries = self.locked_access(self.get_dir_entries, "get_dir_entries")

    def set_last_error(self, ex):
        print 'ERROR : set last error Called.',
        print ex
        self._last_error = ex

    def get_last_error(self):
        return self._last_error

    def cleanup(self):
        self.clean_locals(self)
        if self.ssh_transport is not None:
            self.ssh_transport.close()

    def open(self, *args, **kw):
        if self.isRemote:
            ret = self.sftp_client.open(*args, **kw)
            if ret is not None:
                return Protected(ret, self, self._sftp_client_lock)
            return ret
        return open(*args, **kw)

    def get_dir_entries(self, dir):
        dir_entries=[]
        if self.isRemote:
            entries=self.sftp_client.listdir_attr(dir)
            for e in entries:
                dir_entries.append(dict(filename=e.filename,\
                                        path=os.path.join(dir,e.filename),\
                                        mtime=e.st_mtime, \
                                        size=e.st_size,\
                                        isdir=bool(stat.S_ISDIR(e.st_mode))))
        else:
            entries=os.listdir(dir)
            for file in entries:
                e=os.stat(os.path.join(dir,file))
                dir_entries.append(dict(filename=file,\
                                        path=os.path.join(dir,file),\
                                        mtime=e.st_mtime,\
                                        size=e.st_size,\
                                        isdir=bool(stat.S_ISDIR(e.st_mode))))

        return dir_entries
        
    def exec_cmd(self, cmd, exec_path=None, timeout=-1, params=None, cd=False, env=None, pid_file=None):
        evn_str = ''
        if env is not None:
            for env_var in env.keys():
                evn_str += 'export ' + env_var + '=' + env.get(env_var) + ';'
        if self.use_bash_timeout:
            bash_script = os.path.join(self.local_bash_dir, 'bash_timeout.sh')
            if self.isRemote:
                bash_script = os.path.join(self.bash_dir, 'bash_timeout.sh')
            
            bash_cmd = ''
            if timeout == -1:
                bash_cmd = bash_script + ' -t ' + to_str(self.default_bash_timeout) + ' '
            elif timeout is not None:
                bash_cmd = bash_script + ' -t ' + to_str(timeout) + ' '
            if pid_file is not None:
                bash_cmd = bash_cmd + '-p ' + pid_file + ' '
            cmd = bash_cmd + cmd
       
        if timeout == -1:
            timeout = None
        if exec_path is not None and exec_path is not '':
            exec_cmd = 'PATH=$PATH:%s; %s' % (exec_path, cmd)
            if cd == True:
                exec_cmd = 'cd ' + exec_path + ';' + exec_cmd
        else:
            exec_cmd = cmd
            
        exec_cmd = evn_str + exec_cmd
        if self.isRemote:
            return self.remote_exec_cmd(exec_cmd, timeout, params)
        else:
            return self.local_exec_cmd(exec_cmd, timeout, params)
            
    
    def local_exec_cmd(self, cmd, timeout=None, params=None):
        p1 = subprocess.Popen(cmd,stdin=subprocess.PIPE,
                              stdout=subprocess.PIPE,stderr=subprocess.STDOUT,
                              universal_newlines=True,
                              shell=True, close_fds=True)
        exit_code = -98
        out = ""
        err=None
        #out = p1.communicate()[0]
        #exit_code   = p1.returncode

        if params is not None:
            for param in params:
                p1.stdin.write(param+"\n")

        import time, datetime
        start = datetime.datetime.now()
        timedout = False
        while timeout is not None and p1.poll() is None:
            time.sleep(0.1)
            now = datetime.datetime.now()
            if (now - start).seconds> timeout:
                print "Local command timedout"
                timedout = True
                out = "__TIMEOUT__"
                exit_code = -99
                break
 
        if not timedout:
            #out = p1.stdout.read()
            (out,err)=p1.communicate()
            p1.wait()
            exit_code = p1.wait()
        if err is not None:
            out=out+"\n"+err
                
        # close the descriptors. fix descriptor leak
        for f in (p1.stdout, p1.stderr, p1.stdin):
            if f is not None:
                f.close()
        return out, exit_code
    def remote_exec_cmd(self, cmd, timeout=None, params=None):
        """
        Open channel on transport, run remote command,
        returns (stdout/stdin,process exit code)
        """

        out = ''
        exit_code = -98
        if self.ssh_transport is None:
            raise CommandException(0, "Transport not initialized")
        chan = None
        try:
            try:
                chan = self.ssh_transport.open_session()
                if not chan:
                    raise Exception("remote_exec_cmd :Could not create channel")
                chan.set_combine_stderr(True)
                chan.setblocking(0)
                chan.settimeout(socket.getdefaulttimeout())
                print '#######cmd',cmd
                x = chan.exec_command(to_str(cmd))

                if params is not None:
                    for param in params:
                        print param,'###########param#########'
                        chan.send(param+"\n")
                    chan.shutdown_write()

                ### Read when data is available
                timedout = False
                while True:
                    try:
                        # special case handling when command executes 
                        # quicker. When there is no output, the select was
                        # hanging.
                        if chan.exit_status_ready():
                            if  chan.recv_ready():
                                # read all data
                                x=chan.recv(1024)
                                while x:
                                    out = out + x
                                    x = chan.recv(1024)
                            else:
                                pass
                            break
                        # This one needs a timeout.. need to think about
                        # but can not be small as the app may take more time
                        # to process and return result. 
                        if select.select([chan,], [], [], timeout) == ([],[],[]):
                            timedout = True
                            print "remote command timedout"
                            out = "__TIMEOUT__" + out
                            exit_code = -99
                            break
                        x = chan.recv(1024)
                        if not x: break
                        out += x
                        select.select([],[],[],.1)
                    except (socket.error,select.error),  e:
                        if (type(e.args) is tuple) and (len(e.args) > 0) and \
                               ((e.args[0] == errno.EAGAIN or e.args[0] == 4)):
                            try:
                                select.select([],[],[],.1)
                            except Exception, ex:
                                pass
                            continue
                        else:
                            raise
                if not timedout:
                    exit_code = chan.recv_exit_status()
                #chan.close()
            except SSHException, ex:
                raise CommandException(0, to_str(ex))
        finally:
            if chan:
                try:
                    chan.close()
                except Exception, ex:
                    pass

        return out, exit_code

    def file_exists(self, filename):
        if self.isRemote:
            try:
                file_attribs = self.sftp_client.lstat(filename)
            except IOError, err:
                if err.errno == 2:  # ENOENT
                    return False
                raise
            return True
        else:
            return os.path.exists(filename)

    def file_is_writable(self, filename):
        """ Check for write permissions on 'filename'"""
        try:
            if self.isRemote:
                mode = self.sftp_client.stat(filename).st_mode
                return bool(stat.S_IMODE(mode) & stat.S_IWRITE)
            else:
                return os.access(filename,os.W_OK)
        except IOError:
            return False    
    def put(self, local, remote):
        if self.isRemote:
            f = None
            ch = None
            try:
                #self.sftp_client.put(local, remote)
                ch = self.ssh_transport.open_session()
                if not ch:
                    raise Exception("put: Could not create channel")
                ch.settimeout(2) # couple of seconds
                f = file(local,"rb")
                ch.exec_command("scp -t %s\n" % os.path.dirname(remote))
                fname = os.path.basename(remote)
                size = os.stat(local)[6]
                #print fname, size
                ch.sendall("C0664 %d %s\n" % (size, fname))
                r = ch.recv(1) # wait for ack
                buf = f.read(65536)
                while buf:
                    ch.sendall(buf)
                    buf = f.read(65536)
                r = ch.recv(1) # wait for ack
                #print "RECEIVED ", r == chr(0)
            finally:
                if f :
                    f.close()
                if ch:
                    ch.close()
        else:
            if local != remote :
                shutil.copyfile(local, remote)
                
    def get(self, remote, local):
        if self.isRemote:
            self.sftp_client.get(remote, local)
        else:
            if local != remote :
                shutil.copyfile(remote, local)

    @classmethod
    def clean_locals(cls, node_instance=None):
        #print "Cleaning up locals"
        ct = threading.currentThread()
        for k in  threading.currentThread().__dict__.keys():
            if isinstance(k, tuple):
                #print "key ", k
                d = threading.currentThread().__dict__.get(k)
                if node_instance is not None:
                    obj_key = node_instance.local_obj_key
                    #print "obj_key" ,obj_key
                    if k != obj_key:
                        continue
                
                if d is not None:
                    ftp_client = d.get("sftp_client")
                    if ftp_client is not None:
                        ftp_client.close()
                        del d["sftp_client"]
                        #print "cleaned sftp_client " , k, ct

                    _fptrs = d.get("_fptrs")
                    if _fptrs is not None:
                        del _fptrs
                        del d["_fptrs"]
                        #print "cleanedup _fptrs " , k, ct
                        
                        



class NodeWrapper():
    def __init__(self, external_manager, proxy_class, hostname=None, ssh_port=22, username=Node.DEFAULT_USER, password=None, isRemote=False, use_keys=False):
        self.external_manager = external_manager
        self.proxy_class = proxy_class
        self.hostname = hostname
        self.ssh_port = ssh_port
        self.username = username
        self.password = password
        self.isRemote = isRemote
        self.use_keys = use_keys
        self.connect()
    def connect(self):
        print 'Creating node proxy with ',
        print self.proxy_class.__name__
        self.n_p = self.proxy_class(self.external_manager, self.hostname, self.ssh_port, self.username, self.password, self.isRemote, self.use_keys)

    def disconnect(self):
        try:
            if self.n_p is not None:
                self.n_p.cleanup()
        except Exception as ex:
            print ex
        self.n_p = None
        return None

    def __getattr__(self, name):
        if self.n_p is None:
            print self.hostname,
            print ' not connected. Trying to connect.'
            self.connect()
        if self.n_p.get_last_error() is not None:
            print 'ERROR detected, recycling NodeProxy'
            try:
                self.disconnect()
            except Exception as ex:
                print 'ERROR in disconnect',
                print ex
            self.connect()
            print 'ERROR detected, recycling NodeProxy...DONE'
        get_attr = getattr(self.n_p, name)
        if get_attr is None:
            print 'get_attr for ',
            print name,
            print 'is None !!',
            print self.n_p.__class__
        return get_attr
#    def __init__(self, hostname=None, ssh_port=22, username=Node.DEFAULT_USER, password=None, isRemote=False, use_keys=False):
#        self.hostname = hostname
#        self.ssh_port = ssh_port
#        self.username = username
#        self.password = password
#        self.isRemote = isRemote
#        self.use_keys = use_keys
#        self.n_p = Node(hostname, ssh_port, username, password, isRemote, use_keys)


#    def connect(self, hostname, ssh_port, username, password, isRemote, use_keys):
#        self.hostname = hostname
#        self.ssh_port = ssh_port
#        self.username = username
#        self.password = password
#        self.isRemote = isRemote
#        self.use_keys = use_keys
#        self.n_p = Node(hostname, ssh_port, username, password, isRemote, use_keys)
#
#    def disconnect(self):
#        try:
#            if self.n_p is not None:
#                self.n_p.cleanup()
#        except Exception as ex:
#            pass
#        self.n_p = None
#
#    def __getattr__(self, name):
#        if self.n_p is None:
#            print self.hostname," not connected. Trying to connect."
#            self.connect(self.hostname, self.ssh_port, self.username, 
#                         self.password, self.isRemote, self.use_keys)
#            #raise Exception("Node not connected")
#        if self.n_p.get_last_error() is not None:
#            print "ERROR detected, recycling NodeProxy"
#            try:
#                self.disconnect()
#            except Exception , ex:
#                print "ERROR in disconnect", ex
#                pass
#            self.connect(self.hostname, self.ssh_port, self.username, 
#                         self.password, self.isRemote, self.use_keys)
#            print "ERROR detected, recycling NodeProxy...DONE"
#        return getattr(self.n_p, name)


#class NodePool():
#
#    _node_pool_lock = threading.RLock()
#    nodes = {}
#    
#    @classmethod
#    def get_key(cls, proxy_class, hostname, port, username, password, is_remote, use_keys):
#        if False:
#            key = '%s:%s:%d:%s:%s:%s:%s:%s' % (proxy_class.__name__,hostname, port, username, password, 
#                                     to_str(is_remote), to_str(use_keys),get_subsystem_context())
#        else:
#            key = '%s:%s:%d:%s:%s:%s:%s' % (proxy_class.__name__,hostname, port, username, password, 
#                                     to_str(is_remote), to_str(use_keys))
#        return key
#
#    @classmethod
#    def get_node(cls, external_manager, proxy_class, hostname=None, ssh_port=22, username='root', password=None, isRemote=False, use_keys=False):
#
#        # construct the key
#        key = cls.get_key(proxy_class,hostname, ssh_port, username, password, isRemote,
#                          use_keys)
#
#        # bug fix : unsynchronized check
#        if cls.nodes.get(key) is not None:
#           return cls.nodes[key]
#
#        try:
#            # TODO : Look in to removing Node Wrapper.
#            import time, datetime
#            start = datetime.datetime.now()
#            print "NODE_PROXY : START ", proxy_class,hostname, \
#                                         socket.getdefaulttimeout(), start
#            node = NodeWrapper(external_manager,
#                               proxy_class,
#                               hostname,
#                               ssh_port,
#                               username,
#                               password,
#                               isRemote,
#                               use_keys)
#        finally:
#            now = datetime.datetime.now()
#            print "NODE_PROXY : END ", hostname, socket.getdefaulttimeout(), \
#                                       (now - start).seconds
#
#        cls._node_pool_lock.acquire()
#        try:
#            if cls.nodes.get(key) is None:
#                cls.nodes[key] = node
#            else:
#                # two threads created the entry.. we lost.
#                node.cleanup()
#            return cls.nodes[key]            
#        finally:
#            cls._node_pool_lock.release()
#
#    # cleanup all entries 
#    # TODO: Hook it up to app shutdown
#    @classmethod        
#    def cleanup(cls, entry=None):
#        if entry is not None:
#            for n in cls.nodes.itervalues():
#                if n is not None and n == entry:
#                    n.cleanup()
#                    return
#            print "ERROR : NodePool.cleanup : node not found.", entry 
#            return
#        
#        for n in cls.nodes.itervalues():
#            if n is not None:
#                n.cleanup()
#                
#    @classmethod
#    def clear_node(cls,
#                 hostname = None,
#                 ssh_port = 22,
#                 username = Node.DEFAULT_USER,
#                 password=None,
#                 isRemote=False,
#                 use_keys = False):
#        # construct the key
#        key = cls.get_key(hostname, ssh_port, username, password, isRemote,
#                          use_keys)
#        cls._node_pool_lock.acquire()
#        try:
#            if cls.nodes.get(key) is not None:
#                node = cls.nodes[key]
#                node.cleanup()
#                cls.nodes[key] = None
#        finally:
#            cls._node_pool_lock.release()
#    
#    
#
#
#username = 'root'
#hostname = '192.168.12.106'
#if __name__ == '__main__':
#    socket.setdefaulttimeout(5)
#    node = Node(hostname, isRemote=True, username='root', password='xxx')
#    out = node.exec_cmd('echo $$', timeout=None)
#    print out,
#    print code
#    sys.exit(1)
#    tmp_dir = tmpfile.mkdtemp()
#    node.put(tmp_dir + '/send', tmp_dir + '/send_r')
#    node.get(tmp_dir + '/send_r', tmp_dir + '/received')
#    fd = node.open(tmp_dir + '/test_writable', 'w')
#    fd.seek(off, 0)
#    fd.write('\x00')
#    fd.close()
#    print 'exists?: ',
#    print node.file_exists(tmp_dir + '/test_writable')
#    print 'isWritable?: ',
#    print node.file_is_writable(tmp_dir + '/test_writable')
#    node.remove(tmp_dir + '/test_writable')
#    print 'exists?: ',
#    print node.file_exists(tmp_dir + '/test_writable')
#    sys.exit(0)
#    print node.xend.domains(0)
#    fname = '/etc/stackone.conf'
#    if node.file_exists(fname):
#        node.file_exists(fname)
#        print fname,
#        print 'Exists'
#    else:
#        node.file_exists(fname)
#        print fname,
#        print 'does not Exist'
#    fname = '/etc/xen/junk12'
#    if node.file_exists(fname):
#        node.file_exists(fname)
#        print fname,
#        print 'Exists'
#    else:
#        node.file_exists(fname)
#        print fname,
#        print 'does not Exist'
#    for remote in (False, True):
#        node = Node(hostname, isRemote=remote, protocol='tcp')
#        f = node.open('/etc/stackone.conf')
#        x = f.read(1024)
#        print x
#        f.close()
#    try:
#        node.mkdir(tmp_dir + '/node_test')
#    except (OSError, IOError) as err:
#        print to_str(err)
#    w = node.open(tmp_dir + '/node_test/test', 'w')
#    w.writelines(['hello this is test', 'hello this is second test'])
#    w.close()
#    r = node.open(tmp_dir + '/node_test/test')
#    x = r.readline()
#    while x != None and x != '':
#        print x
#        x = r.readline()
#    r.close()
#    node.remove(tmp_dir + '/node_test/test')
#    node.rmdir(tmp_dir + '/node_test')
#    output = node.exec_cmd('ls -la /')
#    # as code
#    print output
#    print 'EXIT CODE = ',
#    print code
#    output = node.exec_cmd('find /foo')
#    # as code
#    print output
#    print 'EXIT CODE = ',
#    print code
#    output = node.exec_cmd('junk /foo')
#    # as code
#    print output
#    print 'EXIT CODE = ',
#    print code
#    output = node.exec_cmd('touch x')
#    print output
#    print 'EXIT CODE = ',
#    print code
#    node.cleanup()
