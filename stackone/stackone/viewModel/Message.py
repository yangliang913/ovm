from Sessions import SessionInfo
from xml.dom import minidom
class Message():
    def __init__(self, sess, resp, tag=None):
        self.sessionInfo = sess
        self.response = resp
        self.tag = tag

    def toXml(self):
        xml = minidom.Document()
        message = xml.createElement('message')
        message.appendChild(self.sessionInfo.toXml(xml))
        if self.response is not None:
            if isinstance(self.response, list):
                listCtr = xml.createElement(self.tag)
                for item in self.response:
                    listCtr.appendChild(item.toXml(xml))
                message.appendChild(listCtr)
            else:
                message.appendChild(self.response.toXml(xml))
        xml.appendChild(message)
        return xml
