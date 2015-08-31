from stackone.core.utils import constants
from stackone.model.ImageStore import ImageStore
from stackone.model.ApplianceStore import ApplianceStore
from stackone.model.PlatformRegistry import PlatformRegistry
from stackone.model.GridManager import GridManager
from stackone.model.ManagedNode import ManagedNode
from stackone.model.storage import StorageManager
from stackone.model.network import NwManager
from stackone.model.DBHelper import DBHelper
from stackone.config.ConfigSettings import ClientConfiguration

local_node = None
client_config = ClientConfiguration()
store = None
registry = None
image_store = None
manager = None
storage_manager = None
nw_manager = None
appliance_store = None
cp_feature_registry = None
def basic_initialize():
    global local_node, client_config, store, registry, image_store, manager, storage_manager
    global nw_manager, appliance_store,cp_feature_registry
    try:
        local_node = ManagedNode(hostname = constants.LOCALHOST, isRemote = False, helper = None)
        registry = PlatformRegistry(client_config, {})
#        cp_feature_registry = ProviderFeatureRegistry(client_config)
        image_stores = DBHelper().filterby(ImageStore,[],[ImageStore.type != constants.VCENTER])
        if len(image_stores)>0:
            image_store =image_stores[0]
            image_store.set_registry(registry)
        manager = GridManager(client_config,registry, None)
        storage_manager = StorageManager()
        nw_manager = NwManager()

        appliance_store = ApplianceStore(local_node, client_config)
    except Exception, e:
        import traceback
        traceback.print_exc()
        raise e
    return None


def getGridManager():
    if not manager:
        basic_initialize()
    return manager

def getImageStore():
    if not image_store:
        basic_initialize()
    return image_store

def getApplianceStore():
    if appliance_store is None:
        basic_initialize()
    return appliance_store

def getPlatformRegistry():
    if not registry:
        basic_initialize()
    return registry

def getCPFeatureRegistry():
    if not cp_feature_registry:
        basic_initialize()
    return cp_feature_registry

def getStorageManager():
    if not storage_manager:
        basic_initialize()
    return storage_manager

def getNetworkManager():
    if not nw_manager:
        basic_initialize()
    return nw_manager

def getManagedNode():
    if not local_node:
        basic_initialize()
    return local_node


