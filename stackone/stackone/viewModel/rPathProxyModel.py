class rPathProxyModel():
    url_list = [('NAV_BACKUP_CONFIG', ('Backup', 'rAA/backup/Backup')), ('NAV_EMAIL_CONFIG', ('Email', 'rAA/configure/SmtpConf')), ('NAV_NETWORK_CONFIG', ('Network', 'rAA/configure/Network')), ('NAV_PROXY_CONFIG', ('Proxy', 'rAA/configure/Proxy')), ('NAV_SET_ROOT_PASSWORD', ('Root Password', 'rAA/configure/RootPw')), ('NAV_SET_TIME_ZONE', ('Time Zone', 'rAA/configure/SetTimeZone')), ('NAV_SET_SSL_CERT', ('SSL Cert', 'rAA/configure/SSLCert')), ('NAV_SERVICES', ('Services', 'rAA/services/Services')), ('NAV_UPDATES', ('Updates', 'rAA/updatetroves/UpdateTroves')), ('NAV_USERS', ('Users', 'rAA/usermanagement/UserInterface')), ('NAV_LOGS', ('Logs', 'rAA/logs/Logs'))]
    def __init__(self):
        pass

    def get_path(self, in_opcode):
        for (opcode,(desc, path)) in self.url_list:
            if opcode == in_opcode:
                return path


    def getProxyIntegration(self):
        ops = []
        ops.append(('SPECIFY_DETAILS', 'Specify Details'))
        ops.append(('SEPARATOR', '--'))
        ops.append(('VISIT_APPLICATION', 'Application'))
        ops.append(('SEPARATOR', '--'))

        for op, details in self.url_list:
            desc, url = details
            ops.append((op, desc))

        return ops


    def get_keys(self):
        return ('host', 'app_protocol', 'app_port', 'app_path', 'app_mgmt_protocol', 'app_mgmt_port')

    def is_valid_info(self,vm):
        if vm and vm.get_config():
            config = vm.get_config()
            for vkey in self.get_keys():
                if not config.get(vkey):
                    return False
            return True

    def get_info(self, vm, username=None, password=None):
        if vm and vm.get_config():
            config = vm.get_config()
            (port,app_port)=("","")
            host = config["host"]
            proto = config["app_mgmt_protocol"]
            if config["app_mgmt_port"]:
                port = int(config["app_mgmt_port"])
            app_proto= config["app_protocol"]
            if config["app_port"]:
                app_port = int(config["app_port"])
            if config["app_path"] :
                app_path = config["app_path"]
            else:
                app_path = "/"

            # TBD : credential management needs to be done properly
            if username is None:
                username = "admin"
            if password is None:
                password = "password"

            return ((app_proto, host, app_port, app_path),
                    (proto, host, port),
                    (username, password))



    def get_web_url(self, vm):
        (app_url, mgmt_url, creds) = self. get_info(vm)
        (proto, host, port, path) = app_url
        url = "%s://%s:%d/%s" % (proto, host, port, path)
        return url

    def get_mgmt_web_url(self, vm, path):
        (app_url, mgmt_url, creds) = self. get_info(vm)
        (proto, host, port) = mgmt_url
        (u, p) = creds
        url = "%s://%s:%d/%s" % (proto, host, port, path)
        return url




if __name__ == '__main__':
    print 'Hello'

