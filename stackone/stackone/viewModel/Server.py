from xml.dom import minidom
class Server(object):
    def __init__(self, id, type, label, icon, branch='false'):
        self.id = id
        self.type = type
        self.label = label
        self.icon = icon
        self.branch = branch
        self.children = []

    def addChild(self, child):
        self.children.append(child)
    @classmethod
    def loadAll():
        rootNode = Server(0, 0, 'Server Pool', 'gearIcon', 'false')
        node = Server(0, 0, '192.168.12.100', 'gearIcon', 'true')
        rootNode.addChild(node)
        node.addChild(Server(0, 0, 'Sally-Workstation', 'downIcon'))
        node.addChild(Server(0, 0, 'Xen-U1', 'downIcon'))
        node.addChild(Server(0, 0, 'content-db', 'checkIcon'))
        node = Server(0, 0, 'localhost', 'gearIcon', 'true')
        rootNode.addChild(node)
        node.addChild(Server(0, 0, 'Joe-PC', 'checkIcon'))
        node.addChild(Server(0, 0, 'web-01', 'checkIcon'))
        node.addChild(Server(0, 0, 'web_02', 'checkIcon'))
        node.addChild(Server(0, 0, 'web_03', 'checkIcon'))
        node = Server(0, 0, 'Image Store', 'gearIcon', 'true')
        rootNode.addChild(node)
        node.addChild(Server(0, 0, 'Fedora Core Install', 'gearIcon'))
        node.addChild(Server(0, 0, 'Linux CD Install', 'gearIcon'))
        node.addChild(Server(0, 0, 'MySQL', 'gearIcon'))
        node.addChild(Server(0, 0, 'Windows CD Install', 'gearIcon'))
        return [rootNode]

    def toXml(self, xml):
        server = xml.createElement('server')
        server.setAttribute('id', str(self.id))
        server.setAttribute('type', str(self.type))
        server.setAttribute('label', self.label)
        server.setAttribute('icon', str(self.icon))
        server.setAttribute('branch', str(self.branch))

        if self.children is not None:
            for child in self.children:
                server.appendChild(child.toXml(xml))
        return server




