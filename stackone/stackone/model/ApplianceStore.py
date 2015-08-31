import os
import types
import stackone.core.utils.constants
from stackone.model.ImageStore import ImageStore
from stackone.core.utils.utils import PyConfig
from stackone.core.utils.utils import to_unicode, to_str
import stackone.core.utils.utils
import xml.dom.minidom
from xml.dom.minidom import Node
from stackone.core.utils.utils import fetch_isp, mkdir2, populate_node, populate_attrs, getText
import urllib
from stackone.model.DBHelper import DBHelper
from stackone.model.Appliance import ApplianceCatalog, ApplianceFeed, Appliance
utils = stackone.core.utils.utils
constants = stackone.core.utils.constants
class ApplianceStore():
    DEFAULT_APPLIANCE_STORE = '/var/cache/stackone/appliance_store'
    APPLIANCE_FEEDS = 'appliance_feeds.conf'
    CATALOG_CONF = 'catalog.conf'
    def __init__(self, local_node, config):
        self.local_node = local_node
        self.config = config
        self._feeds = None
        self.cache_dir = None
        self.catalogs = {}
        self.appliance_list = {}
        self.appliance_store_dir = config.get(constants.prop_appliance_store)
        if self.appliance_store_dir is None or self.appliance_store_dir is '':
            self.appliance_store_dir = self.DEFAULT_APPLIANCE_STORE


        catalogs = DBHelper().get_all(ApplianceCatalog)

        for catalog in catalogs:
            self.catalogs[catalog.name] = catalog.url

        print self.catalogs
        mkdir2(self.local_node, self.get_cache_dir())

        
    def __getattr__(self, name):
        if name == 'feeds':
            return self._ApplianceStore__initialize()


    def _ApplianceStore__initialize(self):
        if not self._feeds:
            return self._ApplianceStore__read_appliance_feeds()

        return self._feeds


    def _ApplianceStore__read_appliance_feeds(self):
        feeds_list = DBHelper().get_all(ApplianceFeed)
        if len(feeds_list) == 0L:
            feeds_list = self.populate_appliance_feeds()

        self._feeds = {}

        for feed in feeds_list:
            v = {}
            v['provider'] = feed.provider_name
            v['provider_url'] = feed.provider_url
            v['logo_url'] = feed.provider_logo_url
            v['feed_url'] = feed.feed_url
            v['feed_name'] = feed.feed_name
            v['provider_id'] = feed.provider_id
            v['id'] = feed.id
            self._feeds[feed.provider_id] = v

        return self._feeds


    def populate_appliance_feeds(self):
        feeds = {}
        for c,c_info in self.catalogs.iteritems():
            print c,c_info
            if type(c_info) in [types.StringType, types.UnicodeType]:
                url = c_info
        try:
            feed_conf = self.fetch_catalog(c, url)
        except Exception as ex:
            feed_conf = self.get_conf_name(c)
            print 'Error getting catalog ',c,url,ex
            print 'Continue using the existing data'
            

        if not os.path.exists(feed_conf):
            print 'Skipping : %s does not exist.',feed_conf
            

        feed = PyConfig(self.local_node, feed_conf)
        for k,v in feed.iteritems():
            feeds[k] = v
        a_feeds = []
        for k in feeds.iteritems():
            a_feed = ApplianceFeed(to_unicode(k))
            a_feed.feed_name = to_unicode(v['feed_name'])
            a_feed.feed_url = to_unicode(v['feed_url'])
            a_feed.provider_logo_url = to_unicode(v['logo_url'])
            a_feed.provider_name = to_unicode(v['provider'])
            a_feed.provider_url = to_unicode(v['provider_url'])
            a_feeds.append(a_feed)

        DBHelper().truncate(ApplianceFeed)
        DBHelper().add_all(a_feeds)
        return a_feeds


    def get_conf_name(self, catalog):
        feed_conf_dir = os.path.join(self.appliance_store_dir, catalog)
        feed_conf = os.path.join(feed_conf_dir, self.APPLIANCE_FEEDS)
        return feed_conf

    def fetch_catalog(self, catalog, url):
        feed_conf = self.get_conf_name(catalog)
        feed_conf_dir = os.path.dirname(feed_conf)
        mkdir2(self.local_node, feed_conf_dir)
        fetch_isp(url, feed_conf, 'text/plain')
        print "fetched ", url, feed_conf
        return feed_conf

    def get_appliance_feeds(self):
        return self.feeds.keys()

    def get_appliances_list(self, feed_name):
        if feed_name is None:
            return []

        if self.appliance_list.get(feed_name) is not None:
            return self.appliance_list[feed_name]

        a_list = []
        provider_id = self.get_provider_id(feed_name)
        list = DBHelper().filterby(Appliance, [], [Appliance.provider_id == to_unicode(provider_id)])

        if len(list) == 0:
            a_list = self.populate_appliances(feed_name)
            if a_list :
                self.appliance_list[feed_name] = a_list
        else:
            for appliance in list:
                appliance_info = {}
                appliance_info['title'] = appliance.title
                appliance_info['id'] = appliance.catalog_id
                appliance_info['provider_id'] = appliance.provider_id
                appliance_info['provider'] = self.get_provider(feed_name)
                appliance_info['provider_url'] = self.get_provider_url(feed_name)
                appliance_info['provider_logo_url'] = self.get_logo_url(feed_name)
                appliance_info['link'] = appliance.link_href
                appliance_info['description'] = appliance.description
                appliance_info['popularity_score'] = appliance.popularity_score
                appliance_info['short_description'] = appliance.short_description
                appliance_info['PAE'] = appliance.PAE
                appliance_info['arch'] = appliance.arch
                appliance_info['archive'] = appliance.archive
                appliance_info['compressed'] = appliance.compression_type
                appliance_info['href'] = appliance.download_href
                appliance_info['filename'] = appliance.filename
                appliance_info['installed_size'] = appliance.installed_size
                appliance_info['is_hvm'] = appliance.is_hvm
                appliance_info['platform'] = appliance.platform
                appliance_info['size'] = appliance.size
                appliance_info['type'] = appliance.type
                appliance_info['updated'] = appliance.updated_date
                appliance_info['version'] = appliance.version
                a_list.append(appliance_info)
                self.appliance_list[feed_name] = a_list
        return a_list


    def refresh_appliance_catalog(self):
        self.populate_appliance_feeds()
        self._feeds = self._ApplianceStore__read_appliance_feeds()

        for k,v in self._feeds.iteritems():
            self.appliance_list[k] = self.populate_appliances(k)


    def get_cache_dir(self):
        if self.cache_dir is None:
            self.cache_dir = os.path.join(self.appliance_store_dir, 'cache')
        return self.cache_dir


    def get_feed_cache_dir(self, feed_name):
        return os.path.join(self.get_cache_dir(), feed_name)

    def get_feed_file_name(self, feed_name):
        return 'feed.xml'

    def get_provider_id(self, feed_name):
        feed = self.feeds.get(feed_name)
        if feed:
            return feed_name


    def get_provider(self, feed_name):
        feed = self.feeds.get(feed_name)
        if feed:
            return feed['provider']


    def get_provider_url(self, feed_name):
        feed = self.feeds.get(feed_name)
        if feed:
            return feed['provider_url']

    def get_logo_url(self, feed_name):
        feed = self.feeds.get(feed_name)
        if feed:
            return feed['logo_url']


    def get_feed_url(self, feed_name):
        feed = self.feeds.get(feed_name)
        if feed:
            return feed['feed_url']


    def get_feed_name(self, feed_name):
        feed = self.feeds.get(feed_name)
        if feed:
            return feed['feed_name']


    def populate_appliances(self, feed_name):
        feed = self.feeds.get(feed_name)
        if feed is None:
            return None

        cache_dir = self.get_feed_cache_dir(feed_name)
        utils.mkdir2(self.local_node, cache_dir)
        cache_file = self.get_feed_file_name(feed_name)
        feed_dest = os.path.join(cache_dir, cache_file)
        url = self.get_feed_url(feed_name)

        try:
            fetch_isp(url, feed_dest, '/xml')
        except Exception as ex:
            print "Error downloading feed " , url, ex
            print 'Will try to use cached copy if available.'

        details = []
        if self.local_node.node_proxy.file_exists(feed_dest):
            details = self._make_details(feed_name, feed_dest)
        else:
            print "Skipping ", feed_dest, " not found."

        return details


    def _make_details(self, feed_name, feed_file):
        feed_dom = xml.dom.minidom.parse(feed_file)
        a_list = []
        appliance_list = []

        for entry in feed_dom.getElementsByTagName('entry'):
            info = {}
            info['provider_id'] = self.get_provider_id(feed_name)
            info['provider'] = self.get_provider(feed_name)
            info['provider_url'] = self.get_provider_url(feed_name)
            info['provider_logo_url'] = self.get_logo_url(feed_name)

            for text in ('title', 'id', 'popularity_score', 'description', 'short_description'):
                info[text]=getText(entry, text)

            populate_node(info,entry,"link",{ "link" : "href"})
            download_nodes = entry.getElementsByTagName("download")
            for download_node in download_nodes:
                download_info = {}
                populate_attrs(download_info,download_node,
                               { "href" : "href",
                                 "type" : "type"
                                 })

                populate_node(download_info,download_node,"platform",
                               { "platform" : "name"})
                
                populate_node(download_info,download_node, "package",
                               { "filename" : "filename",
                                 "compressed" : "compressed",
                                 "archive" : "archive",
                                 "size" : "size",
                                 "installed_size" : "installed_size"})
                populate_node(download_info,download_node,"kernel",
                               { "PAE" : "PAE",
                                 "arch": "arch",
                                 "is_hvm": "is_hvm"})
                if download_info.get('arch'):
                    if download_info['arch'].upper() == 'X86_32':
                        download_info["arch"] = "x86"

                for t in ('updated',):
                    download_info[t] = getText(download_node, t)

                feed_info={}
                for k in info.keys():
                    feed_info[k] = info[k]
                for k in download_info.keys():
                    if feed_info.get(k) is None:
                        feed_info[k] = download_info[k]
                else:
                    print 'ERROR : collision in feed and download entry'
        
                appliance=Appliance(to_unicode(info['title']))
                appliance.catalog_id=to_unicode(info['id'])
                appliance.provider_id=to_unicode(info['provider_id'])
                appliance.link_href=to_unicode(info['link'])
                appliance.description=info['description']
                appliance.popularity_score=to_unicode(info['popularity_score'])
                appliance.short_description=info['short_description']
                if download_info['PAE'] is not None and download_info['PAE']!='':
                    appliance.PAE=eval(download_info['PAE'])
                appliance.arch=to_unicode(download_info['arch'])
                appliance.archive=to_unicode(download_info['archive'])
                appliance.compression_type=to_unicode(download_info['compressed'])
                appliance.download_href=to_unicode(download_info['href'])
                appliance.filename=to_unicode(download_info['filename'])
                appliance.installed_size=download_info['installed_size']
                if download_info['is_hvm'] is not None and download_info['is_hvm']!='':
                    appliance.is_hvm=eval(download_info['is_hvm'])
                appliance.platform=to_unicode(download_info['platform'])
                appliance.size=download_info['size']
                appliance.type=to_unicode(download_info['type'])
                appliance.updated_date=to_unicode(download_info['updated'])
                appliance.version=to_unicode(download_info.get('version',None))
                appliance_list.append(appliance)

                a_list.append(feed_info)

        provider_id = self.get_provider_id(feed_name)
        DBHelper().delete_all(Appliance, [], [Appliance.provider_id == to_unicode(provider_id)])
        DBHelper().add_all(appliance_list)
        return a_list

        


    def _init_all(self):
        for f in self.feeds.keys():
            l = self.get_appliances_list(f)


    def get_all_archs(self):
        self._init_all()
        all_archs = {}
        for l in self.appliance_list.itervalues():
            for a in l:
                arch = a.get("arch")
                if arch and not all_archs.get(arch):
                    all_archs[arch] = arch

        return all_archs.keys()


    def get_all_packages(self):
        self._init_all()
        all_packages = {}
        for l in self.appliance_list.itervalues():
            for a in l:
                package = a.get("type")
                if package and not all_packages.get(package):
                    all_packages[package] = package

        return all_packages.keys()





if __name__ == '__main__':
    from ManagedNode import ManagedNode
    import pprint

    local_node = ManagedNode(hostname=constants.LOCALHOST)
    appliance_store = ApplianceStore(local_node, local_node.config)
    feeds = appliance_store.get_appliance_feeds()
    for feed_name in feeds:
        a_list = appliance_store.get_appliances_list(feed_name)
        print "=================", feed_name
        for a in a_list:
            print "*** ", a["title"]
            pprint.pprint(a)

