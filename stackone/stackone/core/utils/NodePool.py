from stackone.core.utils.NodeProxy import Node, NodeWrapper
from stackone.core.utils.utils import to_unicode, to_str
from stackone.core.utils.thread_context import get_subsystem_context
import socket
import threading
class NodePool():
    _node_pool_lock = threading.RLock()
    nodes = {}
    @classmethod
    def get_key(cls, proxy_class, hostname, port, username, password, is_remote, use_keys):
        if False:
            key = '%s:%s:%d:%s:%s:%s:%s:%s' %(proxy_class.__name__,hostname,port,username,password,to_str(is_remote),to_str(use_keys),get_subsystem_context())
        else:
            key = '%s:%s:%d:%s:%s:%s:%s' % (proxy_class.__name__,hostname,port,username,password,to_str(is_remote),to_str(use_keys))
        return key
    @classmethod        
    def get_node(cls, external_manager, proxy_class, hostname=None, ssh_port=22, username='root', password=None, isRemote=False, use_keys=False):
        key = cls.get_key(proxy_class, hostname, ssh_port, username, password, isRemote, use_keys)
        if cls.nodes.get(key) is not None:
            return cls.nodes[key]
        try:
            import time
            import datetime
            start = datetime.datetime.now()
            print 'NODE_PROXY : START ',proxy_class,hostname
            print socket.getdefaulttimeout()
            print start
            node = NodeWrapper(external_manager,proxy_class,hostname,ssh_port,username,password,isRemote,use_keys)
        finally:
            now = datetime.datetime.now()    
            print 'NODE_PROXY : END ',hostname,socket.getdefaulttimeout()
            print (now - start).seconds
        cls._node_pool_lock.acquire()
        try:
            if cls.nodes.get(key) is None:
                cls.nodes[key] = node
                print 'Adding to NodePool'
            else:
                node.cleanup()
            return cls.nodes[key]
        finally:
            cls._node_pool_lock.release()
    @classmethod
    def cleanup(cls, entry=None):
        if entry is not None:
            for n in cls.nodes.itervalues():
                if n is not None and n == entry:
                    n.cleanup()
                    return None
            print 'ERROR : NodePool.cleanup : node not found.'
            print entry
            return None
        for n in cls.nodes.itervalues():
            if n is not None:
                n.cleanup()
                
    @classmethod
    def clear_node(cls, proxy_class, hostname=None, ssh_port=22, username='root', password=None, isRemote=False, use_keys=False):
        key = cls.get_key(proxy_class, hostname, ssh_port, username, password, isRemote, use_keys)
        cls._node_pool_lock.acquire()
        try:
            if cls.nodes.get(key) is not None:
                node = cls.nodes[key]
                node.cleanup()
                cls.nodes[key] = None
        finally:
            cls._node_pool_lock.release()
        
        


if __name__ == '__main__':
    print 'Hello'
