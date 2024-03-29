class JBProxyModel():
    url_list = [('NAV_REGISTER_APPLIANCE', ('Register', 'register')), ('NAV_INFO', ('Info', 'info')), ('NAV_NETWORK_CONFIG', ('Network', 'staticip')), ('NAV_PROXY_CONFIG', ('Proxy', 'proxy')), ('NAV_SET_TIME_ZONE', ('Time Zone', 'timezone')), ('NAV_BACKUP', ('Backup', 'backup'))]
    def __init__(self):
        pass

    def get_path(self, in_opcode):
        for (opcode, (desc, path)) in self.url_list:
            if opcode == in_opcode:
                return path


    def getProxyIntegration(self):
        ops = []
        ops.append(('SPECIFY_DETAILS', 'Specify Details'))
        ops.append(('SEPARATOR', '--'))
        ops.append(('VISIT_APPLICATION', 'Application'))
        ops.append(('SEPARATOR', '--'))

        for (op,details) in self.url_list:
            (desc,url) = details
            ops.append((op, desc))

        return ops


    def get_keys(self):
        return ('host', 'app_protocol', 'app_port', 'app_path', 'app_mgmt_protocol', 'app_mgmt_port')

    def is_valid_info(self, vm):
        if vm and vm.get_config():
            config = vm.get_config()

            for vkey in self.get_keys():
                if not config.get(vkey):
                    config.get(vkey)
                    return False


            return True


    def get_info(self, vm, username=None, password=None):
        if vm and vm.get_config():
            config = vm.get_config()
            (port,app_port)= ('', '')
            host = config['host']
            proto = config['app_mgmt_protocol']
            if config['app_mgmt_port']:
                port = int(config['app_mgmt_port'])

            app_proto = config['app_protocol']
            if config['app_port']:
                app_port = int(config['app_port'])

            if config['app_path']:
                app_path = config['app_path']
            else:
                app_path = '/'

            if username is None:
                username = 'admin'

            if password is None:
                password = 'password'

            return ((app_proto, host, app_port, app_path), (proto, host, port), (username, password))

        return None


    def get_web_url(self, vm):
        (app_url,mgmt_url,creds) = self.get_info(vm)
        (proto,host,port,path)= app_url
        url = '%s://%s:%d/%s' % (proto, host, port, path)
        return url

    def get_mgmt_web_url(self, vm, path):
        (app_url,mgmt_url,creds)= self.get_info(vm)
        (proto,host,port) = mgmt_url
        (u,p) = creds
        url = '%s://%s:%d/%s' % (proto, host, port, path)
        return url



if __name__ == '__main__':
    print 'Hello'

