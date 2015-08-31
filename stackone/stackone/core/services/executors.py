from threading import Thread
from stackone.core.services.core import Service, ServiceException
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
import time
from stackone.core.utils.utils import to_unicode, to_str
import logging
logger = logging.getLogger('stackone.services')
enable_processes = True
try:
    from processing import Process
    from Pyro.core import ObjBase, Daemon, getProxyForURI, initClient
    from Pyro.naming import NameServerLocator
    from Pyro.errors import NamingError
    try:
        NameServerLocator().getNS()
    except NamingError:
        enable_processes = False
except ImportError:
    enable_processes = False
    
class Executor():
    def start(self, service, service_id, dbconn, service_deps):
        pass

    def check(self):
        pass

    def query(self, service):
        pass

    def get_service(self, service):
        pass

    def stop(self, service):
        pass

    def stop_all(self):
        pass

    def kill(self, service):
        pass



if enable_processes:
    class ProcessInst(Process):
        def __init__(self, service, db_conn_string):
            self.service = service
            self.db_conn_string = db_conn_string
            Process.__init__(self)

        def run(self):
            self.pd = PyroRemoteDaemon(self.service)
            self.pd.configure()
            self.pd.start()
            engine = create_engine(self.db_conn_string)
            self.service.dbconn = sessionmaker(bind=engine)
            self.stop_service_fn = self.service.stop
            self.service.stop = self.stop
            self.service._exec()

        def stop(self):
            self.pd.stop()
            self.stop_service_fn()

    class PyroRemoteDaemon(Thread):
        def __init__(self, service_obj):
            self.service_obj = service_obj
            self.service_id = service_obj.getid()
            Thread.__init__(self)

        def configure(self):
            pyro_obj = ObjBase()
            pyro_obj.delegateTo(self.service_obj)
            (self.pd, pd) = (Daemon(), Daemon())
            ns = NameServerLocator().getNS()
            pd.useNameServer(ns)
            pyro_id = 'REMOTESVC' + to_str(self.service_id)
            try:
                ns.unregister(pyro_id)
            except NamingError:
                pass
            pd.connect(pyro_obj, pyro_id)
            self.service_obj.set_external_ref(pd.getProxyForObj(pyro_obj))


        def run(self):
            self.pd.requestLoop()

        def stop(self):
            self.pd.shutdown()



    class ProcessExecutor(Executor):
        def __init__(self):
            self.processes = []
            try:
                NameServerLocator().getNS()
            except NamingError:
                raise ServiceException('Pyro name server is not found.                                        Please run pyro-ns')
            initClient()

        def startProcess(self, process):
            process.start()
            proxy_service = None
            while True:
                try:
                    if proxy_service is None:
                        proxy_service = self.get_po_process(process)
                    if proxy_service.is_ready():
                        break
                    time.sleep(0.1)
                except NamingError:
                    pass

        def start(self, _service, service_id, dbconn, service_deps):
            temp = dbconn()
            try:
                db_conn_string = to_str(temp.get_bind(None).url)
            finally:
                temp.close()
            service = _service(service_id, Service.MODE_PROCESS, None)
            service.set_dependencies(service_deps)
            process = ProcessInst(service, db_conn_string)
            self.processes.append(process)
            self.startProcess(process)
        def check(self):
            revived = []
            for p in self.processes[:]:
                if not p.isAlive():
                    logger.debug("dead process found")
                    newP = ProcessInst(p.service, p.db_conn_string)
                    self.processes.remove(p)
                    self.processes.append(newP)
                    self.startProcess(newP)
                    revived.append(newP.service.getid())
            return revived
        def find_process(self, _service):
            for p in self.processes:
                if isinstance(p.service, _service):
                    return p
            else:
                return None


        def query(self, _service):
            p = self.find_process(_service)
            if p:
                return t.isAlive()
            else:
                return False

        def get_po_service(self, _service):
            return self.get_po_process(self.find_process(_service))

        def get_po_process(self, process):
            return getProxyForURI('PYRONAME://REMOTESVC' + to_str(process.service.getid()))

        def get_service(self, _service):
            po = self.get_po_service(_service)
            return po

        def stop(self, _service):
            p = self.find_process(_service)
            po = self.get_po_process(p)
            if p:
                po._stop()
                self.processes.remove(p)


        def stop_all(self):
            for p in self.processes[:]:
                self.get_po_process(p)._stop()
                self.processes.remove(p)
        def kill(self, _service):
            p = self.find_process(_service)
            if p:
                p.get_po_process(p)._stop()
                p.terminate()
                self.processes.remove(p)



class ThreadInst(Thread):
    def __init__(self, service):
        self.service = service
        Thread.__init__(self)

    def run(self):
        self.service._exec()

    def stop(self):
        self.service._stop()


if enable_processes:
    class PyroLocalDaemon(Thread):
        def register_service(self, service_obj):
            pyro_obj = ObjBase()
            pyro_obj.delegateTo(service_obj)
            service_id = service_obj.getid()
            pyro_id = 'LOCALSVC' + to_str(service_id)
            ns = self.pd.getNameServer()
            try:
                ns.unregister(pyro_id)
            except NamingError:
                pass
            self.pd.connect(pyro_obj, pyro_id)
            service_obj.set_external_ref(self.pd.getProxyForObj(pyro_obj))
            service_obj._PyroLocalDaemon__pyro_obj = pyro_obj


        def unregister_service(self, service_obj):
            self.pd.disconnect(service_obj._PyroLocalDaemon__pyro_obj)

        def configure(self):
            (self.pd, pd) = (Daemon(), Daemon())
            ns = NameServerLocator().getNS()
            pd.useNameServer(ns)
            logger.debug('Local Pyro started')

        def run(self):
            self.pd.requestLoop()

        def stop(self):
            self.pd.shutdown()

class ThreadExecutor(Executor):
    def __init__(self):
        self.threads = []
        if enable_processes:
            self.pyro_daemon = PyroLocalDaemon()
            self.pyro_daemon.configure()
            self.pyro_daemon.start()


    def start(self, _service, service_id, dbconn, service_deps):
        service = _service(service_id, Service.MODE_THREAD, dbconn)
        service.set_dependencies(service_deps)
        if enable_processes:
            self.pyro_daemon.register_service(service)
        threadInst = ThreadInst(service)
        self.threads.append(threadInst)
        threadInst.start()
        while not service.is_ready():
            time.sleep(0.1)


    def check(self):
        revived = []
        for t in self.threads[:]:
            if not t.isAlive():
                logger.debug("dead thread found. restarting")
                newT = ThreadInst(t.service)
                self.threads.remove(t)
                self.threads.append(newT)
                newT.start()
                while not newT.service.is_ready():
                    time.sleep(0.1)
                revived.append(newT.service.getid())
        return revived
    def find_thread(self, _service):
        for t in self.threads:
            if isinstance(t.service, _service):
                return t

    def query(self, _service):
        t = self.find_thread(_service)
        if t:
            return t.isAlive()
        else:
            return False


    def get_service(self, _service):
        t = self.find_thread(_service)
        if t:
            return t.service

    def stop(self, _service):
        t = self.find_thread(_service)
        if t:
            if enable_processes:
                self.pyro_daemon.unregister_service(t.service)
            t.stop()
            self.threads.remove(t)


    def stop_all(self):
        if enable_processes:
            self.pyro_daemon.stop()
        for t in self.threads[:]:
            t.stop()
            self.threads.remove(t)


