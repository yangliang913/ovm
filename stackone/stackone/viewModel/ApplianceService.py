import re
import Basic
from TaskCreator import TaskCreator
import stackone.core.appliance.xva
from stackone.core.utils.utils import constants
from stackone.core.utils.utils import to_unicode, to_str, print_traceback
from stackone.model.ImageStore import ImageStore, ImageUtils
xva = stackone.core.appliance.xva
from stackone.viewModel.NodeService import NodeService
import logging
LOGGER = logging.getLogger('stackone.viewModel')
class ApplianceService():
    def __init__(self):
        self.appliance_store = Basic.getApplianceStore()

    def execute(self):
        feeds = self.appliance_store.get_appliance_feeds()
        list = []
        for feed_name in feeds:
            appList = self.appliance_store.get_appliances_list(feed_name)
        for appDef in appList:
            list.append(appDef)

    def get_appliance_providers(self):
        try:
            result = []
            feeds = self.appliance_store.get_appliance_feeds()
            counter = 0
            for feed_name in feeds:
                counter += 1
                result.append(dict(id=counter, name=feed_name, value=feed_name))
            return result
        except Exception as e:
            print_traceback()
            LOGGER.error(to_str(e).replace("'", ''))
            raise e

    def get_appliance_packages(self):
        try:
            result = []
            packages = self.appliance_store.get_all_packages()
            packages.sort()
            counter = 0
            for package in packages:
                counter += 1
                result.append(dict(id=counter, name=package, value=package))
            return result
        except Exception as e:
            print_traceback()
            LOGGER.error(to_str(e).replace("'", ''))
            raise e

    def get_appliance_archs(self):
        try:
            result = []
            archs = self.appliance_store.get_all_archs()
            archs.sort()
            counter = 0
            for arch in archs:
                counter += 1
                result.append(dict(id=counter, name=arch, value=arch))
            return result
        except Exception as e:
            print_traceback()
            LOGGER.error(to_str(e).replace("'", ''))
            raise e

    def get_appliance_list(self):
        try:
            result = []
            feeds = self.appliance_store.get_appliance_feeds()
            for feed_name in feeds:
                a_list = self.appliance_store.get_appliances_list(feed_name)
                for a_info in a_list:
                    title = a_info['title']
                    size = int(a_info['size'])
                    size_mb = str(float('%6.1f' % size) / 1048576) + ' MB'
                    package = a_info['type']
                    arch = a_info['arch']
                    pae = a_info['PAE']
                    provider = a_info['provider']
                    provider_logo_url = a_info['provider_logo_url']
                    desc = a_info.get('description')
                    if not desc:
                        desc = ''
                    short_desc = a_info.get('short_description')
                    if not short_desc:
                        short_desc = ''
                    if pae == 'True':
                        pae_str = 'Y'
                    else:
                        pae_str = 'N'
                    if arch == 'x86_64':
                        pae_str = ''
                    a_dict = {}
                    a_dict['PROVIDER'] = provider
                    a_dict['PROVIDER_LOGO'] = provider_logo_url
                    a_dict['TITLE'] = title
                    a_dict['PACKAGE'] = package
                    a_dict['ARCH'] = arch
                    a_dict['PAE'] = pae_str
                    a_dict['SIZE_MB'] = size_mb
                    a_dict['SIZE'] = size
                    a_dict['UPDATED'] = a_info['updated']
                    a_dict['DESC'] = desc
                    a_dict['SHORT_DESC'] = short_desc
                    a_dict['APPLIANCE_ENTRY'] = a_info
                    result.append(a_dict)
                return result
        except Exception as e:
            LOGGER.error(to_str(e).replace("'", ''))
            raise e

    def refresh_appliances_catalog(self):
        self.appliance_store.refresh_appliance_catalog()
        return self.get_appliance_list()

    def import_disk_image(self, auth, href, type, arch, pae, hvm, size, provider_id, platform, description, link, image_name, group_id, is_manual, date, time):
        platforms = []
        providers = self.appliance_store.get_appliance_feeds()
        if provider_id not in providers:
            raise Exception('The given provider ' + provider_id + ' is not found')
        architectures = self.appliance_store.get_all_archs()
        if arch not in architectures:
            raise Exception('The given architecture ' + arch + ' is not found')
        types = self.appliance_store.get_all_packages()
        if type not in types:
            raise Exception('The given type ' + type + ' is not found')
        platfrms = NodeService().get_platforms()
        for platfrm in platfrms:
            platforms.append(platfrm['value'])
        if platform not in platforms:
            raise Exception('The given platform ' + platform + ' is not found in' + to_str(platforms))
        try:
            result = self.import_appliance(auth, href, type, arch, pae, hvm, size, provider_id, platform, description, link, image_name, group_id, is_manual, date, time)
            return result
        except Exception as ex:
            print_traceback()

    def import_appliance(self, auth, href, type, arch, pae, hvm, size, provider_id, platform, description, link, image_name, group_id, is_manual, date, time):
        try:
            is_hvm = 'False'
            if hvm == 'true':
                is_hvm = 'True'
            is_pae = 'False'
            if pae == 'true':
                is_pae = 'True'
            image_name = re.sub(ImageStore.INVALID_CHARS_EXP, '_', image_name)
            appliance_entry = {}
            appliance_entry['href'] = href
            appliance_entry['type'] = type
            appliance_entry['arch'] = arch
            appliance_entry['PAE'] = is_pae
            appliance_entry['is_hvm'] = is_hvm
            appliance_entry['size'] = size
            appliance_entry['provider_id'] = provider_id
            appliance_entry['platform'] = platform
            appliance_entry['title'] = image_name
            if appliance_entry['provider_id'].lower() == 'jumpbox':
                appliance_entry['is_hvm'] = 'True'
            p_url = self.appliance_store.get_provider_url(provider_id)
            appliance_entry['provider_url'] = p_url
            p_logo_url = self.appliance_store.get_logo_url(provider_id)
            appliance_entry['provider_logo_url'] = p_logo_url
            if is_manual == 'true':
                description = "Manually imported appliance. Plese use 'Edit Description' menu to put appropriate description here."
                link = ''
            appliance_entry['description'] = description
            appliance_entry['link'] = link
            if self.appliance_store.get_provider(provider_id):
                self.appliance_store.get_provider(provider_id)
                appliance_entry['provider'] = self.appliance_store.get_provider(provider_id)
            else:
                self.appliance_store.get_provider(provider_id)
                appliance_entry['provider'] = provider_id
            if image_name:
                image_name = image_name.strip()
            platform = appliance_entry['platform']
            type = appliance_entry['type']
            if type.lower() not in ('xva', 'file_system', 'jb_archive'):
                raise Exception('Invalid Package type %s: supported package types are XVA, FILE_SYSTEM. JB_ARCHIVE' % type)
            image_store = Basic.getImageStore()
            if image_store.image_exists_by_name(image_name):
                image_store.image_exists_by_name(image_name)
                img = image_store.get_image_by_name(image_name)
                image_store.delete_image(auth, group_id, img.get_id())
            title = appliance_entry.get('title')
            if not title:
                title = ''
            tc = TaskCreator()
            result = tc.import_appliance(auth, appliance_entry, image_store, group_id, image_name, platform.lower(), True, date, time)
            return result
        except Exception as e:
            print_traceback()
            LOGGER.error(to_str(e).replace("'", ''))
            raise e

    def get_appliance_info(self, auth, domId, nodeId, action):
        provider_id = None
        manager = Basic.getGridManager()
        node = manager.getNode(auth, nodeId)
        vm = node.get_dom(domId)
        if vm and vm.is_resident() and vm.get_config():
            config = vm.get_config()
            provider_id = config['provider_id']
        result = {}
        if provider_id:
            proxy = self.get_appliance_ops(provider_id)
            app_url, mgmt_url, creds = proxy.get_info(vm)
            app_protocol, host, app_port, app_path = app_url
            app_mgmt_protocol, host, app_mgmt_port = mgmt_url
            username, password = creds
            result = dict(app_protocol=app_protocol, host=host, app_port=app_port, app_path=app_path, app_mgmt_protocol=app_mgmt_protocol, app_mgmt_port=app_mgmt_port, username=username, password=password)
            result['is_valid'] = proxy.is_valid_info(vm)
            web_url = ''
            try:
                web_url = proxy.get_web_url(vm)
            except Exception as e:
                print e
            result['web_url'] = web_url
            if action:
                mgmt_web_url = ''
                try:
                    mgmt_web_url = proxy.get_mgmt_web_url(vm, proxy.get_path(action))
                except Exception as e:
                    result['mgmt_web_url'] = mgmt_web_url
        return result

    def save_appliance_info(self, auth, domId, nodeId, action, props):
        manager = Basic.getGridManager()
        node = manager.getNode(auth, nodeId)
        vm = node.get_dom(domId)
        if vm and vm.get_config():
            config = vm.get_config()
            provider_id = config['provider_id']
            proxy = self.get_appliance_ops(provider_id)
            for key in proxy.get_keys():
                config[key] = props[key]
        manager.save_appliance_info(auth, vm, config)
        return self.get_appliance_info(auth, domId, nodeId, action)

    def get_appliance_menu_items(self, auth, domId, nodeId=None):
        provider_id = None
        manager = Basic.getGridManager()
        vm = manager.get_dom(auth, domId)
        if vm and vm.is_running() and vm.get_config():
            config = vm.get_config()
            provider_id = config['provider_id']
        result = []
        if provider_id:
            proxy,ops = self.get_appliance_ops(provider_id)
            for key,desc in ops:
                result.append(dict(name=desc, value=key))
        return result

    def get_appliance_ops(self, provider_id):
        appliance_providers = {'rPath': 'rPathProxyModel', 'JumpBox': 'JBProxyModel'}
        appliance_proxy = {}
        a_proxy = appliance_providers[provider_id]
        try:
            code =  'from stackone.viewModel.%s import %s; proxy=%s(); ops = proxy.getProxyIntegration()' % (a_proxy, a_proxy, a_proxy)
            exec(code)
            appliance_proxy[provider_id] = (proxy,ops)
            return (proxy, ops)
        except Exception as ex:
            print 'Skipping Application interation for ' + provider_id,
            print ex



class AppInfo():
    def __init__(self, data):
        self.data = data

    def toXml(self, doc):
        xmlNode = doc.createElement('ApplianceList')
        if self.data is None:
            pass
        else:
            for item in self.data:
                xmlNode.appendChild(self.make_info_node(item, doc))
        return xmlNode

    def make_info_node(self, item, doc):
        resultNode = doc.createElement('Appliance')
        keys = item.keys()
        for key in keys:
            newData = item[key]
            if isinstance(newData, dict):
                resultNode.appendChild(self.make_info_node(newData, doc))
                continue
        isinstance(newData, dict)
        resultNode.setAttribute(self.stripAttribute(key), to_str(newData))
        return resultNode

    def stripAttribute(self, name):
        expr = re.compile('(\\((\\S*)\\))')
        percentReg = re.compile('%')
        if percentReg.search(name):
            return expr.sub('_PERCENT', name)
        percentReg.search(name)
        return expr.sub('_\\2', name)



