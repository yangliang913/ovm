from stackone.model.GenericCache import GenericCache
from stackone.core.utils.utils import to_str, print_traceback
import stackone.core.utils.utils
constants = stackone.core.utils.constants
import tg
import threading
import traceback
from datetime import datetime, timedelta
class NodeCache(GenericCache):
    node_cache = {}
    lock = threading.RLock()
    def get_port(self, hostname, key, used_ports, start, end):
        selected_port = -1
        self.lock.acquire()
        try:
            self.clear_ports_cache(hostname, key)
            ports_in_cache = self.get_cache_val(hostname, key)
            used_ports.extend(ports_in_cache.keys())
            selected_port = self.get_free_port(used_ports, start, end)
            self.set_cache_val(hostname, key, selected_port)
        except Exception as ex:
            traceback.print_exc()
            raise ex
        finally:
            self.lock.release()
        return selected_port

    def get_free_port(self, used_ports, start, end):
        for port in range(start, end):
            if port not in used_ports:
                return port
        return None

    def get_node_cache(self, node_id):
        n_cache = self.node_cache.get(node_id)
        if n_cache is None:
            n_cache = {}
            self.node_cache.update({node_id:n_cache})
        return n_cache

    def get_cache_val(self, node_id, key):
        n_cache = self.get_node_cache(node_id)
        if key in [constants.PORTS]:
            val = n_cache.get(key, {})
            return val
        val = n_cache.get(key)
        return val

    def set_cache_val(self, node_id, key, val):
        n_cache = self.get_node_cache(node_id)
        upd_val = val
        if key in [constants.PORTS]:
            ports_dict = self.get_cache_val(node_id, key)
            ports_dict[val] = datetime.now()
            upd_val = ports_dict
        n_cache.update({key:upd_val})
        self.node_cache.update({node_id:n_cache})

    def clear_ports_cache(self, node_id, key):
        interval = 30
        try:
            interval = int(tg.config.get('node_ports_cache_clear_time', 30))
        except Exception as e:
            pass
        ports_dict = self.get_cache_val(node_id, key)
        for port,time in ports_dict.items():
            if time < (datetime.now() - timedelta(seconds = interval)): 
                del ports_dict[port]

    def get_cache(self):
        return self.node_cache

