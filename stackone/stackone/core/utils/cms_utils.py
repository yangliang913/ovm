import os
import base64
import xmlrpclib
import urllib2
import cookielib
import urllib
from urllib2 import *
from stackone.core.utils.CMSXMLRPCclient import CMSXmlRpcClient
class CMSXmlRpcUtils():
    def cms_connect(self, cms_url, login, password, ldap_user):
        tmp_url = cms_url.rsplit('/', 1)
        csep_name = tmp_url[1]
        cms_url = tmp_url[0]
        if cms_url.endswith('/'):
            cmsurl = cms_url
        else:
            cmsurl = cms_url + '/'
        cookieProcessor = HTTPCookieProcessor()
        opener = urllib2.build_opener(ProxyHandler(), UnknownHandler(), HTTPHandler(debuglevel=0), HTTPDefaultErrorHandler(), HTTPRedirectHandler(), FTPHandler(), FileHandler(), HTTPErrorProcessor(), cookieProcessor)
        response = self.cms_login(opener, cmsurl, login, password, ldap_user, csep_name)
        cj = cookieProcessor.cookiejar
        if response == '{success:true}':
            cms_client = CMSXmlRpcClient()
            cms_client.initialize_proxies(cj, cmsurl)
            return cms_client
        if response.find('{success:false,msg:') > -1:
            msg = response.replace('{success:false,msg:', '')[0:-1]
            raise Exception(msg)
        else:
            raise Exception(response)
        raise Exception('Username or Password or URL is invalid.')

    def cms_login(self, opener, url, user, password, ldap_user, csep_name):
        cred = {'login':user,'password':password,'ldap_user':ldap_user,'csep_name':csep_name}
        data = urllib.urlencode(cred)
        try:
            #req = urllib2.Request(url)
            req = urllib2.Request(url+'servicepoint_login')
            response = opener.open(req,data)
        except Exception as e:
            raise Exception('Error: Can not connect to CMS Server.')
        login_response = response.read()
        return login_response



